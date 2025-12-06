# 🚀 部署下一步指南

## 當前狀態

部署腳本已準備好，現在可以開始執行部署。

## 執行部署

### 方法 1: 使用英文版本（推薦，避免編碼問題）

```powershell
.\setup-and-deploy-fixed.ps1
```

### 方法 2: 使用中文版本（如果 PowerShell 編碼設置正確）

```powershell
# 先設置編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001

# 然後運行
.\setup-and-deploy.ps1
```

### 方法 3: 使用批處理文件

雙擊 `快速部署.bat`

## 部署流程

腳本會自動執行以下步驟：

1. **檢查環境配置**
   - 檢查 `.env` 文件
   - 如果不存在，從 `.env.example` 創建
   - 提示配置必要的變量

2. **檢查 Python**
   - 驗證 Python 3.10+ 已安裝
   - 檢查是否在 PATH 中

3. **設置 API 環境**
   - 創建虛擬環境（如果不存在）
   - 安裝所有依賴包
   - 這可能需要幾分鐘

4. **設置 Bot 環境**
   - 創建虛擬環境（如果不存在）
   - 安裝所有依賴包

5. **初始化數據庫**
   - 連接數據庫
   - 創建所有必要的表

6. **提供啟動選項**
   - 詢問是否立即啟動服務
   - 或提供手動啟動指令

## 手動執行步驟（如果腳本有問題）

### 1. 配置環境變量
```powershell
# 如果 .env 不存在
Copy-Item .env.example .env
notepad .env
```

### 2. 設置 API 環境
```powershell
cd api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

### 3. 設置 Bot 環境
```powershell
cd bot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

### 4. 初始化數據庫
```powershell
cd api
.venv\Scripts\Activate.ps1
python -c "from shared.database.connection import init_db; init_db()"
deactivate
cd ..
```

### 5. 啟動服務

**API 服務器：**
```powershell
cd api
.venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

**Bot（新終端窗口）：**
```powershell
cd bot
.venv\Scripts\Activate.ps1
python main.py
```

**或使用快速啟動腳本：**
```powershell
.\start-services.ps1
```

## 驗證部署

### 檢查服務
- API: 訪問 http://localhost:8080/docs
- Bot: 在 Telegram 中發送 `/start` 命令

### 檢查日誌
查看終端窗口中的輸出，確認沒有錯誤。

## 常見問題

### 問題 1: 編碼錯誤
**解決方案**: 使用英文版本 `setup-and-deploy-fixed.ps1`

### 問題 2: 依賴安裝失敗
**解決方案**: 
- 檢查網絡連接
- 使用國內鏡像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

### 問題 3: 數據庫連接失敗
**解決方案**: 
- 檢查 `.env` 中的 `DATABASE_URL`
- 確保數據庫服務正在運行
- 檢查數據庫用戶權限

### 問題 4: 虛擬環境激活失敗
**解決方案**: 
- 檢查執行策略：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- 手動激活：`.venv\Scripts\Activate.ps1`

## 下一步

運行部署腳本後，系統會：
1. 自動完成所有設置
2. 詢問是否立即啟動服務
3. 提供手動啟動指令

準備好了嗎？運行：
```powershell
.\setup-and-deploy-fixed.ps1
```
