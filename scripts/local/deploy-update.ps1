# Update Deployment Script
# Uses system SSH command

$SERVER = "ubuntu@165.154.254.99"
$PROJECT_DIR = "/home/ubuntu/hbgm001"

Write-Host "=========================================="
Write-Host "  Update Deployment"
Write-Host "=========================================="
Write-Host ""
Write-Host "Connecting to server: $SERVER"
Write-Host "Project directory: $PROJECT_DIR"
Write-Host ""

# Execute deployment commands via SSH
$deployCommand = @"
cd $PROJECT_DIR && \
git pull origin main && \
chmod +x deploy/update-deploy.sh && \
bash deploy/update-deploy.sh
"@

Write-Host "Executing deployment..."
ssh $SERVER $deployCommand

Write-Host ""
Write-Host "=========================================="
Write-Host "  Deployment Complete!"
Write-Host "=========================================="

