@echo off
chcp 65001 >nul
echo ==========================================
echo   📤 上传代码到 GitHub
echo ==========================================
echo.

cd /d "%~dp0\..\.."

echo [1/4] 检查 Git 状态...
git status

echo.
echo [2/4] 添加所有更改...
git add -A

echo.
echo [3/4] 提交更改...
set /p COMMIT_MSG="请输入提交信息 (直接回车使用默认): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=更新代码: %date% %time%
git commit -m "%COMMIT_MSG%"

echo.
echo [4/4] 推送到 GitHub...
git push origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo   ✅ 上传成功！
    echo ==========================================
    echo.
    echo 📝 下一步：在服务器上执行拉取命令
    echo    bash scripts/sh/从GitHub拉取并部署.sh
    echo.
) else (
    echo.
    echo ==========================================
    echo   ❌ 上传失败！
    echo ==========================================
    echo.
    echo 请检查：
    echo   1. Git 远程仓库配置是否正确
    echo   2. 是否有推送权限
    echo   3. 网络连接是否正常
    echo.
)

pause

