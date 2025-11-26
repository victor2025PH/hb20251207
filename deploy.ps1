# PowerShell 部署腳本 - 上傳到服務器並部署

param(
    [string]$Server = "ubuntu@usdt2026.cc",
    [string]$RemotePath = "/opt/luckyred"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LuckyRed 部署腳本 (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Git 操作
Write-Host "`n[1/4] Git 操作..." -ForegroundColor Green
Set-Location "C:\hbgm001"
git add -A
git status
$commitMsg = Read-Host "輸入提交信息 (直接回車使用默認)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}
git commit -m $commitMsg
git push origin master

# 2. SSH 到服務器拉取代碼
Write-Host "`n[2/4] 連接服務器..." -ForegroundColor Green
$sshCommands = @"
cd $RemotePath
git pull
cd frontend && npm install && npm run build
sudo systemctl restart luckyred-api luckyred-bot luckyred-admin
sudo systemctl status luckyred-api luckyred-bot luckyred-admin --no-pager
"@

ssh $Server $sshCommands

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "MiniApp: https://mini.usdt2026.cc"
Write-Host "Admin: https://admin.usdt2026.cc"

