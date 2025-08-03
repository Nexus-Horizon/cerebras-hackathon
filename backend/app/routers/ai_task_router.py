from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
import os

router = APIRouter()

@router.post("/api/process")
async def process_image(question: str = Form(...), image: UploadFile = File(...)):
    # Send prompt to Qwen to determine task type
    task_type = determine_task_type(question, image)

    # Dispatch to the appropriate model for that task
    output, latency = dispatch_to_model(task_type, image)

    # Return model output, latency, task type, and model used
    return JSONResponse(content={"task": task_type, "output": output, "latency": latency}, media_type="application/json")

def determine_task_type(question: str, image: UploadFile):
    # TO DO: implement Qwen task type classification
    pass

def dispatch_to_model(task_type: str, image: UploadFile):
    # TO DO: implement model dispatching
    pass
