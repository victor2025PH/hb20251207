# 手动部署命令清单

## 步骤1: 移动文件到部署目录
```bash
sudo mkdir -p /opt/luckyred
sudo cp -r /home/ubuntu/hbgm001/* /opt/luckyred/
sudo chown -R ubuntu:ubuntu /opt/luckyred
cd /opt/luckyred
```

## 步骤2: 安装系统依赖
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx postgresql postgresql-contrib python3 python3-pip python3-venv nodejs npm git curl
```

## 步骤3: 配置 PostgreSQL
```bash
sudo -u postgres psql -c "CREATE USER luckyred WITH PASSWORD 'LuckyRed2025!';" 2>/dev/null || echo "用户已存在"
sudo -u postgres psql -c "CREATE DATABASE luckyred OWNER luckyred;" 2>/dev/null || echo "数据库已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE luckyred TO luckyred;"
```

## 步骤4: 创建环境变量文件
```bash
cat > /opt/luckyred/.env << 'EOF'
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
EOF
```

**⚠️ 重要：编辑 .env 文件填入 BOT_TOKEN**
```bash
nano /opt/luckyred/.env
# 将 YOUR_BOT_TOKEN_HERE 替换为实际的 Bot Token
```

## 步骤5: 安装 API 依赖
```bash
cd /opt/luckyred/api
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## 步骤6: 安装 Bot 依赖
```bash
cd /opt/luckyred/bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## 步骤7: 构建前端
```bash
cd /opt/luckyred/frontend
npm install
npm run build
```

## 步骤8: 配置 Nginx
```bash
sudo cp /opt/luckyred/deploy/nginx/*.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 步骤9: 配置 Systemd 服务
```bash
sudo cp /opt/luckyred/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo chown -R www-data:www-data /opt/luckyred
```

## 步骤10: 启动服务
```bash
sudo systemctl enable luckyred-api luckyred-bot
sudo systemctl start luckyred-api luckyred-bot
```

## 步骤11: 检查服务状态
```bash
sudo systemctl status luckyred-api
sudo systemctl status luckyred-bot
```

## 步骤12: 获取 SSL 证书
```bash
sudo certbot --nginx -d mini.usdt2026.cc -d admin.usdt2026.cc --non-interactive --agree-tos -m admin@usdt2026.cc
```

## 步骤13: 查看日志（如果需要）
```bash
sudo journalctl -u luckyred-api -f
sudo journalctl -u luckyred-bot -f
```

## 一键执行所有命令（复制粘贴）
```bash
# 1. 移动文件
sudo mkdir -p /opt/luckyred && sudo cp -r /home/ubuntu/hbgm001/* /opt/luckyred/ && sudo chown -R ubuntu:ubuntu /opt/luckyred && cd /opt/luckyred

# 2. 安装依赖
sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx postgresql postgresql-contrib python3 python3-pip python3-venv nodejs npm git curl

# 3. 配置数据库
sudo -u postgres psql -c "CREATE USER luckyred WITH PASSWORD 'LuckyRed2025!';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE luckyred OWNER luckyred;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE luckyred TO luckyred;"

# 4. 创建环境变量（需要手动编辑 BOT_TOKEN）
cat > /opt/luckyred/.env << 'EOF'
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_IDS=5433982810
DATABASE_URL=postgresql://luckyred:LuckyRed2025!@localhost:5432/luckyred
SECRET_KEY=luckyred_secret_key_2025_very_secure
MINIAPP_URL=https://mini.usdt2026.cc
ADMIN_URL=https://admin.usdt2026.cc
DEBUG=false
EOF

# 5. 安装 API 依赖
cd /opt/luckyred/api && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate

# 6. 安装 Bot 依赖
cd /opt/luckyred/bot && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate

# 7. 构建前端
cd /opt/luckyred/frontend && npm install && npm run build

# 8. 配置 Nginx
sudo cp /opt/luckyred/deploy/nginx/*.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 9. 配置服务
sudo cp /opt/luckyred/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo chown -R www-data:www-data /opt/luckyred

# 10. 启动服务
sudo systemctl enable luckyred-api luckyred-bot
sudo systemctl start luckyred-api luckyred-bot

# 11. 检查状态
sudo systemctl status luckyred-api --no-pager
sudo systemctl status luckyred-bot --no-pager
```


