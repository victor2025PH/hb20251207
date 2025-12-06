@echo off
chcp 65001 >nul
echo ==========================================
echo   测试 MiniApp 访问
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo [1] 从服务器测试 HTTP 访问...
ssh %SERVER% "curl -s http://mini.usdt2026.cc | head -20"
echo.

echo [2] 检查返回的 HTML 标题...
ssh %SERVER% "curl -s http://mini.usdt2026.cc | grep -i '<title>'"
echo.

echo [3] 检查是否有重定向...
ssh %SERVER% "curl -I http://mini.usdt2026.cc 2>&1 | grep -E 'HTTP|Location'"
echo.

echo ==========================================
echo   测试完成
echo ==========================================
echo.
echo 如果看到 HTML 内容，说明配置正确
echo 如果看到重定向到 admin，说明还有问题
echo.
pause

