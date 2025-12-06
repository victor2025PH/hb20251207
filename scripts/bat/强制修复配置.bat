@echo off
chcp 65001 >nul
echo ==========================================
echo   强制修复 Nginx 配置
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred

echo [1] 备份当前配置...
ssh %SERVER% "sudo cp /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf.bak 2>/dev/null || echo '备份完成'"
echo.

echo [2] 上传正确的配置...
scp deploy\nginx\mini.usdt2026.cc.conf %SERVER%:/tmp/mini.usdt2026.cc.conf
echo.

echo [3] 复制到正确位置...
ssh %SERVER% "sudo cp /tmp/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf"
echo.

echo [4] 确保符号链接存在...
ssh %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf"
echo.

echo [5] 检查配置语法...
ssh %SERVER% "sudo nginx -t"
if errorlevel 1 (
    echo 配置语法错误！
    pause
    exit /b 1
)
echo.

echo [6] 重新加载 Nginx...
ssh %SERVER% "sudo systemctl reload nginx"
echo.

echo [7] 验证配置...
ssh %SERVER% "sudo nginx -T 2>&1 | grep -A 3 'server_name mini.usdt2026.cc' | grep root"
echo.

echo [8] 测试访问...
ssh %SERVER% "curl -s http://localhost -H 'Host: mini.usdt2026.cc' | grep -i '<title>'"
echo.

echo ==========================================
echo   修复完成
echo ==========================================
echo.
pause

