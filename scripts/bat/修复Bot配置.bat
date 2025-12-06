@echo off
chcp 65001 >nul
echo ==========================================
echo   修复 Bot 配置 - 创建 .env 文件
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1/3] 检查项目根目录 .env 文件...
ssh %SERVER% "ls -la %APP_DIR%/.env 2>&1"
echo.

echo [2/3] 检查现有配置（如果存在）...
ssh %SERVER% "if [ -f %APP_DIR%/.env ]; then grep MINIAPP_URL %APP_DIR%/.env; else echo '文件不存在'; fi"
echo.

echo [3/3] 创建/更新 .env 文件（确保 MINIAPP_URL 正确）...
ssh %SERVER% "cat >> %APP_DIR%/.env << 'EOF'

# MiniApp URL (确保指向正确的域名)
MINIAPP_URL=https://mini.usdt2026.cc
MINIAPP_DOMAIN=mini.usdt2026.cc
EOF" 2>nul

echo.
echo 检查更新后的配置...
ssh %SERVER% "grep MINIAPP_URL %APP_DIR%/.env"
echo.

echo ==========================================
echo   ✅ 配置已更新！
echo ==========================================
echo.
echo 现在需要重启 Bot 服务使配置生效...
echo.
pause

