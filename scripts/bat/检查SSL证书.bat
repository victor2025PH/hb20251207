@echo off
chcp 65001 >nul
echo ==========================================
echo   检查 SSL 证书
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 检查 mini.usdt2026.cc 的 SSL 证书是否存在...
ssh %SERVER% "sudo test -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem && echo '证书存在' || echo '证书不存在'"
echo.

echo [2] 如果证书存在，检查证书信息...
ssh %SERVER% "sudo openssl x509 -in /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem -noout -subject -dates 2>/dev/null || echo '无法读取证书'"
echo.

echo [3] 检查是否有其他域名的证书...
ssh %SERVER% "sudo ls -la /etc/letsencrypt/live/ 2>/dev/null | grep usdt2026"
echo.

echo [4] 检查 Nginx SSL 配置...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -B 5 -A 5 'ssl_certificate.*mini.usdt2026.cc'"
echo.

pause

