# 查看服务日志的 PowerShell 脚本
# 在服务器上通过 SSH 执行

param(
    [Parameter(Position=0)]
    [ValidateSet("api", "bot", "all")]
    [string]$Service = "all",
    
    [Parameter(Position=1)]
    [int]$Lines = 100,
    
    [Parameter(Position=2)]
    [string]$Filter = ""
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  日志查看工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 服务名称映射
$serviceMap = @{
    "api" = "hbgm001-backend"
    "bot" = "hbgm001-bot"
}

Write-Host "查看最近 $Lines 行日志" -ForegroundColor Green
if ($Filter) {
    Write-Host "过滤关键词: $Filter" -ForegroundColor Yellow
}
Write-Host ""

if ($Service -eq "all") {
    if ($Filter) {
        ssh ubuntu@your-server-ip "journalctl -u hbgm001-backend -u hbgm001-bot -n $Lines --no-pager | grep -i '$Filter'"
    } else {
        ssh ubuntu@your-server-ip "journalctl -u hbgm001-backend -u hbgm001-bot -n $Lines --no-pager"
    }
} else {
    $serviceName = $serviceMap[$Service]
    if ($Filter) {
        ssh ubuntu@your-server-ip "journalctl -u $serviceName -n $Lines --no-pager | grep -i '$Filter'"
    } else {
        ssh ubuntu@your-server-ip "journalctl -u $serviceName -n $Lines --no-pager"
    }
}

