# ============================================
# 启动本地机器人测试
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动本地机器人" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "c:\hbgm001"

# 检查 .env 文件
Write-Host "[1/4] 检查环境配置..." -ForegroundColor Yellow
if (-not (Test-Path "$projectRoot\.env")) {
    Write-Host "  ✗ .env 文件不存在" -ForegroundColor Red
    Write-Host "  请先创建 .env 文件并填入 BOT_TOKEN" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  ✓ .env 文件存在" -ForegroundColor Green
}

# 检查 Bot 虚拟环境
Write-Host ""
Write-Host "[2/4] 检查 Bot 虚拟环境..." -ForegroundColor Yellow
if (-not (Test-Path "$projectRoot\bot\.venv")) {
    Write-Host "  创建 Bot 虚拟环境..." -ForegroundColor Yellow
    Set-Location "$projectRoot\bot"
    python -m venv .venv
    Write-Host "  ✓ 虚拟环境已创建" -ForegroundColor Green
} else {
    Write-Host "  ✓ Bot 虚拟环境存在" -ForegroundColor Green
}

# 安装依赖
Write-Host ""
Write-Host "[3/4] 检查 Bot 依赖..." -ForegroundColor Yellow
Set-Location "$projectRoot\bot"
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ 无法激活虚拟环境" -ForegroundColor Red
    exit 1
}

# 检查是否需要安装依赖
$requirementsFile = "$projectRoot\bot\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "  检查依赖..." -ForegroundColor Yellow
    pip install -q -r requirements.txt 2>&1 | Out-Null
    Write-Host "  ✓ 依赖已安装" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  requirements.txt 不存在" -ForegroundColor Yellow
}

# 启动 Bot
Write-Host ""
Write-Host "[4/4] 启动 Bot..." -ForegroundColor Yellow
Write-Host "  所有日志将显示在当前窗口" -ForegroundColor Cyan
Write-Host "  按 Ctrl+C 停止 Bot`n" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Bot 启动中..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 运行 Bot
python main.py

# Bot 停止后
Write-Host ""
Write-Host "Bot 已停止" -ForegroundColor Yellow
deactivate
