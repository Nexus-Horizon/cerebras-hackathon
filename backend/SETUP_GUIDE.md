# Backend Setup Guide

## Virtual Environment Setup

This project uses a Python virtual environment to manage dependencies. The virtual environment is located in the `myenv` directory.

### Activating the Virtual Environment

#### Windows (Command Prompt)
```cmd
myenv\Scripts\activate.bat
```

#### Windows (PowerShell)
```powershell
.\myenv\Scripts\Activate.ps1
```

#### Using the provided scripts
```cmd
# Command Prompt
activate_env.bat

# PowerShell
.\activate_env.ps1
```

### Installing Dependencies

Once the virtual environment is activated, install the required packages:

```bash
python -m pip install -r requirements.txt
```

### Running the Application

Start the FastAPI server:

```bash
python run.py
```

The server will start on `http://127.0.0.1:8000`

### Available Endpoints

- `/task/ocr` - Extract text from images using PaddleOCR
- `/task/caption` - Generate image captions using BLIP-2
- `/task/vqa` - Visual Question Answering using BLIP-2
- `/task/medical` - Medical image analysis using ResNet-50
- `/task/simocr` - Simple OCR using PaddleOCR
- `/task/other` - Handle other tasks

### Troubleshooting

#### MMOCR Compilation Error (FIXED)
The original error with MMOCR compilation has been resolved by:
1. Removing MMOCR dependencies from the code
2. Replacing MMOCR functionality with PaddleOCR
3. Installing pre-compiled packages instead of building from source

#### Package Recognition Issues
If VS Code doesn't recognize packages:
1. Ensure VS Code is using the correct Python interpreter
2. Check `.vscode/settings.json` points to `myenv\Scripts\python.exe`
3. Reload VS Code window if needed

#### Virtual Environment Issues
If the virtual environment doesn't activate:
1. Check that `myenv` directory exists
2. Try recreating the virtual environment:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate
   python -m pip install -r requirements.txt
   ```

### Development

The application structure:
```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   └── routers/
│       └── tasks.py         # Task endpoints
├── myenv/                   # Virtual environment
├── requirements.txt         # Python dependencies
├── run.py                  # Server startup script
└── .vscode/
    └── settings.json       # VS Code configuration
```

### Dependencies

Key packages used:
- **FastAPI**: Web framework
- **PaddleOCR**: OCR functionality (replaces MMOCR)
- **Transformers**: BLIP-2 models for caption and VQA
- **PyTorch**: Deep learning framework
- **Pillow**: Image processing
- **Pytesseract**: Additional OCR support 