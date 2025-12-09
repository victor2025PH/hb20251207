@echo off
chcp 65001 >nul
title SSH 连接到服务器

REM 打开 PowerShell 并 SSH 连接到服务器
start powershell -NoExit -Command "ssh ubuntu@165.154.254.99"

