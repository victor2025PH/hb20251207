@echo off
chcp 65001 >nul
echo ==========================================
echo   检查前端文件内容
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查前端 index.html 的标题...
ssh %SERVER% "head -15 %APP_DIR%/frontend/dist/index.html | grep -i title"
echo.

echo [2] 检查前端 index.html 的完整内容（前30行）...
ssh %SERVER% "head -30 %APP_DIR%/frontend/dist/index.html"
echo.

echo [3] 检查 admin index.html 的标题...
ssh %SERVER% "head -15 %APP_DIR%/admin/frontend/dist/index.html | grep -i title"
echo.

echo [4] 比较两个目录的文件数量...
ssh %SERVER% "echo '前端文件数:' && ls -1 %APP_DIR%/frontend/dist/*.html 2>/dev/null | wc -l && echo 'Admin 文件数:' && ls -1 %APP_DIR%/admin/frontend/dist/*.html 2>/dev/null | wc -l"
echo.

echo [5] 检查是否有 HTTPS 配置...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -A 10 'server_name mini.usdt2026.cc' | grep -E 'listen.*443|ssl_certificate'"
echo.

pause

