@echo off
chcp 65001 >nul
echo ==========================================
echo   检查 Bot MiniApp URL 配置
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查 Bot .env 配置...
ssh %SERVER% "grep MINIAPP_URL %APP_DIR%/bot/.env"
echo.

echo [2] 检查 API .env 配置...
ssh %SERVER% "grep MINIAPP_URL %APP_DIR%/api/.env"
echo.

echo [3] 检查 Bot 日志中的 MiniApp URL...
ssh %SERVER% "sudo journalctl -u luckyred-bot -n 20 --no-pager | grep -i miniapp"
echo.

pause

