#!/bin/bash
# 快速部署脚本 - 在服务器上执行

set -e

echo "=========================================="
echo "  LuckyRed 快速部署"
echo "=========================================="

APP_DIR="/opt/luckyred"
SOURCE_DIR="/home/ubuntu/hbgm001"

# 1. 移动文件到部署目录
echo "[1/8] 移动文件到部署目录..."
sudo mkdir -p $APP_DIR
sudo cp -r $SOURCE_DIR/* $APP_DIR/
sudo chown -R ubuntu:ubuntu $APP_DIR
cd $APP_DIR

# 2. 安装系统依赖
echo "[2/8] 安装系统依赖..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx postgresql postgresql-contrib python3 python3-pip python3-venv nodejs npm git curl

# 3. 配置 PostgreSQL
echo "[3/8] 配置 PostgreSQL..."
sudo -u postgres psql -c "CREATE USER luckyred WITH PASSWORD 'LuckyRed2025!';" 2>/dev/null || echo "用户已存在"
sudo -u postgres psql -c "CREATE DATABASE luckyred OWNER luckyred;" 2>/dev/null || echo "数据库已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE luckyred TO luckyred;"

# 4. 创建环境变量文件
echo "[4/8] 创建环境变量文件..."
if [ ! -f "$APP_DIR/.env" ]; then
cat > $APP_DIR/.env << 'ENVEOF'
# Telegram Bot
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_IDS=5433982810

# Database
DATABASE_URL=postgresql://luckyred:LuckyRed2025!@localhost:5432/luckyred

# Security
SECRET_KEY=luckyred_secret_key_2025_very_secure

# URLs
MINIAPP_URL=https://mini.usdt2026.cc
ADMIN_URL=https://admin.usdt2026.cc
DEBUG=false
ENVEOF
echo "⚠️  请编辑 $APP_DIR/.env 填入正确的 BOT_TOKEN！"
fi

# 5. 安装 Python 依赖
echo "[5/8] 安装 API 依赖..."
cd $APP_DIR/api
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "安装 Bot 依赖..."
cd $APP_DIR/bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 6. 构建前端
echo "[6/8] 构建前端..."
cd $APP_DIR/frontend
npm install
npm run build

# 7. 配置 Nginx
echo "[7/8] 配置 Nginx..."
sudo cp $APP_DIR/deploy/nginx/*.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 8. 配置 Systemd
echo "[8/8] 配置服务..."
sudo cp $APP_DIR/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo chown -R www-data:www-data $APP_DIR

echo ""
echo "=========================================="
echo "  ✅ 基础部署完成！"
echo "=========================================="
echo ""
echo "⚠️  重要：请编辑 /opt/luckyred/.env 填入 BOT_TOKEN"
echo "   nano /opt/luckyred/.env"
echo ""
echo "然后启动服务："
echo "   sudo systemctl enable luckyred-api luckyred-bot"
echo "   sudo systemctl start luckyred-api luckyred-bot"
echo ""
echo "获取 SSL 证书："
echo "   sudo certbot --nginx -d mini.usdt2026.cc -d admin.usdt2026.cc"
echo "=========================================="


