@echo off
chcp 65001 >nul

echo ========================================
echo   快速重啟所有服務
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo 正在重啟服務...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl daemon-reload && sudo systemctl restart luckyred-api luckyred-bot nginx && echo '[OK] 所有服務已重啟'"

timeout /t 3 /nobreak >nul

echo.
echo 檢查服務狀態:
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl status luckyred-api --no-pager -l | head -8 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -8 && echo && sudo systemctl status nginx --no-pager | head -5"

echo.
echo 完成!

