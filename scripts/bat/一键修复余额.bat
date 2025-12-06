@echo off
chcp 65001 >nul
echo ========================================
echo 一键修复余额不同步问题
echo ========================================
echo.

echo [1/3] 检查数据库配置...
python -c "from shared.config.settings import get_settings; s = get_settings(); print('DATABASE_URL:', s.DATABASE_URL)"
echo.

echo [2/3] 检查当前余额...
python 诊断余额问题.py
echo.

echo [3/3] 更新余额（从MiniApp同步）...
python 更新余额.py
echo.

echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 现在请重新启动Bot并测试余额显示
echo.
pause
