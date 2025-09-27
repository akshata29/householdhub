# PowerShell script to stop all WealthOps backend services

Write-Host "Stopping WealthOps Backend Services..." -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Red

# Kill any Python processes that might be running our services
$processes = Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.MainWindowTitle -like "*uvicorn*" }

foreach ($process in $processes) {
    Write-Host "Stopping process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
}

# Also kill any uvicorn processes
$uvicornProcesses = Get-Process | Where-Object { $_.ProcessName -like "*uvicorn*" }

foreach ($process in $uvicornProcesses) {
    Write-Host "Stopping uvicorn process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "All services stopped!" -ForegroundColor Green