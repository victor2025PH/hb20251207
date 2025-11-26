# 下一步操作指南

## 當前狀況
根據檢查結果，發現以下問題：
- ✅ `nginx.service` - 正常運行
- ❌ `luckyred-api.service` - 失敗（退出碼 1）
- ❌ `luckyred-bot.service` - 自動重啟但失敗（退出碼 1）

## 診斷步驟

### 1. 執行診斷腳本
```bash
.\diagnose-and-fix.bat
```
或
```bash
.\fix-services.bat
```

### 2. 手動檢查錯誤日誌
```bash
ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-api -n 50 --no-pager"
ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-bot -n 50 --no-pager"
```

## 常見問題和解決方案

### 問題 1: .env 文件不存在或配置錯誤

**檢查：**
```bash
ssh ubuntu@165.154.254.99 "test -f /opt/luckyred/.env && echo '存在' || echo '不存在'"
```

**修復：**
```bash
ssh ubuntu@165.154.254.99 "cat /opt/luckyred/.env"
```

確認以下變量已正確設置：
- `BOT_TOKEN` - Telegram Bot Token
- `DATABASE_URL` - PostgreSQL 數據庫連接字符串
- `SECRET_KEY` - JWT 密鑰
- `ADMIN_IDS` - 管理員 Telegram ID

### 問題 2: 虛擬環境不存在或依賴缺失

**檢查：**
```bash
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/api/.venv && echo 'API虛擬環境存在' || echo 'API虛擬環境不存在'"
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/bot/.venv && echo 'Bot虛擬環境存在' || echo 'Bot虛擬環境不存在'"
```

**修復：**
```bash
# 重新創建 API 虛擬環境
ssh ubuntu@165.154.254.99 "cd /opt/luckyred/api && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# 重新創建 Bot 虛擬環境
ssh ubuntu@165.154.254.99 "cd /opt/luckyred/bot && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
```

### 問題 3: 數據庫連接失敗

**檢查：**
```bash
ssh ubuntu@165.154.254.99 "sudo systemctl status postgresql"
ssh ubuntu@165.154.254.99 "sudo -u postgres psql -c 'SELECT version();'"
```

**修復：**
```bash
# 檢查數據庫是否存在
ssh ubuntu@165.154.254.99 "sudo -u postgres psql -c '\l' | grep luckyred"

# 如果不存在，創建數據庫
ssh ubuntu@165.154.254.99 "sudo -u postgres psql -c \"CREATE DATABASE luckyred OWNER luckyred;\""
```

### 問題 4: 模塊導入錯誤

**測試：**
```bash
# 測試 API 模塊
ssh ubuntu@165.154.254.99 "cd /opt/luckyred/api && source .venv/bin/activate && python -c 'from main import app; print(\"OK\")'"

# 測試 Bot 模塊
ssh ubuntu@165.154.254.99 "cd /opt/luckyred/bot && source .venv/bin/activate && python -c 'import main; print(\"OK\")'"
```

**修復：**
- 檢查 Python 依賴是否完整安裝
- 檢查代碼是否有語法錯誤
- 查看詳細錯誤信息

### 問題 5: 文件權限問題

**修復：**
```bash
ssh ubuntu@165.154.254.99 "sudo chown -R www-data:www-data /opt/luckyred"
ssh ubuntu@165.154.254.99 "sudo chmod -R 755 /opt/luckyred"
```

## 修復後重啟服務

```bash
ssh ubuntu@165.154.254.99 "sudo systemctl daemon-reload"
ssh ubuntu@165.154.254.99 "sudo systemctl restart luckyred-api luckyred-bot"
ssh ubuntu@165.154.254.99 "sudo systemctl status luckyred-api luckyred-bot"
```

## 驗證服務運行

```bash
# 檢查服務狀態
ssh ubuntu@165.154.254.99 "sudo systemctl status luckyred-api luckyred-bot nginx"

# 檢查端口監聽
ssh ubuntu@165.154.254.99 "sudo netstat -tlnp | grep -E ':(80|443|8080)'"

# 測試 API 健康檢查
curl http://localhost:8080/health
```

## 快速修復命令（一鍵執行）

如果確定問題，可以執行以下命令快速修復：

```bash
ssh ubuntu@165.154.254.99 << 'EOF'
# 確保目錄存在
sudo mkdir -p /opt/luckyred/{api,bot,frontend}

# 修復權限
sudo chown -R www-data:www-data /opt/luckyred

# 重新安裝 API 依賴
cd /opt/luckyred/api
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 重新安裝 Bot 依賴
cd /opt/luckyred/bot
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 重啟服務
sudo systemctl daemon-reload
sudo systemctl restart luckyred-api luckyred-bot
sudo systemctl status luckyred-api luckyred-bot
EOF
```

