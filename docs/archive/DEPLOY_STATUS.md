# 📊 部署狀態檢查

## 快速檢查命令

### 檢查環境
```powershell
# 檢查虛擬環境
Test-Path api\.venv
Test-Path bot\.venv

# 檢查依賴
api\.venv\Scripts\python.exe -m pip list
bot\.venv\Scripts\python.exe -m pip list
```

### 手動完成部署

如果自動部署腳本未完全執行，可以手動執行以下步驟：

#### 1. 設置 API 環境
```powershell
cd api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

#### 2. 設置 Bot 環境
```powershell
cd bot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

#### 3. 初始化數據庫
```powershell
cd api
.venv\Scripts\Activate.ps1
python -c "from shared.database.connection import init_db; init_db()"
deactivate
cd ..
```

#### 4. 啟動服務
```powershell
# 方法 1: 使用啟動腳本
.\start-services.ps1

# 方法 2: 手動啟動
# 終端 1 - API
cd api
.venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# 終端 2 - Bot
cd bot
.venv\Scripts\Activate.ps1
python main.py
```

## 驗證部署

### 檢查服務
- API: http://localhost:8080/docs
- Bot: 在 Telegram 中發送 `/start`

### 檢查日誌
查看終端窗口中的輸出，確認沒有錯誤。

## 常見問題

### 問題 1: 虛擬環境創建失敗
**解決方案**: 確保 Python 已正確安裝並在 PATH 中
```powershell
python --version  # 應該顯示 3.10+
```

### 問題 2: 依賴安裝失敗
**解決方案**: 檢查網絡連接，或使用國內鏡像
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 問題 3: 數據庫連接失敗
**解決方案**: 檢查 `.env` 文件中的 `DATABASE_URL` 配置

### 問題 4: Bot 無法啟動
**解決方案**: 檢查 `.env` 文件中的 `BOT_TOKEN` 是否正確
