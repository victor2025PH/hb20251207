# ✅ 部署腳本已修復

## 修復的問題

1. **Python 命令字符串語法錯誤**
   - 修復前: `python -c "from shared.database.connection import init_db; init_db(); print('✓ 數據庫初始化成功')"`
   - 修復後: 使用變量存儲命令字符串

2. **啟動服務的命令格式錯誤**
   - 修復前: 使用 here-string (`@"..."@`) 導致解析錯誤
   - 修復後: 使用 `Join-Path` 和參數數組格式

3. **字符編碼問題**
   - 確保腳本使用 UTF-8 編碼保存

## 現在可以運行

```powershell
.\setup-and-deploy.ps1
```

或

```powershell
.\快速部署.bat
```

## 如果還有問題

### 問題 1: 字符編碼顯示亂碼
**解決方案**: 在 PowerShell 中設置編碼
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

### 問題 2: 執行策略錯誤
**解決方案**: 設置執行策略
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 問題 3: 虛擬環境激活失敗
**解決方案**: 手動激活
```powershell
cd api
.venv\Scripts\Activate.ps1
```

## 手動部署（如果腳本仍有問題）

參考 `DEPLOY_STATUS.md` 中的手動部署步驟。
