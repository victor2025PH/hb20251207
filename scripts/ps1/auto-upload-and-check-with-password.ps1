# PowerShell 腳本 - 支持密碼輸入的自動檢查

param(
    [string]$Server = "165.154.254.99",
    [string]$Username = "ubuntu",
    [string]$RemotePath = "/opt/luckyred",
    [int]$TimeoutSeconds = 10
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LuckyRed 自動上傳並檢查部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 SSH 密鑰是否已配置
Write-Host "正在檢查 SSH 連接..." -ForegroundColor Yellow
$testConnection = ssh -o BatchMode=yes -o ConnectTimeout=5 "${Username}@${Server}" "echo 'OK'" 2>$null
$needsPassword = $LASTEXITCODE -ne 0

if (-not $needsPassword) {
    Write-Host "[OK] SSH 密鑰已配置，無需輸入密碼" -ForegroundColor Green
    $password = $null
} else {
    Write-Host "[提示] 需要輸入 SSH 密碼" -ForegroundColor Yellow
    Write-Host ""
    $securePassword = Read-Host "請輸入 SSH 密碼" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    Write-Host ""
}

# 檢查是否安裝了 sshpass（Linux 工具，Windows 上需要 WSL 或 Git Bash）
$hasSshpass = $false
if (Get-Command sshpass -ErrorAction SilentlyContinue) {
    $hasSshpass = $true
    Write-Host "[OK] 檢測到 sshpass 工具" -ForegroundColor Green
}

# 執行 SSH 命令的函數
function Invoke-SSHCommand {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host $Description -ForegroundColor Yellow
    
    if ($needsPassword) {
        if ($hasSshpass) {
            # 使用 sshpass
            $env:SSHPASS = $password
            sshpass -e ssh -o StrictHostKeyChecking=no "${Username}@${Server}" $Command
        } else {
            # 使用 expect-like 方式（需要額外工具）
            Write-Host "[警告] 未安裝 sshpass，嘗試使用 plink..." -ForegroundColor Yellow
            if (Get-Command plink -ErrorAction SilentlyContinue) {
                echo $password | plink -ssh -pw $password "${Username}@${Server}" $Command
            } else {
                Write-Host "[錯誤] 需要安裝 sshpass 或 plink 來自動輸入密碼" -ForegroundColor Red
                Write-Host "或者配置 SSH 密鑰以避免輸入密碼" -ForegroundColor Yellow
                return $false
            }
        }
    } else {
        ssh -o ConnectTimeout=$TimeoutSeconds "${Username}@${Server}" $Command
    }
    
    return $LASTEXITCODE -eq 0
}

# 執行 SCP 命令的函數
function Invoke-SCPCommand {
    param(
        [string]$LocalFile,
        [string]$RemoteFile,
        [string]$Description
    )
    
    Write-Host $Description -ForegroundColor Yellow
    
    if ($needsPassword) {
        if ($hasSshpass) {
            $env:SSHPASS = $password
            sshpass -e scp -o StrictHostKeyChecking=no $LocalFile "${Username}@${Server}:${RemoteFile}"
        } else {
            if (Get-Command pscp -ErrorAction SilentlyContinue) {
                echo $password | pscp -pw $password $LocalFile "${Username}@${Server}:${RemoteFile}"
            } else {
                Write-Host "[錯誤] 需要安裝 sshpass 或 pscp 來自動上傳文件" -ForegroundColor Red
                return $false
            }
        }
    } else {
        scp -o ConnectTimeout=$TimeoutSeconds $LocalFile "${Username}@${Server}:${RemoteFile}"
    }
    
    return $LASTEXITCODE -eq 0
}

try {
    # 步驟 1: 上傳檢查腳本
    Write-Host ""
    Write-Host "[步驟 1/3] 上傳檢查腳本到服務器" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $localScript = "check_deployment.sh"
    if (-not (Test-Path $localScript)) {
        Write-Host "[警告] 找不到 $localScript，跳過上傳" -ForegroundColor Yellow
    } else {
        $uploaded = Invoke-SCPCommand -LocalFile $localScript -RemoteFile "${RemotePath}/check_deployment.sh" -Description "正在上傳 check_deployment.sh..."
        if ($uploaded) {
            Write-Host "[OK] 檢查腳本上傳成功" -ForegroundColor Green
            Invoke-SSHCommand -Command "chmod +x ${RemotePath}/check_deployment.sh" -Description "設置執行權限..."
        } else {
            Write-Host "[警告] 上傳失敗，將使用遠程命令檢查" -ForegroundColor Yellow
        }
    }
    
    # 步驟 2: 執行部署檢查
    Write-Host ""
    Write-Host "[步驟 2/3] 執行部署檢查" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $checkCommand = "if [ -f ${RemotePath}/check_deployment.sh ]; then bash ${RemotePath}/check_deployment.sh; else echo '檢查腳本不存在，執行基本檢查...'; bash -c 'echo \"=== 服務狀態 ===\" && sudo systemctl status luckyred-api --no-pager -l | head -15 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -15 && echo && echo \"=== 錯誤日誌 ===\" && sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15 && echo && sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -15'; fi"
    Invoke-SSHCommand -Command $checkCommand -Description "執行檢查..."
    
    # 步驟 3: 生成診斷報告
    Write-Host ""
    Write-Host "[步驟 3/3] 生成診斷報告" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $diagnoseCommand = "echo '=== 文件檢查 ===' && test -f ${RemotePath}/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在' && test -d ${RemotePath}/api/.venv && echo '[OK] API虛擬環境存在' || echo '[ERROR] API虛擬環境不存在' && test -d ${RemotePath}/bot/.venv && echo '[OK] Bot虛擬環境存在' || echo '[ERROR] Bot虛擬環境不存在' && echo && echo '=== 服務狀態摘要 ===' && (sudo systemctl is-active luckyred-api 2>/dev/null && echo 'API服務: [運行中]' || echo 'API服務: [未運行]') && (sudo systemctl is-active luckyred-bot 2>/dev/null && echo 'Bot服務: [運行中]' || echo 'Bot服務: [未運行]') && (sudo systemctl is-active nginx 2>/dev/null && echo 'Nginx服務: [運行中]' || echo 'Nginx服務: [未運行]')"
    Invoke-SSHCommand -Command $diagnoseCommand -Description "生成診斷報告..."
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  檢查完成" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ 執行錯誤" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "錯誤信息: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "建議:" -ForegroundColor Yellow
    Write-Host "  1. 檢查網絡連接" -ForegroundColor Yellow
    Write-Host "  2. 確認服務器地址正確: $Server" -ForegroundColor Yellow
    Write-Host "  3. 如果使用密碼，確保已安裝 sshpass 或 plink" -ForegroundColor Yellow
    Write-Host "  4. 或配置 SSH 密鑰以避免輸入密碼" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

