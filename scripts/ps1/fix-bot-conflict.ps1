# ============================================
# 修復 Bot 衝突腳本
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修復 Bot 衝突" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 停止所有本地 Bot
Write-Host "1. 停止所有本地 Bot 進程..." -ForegroundColor Yellow
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
    Write-Host "  發現 $($allBots.Count) 個 Bot 進程：" -ForegroundColor Yellow
    $allBots | ForEach-Object {
        Write-Host "    PID: $($_.Id)" -ForegroundColor Cyan
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✓ 已停止所有本地 Bot" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "  ✓ 沒有本地 Bot 進程" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. 請在遠程服務器上執行以下命令：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ssh ubuntu@165.154.254.99" -ForegroundColor Cyan
Write-Host "  sudo systemctl stop luckyred-bot" -ForegroundColor White
Write-Host "  ps aux | grep bot | grep -v grep | awk '{print \$2}' | xargs kill -9" -ForegroundColor White
Write-Host ""

$response = Read-Host "  是否已經停止遠程服務器上的 Bot？(Y/N)"
if ($response -ne "Y" -and $response -ne "y") {
    Write-Host "  請先停止遠程 Bot，然後重新運行此腳本" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "3. 等待 10 秒確保連接釋放..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "4. 啟動本地 Bot..." -ForegroundColor Yellow
$projectRoot = "c:\hbgm001"
Set-Location "$projectRoot\bot"
.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bot 啟動中..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意：Bot 將在當前終端運行" -ForegroundColor Yellow
Write-Host "按 Ctrl+C 可以停止 Bot" -ForegroundColor Yellow
Write-Host ""

python main.py
