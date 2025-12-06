@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 全自動部署檢查與診斷
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

echo [檢查 1/10] 服務運行狀態
echo ========================================
ssh %SERVER% "echo '--- API 服務 ---' && sudo systemctl status luckyred-api --no-pager -l | head -15"
echo.
ssh %SERVER% "echo '--- Bot 服務 ---' && sudo systemctl status luckyred-bot --no-pager -l | head -15"
echo.
ssh %SERVER% "echo '--- Nginx 服務 ---' && sudo systemctl status nginx --no-pager | head -10"
echo.

echo [檢查 2/10] 服務錯誤日誌
echo ========================================
ssh %SERVER% "echo '--- API 最近錯誤 ---' && sudo journalctl -u luckyred-api -n 30 --no-pager | tail -20"
echo.
ssh %SERVER% "echo '--- Bot 最近錯誤 ---' && sudo journalctl -u luckyred-bot -n 30 --no-pager | tail -20"
echo.

echo [檢查 3/10] 部署目錄結構
echo ========================================
ssh %SERVER% "if [ -d %REMOTE_PATH% ]; then echo [OK] 目錄存在; ls -la %REMOTE_PATH% | head -15; else echo [ERROR] 目錄不存在; fi"
echo.

echo [檢查 4/10] 環境變量文件
echo ========================================
ssh %SERVER% "if [ -f %REMOTE_PATH%/.env ]; then echo [OK] .env文件存在; echo '環境變量鍵:' ; cat %REMOTE_PATH%/.env | grep -v '^#' | grep -v '^$' | cut -d'=' -f1 | sort; else echo [ERROR] .env文件不存在; fi"
echo.

echo [檢查 5/10] API 虛擬環境
echo ========================================
ssh %SERVER% "if [ -d %REMOTE_PATH%/api/.venv ]; then echo [OK] API虛擬環境存在; ls -la %REMOTE_PATH%/api/.venv/bin/ | grep -E '(python|uvicorn|pip)' | head -5; else echo [ERROR] API虛擬環境不存在; fi"
echo.

echo [檢查 6/10] Bot 虛擬環境
echo ========================================
ssh %SERVER% "if [ -d %REMOTE_PATH%/bot/.venv ]; then echo [OK] Bot虛擬環境存在; ls -la %REMOTE_PATH%/bot/.venv/bin/ | grep -E '(python|pip)' | head -5; else echo [ERROR] Bot虛擬環境不存在; fi"
echo.

echo [檢查 7/10] API 主文件
echo ========================================
ssh %SERVER% "if [ -f %REMOTE_PATH%/api/main.py ]; then echo [OK] main.py存在; head -20 %REMOTE_PATH%/api/main.py; else echo [ERROR] main.py不存在; fi"
echo.

echo [檢查 8/10] Bot 主文件
echo ========================================
ssh %SERVER% "if [ -f %REMOTE_PATH%/bot/main.py ]; then echo [OK] main.py存在; head -20 %REMOTE_PATH%/bot/main.py; else echo [ERROR] main.py不存在; fi"
echo.

echo [檢查 9/10] 前端文件
echo ========================================
ssh %SERVER% "if [ -d %REMOTE_PATH%/frontend/dist ]; then echo [OK] 前端dist目錄存在; ls -la %REMOTE_PATH%/frontend/dist | head -10; else echo [ERROR] 前端dist目錄不存在; fi"
echo.

echo [檢查 10/10] Nginx 配置和端口
echo ========================================
ssh %SERVER% "echo '--- Nginx 配置測試 ---' && sudo nginx -t 2>&1"
echo.
ssh %SERVER% "echo '--- 監聽端口 ---' && sudo netstat -tlnp 2>/dev/null | grep -E ':(80|443|8080)' || echo '未發現監聽端口'"
echo.

echo ========================================
echo   診斷測試
echo ========================================
echo.
echo [測試] 手動測試 API 啟動...
ssh %SERVER% "cd %REMOTE_PATH%/api && if [ -f .venv/bin/activate ]; then source .venv/bin/activate && python --version && python -c 'from main import app; print(\"[OK] API模塊可以導入\")' 2>&1 | head -10; else echo '[ERROR] 無法激活虛擬環境'; fi"
echo.

echo [測試] 手動測試 Bot 啟動...
ssh %SERVER% "cd %REMOTE_PATH%/bot && if [ -f .venv/bin/activate ]; then source .venv/bin/activate && python --version && python -c 'import main; print(\"[OK] Bot模塊可以導入\")' 2>&1 | head -10; else echo '[ERROR] 無法激活虛擬環境'; fi"
echo.

echo ========================================
echo   服務狀態摘要
echo ========================================
echo.
ssh %SERVER% "echo 'API服務:' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo '  [運行中]' || echo '  [未運行/失敗]') && echo 'Bot服務:' && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo '  [運行中]' || echo '  [未運行/失敗]') && echo 'Nginx服務:' && (sudo systemctl is-active nginx 2>/dev/null && echo '  [運行中]' || echo '  [未運行]')"
echo.

echo ========================================
echo   檢查完成
echo ========================================
echo.
echo 提示: 查看上面的錯誤日誌以了解服務失敗原因
echo.
