@echo off
chcp 65001 >nul
echo ==========================================
echo   重启所有服务
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1/3] 重启 API 服务...
ssh %SERVER% "sudo systemctl restart luckyred-api"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ API 服务重启失败
    pause
    exit /b 1
)

echo.
echo [2/3] 重启 Bot 服务...
ssh %SERVER% "sudo systemctl restart luckyred-bot"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Bot 服务重启失败
    pause
    exit /b 1
)

echo.
echo [3/3] 检查服务状态...
ssh %SERVER% "sudo systemctl status luckyred-api --no-pager -l | head -15"
echo.
ssh %SERVER% "sudo systemctl status luckyred-bot --no-pager -l | head -15"

echo.
echo ==========================================
echo   ✅ 服务重启完成！
echo ==========================================
echo.
pause

