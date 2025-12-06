# ============================================
# Lucky Red 部署啟動腳本 (Windows)
# ============================================

Write-Host "🚀 Lucky Red 部署準備檢查" -ForegroundColor Green
Write-Host ""

# 檢查 .env 文件
if (Test-Path .env) {
    Write-Host "✓ .env 文件存在" -ForegroundColor Green
} else {
    Write-Host "✗ .env 文件不存在" -ForegroundColor Red
    Write-Host "正在從 .env.example 創建 .env 文件..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ 已創建 .env 文件，請編輯並填寫配置" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "重要：請編輯 .env 文件並配置以下變量：" -ForegroundColor Yellow
    Write-Host "  - BOT_TOKEN" -ForegroundColor Cyan
    Write-Host "  - BOT_USERNAME" -ForegroundColor Cyan
    Write-Host "  - ADMIN_IDS" -ForegroundColor Cyan
    Write-Host "  - DATABASE_URL" -ForegroundColor Cyan
    Write-Host "  - JWT_SECRET" -ForegroundColor Cyan
    Write-Host "  - API_BASE_URL" -ForegroundColor Cyan
    Write-Host ""
    $open = Read-Host "是否現在打開 .env 文件進行編輯？(Y/N)"
    if ($open -eq "Y" -or $open -eq "y") {
        notepad .env
    }
    Write-Host ""
    Write-Host "配置完成後，請重新運行此腳本" -ForegroundColor Yellow
    exit
}

# 檢查必要的目錄
Write-Host "檢查項目結構..." -ForegroundColor Cyan
$requiredDirs = @("api", "bot", "frontend", "shared", "deploy")
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir 不存在" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "選擇部署方式：" -ForegroundColor Cyan
Write-Host "1. 本地開發測試（Windows）" -ForegroundColor Yellow
Write-Host "2. 準備部署到 Linux 服務器" -ForegroundColor Yellow
Write-Host "3. 檢查部署配置" -ForegroundColor Yellow
Write-Host "4. 查看部署文檔" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "請選擇 (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "啟動本地開發環境..." -ForegroundColor Green
        Write-Host ""
        Write-Host "注意：本地開發需要：" -ForegroundColor Yellow
        Write-Host "  - Python 3.10+ 已安裝" -ForegroundColor Cyan
        Write-Host "  - PostgreSQL 已安裝並運行" -ForegroundColor Cyan
        Write-Host "  - Node.js 18+ 已安裝（前端）" -ForegroundColor Cyan
        Write-Host ""
        
        # 檢查 Python
        try {
            $pythonVersion = python --version 2>&1
            Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
        } catch {
            Write-Host "✗ Python 未安裝或不在 PATH 中" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "啟動選項：" -ForegroundColor Cyan
        Write-Host "  A. 啟動 API 服務器" -ForegroundColor Yellow
        Write-Host "  B. 啟動 Bot" -ForegroundColor Yellow
        Write-Host "  C. 啟動前端開發服務器" -ForegroundColor Yellow
        Write-Host "  D. 啟動所有服務（需要多個終端）" -ForegroundColor Yellow
        Write-Host ""
        
        $startChoice = Read-Host "請選擇 (A-D)"
        
        switch ($startChoice.ToUpper()) {
            "A" {
                Write-Host "啟動 API 服務器..." -ForegroundColor Green
                Set-Location api
                if (Test-Path .venv) {
                    .\.venv\Scripts\Activate.ps1
                } else {
                    Write-Host "創建虛擬環境..." -ForegroundColor Yellow
                    python -m venv .venv
                    .\.venv\Scripts\Activate.ps1
                    pip install -r requirements.txt
                }
                Write-Host "啟動 API 服務器在 http://localhost:8080" -ForegroundColor Green
                uvicorn main:app --host 0.0.0.0 --port 8080 --reload
            }
            "B" {
                Write-Host "啟動 Bot..." -ForegroundColor Green
                Set-Location bot
                if (Test-Path .venv) {
                    .\.venv\Scripts\Activate.ps1
                } else {
                    Write-Host "創建虛擬環境..." -ForegroundColor Yellow
                    python -m venv .venv
                    .\.venv\Scripts\Activate.ps1
                    pip install -r requirements.txt
                }
                Write-Host "啟動 Telegram Bot..." -ForegroundColor Green
                python main.py
            }
            "C" {
                Write-Host "啟動前端開發服務器..." -ForegroundColor Green
                Set-Location frontend
                if (-not (Test-Path node_modules)) {
                    Write-Host "安裝依賴..." -ForegroundColor Yellow
                    npm install
                }
                Write-Host "啟動開發服務器在 http://localhost:3000" -ForegroundColor Green
                npm run dev
            }
            "D" {
                Write-Host "請在三個不同的終端窗口中分別運行：" -ForegroundColor Yellow
                Write-Host "  1. API: cd api && .venv\Scripts\Activate.ps1 && uvicorn main:app --reload" -ForegroundColor Cyan
                Write-Host "  2. Bot: cd bot && .venv\Scripts\Activate.ps1 && python main.py" -ForegroundColor Cyan
                Write-Host "  3. Frontend: cd frontend && npm run dev" -ForegroundColor Cyan
            }
        }
    }
    "2" {
        Write-Host ""
        Write-Host "準備部署到 Linux 服務器..." -ForegroundColor Green
        Write-Host ""
        Write-Host "部署步驟：" -ForegroundColor Cyan
        Write-Host "1. 將代碼上傳到服務器 /opt/luckyred" -ForegroundColor Yellow
        Write-Host "2. SSH 登錄服務器" -ForegroundColor Yellow
        Write-Host "3. 配置 .env 文件" -ForegroundColor Yellow
        Write-Host "4. 運行部署腳本: sudo bash deploy/scripts/deploy-full.sh" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "詳細說明請參考：" -ForegroundColor Cyan
        Write-Host "  - QUICK_START_DEPLOY.md" -ForegroundColor Green
        Write-Host "  - DEPLOYMENT_GUIDE.md" -ForegroundColor Green
        Write-Host ""
        
        # 檢查是否有部署腳本
        if (Test-Path deploy\scripts\deploy-full.sh) {
            Write-Host "✓ 部署腳本已準備好" -ForegroundColor Green
        } else {
            Write-Host "✗ 部署腳本不存在" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "準備上傳到服務器？" -ForegroundColor Yellow
        Write-Host "可以使用以下命令（需要配置 SSH）：" -ForegroundColor Cyan
        Write-Host "  scp -r . user@server:/opt/luckyred/" -ForegroundColor White
        Write-Host "  或使用 rsync:" -ForegroundColor Cyan
        Write-Host "  rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' . user@server:/opt/luckyred/" -ForegroundColor White
    }
    "3" {
        Write-Host ""
        Write-Host "檢查部署配置..." -ForegroundColor Green
        Write-Host ""
        
        # 檢查部署文件
        $deployFiles = @(
            "deploy\scripts\deploy-full.sh",
            "deploy\scripts\quick-update.sh",
            "deploy\systemd\luckyred-api.service",
            "deploy\systemd\luckyred-bot.service",
            "deploy\nginx\mini.usdt2026.cc.conf",
            "DEPLOYMENT_GUIDE.md",
            "QUICK_START_DEPLOY.md"
        )
        
        foreach ($file in $deployFiles) {
            if (Test-Path $file) {
                Write-Host "  ✓ $file" -ForegroundColor Green
            } else {
                Write-Host "  ✗ $file 不存在" -ForegroundColor Red
            }
        }
        
        Write-Host ""
        Write-Host "檢查 .env 配置..." -ForegroundColor Cyan
        if (Test-Path .env) {
            $envContent = Get-Content .env
            $requiredVars = @("BOT_TOKEN", "DATABASE_URL", "JWT_SECRET", "API_BASE_URL")
            foreach ($var in $requiredVars) {
                $found = $envContent | Select-String "^$var="
                if ($found -and $found -notmatch "your_|change-this") {
                    Write-Host "  ✓ $var 已配置" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠ $var 需要配置" -ForegroundColor Yellow
                }
            }
        }
    }
    "4" {
        Write-Host ""
        Write-Host "部署文檔：" -ForegroundColor Green
        Write-Host ""
        Write-Host "1. QUICK_START_DEPLOY.md - 快速開始指南" -ForegroundColor Cyan
        Write-Host "2. DEPLOYMENT_GUIDE.md - 完整部署指南" -ForegroundColor Cyan
        Write-Host "3. deploy/checklist.md - 部署檢查清單" -ForegroundColor Cyan
        Write-Host "4. deploy/README.md - 部署文件說明" -ForegroundColor Cyan
        Write-Host ""
        
        $docChoice = Read-Host "打開哪個文檔？(1-4)"
        $docs = @(
            "QUICK_START_DEPLOY.md",
            "DEPLOYMENT_GUIDE.md",
            "deploy\checklist.md",
            "deploy\README.md"
        )
        
        if ($docChoice -ge 1 -and $docChoice -le 4) {
            $doc = $docs[$docChoice - 1]
            if (Test-Path $doc) {
                notepad $doc
            } else {
                Write-Host "文件不存在: $doc" -ForegroundColor Red
            }
        }
    }
    default {
        Write-Host "無效選擇" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "完成！" -ForegroundColor Green
