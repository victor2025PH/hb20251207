@echo off
chcp 65001 >nul
echo ========================================
echo   LuckyRed 部署狀態檢查
echo ========================================
echo.

echo === 1. 服務運行狀態 ===
ssh ubuntu@165.154.254.99 "sudo systemctl status luckyred-api --no-pager -l | head -20"
echo.
ssh ubuntu@165.154.254.99 "sudo systemctl status luckyred-bot --no-pager -l | head -20"
echo.
ssh ubuntu@165.154.254.99 "sudo systemctl status nginx --no-pager | head -10"
echo.

echo === 2. 檢查部署目錄 ===
ssh ubuntu@165.154.254.99 "ls -la /opt/luckyred 2>/dev/null | head -10 || echo 目錄不存在"
echo.

echo === 3. 檢查環境變量文件 ===
ssh ubuntu@165.154.254.99 "test -f /opt/luckyred/.env && echo [OK] .env文件存在 || echo [ERROR] .env文件不存在"
echo.

echo === 4. 檢查虛擬環境 ===
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/api/.venv && echo [OK] API虛擬環境存在 || echo [ERROR] API虛擬環境不存在"
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/bot/.venv && echo [OK] Bot虛擬環境存在 || echo [ERROR] Bot虛擬環境不存在"
echo.

echo === 5. 檢查前端文件 ===
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/frontend/dist && echo [OK] 前端dist目錄存在 || echo [ERROR] 前端dist目錄不存在"
echo.

echo === 6. 檢查 Nginx 配置 ===
ssh ubuntu@165.154.254.99 "sudo nginx -t"
echo.

echo === 7. 檢查端口監聽 ===
ssh ubuntu@165.154.254.99 "sudo netstat -tlnp 2>/dev/null | grep -E ':(80|443|8080)' || echo 未發現監聽端口"
echo.

echo ========================================
echo   檢查完成
echo ========================================
pause

