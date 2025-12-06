@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Lucky Red - 启动API服务器
echo ========================================
echo.

cd /d C:\hbgm001

echo 正在启动API服务器...
echo.

REM 在新窗口中启动API服务器
start "Lucky Red API Server" cmd /k "cd /d C:\hbgm001\api && python main.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   API服务器已在新窗口中启动！
echo ========================================
echo.
echo API服务器运行在: http://localhost:8080
echo API文档: http://localhost:8080/docs
echo.
echo 请查看新打开的窗口确认启动状态
echo.
pause
