@echo off
chcp 65001 >nul
echo ==========================================
echo   修复 SSL 配置 - 使用正确的证书
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1/4] 检查当前配置...
ssh %SERVER% "cat /etc/nginx/sites-enabled/mini.usdt2026.cc.conf | grep ssl_certificate"
echo.

echo [2/4] 检查证书文件...
ssh %SERVER% "if [ -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem ]; then echo '✅ mini.usdt2026.cc 证书存在'; else echo '❌ mini.usdt2026.cc 证书不存在'; fi"
echo.

echo [3/4] 如果证书不存在，暂时使用 HTTP 配置...
ssh %SERVER% "if [ ! -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem ]; then sudo cp %APP_DIR%/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf && sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf && echo '已切换到 HTTP 配置'; else echo '证书存在，检查配置...'; fi"
echo.

echo [4/4] 如果证书存在但配置错误，修复 SSL 配置...
ssh %SERVER% "if [ -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem ]; then sudo cp %APP_DIR%/deploy/nginx/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf && sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf && echo '已更新为 SSL 配置'; fi"
echo.

echo 测试 Nginx 配置...
ssh %SERVER% "sudo nginx -t"
echo.

echo 重载 Nginx...
ssh %SERVER% "sudo systemctl reload nginx"
echo.

echo ==========================================
echo   ✅ 配置已修复！
echo ==========================================
echo.
pause

