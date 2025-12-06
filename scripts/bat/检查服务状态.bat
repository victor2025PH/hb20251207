@echo off
chcp 65001 >nul
echo ==========================================
echo   检查服务器服务状态
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [检查 API 服务状态]
ssh %SERVER% "sudo systemctl status luckyred-api --no-pager -l | head -20"
echo.
echo [检查 Bot 服务状态]
ssh %SERVER% "sudo systemctl status luckyred-bot --no-pager -l | head -20"
echo.
echo [检查服务是否运行中]
ssh %SERVER% "sudo systemctl is-active luckyred-api luckyred-bot"
echo.
pause

