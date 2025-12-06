@echo off
chcp 65001 >nul
title Lucky Red Bot - 机器人运行窗口
color 0A

echo.
echo ========================================
echo   Lucky Red Bot 启动中...
echo ========================================
echo.

cd /d C:\hbgm001\bot

REM 检查虚拟环境
if not exist .venv\Scripts\python.exe (
    echo [1/3] 创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo   错误: 无法创建虚拟环境
        pause
        exit /b 1
    )
    echo   ✓ 虚拟环境已创建
) else (
    echo [1/3] ✓ 虚拟环境已存在
)

REM 激活虚拟环境
echo.
echo [2/3] 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo   错误: 无法激活虚拟环境
    pause
    exit /b 1
)

REM 安装依赖
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
echo   ✓ 依赖已安装

REM 启动机器人
echo.
echo [3/3] 启动机器人...
echo.
echo ========================================
echo   Bot 正在运行...
echo ========================================
echo.
echo 所有日志将显示在下方
echo 按 Ctrl+C 停止 Bot
echo.
echo ========================================
echo.

python main.py

echo.
echo ========================================
echo   Bot 已停止
echo ========================================
echo.
deactivate
pause
