# ============================================
# 簡單的 Bot 測試腳本
# 在當前終端運行，可以看到所有日誌
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bot 測試（當前終端）" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意：Bot 將在當前終端運行" -ForegroundColor Yellow
Write-Host "按 Ctrl+C 可以停止 Bot" -ForegroundColor Yellow
Write-Host ""
Write-Host "正在啟動 Bot...`n" -ForegroundColor Green

$projectRoot = "c:\hbgm001"

# 停止現有 Bot
$botProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
        $cmdLine -like "*bot*main.py*"
    } catch {
        $false
    }
}
if ($botProcesses) {
    Write-Host "停止現有 Bot 進程..." -ForegroundColor Yellow
    $botProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

# 切換到 Bot 目錄並啟動
Set-Location "$projectRoot\bot"

if (Test-Path ".venv\Scripts\Activate.ps1") {
    .venv\Scripts\Activate.ps1
    Write-Host "虛擬環境已激活`n" -ForegroundColor Green
    Write-Host "開始啟動 Bot...`n" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Gray
    
    # 直接運行，日誌會顯示在這裡
    python main.py
} else {
    Write-Host "錯誤：找不到虛擬環境" -ForegroundColor Red
    Write-Host "請先運行: .\setup-and-deploy-fixed.ps1" -ForegroundColor Yellow
}
