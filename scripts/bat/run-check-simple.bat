@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 自動檢查（帶超時保護）
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set TIMEOUT=10

echo 正在測試 SSH 連接...
echo 如果 %TIMEOUT% 秒內無響應，將顯示錯誤信息
echo.

REM 測試 SSH 連接（帶超時）
timeout /t 1 /nobreak >nul
ssh -o ConnectTimeout=%TIMEOUT% -o BatchMode=yes %SERVER% "echo '連接成功'" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo   ❌ SSH 連接失敗
    echo ========================================
    echo.
    echo 可能的原因：
    echo   1. 需要輸入 SSH 密碼（未配置 SSH 密鑰）
    echo   2. 服務器無響應或離線
    echo   3. 網絡連接問題
    echo   4. 防火牆阻擋
    echo.
    echo 建議操作：
    echo   1. 手動測試: ssh %SERVER%
    echo   2. 檢查服務器 IP: 165.154.254.99
    echo   3. 配置 SSH 密鑰以避免輸入密碼
    echo.
    echo 如果確定服務器正常，可以手動執行：
    echo   .\auto-upload-and-check.bat
    echo.
    pause
    exit /b 1
)

echo [OK] SSH 連接成功
echo.
echo 正在執行完整檢查...
echo.

call auto-upload-and-check.bat

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo   檢查過程中出現錯誤
    echo ========================================
    echo.
    echo 退出代碼: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo   檢查完成
echo ========================================
pause

