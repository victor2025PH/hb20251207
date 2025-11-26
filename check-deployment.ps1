# PowerShell 部署檢查腳本

param(
    [string]$Server = "ubuntu@165.154.254.99",
    [string]$RemotePath = "/opt/luckyred"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LuckyRed 部署狀態檢查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服務器: $Server" -ForegroundColor Yellow
Write-Host "路徑: $RemotePath" -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "正在連接到服務器..." -ForegroundColor Green
    Write-Host ""
    
    # 執行服務器上的檢查腳本
    $checkScript = "$RemotePath/check_deployment.sh"
    Write-Host "執行檢查腳本..." -ForegroundColor Green
    ssh $Server "bash $checkScript"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  檢查完成" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "錯誤: 無法連接到服務器" -ForegroundColor Red
    Write-Host "請確認:" -ForegroundColor Yellow
    Write-Host "  1. SSH 密鑰已配置" -ForegroundColor Yellow
    Write-Host "  2. 服務器地址正確: $Server" -ForegroundColor Yellow
    Write-Host "  3. 網絡連接正常" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "錯誤詳情: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
