@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   Lucky Red 快速部署
echo ============================================
echo.

powershell -ExecutionPolicy Bypass -File setup-and-deploy.ps1

pause
