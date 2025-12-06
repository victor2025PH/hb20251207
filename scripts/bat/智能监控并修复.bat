@echo off
chcp 65001 >nul
title 智能监控并修复系统
color 0A

echo.
echo ========================================
echo   智能监控并修复系统
echo ========================================
echo.

:loop
echo [%date% %time%] 开始检测...
echo.

python 自动检测并修复.py
set FIX_RESULT=%ERRORLEVEL%

echo.
if %FIX_RESULT% == 0 (
    echo ✅ 检测完成，没有发现错误
    echo.
    echo 正在启动Bot...
    echo.
    call "一键启动测试.bat"
    goto end
) else (
    echo ⚠️  发现错误，已尝试修复
    echo.
    echo 等待3秒后重新检测...
    timeout /t 3 /nobreak >nul
    echo.
    goto loop
)

:end
echo.
echo ========================================
echo   监控结束
echo ========================================
pause
