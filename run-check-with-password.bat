@echo off
chcp 65001 >nul

echo ========================================
echo   LuckyRed 自動檢查（支持密碼輸入）
echo ========================================
echo.

REM 優先使用 PowerShell 版本（功能更完整）
if exist "auto-upload-and-check-with-password.ps1" (
    echo 使用 PowerShell 版本執行...
    echo.
    powershell -ExecutionPolicy Bypass -File "auto-upload-and-check-with-password.ps1"
) else (
    echo 使用批處理版本執行...
    echo.
    call "auto-upload-and-check-with-password.bat"
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo   執行失敗
    echo ========================================
    pause
    exit /b %ERRORLEVEL%
)

