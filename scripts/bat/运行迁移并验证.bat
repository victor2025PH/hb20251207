@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   运行数据库迁移并验证
echo ========================================
echo.

cd /d C:\hbgm001

echo [1/2] 运行数据库迁移...
python migrations/add_interaction_mode.py
if errorlevel 1 (
    echo.
    echo ❌ 迁移失败
    echo.
    echo 请检查错误信息
    pause
    exit /b 1
)
echo.
echo ✅ 迁移脚本执行完成
echo.

echo [2/2] 验证数据库字段...
python 检查数据库字段.py
echo.

echo ========================================
echo   完成
echo ========================================
echo.
pause
