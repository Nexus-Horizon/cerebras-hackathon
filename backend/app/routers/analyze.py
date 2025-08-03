import os
import random
import time
import json
import traceback
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
from app.routers.ai_classifier import classify_task_with_qwen, mock_classify_task
import httpx
import uuid
from pathlib import Path
from PIL import Image

from app.routers.tasks import get_image_caption

router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)

# Create absolute path to uploads directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/")
async def analyze_image(
    question: str = Form(...),
    image: UploadFile = File(...)
):
    total_start_time = time.time()
    
    # Validate file type
    if image.content_type not in ["image/jpeg", "image/png"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Only JPG and PNG images are allowed"}
        )
    
    # Save the uploaded image
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    
    # Handle potential filename conflicts
    base_name, extension = os.path.splitext(image.filename)
    counter = 1
    while os.path.exists(file_path):
        new_filename = f"{base_name}_{counter}{extension}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        counter += 1
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Create image context (using filename for now)
    # image_context = f"Image file: {os.path.basename(file_path)}"
    pil_image = Image.open(image.file).convert("RGB")
    image_context = get_image_caption(pil_image)
    
    # Classify the task
    classification_start_time = time.time()
    task = classify_task_with_qwen(question, image_context)
    classification_latency = time.time() - classification_start_time
    
    # Handle the task
    task_handling_start_time = time.time()
    result, model_used = await handle_task(task, file_path, question)
    task_latency = time.time() - task_handling_start_time
    
    # Calculate total latency
    total_latency = time.time() - total_start_time
    
    # Log the analysis call
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "model": model_used,
        "latency": round(total_latency, 2),
        "result": result
    }
    
    # Read existing logs
    logs = []
    logs_file = BASE_DIR / "logs.json"
    if os.path.exists(logs_file):
        try:
            with open(logs_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            pass  # If file is empty or corrupted, start with empty list
    
    # Append new log entry
    logs.append(log_entry)
    
    # Write logs back to file
    with open(logs_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    # Print to console
    print(f"Question: {question}")
    print(f"Image filename: {os.path.basename(file_path)}")
    print(f"Classified task: {task}")
    print(f"Result: {result}")
    
    # Return JSON response
    return {
        "id": log_entry["id"],
        "task": task,
        "question": question,
        "filename": os.path.basename(file_path),
        "result": result,
        "latency": total_latency,
        "model": model_used
    }

async def handle_task(task: str, image_path: str, question: str) -> tuple[str, str]:
    """
    Handle different AI tasks by routing to appropriate endpoints
    
    Args:
        task (str): The classified AI task
        image_path (str): Path to the uploaded image
        question (str): The user's question
        
    Returns:
        tuple: (result string, model name used)
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Map task names to endpoint URLs
            task_mapping = {
                "OCR": "pytesseract",  # Default to pytesseract for OCR
                "Image Captioning": "caption",
                "Visual QA": "vqa",
                "Image Classification": "other",
                "Object Detection": "other",
                "Style Transfer": "other",
                "Medical Diagnosis": "medical",
                "Other": "other"
            }
            
            # For OCR tasks, randomly choose between OCR and SimOCR for demo
            model_used = "pytesseract"
            endpoint = task_mapping.get(task, "other")
            if task == "OCR":
                endpoint = random.choice(["ocr", "simocr"])
                if endpoint == "simocr":
                    model_used = "simocr"
                elif endpoint == "ocr":
                    model_used = "pytesseract"  # OCR route now uses pytesseract as primary
            
            url = f"http://localhost:8000/task/{endpoint}"
            print(f"Making request to: {url}")
            print(f"Request data: image_path={image_path}, question={question}")
            
            response = await client.post(
                url,
                json={"image_path": image_path, "question": question}
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                result_data = response.json()
                print(f"Result data: {result_data}")
                return result_data.get("result", "Task completed successfully"), model_used
            else:
                return f"Task handling failed with status {response.status_code}", model_used
                
    except Exception as e:
        print(f"Task handling error: {e}")
        traceback.print_exc()
        return "Task handling failed due to an error", "error"

@router.get("/result/{result_id}")
async def get_result(result_id: str):
    logs_file = BASE_DIR / "logs.json"

    print(f"Looking for result_id: {result_id}")
    print(f"Logs file path: {logs_file}")
    
    if not os.path.exists(logs_file):
        raise HTTPException(status_code=404, detail="No results found")
    
    with open(logs_file, 'r') as f:
        logs = json.load(f)
    
    print(f"Total entries in logs: {len(logs)}")
    
    result_entry = next((entry for entry in logs if entry.get("id") == result_id), None)
    
    if not result_entry:
        raise HTTPException(status_code=404, detail=f"Result not found for ID: {result_id}")
    
    return result_entry
