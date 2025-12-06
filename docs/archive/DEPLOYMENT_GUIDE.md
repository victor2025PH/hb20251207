# 🚀 Lucky Red 完整部署指南

## 📋 部署前準備

### 1. 系統要求
- **操作系統**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.10+
- **PostgreSQL**: 14+
- **Node.js**: 18+ (用於前端)
- **Nginx**: 最新版本
- **系統內存**: 至少 2GB
- **硬盤空間**: 至少 10GB

### 2. 服務器準備
```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝基礎工具
sudo apt install -y git curl wget build-essential

# 安裝 PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 安裝 Nginx
sudo apt install -y nginx

# 安裝 Python 和 pip
sudo apt install -y python3.10 python3.10-venv python3-pip

# 安裝 Node.js (使用 nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

## 🔧 配置步驟

### 步驟 1: 克隆項目
```bash
# 創建項目目錄
sudo mkdir -p /opt/luckyred
sudo chown $USER:$USER /opt/luckyred
cd /opt/luckyred

# 克隆項目（或上傳代碼）
git clone <your-repo-url> .
# 或使用 scp/rsync 上傳代碼
```

### 步驟 2: 配置數據庫
```bash
# 切換到 postgres 用戶
sudo -u postgres psql

# 在 PostgreSQL 中執行
CREATE DATABASE luckyred;
CREATE USER luckyred WITH PASSWORD 'your_secure_password_here';
ALTER ROLE luckyred SET client_encoding TO 'utf8';
ALTER ROLE luckyred SET default_transaction_isolation TO 'read committed';
ALTER ROLE luckyred SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE luckyred TO luckyred;
\q
```

### 步驟 3: 配置環境變量
```bash
# 複製環境變量模板
cp .env.example .env

# 編輯環境變量
nano .env
```

**重要環境變量配置：**
```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=your_bot_username
ADMIN_IDS=123456789,987654321

# Database
DATABASE_URL=postgresql://luckyred:your_password@localhost:5432/luckyred

# API
API_HOST=127.0.0.1
API_PORT=8080
API_BASE_URL=https://api.usdt2026.cc

# Security
JWT_SECRET=your_very_secure_random_secret_key_here

# Domains
BOT_DOMAIN=bot.usdt2026.cc
ADMIN_DOMAIN=admin.usdt2026.cc
MINIAPP_DOMAIN=mini.usdt2026.cc
MINIAPP_URL=https://mini.usdt2026.cc

# Application
DEBUG=false
LOG_LEVEL=INFO
```

### 步驟 4: 安裝 Python 依賴
```bash
# API 服務
cd /opt/luckyred/api
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Bot 服務
cd /opt/luckyred/bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 步驟 5: 初始化數據庫
```bash
# 設置環境變量
export DATABASE_URL="postgresql://luckyred:your_password@localhost:5432/luckyred"

# 初始化數據庫（運行一次即可）
cd /opt/luckyred/api
source .venv/bin/activate
python -c "from shared.database.connection import init_db; init_db()"
```

### 步驟 6: 配置 Systemd 服務

#### API 服務
```bash
# 複製服務文件
sudo cp deploy/systemd/luckyred-api.service /etc/systemd/system/

# 編輯服務文件（如果需要）
sudo nano /etc/systemd/system/luckyred-api.service

# 重新加載 systemd
sudo systemctl daemon-reload

# 啟用並啟動服務
sudo systemctl enable luckyred-api
sudo systemctl start luckyred-api

# 檢查狀態
sudo systemctl status luckyred-api
```

#### Bot 服務
```bash
# 複製服務文件
sudo cp deploy/systemd/luckyred-bot.service /etc/systemd/system/

# 重新加載 systemd
sudo systemctl daemon-reload

# 啟用並啟動服務
sudo systemctl enable luckyred-bot
sudo systemctl start luckyred-bot

# 檢查狀態
sudo systemctl status luckyred-bot
```

### 步驟 7: 配置 Nginx

#### 複製 Nginx 配置
```bash
# 複製配置文件
sudo cp deploy/nginx/*.conf /etc/nginx/sites-available/

# 創建符號鏈接
sudo ln -s /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/

# 測試配置
sudo nginx -t

# 重載 Nginx
sudo systemctl reload nginx
```

#### 配置 SSL 證書（使用 Certbot）
```bash
# 安裝 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 獲取 SSL 證書
sudo certbot --nginx -d mini.usdt2026.cc
sudo certbot --nginx -d admin.usdt2026.cc
sudo certbot --nginx -d bot.usdt2026.cc

# 設置自動續期
sudo certbot renew --dry-run
```

### 步驟 8: 部署前端

#### Miniapp (React)
```bash
cd /opt/luckyred/frontend

# 安裝依賴
npm install

# 構建生產版本
npm run build

# 配置 Nginx 指向構建目錄
# (已在 nginx 配置文件中設置)
```

#### Admin (如果需要)
```bash
cd /opt/luckyred/admin

# 安裝依賴
npm install

# 構建生產版本
npm run build
```

## 🔍 驗證部署

### 檢查服務狀態
```bash
# 檢查所有服務
sudo systemctl status luckyred-api
sudo systemctl status luckyred-bot
sudo systemctl status nginx
sudo systemctl status postgresql

# 檢查端口
sudo netstat -tlnp | grep -E '8080|5432|80|443'
```

### 檢查日誌
```bash
# API 日誌
sudo journalctl -u luckyred-api -f

# Bot 日誌
sudo journalctl -u luckyred-bot -f

# Nginx 日誌
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 測試 API
```bash
# 健康檢查
curl http://localhost:8080/health

# API 文檔（如果 DEBUG=true）
curl http://localhost:8080/docs
```

### 測試 Bot
```bash
# 在 Telegram 中發送 /start 命令測試
# 檢查日誌確認 Bot 響應
```

## 🔄 更新部署

### 快速更新腳本
```bash
# 使用提供的更新腳本
./deploy/scripts/quick-update.sh

# 或手動更新
cd /opt/luckyred
git pull  # 或上傳新代碼

# 更新 API
cd api
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart luckyred-api

# 更新 Bot
cd ../bot
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart luckyred-bot

# 更新前端
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

## 🛠️ 故障排除

### 服務無法啟動
```bash
# 檢查日誌
sudo journalctl -u luckyred-api -n 50
sudo journalctl -u luckyred-bot -n 50

# 檢查環境變量
sudo systemctl show luckyred-api --property=Environment

# 檢查文件權限
ls -la /opt/luckyred/
```

### 數據庫連接問題
```bash
# 測試數據庫連接
psql -U luckyred -d luckyred -h localhost

# 檢查 PostgreSQL 狀態
sudo systemctl status postgresql

# 檢查數據庫配置
sudo nano /etc/postgresql/*/main/postgresql.conf
```

### Nginx 配置問題
```bash
# 測試配置
sudo nginx -t

# 檢查錯誤日誌
sudo tail -f /var/log/nginx/error.log

# 檢查訪問日誌
sudo tail -f /var/log/nginx/access.log
```

### Bot 無法連接
```bash
# 檢查 BOT_TOKEN 是否正確
grep BOT_TOKEN /opt/luckyred/.env

# 檢查網絡連接
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# 檢查防火牆
sudo ufw status
```

## 📊 監控和維護

### 設置日誌輪轉
```bash
# 創建日誌輪轉配置
sudo nano /etc/logrotate.d/luckyred

# 內容：
/var/log/luckyred/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 設置備份
```bash
# 創建備份腳本
sudo nano /opt/luckyred/scripts/backup.sh

# 內容示例：
#!/bin/bash
BACKUP_DIR="/opt/backups/luckyred"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 備份數據庫
pg_dump -U luckyred luckyred > $BACKUP_DIR/db_$DATE.sql

# 備份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/luckyred/.env

# 保留最近 7 天的備份
find $BACKUP_DIR -type f -mtime +7 -delete
```

### 設置定時任務
```bash
# 編輯 crontab
crontab -e

# 添加每日備份（凌晨 2 點）
0 2 * * * /opt/luckyred/scripts/backup.sh

# 添加日誌清理（每週一）
0 3 * * 1 /opt/luckyred/scripts/cleanup-logs.sh
```

## 🔒 安全建議

1. **防火牆配置**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **定期更新**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **強密碼策略**
   - 使用強密碼生成器
   - 定期更換密碼
   - 使用密碼管理器

4. **SSL 證書**
   - 確保所有域名都有有效的 SSL 證書
   - 設置自動續期

5. **訪問控制**
   - 限制 SSH 訪問
   - 使用 SSH 密鑰認證
   - 禁用 root 登錄

## 📞 支持

如果遇到問題，請檢查：
1. 日誌文件
2. 服務狀態
3. 網絡連接
4. 配置文件

更多信息請參考：
- `OPTIMIZATION_SUMMARY.md` - 優化總結
- `README.md` - 項目文檔
