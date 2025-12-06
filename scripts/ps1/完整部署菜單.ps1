# 完整部署菜單腳本
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完整部署 Bot 菜單" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "c:\hbgm001"

# 步驟 1: 檢查關鍵文件
Write-Host "[1/7] 檢查關鍵文件..." -ForegroundColor Yellow
$files = @(
    "bot/keyboards/reply_keyboards.py",
    "bot/handlers/start.py",
    "bot/handlers/wallet.py",
    "bot/handlers/keyboard.py"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file 存在" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file 不存在" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# 步驟 2: 檢查 Git 狀態
Write-Host "[2/7] 檢查 Git 狀態..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    Write-Host "發現未提交的更改:" -ForegroundColor Yellow
    Write-Host $status
} else {
    Write-Host "  ✓ 沒有未提交的更改" -ForegroundColor Green
}
Write-Host ""

# 步驟 3: 添加所有文件
Write-Host "[3/7] 添加所有文件到 Git..." -ForegroundColor Yellow
git add -A
$added = git status --short
if ($added) {
    Write-Host "已添加的文件:" -ForegroundColor Cyan
    Write-Host $added
} else {
    Write-Host "  ✓ 沒有需要添加的文件" -ForegroundColor Green
}
Write-Host ""

# 步驟 4: 提交
Write-Host "[4/7] 提交更改..." -ForegroundColor Yellow
$commitMsg = "fix: 完整部署 ReplyKeyboard 多級菜單系統"
$commitResult = git commit -m $commitMsg 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 已提交: $commitMsg" -ForegroundColor Green
    Write-Host $commitResult
} else {
    if ($commitResult -match "nothing to commit") {
        Write-Host "  ℹ 沒有需要提交的更改" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ 提交失敗: $commitResult" -ForegroundColor Red
    }
}
Write-Host ""

# 步驟 5: 推送到遠程
Write-Host "[5/7] 推送到遠程倉庫..." -ForegroundColor Yellow
$pushResult = git push origin master 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 推送成功" -ForegroundColor Green
} else {
    Write-Host "  ✗ 推送失敗: $pushResult" -ForegroundColor Red
    Write-Host "  繼續執行服務器更新..." -ForegroundColor Yellow
}
Write-Host ""

# 步驟 6: 更新服務器代碼
Write-Host "[6/7] 更新服務器代碼..." -ForegroundColor Yellow
$serverUpdate = @"
cd /opt/luckyred && \
echo '=== 更新前提交 ===' && \
git log --oneline -1 && \
echo '' && \
echo '=== 拉取最新代碼 ===' && \
git fetch origin && \
git reset --hard origin/master && \
echo '✓ 代碼已更新' && \
echo '' && \
echo '=== 更新後提交 ===' && \
git log --oneline -1 && \
echo '' && \
echo '=== 驗證關鍵文件 ===' && \
ls -lh bot/keyboards/reply_keyboards.py 2>&1 && \
echo '' && \
echo '=== 檢查 start.py ===' && \
grep -n 'get_main_reply_keyboard' bot/handlers/start.py 2>&1 | head -3
"@

$updateResult = ssh ubuntu@165.154.254.99 $serverUpdate 2>&1
Write-Host $updateResult
Write-Host ""

# 步驟 7: 重啟服務
Write-Host "[7/7] 重啟 Bot 服務..." -ForegroundColor Yellow
$restartCmd = @"
sudo systemctl restart luckyred-bot && \
sleep 3 && \
echo '✓ 服務已重啟' && \
echo '' && \
echo '=== 服務狀態 ===' && \
sudo systemctl is-active luckyred-bot && \
echo '' && \
echo '=== 服務日誌（最後 15 行）===' && \
sudo journalctl -u luckyred-bot -n 15 --no-pager
"@

$restartResult = ssh ubuntu@165.154.254.99 $restartCmd 2>&1
Write-Host $restartResult
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "請在 Telegram 中測試：" -ForegroundColor Yellow
Write-Host "  1. 發送 /start 給 @sucai2025_bot" -ForegroundColor White
Write-Host "  2. 應該看到多級菜單按鈕（在輸入框下方）" -ForegroundColor White
Write-Host "  3. 按鈕包括：💰 錢包、🧧 紅包、📈 賺取、🎮 遊戲、👤 我的" -ForegroundColor White
Write-Host ""
