@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 全自動重啟、監控和修復
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

echo [階段 1] 檢測和準備
echo ========================================
echo.

REM 檢測實際路徑
echo 1.1 檢測部署路徑...
for /f "tokens=*" %%i in ('ssh -o ConnectTimeout=5 %SERVER% "grep WorkingDirectory /etc/systemd/system/luckyred-api.service 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' '"') do set REMOTE_PATH=%%i
if "!REMOTE_PATH!"=="" set REMOTE_PATH=/opt/luckyred
echo    使用路徑: !REMOTE_PATH!
echo.

REM 檢查服務狀態
echo 1.2 檢查當前服務狀態...
ssh -o ConnectTimeout=10 %SERVER% "echo 'API:' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo '  [運行中]' || echo '  [未運行]') && echo 'Bot:' && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo '  [運行中]' || echo '  [未運行]') && echo 'Nginx:' && (sudo systemctl is-active nginx 2>/dev/null && echo '  [運行中]' || echo '  [未運行]')"
echo.

REM 查看錯誤
echo 1.3 查看當前錯誤...
ssh -o ConnectTimeout=10 %SERVER% "echo 'API錯誤:' && sudo journalctl -u luckyred-api -n 5 --no-pager | grep -i error | tail -3 || echo '  無錯誤' && echo 'Bot錯誤:' && sudo journalctl -u luckyred-bot -n 5 --no-pager | grep -i error | tail -3 || echo '  無錯誤'"
echo.

echo [階段 2] 修復常見問題
echo ========================================
echo.

echo 2.1 修復文件權限...
ssh -o ConnectTimeout=10 %SERVER% "sudo chown -R www-data:www-data !REMOTE_PATH! 2>/dev/null && echo '  [OK]' || echo '  [跳過]'"
echo.

echo 2.2 檢查關鍵文件...
ssh -o ConnectTimeout=10 %SERVER% "test -f !REMOTE_PATH!/.env && echo '  [OK] .env存在' || echo '  [ERROR] .env不存在' && test -d !REMOTE_PATH!/api/.venv && echo '  [OK] API虛擬環境存在' || echo '  [ERROR] API虛擬環境不存在' && test -d !REMOTE_PATH!/bot/.venv && echo '  [OK] Bot虛擬環境存在' || echo '  [ERROR] Bot虛擬環境不存在'"
echo.

echo [階段 3] 重啟所有服務
echo ========================================
echo.

echo 3.1 重載 systemd...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl daemon-reload && echo '  [OK]'"
echo.

echo 3.2 重啟服務...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl restart luckyred-api luckyred-bot nginx && echo '  [OK] 所有服務已重啟'"
echo.

echo 3.3 等待服務啟動...
timeout /t 5 /nobreak >nul
echo.

echo [階段 4] 檢查重啟後狀態
echo ========================================
echo.

echo 4.1 服務運行狀態...
ssh -o ConnectTimeout=10 %SERVER% "echo 'API:' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo '  [運行中]' || echo '  [失敗]') && echo 'Bot:' && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo '  [運行中]' || echo '  [失敗]') && echo 'Nginx:' && (sudo systemctl is-active nginx 2>/dev/null && echo '  [運行中]' || echo '  [失敗]')"
echo.

echo 4.2 查看服務詳細狀態...
ssh -o ConnectTimeout=10 %SERVER% "echo '=== API 服務 ===' && sudo systemctl status luckyred-api --no-pager -l | head -10 && echo && echo '=== Bot 服務 ===' && sudo systemctl status luckyred-bot --no-pager -l | head -10"
echo.

echo [階段 5] 監控日誌和錯誤
echo ========================================
echo.

echo 5.1 等待服務運行...
timeout /t 3 /nobreak >nul
echo.

echo 5.2 查看最新日誌...
ssh -o ConnectTimeout=10 %SERVER% "echo '=== API 最新日誌 ===' && sudo journalctl -u luckyred-api -n 15 --no-pager --since '10 seconds ago' | tail -8 && echo && echo '=== Bot 最新日誌 ===' && sudo journalctl -u luckyred-bot -n 15 --no-pager --since '10 seconds ago' | tail -8"
echo.

echo 5.3 檢查錯誤...
ssh -o ConnectTimeout=10 %SERVER% "echo '=== API 錯誤 ===' && sudo journalctl -u luckyred-api --since '1 minute ago' --no-pager | grep -i error | tail -5 || echo '  無錯誤' && echo && echo '=== Bot 錯誤 ===' && sudo journalctl -u luckyred-bot --since '1 minute ago' --no-pager | grep -i error | tail -5 || echo '  無錯誤'"
echo.

echo [階段 6] 生成報告
echo ========================================
echo.

echo 6.1 服務狀態摘要...
ssh -o ConnectTimeout=10 %SERVER% "echo '服務狀態:' && echo '  API: ' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo '    運行中' || echo '    未運行') && echo '  Bot: ' && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo '    運行中' || echo '    未運行') && echo '  Nginx: ' && (sudo systemctl is-active nginx 2>/dev/null && echo '    運行中' || echo '    未運行') && echo && echo '端口監聽:' && sudo netstat -tlnp 2>/dev/null | grep -E ':(80|443|8080)' || echo '  未發現監聽端口'"
echo.

echo 6.2 保存錯誤日誌...
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-api --since '5 minutes ago' --no-pager | grep -i error > /tmp/api-errors-$(date +%%Y%%m%%d-%%H%%M%%S).txt 2>/dev/null && sudo journalctl -u luckyred-bot --since '5 minutes ago' --no-pager | grep -i error > /tmp/bot-errors-$(date +%%Y%%m%%d-%%H%%M%%S).txt 2>/dev/null && echo '  [OK] 錯誤日誌已保存到 /tmp/'"
echo.

echo ========================================
echo   執行完成
echo ========================================
echo.
echo 如果服務未運行，請查看上面的錯誤信息
echo 錯誤日誌已保存到服務器的 /tmp/ 目錄
echo.

