# PowerShell script to start all WealthOps backend services locally

Write-Host "Starting WealthOps Backend Services..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r requirements.txt
} else {
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
}

# Set environment variables
$env:ENVIRONMENT = "development"
$env:DEBUG = "true"
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

# Start services in separate PowerShell windows
Write-Host "Starting Orchestrator on port 9000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH = '$PWD;`$env:PYTHONPATH'; cd orchestrator; python -m uvicorn main:app --host 0.0.0.0 --port 9000 --reload"

Start-Sleep -Seconds 3

Write-Host "Starting NL2SQL Agent on port 9001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH = '$PWD;`$env:PYTHONPATH'; cd nl2sql_agent; python -m uvicorn main:app --host 0.0.0.0 --port 9001 --reload"

Start-Sleep -Seconds 3

Write-Host "Starting Vector Agent on port 9002..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH = '$PWD;`$env:PYTHONPATH'; cd vector_agent; python -m uvicorn main:app --host 0.0.0.0 --port 9002 --reload"

Start-Sleep -Seconds 3

Write-Host "Starting API Agent on port 9003..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH = '$PWD;`$env:PYTHONPATH'; cd api_agent; python -m uvicorn main:app --host 0.0.0.0 --port 9003 --reload"

Write-Host ""
Write-Host "All services started!" -ForegroundColor Green
Write-Host "Orchestrator: http://localhost:9000/docs" -ForegroundColor Cyan
Write-Host "NL2SQL Agent: http://localhost:9001/docs" -ForegroundColor Cyan
Write-Host "Vector Agent: http://localhost:9002/docs" -ForegroundColor Cyan
Write-Host "API Agent: http://localhost:9003/docs" -ForegroundColor Cyan