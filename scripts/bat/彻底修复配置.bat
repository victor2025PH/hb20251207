@echo off
chcp 65001 >nul
echo ==========================================
echo   彻底修复配置 - 禁用 HTTPS 重定向
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 检查是否有 SSL 配置被启用...
ssh %SERVER% "sudo ls -la /etc/nginx/sites-enabled/ | grep mini"
echo.

echo [2] 禁用 SSL 配置（如果存在）...
ssh %SERVER% "sudo rm -f /etc/nginx/sites-enabled/mini.usdt2026.cc-ssl.conf 2>/dev/null && echo '已删除 SSL 配置链接' || echo 'SSL 配置链接不存在'"
echo.

echo [3] 确保只启用 HTTP 配置...
ssh %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf && echo 'HTTP 配置已启用'"
echo.

echo [4] 验证配置...
ssh %SERVER% "sudo nginx -t"
if errorlevel 1 (
    echo 配置语法错误！
    pause
    exit /b 1
)
echo.

echo [5] 重新加载 Nginx...
ssh %SERVER% "sudo systemctl reload nginx"
echo.

echo [6] 检查实际使用的配置...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -A 3 'server_name mini.usdt2026.cc' | head -10"
echo.

echo [7] 测试 HTTP 访问（不应该有重定向）...
ssh %SERVER% "curl -I http://mini.usdt2026.cc 2>&1 | grep -E 'HTTP|Location'"
echo.

echo [8] 检查前端文件标题...
ssh %SERVER% "curl -s http://mini.usdt2026.cc | grep -i '<title>'"
echo.

echo ==========================================
echo   修复完成
echo ==========================================
echo.
echo 现在请在浏览器中测试：
echo http://mini.usdt2026.cc
echo.
pause

