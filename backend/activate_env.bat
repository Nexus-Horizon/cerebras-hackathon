@echo off
echo Activating virtual environment...
call myenv\Scripts\activate.bat
echo Virtual environment activated!
echo.
echo Available commands:
echo   python -m pip install -r requirements.txt  - Install all dependencies
echo   python run.py                            - Start the server
echo   python -m pip list                       - List installed packages
echo.
cmd /k 