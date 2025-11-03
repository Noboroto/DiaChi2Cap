# Build script for Windows PowerShell
# Tao file exe portable tu app.py

Write-Host "[BUILD] Bat dau build ung dung thanh file exe..." -ForegroundColor Cyan

# Kiem tra PyInstaller
Write-Host "[CHECK] Kiem tra PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = python -m pip show pyinstaller 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] PyInstaller chua duoc cai dat!" -ForegroundColor Red
    Write-Host "[INFO] Dang cai dat PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Khong the cai dat PyInstaller!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[OK] PyInstaller da san sang" -ForegroundColor Green

# Kiem tra dependencies
Write-Host "[CHECK] Kiem tra cac thu vien can thiet..." -ForegroundColor Yellow
python -m pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Khong the cai dat dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Dependencies da san sang" -ForegroundColor Green

# Build exe
Write-Host "[BUILD] Dang build file exe..." -ForegroundColor Yellow
pyinstaller app.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Build thanh cong!" -ForegroundColor Green
    Write-Host "[INFO] File exe: dist\DiaChi2Cap.exe" -ForegroundColor Cyan
    
    if (Test-Path "dist\DiaChi2Cap.exe") {
        $fileSize = (Get-Item "dist\DiaChi2Cap.exe").Length / 1MB
        Write-Host ("[INFO] Kich thuoc: {0:N2} MB" -f $fileSize) -ForegroundColor Cyan
    }
} else {
    Write-Host "[ERROR] Build that bai!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[DONE] Hoan thanh!" -ForegroundColor Green
