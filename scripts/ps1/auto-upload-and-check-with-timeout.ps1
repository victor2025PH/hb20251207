# PowerShell 腳本 - 帶超時檢測的自動上傳和檢查

param(
    [int]$TimeoutSeconds = 10
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LuckyRed 自動上傳並檢查部署" -ForegroundColor Cyan
Write-Host "  超時設置: $TimeoutSeconds 秒" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SERVER = "ubuntu@165.154.254.99"
$REMOTE_PATH = "/opt/luckyred"
$scriptPath = Join-Path $PSScriptRoot "auto-upload-and-check.bat"

# 檢查批處理文件是否存在
if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ 錯誤: 找不到 auto-upload-and-check.bat" -ForegroundColor Red
    Write-Host "路徑: $scriptPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "正在執行檢查腳本..." -ForegroundColor Green
Write-Host "如果 $TimeoutSeconds 秒內沒有響應，將自動停止" -ForegroundColor Yellow
Write-Host ""

try {
    # 創建進程啟動信息
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "cmd.exe"
    $psi.Arguments = "/c `"$scriptPath`""
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    
    # 啟動進程
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    
    # 創建輸出緩衝區
    $outputBuilder = New-Object System.Text.StringBuilder
    $errorBuilder = New-Object System.Text.StringBuilder
    
    $outputEvent = Register-ObjectEvent -InputObject $process -EventName "OutputDataReceived" -Action {
        if ($EventArgs.Data) {
            [void]$Event.MessageData.AppendLine($EventArgs.Data)
            Write-Host $EventArgs.Data
        }
    } -MessageData $outputBuilder
    
    $errorEvent = Register-ObjectEvent -InputObject $process -EventName "ErrorDataReceived" -Action {
        if ($EventArgs.Data) {
            [void]$Event.MessageData.AppendLine($EventArgs.Data)
            Write-Host $EventArgs.Data -ForegroundColor Red
        }
    } -MessageData $errorBuilder
    
    $process.Start() | Out-Null
    $process.BeginOutputReadLine()
    $process.BeginErrorReadLine()
    
    $startTime = Get-Date
    $hasOutput = $false
    
    # 監控進程，檢查超時和輸出
    while (-not $process.HasExited) {
        Start-Sleep -Milliseconds 500
        
        $elapsed = (Get-Date) - $startTime
        
        # 檢查是否有輸出
        if ($outputBuilder.Length -gt 0 -or $errorBuilder.Length -gt 0) {
            $hasOutput = $true
            $startTime = Get-Date  # 重置計時器
        }
        
        # 檢查超時
        if ($elapsed.TotalSeconds -gt $TimeoutSeconds -and -not $hasOutput) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Red
            Write-Host "  ⚠️  超時錯誤 ($TimeoutSeconds 秒)" -ForegroundColor Red
            Write-Host "========================================" -ForegroundColor Red
            Write-Host ""
            Write-Host "可能的原因：" -ForegroundColor Yellow
            Write-Host "  1. SSH 連接失敗 - 檢查網絡連接和服務器地址" -ForegroundColor Yellow
            Write-Host "  2. 需要輸入密碼 - SSH 密鑰未配置" -ForegroundColor Yellow
            Write-Host "  3. 服務器無響應 - 服務器可能離線或防火牆阻擋" -ForegroundColor Yellow
            Write-Host "  4. DNS 解析問題 - 雖然已使用 IP，但可能仍有網絡問題" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "建議操作：" -ForegroundColor Cyan
            Write-Host "  1. 手動測試連接: ssh $SERVER" -ForegroundColor Cyan
            Write-Host "  2. 檢查 SSH 密鑰配置" -ForegroundColor Cyan
            Write-Host "  3. 確認服務器 IP 地址正確: 165.154.254.99" -ForegroundColor Cyan
            Write-Host "  4. 檢查防火牆設置" -ForegroundColor Cyan
            Write-Host ""
            
            # 終止進程
            try {
                $process.Kill()
                Write-Host "已終止進程" -ForegroundColor Yellow
            } catch {
                Write-Host "無法終止進程: $_" -ForegroundColor Red
            }
            
            exit 1
        }
    }
    
    # 等待進程完全結束
    $process.WaitForExit()
    
    # 獲取剩餘輸出
    Start-Sleep -Milliseconds 500
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  執行完成" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "退出代碼: $($process.ExitCode)" -ForegroundColor $(if ($process.ExitCode -eq 0) { "Green" } else { "Red" })
    
    if ($process.ExitCode -ne 0) {
        Write-Host ""
        Write-Host "執行過程中出現錯誤，退出代碼: $($process.ExitCode)" -ForegroundColor Red
        exit $process.ExitCode
    }
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ 執行錯誤" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "錯誤信息: $_" -ForegroundColor Red
    Write-Host "錯誤位置: $($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor Yellow
    Write-Host ""
    exit 1
} finally {
    # 清理事件
    if ($outputEvent) { Unregister-Event -SourceIdentifier $outputEvent.Name }
    if ($errorEvent) { Unregister-Event -SourceIdentifier $errorEvent.Name }
    if ($process -and -not $process.HasExited) {
        try { $process.Kill() } catch {}
    }
}

