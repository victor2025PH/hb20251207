@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo   修复 Telegram MiniApp SSL 证书（优化版）
echo ==========================================
echo.

set SERVER=ubuntu@165.154.254.99
set APP_DIR=/opt/luckyred
set SSH_TIMEOUT=10

REM 测试 SSH 连接
echo [0] 测试 SSH 连接（超时 %SSH_TIMEOUT% 秒）...
ssh -o ConnectTimeout=%SSH_TIMEOUT% -o BatchMode=yes %SERVER% "echo '连接成功'" >nul 2>&1
if errorlevel 1 (
    echo ❌ SSH 连接失败或需要密码
    echo 请先配置 SSH 密钥或手动执行命令
    pause
    exit /b 1
)
echo ✓ SSH 连接正常
echo.

echo [1] 检查证书是否存在...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "sudo test -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem && echo '证书存在' || echo '证书不存在'" 2>&1
if errorlevel 1 (
    echo ⚠️ 检查证书时出错，继续执行...
)
echo.

echo [2] 如果证书不存在，申请证书...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "if [ ! -f /etc/letsencrypt/live/mini.usdt2026.cc/fullchain.pem ]; then echo '开始申请证书...'; timeout 60 sudo certbot certonly --nginx -d mini.usdt2026.cc --non-interactive --agree-tos --email admin@usdt2026.cc --keep-until-expiring 2>&1; else echo '证书已存在'; fi" 2>&1
if errorlevel 1 (
    echo ⚠️ 证书申请可能失败，请检查输出
)
echo.

echo [3] 上传 SSL 配置文件...
scp -o ConnectTimeout=%SSH_TIMEOUT% deploy\nginx\mini.usdt2026.cc-ssl.conf %SERVER%:/tmp/mini.usdt2026.cc-ssl.conf 2>&1
if errorlevel 1 (
    echo ❌ 上传配置文件失败
    pause
    exit /b 1
)
echo ✓ 配置文件已上传
echo.

echo [4] 复制 SSL 配置到正确位置...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "sudo cp /tmp/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf && echo '配置已复制'" 2>&1
if errorlevel 1 (
    echo ❌ 复制配置失败
    pause
    exit /b 1
)
echo.

echo [5] 启用 SSL 配置...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc-ssl.conf /etc/nginx/sites-enabled/mini.usdt2026.cc-ssl.conf && echo 'SSL 配置已启用'" 2>&1
if errorlevel 1 (
    echo ❌ 启用配置失败
    pause
    exit /b 1
)
echo.

echo [6] 验证配置...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "sudo nginx -t 2>&1" | findstr /C:"syntax is ok" /C:"test is successful" /C:"error"
if errorlevel 1 (
    echo ❌ 配置语法错误！
    pause
    exit /b 1
)
echo ✓ 配置验证通过
echo.

echo [7] 重新加载 Nginx...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "sudo systemctl reload nginx && echo 'Nginx 已重新加载'" 2>&1
if errorlevel 1 (
    echo ⚠️ 重新加载 Nginx 时出错
)
echo.

echo [8] 测试 HTTPS 访问...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "timeout 5 curl -k -I https://mini.usdt2026.cc 2>&1 | head -3" 2>&1
echo.

echo [9] 更新 Bot 配置为 HTTPS...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "sed -i 's|^MINIAPP_URL=.*|MINIAPP_URL=https://mini.usdt2026.cc|' %APP_DIR%/.env && grep MINIAPP_URL %APP_DIR%/.env" 2>&1
if errorlevel 1 (
    echo ⚠️ 更新配置时出错
)
echo.

echo [10] 重启 Bot 服务...
ssh -o ConnectTimeout=%SSH_TIMEOUT% %SERVER% "sudo systemctl restart luckyred-bot && echo 'Bot 服务已重启'" 2>&1
if errorlevel 1 (
    echo ⚠️ 重启服务时出错
)
echo.

echo ==========================================
echo   修复完成
echo ==========================================
echo.
echo 现在请在 Telegram 中测试 MiniApp
echo.
pause

