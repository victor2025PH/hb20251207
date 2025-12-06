@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   Lucky Red 部署啟動
echo ============================================
echo.

powershell -ExecutionPolicy Bypass -File start-deployment.ps1

pause
