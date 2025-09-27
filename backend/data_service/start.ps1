# WealthOps Data Service Startup Script (PowerShell)
# This script sets up and starts the data service on Windows

Write-Host "🚀 Starting WealthOps Data Service..." -ForegroundColor Green

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Please run .\setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment. Please run .\setup.ps1" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please update .env with your database credentials" -ForegroundColor Yellow
}

# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content ".env" | Where-Object {$_ -match "="} | ForEach-Object {
        $key, $value = $_ -split "=", 2
        if ($key -and $value -and -not $key.StartsWith("#")) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Get port from environment or use default
$port = $env:SERVICE_PORT
if (-not $port) { $port = "8010" }

$host = $env:SERVICE_HOST
if (-not $host) { $host = "localhost" }

# Check if the port is available
$portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Port $port is already in use. Trying next available port..." -ForegroundColor Yellow
    $port = [int]$port + 1
}

# Check if uvicorn is installed
$uvicornCheck = python -m uvicorn --help 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ uvicorn not found. Installing..." -ForegroundColor Red
    pip install uvicorn[standard]
}

# Start the service
Write-Host "🌐 Starting FastAPI service on http://$host:$port..." -ForegroundColor Green
Write-Host "📊 Health check available at: http://$host:$port/health" -ForegroundColor Cyan
Write-Host "📖 API documentation: http://$host:$port/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow

try {
    python -m uvicorn main:app --host $host --port $port --reload
}
catch {
    Write-Host "❌ Failed to start service. Error: $_" -ForegroundColor Red
    Write-Host "💡 Try running .\setup.ps1 first, or check if another service is using port $port" -ForegroundColor Cyan
    exit 1
}