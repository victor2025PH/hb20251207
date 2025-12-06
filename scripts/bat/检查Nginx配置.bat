@echo off
chcp 65001 >nul
echo ==========================================
echo   检查服务器 Nginx 配置
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 检查启用的站点...
ssh %SERVER% "ls -la /etc/nginx/sites-enabled/"
echo.

echo [2] 检查 mini.usdt2026.cc 配置...
ssh %SERVER% "cat /etc/nginx/sites-available/mini.usdt2026.cc.conf | head -10"
echo.

echo [3] 检查 admin.usdt2026.cc 配置...
ssh %SERVER% "cat /etc/nginx/sites-available/admin.usdt2026.cc.conf | head -10"
echo.

echo [4] 检查 Nginx 配置语法...
ssh %SERVER% "sudo nginx -t"
echo.

echo [5] 检查前端文件是否存在...
ssh %SERVER% "ls -la /opt/luckyred/frontend/dist/ | head -10"
echo.

pause

