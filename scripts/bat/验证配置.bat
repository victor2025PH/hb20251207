@echo off
chcp 65001 >nul
echo ==========================================
echo   验证配置是否正确
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查 Nginx 配置（应该使用 HTTP，无 SSL）...
ssh %SERVER% "cat /etc/nginx/sites-enabled/mini.usdt2026.cc.conf | grep -E 'listen|server_name|root' | head -5"
echo.

echo [2] 检查 Bot 配置...
ssh %SERVER% "grep MINIAPP_URL %APP_DIR%/.env"
echo.

echo [3] 检查前端文件是否存在...
ssh %SERVER% "ls -la %APP_DIR%/frontend/dist/index.html"
echo.

echo [4] 检查 Nginx 服务状态...
ssh %SERVER% "sudo systemctl status nginx --no-pager -l | head -5"
echo.

echo [5] 检查 Bot 服务状态...
ssh %SERVER% "sudo systemctl status luckyred-bot --no-pager -l | head -5"
echo.

echo [6] 测试 HTTP 访问（应该返回前端页面）...
ssh %SERVER% "curl -I http://localhost 2>&1 | head -5"
echo.

echo ==========================================
echo   验证完成
echo ==========================================
echo.
pause

