#!/usr/bin/env python
"""
Test script to verify backend imports correctly
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

try:
    from app.main import app
    print("✅ Backend imports successfully!")
    print(f"✅ FastAPI app created with title: {getattr(app, 'title', 'Unknown')}")
    
    # Print available routes
    print("\n📋 Available routes:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            print(f"  {methods} {route.path}")
        else:
            print(f"  {route.path}")
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
