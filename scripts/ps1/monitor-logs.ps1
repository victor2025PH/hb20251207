# 监控服务日志的 PowerShell 脚本
# 在服务器上通过 SSH 执行

param(
    [Parameter(Position=0)]
    [ValidateSet("api", "bot", "all")]
    [string]$Service = "all",
    
    [Parameter(Position=1)]
    [string]$Filter = ""
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  日志监控工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 服务名称映射
$serviceMap = @{
    "api" = "hbgm001-backend"
    "bot" = "hbgm001-bot"
}

if ($Service -eq "all") {
    Write-Host "监控所有服务日志..." -ForegroundColor Green
    Write-Host "按 Ctrl+C 停止监控" -ForegroundColor Yellow
    Write-Host ""
    
    if ($Filter) {
        ssh ubuntu@your-server-ip "journalctl -u hbgm001-backend -u hbgm001-bot -f --no-pager | grep -i '$Filter'"
    } else {
        ssh ubuntu@your-server-ip "journalctl -u hbgm001-backend -u hbgm001-bot -f --no-pager"
    }
} else {
    $serviceName = $serviceMap[$Service]
    Write-Host "监控 $serviceName 服务日志..." -ForegroundColor Green
    Write-Host "按 Ctrl+C 停止监控" -ForegroundColor Yellow
    Write-Host ""
    
    if ($Filter) {
        ssh ubuntu@your-server-ip "journalctl -u $serviceName -f --no-pager | grep -i '$Filter'"
    } else {
        ssh ubuntu@your-server-ip "journalctl -u $serviceName -f --no-pager"
    }
}
