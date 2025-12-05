@echo off
chcp 65001 >nul
title MiniApp API 全自動測試

echo.
echo 正在運行 MiniApp API 測試...
echo.

cd /d "c:\hbgm001"
python test_miniapp_api.py

echo.
pause
