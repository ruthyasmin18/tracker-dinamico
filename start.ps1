# Levanta backend (puerto 8000) y frontend (puerto 5173) en paralelo.
# Uso (desde la carpeta tracker-dinamico):
#   .\start.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

# Backend
$backendCmd = "cd `"$root\backend`"; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Frontend
Start-Sleep -Seconds 2
$frontendCmd = "cd `"$root\frontend`"; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "Tracker Dinámico iniciado:" -ForegroundColor Green
Write-Host "  Backend  → http://127.0.0.1:8000  (docs en /docs)" -ForegroundColor Cyan
Write-Host "  Frontend → http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cierra cada ventana de PowerShell para detener los servicios." -ForegroundColor Yellow
