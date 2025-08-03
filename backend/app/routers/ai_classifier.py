import os
import time
import re
from typing import Optional
import httpx
from .qwen_model import call_qwen_model_local, call_qwen_model_api, parse_task_from_response
from .cerebras_qwen import classify_task_with_cerebras_qwen, call_cerebras_qwen

# Prompt template for Qwen model
prompt_template = """
Classify the AI task based on the question and image description.

Question: {question}
Image: {image_context}

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

def classify_task_with_qwen(question: str, image_context: Optional[str] = None) -> str:
    """
    Classify AI task using Qwen model via OpenAI-compatible API
    
    Args:
        question (str): The user's question
        image_context (Optional[str]): Description of the image
        
    Returns:
        str: The predicted AI task or "Other" if API call fails
    """
    start_time = time.time()
    
    # Check if Cerebras is preferred
    print(os.getenv("USE_CEREBRAS_QWEN", "false"))
    use_cerebras = os.getenv("USE_CEREBRAS_QWEN", "false").lower() == "true"

    if use_cerebras:
        try:
            result = classify_task_with_cerebras_qwen(question, image_context)
            latency = time.time() - start_time
            print(f"Cerebras Qwen classification latency: {latency:.4f}s")
            return result
        except Exception as e:
            print(f"Cerebras Qwen classification failed: {e}")
    
    # Format the prompt
    prompt = prompt_template.format(
        question=question,
        image_context=image_context or "No image context provided"
    )
    
    try:
        # Try API first, fallback to local if API fails
        try:
            response = call_qwen_model_api(prompt)
            if not response.startswith("Error:"):
                return parse_task_from_response(response)
        except Exception as api_error:
            print(f"Qwen API call failed: {api_error}")
        
        # Fallback to local model
        response = call_qwen_model_local(prompt)
        return parse_task_from_response(response)
        
    except Exception as e:
        print(f"All Qwen model calls failed: {e}")
        return "Other"
    finally:
        latency = time.time() - start_time
        print(f"Classification latency: {latency:.4f}s")

def mock_classify_task(question: str) -> str:
    """
    Fallback function that uses keywords to classify tasks
    
    Args:
        question (str): The user's question
        
    Returns:
        str: The predicted AI task
    """
    question_lower = question.lower()
    
    # Medical Diagnosis detection (check first as it's more specific)
    medical_keywords = ["medical", "diagnosis", "health", "doctor", "patient", "disease", "condition", "symptoms", "diagnose"]
    if any(keyword in question_lower for keyword in medical_keywords):
        return "Medical Diagnosis"
    
    # OCR detection
    ocr_keywords = ["text", "read", "extract", "ocr", "words", "letters", "characters", "document"]
    if any(keyword in question_lower for keyword in ocr_keywords):
        return "OCR"
    
    # Image Classification detection
    classification_keywords = ["classify", "category", "type", "kind", "sort", "group", "label"]
    if any(keyword in question_lower for keyword in classification_keywords):
        return "Image Classification"
    
    # Object Detection detection
    object_keywords = ["objects", "items", "things", "find", "locate", "bounding box", "coordinates", "detect"]
    if any(keyword in question_lower for keyword in object_keywords):
        return "Object Detection"
    
    # Style Transfer detection
    style_keywords = ["style", "art", "transform", "convert", "change style", "make it look like"]
    if any(keyword in question_lower for keyword in style_keywords):
        return "Style Transfer"
    
    # Image Captioning detection
    caption_keywords = ["describe", "caption", "what is this", "what do you see", "scene", "picture", "image"]
    if any(keyword in question_lower for keyword in caption_keywords):
        return "Image Captioning"
    
    # Visual QA detection (more specific patterns)
    vqa_keywords = ["what color", "how many", "count", "identify", "recognize"]
    if any(keyword in question_lower for keyword in vqa_keywords):
        return "Visual QA"
    
    # General Visual QA patterns
    if question_lower.startswith("what") or question_lower.startswith("where") or question_lower.startswith("how"):
        return "Visual QA"
    
    return "Other"
