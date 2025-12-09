@echo off
chcp 65001 >nul
title Add SSH Key to Server

echo ==========================================
echo   Add SSH Key to Server
echo ==========================================
echo.
echo Server: ubuntu@165.154.254.99
echo.
echo This will copy your public key to the server.
echo Please enter password when prompted: Along2025!!!
echo.

type %USERPROFILE%\.ssh\id_rsa.pub | ssh ubuntu@165.154.254.99 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] SSH key added successfully!
    echo.
    echo Testing connection...
    ssh -o BatchMode=yes ubuntu@165.154.254.99 "echo 'SSH key authentication works!'"
    if %errorlevel% equ 0 (
        echo.
        echo [SUCCESS] You can now connect without password!
    ) else (
        echo.
        echo [WARNING] Connection test failed. Please check manually.
    )
) else (
    echo.
    echo [ERROR] Failed to add SSH key.
)

echo.
pause

