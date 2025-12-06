@echo off
chcp 65001 >nul
echo ==========================================
echo   检查 SSL 证书配置
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 检查启用的 Nginx 配置...
ssh %SERVER% "ls -la /etc/nginx/sites-enabled/ | grep mini"
echo.

echo [2] 检查 mini.usdt2026.cc 实际使用的配置...
ssh %SERVER% "cat /etc/nginx/sites-enabled/mini.usdt2026.cc.conf | grep -A 5 'server_name\|ssl_certificate\|root'"
echo.

echo [3] 检查证书文件是否存在...
ssh %SERVER% "ls -la /etc/letsencrypt/live/mini.usdt2026.cc/ 2>&1 | head -5"
echo.

echo [4] 检查 admin 证书（可能被错误使用）...
ssh %SERVER% "ls -la /etc/letsencrypt/live/admin.usdt2026.cc/ 2>&1 | head -5"
echo.

pause

