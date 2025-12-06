@echo off
chcp 65001 >nul
title 紅包遊戲 MiniApp 開發服務器

echo ================================================
echo    紅包遊戲 MiniApp - 本地開發服務器
echo ================================================
echo.

cd /d "c:\hbgm001\frontend"

echo [1/2] 檢查依賴...
if not exist "node_modules" (
    echo 正在安裝依賴，請稍候...
    call npm install
)

echo.
echo [2/2] 啟動開發服務器...
echo.
echo ================================================
echo    服務器啟動後訪問: http://localhost:3001
echo ================================================
echo.

call npm run dev

pause
