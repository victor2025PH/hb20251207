# 🚀 快速部署指南

## 一鍵部署（推薦）

### 使用自動部署腳本
```bash
# 1. 上傳代碼到服務器
scp -r . user@your-server:/opt/luckyred/

# 2. SSH 登錄服務器
ssh user@your-server

# 3. 配置環境變量
cd /opt/luckyred
cp .env.example .env
nano .env  # 填寫實際配置值

# 4. 運行部署腳本
sudo bash deploy/scripts/deploy-full.sh
```

## 手動部署步驟

### 1. 準備環境變量
```bash
cd /opt/luckyred
cp .env.example .env
nano .env
```

**必須配置的變量：**
- `BOT_TOKEN` - Telegram Bot Token
- `BOT_USERNAME` - Bot 用戶名
- `ADMIN_IDS` - 管理員 ID（逗號分隔）
- `DATABASE_URL` - 數據庫連接字符串
- `JWT_SECRET` - JWT 密鑰（使用強隨機字符串）
- `API_BASE_URL` - API 基礎 URL（生產環境使用 HTTPS）

### 2. 安裝依賴
```bash
# API
cd /opt/luckyred/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Bot
cd /opt/luckyred/bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 初始化數據庫
```bash
cd /opt/luckyred/api
source .venv/bin/activate
python3 -c "from shared.database.connection import init_db; init_db()"
```

### 4. 配置服務
```bash
# 複製服務文件
sudo cp deploy/systemd/*.service /etc/systemd/system/

# 重新加載 systemd
sudo systemctl daemon-reload

# 啟用服務
sudo systemctl enable luckyred-api
sudo systemctl enable luckyred-bot

# 啟動服務
sudo systemctl start luckyred-api
sudo systemctl start luckyred-bot
```

### 5. 配置 Nginx
```bash
# 複製配置文件
sudo cp deploy/nginx/*.conf /etc/nginx/sites-available/

# 啟用站點
sudo ln -s /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/

# 測試並重載
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 構建前端
```bash
cd /opt/luckyred/frontend
npm install
npm run build
```

## 驗證部署

### 檢查服務狀態
```bash
sudo systemctl status luckyred-api
sudo systemctl status luckyred-bot
sudo systemctl status nginx
```

### 檢查日誌
```bash
# API 日誌
sudo journalctl -u luckyred-api -f

# Bot 日誌
sudo journalctl -u luckyred-bot -f
```

### 測試功能
1. 在 Telegram 中發送 `/start` 給 Bot
2. 訪問 Miniapp 域名
3. 檢查 API 健康狀態：`curl http://localhost:8080/health`

## 更新部署

### 快速更新
```bash
sudo bash deploy/scripts/quick-update.sh
```

### 手動更新
```bash
# 更新代碼
cd /opt/luckyred
git pull  # 或上傳新代碼

# 更新依賴
cd api && source .venv/bin/activate && pip install -r requirements.txt
cd ../bot && source .venv/bin/activate && pip install -r requirements.txt

# 重啟服務
sudo systemctl restart luckyred-api
sudo systemctl restart luckyred-bot

# 更新前端
cd ../frontend && npm install && npm run build
sudo systemctl reload nginx
```

## 常見問題

### 服務無法啟動
```bash
# 查看詳細日誌
sudo journalctl -u luckyred-api -n 50
sudo journalctl -u luckyred-bot -n 50
```

### 數據庫連接失敗
```bash
# 測試連接
psql -U luckyred -d luckyred -h localhost

# 檢查 PostgreSQL 狀態
sudo systemctl status postgresql
```

### Bot 無響應
```bash
# 檢查 Token
grep BOT_TOKEN /opt/luckyred/.env

# 測試 Bot API
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

## 完整文檔

詳細部署說明請參考：
- `DEPLOYMENT_GUIDE.md` - 完整部署指南
- `deploy/checklist.md` - 部署檢查清單
