import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import torch

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app
from app.main import app

# Create a test client
client = TestClient(app)

# Sample test image path (will need to be adjusted based on actual test setup)
TEST_IMAGE_PATH = "uploads/stop sign.png"

# Ensure test image exists
@pytest.fixture(autouse=True)
def check_test_image():
    if not os.path.exists(TEST_IMAGE_PATH):
        pytest.skip(f"Test image {TEST_IMAGE_PATH} not found. Skipping tests.")

class TestTasksRouter:
    """Test suite for the tasks router endpoints"""
    
    def test_ocr_task_success(self):
        """Test successful OCR task"""
        # Prepare test data
        test_data = {
            "image_path": TEST_IMAGE_PATH,
            "question": ""
        }
        
        # Mock paddleocr to avoid actual OCR processing
        with patch('app.routers.tasks.paddleocr.PaddleOCR') as mock_ocr:
            # Setup mock return value
            mock_result = [[[[[10, 10], [100, 10], [100, 50], [10, 50]], ('STOP', 0.95)]]]
            mock_ocr_instance = MagicMock()
            mock_ocr_instance.ocr.return_value = mock_result
            mock_ocr.return_value = mock_ocr_instance
            
            # Make request to OCR endpoint
            response = client.post("/task/ocr", json=test_data)
            
            # Assert response
            assert response.status_code == 200
            result = response.json()
            assert "result" in result
            assert "latency" in result
            assert "model_name" in result
            assert result["model_name"] == "PaddleOCR"
            assert "STOP" in result["result"]
    
    def test_ocr_task_image_not_found(self):
        """Test OCR task with non-existent image"""
        test_data = {
            "image_path": "nonexistent.png",
            "question": ""
        }
        
        response = client.post("/task/ocr", json=test_data)
        
        # Assert response
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert "latency" in result
        assert "model_name" in result
        assert result["model_name"] == "PaddleOCR"
        assert result["result"] == "Image file not found"
    
    def test_caption_task_success(self):
        """Test successful caption generation task"""
        test_data = {
            "image_path": TEST_IMAGE_PATH,
            "question": ""
        }
        
        # Mock BLIP processor and model
        with patch('app.routers.tasks.BlipProcessor') as mock_processor, \
             patch('app.routers.tasks.BlipForConditionalGeneration') as mock_model:
            
            # Setup mocks
            mock_processor_instance = MagicMock()
            mock_processor.from_pretrained.return_value = mock_processor_instance
            
            mock_model_instance = MagicMock()
            mock_model.from_pretrained.return_value = mock_model_instance
            
            mock_processor_instance.return_tensors = "pt"
            mock_model_instance.generate.return_value = [torch.tensor([1, 2, 3, 4])]
            mock_processor_instance.decode.return_value = "a stop sign on a pole"
            
            # Make request
            response = client.post("/task/caption", json=test_data)
            
            # Assert response
            assert response.status_code == 200
            result = response.json()
            assert "result" in result
            assert "latency" in result
            assert "model_name" in result
            assert result["model_name"] == "BLIP-2"
            assert len(result["result"]) > 0
    
    def test_vqa_task_success(self):
        """Test successful visual question answering task"""
        test_data = {
            "image_path": TEST_IMAGE_PATH,
            "question": "What is in the image?"
        }
        
        # Mock BLIP processor and model
        with patch('app.routers.tasks.BlipProcessor') as mock_processor, \
             patch('app.routers.tasks.BlipForConditionalGeneration') as mock_model:
            
            # Setup mocks
            mock_processor_instance = MagicMock()
            mock_processor.from_pretrained.return_value = mock_processor_instance
            
            mock_model_instance = MagicMock()
            mock_model.from_pretrained.return_value = mock_model_instance
            
            mock_processor_instance.return_tensors = "pt"
            mock_model_instance.generate.return_value = [torch.tensor([1, 2, 3, 4])]
            mock_processor_instance.decode.return_value = "a stop sign"
            
            # Make request
            response = client.post("/task/vqa", json=test_data)
            
            # Assert response
            assert response.status_code == 200
            result = response.json()
            assert "result" in result
            assert "latency" in result
            assert "model_name" in result
            assert result["model_name"] == "BLIP-2"
            assert len(result["result"]) > 0
    
    def test_medical_task_success(self):
        """Test successful medical image analysis task"""
        test_data = {
            "image_path": TEST_IMAGE_PATH,
            "question": ""
        }
        
        # Mock ResNet processor and model
        with patch('app.routers.tasks.AutoFeatureExtractor') as mock_extractor, \
             patch('app.routers.tasks.AutoModelForImageClassification') as mock_model:
            
            # Setup mocks
            mock_extractor_instance = MagicMock()
            mock_extractor.from_pretrained.return_value = mock_extractor_instance
            
            mock_model_instance = MagicMock()
            mock_model.from_pretrained.return_value = mock_model_instance
            
            mock_extractor_instance.return_tensors = "pt"
            mock_model_instance.return_value = torch.tensor([[0.1, 0.2, 0.3, 0.4]])
            
            # Make request
            response = client.post("/task/medical", json=test_data)
            
            # Assert response
            assert response.status_code == 200
            result = response.json()
            assert "result" in result
            assert "latency" in result
            assert "model_name" in result
            assert result["model_name"] == "ResNet-50"
            assert isinstance(result["result"], (int, str))
    
    def test_simocr_task_success(self):
        """Test successful simple OCR task"""
        test_data = {
            "image_path": TEST_IMAGE_PATH,
            "question": ""
        }
        
        # Mock paddleocr
        with patch('app.routers.tasks.paddleocr.PaddleOCR') as mock_ocr:
            mock_result = [[[[[10, 10], [100, 10], [100, 50], [10, 50]], ('STOP', 0.95)]]]
            mock_ocr_instance = MagicMock()
            mock_ocr_instance.ocr.return_value = mock_result
            mock_ocr.return_value = mock_ocr_instance
            
            # Make request
            response = client.post("/task/simocr", json=test_data)
            
            # Assert response
            assert response.status_code == 200
            result = response.json()
            assert "result" in result
            assert "latency" in result
            assert "model_name" in result
            assert result["model_name"] == "PaddleOCR (Simple)"
            assert "STOP" in result["result"]
    
    def test_other_task(self):
        """Test other task endpoint"""
        test_data = {
            "image_path": TEST_IMAGE_PATH,
            "question": ""
        }
        
        response = client.post("/task/other", json=test_data)
        
        # Assert response
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert "latency" in result
        assert "model_name" in result
        assert result["model_name"] == "None"
        assert result["result"] == "Task not supported"
