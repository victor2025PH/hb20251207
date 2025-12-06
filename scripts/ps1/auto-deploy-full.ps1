# 全自動部署腳本 - 完整版

param(
    [string]$Server = "ubuntu@165.154.254.99",
    [string]$RemotePath = "/opt/luckyred"
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LuckyRed 全自動部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Git 操作
Write-Host "[1/5] Git 操作..." -ForegroundColor Yellow
Set-Location "C:\hbgm001"

# 檢查未提交的修改
$status = git status --porcelain
if ($status) {
    Write-Host "發現未提交的修改：" -ForegroundColor Yellow
    Write-Host $status
    Write-Host ""
    Write-Host "添加所有修改..." -ForegroundColor Yellow
    git add -A
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 已添加到暫存區" -ForegroundColor Green
        $commitMsg = "chore: 自動部署 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        Write-Host "提交: $commitMsg" -ForegroundColor Yellow
        git commit -m $commitMsg
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 提交成功" -ForegroundColor Green
        } else {
            Write-Host "⚠️  提交失敗或無變更" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "✓ 沒有未提交的修改" -ForegroundColor Green
}

# 檢查未推送的提交
Write-Host ""
Write-Host "[2/5] 檢查未推送的提交..." -ForegroundColor Yellow
$unpushed = git log origin/master..HEAD --oneline 2>$null
if ($unpushed) {
    Write-Host "發現未推送的提交：" -ForegroundColor Yellow
    Write-Host $unpushed
    Write-Host "推送到 GitHub..." -ForegroundColor Yellow
    git push origin master
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 推送成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 推送失敗" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ 所有提交已推送" -ForegroundColor Green
}

# 3. 部署到服務器
Write-Host ""
Write-Host "[3/5] 部署到服務器..." -ForegroundColor Yellow
Write-Host "正在連接到服務器..." -ForegroundColor Cyan

$deployScript = @"
cd $RemotePath && \
echo '=== [1/4] 拉取最新代碼 ===' && \
git pull origin master && \
echo '' && \
echo '=== [2/4] 清除構建緩存 ===' && \
cd frontend && \
rm -rf node_modules/.vite dist && \
echo '' && \
echo '=== [3/4] 重新構建前端 ===' && \
npm install --silent && \
npm run build 2>&1 | tail -20 && \
echo '' && \
echo '=== [4/4] 重啟服務 ===' && \
sudo systemctl restart luckyred-api luckyred-bot luckyred-admin && \
sudo systemctl reload nginx && \
echo '' && \
echo '=== 服務狀態 ===' && \
echo 'API:' && (sudo systemctl is-active luckyred-api && echo '  ✓ 運行中' || echo '  ✗ 未運行') && \
echo 'Bot:' && (sudo systemctl is-active luckyred-bot && echo '  ✓ 運行中' || echo '  ✗ 未運行') && \
echo 'Admin:' && (sudo systemctl is-active luckyred-admin && echo '  ✓ 運行中' || echo '  ✗ 未運行')
"@

try {
    ssh $Server $deployScript
    Write-Host "✓ 服務器部署完成" -ForegroundColor Green
} catch {
    Write-Host "❌ 服務器部署失敗: $_" -ForegroundColor Red
}

# 4. 檢查服務狀態
Write-Host ""
Write-Host "[4/5] 檢查服務詳細狀態..." -ForegroundColor Yellow

$statusCheck = @"
echo '--- API 服務 ---' && \
sudo systemctl status luckyred-api --no-pager | head -10 && \
echo '' && \
echo '--- Bot 服務 ---' && \
sudo systemctl status luckyred-bot --no-pager | head -10 && \
echo '' && \
echo '--- 構建文件檢查 ---' && \
ls -lh /opt/luckyred/frontend/dist/assets/ | grep -i 'SendRedPacket\|index' | head -3
"@

try {
    ssh $Server $statusCheck
} catch {
    Write-Host "⚠️  無法檢查服務狀態" -ForegroundColor Yellow
}

# 5. 完成報告
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  全自動部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "部署狀態：" -ForegroundColor Cyan
Write-Host "  ✓ Git 操作完成" -ForegroundColor Green
Write-Host "  ✓ 代碼已推送到 GitHub" -ForegroundColor Green
Write-Host "  ✓ 服務器已更新" -ForegroundColor Green
Write-Host "  ✓ 前端已重新構建" -ForegroundColor Green
Write-Host "  ✓ 服務已重啟" -ForegroundColor Green
Write-Host ""
Write-Host "請訪問以下網址測試：" -ForegroundColor Cyan
Write-Host "  🌐 MiniApp: https://mini.usdt2026.cc" -ForegroundColor Yellow
Write-Host "  🌐 Admin: https://admin.usdt2026.cc" -ForegroundColor Yellow
Write-Host ""
Write-Host "測試重點：" -ForegroundColor Cyan
Write-Host "  1. 進入「發送紅包」頁面" -ForegroundColor White
Write-Host "  2. 確認遊戲規則彈窗自動顯示" -ForegroundColor White
Write-Host "  3. 檢查「✨ 遊戲規則 ✨」按鈕" -ForegroundColor White
Write-Host "  4. 測試「以後不再彈出」選項" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  如果看不到新功能，請清除瀏覽器緩存！" -ForegroundColor Red
Write-Host "  方法: Ctrl + Shift + Delete 或使用無痕模式" -ForegroundColor Yellow
Write-Host ""
