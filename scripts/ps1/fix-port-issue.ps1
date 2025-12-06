# ============================================
# Fix Port 8080 Issue
# ============================================

Write-Host ""
Write-Host "Checking port 8080..." -ForegroundColor Cyan
Write-Host ""

# Check if port 8080 is in use
$portInUse = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

if ($portInUse) {
    Write-Host "Port 8080 is already in use!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Process using port 8080:" -ForegroundColor Yellow
    $portInUse | ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        Write-Host "  PID: $($_.OwningProcess) - $($process.ProcessName)" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  1. Kill the process using port 8080" -ForegroundColor Yellow
    Write-Host "  2. Use a different port (e.g., 8081)" -ForegroundColor Yellow
    Write-Host ""
    
    $choice = Read-Host "Choose option (1 or 2)"
    
    if ($choice -eq "1") {
        $portInUse | ForEach-Object {
            $pid = $_.OwningProcess
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "Killing process $pid ($($process.ProcessName))..." -ForegroundColor Yellow
                Stop-Process -Id $pid -Force
                Write-Host "Process killed" -ForegroundColor Green
            }
        }
        Write-Host ""
        Write-Host "Port 8080 is now free. You can start the API server again." -ForegroundColor Green
    } elseif ($choice -eq "2") {
        $newPort = Read-Host "Enter new port number (default: 8081)"
        if ([string]::IsNullOrWhiteSpace($newPort)) {
            $newPort = "8081"
        }
        Write-Host ""
        Write-Host "To use port $newPort, update your command:" -ForegroundColor Cyan
        Write-Host "  uvicorn main:app --host 0.0.0.0 --port $newPort --reload" -ForegroundColor White
        Write-Host ""
        Write-Host "Or update API_PORT in .env file to $newPort" -ForegroundColor Yellow
    }
} else {
    Write-Host "Port 8080 is free" -ForegroundColor Green
    Write-Host ""
    Write-Host "The error might be due to:" -ForegroundColor Yellow
    Write-Host "  1. Firewall blocking the port" -ForegroundColor White
    Write-Host "  2. Administrator privileges required" -ForegroundColor White
    Write-Host ""
    Write-Host "Try running PowerShell as Administrator" -ForegroundColor Cyan
}

Write-Host ""
