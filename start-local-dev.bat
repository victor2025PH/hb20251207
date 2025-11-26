@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 本地開發環境啟動
echo ========================================
echo.

cd /d C:\hbgm001

REM 檢查 .env 文件
if not exist ".env" (
    echo [ERROR] .env 文件不存在！
    echo 請先創建 .env 文件，參考 env.example.txt
    pause
    exit /b 1
)
echo [OK] .env 文件存在
echo.

REM ========================================
REM 步驟 1: 安裝前端依賴並啟動
REM ========================================
echo [步驟 1] 啟動前端開發服務器
echo ========================================
echo.

cd frontend
echo 檢查 node_modules...
if not exist "node_modules" (
    echo 正在安裝前端依賴...
    call npm install
)
echo.

echo 正在後台啟動前端服務器 (端口 3001)...
start "Frontend Dev Server" cmd /c "npm run dev"
echo [OK] 前端服務器啟動中...
timeout /t 3 /nobreak >nul
echo.

REM ========================================
REM 步驟 2: 設置 Python 虛擬環境並啟動 API
REM ========================================
echo [步驟 2] 啟動後端 API 服務
echo ========================================
echo.

cd /d C:\hbgm001\api
echo 檢查 Python 虛擬環境...
if not exist ".venv" (
    echo 正在創建虛擬環境...
    python -m venv .venv
)

echo 激活虛擬環境並安裝依賴...
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo.
echo 正在後台啟動 API 服務器 (端口 8080)...
start "API Server" cmd /c ".venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload"
echo [OK] API 服務器啟動中...
timeout /t 3 /nobreak >nul
echo.

REM ========================================
REM 步驟 3: 啟動 Bot
REM ========================================
echo [步驟 3] 啟動 Telegram Bot
echo ========================================
echo.

cd /d C:\hbgm001\bot
echo 檢查 Python 虛擬環境...
if not exist ".venv" (
    echo 正在創建虛擬環境...
    python -m venv .venv
)

echo 激活虛擬環境並安裝依賴...
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo.
echo 正在後台啟動 Bot...
start "Telegram Bot" cmd /c ".venv\Scripts\python.exe main.py"
echo [OK] Bot 啟動中...
timeout /t 3 /nobreak >nul
echo.

cd /d C:\hbgm001

echo ========================================
echo   所有服務已啟動
echo ========================================
echo.
echo 訪問地址:
echo   前端 MiniApp: http://localhost:3001
echo   API 文檔:     http://localhost:8080/docs
echo.
echo 提示:
echo   - 每個服務都在單獨的窗口中運行
echo   - 關閉窗口即可停止對應服務
echo   - 查看窗口可以看到實時日誌
echo.
echo 按任意鍵打開瀏覽器訪問...
pause >nul

start http://localhost:3001
start http://localhost:8080/docs

