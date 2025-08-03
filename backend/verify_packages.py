#!/usr/bin/env python3
"""
Script to verify that all required packages are properly installed
and accessible in the virtual environment.
"""

import sys
import subprocess
import importlib

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: {e}")
        return False

def check_python_path():
    """Check Python path and virtual environment"""
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[0]}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("❌ Not running in virtual environment")

def main():
    print("🔍 Package Verification")
    print("=" * 50)
    
    # Check Python environment
    check_python_path()
    print()
    
    # Check required packages
    print("Checking required packages:")
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("httpx", "httpx"),
        ("pytesseract", "pytesseract"),
        ("Pillow", "PIL"),
        ("torch", "torch"),
        ("transformers", "transformers"),
        ("paddleocr", "paddleocr"),
    ]
    
    all_good = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_good = False
    
    print()
    
    # Test importing from app
    print("Testing app imports:")
    try:
        sys.path.append('./app')
        from routers.tasks import router
        print("✅ App router imported successfully")
    except Exception as e:
        print(f"❌ App router import failed: {e}")
        all_good = False
    
    print()
    
    if all_good:
        print("🎉 All packages are properly installed and accessible!")
        print("VS Code should now recognize all packages.")
    else:
        print("❌ Some packages are missing or not accessible.")
        print("Try running: python -m pip install -r requirements.txt")

if __name__ == "__main__":
    main() 