@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   快速啟動本地服務
echo ========================================
echo.

cd /d C:\hbgm001

echo [1/3] 檢查前端依賴...
cd frontend
if not exist node_modules (
    echo 安裝前端依賴...
    call npm install
)
cd ..

echo.
echo [2/3] 啟動前端服務器 (http://localhost:3001)...
start "前端開發服務器" cmd /k "cd /d C:\hbgm001\frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] 啟動 API 服務器 (http://localhost:8080)...
cd api
if not exist .venv (
    echo 創建虛擬環境...
    python -m venv .venv
)
cd ..
start "API 服務器" cmd /k "cd /d C:\hbgm001\api && .venv\Scripts\activate.bat && python main.py"

echo.
echo ========================================
echo   服務啟動中...
echo ========================================
echo.
echo 前端: http://localhost:3001
echo API:  http://localhost:8080
echo.
echo 請等待幾秒鐘讓服務完全啟動
echo 如果出現錯誤，請檢查打開的命令窗口
echo.
timeout /t 5 /nobreak >nul

echo.
echo 正在檢查服務狀態...
timeout /t 3 /nobreak >nul

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3001' -TimeoutSec 2 -UseBasicParsing; Write-Host '✓ 前端服務器運行正常' -ForegroundColor Green } catch { Write-Host '前端服務器可能還在啟動中...' -ForegroundColor Yellow }"

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/docs' -TimeoutSec 2 -UseBasicParsing; Write-Host '✓ API 服務器運行正常' -ForegroundColor Green } catch { Write-Host 'API 服務器可能還在啟動中...' -ForegroundColor Yellow }"

echo.
echo 請在瀏覽器中訪問 http://localhost:3001
echo.
pause
