# ============================================
# 在可見窗口中啟動 Bot（可以看到日誌）
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  啟動 Bot（可見窗口）" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "c:\hbgm001"

# 停止現有 Bot
Write-Host "檢查並停止現有 Bot..." -ForegroundColor Cyan
$botProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
        $cmdLine -like "*bot*main.py*" -or ($cmdLine -like "*hbgm001\bot*" -and $cmdLine -notlike "*uvicorn*")
    } catch {
        $false
    }
}
if ($botProcesses) {
    Write-Host "  停止 $($botProcesses.Count) 個 Bot 進程..." -ForegroundColor Yellow
    $botProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

# 檢查環境
if (-not (Test-Path "$projectRoot\bot\.venv")) {
    Write-Host "  ✗ Bot 虛擬環境不存在" -ForegroundColor Red
    Write-Host "  請先運行: .\setup-and-deploy-fixed.ps1" -ForegroundColor Yellow
    exit 1
}

# 在新窗口中啟動 Bot
Write-Host "`n正在新窗口中啟動 Bot..." -ForegroundColor Green
Write-Host "  窗口標題: Lucky Red Bot" -ForegroundColor Cyan
Write-Host "  所有日誌將顯示在該窗口中`n" -ForegroundColor Cyan

$command = @"
cd '$projectRoot\bot'
.venv\Scripts\Activate.ps1
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  Lucky Red Bot 啟動日誌' -ForegroundColor Yellow
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '正在啟動 Bot...' -ForegroundColor Green
Write-Host 'Token: 8201090864...' -ForegroundColor Cyan
Write-Host ''
python main.py
Write-Host ''
Write-Host 'Bot 已停止，按任意鍵關閉窗口...' -ForegroundColor Yellow
pause
"@

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    $command
) -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "✅ Bot 已在新窗口中啟動！" -ForegroundColor Green
Write-Host ""
Write-Host "請查看新打開的 PowerShell 窗口：" -ForegroundColor Yellow
Write-Host "  • 窗口標題應該包含 'Lucky Red Bot'" -ForegroundColor White
Write-Host "  • 查看是否有 'Bot @username started!' 消息" -ForegroundColor White
Write-Host "  • 如果有錯誤，會顯示在該窗口中" -ForegroundColor White
Write-Host ""
Write-Host "然後在 Telegram 中發送 /start 測試" -ForegroundColor Cyan
Write-Host ""
