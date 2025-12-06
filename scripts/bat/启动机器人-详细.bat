@echo off
chcp 65001 >nul
title Lucky Red Bot
color 0A

echo.
echo ========================================
echo   Lucky Red Bot 启动脚本
echo ========================================
echo.

cd /d C:\hbgm001

REM 检查 .env 文件
echo [检查] .env 文件...
if not exist .env (
    echo   ✗ .env 文件不存在！
    echo   请先创建 .env 文件并填入 BOT_TOKEN
    echo   可以从 .env.example 复制
    pause
    exit /b 1
) else (
    echo   ✓ .env 文件存在
)

cd bot

REM 检查虚拟环境
echo.
echo [检查] 虚拟环境...
if not exist .venv\Scripts\python.exe (
    echo   虚拟环境不存在，正在创建...
    python -m venv .venv
    if errorlevel 1 (
        echo   ✗ 创建虚拟环境失败
        echo   请检查 Python 是否已安装
        pause
        exit /b 1
    )
    echo   ✓ 虚拟环境已创建
) else (
    echo   ✓ 虚拟环境已存在
)

REM 激活虚拟环境
echo.
echo [步骤] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo   ✗ 无法激活虚拟环境
    pause
    exit /b 1
)
echo   ✓ 虚拟环境已激活

REM 检查 Python 版本
echo.
echo [检查] Python 版本...
python --version
if errorlevel 1 (
    echo   ✗ Python 无法运行
    pause
    exit /b 1
)

REM 安装依赖
echo.
echo [步骤] 安装依赖...
python -m pip install --upgrade pip -q
echo   正在安装依赖包（这可能需要几分钟）...
pip install -r requirements.txt
if errorlevel 1 (
    echo   ⚠️  依赖安装可能有错误，但继续尝试启动...
) else (
    echo   ✓ 依赖已安装
)

REM 启动机器人
echo.
echo ========================================
echo   启动机器人...
echo ========================================
echo.
echo 所有日志将显示在下方
echo 如果看到 "Bot @username started!" 说明启动成功
echo 按 Ctrl+C 停止 Bot
echo.
echo ========================================
echo.

python main.py

REM 如果到这里，说明机器人已停止
echo.
echo ========================================
echo   Bot 已停止
echo ========================================
echo.
deactivate
echo 按任意键关闭窗口...
pause >nul
