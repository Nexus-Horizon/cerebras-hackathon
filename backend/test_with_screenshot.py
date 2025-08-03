import requests
import json

def test_ocr_with_screenshot():
    """Test OCR with a screenshot that might have clearer text"""
    
    test_data = {
        "image_path": "uploads/Screenshot 2025-08-03 153541.png",
        "question": "Extract text from this image"
    }
    
    endpoints = ["ocr", "simocr"]
    
    for endpoint in endpoints:
        print(f"\n=== Testing {endpoint} endpoint with screenshot ===")
        try:
            response = requests.post(
                f"http://localhost:8000/task/{endpoint}",
                json=test_data,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Result: {result}")
                
                # Check if text was detected
                if "No text found in image" in result.get("result", ""):
                    print("❌ No text detected")
                else:
                    print("✅ Text detected!")
                    
                # Check for the problematic string
                if "naotoeeeeeeiee" in result.get("result", ""):
                    print("❌ ERROR: Found the problematic 'naotoeeeeeeiee' string!")
                else:
                    print("✅ No problematic string found!")
            else:
                print(f"❌ ERROR: Request failed with status {response.status_code}")
                print(f"Response text: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: Exception occurred: {e}")

if __name__ == "__main__":
    print("Testing OCR with screenshot...")
    test_ocr_with_screenshot() 