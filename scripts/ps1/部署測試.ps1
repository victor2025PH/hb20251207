# ============================================
# Lucky Red 部署測試腳本
# 將代碼推送到服務器並重啟服務
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lucky Red 部署測試" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SERVER = "ubuntu@165.154.254.99"
$REMOTE_PATH = "/opt/luckyred"

# ============================================
# 第一步：檢查 Git 狀態並提交更改
# ============================================
Write-Host "第一步：檢查本地更改..." -ForegroundColor Yellow
Write-Host ""

$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "發現未提交的更改：" -ForegroundColor Yellow
    Write-Host $gitStatus -ForegroundColor Gray
    Write-Host ""
    
    $commit = Read-Host "是否提交這些更改？(Y/N)"
    if ($commit -eq "Y" -or $commit -eq "y") {
        $commitMsg = Read-Host "請輸入提交信息（留空使用默認）"
        if ([string]::IsNullOrWhiteSpace($commitMsg)) {
            $commitMsg = "部署測試: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
        git add .
        git commit -m $commitMsg
        Write-Host "✓ 已提交更改" -ForegroundColor Green
    }
} else {
    Write-Host "✓ 沒有未提交的更改" -ForegroundColor Green
}

# ============================================
# 第二步：推送到遠程倉庫
# ============================================
Write-Host ""
Write-Host "第二步：推送到遠程倉庫..." -ForegroundColor Yellow
Write-Host ""

$push = Read-Host "是否推送到遠程倉庫？(Y/N)"
if ($push -eq "Y" -or $push -eq "y") {
    Write-Host "正在推送..." -ForegroundColor Cyan
    git push origin master
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 推送成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 推送失敗" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "跳過推送，將直接部署本地代碼" -ForegroundColor Yellow
}

# ============================================
# 第三步：連接到服務器並更新代碼
# ============================================
Write-Host ""
Write-Host "第三步：連接到服務器並更新代碼..." -ForegroundColor Yellow
Write-Host ""

Write-Host "正在連接到服務器: $SERVER" -ForegroundColor Cyan
Write-Host ""

# 檢查服務器連接
Write-Host "檢查服務器連接..." -ForegroundColor Cyan
$testConnection = ssh -o ConnectTimeout=5 $SERVER "echo '連接成功'" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 無法連接到服務器，請檢查：" -ForegroundColor Red
    Write-Host "  1. SSH 密鑰是否已配置" -ForegroundColor Yellow
    Write-Host "  2. 服務器 IP 是否正確: $SERVER" -ForegroundColor Yellow
    Write-Host "  3. 網絡連接是否正常" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ 服務器連接正常" -ForegroundColor Green
Write-Host ""

# 更新代碼
Write-Host "更新服務器代碼..." -ForegroundColor Cyan
$updateCmd = @"
cd $REMOTE_PATH && \
echo '=== 當前提交 ===' && \
git log --oneline -1 && \
echo '' && \
echo '=== 拉取最新代碼 ===' && \
git fetch origin && \
git reset --hard origin/master && \
echo '✓ 代碼已更新' && \
git log --oneline -1
"@

ssh $SERVER $updateCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 代碼更新失敗" -ForegroundColor Red
    exit 1
}

Write-Host "✓ 代碼更新成功" -ForegroundColor Green
Write-Host ""

# ============================================
# 第四步：檢查服務狀態
# ============================================
Write-Host "第四步：檢查服務狀態..." -ForegroundColor Yellow
Write-Host ""

$statusCmd = @"
echo '=== Bot 服務狀態 ===' && \
sudo systemctl is-active luckyred-bot 2>&1 && \
echo '' && \
echo '=== API 服務狀態 ===' && \
sudo systemctl is-active luckyred-api 2>&1 && \
echo '' && \
echo '=== 數據庫連接 ===' && \
cd $REMOTE_PATH && \
if [ -f .env ]; then \
  grep -q 'DATABASE_URL' .env && echo '✓ .env 文件存在且包含 DATABASE_URL' || echo '✗ .env 文件缺少 DATABASE_URL'; \
else \
  echo '✗ .env 文件不存在'; \
fi
"@

ssh $SERVER $statusCmd
Write-Host ""

# ============================================
# 第五步：重啟服務
# ============================================
Write-Host "第五步：重啟服務..." -ForegroundColor Yellow
Write-Host ""

$restart = Read-Host "是否重啟 Bot 和 API 服務？(Y/N)"
if ($restart -eq "Y" -or $restart -eq "y") {
    Write-Host "正在重啟服務..." -ForegroundColor Cyan
    
    $restartCmd = @"
cd $REMOTE_PATH && \
echo '=== 重啟 Bot 服務 ===' && \
sudo systemctl restart luckyred-bot && \
sleep 2 && \
sudo systemctl is-active luckyred-bot && \
echo '' && \
echo '=== 重啟 API 服務 ===' && \
sudo systemctl restart luckyred-api && \
sleep 2 && \
sudo systemctl is-active luckyred-api && \
echo '' && \
echo '✓ 服務重啟完成'
"@
    
    ssh $SERVER $restartCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 服務重啟成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 服務重啟失敗" -ForegroundColor Red
    }
} else {
    Write-Host "跳過服務重啟" -ForegroundColor Yellow
}

# ============================================
# 第六步：查看服務日誌
# ============================================
Write-Host ""
Write-Host "第六步：查看服務日誌..." -ForegroundColor Yellow
Write-Host ""

$viewLogs = Read-Host "是否查看 Bot 服務日誌？(Y/N)"
if ($viewLogs -eq "Y" -or $viewLogs -eq "y") {
    Write-Host "Bot 服務日誌（最後 20 行）：" -ForegroundColor Cyan
    Write-Host ""
    ssh $SERVER "sudo journalctl -u luckyred-bot -n 20 --no-pager"
    Write-Host ""
    
    $viewApiLogs = Read-Host "是否查看 API 服務日誌？(Y/N)"
    if ($viewApiLogs -eq "Y" -or $viewApiLogs -eq "y") {
        Write-Host "API 服務日誌（最後 20 行）：" -ForegroundColor Cyan
        Write-Host ""
        ssh $SERVER "sudo journalctl -u luckyred-api -n 20 --no-pager"
    }
}

# ============================================
# 完成
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署測試完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 在 Telegram 中測試 Bot: @sucai2025_bot" -ForegroundColor White
Write-Host "  2. 檢查錢包餘額是否正確顯示" -ForegroundColor White
Write-Host "  3. 測試發紅包功能" -ForegroundColor White
Write-Host ""
Write-Host "查看實時日誌：" -ForegroundColor Yellow
Write-Host "  ssh $SERVER 'sudo journalctl -u luckyred-bot -f'" -ForegroundColor Gray
Write-Host ""
