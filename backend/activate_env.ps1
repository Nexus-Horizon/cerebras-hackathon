# PowerShell script to activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\myenv\Scripts\Activate.ps1"

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  python -m pip install -r requirements.txt  - Install all dependencies" -ForegroundColor Cyan
Write-Host "  python run.py                            - Start the server" -ForegroundColor Cyan
Write-Host "  python -m pip list                       - List installed packages" -ForegroundColor Cyan
Write-Host "" 