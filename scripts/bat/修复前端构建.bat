@echo off
chcp 65001 >nul
echo ==========================================
echo   重新构建前端并部署
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 本地构建前端...
echo.
cd frontend
call npm run build
if errorlevel 1 (
    echo 构建失败！
    pause
    exit /b 1
)
cd ..

echo.
echo [2] 上传构建文件到服务器...
echo.
scp -r frontend/dist/* %SERVER%:%APP_DIR%/frontend/dist/

echo.
echo [3] 设置正确的文件权限...
echo.
ssh %SERVER% "sudo chown -R www-data:www-data %APP_DIR%/frontend/dist"

echo.
echo [4] 重新加载 Nginx...
echo.
ssh %SERVER% "sudo systemctl reload nginx"

echo.
echo ==========================================
echo   部署完成
echo ==========================================
echo.
pause

