# Setup SSH Key Authentication
# This script will copy your public key to the server

$SERVER = "ubuntu@165.154.254.99"
$PUBLIC_KEY_PATH = "$env:USERPROFILE\.ssh\id_rsa.pub"

Write-Host "=========================================="
Write-Host "  SSH Key Setup"
Write-Host "=========================================="
Write-Host ""

# Check if public key exists
if (-not (Test-Path $PUBLIC_KEY_PATH)) {
    Write-Host "[ERROR] Public key not found: $PUBLIC_KEY_PATH" -ForegroundColor Red
    Write-Host "Generating new SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N '""'
    Write-Host "[SUCCESS] SSH key generated" -ForegroundColor Green
}

# Read public key
$publicKey = Get-Content $PUBLIC_KEY_PATH
Write-Host "[INFO] Your public key:" -ForegroundColor Cyan
Write-Host $publicKey
Write-Host ""

# Copy public key to server
Write-Host "[INFO] Copying public key to server..." -ForegroundColor Cyan
Write-Host "Please enter password when prompted: Along2025!!!" -ForegroundColor Yellow
Write-Host ""

# Use ssh-copy-id if available, otherwise manual method
$sshCopyId = Get-Command ssh-copy-id -ErrorAction SilentlyContinue
if ($sshCopyId) {
    ssh-copy-id -i $PUBLIC_KEY_PATH $SERVER
} else {
    # Manual method: append public key to authorized_keys
    Write-Host "Using manual method to copy key..."
    $tempFile = [System.IO.Path]::GetTempFileName()
    $publicKey | Out-File -FilePath $tempFile -Encoding ASCII
    
    # Copy key to server
    $command = "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
    Get-Content $tempFile | ssh $SERVER $command
    
    Remove-Item $tempFile
}

Write-Host ""
Write-Host "[INFO] Testing SSH connection..." -ForegroundColor Cyan
ssh -o BatchMode=yes -o ConnectTimeout=5 $SERVER "echo 'SSH key authentication successful!'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] SSH key authentication configured successfully!" -ForegroundColor Green
    Write-Host "You can now connect without password using: ssh $SERVER" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[WARNING] SSH key may not be configured correctly." -ForegroundColor Yellow
    Write-Host "Please check the output above for errors." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================="

