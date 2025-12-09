# 查找红包相关日志的 PowerShell 脚本
# 在服务器上通过 SSH 执行

param(
    [Parameter(Position=0)]
    [string]$Since = "1 hour ago"
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  红包日志查找工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "查找时间范围: $Since 到现在" -ForegroundColor Green
Write-Host "查找关键词: 红包、發送、群組、send、redpacket" -ForegroundColor Yellow
Write-Host ""

# 查找红包相关日志
ssh ubuntu@your-server-ip "journalctl -u hbgm001-backend -u hbgm001-bot --since '$Since' --no-pager | grep -iE '(红包|發送|群組|send|redpacket|claim|領取|chat_id|bot|機器人|✅|❌|⚠️)' | tail -100"

Write-Host ""
Write-Host "查找完成！" -ForegroundColor Green

