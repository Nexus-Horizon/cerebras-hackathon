import os
import requests
import json
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class CerebrasConfig:
    """Configuration for Cerebras Qwen model"""
    api_url: str
    api_key: Optional[str] = None
    model_name: str = "qwen-7b"
    max_tokens: int = 100
    temperature: float = 0.7
    timeout: int = 30
    # Alternative endpoints to try if primary fails
    fallback_urls: list = None

    def __post_init__(self):
        if self.fallback_urls is None:
            self.fallback_urls = [
                "https://api.cerebras.com/v1/chat/completions",
                "https://api.cerebras.com/v1/completions",
                "https://api.cerebras.com/chat/completions",
                "https://api.cerebras.com/completions"
            ]

class CerebrasQwenClient:
    """Client for interacting with Cerebras Qwen model"""
    
    def __init__(self, config: CerebrasConfig):
        self.config = config
        self.session = requests.Session()
        
        # Set up headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if config.api_key:
            self.headers["Authorization"] = f"Bearer {config.api_key}"
    
    def _test_endpoint_connectivity(self, url: str) -> bool:
        """Test if an endpoint is reachable"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code < 500  # Accept any response that's not a server error
        except:
            return False
    
    def _find_working_endpoint(self) -> Optional[str]:
        """Find a working API endpoint from the list of URLs"""
        urls_to_try = [self.config.api_url] + self.config.fallback_urls
        
        for url in urls_to_try:
            if self._test_endpoint_connectivity(url):
                if os.getenv("DEBUG_CEREBRAS", "false").lower() == "true":
                    print(f"✅ Found working endpoint: {url}")
                return url
        
        return None
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using Cerebras Qwen model
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            Dict containing response and metadata
        """
        start_time = time.time()
        
        # Find working endpoint
        working_url = self._find_working_endpoint()
        if not working_url:
            return {
                "success": False,
                "error": "No working Cerebras API endpoint found. Please check your network connection and API configuration.",
                "latency": time.time() - start_time,
                "model": self.config.model_name
            }
        
        # Prepare request data
        data = {
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "model": self.config.model_name
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            data["top_k"] = kwargs["top_k"]
        if "stop" in kwargs:
            data["stop"] = kwargs["stop"]
        
        try:
            # Make API request
            response = self.session.post(
                working_url,
                headers=self.headers,
                json=data,
                timeout=self.config.timeout
            )
            
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("text", result.get("response", "")),
                    "latency": latency,
                    "model": self.config.model_name,
                    "raw_response": result
                }
            else:
                return {
                    "success": False,
                    "error": f"API call error with status {response.status_code}: {response.text}",
                    "latency": latency,
                    "model": self.config.model_name
                }
                
        except requests.exceptions.ConnectionError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}. Please check your network connection and API endpoint.",
                "latency": time.time() - start_time,
                "model": self.config.model_name
            }
        except requests.exceptions.Timeout as e:
            return {
                "success": False,
                "error": f"Request timeout: {str(e)}. Please try again or increase timeout.",
                "latency": time.time() - start_time,
                "model": self.config.model_name
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "latency": time.time() - start_time,
                "model": self.config.model_name
            }

def get_cerebras_config() -> CerebrasConfig:
    """Get Cerebras configuration from environment variables"""
    # Get the primary API URL
    primary_url = os.getenv("CEREBRAS_API_URL", "https://api.cerebras.com/v1/chat/completions")
    
    # Define fallback URLs
    fallback_urls = [
        "https://api.cerebras.com/v1/completions",
        "https://api.cerebras.com/chat/completions", 
        "https://api.cerebras.com/completions",
        # Add alternative domains if needed
        "https://cerebras-api.com/v1/chat/completions",
        "https://cerebras-api.com/v1/completions"
    ]
    
    return CerebrasConfig(
        api_url=primary_url,
        api_key=os.getenv("CEREBRAS_API_KEY"),
        model_name=os.getenv("CEREBRAS_MODEL_NAME", "qwen-7b"),
        max_tokens=int(os.getenv("CEREBRAS_MAX_TOKENS", "100")),
        temperature=float(os.getenv("CEREBRAS_TEMPERATURE", "0.7")),
        timeout=int(os.getenv("CEREBRAS_TIMEOUT", "30")),
        fallback_urls=fallback_urls
    )

def call_cerebras_qwen(prompt: str) -> str:
    """
    Call Cerebras Qwen model
    
    Args:
        prompt: Input prompt
        
    Returns:
        Model response or error message
    """
    config = get_cerebras_config()
    client = CerebrasQwenClient(config)
    
    # Debug logging
    if os.getenv("DEBUG_CEREBRAS", "false").lower() == "true":
        print(f"Cerebras Debug - API URL: {config.api_url}")
        print(f"Cerebras Debug - Model: {config.model_name}")
        print(f"Cerebras Debug - Prompt: {prompt[:100]}...")

    # Test connectivity first
    working_url = client._find_working_endpoint()
    if not working_url:
        # Fallback to local or alternative implementation
        return _fallback_response(prompt)
    
    result = client.generate(prompt)
    
    if result["success"]:
        return result["response"]
    else:
        # If Cerebras fails, try fallback
        return _fallback_response(prompt, result["error"])

def _fallback_response(prompt: str, error_msg: str = None) -> str:
    """
    Fallback response when Cerebras API is not available
    
    Args:
        prompt: Original prompt
        error_msg: Error message from Cerebras (optional)
        
    Returns:
        Fallback response
    """
    if os.getenv("DEBUG_CEREBRAS", "false").lower() == "true":
        if error_msg:
            print(f"Cerebras Debug - Fallback triggered due to: {error_msg}")
        else:
            print("Cerebras Debug - Fallback triggered due to connectivity issues")
    
    # Simple rule-based fallback for task classification
    prompt_lower = prompt.lower()
    
    # Task classification fallback
    if "classify" in prompt_lower or "task" in prompt_lower:
        if any(word in prompt_lower for word in ["text", "extract", "read", "ocr"]):
            return "OCR"
        elif any(word in prompt_lower for word in ["describe", "caption", "what is this"]):
            return "Image Captioning"
        elif any(word in prompt_lower for word in ["what color", "how many", "count", "visual qa", "vqa"]):
            return "Visual QA"
        elif any(word in prompt_lower for word in ["classify", "category", "type"]):
            return "Image Classification"
        elif any(word in prompt_lower for word in ["detect", "objects", "find"]):
            return "Object Detection"
        elif any(word in prompt_lower for word in ["style", "art", "transfer"]):
            return "Style Transfer"
        elif any(word in prompt_lower for word in ["medical", "diagnosis", "health"]):
            return "Medical Diagnosis"
        else:
            return "Other"
    
    # General fallback response
    return f"Fallback response: I'm currently using a simplified response system. Your prompt was: '{prompt[:100]}...'"

def call_cerebras_qwen_chat(messages: list, **kwargs) -> str:
    """
    Call Cerebras Qwen model with chat format
    
    Args:
        messages: List of message dictionaries
        **kwargs: Additional parameters
        
    Returns:
        Model response or error message
    """
    config = get_cerebras_config()
    client = CerebrasQwenClient(config)
    
    # Find working endpoint
    working_url = client._find_working_endpoint()
    if not working_url:
        return _fallback_chat_response(messages)
    
    # Convert to chat format
    data = {
        "messages": messages,
        "model": config.model_name,
        "max_tokens": kwargs.get("max_tokens", config.max_tokens),
        "temperature": kwargs.get("temperature", config.temperature)
    }
    
    try:
        response = client.session.post(
            working_url,
            headers=client.headers,
            json=data,
            timeout=config.timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return _fallback_chat_response(messages, f"API call failed with status {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        return _fallback_chat_response(messages, f"Connection error - {str(e)}")
    except requests.exceptions.Timeout as e:
        return _fallback_chat_response(messages, f"Request timeout - {str(e)}")
    except requests.exceptions.RequestException as e:
        return _fallback_chat_response(messages, f"Request failed - {str(e)}")

def _fallback_chat_response(messages: list, error_msg: str = None) -> str:
    """
    Fallback response for chat format when Cerebras API is not available
    
    Args:
        messages: List of message dictionaries
        error_msg: Error message (optional)
        
    Returns:
        Fallback response
    """
    if os.getenv("DEBUG_CEREBRAS", "false").lower() == "true":
        if error_msg:
            print(f"Cerebras Debug - Chat fallback triggered due to: {error_msg}")
        else:
            print("Cerebras Debug - Chat fallback triggered due to connectivity issues")
    
    # Extract the last user message
    last_user_message = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            last_user_message = message.get("content", "")
            break
    
    # Simple fallback response
    if last_user_message:
        return f"Fallback response: I'm currently using a simplified response system. Your message was: '{last_user_message[:100]}...'"
    else:
        return "Fallback response: I'm currently using a simplified response system."

def test_cerebras_connectivity() -> Dict[str, Any]:
    """
    Test connectivity to Cerebras API endpoints
    
    Returns:
        Dict with connectivity test results
    """
    config = get_cerebras_config()
    client = CerebrasQwenClient(config)
    
    results = {
        "primary_url": config.api_url,
        "fallback_urls": config.fallback_urls,
        "working_endpoint": None,
        "all_tests": []
    }
    
    urls_to_test = [config.api_url] + config.fallback_urls
    
    for url in urls_to_test:
        test_result = {
            "url": url,
            "reachable": False,
            "status_code": None,
            "error": None
        }
        
        try:
            response = client.session.head(url, timeout=5)
            test_result["reachable"] = True
            test_result["status_code"] = response.status_code
        except requests.exceptions.ConnectionError as e:
            test_result["error"] = f"Connection error: {str(e)}"
        except requests.exceptions.Timeout as e:
            test_result["error"] = f"Timeout: {str(e)}"
        except Exception as e:
            test_result["error"] = f"Error: {str(e)}"
        
        results["all_tests"].append(test_result)
        
        if test_result["reachable"] and test_result["status_code"] < 500:
            results["working_endpoint"] = url
            break
    
    return results

# Task classification specific function
def classify_task_with_cerebras_qwen(question: str, image_context: Optional[str] = None) -> str:
    """
    Classify AI task using Cerebras Qwen model
    
    Args:
        question: User's question
        image_context: Optional image description
        
    Returns:
        Predicted task type
    """
    prompt = f"""
Classify the AI task based on the question and image description.

Question: {question}
Image: {image_context or "No image context provided"}

Respond with exactly one of these options:
- OCR
- Image Captioning
- Visual QA
- Image Classification
- Object Detection
- Style Transfer
- Medical Diagnosis
- Other

Task:"""

    
    response = call_cerebras_qwen(prompt)
    
    if os.getenv("DEBUG_CEREBRAS", "false").lower() == "true":
        print("Response from calling cerebras:")
        print(response)
    
    # Parse response to extract task
    response_lower = response.lower().strip()
    
    # Check if this is a fallback response
    if response.startswith("Fallback response:"):
        # Use the fallback logic that's already built into _fallback_response
        # The fallback response should already be the correct task type
        return response
    
    # Define task keywords for parsing
    task_mapping = {
        "ocr": "OCR",
        "text": "OCR",
        "read": "OCR",
        "extract": "OCR",
        "caption": "Image Captioning",
        "describe": "Image Captioning",
        "what is this": "Image Captioning",
        "visual qa": "Visual QA",
        "vqa": "Visual QA",
        "what color": "Visual QA",
        "how many": "Visual QA",
        "count": "Visual QA",
        "classify": "Image Classification",
        "category": "Image Classification",
        "type": "Image Classification",
        "detect": "Object Detection",
        "objects": "Object Detection",
        "style transfer": "Style Transfer",
        "style": "Style Transfer",
        "art": "Style Transfer",
        "medical": "Medical Diagnosis",
        "diagnosis": "Medical Diagnosis",
        "health": "Medical Diagnosis"
    }
    
    return parse_task_from_response(response) or "Other"

def parse_task_from_response(response: str) -> str:
    valid_tasks = ["OCR", "Image Captioning", "Visual QA", "Image Classification", "Object Detection", "Style Transfer", "Medical Diagnosis", "Other"]
    
    response = response.lower().replace(".", "").replace(",", "").replace("?", "").replace("!", "")
    
    for task in valid_tasks:
        if task.lower() in response:
            return task
    
    return "Other"
