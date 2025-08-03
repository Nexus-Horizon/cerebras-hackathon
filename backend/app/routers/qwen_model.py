import os
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer

def call_qwen_model_local(prompt: str) -> str:
    # Load the Qwen model and tokenizer
    model = AutoModelForCausalLM.from_pretrained("qwen-model")
    tokenizer = AutoTokenizer.from_pretrained("qwen-model")

    # Tokenize the prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate the response
    response = model.generate(**inputs)

    # Convert the response to text
    response_text = tokenizer.decode(response[0], skip_special_tokens=True)

    return response_text

def call_qwen_model_api(prompt: str) -> str:
    """
    Call Qwen model via API endpoint
    
    Args:
        prompt (str): The input prompt for the model
        
    Returns:
        str: The model's response or error message
    """
    # Set the API endpoint URL - configure this to your actual API endpoint
    # For local development, you might use a local API server
    # You can override this with environment variable QWEN_API_URL
    url = os.getenv("QWEN_API_URL", "http://localhost:8000/qwen/predict")
    
    # Get API key from environment variable
    api_key = os.getenv("QWEN_API_KEY")
    
    # Set the API request headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Add API key to headers if provided
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    elif not url.startswith("http://localhost"):  # Warn if no API key for external APIs
        print("Warning: No QWEN_API_KEY provided for external API call")

    # Set the API request data with configurable parameters
    data = {
        "prompt": prompt,
        "max_tokens": int(os.getenv("QWEN_MAX_TOKENS", "100")),
        "temperature": float(os.getenv("QWEN_TEMPERATURE", "0.7"))
    }

    try:
        # Send the API request with configurable timeout
        timeout = int(os.getenv("QWEN_API_TIMEOUT", "30"))
        
        # Debug logging
        if os.getenv("DEBUG_QWEN", "false").lower() == "true":
            print(f"Qwen API Debug - URL: {url}")
            print(f"Qwen API Debug - Headers: {headers}")
            print(f"Qwen API Debug - Data: {data}")
            print(f"Qwen API Debug - Timeout: {timeout}")
        
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        
        # Check if the response was successful
        if response.status_code == 200:
            # Return the response text
            result = response.json()
            return result.get("response", result.get("text", "No response text"))
        else:
            # Return an error message with status code
            return f"Error: API call failed with status {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to call Qwen API - {str(e)}"

def parse_task_from_response(response: str) -> str:
    # Define the valid task strings
    valid_tasks = ["OCR", "Image Captioning", "Visual QA", "Image Classification", "Object Detection", "Style Transfer", "Medical Diagnosis", "Other"]

    # Convert the response to lowercase and remove punctuation
    response = response.lower().replace(".", "").replace(",", "").replace("?", "").replace("!", "")

    # Iterate over the valid tasks
    for task in valid_tasks:
        # Check if the task is in the response
        if task.lower() in response:
            # Return the task
            return task

    # If no valid task is found, return "Other"
    return "Other"
