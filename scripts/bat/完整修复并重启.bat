@echo off
chcp 65001 >nul
echo ==========================================
echo   完整修复：配置 + 重启服务
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1/5] 检查 .env 文件...
ssh %SERVER% "if [ ! -f %APP_DIR%/.env ]; then echo '❌ .env 文件不存在，需要创建'; else echo '✅ .env 文件存在'; fi"
echo.

echo [2/5] 确保 MINIAPP_URL 配置正确...
ssh %SERVER% "if grep -q '^MINIAPP_URL=' %APP_DIR%/.env 2>/dev/null; then sed -i 's|^MINIAPP_URL=.*|MINIAPP_URL=https://mini.usdt2026.cc|' %APP_DIR%/.env; else echo 'MINIAPP_URL=https://mini.usdt2026.cc' >> %APP_DIR%/.env; fi"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  如果文件不存在，将创建新文件...
    ssh %SERVER% "echo 'MINIAPP_URL=https://mini.usdt2026.cc' >> %APP_DIR%/.env"
)

echo.
echo [3/5] 验证配置...
ssh %SERVER% "grep MINIAPP_URL %APP_DIR%/.env"
echo.

echo [4/5] 重启 Bot 服务...
ssh %SERVER% "sudo systemctl restart luckyred-bot"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Bot 服务重启失败
    pause
    exit /b 1
)

echo.
echo [5/5] 检查服务状态...
ssh %SERVER% "sudo systemctl status luckyred-bot --no-pager -l | head -15"
echo.

echo ==========================================
echo   ✅ 修复完成！
echo ==========================================
echo.
echo 现在 Bot 应该使用正确的 MiniApp URL: https://mini.usdt2026.cc
echo.
pause

