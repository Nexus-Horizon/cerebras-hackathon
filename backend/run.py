#!/usr/bin/env python
import uvicorn
import os

if __name__ == "__main__":
    # Add the current directory to Python path
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
