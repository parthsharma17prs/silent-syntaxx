# Hack-Vento 2K26 Portal Frontend Startup Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Hack-Vento 2K26 - Portal Frontend" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Portal is now served by the unified Vite frontend." -ForegroundColor Yellow
Write-Host "Starting frontend dev server..." -ForegroundColor Green
Write-Host "Landing: http://localhost:3000/" -ForegroundColor Magenta
Write-Host "Portal:  http://localhost:3000/portal/index.html" -ForegroundColor Magenta
Write-Host "" 

& "$PSScriptRoot\start_frontend.ps1"
