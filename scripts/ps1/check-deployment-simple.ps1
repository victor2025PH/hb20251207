# PowerShell 簡單部署檢查腳本

param(
    [string]$Server = "ubuntu@165.154.254.99"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LuckyRed 部署狀態檢查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "正在檢查服務狀態..." -ForegroundColor Green
    Write-Host ""
    
    # 檢查服務狀態
    Write-Host "=== 1. 服務運行狀態 ===" -ForegroundColor Yellow
    ssh $Server "sudo systemctl status luckyred-api --no-pager -l | head -20"
    Write-Host ""
    ssh $Server "sudo systemctl status luckyred-bot --no-pager -l | head -20"
    Write-Host ""
    ssh $Server "sudo systemctl status nginx --no-pager | head -10"
    Write-Host ""
    
    # 檢查目錄
    Write-Host "=== 2. 檢查部署目錄 ===" -ForegroundColor Yellow
    ssh $Server "ls -la /opt/luckyred 2>/dev/null | head -10 || echo '目錄不存在'"
    Write-Host ""
    
    # 檢查環境變量文件
    Write-Host "=== 3. 檢查環境變量文件 ===" -ForegroundColor Yellow
    ssh $Server "test -f /opt/luckyred/.env && echo '✅ .env文件存在' || echo '❌ .env文件不存在'"
    Write-Host ""
    
    # 檢查虛擬環境
    Write-Host "=== 4. 檢查虛擬環境 ===" -ForegroundColor Yellow
    ssh $Server "test -d /opt/luckyred/api/.venv && echo '✅ API虛擬環境存在' || echo '❌ API虛擬環境不存在'"
    ssh $Server "test -d /opt/luckyred/bot/.venv && echo '✅ Bot虛擬環境存在' || echo '❌ Bot虛擬環境不存在'"
    Write-Host ""
    
    # 檢查前端
    Write-Host "=== 5. 檢查前端文件 ===" -ForegroundColor Yellow
    ssh $Server "test -d /opt/luckyred/frontend/dist && echo '✅ 前端dist目錄存在' || echo '❌ 前端dist目錄不存在'"
    Write-Host ""
    
    # 檢查 Nginx
    Write-Host "=== 6. 檢查 Nginx 配置 ===" -ForegroundColor Yellow
    ssh $Server "sudo nginx -t"
    Write-Host ""
    
    # 檢查端口
    Write-Host "=== 7. 檢查端口監聽 ===" -ForegroundColor Yellow
    ssh $Server "sudo netstat -tlnp 2>/dev/null | grep -E ':(80|443|8080)' || echo '未發現監聽端口'"
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  檢查完成" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "錯誤: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

