@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   运行数据库迁移
echo ========================================
echo.

cd /d C:\hbgm001

echo 正在运行迁移脚本...
python migrations/add_interaction_mode.py

if errorlevel 1 (
    echo.
    echo ❌ 迁移失败
    pause
    exit /b 1
) else (
    echo.
    echo ✅ 迁移成功
    echo.
    echo 新字段已添加：
    echo   - interaction_mode
    echo   - last_interaction_mode
    echo   - seamless_switch_enabled
    echo.
)

pause
