@echo off
chcp 65001 >nul
echo ==========================================
echo   诊断 MiniApp 问题
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查服务器上实际使用的 Nginx 配置...
echo.
ssh %SERVER% "sudo nginx -T 2>&1 | grep -A 30 'server_name mini.usdt2026.cc'"
echo.

echo [2] 检查前端构建文件是否存在...
echo.
ssh %SERVER% "ls -la %APP_DIR%/frontend/dist/ | head -10"
echo.

echo [3] 检查前端 index.html 内容...
echo.
ssh %SERVER% "head -20 %APP_DIR%/frontend/dist/index.html"
echo.

echo [4] 检查是否有其他 Nginx 配置干扰...
echo.
ssh %SERVER% "sudo ls -la /etc/nginx/sites-enabled/ | grep mini"
echo.

echo [5] 测试访问根路径...
echo.
ssh %SERVER% "curl -s http://mini.usdt2026.cc | head -20"
echo.

echo [6] 测试访问 /login 路径...
echo.
ssh %SERVER% "curl -I http://mini.usdt2026.cc/login 2>&1 | head -10"
echo.

echo ==========================================
echo   诊断完成
echo ==========================================
echo.
pause

