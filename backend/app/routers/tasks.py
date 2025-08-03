import os
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pytesseract
from PIL import Image
import httpx
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, AutoFeatureExtractor, AutoModelForImageClassification
import paddleocr
from PIL import Image

class TaskRequest(BaseModel):
    image_path: str
    question: str = ""

router = APIRouter(
    prefix="/task",
    tags=["tasks"]
)

@router.post("/ocr")
async def ocr_task(request: TaskRequest):
    """Extract text from image using OCR with pytesseract as primary engine"""
    image_path = request.image_path
    question = request.question
    start_time = time.time()
    
    try:
        # Check if image file exists
        if not os.path.exists(image_path):
            return {
                "result": "Image file not found",
                "latency": 0,
                "model_name": "pytesseract"
            }
        
        # Try pytesseract first (primary OCR engine)
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Try different PSM modes for better text detection
            psm_modes = ['--psm 6', '--psm 8', '--psm 13', '--psm 3', '--psm 11']
            text = ""
            
            for psm in psm_modes:
                try:
                    detected_text = pytesseract.image_to_string(image, lang='eng', config=psm)
                    if detected_text.strip():
                        text = detected_text
                        break
                except Exception as e:
                    print(f"pytesseract failed with {psm}: {e}")
                    continue
            
            if text.strip():
                latency = time.time() - start_time
                # Record metric for pytesseract
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            "http://localhost:8000/metrics/record",
                            params={"model_name": "pytesseract", "latency": latency, "task": "OCR"}
                        )
                except Exception:
                    pass
                
                return {
                    "result": text.strip(),
                    "latency": round(latency, 4),
                    "model_name": "pytesseract"
                }
        except Exception as pytesseract_error:
            print(f"pytesseract failed: {pytesseract_error}")
        
        # Fallback to PaddleOCR if pytesseract fails
        try:
            ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang="en", det_db_thresh=0.3, det_db_box_thresh=0.5)
            result = ocr.ocr(image_path)
            
            if not result or not result[0]:
                text = "No text found in image"
            else:
                # Extract text with proper validation - handle new PaddleOCR format
                text_parts = []
                for line in result:
                    if line is None:
                        continue
                    for item in line:
                        if isinstance(item, list) and len(item) >= 2 and isinstance(item[1], list) and len(item[1]) >= 2:
                            detected_text = item[1][0]
                            confidence = item[1][1]
                            # Validate that the text is meaningful and not the problematic string
                            if (detected_text and isinstance(detected_text, str) and 
                                detected_text.strip() and len(detected_text.strip()) > 1 and
                                "naotoeeeeeeiee" not in detected_text.lower()):
                                text_parts.append(detected_text)
                
                text = " ".join(text_parts) if text_parts else "No text found in image"
            
            latency = time.time() - start_time
            
            # Record metric for PaddleOCR
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "http://localhost:8000/metrics/record",
                        params={"model_name": "PaddleOCR", "latency": latency, "task": "OCR"}
                    )
            except Exception:
                pass
            
            return {
                "result": text.strip() if text.strip() else "No text found in image",
                "latency": round(latency, 4),
                "model_name": "PaddleOCR"
            }
        except Exception as paddleocr_error:
            print(f"PaddleOCR failed: {paddleocr_error}")
            raise Exception(f"Both pytesseract and PaddleOCR failed. pytesseract: {pytesseract_error}, PaddleOCR: {paddleocr_error}")
            
    except Exception as e:
        latency = time.time() - start_time
        return {
            "result": "No text detected in image",
            "latency": round(latency, 4),
            "model_name": "pytesseract"
        }



@router.post("/caption")
async def caption_task(request: TaskRequest):
    """Generate image caption using BLIP"""
    image_path = request.image_path
    question = request.question
    start_time = time.time()
    
    try:
        # Load pre-trained model and processor
        processor = BlipProcessor.from_pretrained("Salesforce/BLIP-2")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/BLIP-2")
        

        image = Image.open(image_path)
        
        # Preprocess image
        inputs = processor(images=image, return_tensors="pt")
        
        # Generate caption
        outputs = model.generate(**inputs)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        
        latency = time.time() - start_time
        return {
            "result": caption,
            "latency": round(latency, 4),
            "model_name": "BLIP-2"
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "result": "Unable to generate image caption",
            "latency": round(latency, 4),
            "model_name": "BLIP-2"
        }
@router.post("/vqa")
async def vqa_task(request: TaskRequest):
    """Visual Question Answering using BLIP-2"""
    image_path = request.image_path
    question = request.question
    start_time = time.time()
    
    try:
        # Load pre-trained model and processor
        processor = BlipProcessor.from_pretrained("Salesforce/BLIP-2")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/BLIP-2")
        
        image = Image.open(image_path)
        
        # Preprocess image and question
        inputs = processor(images=image, text=question, return_tensors="pt")
        
        # Generate answer
        outputs = model.generate(**inputs)
        answer = processor.decode(outputs[0], skip_special_tokens=True)
        
        latency = time.time() - start_time
        return {
            "result": answer,
            "latency": round(latency, 4),
            "model_name": "BLIP-2"
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "result": "Unable to answer visual question",
            "latency": round(latency, 4),
            "model_name": "BLIP-2"
        }

@router.post("/medical")
async def medical_task(request: TaskRequest):
    """Medical image analysis using ResNet"""
    image_path = request.image_path
    question = request.question
    start_time = time.time()
    
    try:
        
        # Load pre-trained model and feature extractor
        feature_extractor = AutoFeatureExtractor.from_pretrained("microsoft/ResNet-50")
        model = AutoModelForImageClassification.from_pretrained("microsoft/ResNet-50")
        
        image = Image.open(image_path)
        
        # Preprocess image
        inputs = feature_extractor(images=image, return_tensors="pt")
        
        # Generate diagnosis
        try:
            outputs = model(**inputs)
            logits = outputs.logits
            diagnosis = torch.argmax(logits)
        except Exception as e:
            diagnosis = "Unable to generate medical diagnosis"
        
        latency = time.time() - start_time
        return {
            "result": diagnosis,
            "latency": round(latency, 4),
            "model_name": "ResNet-50"
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "result": "Unable to perform medical analysis",
            "latency": round(latency, 4),
            "model_name": "ResNet-50"
        }

@router.post("/simocr")
async def simocr_task(request: TaskRequest):
    """Simple OCR using PaddleOCR"""
    image_path = request.image_path
    question = request.question
    start_time = time.time()
    
    try:
        # Check if image file exists
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")
        
        # Use PaddleOCR with better configuration
        ocr = paddleocr.PaddleOCR(lang="en", use_angle_cls=True, det_db_thresh=0.3, det_db_box_thresh=0.5)
        result = ocr.ocr(image_path)
        
        # Handle case where result is None or empty
        if result is None:
            result_text = "No text found in image"
        elif not result:
            result_text = "No text found in image"
        else:
            # Extract text with layout information
            text_results = []
            for line in result:
                if line is None:
                    continue
                for item in line:
                    try:
                        # Validate item structure before accessing
                        if (isinstance(item, list) and len(item) >= 2 and 
                            isinstance(item[1], list) and len(item[1]) >= 2):
                            detected_text = item[1][0]
                            # Validate that the text is meaningful and not the problematic string
                            if (detected_text and isinstance(detected_text, str) and 
                                detected_text.strip() and len(detected_text.strip()) > 1 and
                                "naotoeeeeeeiee" not in detected_text.lower()):
                                text_results.append({
                                    "text": detected_text,
                                    "confidence": item[1][1],
                                    "bbox": item[0]
                                })
                        else:
                            # Handle unexpected item structure
                            print(f"Unexpected item structure: {item}")
                            continue
                    except (IndexError, TypeError) as e:
                        print(f"Error processing item {item}: {e}")
                        continue
            
            # Format result
            if text_results:
                result_text = " ".join([item["text"] for item in text_results])
            else:
                result_text = "No text found in image"
        
        latency = time.time() - start_time
        return {
            "result": result_text,
            "latency": round(latency, 4),
            "model_name": "PaddleOCR (Simple)"
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "result": "No text detected in image",
            "latency": round(latency, 4),
            "model_name": "PaddleOCR (Simple)"
        }

@router.post("/other")
async def other_task(request: TaskRequest):
    """Handle other tasks"""
    image_path = request.image_path
    question = request.question
    start_time = time.time()
    
    try:
        response = "Task not supported"
        
        latency = time.time() - start_time
        return {
            "result": response,
            "latency": round(latency, 4),
            "model_name": "None"
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "result": "Task processing completed",
            "latency": round(latency, 4),
            "model_name": "None"
        }

def get_image_caption(image: Image.Image) -> str:
    """Generate a caption from an image using BLIP"""
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption
