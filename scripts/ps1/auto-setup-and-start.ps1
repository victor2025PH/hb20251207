# ============================================
# Lucky Red - 全自動設置和啟動腳本
# ============================================

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Lucky Red - Full Auto Setup & Start" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Get-Location
}

# Step 1: Check Python
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -like "*Python 3*") {
    Write-Host "  OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Python 3.10+ is required" -ForegroundColor Red
    Write-Host "  Please install Python from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check .env file
Write-Host "[2/6] Checking environment configuration..." -ForegroundColor Yellow
$envFile = Join-Path $projectRoot ".env"
$envExample = Join-Path $projectRoot ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  Created .env from .env.example" -ForegroundColor Yellow
        Write-Host "  Please edit .env to configure BOT_TOKEN and other settings!" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Opening .env file for editing..." -ForegroundColor Cyan
        notepad $envFile
        Write-Host "  Press Enter after saving .env file..." -ForegroundColor Yellow
        Read-Host
    } else {
        Write-Host "  ERROR: .env.example not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  OK: .env file exists" -ForegroundColor Green
}

# Step 3: Setup API virtual environment
Write-Host "[3/6] Setting up API environment..." -ForegroundColor Yellow
$apiDir = Join-Path $projectRoot "api"
$apiVenv = Join-Path $apiDir ".venv"

Push-Location $apiDir
try {
    if (-not (Test-Path $apiVenv)) {
        Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
        python -m venv .venv
    }
    
    Write-Host "  Installing dependencies..." -ForegroundColor Cyan
    & "$apiVenv\Scripts\pip.exe" install --upgrade pip -q
    & "$apiVenv\Scripts\pip.exe" install -r requirements.txt -q
    Write-Host "  OK: API environment ready" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Failed to setup API environment: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# Step 4: Setup Bot virtual environment
Write-Host "[4/6] Setting up Bot environment..." -ForegroundColor Yellow
$botDir = Join-Path $projectRoot "bot"
$botVenv = Join-Path $botDir ".venv"

Push-Location $botDir
try {
    if (-not (Test-Path $botVenv)) {
        Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
        python -m venv .venv
    }
    
    Write-Host "  Installing dependencies..." -ForegroundColor Cyan
    & "$botVenv\Scripts\pip.exe" install --upgrade pip -q
    & "$botVenv\Scripts\pip.exe" install -r requirements.txt -q
    Write-Host "  OK: Bot environment ready" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Failed to setup Bot environment: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# Step 5: Initialize database
Write-Host "[5/6] Initializing database..." -ForegroundColor Yellow
Push-Location $apiDir
try {
    $initScript = @"
import sys
sys.path.insert(0, '..')
from shared.database.connection import init_db
try:
    init_db()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database may already exist: {e}')
"@
    $initScript | & "$apiVenv\Scripts\python.exe" -
    Write-Host "  OK: Database ready" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Database initialization issue (may already exist)" -ForegroundColor Yellow
} finally {
    Pop-Location
}

# Step 6: Stop existing processes
Write-Host "[6/6] Stopping any existing services..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = ""
    try {
        $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    } catch {}
    $cmdLine -like "*hbgm001*" -or $cmdLine -like "*luckyred*"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "  OK: Ready to start" -ForegroundColor Green

# Start services
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "   Starting Services..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Start API in new window
Write-Host "Starting API server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$apiDir'; & '.venv\Scripts\Activate.ps1'; Write-Host ''; Write-Host '========================================' -ForegroundColor Green; Write-Host '  API Server - http://localhost:8080' -ForegroundColor Green; Write-Host '  Docs: http://localhost:8080/docs' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Green; Write-Host ''; uvicorn main:app --host 127.0.0.1 --port 8080 --reload"
)

# Wait for API to start
Write-Host "Waiting for API to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Start Bot in new window
Write-Host "Starting Bot..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$botDir'; & '.venv\Scripts\Activate.ps1'; Write-Host ''; Write-Host '========================================' -ForegroundColor Green; Write-Host '  Telegram Bot Starting...' -ForegroundColor Green; Write-Host '========================================' -ForegroundColor Green; Write-Host ''; python main.py"
)

# Final message
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "   Services Started Successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service Information:" -ForegroundColor Yellow
Write-Host "  - API Server: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  - API Docs: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host "  - Bot: Check Bot window for status" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Commands:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:8080/docs in browser" -ForegroundColor White
Write-Host "  2. Send /start to your Bot in Telegram" -ForegroundColor White
Write-Host ""
Write-Host "To stop services: Close the API and Bot windows" -ForegroundColor Gray
Write-Host ""
