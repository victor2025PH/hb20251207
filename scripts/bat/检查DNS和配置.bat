@echo off
chcp 65001 >nul
echo ==========================================
echo   检查 DNS 和实际配置
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 检查 mini.usdt2026.cc 的 DNS 解析...
nslookup mini.usdt2026.cc
echo.

echo [2] 检查服务器上实际响应的配置...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -B 2 -A 10 'server_name.*mini.usdt2026.cc'"
echo.

echo [3] 检查是否有默认 server 块...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -A 5 'listen 80 default_server'"
echo.

echo [4] 检查所有启用的配置...
ssh %SERVER% "sudo ls -la /etc/nginx/sites-enabled/"
echo.

echo [5] 测试服务器直接访问...
ssh %SERVER% "curl -s http://127.0.0.1 -H 'Host: mini.usdt2026.cc' | head -15"
echo.

pause

