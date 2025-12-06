# ============================================
# Lucky Red 完整重啟腳本
# 關閉所有進程並重啟前端、後端和 Bot
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lucky Red 完整重啟" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Get-Location
}

# ============================================
# 第一步：停止所有進程
# ============================================
Write-Host "第一步：停止所有進程..." -ForegroundColor Yellow
Write-Host ""

# 1. 停止 API 進程（uvicorn）
Write-Host "  檢查 API 進程..." -ForegroundColor Cyan
$apiProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
    $cmdLine -like "*uvicorn*" -or ($cmdLine -like "*api*main.py*" -and $cmdLine -like "*hbgm001*")
}
if ($apiProcesses) {
    Write-Host "    發現 $($apiProcesses.Count) 個 API 進程，正在停止..." -ForegroundColor Yellow
    $apiProcesses | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "      ✓ 已停止 PID: $($_.Id)" -ForegroundColor Green
        } catch {
            Write-Host "      ✗ 停止失敗 PID: $($_.Id) - $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "    ✓ 沒有運行中的 API 進程" -ForegroundColor Green
}

# 2. 停止 Bot 進程
Write-Host "  檢查 Bot 進程..." -ForegroundColor Cyan
$botProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
    $cmdLine -like "*bot*main.py*" -or ($cmdLine -like "*hbgm001\bot*" -and $cmdLine -notlike "*uvicorn*")
}
if ($botProcesses) {
    Write-Host "    發現 $($botProcesses.Count) 個 Bot 進程，正在停止..." -ForegroundColor Yellow
    $botProcesses | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "      ✓ 已停止 PID: $($_.Id)" -ForegroundColor Green
        } catch {
            Write-Host "      ✗ 停止失敗 PID: $($_.Id) - $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "    ✓ 沒有運行中的 Bot 進程" -ForegroundColor Green
}

# 3. 停止前端進程（node/vite）
Write-Host "  檢查前端進程..." -ForegroundColor Cyan
$frontendProcesses = Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
    $cmdLine -like "*vite*" -or ($cmdLine -like "*frontend*" -and $cmdLine -like "*hbgm001*")
}
if ($frontendProcesses) {
    Write-Host "    發現 $($frontendProcesses.Count) 個前端進程，正在停止..." -ForegroundColor Yellow
    $frontendProcesses | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "      ✓ 已停止 PID: $($_.Id)" -ForegroundColor Green
        } catch {
            Write-Host "      ✗ 停止失敗 PID: $($_.Id) - $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "    ✓ 沒有運行中的前端進程" -ForegroundColor Green
}

# 等待進程完全關閉
Write-Host ""
Write-Host "  等待進程完全關閉..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✓ 所有進程已停止" -ForegroundColor Green
Write-Host ""

# ============================================
# 第二步：檢查虛擬環境
# ============================================
Write-Host "第二步：檢查環境..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path "$projectRoot\api\.venv")) {
    Write-Host "  ✗ API 虛擬環境不存在" -ForegroundColor Red
    Write-Host "    請先運行: .\setup-and-deploy-fixed.ps1" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  ✓ API 虛擬環境存在" -ForegroundColor Green
}

if (-not (Test-Path "$projectRoot\bot\.venv")) {
    Write-Host "  ✗ Bot 虛擬環境不存在" -ForegroundColor Red
    Write-Host "    請先運行: .\setup-and-deploy-fixed.ps1" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  ✓ Bot 虛擬環境存在" -ForegroundColor Green
}

if (-not (Test-Path "$projectRoot\frontend\node_modules")) {
    Write-Host "  ⚠ 前端依賴未安裝，將自動安裝..." -ForegroundColor Yellow
    Write-Host "    正在安裝前端依賴..." -ForegroundColor Cyan
    Push-Location "$projectRoot\frontend"
    npm install
    Pop-Location
    Write-Host "  ✓ 前端依賴已安裝" -ForegroundColor Green
} else {
    Write-Host "  ✓ 前端依賴已安裝" -ForegroundColor Green
}

Write-Host ""

# ============================================
# 第三步：啟動所有服務
# ============================================
Write-Host "第三步：啟動所有服務..." -ForegroundColor Yellow
Write-Host ""

# 1. 啟動 API
Write-Host "  啟動 API 服務器..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot\api'; .venv\Scripts\Activate.ps1; Write-Host '🚀 API 服務器啟動中...' -ForegroundColor Green; Write-Host '📍 地址: http://localhost:8080' -ForegroundColor Cyan; Write-Host '📚 API 文檔: http://localhost:8080/docs' -ForegroundColor Cyan; Write-Host ''; uvicorn main:app --host 127.0.0.1 --port 8080 --reload"
)
Start-Sleep -Seconds 2
Write-Host "    ✓ API 服務器已啟動（窗口已打開）" -ForegroundColor Green

# 2. 等待 API 啟動
Write-Host "  等待 API 啟動..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# 3. 啟動 Bot
Write-Host "  啟動 Bot..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot\bot'; .venv\Scripts\Activate.ps1; Write-Host '🤖 Telegram Bot 啟動中...' -ForegroundColor Green; Write-Host ''; python main.py"
)
Start-Sleep -Seconds 2
Write-Host "    ✓ Bot 已啟動（窗口已打開）" -ForegroundColor Green

# 4. 啟動前端
Write-Host "  啟動前端開發服務器..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot\frontend'; Write-Host '🎨 前端開發服務器啟動中...' -ForegroundColor Green; Write-Host '📍 地址: http://localhost:3001' -ForegroundColor Cyan; Write-Host ''; npm run dev"
)
Start-Sleep -Seconds 2
Write-Host "    ✓ 前端開發服務器已啟動（窗口已打開）" -ForegroundColor Green

# ============================================
# 完成
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ 所有服務已重啟完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服務信息：" -ForegroundColor Yellow
Write-Host "  • API 服務器: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  • API 文檔: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host "  • 前端開發服務器: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  • Telegram Bot: 運行中（查看 Bot 窗口）" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示：" -ForegroundColor Yellow
Write-Host "  • 關閉對應的 PowerShell 窗口即可停止該服務" -ForegroundColor Gray
Write-Host "  • 所有服務都在獨立的窗口中運行" -ForegroundColor Gray
Write-Host "  • 如需再次重啟，運行此腳本即可" -ForegroundColor Gray
Write-Host ""
