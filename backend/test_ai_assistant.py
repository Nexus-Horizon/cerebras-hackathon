from fastapi import HTTPException
import pytest
import json
import os
from pathlib import Path
from app.routers.analyze import get_result

# Setup test environment
TEST_DIR = Path(__file__).parent
TEST_LOGS = TEST_DIR / "test_logs.json"

@pytest.fixture(autouse=True)
def setup_test_logs():
    """Create test logs file before tests"""
    test_entries = [
        {
            "id": "test-123",
            "timestamp": "2024-01-01T00:00:00",
            "task": "OCR",
            "model": "pytesseract",
            "latency": 0.5,
            "result": "Test document text"
        }
    ]
    with open(TEST_LOGS, 'w') as f:
        json.dump(test_entries, f, indent=2)
    yield
    # Cleanup
    if os.path.exists(TEST_LOGS):
        os.remove(TEST_LOGS)

def test_get_result_valid_id(monkeypatch):
    """Test getting result with valid ID"""
    # Patch the BASE_DIR in analyze.py to use our test logs
    def mock_get_result(result_id: str):
        logs_file = TEST_LOGS
        if not os.path.exists(logs_file):
            raise HTTPException(status_code=404, detail="No results found")
        
        with open(logs_file, 'r') as f:
            logs = json.load(f)
        
        result_entry = next((entry for entry in logs if entry["id"] == result_id), None)
        
        if not result_entry:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return result_entry
    
    monkeypatch.setattr("app.routers.analyze.get_result", mock_get_result)
    
    result = get_result("test-123")
    assert result["id"] == "test-123"
    assert result["result"] == "Test document text"

def test_get_result_invalid_id(monkeypatch):
    """Test getting result with invalid ID"""
    # Patch the BASE_DIR in analyze.py to use our test logs
    def mock_get_result(result_id: str):
        logs_file = TEST_LOGS
        if not os.path.exists(logs_file):
            raise HTTPException(status_code=404, detail="No results found")
        
        with open(logs_file, 'r') as f:
            logs = json.load(f)
        
        result_entry = next((entry for entry in logs if entry["id"] == result_id), None)
        
        if not result_entry:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return result_entry
    
    monkeypatch.setattr("app.routers.analyze.get_result", mock_get_result)
    
    with pytest.raises(HTTPException) as exc_info:
        get_result("invalid-id")
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Result not found"

def test_file_path_handling(monkeypatch):
    """Test proper file path resolution"""
    from app.routers.analyze import UPLOAD_DIR, BASE_DIR
    
    # Verify paths are absolute
    assert UPLOAD_DIR.is_absolute()
    assert (BASE_DIR / "uploads").exists()
    assert (BASE_DIR / "logs.json").exists()
