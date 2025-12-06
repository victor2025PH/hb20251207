@echo off
chcp 65001 >nul
echo ==========================================
echo   修复 Nginx 配置 - 确保 MiniApp 正确路由
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1/4] 更新 mini.usdt2026.cc 配置...
ssh %SERVER% "sudo cp %APP_DIR%/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 配置复制失败
    pause
    exit /b 1
)

echo.
echo [2/4] 确保站点已启用...
ssh %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 站点启用失败
    pause
    exit /b 1
)

echo.
echo [3/4] 测试 Nginx 配置...
ssh %SERVER% "sudo nginx -t"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Nginx 配置测试失败
    pause
    exit /b 1
)

echo.
echo [4/4] 重载 Nginx...
ssh %SERVER% "sudo systemctl reload nginx"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Nginx 重载失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   ✅ Nginx 配置已修复！
echo ==========================================
echo.
echo 现在 mini.usdt2026.cc 应该正确指向 MiniApp 前端
echo.
pause

