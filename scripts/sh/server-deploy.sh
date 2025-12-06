#!/bin/bash
# LuckyRed 一鍵部署腳本
# 在服務器上執行: bash server-deploy.sh

set -e

echo "=========================================="
echo "  LuckyRed 自動部署"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 系統更新和依賴安裝
echo "[1/10] 安裝系統依賴..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx postgresql postgresql-contrib python3 python3-pip python3-venv nodejs npm git curl

# 2. 配置 PostgreSQL
echo "[2/10] 配置 PostgreSQL..."
sudo -u postgres psql -c "CREATE USER luckyred WITH PASSWORD 'LuckyRed2025!';" 2>/dev/null || echo "用戶已存在"
sudo -u postgres psql -c "CREATE DATABASE luckyred OWNER luckyred;" 2>/dev/null || echo "數據庫已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE luckyred TO luckyred;"

# 3. 創建目錄
echo "[3/10] 創建應用目錄..."
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR
cd $APP_DIR

# 4. 克隆代碼
echo "[4/10] 克隆代碼..."
if [ -d ".git" ]; then
    git pull
else
    git clone https://github.com/victor2025PH/hongbao20251025.git .
fi

# 5. 創建環境變量文件
echo "[5/10] 創建環境變量..."
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
echo "⚠️  請編輯 $APP_DIR/.env 填入正確的 BOT_TOKEN！"
fi

# 6. 安裝 Python 依賴
echo "[6/10] 安裝 API 依賴..."
cd $APP_DIR/api
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "安裝 Bot 依賴..."
cd $APP_DIR/bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 7. 安裝前端依賴並構建
echo "[7/10] 構建前端..."
cd $APP_DIR/frontend
npm install
npm run build

# 8. 配置 Nginx
echo "[8/10] 配置 Nginx..."
sudo cp $APP_DIR/deploy/nginx/*.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 9. 配置 Systemd
echo "[9/10] 配置服務..."
sudo cp $APP_DIR/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo chown -R www-data:www-data $APP_DIR

# 10. 啟動服務
echo "[10/10] 啟動服務..."
sudo systemctl enable luckyred-api luckyred-bot
sudo systemctl restart luckyred-api luckyred-bot

# 獲取 SSL
echo "獲取 SSL 證書..."
sudo certbot --nginx -d mini.usdt2026.cc -d admin.usdt2026.cc --non-interactive --agree-tos -m admin@usdt2026.cc || echo "SSL 獲取失敗，請手動執行 certbot"

echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "⚠️  重要：請編輯 /opt/luckyred/.env 填入 BOT_TOKEN"
echo "   nano /opt/luckyred/.env"
echo ""
echo "然後重啟服務："
echo "   sudo systemctl restart luckyred-bot"
echo ""
echo "檢查服務狀態："
echo "   sudo systemctl status luckyred-api"
echo "   sudo systemctl status luckyred-bot"
echo ""
echo "查看日誌："
echo "   sudo journalctl -u luckyred-api -f"
echo "   sudo journalctl -u luckyred-bot -f"
echo "=========================================="

