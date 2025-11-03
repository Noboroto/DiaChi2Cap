# Test script for Windows PowerShell
# Chay localhost test server

Write-Host "[TEST] Khoi dong test server..." -ForegroundColor Cyan

# Kiem tra Flask
Write-Host "[CHECK] Kiem tra Flask..." -ForegroundColor Yellow
$flaskCheck = python -m pip show flask 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Flask chua duoc cai dat!" -ForegroundColor Red
    Write-Host "[INFO] Dang cai dat Flask..." -ForegroundColor Yellow
    python -m pip install flask
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Khong the cai dat Flask!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[OK] Flask da san sang" -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "TEST SERVER - LOCALHOST API" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "URL: http://localhost:5000" -ForegroundColor Yellow
Write-Host "API Key de test: testing-chuyen-doi-2-cap" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Nhan Ctrl+C de dung server" -ForegroundColor Yellow
Write-Host ""

# Chay test server
python test_server.py
