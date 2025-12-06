@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 智能重啟和修復所有服務
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99

REM 自動檢測部署路徑
echo [1/7] 自動檢測部署路徑...
for /f "tokens=*" %%i in ('ssh -o ConnectTimeout=5 %SERVER% "grep WorkingDirectory /etc/systemd/system/luckyred-api.service 2>/dev/null | head -1 | cut -d'=' -f2"') do set REMOTE_PATH=%%i
if "!REMOTE_PATH!"=="" set REMOTE_PATH=/opt/luckyred
echo 使用路徑: !REMOTE_PATH!
echo.

REM 檢查當前狀態
echo [2/7] 檢查當前服務狀態...
ssh -o ConnectTimeout=10 %SERVER% "echo 'API:' && sudo systemctl is-active luckyred-api 2>/dev/null && echo '  [運行中]' || echo '  [未運行]' && echo 'Bot:' && sudo systemctl is-active luckyred-bot 2>/dev/null && echo '  [運行中]' || echo '  [未運行]' && echo 'Nginx:' && sudo systemctl is-active nginx 2>/dev/null && echo '  [運行中]' || echo '  [未運行]'"
echo.

REM 查看錯誤
echo [3/7] 查看當前錯誤...
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-api -n 10 --no-pager | grep -i error | tail -5 || echo '無錯誤'"
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-bot -n 10 --no-pager | grep -i error | tail -5 || echo '無錯誤'"
echo.

REM 修復權限
echo [4/7] 修復文件權限...
ssh -o ConnectTimeout=10 %SERVER% "sudo chown -R www-data:www-data !REMOTE_PATH! 2>/dev/null && echo '[OK]' || echo '[跳過]'"
echo.

REM 重啟服務
echo [5/7] 重啟所有服務...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl daemon-reload && sudo systemctl restart luckyred-api luckyred-bot nginx && echo '[OK] 所有服務已重啟'"
timeout /t 3 /nobreak >nul
echo.

REM 檢查重啟後狀態
echo [6/7] 檢查重啟後狀態...
timeout /t 2 /nobreak >nul
ssh -o ConnectTimeout=10 %SERVER% "echo 'API:' && sudo systemctl is-active luckyred-api 2>/dev/null && echo '  [運行中]' || echo '  [失敗]' && echo 'Bot:' && sudo systemctl is-active luckyred-bot 2>/dev/null && echo '  [運行中]' || echo '  [失敗]' && echo 'Nginx:' && sudo systemctl is-active nginx 2>/dev/null && echo '  [運行中]' || echo '  [失敗]'"
echo.

REM 查看最新日誌
echo [7/7] 查看最新日誌和錯誤...
timeout /t 3 /nobreak >nul
ssh -o ConnectTimeout=10 %SERVER% "echo '=== API 最新日誌 ===' && sudo journalctl -u luckyred-api -n 10 --no-pager --since '10 seconds ago' | tail -5 && echo && echo '=== Bot 最新日誌 ===' && sudo journalctl -u luckyred-bot -n 10 --no-pager --since '10 seconds ago' | tail -5"
echo.

echo ========================================
echo   執行完成
echo ========================================
echo.
echo 如果服務未運行，請查看上面的錯誤信息
echo.

