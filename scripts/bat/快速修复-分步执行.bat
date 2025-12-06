@echo off
chcp 65001 >nul
echo ==========================================
echo   快速修复 - 分步执行（避免卡死）
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo 步骤 1: 复制 HTTP 配置...
ssh %SERVER% "sudo cp %APP_DIR%/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 步骤 1 失败
    pause
    exit /b 1
)
echo ✅ 完成

echo.
echo 步骤 2: 启用配置...
ssh %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 步骤 2 失败
    pause
    exit /b 1
)
echo ✅ 完成

echo.
echo 步骤 3: 测试 Nginx 配置...
ssh %SERVER% "sudo nginx -t"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Nginx 配置测试失败
    pause
    exit /b 1
)
echo ✅ 完成

echo.
echo 步骤 4: 重载 Nginx...
ssh %SERVER% "sudo systemctl reload nginx"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Nginx 重载失败
    pause
    exit /b 1
)
echo ✅ 完成

echo.
echo 步骤 5: 更新 Bot 配置...
ssh %SERVER% "sed -i 's|^MINIAPP_URL=.*|MINIAPP_URL=http://mini.usdt2026.cc|' %APP_DIR%/.env"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 配置更新失败
    pause
    exit /b 1
)
echo ✅ 完成

echo.
echo 步骤 6: 验证配置...
ssh %SERVER% "grep MINIAPP_URL %APP_DIR%/.env"
echo.

echo 步骤 7: 重启 Bot...
ssh %SERVER% "sudo systemctl restart luckyred-bot"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Bot 重启失败
    pause
    exit /b 1
)
echo ✅ 完成

echo.
echo ==========================================
echo   ✅ 所有步骤完成！
echo ==========================================
echo.
pause

