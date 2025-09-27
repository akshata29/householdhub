# WealthOps Data Service Setup Script (PowerShell)
# This script creates a virtual environment and installs dependencies

Write-Host "🔧 Setting up WealthOps Data Service..." -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "venv")) {
    Write-Host "🐍 Creating Python virtual environment..." -ForegroundColor Blue
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment. Please ensure Python 3.11+ is installed." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment." -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Blue
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host "💡 Now you can run: .\start.ps1" -ForegroundColor Cyan