# Hack-Vento 2K26 Frontend Startup Script (Unified)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Hack-Vento 2K26 - Frontend (Landing + Portal)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "$PSScriptRoot\frontend"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Stop any process currently using port 3000 (usually the old python http.server)
try {
  $conn = Get-NetTCPConnection -LocalPort 3000 -ErrorAction Stop | Select-Object -First 1
  if ($conn -and $conn.OwningProcess) {
    $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
    if ($proc) {
      Write-Host "Port 3000 is in use by $($proc.ProcessName) (PID $($proc.Id)). Stopping it..." -ForegroundColor Yellow
      Stop-Process -Id $proc.Id -Force
      Start-Sleep -Milliseconds 400
    }
  }
} catch {
  # Port not in use
}

Write-Host "Checking Node/NPM..." -ForegroundColor Cyan
node --version
npm --version
Write-Host ""

if (-not (Test-Path "node_modules")) {
  Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
  npm install
  if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
  Write-Host ""
}

Write-Host "Starting Vite dev server..." -ForegroundColor Green
Write-Host "Landing: http://localhost:3000/" -ForegroundColor Magenta
Write-Host "Portal:  http://localhost:3000/portal/index.html" -ForegroundColor Magenta
Write-Host "Press Ctrl+C in this window to stop" -ForegroundColor Yellow
Write-Host ""

npm run dev
