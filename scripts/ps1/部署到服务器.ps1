# 部署到服务器 - 从 GitHub 下载并更新
# 可以在 Cursor 外的 PowerShell 中运行

$ErrorActionPreference = "Stop"
$SERVER = "ubuntu@165.154.254.99"
$APP_DIR = "/opt/luckyred"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  部署到服务器 - 从 GitHub 下载并更新" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "[1/5] 连接到服务器并更新代码..." -ForegroundColor Yellow
    ssh $SERVER "cd $APP_DIR; git pull origin master"
    if ($LASTEXITCODE -ne 0) { throw "Git 更新失败" }
    
    Write-Host ""
    Write-Host "[2/5] 重新构建前端..." -ForegroundColor Yellow
    ssh $SERVER "cd $APP_DIR/frontend; npm run build"
    if ($LASTEXITCODE -ne 0) { throw "前端构建失败" }
    
    Write-Host ""
    Write-Host "[3/5] 更新 Nginx 配置..." -ForegroundColor Yellow
    ssh $SERVER "sudo cp $APP_DIR/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf; sudo nginx -t; sudo systemctl reload nginx"
    if ($LASTEXITCODE -ne 0) { throw "Nginx 配置更新失败" }
    
    Write-Host ""
    Write-Host "[4/5] 重启 API 服务..." -ForegroundColor Yellow
    ssh $SERVER "sudo systemctl restart luckyred-api"
    if ($LASTEXITCODE -ne 0) { throw "API 服务重启失败" }
    
    Write-Host ""
    Write-Host "[5/5] 重启 Bot 服务..." -ForegroundColor Yellow
    ssh $SERVER "sudo systemctl restart luckyred-bot"
    if ($LASTEXITCODE -ne 0) { throw "Bot 服务重启失败" }
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  ✅ 部署完成！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "检查服务状态..." -ForegroundColor Yellow
    ssh $SERVER "sudo systemctl status luckyred-api --no-pager -l"
    Write-Host ""
    ssh $SERVER "sudo systemctl status luckyred-bot --no-pager -l"
    
} catch {
    Write-Host ""
    Write-Host "❌ 部署失败: $_" -ForegroundColor Red
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host ""
Read-Host "按 Enter 键退出"

