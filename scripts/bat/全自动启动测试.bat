@echo off
chcp 65001 >nul
title Lucky Red Bot - 全自动启动测试
color 0A

echo.
echo ========================================
echo   Lucky Red Bot - 全自动启动测试
echo ========================================
echo.

cd /d C:\hbgm001

REM ========================================
REM 步骤 1: 检查环境
REM ========================================
echo [步骤 1/4] 检查环境配置...
echo.

if not exist .env (
    echo ❌ .env 文件不存在
    echo 请先创建 .env 文件并配置 BOT_TOKEN
    pause
    exit /b 1
)
echo ✅ .env 文件存在

if not exist "bot\main.py" (
    echo ❌ Bot 主文件不存在
    pause
    exit /b 1
)
echo ✅ Bot 文件存在
echo.

REM ========================================
REM 步骤 2: 运行数据库迁移
REM ========================================
echo [步骤 2/4] 运行数据库迁移...
echo.

if not exist "migrations\add_interaction_mode.py" (
    echo ⚠️  迁移脚本不存在，跳过迁移
) else (
    python migrations/add_interaction_mode.py
    if errorlevel 1 (
        echo ⚠️  数据库迁移可能有警告，继续...
    ) else (
        echo ✅ 数据库迁移完成
    )
)
echo.

REM ========================================
REM 步骤 3: 检查 Bot 虚拟环境
REM ========================================
echo [步骤 3/4] 检查 Bot 虚拟环境...
echo.

cd bot

if not exist .venv\Scripts\python.exe (
    echo   创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境已创建
) else (
    echo ✅ 虚拟环境已存在
)

REM 激活虚拟环境
echo   激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 无法激活虚拟环境
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

REM 检查依赖
echo   检查依赖...
if exist requirements.txt (
    echo   安装/更新依赖（这可能需要几分钟）...
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
    if errorlevel 1 (
        echo ⚠️  依赖安装可能有警告，继续...
    ) else (
        echo ✅ 依赖已安装
    )
) else (
    echo ⚠️  requirements.txt 不存在
)
echo.

REM ========================================
REM 步骤 4: 启动 Bot
REM ========================================
echo [步骤 4/4] 启动 Bot...
echo.
echo ========================================
echo   Bot 正在启动...
echo ========================================
echo.
echo 所有日志将显示在下方
echo 如果看到 "Bot @username started!" 说明启动成功
echo 按 Ctrl+C 停止 Bot
echo.
echo ========================================
echo.

REM 运行 Bot
python main.py

REM Bot 停止后
echo.
echo ========================================
echo   Bot 已停止
echo ========================================
echo.
deactivate
cd ..
echo 按任意键关闭窗口...
pause >nul
