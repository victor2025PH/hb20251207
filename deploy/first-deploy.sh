#!/bin/bash
# ===========================================
# hbgm001 First Deployment Script
# Execute this script on the server for first-time deployment
# ===========================================

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PROJECT_DIR="/home/ubuntu/hbgm001"
GIT_REPO="https://github.com/victor2025PH/hb20251207.git"
SERVICE_NAME="hbgm001-backend"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  hbgm001 First Deployment"
echo "=========================================="
echo

# 1. Check if running as root or sudo
if [ "$EUID" -ne 0 ]; then
    log_warn "sudo privileges required, some operations may need password"
fi

# 2. Update system
log_info "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# 3. Install basic dependencies
log_info "Installing basic dependencies..."
sudo apt install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    curl \
    wget

# 4. Create project directory
log_info "Creating project directory: $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown -R ubuntu:ubuntu $PROJECT_DIR

# 5. Clone code (if directory is empty)
if [ ! -d "$PROJECT_DIR/.git" ]; then
    log_info "Cloning code repository..."
    cd /home/ubuntu
    git clone $GIT_REPO hbgm001
else
    log_info "Code already exists, skipping clone"
fi

# 6. Create virtual environment
log_info "Creating Python virtual environment..."
cd $PROJECT_DIR
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    log_info "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# 7. Activate virtual environment and install dependencies
log_info "Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 8. Create .env file (if not exists)
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_warn ".env file does not exist, please create and configure manually"
    log_info "You can copy from env-template.txt"
    if [ -f "$PROJECT_DIR/env-template.txt" ]; then
        cp $PROJECT_DIR/env-template.txt $PROJECT_DIR/.env
        log_info "Created .env file from template, please edit configuration"
    fi
else
    log_info ".env file already exists"
fi

# 9. Create systemd service file
log_info "Creating systemd service..."
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=hbgm001 Backend API Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$PROJECT_DIR"
EnvironmentFile=$PROJECT_DIR/.env

# Start command
ExecStart=$PROJECT_DIR/.venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8080 --workers 4

# Restart policy
Restart=always
RestartSec=5
StartLimitInterval=200
StartLimitBurst=5

# Logging configuration
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security configuration
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# 10. Reload systemd
log_info "Reloading systemd..."
sudo systemctl daemon-reload

# 11. Enable service (start on boot)
log_info "Enabling service..."
sudo systemctl enable ${SERVICE_NAME}.service

# 12. Start service
log_info "Starting service..."
sudo systemctl start ${SERVICE_NAME}.service

# 13. Wait for service to start
sleep 3

# 14. Check service status
log_info "Checking service status..."
sudo systemctl status ${SERVICE_NAME}.service --no-pager -l || true

echo
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo
echo "Common commands:"
echo "  Check status: sudo systemctl status $SERVICE_NAME"
echo "  View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  Stop service: sudo systemctl stop $SERVICE_NAME"
echo
echo "Important: Please ensure .env file is configured!"
echo

