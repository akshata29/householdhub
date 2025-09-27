# WealthOps Data Service Troubleshooting Script
# This script checks common issues and provides solutions

Write-Host "🔍 WealthOps Data Service Troubleshooting" -ForegroundColor Cyan
Write-Host "=" * 50

# Check Python installation
Write-Host "`n1. Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python not found or not in PATH" -ForegroundColor Red
        Write-Host "💡 Please install Python 3.11+ from https://python.org" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Python not found: $_" -ForegroundColor Red
}

# Check virtual environment
Write-Host "`n2. Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    
    # Check if venv can be activated
    try {
        & "venv\Scripts\Activate.ps1" 2>$null
        Write-Host "✅ Virtual environment can be activated" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Virtual environment found but cannot be activated" -ForegroundColor Yellow
        Write-Host "💡 Try deleting 'venv' folder and running .\setup.ps1" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Virtual environment not found" -ForegroundColor Red
    Write-Host "💡 Run .\setup.ps1 to create virtual environment" -ForegroundColor Cyan
}

# Check dependencies
Write-Host "`n3. Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Write-Host "✅ Requirements file found" -ForegroundColor Green
    
    if (Test-Path "venv") {
        & "venv\Scripts\Activate.ps1" 2>$null
        $packages = pip list --format=freeze 2>$null
        if ($packages -match "fastapi") {
            Write-Host "✅ FastAPI installed" -ForegroundColor Green
        } else {
            Write-Host "❌ FastAPI not installed" -ForegroundColor Red
            Write-Host "💡 Run .\setup.ps1 to install dependencies" -ForegroundColor Cyan
        }
        
        if ($packages -match "uvicorn") {
            Write-Host "✅ Uvicorn installed" -ForegroundColor Green
        } else {
            Write-Host "❌ Uvicorn not installed" -ForegroundColor Red
            Write-Host "💡 Run .\setup.ps1 to install dependencies" -ForegroundColor Cyan
        }
        
        if ($packages -match "pyodbc") {
            Write-Host "✅ PyODBC installed" -ForegroundColor Green
        } else {
            Write-Host "❌ PyODBC not installed" -ForegroundColor Red
            Write-Host "💡 Run .\setup.ps1 to install dependencies" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "❌ Requirements file not found" -ForegroundColor Red
}

# Check .env file
Write-Host "`n4. Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
    
    $envContent = Get-Content ".env" | Where-Object { $_ -match "=" -and -not $_.StartsWith("#") }
    foreach ($line in $envContent) {
        $key, $value = $line -split "=", 2
        if ($key -eq "SERVICE_HOST") {
            Write-Host "  📍 Host: $value" -ForegroundColor White
        }
        if ($key -eq "SERVICE_PORT") {
            Write-Host "  🔌 Port: $value" -ForegroundColor White
        }
    }
} else {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    Write-Host "💡 Copy .env.example to .env and configure your settings" -ForegroundColor Cyan
}

# Check port availability
Write-Host "`n5. Checking port availability..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    $portLine = $envContent | Where-Object { $_ -match "SERVICE_PORT=" }
    if ($portLine) {
        $port = ($portLine -split "=")[1]
        $portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($portInUse) {
            Write-Host "❌ Port $port is already in use" -ForegroundColor Red
            Write-Host "💡 Change SERVICE_PORT in .env to a different port (e.g., 8010)" -ForegroundColor Cyan
        } else {
            Write-Host "✅ Port $port is available" -ForegroundColor Green
        }
    }
}

# Check main.py file
Write-Host "`n6. Checking main application file..." -ForegroundColor Yellow
if (Test-Path "main.py") {
    Write-Host "✅ main.py found" -ForegroundColor Green
} else {
    Write-Host "❌ main.py not found" -ForegroundColor Red
}

Write-Host "`n" + "=" * 50
Write-Host "🏁 Troubleshooting Summary" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you see any ❌ issues above, here's what to do:" -ForegroundColor White
Write-Host ""
Write-Host "1. 🔧 First time setup: .\setup.ps1" -ForegroundColor Green
Write-Host "2. 🚀 Start the service: .\start.ps1" -ForegroundColor Green  
Write-Host "3. 🧪 Test the service: curl http://localhost:8010/health" -ForegroundColor Green
Write-Host ""
Write-Host "Need help? Check the DATA_ARCHITECTURE.md file" -ForegroundColor Cyan