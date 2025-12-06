@echo off
chcp 65001 >nul
echo ==========================================
echo   修复 MiniApp URL 配置
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1/4] 检查 .env 文件...
ssh %SERVER% "test -f %APP_DIR%/.env && echo '文件存在' || echo '文件不存在'"
echo.

echo [2/4] 备份 .env 文件...
ssh %SERVER% "cp %APP_DIR%/.env %APP_DIR%/.env.backup"
echo.

echo [3/4] 清理重复的 MINIAPP_URL 并设置正确值...
ssh %SERVER% "grep -v '^MINIAPP_URL=' %APP_DIR%/.env > %APP_DIR%/.env.tmp && mv %APP_DIR%/.env.tmp %APP_DIR%/.env && echo 'MINIAPP_URL=https://mini.usdt2026.cc' >> %APP_DIR%/.env"
echo.

echo [4/4] 验证配置...
ssh %SERVER% "grep MINIAPP_URL %APP_DIR%/.env"
echo.

echo ==========================================
echo   ✅ 配置已修复！
echo ==========================================
echo.
echo 现在重启 Bot 服务...
ssh %SERVER% "sudo systemctl restart luckyred-bot"
echo.
echo 检查服务状态...
ssh %SERVER% "sudo systemctl status luckyred-bot --no-pager -l | head -10"
echo.
pause

