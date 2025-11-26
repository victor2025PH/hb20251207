@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   上傳所有檢查和修復腳本到服務器
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred
set REMOTE_SCRIPTS_DIR=%REMOTE_PATH%/scripts

echo 正在創建遠程腳本目錄...
ssh %SERVER% "mkdir -p %REMOTE_SCRIPTS_DIR%"
echo.

echo [1/1] 上傳 check_deployment.sh...
scp check_deployment.sh %SERVER%:%REMOTE_SCRIPTS_DIR%/check_deployment.sh
if %ERRORLEVEL% EQU 0 (
    echo [OK] check_deployment.sh 上傳成功
    ssh %SERVER% "chmod +x %REMOTE_SCRIPTS_DIR%/check_deployment.sh"
) else (
    echo [ERROR] check_deployment.sh 上傳失敗
)
echo.

echo ========================================
echo   上傳完成
echo ========================================
echo.
echo 現在可以在服務器上執行：
echo   ssh %SERVER% "bash %REMOTE_SCRIPTS_DIR%/check_deployment.sh"
echo.
echo 或使用本地腳本自動檢查：
echo   .\auto-upload-and-check.bat
echo.

