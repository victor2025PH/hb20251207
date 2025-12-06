# ============================================
# LuckyRed 全自動部署腳本
# ============================================

param(
    [string]$Server = "ubuntu@165.154.254.99",
    [string]$RemotePath = "/opt/luckyred"
)

$ErrorActionPreference = "Stop"

# 顏色輸出函數
function Write-Step {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host "`n========================================" -ForegroundColor $Color
    Write-Host "  $Message" -ForegroundColor $Color
    Write-Host "========================================" -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 檢查 SSH 連接
function Test-SSHConnection {
    param([string]$Server)
    Write-Info "測試 SSH 連接..."
    try {
        $result = ssh -o ConnectTimeout=5 -o BatchMode=yes $Server "echo 'SSH connection successful'" 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        } else {
            Write-Warn "SSH 需要密碼認證，將在部署時提示輸入"
            return $false
        }
    } catch {
        Write-Warn "SSH 連接測試失敗，將在部署時提示輸入密碼"
        return $false
    }
}

# 執行 SSH 命令
function Invoke-SSHCommand {
    param(
        [string]$Server,
        [string]$Command
    )
    
    Write-Info "執行命令: $Command"
    
    # 構建完整的 SSH 命令
    $sshCommand = "ssh $Server `"$Command`""
    
    try {
        $output = Invoke-Expression $sshCommand 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "命令執行失敗 (退出碼: $LASTEXITCODE)"
            Write-Host $output
            throw "SSH 命令執行失敗"
        }
        return $output
    } catch {
        Write-Error "執行 SSH 命令時發生錯誤: $_"
        throw
    }
}

# 主部署流程
Write-Step "LuckyRed 全自動部署" "Cyan"

# 步驟 1: 檢查本地 Git 狀態
Write-Step "步驟 1: 檢查本地 Git 狀態" "Yellow"
Set-Location "C:\hbgm001"

$gitStatus = git status --short
if ($gitStatus) {
    Write-Warn "發現未提交的更改："
    Write-Host $gitStatus
    $continue = Read-Host "是否繼續部署？(y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Error "部署已取消"
        exit 1
    }
}

# 檢查是否有未推送的提交
$unpushed = git log origin/master..HEAD --oneline
if ($unpushed) {
    Write-Warn "發現未推送的提交："
    Write-Host $unpushed
    Write-Info "正在推送到 GitHub..."
    git push origin master
    if ($LASTEXITCODE -ne 0) {
        Write-Error "推送失敗，請檢查網絡連接和權限"
        exit 1
    }
    Write-Info "代碼已推送到 GitHub"
} else {
    Write-Info "所有提交已推送到 GitHub"
}

# 步驟 2: 測試 SSH 連接
Write-Step "步驟 2: 測試服務器連接" "Yellow"
$sshReady = Test-SSHConnection -Server $Server

# 步驟 3: 部署到服務器
Write-Step "步驟 3: 部署到服務器" "Yellow"
Write-Info "服務器: $Server"
Write-Info "路徑: $RemotePath"

# 構建部署腳本
$deployScript = @"
set -e
cd $RemotePath

echo '========================================'
echo '  開始部署...'
echo '========================================'
echo ''

echo '[1/5] 拉取最新代碼...'
git fetch origin
git reset --hard origin/master
echo '✓ 代碼已更新'
echo ''

echo '[2/5] 構建前端...'
cd frontend
npm install --silent 2>&1 | tail -5
npm run build 2>&1 | tail -10
echo '✓ 前端構建完成'
echo ''

echo '[3/5] 重啟服務...'
sudo systemctl restart luckyred-api luckyred-bot luckyred-admin
echo '✓ 服務已重啟'
echo ''

echo '[4/5] 檢查服務狀態...'
echo ''
echo '--- API 狀態 ---'
sudo systemctl is-active luckyred-api && echo '✓ API 運行中' || echo '✗ API 未運行'
echo ''
echo '--- Bot 狀態 ---'
sudo systemctl is-active luckyred-bot && echo '✓ Bot 運行中' || echo '✗ Bot 未運行'
echo ''
echo '--- Admin 狀態 ---'
sudo systemctl is-active luckyred-admin && echo '✓ Admin 運行中' || echo '✗ Admin 未運行'
echo ''

echo '[5/5] 獲取詳細狀態...'
sudo systemctl status luckyred-api --no-pager | head -8
echo ''
sudo systemctl status luckyred-bot --no-pager | head -8
echo ''

echo '========================================'
echo '  部署完成！'
echo '========================================'
"@

# 執行部署
try {
    Write-Info "正在執行部署腳本..."
    Write-Host ""
    
    # 將腳本寫入臨時文件
    $tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
    $deployScript | Out-File -FilePath $tempScript -Encoding UTF8 -NoNewline
    
    # 使用 SSH 執行腳本
    if ($sshReady) {
        # 如果 SSH 已配置密鑰，直接執行
        $command = "bash -s < `"$tempScript`""
        ssh $Server $command
    } else {
        # 需要密碼認證，使用 plink 或直接 ssh
        Write-Info "請輸入 SSH 密碼（如果需要）..."
        $command = Get-Content $tempScript -Raw
        ssh $Server "bash -s" < $tempScript
    }
    
    # 清理臨時文件
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force
    }
    
    Write-Step "部署完成！" "Green"
    Write-Host ""
    Write-Info "MiniApp: https://mini.usdt2026.cc"
    Write-Info "Admin: https://admin.usdt2026.cc"
    Write-Host ""
    Write-Info "請訪問網站確認部署是否成功"
    Write-Info "特別檢查遊戲規則彈窗功能"
    
} catch {
    Write-Error "部署過程中發生錯誤: $_"
    Write-Host ""
    Write-Warn "如果遇到 SSH 認證問題，請："
    Write-Warn "1. 確保已配置 SSH 密鑰"
    Write-Warn "2. 或手動執行: ssh $Server"
    Write-Warn "3. 然後在服務器上執行: cd $RemotePath && bash deploy/scripts/quick-update.sh"
    exit 1
}
