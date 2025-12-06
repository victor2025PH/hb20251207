# 📤 上传代码到 GitHub
# 使用方法: .\scripts\ps1\上传到GitHub.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  📤 上传代码到 GitHub" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 进入项目根目录
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

try {
    Write-Host "[1/4] 检查 Git 状态..." -ForegroundColor Yellow
    git status
    
    Write-Host ""
    Write-Host "[2/4] 添加所有更改..." -ForegroundColor Yellow
    git add -A
    
    Write-Host ""
    Write-Host "[3/4] 提交更改..." -ForegroundColor Yellow
    $CommitMsg = Read-Host "请输入提交信息 (直接回车使用默认)"
    if ([string]::IsNullOrWhiteSpace($CommitMsg)) {
        $CommitMsg = "更新代码: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }
    git commit -m $CommitMsg
    
    Write-Host ""
    Write-Host "[4/4] 推送到 GitHub..." -ForegroundColor Yellow
    git push origin master
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  ✅ 上传成功！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 下一步：在服务器上执行拉取命令" -ForegroundColor Cyan
    Write-Host "   bash scripts/sh/从GitHub拉取并部署.sh" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "  ❌ 上传失败！" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "错误信息: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查：" -ForegroundColor Yellow
    Write-Host "  1. Git 远程仓库配置是否正确" -ForegroundColor Yellow
    Write-Host "  2. 是否有推送权限" -ForegroundColor Yellow
    Write-Host "  3. 网络连接是否正常" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

