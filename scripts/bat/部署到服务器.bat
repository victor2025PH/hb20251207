@echo off
chcp 65001 >nul
echo ==========================================
echo   部署到服务器 - 从 GitHub 下载并更新
echo ==========================================
echo.

REM 服务器信息
set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1/5] 连接到服务器并更新代码...
ssh %SERVER% "cd %APP_DIR% && git pull origin master"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git 更新失败
    pause
    exit /b 1
)

echo.
echo [2/5] 重新构建前端...
ssh %SERVER% "cd %APP_DIR%/frontend && npm run build"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 前端构建失败
    pause
    exit /b 1
)

echo.
echo [3/5] 更新 Nginx 配置...
ssh %SERVER% "sudo cp %APP_DIR%/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf && sudo nginx -t && sudo systemctl reload nginx"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Nginx 配置更新失败
    pause
    exit /b 1
)

echo.
echo [4/5] 重启 API 服务...
ssh %SERVER% "sudo systemctl restart luckyred-api"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ API 服务重启失败
    pause
    exit /b 1
)

echo.
echo [5/5] 重启 Bot 服务...
ssh %SERVER% "sudo systemctl restart luckyred-bot"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Bot 服务重启失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   ✅ 部署完成！
echo ==========================================
echo.
echo 检查服务状态：
ssh %SERVER% "sudo systemctl status luckyred-api --no-pager -l && echo. && sudo systemctl status luckyred-bot --no-pager -l"
echo.
pause
