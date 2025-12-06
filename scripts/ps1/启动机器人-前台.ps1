# ============================================
# 在前台启动机器人（可以看到日志）
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动本地机器人（前台模式）" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "c:\hbgm001"
$botDir = "$projectRoot\bot"

# 检查 .env 文件
Write-Host "[1/4] 检查环境配置..." -ForegroundColor Yellow
if (-not (Test-Path "$projectRoot\.env")) {
    Write-Host "  ✗ .env 文件不存在" -ForegroundColor Red
    Write-Host "  请先创建 .env 文件并填入 BOT_TOKEN" -ForegroundColor Yellow
    Write-Host "  可以从 .env.example 复制" -ForegroundColor Yellow
    pause
    exit 1
} else {
    Write-Host "  ✓ .env 文件存在" -ForegroundColor Green
}

# 检查并创建虚拟环境
Write-Host ""
Write-Host "[2/4] 检查 Bot 虚拟环境..." -ForegroundColor Yellow
Set-Location $botDir

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "  创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ 创建虚拟环境失败" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "  ✓ 虚拟环境已创建" -ForegroundColor Green
} else {
    Write-Host "  ✓ Bot 虚拟环境存在" -ForegroundColor Green
}

# 激活虚拟环境并安装依赖
Write-Host ""
Write-Host "[3/4] 安装依赖..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ 无法激活虚拟环境" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "  升级 pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip -q

Write-Host "  安装依赖包..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ⚠️  依赖安装可能有警告，继续..." -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ 依赖已安装" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠️  requirements.txt 不存在" -ForegroundColor Yellow
}

# 启动 Bot
Write-Host ""
Write-Host "[4/4] 启动 Bot..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Bot 启动中..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "所有日志将显示在下方" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止 Bot" -ForegroundColor Yellow
Write-Host ""

# 运行 Bot
python main.py

# Bot 停止后
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  Bot 已停止" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
deactivate
Write-Host "按任意键关闭..." -ForegroundColor Cyan
pause
