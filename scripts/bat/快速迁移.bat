@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   快速数据库迁移
echo ========================================
echo.

cd /d C:\hbgm001

echo 正在运行迁移...
python 直接添加字段.py

echo.
echo 如果看到 "✅ 迁移成功！所有字段已添加"
echo 说明迁移已完成
echo.
pause
