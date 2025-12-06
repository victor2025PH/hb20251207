# ============================================
# Stop All Bot Instances
# ============================================

Write-Host ""
Write-Host "Stopping all Bot instances..." -ForegroundColor Yellow
Write-Host ""

# Find all Python processes that might be running the bot
$botProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*bot*" -or 
    $_.Path -like "*hbgm001*" -or
    (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | 
     Select-Object -ExpandProperty CommandLine) -like "*bot*main.py*"
}

if ($botProcesses) {
    Write-Host "Found $($botProcesses.Count) Bot process(es):" -ForegroundColor Cyan
    foreach ($proc in $botProcesses) {
        Write-Host "  PID: $($proc.Id) - $($proc.ProcessName)" -ForegroundColor White
        try {
            Stop-Process -Id $proc.Id -Force
            Write-Host "    ✓ Stopped" -ForegroundColor Green
        } catch {
            Write-Host "    ✗ Failed to stop: $_" -ForegroundColor Red
        }
    }
    Write-Host ""
    Write-Host "All Bot instances stopped" -ForegroundColor Green
} else {
    Write-Host "No Bot processes found" -ForegroundColor Green
}

# Wait a moment for processes to fully terminate
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "You can now start the Bot again" -ForegroundColor Cyan
Write-Host ""
