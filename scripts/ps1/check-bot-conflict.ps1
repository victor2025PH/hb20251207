# ============================================
# 檢查 Bot 衝突腳本
# 分析是否有多個 Bot 實例導致衝突
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bot 衝突檢查工具" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查本地 Bot 進程
Write-Host "1. 檢查本地 Bot 進程..." -ForegroundColor Yellow
$localBots = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
        $cmdLine -like "*bot*main.py*" -or ($cmdLine -like "*hbgm001\bot*" -and $cmdLine -notlike "*uvicorn*")
    } catch {
        $false
    }
}

if ($localBots) {
    Write-Host "  ⚠ 發現 $($localBots.Count) 個本地 Bot 進程：" -ForegroundColor Yellow
    $localBots | ForEach-Object {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
            Write-Host "    PID: $($_.Id)" -ForegroundColor Cyan
            Write-Host "      啟動時間: $($_.StartTime)" -ForegroundColor White
            Write-Host "      命令行: $($cmdLine.Substring(0, [Math]::Min(100, $cmdLine.Length)))" -ForegroundColor Gray
        } catch {}
    }
    Write-Host ""
    Write-Host "  💡 建議：停止多餘的 Bot 進程" -ForegroundColor Yellow
    $response = Read-Host "  是否停止所有 Bot 進程？(Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        $localBots | ForEach-Object {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "    ✓ 已停止 PID: $($_.Id)" -ForegroundColor Green
        }
        Write-Host "  ✓ 所有本地 Bot 進程已停止" -ForegroundColor Green
    }
} else {
    Write-Host "  ✓ 沒有本地 Bot 進程" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. 檢查可能的衝突原因：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  可能的原因：" -ForegroundColor Cyan
Write-Host "  • 遠程服務器上的 Bot 實例（使用相同的 BOT_TOKEN）" -ForegroundColor White
Write-Host "  • Telegram API 限制：同一 Token 只能有一個 getUpdates 連接" -ForegroundColor White
Write-Host "  • 本地多個 Bot 實例同時運行" -ForegroundColor White
Write-Host "  • Bot 沒有正確關閉，進程仍在運行" -ForegroundColor White

Write-Host ""
Write-Host "3. 檢查 Bot Token 配置：" -ForegroundColor Yellow
if (Test-Path "c:\hbgm001\.env") {
    $envContent = Get-Content "c:\hbgm001\.env" -ErrorAction SilentlyContinue
    $hasToken = ($envContent | Select-String -Pattern "^BOT_TOKEN=").Line -notlike "*your_telegram_bot_token*" -and ($envContent | Select-String -Pattern "^BOT_TOKEN=").Line.Length -gt 20
    if ($hasToken) {
        Write-Host "  ✓ Bot Token 已配置" -ForegroundColor Green
        Write-Host "  ⚠ 如果遠程服務器也使用相同的 Token，會導致衝突" -ForegroundColor Yellow
    } else {
        Write-Host "  ✗ Bot Token 未正確配置" -ForegroundColor Red
    }
} else {
    Write-Host "  ✗ .env 文件不存在" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. 解決方案：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  如果確認有衝突：" -ForegroundColor Cyan
Write-Host "  1. 停止所有 Bot 實例（本地和遠程）" -ForegroundColor White
Write-Host "  2. 等待 5-10 秒" -ForegroundColor White
Write-Host "  3. 只啟動一個 Bot 實例" -ForegroundColor White
Write-Host "  4. 檢查 Bot 日誌是否有衝突錯誤" -ForegroundColor White
Write-Host ""
Write-Host "  檢查遠程服務器：" -ForegroundColor Cyan
Write-Host "  • 如果使用 systemd：sudo systemctl stop luckyred-bot" -ForegroundColor White
Write-Host "  • 如果使用 screen/tmux：檢查是否有其他會話" -ForegroundColor White
Write-Host "  • 檢查服務器進程：ps aux | grep bot" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  檢查完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
