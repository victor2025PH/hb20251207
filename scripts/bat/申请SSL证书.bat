@echo off
chcp 65001 >nul
echo ==========================================
echo   为 mini.usdt2026.cc 申请 SSL 证书
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 检查 certbot 是否已安装...
ssh %SERVER% "which certbot || echo 'certbot 未安装'"
echo.

echo [2] 上传 SSL 配置文件...
scp deploy\nginx\mini.usdt2026.cc-ssl.conf %SERVER%:/tmp/mini.usdt2026.cc-ssl.conf
echo.

echo [3] 临时启用 HTTP 配置（certbot 需要）...
ssh %SERVER% "sudo cp /tmp/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf"
ssh %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf"
ssh %SERVER% "sudo systemctl reload nginx"
echo.

echo [4] 申请 SSL 证书...
echo 注意：这需要域名 DNS 已正确解析到服务器
echo.
ssh %SERVER% "sudo certbot certonly --nginx -d mini.usdt2026.cc --non-interactive --agree-tos --email admin@usdt2026.cc 2>&1"
echo.

echo [5] 如果证书申请成功，启用 SSL 配置...
ssh %SERVER% "if [ -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem ]; then sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-enabled/mini.usdt2026.cc-ssl.conf && sudo systemctl reload nginx && echo 'SSL 配置已启用'; else echo '证书申请失败，请检查 DNS 配置'; fi"
echo.

pause
