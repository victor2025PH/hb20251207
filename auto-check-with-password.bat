@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 自動檢查部署（支持密碼）
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

REM 檢查 SSH 密鑰
echo 正在檢查 SSH 連接...
ssh -o BatchMode=yes -o ConnectTimeout=5 %SERVER% "echo 'OK'" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] SSH 密鑰已配置，無需輸入密碼
    set USE_PASSWORD=0
) else (
    echo [提示] 需要輸入 SSH 密碼
    set USE_PASSWORD=1
)
echo.

if %USE_PASSWORD% EQU 1 (
    echo ========================================
    echo   密碼輸入說明
    echo ========================================
    echo.
    echo 腳本將在執行 SSH/SCP 命令時提示輸入密碼
    echo 請在提示時輸入您的 SSH 密碼
    echo.
    echo 提示: 為了避免每次輸入密碼，建議配置 SSH 密鑰
    echo       執行: ssh-copy-id %SERVER%
    echo.
    timeout /t 2 /nobreak >nul
    echo.
)

echo [步驟 1/3] 上傳檢查腳本到服務器
echo ========================================
echo.
echo 正在上傳 check_deployment.sh...
echo 提示: 如果需要輸入密碼，請在提示時輸入
echo.
scp -o ConnectTimeout=10 check_deployment.sh %SERVER%:%REMOTE_PATH%/check_deployment.sh
if %ERRORLEVEL% EQU 0 (
    echo [OK] 檢查腳本上傳成功
    ssh -o ConnectTimeout=10 %SERVER% "chmod +x %REMOTE_PATH%/check_deployment.sh"
) else (
    echo [警告] 上傳失敗，將使用遠程命令檢查
    echo 可能原因: 密碼錯誤、網絡問題或文件不存在
)
echo.

echo [步驟 2/3] 執行部署檢查
echo ========================================
echo.
echo 提示: 如果需要輸入密碼，請在提示時輸入
echo.
ssh -o ConnectTimeout=10 %SERVER% "if [ -f %REMOTE_PATH%/check_deployment.sh ]; then bash %REMOTE_PATH%/check_deployment.sh; else echo '檢查腳本不存在，執行基本檢查...'; bash -c 'echo \"=== 服務狀態 ===\" && sudo systemctl status luckyred-api --no-pager -l | head -15 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -15 && echo && echo \"=== 錯誤日誌 ===\" && sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15 && echo && sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -15'; fi"
echo.

echo [步驟 3/3] 生成診斷報告
echo ========================================
echo.
echo 提示: 如果需要輸入密碼，請在提示時輸入
echo.
ssh -o ConnectTimeout=10 %SERVER% "echo '=== 文件檢查 ===' && test -f %REMOTE_PATH%/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在' && test -d %REMOTE_PATH%/api/.venv && echo '[OK] API虛擬環境存在' || echo '[ERROR] API虛擬環境不存在' && test -d %REMOTE_PATH%/bot/.venv && echo '[OK] Bot虛擬環境存在' || echo '[ERROR] Bot虛擬環境不存在' && echo && echo '=== 服務狀態摘要 ===' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo 'API服務: [運行中]' || echo 'API服務: [未運行]') && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo 'Bot服務: [運行中]' || echo 'Bot服務: [未運行]') && (sudo systemctl is-active nginx 2>/dev/null && echo 'Nginx服務: [運行中]' || echo 'Nginx服務: [未運行]')"
echo.

echo ========================================
echo   檢查完成
echo ========================================
echo.
echo 提示: 查看上面的輸出以了解服務狀態和錯誤信息
echo.

if %USE_PASSWORD% EQU 1 (
    echo.
    echo ========================================
    echo   配置 SSH 密鑰（可選）
    echo ========================================
    echo.
    echo 為了避免每次輸入密碼，可以配置 SSH 密鑰：
    echo   1. 生成密鑰: ssh-keygen -t ed25519
    echo   2. 複製到服務器: ssh-copy-id %SERVER%
    echo   3. 之後執行腳本就不需要輸入密碼了
    echo.
)

