@echo off
chcp 65001 >nul
echo ==========================================
echo   修复 Telegram MiniApp SSL 证书
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查证书是否存在...
ssh %SERVER% "sudo test -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem && echo '证书存在' || echo '证书不存在'"
echo.

echo [2] 如果证书不存在，申请证书...
ssh %SERVER% "if [ ! -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem ]; then echo '开始申请证书...'; sudo certbot certonly --nginx -d mini.usdt2026.cc --non-interactive --agree-tos --email admin@usdt2026.cc --keep-until-expiring 2>&1; else echo '证书已存在'; fi"
echo.

echo [3] 上传 SSL 配置文件...
scp deploy\nginx\mini.usdt2026.cc-ssl.conf %SERVER%:/tmp/mini.usdt2026.cc-ssl.conf
echo.

echo [4] 复制 SSL 配置到正确位置...
ssh %SERVER% "sudo cp /tmp/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf"
echo.

echo [5] 启用 SSL 配置...
ssh %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-enabled/mini.usdt2026.cc-ssl.conf"
echo.

echo [6] 验证配置...
ssh %SERVER% "sudo nginx -t"
if errorlevel 1 (
    echo 配置语法错误！
    pause
    exit /b 1
)
echo.

echo [7] 重新加载 Nginx...
ssh %SERVER% "sudo systemctl reload nginx"
echo.

echo [8] 测试 HTTPS 访问...
ssh %SERVER% "curl -k -I https://mini.usdt2026.cc 2>&1 | head -5"
echo.

echo [9] 检查证书信息...
ssh %SERVER% "echo | timeout 5 openssl s_client -connect mini.usdt2026.cc:443 -servername mini.usdt2026.cc 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null || echo '无法连接 HTTPS'"
echo.

echo [10] 更新 Bot 配置为 HTTPS...
ssh %SERVER% "sed -i 's|^MINIAPP_URL=.*|MINIAPP_URL=https://mini.usdt2026.cc|' %APP_DIR%/.env && grep MINIAPP_URL %APP_DIR%/.env"
echo.

echo [11] 重启 Bot 服务...
ssh %SERVER% "sudo systemctl restart luckyred-bot && sudo systemctl status luckyred-bot --no-pager -l | head -5"
echo.

echo ==========================================
echo   修复完成
echo ==========================================
echo.
echo 现在请在 Telegram 中测试 MiniApp
echo.
pause

