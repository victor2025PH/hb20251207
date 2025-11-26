@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 自動上傳並檢查部署
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

echo [步驟 1/3] 上傳檢查腳本到服務器
echo ========================================
echo.
echo 正在上傳 check_deployment.sh...
echo 提示: 如果長時間無響應，可能是需要輸入 SSH 密碼
scp -o ConnectTimeout=5 check_deployment.sh %SERVER%:%REMOTE_PATH%/check_deployment.sh
if %ERRORLEVEL% EQU 0 (
    echo [OK] 檢查腳本上傳成功
    ssh %SERVER% "chmod +x %REMOTE_PATH%/check_deployment.sh"
) else (
    echo [ERROR] 上傳失敗，將使用遠程命令檢查
)
echo.

echo [步驟 2/3] 執行部署檢查
echo ========================================
echo.
ssh -o ConnectTimeout=5 %SERVER% "if [ -f %REMOTE_PATH%/check_deployment.sh ]; then bash %REMOTE_PATH%/check_deployment.sh; else echo '檢查腳本不存在，執行基本檢查...'; bash -c 'echo \"=== 服務狀態 ===\" && sudo systemctl status luckyred-api --no-pager -l | head -15 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -15 && echo && echo \"=== 錯誤日誌 ===\" && sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15 && echo && sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -15'; fi"
echo.

echo [步驟 3/3] 生成診斷報告
echo ========================================
echo.
ssh -o ConnectTimeout=5 %SERVER% "echo '=== 文件檢查 ===' && test -f %REMOTE_PATH%/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在' && test -d %REMOTE_PATH%/api/.venv && echo '[OK] API虛擬環境存在' || echo '[ERROR] API虛擬環境不存在' && test -d %REMOTE_PATH%/bot/.venv && echo '[OK] Bot虛擬環境存在' || echo '[ERROR] Bot虛擬環境不存在' && echo && echo '=== 服務狀態摘要 ===' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo 'API服務: [運行中]' || echo 'API服務: [未運行]') && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo 'Bot服務: [運行中]' || echo 'Bot服務: [未運行]') && (sudo systemctl is-active nginx 2>/dev/null && echo 'Nginx服務: [運行中]' || echo 'Nginx服務: [未運行]')"
echo.

echo ========================================
echo   檢查完成
echo ========================================
echo.
echo 提示: 查看上面的輸出以了解服務狀態和錯誤信息
echo.

