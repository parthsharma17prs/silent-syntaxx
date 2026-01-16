# Hack-Vento 2K26 Backend Startup Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Hack-Vento 2K26 - Placement Portal Backend Server" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "$PSScriptRoot\backend"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$pythonCmd = if (Test-Path $venvPython) { $venvPython } else { "python" }

Write-Host "Checking Python environment..." -ForegroundColor Cyan
& $pythonCmd --version
Write-Host ""

Write-Host "Starting Flask server..." -ForegroundColor Green
Write-Host "Access the application at: http://localhost:5000" -ForegroundColor Magenta
Write-Host "Press Ctrl+C in this window to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start the Flask app directly
& $pythonCmd app.py