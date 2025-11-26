@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 全自動重啟和修復服務
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

REM ========================================
REM 步驟 1: 檢查服務器路徑和當前狀態
REM ========================================
echo [步驟 1/6] 檢查服務器路徑和當前狀態
echo ========================================
echo.

echo 正在檢查部署路徑...
ssh -o ConnectTimeout=10 %SERVER% "if [ -d /opt/luckyred ]; then echo '[OK] /opt/luckyred 存在'; set REMOTE_PATH=/opt/luckyred; elif [ -d /home/ubuntu/hbgm001 ]; then echo '[OK] /home/ubuntu/hbgm001 存在'; set REMOTE_PATH=/home/ubuntu/hbgm001; else echo '[檢查] 查找部署目錄...'; find /opt /home -type d -name '*luckyred*' -o -name '*hbgm001*' 2>/dev/null | head -5; fi"

REM 從服務文件獲取實際路徑
echo.
echo 正在從服務文件獲取實際路徑...
for /f "tokens=*" %%i in ('ssh -o ConnectTimeout=10 %SERVER% "grep WorkingDirectory /etc/systemd/system/luckyred-api.service 2>/dev/null | cut -d'=' -f2"') do set ACTUAL_PATH=%%i
if "!ACTUAL_PATH!"=="" (
    echo 無法從服務文件獲取路徑，使用默認路徑: /opt/luckyred
    set ACTUAL_PATH=/opt/luckyred
) else (
    echo 檢測到實際路徑: !ACTUAL_PATH!
    set REMOTE_PATH=!ACTUAL_PATH!
)

echo.
echo 當前服務狀態:
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl status luckyred-api --no-pager -l | head -5 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -5"
echo.
pause
echo.

REM ========================================
REM 步驟 2: 查看當前錯誤日誌
REM ========================================
echo [步驟 2/6] 查看當前錯誤日誌
echo ========================================
echo.

echo --- API 服務最近錯誤 ---
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-api -n 30 --no-pager | tail -20"
echo.

echo --- Bot 服務最近錯誤 ---
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-bot -n 30 --no-pager | tail -20"
echo.

echo --- 檢查關鍵文件 ---
ssh -o ConnectTimeout=10 %SERVER% "echo '檢查 .env:' && test -f %REMOTE_PATH%/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在' && echo '檢查 API 虛擬環境:' && test -d %REMOTE_PATH%/api/.venv && echo '[OK] 存在' || echo '[ERROR] 不存在' && echo '檢查 Bot 虛擬環境:' && test -d %REMOTE_PATH%/bot/.venv && echo '[OK] 存在' || echo '[ERROR] 不存在'"
echo.
pause
echo.

REM ========================================
REM 步驟 3: 修復常見問題
REM ========================================
echo [步驟 3/6] 修復常見問題
echo ========================================
echo.

echo 3.1 檢查並修復文件權限...
ssh -o ConnectTimeout=10 %SERVER% "sudo chown -R www-data:www-data %REMOTE_PATH% 2>/dev/null && echo '[OK] 權限已修復' || echo '[警告] 權限修復失敗'"
echo.

echo 3.2 檢查並重新安裝依賴（如果需要）...
ssh -o ConnectTimeout=10 %SERVER% "cd %REMOTE_PATH%/api && if [ -d .venv ]; then echo '[OK] API虛擬環境存在'; else echo '[修復] 創建API虛擬環境...'; python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt; fi"
echo.

ssh -o ConnectTimeout=10 %SERVER% "cd %REMOTE_PATH%/bot && if [ -d .venv ]; then echo '[OK] Bot虛擬環境存在'; else echo '[修復] 創建Bot虛擬環境...'; python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt; fi"
echo.

echo 3.3 重新構建前端（如果需要）...
ssh -o ConnectTimeout=10 %SERVER% "cd %REMOTE_PATH%/frontend && if [ -d dist ]; then echo '[OK] 前端已構建'; else echo '[修復] 構建前端...'; npm install && npm run build; fi"
echo.
pause
echo.

REM ========================================
REM 步驟 4: 重啟所有服務
REM ========================================
echo [步驟 4/6] 重啟所有服務
echo ========================================
echo.

echo 4.1 重載 systemd...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl daemon-reload && echo '[OK] systemd 已重載'"
echo.

echo 4.2 停止所有服務...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl stop luckyred-api luckyred-bot 2>/dev/null && echo '[OK] 服務已停止'"
timeout /t 2 /nobreak >nul
echo.

echo 4.3 重啟 API 服務...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl restart luckyred-api && echo '[OK] API服務已重啟'"
timeout /t 2 /nobreak >nul
echo.

echo 4.4 重啟 Bot 服務...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl restart luckyred-bot && echo '[OK] Bot服務已重啟'"
timeout /t 2 /nobreak >nul
echo.

echo 4.5 重啟 Nginx（前端和Miniapp）...
ssh -o ConnectTimeout=10 %SERVER% "sudo systemctl restart nginx && echo '[OK] Nginx已重啟'"
timeout /t 3 /nobreak >nul
echo.

echo 4.6 檢查服務狀態...
ssh -o ConnectTimeout=10 %SERVER% "echo '=== 服務狀態 ===' && sudo systemctl status luckyred-api --no-pager -l | head -10 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -10 && echo && sudo systemctl status nginx --no-pager | head -5"
echo.
pause
echo.

REM ========================================
REM 步驟 5: 監控日誌並識別錯誤
REM ========================================
echo [步驟 5/6] 監控日誌並識別錯誤
echo ========================================
echo.

echo 等待 5 秒後檢查服務日誌...
timeout /t 5 /nobreak >nul
echo.

echo --- API 服務最新日誌 ---
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-api -n 20 --no-pager --since '1 minute ago' | tail -15"
echo.

echo --- Bot 服務最新日誌 ---
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-bot -n 20 --no-pager --since '1 minute ago' | tail -15"
echo.

echo --- 檢查服務是否運行 ---
ssh -o ConnectTimeout=10 %SERVER% "echo 'API服務:' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo '  [運行中]' || echo '  [未運行]') && echo 'Bot服務:' && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo '  [運行中]' || echo '  [未運行]') && echo 'Nginx服務:' && (sudo systemctl is-active nginx 2>/dev/null && echo '  [運行中]' || echo '  [未運行]')"
echo.

REM 保存錯誤日誌到文件
echo 正在保存錯誤日誌到 error-log.txt...
ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-api -n 50 --no-pager | grep -i error > /tmp/api-errors.txt 2>/dev/null && sudo journalctl -u luckyred-bot -n 50 --no-pager | grep -i error > /tmp/bot-errors.txt 2>/dev/null && echo '[OK] 錯誤日誌已保存'"
echo.
pause
echo.

REM ========================================
REM 步驟 6: 分析問題並提供修復建議
REM ========================================
echo [步驟 6/6] 分析問題並提供修復建議
echo ========================================
echo.

echo 正在分析錯誤...
ssh -o ConnectTimeout=10 %SERVER% "echo '=== API 錯誤分析 ===' && if [ -f /tmp/api-errors.txt ]; then cat /tmp/api-errors.txt | head -10; else echo '無錯誤記錄'; fi && echo && echo '=== Bot 錯誤分析 ===' && if [ -f /tmp/bot-errors.txt ]; then cat /tmp/bot-errors.txt | head -10; else echo '無錯誤記錄'; fi"
echo.

echo 檢查常見問題:
ssh -o ConnectTimeout=10 %SERVER% "echo '1. 檢查 .env 文件:' && test -f %REMOTE_PATH%/.env && (grep -q 'BOT_TOKEN' %REMOTE_PATH%/.env && echo '  [OK] BOT_TOKEN 已設置' || echo '  [ERROR] BOT_TOKEN 未設置') && (grep -q 'DATABASE_URL' %REMOTE_PATH%/.env && echo '  [OK] DATABASE_URL 已設置' || echo '  [ERROR] DATABASE_URL 未設置') || echo '  [ERROR] .env 文件不存在' && echo && echo '2. 檢查數據庫連接:' && sudo systemctl is-active postgresql 2>/dev/null && echo '  [OK] PostgreSQL 運行中' || echo '  [ERROR] PostgreSQL 未運行' && echo && echo '3. 檢查端口監聽:' && sudo netstat -tlnp 2>/dev/null | grep -E ':(80|443|8080)' && echo '  [OK] 端口正在監聽' || echo '  [警告] 未發現監聽端口'"
echo.

echo ========================================
echo   執行完成
echo ========================================
echo.
echo 請查看上面的輸出以了解:
echo   1. 服務是否成功重啟
echo   2. 是否有錯誤信息
echo   3. 需要修復的問題
echo.

