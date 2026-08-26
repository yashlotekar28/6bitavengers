Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting ProcureShield AI - GeM Verification Prototype" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Start FastAPI Backend in background job
Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
$BackendJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} -ArgumentList "$PSScriptRoot\backend"

Start-Sleep -Seconds 2

# Start Frontend Vite Server
Write-Host "[2/2] Starting React + Vite Frontend on http://localhost:5173..." -ForegroundColor Green
Set-Location "$PSScriptRoot\frontend"
npm run dev
