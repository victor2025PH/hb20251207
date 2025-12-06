@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Lucky Red 部署測試
echo ========================================
echo.

cd /d C:\hbgm001

echo [步驟 1] 檢查本地更改...
git status --short
echo.

echo [步驟 2] 檢查 Git 狀態...
echo 本地最新提交:
git log --oneline -1
echo 遠程最新提交:
git log --oneline origin/master -1 2>nul || echo 無法獲取遠程提交
echo.

echo [步驟 3] 推送到遠程倉庫...
git push origin master
if %errorlevel% neq 0 (
    echo [警告] 推送失敗，將繼續部署本地代碼
)
echo.

echo [步驟 4] 連接到服務器並更新代碼...
echo 正在連接服務器 165.154.254.99...
echo.

ssh ubuntu@165.154.254.99 "cd /opt/luckyred && echo '=== 當前提交 ===' && git log --oneline -1 && echo '' && echo '=== 拉取最新代碼 ===' && git fetch origin && git reset --hard origin/master && echo '✓ 代碼已更新' && git log --oneline -1"
echo.

echo [步驟 5] 檢查服務狀態...
ssh ubuntu@165.154.254.99 "echo '=== Bot 服務狀態 ===' && sudo systemctl is-active luckyred-bot 2>&1 && echo '' && echo '=== API 服務狀態 ===' && sudo systemctl is-active luckyred-api 2>&1"
echo.

echo [步驟 6] 重啟服務...
ssh ubuntu@165.154.254.99 "cd /opt/luckyred && echo '=== 重啟 Bot 服務 ===' && sudo systemctl restart luckyred-bot && sleep 2 && sudo systemctl is-active luckyred-bot && echo '' && echo '=== 重啟 API 服務 ===' && sudo systemctl restart luckyred-api && sleep 2 && sudo systemctl is-active luckyred-api && echo '' && echo '✓ 服務重啟完成'"
echo.

echo [步驟 7] 查看 Bot 服務日誌（最後 20 行）...
ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-bot -n 20 --no-pager"
echo.

echo ========================================
echo   部署測試完成！
echo ========================================
echo.
echo 下一步：
echo   1. 在 Telegram 中測試 Bot: @sucai2025_bot
echo   2. 檢查錢包餘額是否正確顯示
echo   3. 測試發紅包功能
echo.
echo 查看實時日誌：
echo   ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-bot -f"
echo.
pause
