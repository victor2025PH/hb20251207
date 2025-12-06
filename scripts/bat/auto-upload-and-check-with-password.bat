@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 自動上傳並檢查部署
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

REM 檢查是否已配置 SSH 密鑰
echo 正在檢查 SSH 連接...
ssh -o BatchMode=yes -o ConnectTimeout=5 %SERVER% "echo 'SSH密鑰已配置'" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] SSH 密鑰已配置，無需輸入密碼
    set NEED_PASSWORD=0
) else (
    echo [提示] 需要輸入 SSH 密碼
    set NEED_PASSWORD=1
)
echo.

if %NEED_PASSWORD% EQU 1 (
    echo ========================================
    echo   需要輸入 SSH 密碼
    echo ========================================
    echo.
    echo 提示: 密碼輸入時不會顯示字符（安全考慮）
    echo 如果不想每次輸入密碼，建議配置 SSH 密鑰
    echo.
    set /p SSH_PASSWORD="請輸入 SSH 密碼: "
    echo.
    
    REM 使用 PowerShell 執行帶密碼的 SSH 命令
    goto :use_powershell
) else (
    goto :direct_ssh
)

:use_powershell
echo [步驟 1/3] 上傳檢查腳本到服務器
echo ========================================
echo.
echo 正在上傳 check_deployment.sh...
powershell -Command "$pass = ConvertTo-SecureString '%SSH_PASSWORD%' -AsPlainText -Force; $cred = New-Object System.Management.Automation.PSCredential('ubuntu', $pass); $session = New-PSSession -ComputerName 165.154.254.99 -Credential $cred -ErrorAction Stop; Copy-Item 'check_deployment.sh' -Destination '/opt/luckyred/check_deployment.sh' -ToSession $session; Invoke-Command -Session $session -ScriptBlock { chmod +x /opt/luckyred/check_deployment.sh }; Remove-PSSession $session" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [嘗試使用 SCP...]
    echo %SSH_PASSWORD%| plink -ssh -pw %SSH_PASSWORD% %SERVER% "mkdir -p %REMOTE_PATH%" 2>nul
    echo %SSH_PASSWORD%| plink -ssh -pw %SSH_PASSWORD% -scp check_deployment.sh %SERVER%:%REMOTE_PATH%/check_deployment.sh 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo %SSH_PASSWORD%| plink -ssh -pw %SSH_PASSWORD% %SERVER% "chmod +x %REMOTE_PATH%/check_deployment.sh" 2>nul
        echo [OK] 檢查腳本上傳成功
    ) else (
        echo [警告] 上傳失敗，將使用遠程命令檢查
        echo 提示: 如果 plink 不可用，請手動上傳文件
    )
) else (
    echo [OK] 檢查腳本上傳成功
)
echo.

echo [步驟 2/3] 執行部署檢查
echo ========================================
echo.
echo 提示: 如果提示輸入密碼，請輸入: %SSH_PASSWORD%
echo.
echo %SSH_PASSWORD%| plink -ssh -pw %SSH_PASSWORD% %SERVER% "if [ -f %REMOTE_PATH%/check_deployment.sh ]; then bash %REMOTE_PATH%/check_deployment.sh; else echo '檢查腳本不存在，執行基本檢查...'; bash -c 'echo \"=== 服務狀態 ===\" && sudo systemctl status luckyred-api --no-pager -l | head -15 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -15 && echo && echo \"=== 錯誤日誌 ===\" && sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15 && echo && sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -15'; fi"
echo.

echo [步驟 3/3] 生成診斷報告
echo ========================================
echo.
echo %SSH_PASSWORD%| plink -ssh -pw %SSH_PASSWORD% %SERVER% "echo '=== 文件檢查 ===' && test -f %REMOTE_PATH%/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在' && test -d %REMOTE_PATH%/api/.venv && echo '[OK] API虛擬環境存在' || echo '[ERROR] API虛擬環境不存在' && test -d %REMOTE_PATH%/bot/.venv && echo '[OK] Bot虛擬環境存在' || echo '[ERROR] Bot虛擬環境不存在' && echo && echo '=== 服務狀態摘要 ===' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo 'API服務: [運行中]' || echo 'API服務: [未運行]') && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo 'Bot服務: [運行中]' || echo 'Bot服務: [未運行]') && (sudo systemctl is-active nginx 2>/dev/null && echo 'Nginx服務: [運行中]' || echo 'Nginx服務: [未運行]')"
goto :end

:direct_ssh
echo [步驟 1/3] 上傳檢查腳本到服務器
echo ========================================
echo.
echo 正在上傳 check_deployment.sh...
scp -o ConnectTimeout=5 check_deployment.sh %SERVER%:%REMOTE_PATH%/check_deployment.sh
if %ERRORLEVEL% EQU 0 (
    echo [OK] 檢查腳本上傳成功
    ssh -o ConnectTimeout=5 %SERVER% "chmod +x %REMOTE_PATH%/check_deployment.sh"
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

:end
echo.
echo ========================================
echo   檢查完成
echo ========================================
echo.
echo 提示: 查看上面的輸出以了解服務狀態和錯誤信息
echo.

