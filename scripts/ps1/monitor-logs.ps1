# PowerShell 腳本 - 持續監控服務日誌

param(
    [string]$Server = "ubuntu@165.154.254.99",
    [int]$Duration = 60
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  服務日誌監控" -ForegroundColor Cyan
Write-Host "  監控時長: $Duration 秒" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$endTime = $startTime.AddSeconds($Duration)

Write-Host "開始監控服務日誌..." -ForegroundColor Green
Write-Host "按 Ctrl+C 可提前停止" -ForegroundColor Yellow
Write-Host ""

try {
    while ((Get-Date) -lt $endTime) {
        $elapsed = ((Get-Date) - $startTime).TotalSeconds
        $remaining = $Duration - $elapsed
        
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  監控中... (剩餘 $([math]::Round($remaining)) 秒)" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # 檢查 API 服務
        Write-Host "--- API 服務最新日誌 ---" -ForegroundColor Green
        ssh -o ConnectTimeout=5 $Server "sudo journalctl -u luckyred-api -n 5 --no-pager --since '30 seconds ago' 2>/dev/null | tail -3" 2>$null
        Write-Host ""
        
        # 檢查 Bot 服務
        Write-Host "--- Bot 服務最新日誌 ---" -ForegroundColor Green
        ssh -o ConnectTimeout=5 $Server "sudo journalctl -u luckyred-bot -n 5 --no-pager --since '30 seconds ago' 2>/dev/null | tail -3" 2>$null
        Write-Host ""
        
        # 檢查服務狀態
        Write-Host "--- 服務狀態 ---" -ForegroundColor Green
        ssh -o ConnectTimeout=5 $Server "echo 'API:' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo '  [運行中]' || echo '  [未運行]') && echo 'Bot:' && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo '  [運行中]' || echo '  [未運行]')" 2>$null
        Write-Host ""
        
        Start-Sleep -Seconds 10
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  監控完成" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # 生成最終報告
    Write-Host "生成最終錯誤報告..." -ForegroundColor Yellow
    ssh -o ConnectTimeout=10 $Server "echo '=== API 錯誤摘要 ===' && sudo journalctl -u luckyred-api --since '5 minutes ago' --no-pager | grep -i error | tail -10 && echo && echo '=== Bot 錯誤摘要 ===' && sudo journalctl -u luckyred-bot --since '5 minutes ago' --no-pager | grep -i error | tail -10" 2>$null
    
} catch {
    Write-Host ""
    Write-Host "監控過程中出現錯誤: $_" -ForegroundColor Red
}

