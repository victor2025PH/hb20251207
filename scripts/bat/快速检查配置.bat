@echo off
chcp 65001 >nul
echo ==========================================
echo   快速检查配置
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查 Nginx 配置中的 root 目录...
ssh %SERVER% "sudo grep -r 'server_name mini.usdt2026.cc' /etc/nginx/ -A 5 | grep root"
echo.

echo [2] 检查前端文件是否存在...
ssh %SERVER% "test -f %APP_DIR%/frontend/dist/index.html && echo '前端文件存在' || echo '前端文件不存在'"
echo.

echo [3] 检查前端 index.html 标题...
ssh %SERVER% "grep -i '<title>' %APP_DIR%/frontend/dist/index.html"
echo.

echo [4] 检查 admin 目录...
ssh %SERVER% "test -f %APP_DIR%/admin/frontend/dist/index.html && echo 'Admin 文件存在' || echo 'Admin 文件不存在'"
echo.

echo [5] 检查 admin index.html 标题...
ssh %SERVER% "grep -i '<title>' %APP_DIR%/admin/frontend/dist/index.html"
echo.

echo [6] 列出所有启用的 Nginx 配置...
ssh %SERVER% "sudo ls -la /etc/nginx/sites-enabled/"
echo.

pause

