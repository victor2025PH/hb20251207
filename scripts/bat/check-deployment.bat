@echo off
chcp 65001 >nul
echo ========================================
echo   LuckyRed 部署狀態檢查
echo ========================================
echo.

echo 正在連接到服務器並執行檢查...
echo.

ssh ubuntu@165.154.254.99 "bash /opt/luckyred/check_deployment.sh"

echo.
echo ========================================
echo   檢查完成
echo ========================================
pause

