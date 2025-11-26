# 上傳檢查腳本到服務器

param(
    [string]$Server = "ubuntu@165.154.254.99",
    [string]$RemotePath = "/opt/luckyred"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  上傳檢查腳本到服務器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "正在上傳 check_deployment.sh 到服務器..." -ForegroundColor Green
    
    # 使用 SCP 上傳文件
    scp check_deployment.sh "${Server}:${RemotePath}/check_deployment.sh"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 上傳成功！" -ForegroundColor Green
        Write-Host ""
        Write-Host "現在可以執行檢查：" -ForegroundColor Yellow
        Write-Host "  ssh $Server 'bash $RemotePath/check_deployment.sh'" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ 上傳失敗" -ForegroundColor Red
    }
}
catch {
    Write-Host ""
    Write-Host "錯誤: $($_.Exception.Message)" -ForegroundColor Red
}

