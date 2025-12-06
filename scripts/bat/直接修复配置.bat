@echo off
chcp 65001 >nul
echo ==========================================
echo   直接修复配置 - 使用 HTTP（避免 SSL 证书问题）
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1/3] 使用 HTTP 配置（无 SSL）...
ssh %SERVER% "sudo cp %APP_DIR%/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf"
echo ✅ 配置已复制

echo.
echo [2/3] 启用配置...
ssh %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf"
echo ✅ 配置已启用

echo.
echo [3/3] 测试并重载 Nginx...
ssh %SERVER% "sudo nginx -t && sudo systemctl reload nginx"
echo ✅ Nginx 已重载

echo.
echo [4/4] 更新 Bot 配置为 HTTP...
ssh %SERVER% "sed -i 's|^MINIAPP_URL=.*|MINIAPP_URL=http://mini.usdt2026.cc|' %APP_DIR%/.env && grep MINIAPP_URL %APP_DIR%/.env"
echo.

echo [5/5] 重启 Bot...
ssh %SERVER% "sudo systemctl restart luckyred-bot"
echo ✅ Bot 已重启

echo.
echo ==========================================
echo   ✅ 修复完成！
echo ==========================================
echo.
echo 现在使用 HTTP 访问，避免 SSL 证书问题
echo MiniApp URL: http://mini.usdt2026.cc
echo.
pause

