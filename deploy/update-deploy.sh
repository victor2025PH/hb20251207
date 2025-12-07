#!/bin/bash
# ===========================================
# hbgm001 Update Deployment Script
# Used to update code and restart service
# ===========================================

set -e

# Configuration
PROJECT_DIR="/home/ubuntu/hbgm001"
SERVICE_NAME="hbgm001-backend"

echo "=========================================="
echo "  Update Deployment hbgm001"
echo "=========================================="
echo

# Enter project directory
cd $PROJECT_DIR

# Pull latest code
echo "📥 Pulling latest code..."
git fetch origin
git pull origin main

# Activate virtual environment and update dependencies
echo "📦 Updating Python dependencies..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️  Virtual environment does not exist, creating new one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Run database migrations (if any)
if [ -d "migrations" ]; then
    echo "🗄️  Checking database migrations..."
    echo "Note: If there are migration files, please run manually"
fi

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart $SERVICE_NAME

# Wait for service to start
sleep 3

# Check service status
echo "✅ Checking service status..."
sudo systemctl status $SERVICE_NAME --no-pager -l || true

echo
echo "=========================================="
echo "  Update Complete!"
echo "=========================================="

