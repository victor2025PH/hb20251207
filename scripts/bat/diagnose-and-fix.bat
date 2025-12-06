@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   LuckyRed 服務診斷與修復
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99
set REMOTE_PATH=/opt/luckyred

echo [步驟 1] 檢查服務錯誤日誌
echo ========================================
echo.
echo --- API 服務錯誤日誌 ---
ssh %SERVER% "sudo journalctl -u luckyred-api -n 50 --no-pager | tail -30"
echo.
echo --- Bot 服務錯誤日誌 ---
ssh %SERVER% "sudo journalctl -u luckyred-bot -n 50 --no-pager | tail -30"
echo.

echo [步驟 2] 檢查關鍵文件
echo ========================================
echo.
ssh %SERVER% "echo '檢查 .env 文件:' && test -f %REMOTE_PATH%/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在'"
ssh %SERVER% "echo '檢查 API main.py:' && test -f %REMOTE_PATH%/api/main.py && echo '[OK] main.py存在' || echo '[ERROR] main.py不存在'"
ssh %SERVER% "echo '檢查 Bot main.py:' && test -f %REMOTE_PATH%/bot/main.py && echo '[OK] main.py存在' || echo '[ERROR] main.py不存在'"
ssh %SERVER% "echo '檢查 API 虛擬環境:' && test -d %REMOTE_PATH%/api/.venv && echo '[OK] 虛擬環境存在' || echo '[ERROR] 虛擬環境不存在'"
ssh %SERVER% "echo '檢查 Bot 虛擬環境:' && test -d %REMOTE_PATH%/bot/.venv && echo '[OK] 虛擬環境存在' || echo '[ERROR] 虛擬環境不存在'"
echo.

echo [步驟 3] 測試手動啟動
echo ========================================
echo.
echo --- 測試 API 模塊導入 ---
ssh %SERVER% "cd %REMOTE_PATH%/api && source .venv/bin/activate 2>/dev/null && python -c 'from main import app; print(\"API模塊導入成功\")' 2>&1 || echo 'API模塊導入失敗'"
echo.
echo --- 測試 Bot 模塊導入 ---
ssh %SERVER% "cd %REMOTE_PATH%/bot && source .venv/bin/activate 2>/dev/null && python -c 'import main; print(\"Bot模塊導入成功\")' 2>&1 || echo 'Bot模塊導入失敗'"
echo.

echo [步驟 4] 檢查環境變量
echo ========================================
echo.
ssh %SERVER% "if [ -f %REMOTE_PATH%/.env ]; then echo '環境變量檢查:' && grep -E '^(BOT_TOKEN|DATABASE_URL|SECRET_KEY)=' %REMOTE_PATH%/.env | sed 's/=.*/=***/' || echo '未找到關鍵環境變量'; else echo '[ERROR] .env文件不存在'; fi"
echo.

echo ========================================
echo   診斷完成
echo ========================================
echo.
echo 根據以上信息，常見問題和解決方案：
echo.
echo 1. 如果 .env 文件不存在或配置錯誤：
echo    - 檢查 /opt/luckyred/.env 文件
echo    - 確認 BOT_TOKEN, DATABASE_URL, SECRET_KEY 已設置
echo.
echo 2. 如果虛擬環境不存在：
echo    - 運行: cd /opt/luckyred/api && python3 -m venv .venv
echo    - 運行: cd /opt/luckyred/bot && python3 -m venv .venv
echo    - 安裝依賴: pip install -r requirements.txt
echo.
echo 3. 如果模塊導入失敗：
echo    - 檢查 Python 依賴是否安裝完整
echo    - 檢查 main.py 文件是否存在語法錯誤
echo    - 查看詳細錯誤日誌
echo.
echo 4. 如果數據庫連接失敗：
echo    - 檢查 DATABASE_URL 是否正確
echo    - 確認 PostgreSQL 服務正在運行
echo    - 檢查數據庫用戶權限
echo.

