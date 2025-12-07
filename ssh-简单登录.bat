@echo off
chcp 65001 >nul
title SSH 登录服务器

REM ==========================================
REM 简单的 SSH 登录脚本
REM ==========================================

set SERVER=ubuntu@165.154.254.99
set PASSWORD=Along2025!!!

REM 使用 plink 连接（如果可用）
where plink >nul 2>&1
if %errorlevel% equ 0 (
    echo y | plink -ssh -pw %PASSWORD% %SERVER%
    pause
    exit /b 0
)

REM 使用 sshpass 连接（如果可用）
where sshpass >nul 2>&1
if %errorlevel% equ 0 (
    sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no %SERVER%
    pause
    exit /b 0
)

REM 使用 SSH 密钥（如果存在）
if exist "%~dp0ssh_key" (
    ssh -i "%~dp0ssh_key" -o StrictHostKeyChecking=no %SERVER%
    pause
    exit /b 0
)

REM 使用 Windows SSH（需要手动输入密码）
where ssh >nul 2>&1
if %errorlevel% equ 0 (
    echo 密码: %PASSWORD%
    ssh %SERVER%
    pause
    exit /b 0
)

echo 未找到 SSH 客户端，请安装 PuTTY
pause
