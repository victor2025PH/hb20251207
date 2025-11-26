@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 手動檢查部署
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

echo 服務器: %SERVER%
echo 路徑: %REMOTE_PATH%
echo.

REM ========================================
REM 步驟 1: 上傳檢查腳本
REM ========================================
echo ========================================
echo   步驟 1: 上傳檢查腳本到服務器
echo ========================================
echo.
echo 命令: scp check_deployment.sh %SERVER%:%REMOTE_PATH%/check_deployment.sh
echo.
set /p STEP1="是否執行步驟 1? (Y/N): "
if /i "!STEP1!"=="Y" (
    echo.
    echo 正在執行...
    scp -o ConnectTimeout=10 check_deployment.sh %SERVER%:%REMOTE_PATH%/check_deployment.sh
    if !ERRORLEVEL! EQU 0 (
        echo [OK] 上傳成功
        echo.
        echo 設置執行權限...
        ssh -o ConnectTimeout=10 %SERVER% "chmod +x %REMOTE_PATH%/check_deployment.sh"
    ) else (
        echo [ERROR] 上傳失敗
        echo 可能原因: 需要輸入密碼、網絡問題或文件不存在
    )
) else (
    echo 跳過步驟 1
)
echo.
pause
echo.

REM ========================================
REM 步驟 2: 執行部署檢查
REM ========================================
echo ========================================
echo   步驟 2: 執行部署檢查
echo ========================================
echo.
echo 命令: ssh %SERVER% "bash %REMOTE_PATH%/check_deployment.sh"
echo.
set /p STEP2="是否執行步驟 2? (Y/N): "
if /i "!STEP2!"=="Y" (
    echo.
    echo 正在執行...
    ssh -o ConnectTimeout=10 %SERVER% "if [ -f %REMOTE_PATH%/check_deployment.sh ]; then bash %REMOTE_PATH%/check_deployment.sh; else echo '檢查腳本不存在，執行基本檢查...'; bash -c 'echo \"=== 服務狀態 ===\" && sudo systemctl status luckyred-api --no-pager -l | head -15 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -15 && echo && echo \"=== 錯誤日誌 ===\" && sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15 && echo && sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -15'; fi"
) else (
    echo 跳過步驟 2
)
echo.
pause
echo.

REM ========================================
REM 步驟 3: 生成診斷報告
REM ========================================
echo ========================================
echo   步驟 3: 生成診斷報告
echo ========================================
echo.
echo 命令: ssh %SERVER% "檢查文件和服務狀態"
echo.
set /p STEP3="是否執行步驟 3? (Y/N): "
if /i "!STEP3!"=="Y" (
    echo.
    echo 正在執行...
    ssh -o ConnectTimeout=10 %SERVER% "echo '=== 文件檢查 ===' && test -f %REMOTE_PATH%/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在' && test -d %REMOTE_PATH%/api/.venv && echo '[OK] API虛擬環境存在' || echo '[ERROR] API虛擬環境不存在' && test -d %REMOTE_PATH%/bot/.venv && echo '[OK] Bot虛擬環境存在' || echo '[ERROR] Bot虛擬環境不存在' && echo && echo '=== 服務狀態摘要 ===' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo 'API服務: [運行中]' || echo 'API服務: [未運行]') && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo 'Bot服務: [運行中]' || echo 'Bot服務: [未運行]') && (sudo systemctl is-active nginx 2>/dev/null && echo 'Nginx服務: [運行中]' || echo 'Nginx服務: [未運行]')"
) else (
    echo 跳過步驟 3
)
echo.
pause
echo.

REM ========================================
REM 步驟 4: 查看錯誤日誌（可選）
REM ========================================
echo ========================================
echo   步驟 4: 查看錯誤日誌（可選）
echo ========================================
echo.
echo 命令: ssh %SERVER% "查看服務錯誤日誌"
echo.
set /p STEP4="是否執行步驟 4? (Y/N): "
if /i "!STEP4!"=="Y" (
    echo.
    echo 正在執行...
    echo.
    echo --- API 服務錯誤日誌 ---
    ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-api -n 30 --no-pager | tail -20"
    echo.
    echo --- Bot 服務錯誤日誌 ---
    ssh -o ConnectTimeout=10 %SERVER% "sudo journalctl -u luckyred-bot -n 30 --no-pager | tail -20"
) else (
    echo 跳過步驟 4
)
echo.
pause
echo.

echo ========================================
echo   檢查完成
echo ========================================
echo.
echo 提示: 如果需要輸入密碼，請在每次 SSH/SCP 命令提示時輸入
echo.

