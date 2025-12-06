@echo off
chcp 65001 >nul
echo ========================================
echo   執行自動檢查（帶超時保護）
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0auto-upload-and-check-with-timeout.ps1" -TimeoutSeconds 10

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo   執行失敗
    echo ========================================
    pause
    exit /b %ERRORLEVEL%
)

