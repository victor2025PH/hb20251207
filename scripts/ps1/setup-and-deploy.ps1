# ============================================
# Lucky Red 自動化部署腳本
# ============================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lucky Red 自動化部署" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 .env 文件
Write-Host "步驟 1: 檢查環境配置..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Write-Host "創建 .env 文件..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "警告: 已創建 .env 文件，請先配置必要的變量！" -ForegroundColor Red
    Write-Host "按 Enter 打開 .env 文件進行配置..." -ForegroundColor Yellow
    Read-Host | Out-Null
    notepad .env
}

# 檢查 Python
Write-Host "`n步驟 2: 檢查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 未安裝或不在 PATH 中" -ForegroundColor Red
    Write-Host "請先安裝 Python 3.10+ 並添加到 PATH" -ForegroundColor Yellow
    exit 1
}

# 設置 API 環境
Write-Host "`n步驟 3: 設置 API 環境..." -ForegroundColor Yellow
Set-Location api

if (-not (Test-Path .venv)) {
    Write-Host "創建 API 虛擬環境..." -ForegroundColor Cyan
    python -m venv .venv
    Write-Host "✓ 虛擬環境已創建" -ForegroundColor Green
}

Write-Host "激活虛擬環境並安裝依賴..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip | Out-Null
Write-Host "安裝 API 依賴（這可能需要幾分鐘）..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 依賴安裝失敗" -ForegroundColor Red
    deactivate
    Set-Location ..
    exit 1
}
Write-Host "✓ API 依賴安裝完成" -ForegroundColor Green
deactivate

Set-Location ..

# 設置 Bot 環境
Write-Host "`n步驟 4: 設置 Bot 環境..." -ForegroundColor Yellow
Set-Location bot

if (-not (Test-Path .venv)) {
    Write-Host "創建 Bot 虛擬環境..." -ForegroundColor Cyan
    python -m venv .venv
    Write-Host "✓ 虛擬環境已創建" -ForegroundColor Green
}

Write-Host "激活虛擬環境並安裝依賴..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip | Out-Null
Write-Host "安裝 Bot 依賴（這可能需要幾分鐘）..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 依賴安裝失敗" -ForegroundColor Red
    deactivate
    Set-Location ..
    exit 1
}
Write-Host "✓ Bot 依賴安裝完成" -ForegroundColor Green
deactivate

Set-Location ..

# 初始化數據庫
Write-Host "`n步驟 5: 初始化數據庫..." -ForegroundColor Yellow
Set-Location api
& .\.venv\Scripts\Activate.ps1

Write-Host "檢查數據庫連接..." -ForegroundColor Cyan
try {
    $initScript = 'from shared.database.connection import init_db; init_db(); print("✓ 數據庫初始化成功")'
    python -c $initScript
    if ($LASTEXITCODE -ne 0) {
        throw "初始化失敗"
    }
} catch {
    Write-Host "警告: 數據庫初始化可能失敗，請檢查：" -ForegroundColor Yellow
    Write-Host "  1. DATABASE_URL 是否正確配置" -ForegroundColor Cyan
    Write-Host "  2. 數據庫服務是否運行" -ForegroundColor Cyan
    Write-Host "  3. 數據庫用戶是否有權限" -ForegroundColor Cyan
}

deactivate
Set-Location ..

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署準備完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 啟動 API 服務器：" -ForegroundColor Cyan
Write-Host "   cd api" -ForegroundColor White
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn main:app --host 0.0.0.0 --port 8080 --reload" -ForegroundColor White
Write-Host ""
Write-Host "2. 啟動 Bot（新終端窗口）：" -ForegroundColor Cyan
Write-Host "   cd bot" -ForegroundColor White
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
Write-Host "3. 或使用快速啟動腳本：" -ForegroundColor Cyan
Write-Host "   .\start-services.ps1" -ForegroundColor White
Write-Host ""

$startNow = Read-Host "是否現在啟動服務？(Y/N)"
if ($startNow -eq "Y" -or $startNow -eq "y") {
    Write-Host ""
    Write-Host "啟動服務..." -ForegroundColor Green
    
    # 啟動 API
    $apiPath = Join-Path $PWD "api"
    $apiCmd = "cd '$apiPath'; .venv\Scripts\Activate.ps1; Write-Host 'API 服務器啟動中...' -ForegroundColor Green; uvicorn main:app --host 0.0.0.0 --port 8080 --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCmd
    
    # 等待一下
    Start-Sleep -Seconds 2
    
    # 啟動 Bot
    $botPath = Join-Path $PWD "bot"
    $botCmd = "cd '$botPath'; .venv\Scripts\Activate.ps1; Write-Host 'Bot 啟動中...' -ForegroundColor Green; python main.py"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
    
    Write-Host "✓ 服務已在新窗口中啟動" -ForegroundColor Green
    Write-Host ""
    Write-Host "API: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "API 文檔: http://localhost:8080/docs" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "部署完成！" -ForegroundColor Green
