@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 服務修復腳本
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

echo [步驟 1] 診斷問題
echo ========================================
echo.
echo 檢查 API 服務錯誤...
ssh %SERVER% "sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15"
echo.
echo 檢查 Bot 服務錯誤...
ssh %SERVER% "sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -15"
echo.

echo [步驟 2] 檢查必要文件
echo ========================================
ssh %SERVER% "test -f %REMOTE_PATH%/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在 - 需要創建'"
ssh %SERVER% "test -d %REMOTE_PATH%/api/.venv && echo '[OK] API虛擬環境存在' || echo '[ERROR] API虛擬環境不存在'"
ssh %SERVER% "test -d %REMOTE_PATH%/bot/.venv && echo '[OK] Bot虛擬環境存在' || echo '[ERROR] Bot虛擬環境不存在'"
echo.

echo [步驟 3] 測試模塊導入
echo ========================================
echo 測試 API 模塊...
ssh %SERVER% "cd %REMOTE_PATH%/api && source .venv/bin/activate 2>/dev/null && python -c 'from main import app' 2>&1 | head -10 || echo 'API模塊導入失敗'"
echo.
echo 測試 Bot 模塊...
ssh %SERVER% "cd %REMOTE_PATH%/bot && source .venv/bin/activate 2>/dev/null && python -c 'import main' 2>&1 | head -10 || echo 'Bot模塊導入失敗'"
echo.

echo [步驟 4] 修復建議
echo ========================================
echo.
echo 根據診斷結果，執行以下修復步驟：
echo.
echo 1. 如果 .env 文件不存在或配置錯誤：
echo    ssh %SERVER% "nano %REMOTE_PATH%/.env"
echo    確認以下變量已設置：
echo    - BOT_TOKEN
echo    - DATABASE_URL
echo    - SECRET_KEY
echo.
echo 2. 如果虛擬環境不存在：
echo    ssh %SERVER% "cd %REMOTE_PATH%/api && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
echo    ssh %SERVER% "cd %REMOTE_PATH%/bot && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
echo.
echo 3. 如果依賴缺失：
echo    ssh %SERVER% "cd %REMOTE_PATH%/api && source .venv/bin/activate && pip install -r requirements.txt"
echo    ssh %SERVER% "cd %REMOTE_PATH%/bot && source .venv/bin/activate && pip install -r requirements.txt"
echo.
echo 4. 檢查文件權限：
echo    ssh %SERVER% "sudo chown -R www-data:www-data %REMOTE_PATH%"
echo.
echo 5. 重啟服務：
echo    ssh %SERVER% "sudo systemctl restart luckyred-api luckyred-bot"
echo    ssh %SERVER% "sudo systemctl status luckyred-api luckyred-bot"
echo.

echo ========================================
echo   診斷完成
echo ========================================

