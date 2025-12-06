# ============================================
# 乾淨啟動 Bot（停止所有舊實例）
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  乾淨啟動 Bot" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 停止所有本地 Bot
Write-Host "停止所有本地 Bot 進程..." -ForegroundColor Yellow
$allBots = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
        if ($cmdLine) {
            $cmdLine -like "*bot*main.py*"
        } else {
            $false
        }
    } catch {
        $false
    }
}

if ($allBots) {
    Write-Host "  發現 $($allBots.Count) 個 Bot 進程，正在停止..." -ForegroundColor Yellow
    $allBots | ForEach-Object {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        Write-Host "    ✓ 已停止 PID: $($_.Id)" -ForegroundColor Green
    }
    Start-Sleep -Seconds 3
} else {
    Write-Host "  ✓ 沒有本地 Bot 進程" -ForegroundColor Green
}

Write-Host ""
Write-Host "等待 5 秒確保進程完全停止..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "啟動 Bot（當前終端，可以看到所有日誌）..." -ForegroundColor Green
Write-Host "按 Ctrl+C 可以停止 Bot" -ForegroundColor Cyan
Write-Host ""

Set-Location "c:\hbgm001\bot"
.venv\Scripts\Activate.ps1
python main.py
