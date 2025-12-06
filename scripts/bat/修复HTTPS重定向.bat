@echo off
chcp 65001 >nul
echo ==========================================
echo   修复 HTTPS 重定向问题
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 检查是否有 HTTPS 配置指向 admin...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -B 5 -A 15 'listen.*443.*mini.usdt2026.cc'"
echo.

echo [2] 检查是否有 HTTP 到 HTTPS 的重定向...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -B 2 -A 5 'return 301.*https.*mini.usdt2026.cc'"
echo.

echo [3] 临时禁用所有 HTTPS 配置（如果存在）...
ssh %SERVER% "sudo find /etc/nginx -name '*mini.usdt2026.cc*ssl*' -o -name '*mini.usdt2026.cc*443*' 2>/dev/null"
echo.

echo [4] 确保只使用 HTTP 配置...
ssh %SERVER% "sudo ls -la /etc/nginx/sites-enabled/ | grep mini"
echo.

echo [5] 测试 HTTP 访问（带 Host 头）...
ssh %SERVER% "curl -s http://127.0.0.1 -H 'Host: mini.usdt2026.cc' | head -20"
echo.

pause

