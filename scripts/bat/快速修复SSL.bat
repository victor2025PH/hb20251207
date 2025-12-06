@echo off
chcp 65001 >nul
echo ==========================================
echo   快速修复 SSL 证书问题
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 检查证书是否存在...
ssh %SERVER% "sudo test -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem && echo '证书存在' || echo '证书不存在，需要申请'"
echo.

echo [2] 如果证书存在，启用 SSL 配置...
ssh %SERVER% "if [ -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem ]; then echo '证书存在，启用 SSL 配置...'; sudo cp /opt/luckyred/deploy/nginx/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf; sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-enabled/mini.usdt2026.cc-ssl.conf; sudo nginx -t && sudo systemctl reload nginx && echo 'SSL 配置已启用'; else echo '证书不存在，请先运行 申请SSL证书.bat'; fi"
echo.

echo [3] 验证 HTTPS 访问...
ssh %SERVER% "curl -k -I https://mini.usdt2026.cc 2>&1 | head -5"
echo.

echo [4] 检查证书信息...
ssh %SERVER% "echo | openssl s_client -connect mini.usdt2026.cc:443 -servername mini.usdt2026.cc 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null || echo '无法连接 HTTPS'"
echo.

pause

