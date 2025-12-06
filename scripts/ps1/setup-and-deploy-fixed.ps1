# ============================================
# Lucky Red Auto Deployment Script
# ============================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lucky Red Auto Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check .env file
Write-Host "Step 1: Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Warning: .env file created, please configure required variables!" -ForegroundColor Red
    Write-Host "Press Enter to open .env file for configuration..." -ForegroundColor Yellow
    Read-Host | Out-Null
    notepad .env
}

# Check Python
Write-Host "`nStep 2: Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ and add to PATH" -ForegroundColor Yellow
    exit 1
}

# Setup API environment
Write-Host "`nStep 3: Setting up API environment..." -ForegroundColor Yellow
Set-Location api

if (-not (Test-Path .venv)) {
    Write-Host "Creating API virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    Write-Host "OK Virtual environment created" -ForegroundColor Green
}

Write-Host "Activating virtual environment and installing dependencies..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip | Out-Null
Write-Host "Installing API dependencies (this may take a few minutes)..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Dependency installation failed" -ForegroundColor Red
    deactivate
    Set-Location ..
    exit 1
}
Write-Host "OK API dependencies installed" -ForegroundColor Green
deactivate

Set-Location ..

# Setup Bot environment
Write-Host "`nStep 4: Setting up Bot environment..." -ForegroundColor Yellow
Set-Location bot

if (-not (Test-Path .venv)) {
    Write-Host "Creating Bot virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    Write-Host "OK Virtual environment created" -ForegroundColor Green
}

Write-Host "Activating virtual environment and installing dependencies..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip | Out-Null
Write-Host "Installing Bot dependencies (this may take a few minutes)..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Dependency installation failed" -ForegroundColor Red
    deactivate
    Set-Location ..
    exit 1
}
Write-Host "OK Bot dependencies installed" -ForegroundColor Green
deactivate

Set-Location ..

# Initialize database
Write-Host "`nStep 5: Initializing database..." -ForegroundColor Yellow
Set-Location api
& .\.venv\Scripts\Activate.ps1

Write-Host "Checking database connection..." -ForegroundColor Cyan
try {
    $initScript = 'from shared.database.connection import init_db; init_db(); print("OK Database initialized successfully")'
    python -c $initScript
    if ($LASTEXITCODE -ne 0) {
        throw "Initialization failed"
    }
} catch {
    Write-Host "Warning: Database initialization may have failed, please check:" -ForegroundColor Yellow
    Write-Host "  1. Is DATABASE_URL correctly configured?" -ForegroundColor Cyan
    Write-Host "  2. Is the database service running?" -ForegroundColor Cyan
    Write-Host "  3. Does the database user have permissions?" -ForegroundColor Cyan
}

deactivate
Set-Location ..

# Complete
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment preparation complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start API server:" -ForegroundColor Cyan
Write-Host "   cd api" -ForegroundColor White
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn main:app --host 0.0.0.0 --port 8080 --reload" -ForegroundColor White
Write-Host ""
Write-Host "2. Start Bot (new terminal window):" -ForegroundColor Cyan
Write-Host "   cd bot" -ForegroundColor White
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
Write-Host "3. Or use quick start script:" -ForegroundColor Cyan
Write-Host "   .\start-services.ps1" -ForegroundColor White
Write-Host ""

$startNow = Read-Host "Start services now? (Y/N)"
if ($startNow -eq "Y" -or $startNow -eq "y") {
    Write-Host ""
    Write-Host "Starting services..." -ForegroundColor Green
    
    # Check if port 8080 is available
    $portInUse = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "Warning: Port 8080 is already in use!" -ForegroundColor Yellow
        Write-Host "Trying to use port 8081 instead..." -ForegroundColor Yellow
        $apiPort = "8081"
    } else {
        $apiPort = "8080"
    }
    
    # Start API
    $apiPath = Join-Path $PWD "api"
    $apiCmd = "cd '$apiPath'; .venv\Scripts\Activate.ps1; Write-Host 'Starting API server on port $apiPort...' -ForegroundColor Green; uvicorn main:app --host 127.0.0.1 --port $apiPort --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCmd
    
    # Wait a bit
    Start-Sleep -Seconds 2
    
    # Stop old Bot instances if any
    Write-Host "Checking for old Bot instances..." -ForegroundColor Cyan
    $botProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine)
            $cmdLine -like "*bot*main.py*" -or $cmdLine -like "*hbgm001\bot*"
        } catch {
            $false
        }
    }
    if ($botProcesses) {
        Write-Host "Found $($botProcesses.Count) old Bot instance(s), stopping..." -ForegroundColor Yellow
        $botProcesses | ForEach-Object {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
        Write-Host "Old instances stopped" -ForegroundColor Green
    }
    
    # Start Bot
    $botPath = Join-Path $PWD "bot"
    $botCmd = "cd '$botPath'; .venv\Scripts\Activate.ps1; Write-Host 'Starting Bot...' -ForegroundColor Green; python main.py"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
    
    Write-Host "OK Services started in new windows" -ForegroundColor Green
    Write-Host ""
    if ($apiPort) {
        Write-Host "API: http://localhost:$apiPort" -ForegroundColor Cyan
        Write-Host "API Docs: http://localhost:$apiPort/docs" -ForegroundColor Cyan
    } else {
        Write-Host "API: http://localhost:8080" -ForegroundColor Cyan
        Write-Host "API Docs: http://localhost:8080/docs" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
