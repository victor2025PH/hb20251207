#!/bin/bash
# LuckyRed 完整部署腳本
# 使用方法: ./deploy.sh

set -e

echo "=========================================="
echo "  LuckyRed 部署腳本"
echo "=========================================="

# 配置
APP_DIR="/opt/luckyred"
REPO_URL="https://github.com/victor2025PH/hongbao20251025.git"

# 顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 檢查 root 權限
if [ "$EUID" -ne 0 ]; then
    log_error "請使用 root 權限運行此腳本"
    exit 1
fi

# 1. 系統更新
log_info "更新系統..."
apt update && apt upgrade -y

# 2. 安裝依賴
log_info "安裝依賴..."
apt install -y \
    nginx \
    certbot python3-certbot-nginx \
    postgresql postgresql-contrib \
    python3 python3-pip python3-venv \
    nodejs npm \
    git curl wget

# 3. 配置 PostgreSQL
log_info "配置 PostgreSQL..."
sudo -u postgres psql -c "CREATE USER luckyred WITH PASSWORD 'your_secure_password';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE luckyred OWNER luckyred;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE luckyred TO luckyred;" 2>/dev/null || true

# 4. 創建應用目錄
log_info "創建應用目錄..."
mkdir -p $APP_DIR
cd $APP_DIR

# 5. 克隆代碼
if [ -d ".git" ]; then
    log_info "更新代碼..."
    git pull
else
    log_info "克隆代碼..."
    git clone $REPO_URL .
fi

# 6. 配置環境變量
if [ ! -f "$APP_DIR/.env" ]; then
    log_warn "請創建 .env 文件！"
    cat > $APP_DIR/.env.example << 'EOF'
# Telegram Bot
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789

# Database
DATABASE_URL=postgresql://luckyred:your_secure_password@localhost:5432/luckyred

# App
SECRET_KEY=your_secret_key_here
DEBUG=false

# Domains
MINIAPP_URL=https://mini.usdt2026.cc
ADMIN_URL=https://admin.usdt2026.cc
EOF
    log_error "請編輯 $APP_DIR/.env 文件後重新運行部署"
    exit 1
fi

# 7. 安裝 API 依賴
log_info "安裝 API 依賴..."
cd $APP_DIR/api
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 8. 安裝 Bot 依賴
log_info "安裝 Bot 依賴..."
cd $APP_DIR/bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 9. 安裝 Admin 依賴
log_info "安裝 Admin 依賴..."
cd $APP_DIR/admin
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 10. 構建前端
log_info "構建前端..."
cd $APP_DIR/frontend
npm install
npm run build

# 11. 配置 Nginx
log_info "配置 Nginx..."
cp $APP_DIR/deploy/nginx/*.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 12. 配置 Systemd 服務
log_info "配置 Systemd 服務..."
cp $APP_DIR/deploy/systemd/*.service /etc/systemd/system/
systemctl daemon-reload

# 13. 設置權限
log_info "設置權限..."
chown -R www-data:www-data $APP_DIR

# 14. 啟動服務
log_info "啟動服務..."
systemctl enable luckyred-api luckyred-bot luckyred-admin
systemctl restart luckyred-api luckyred-bot luckyred-admin

# 15. 獲取 SSL 證書 (需要域名已指向服務器)
log_info "獲取 SSL 證書..."
certbot --nginx -d mini.usdt2026.cc -d admin.usdt2026.cc --non-interactive --agree-tos -m admin@example.com || true

# 16. 檢查服務狀態
log_info "檢查服務狀態..."
systemctl status luckyred-api --no-pager || true
systemctl status luckyred-bot --no-pager || true
systemctl status luckyred-admin --no-pager || true

echo ""
echo "=========================================="
echo -e "${GREEN}  部署完成！${NC}"
echo "=========================================="
echo "MiniApp: https://mini.usdt2026.cc"
echo "Admin: https://admin.usdt2026.cc"
echo ""
echo "查看日誌:"
echo "  journalctl -u luckyred-api -f"
echo "  journalctl -u luckyred-bot -f"
echo "  journalctl -u luckyred-admin -f"
echo "=========================================="

