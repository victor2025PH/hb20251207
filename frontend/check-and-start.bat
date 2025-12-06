@echo off
echo Checking Frontend Environment...
echo.

cd /d %~dp0

echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js is installed
node --version

echo.
echo Checking npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed
    pause
    exit /b 1
)
echo [OK] npm is installed
npm --version

echo.
echo Checking dependencies...
if not exist node_modules (
    echo [INFO] node_modules not found, installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo Checking Vite...
if not exist node_modules\vite (
    echo [INFO] Vite not found, installing...
    call npm install vite
)

echo.
echo Starting development server...
echo.
call npm run dev

pause
