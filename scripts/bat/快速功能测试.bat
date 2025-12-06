@echo off
chcp 65001 >nul
echo ==========================================
echo   MiniApp 功能快速测试
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查服务状态...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl status luckyred-api --no-pager -l | head -5 && echo '---' && sudo systemctl status luckyred-bot --no-pager -l | head -5" 2>&1
echo.

echo [2] 检查 API 健康状态...
ssh -o ConnectTimeout=10 %SERVER% "curl -s http://127.0.0.1:8080/health 2>&1 | head -10" 2>&1
echo.

echo [3] 检查数据库连接...
ssh -o ConnectTimeout=10 %SERVER% "sudo -u postgres psql -d luckyred -c 'SELECT COUNT(*) FROM users;' 2>&1 | head -5" 2>&1
echo.

echo [4] 检查前端文件...
ssh -o ConnectTimeout=10 %SERVER% "ls -lh %APP_DIR%/frontend/dist/index.html && echo '---' && du -sh %APP_DIR%/frontend/dist" 2>&1
echo.

echo [5] 检查 Nginx 配置...
ssh -o ConnectTimeout=10 %SERVER% "sudo nginx -t 2>&1" | findstr /C:"syntax is ok" /C:"test is successful" /C:"error"
echo.

echo [6] 测试 HTTPS 访问...
ssh -o ConnectTimeout=10 %SERVER% "curl -k -I https://mini.usdt2026.cc 2>&1 | head -5" 2>&1
echo.

echo [7] 检查 Bot 配置...
ssh -o ConnectTimeout=10 %SERVER% "grep -E 'MINIAPP_URL|BOT_TOKEN' %APP_DIR%/.env | sed 's/BOT_TOKEN=.*/BOT_TOKEN=***/' 2>&1" 2>&1
echo.

echo [8] 查看最近的错误日志...
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-api -u luckyred-bot --since '5 minutes ago' --no-pager | grep -i error | tail -5" 2>&1
echo.

echo ==========================================
echo   测试完成
echo ==========================================
echo.
echo 如果所有检查都正常，可以开始功能测试
echo 请参考：下一步测试清单.md
echo.
pause

