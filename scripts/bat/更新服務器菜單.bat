@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   更新服務器 Bot 菜單
echo ========================================
echo.

cd /d C:\hbgm001

echo [步驟 1] 檢查本地更改...
git status --short
echo.

echo [步驟 2] 提交本地更改（如果有）...
git add -A
git commit -m "fix: 更新 Bot 菜單和餘額查詢邏輯" 2>nul || echo 沒有需要提交的更改
echo.

echo [步驟 3] 推送到遠程倉庫...
git push origin master
if %errorlevel% neq 0 (
    echo [警告] 推送失敗，請檢查網絡連接
    pause
    exit /b 1
)
echo.

echo [步驟 4] 連接到服務器並更新代碼...
echo 正在連接服務器 165.154.254.99...
echo.

ssh ubuntu@165.154.254.99 "cd /opt/luckyred && echo '=== 更新前提交 ===' && git log --oneline -1 && echo '' && echo '=== 拉取最新代碼 ===' && git fetch origin && git reset --hard origin/master && echo '✓ 代碼已更新' && echo '' && echo '=== 更新後提交 ===' && git log --oneline -1 && echo '' && echo '=== 驗證關鍵文件 ===' && ls -lh bot/keyboards/reply_keyboards.py bot/handlers/start.py 2>&1 && echo '' && echo '=== 檢查 start.py 中的 ReplyKeyboard ===' && grep -n 'get_main_reply_keyboard' bot/handlers/start.py 2>&1 | head -3"
echo.

echo [步驟 5] 停止 Bot 服務...
ssh ubuntu@165.154.254.99 "sudo systemctl stop luckyred-bot && echo '✓ Bot 服務已停止'"
echo.

echo [步驟 6] 重啟 Bot 服務...
ssh ubuntu@165.154.254.99 "sudo systemctl start luckyred-bot && sleep 3 && echo '✓ Bot 服務已啟動' && echo '' && echo '=== 服務狀態 ===' && sudo systemctl is-active luckyred-bot && echo '' && echo '=== 服務日誌（最後 20 行）===' && sudo journalctl -u luckyred-bot -n 20 --no-pager"
echo.

echo ========================================
echo   更新完成！
echo ========================================
echo.
echo 請在 Telegram 中測試：
echo   1. 發送 /start 給 @sucai2025_bot
echo   2. 應該看到多級菜單按鈕（在輸入框下方）
echo   3. 檢查錢包餘額是否正確顯示
echo.
echo 查看實時日誌：
echo   ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-bot -f"
echo.
pause
