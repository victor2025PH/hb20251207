# 部署檢查工具使用說明

## 文件說明

### Windows 本地腳本（不需要上傳）
這些腳本在本地 Windows 機器上運行，通過 SSH 遠程執行命令：

1. **`auto-check-deployment.bat`** - 全自動部署檢查
   - 直接在本地運行，通過 SSH 執行檢查命令
   - 不需要上傳到服務器

2. **`diagnose-and-fix.bat`** - 診斷和修復建議
   - 在本地運行，分析服務器狀態
   - 提供修復建議

3. **`fix-services.bat`** - 服務修復腳本
   - 在本地運行，執行診斷和提供修復步驟

4. **`auto-upload-and-check.bat`** - 自動上傳並檢查
   - 自動上傳檢查腳本到服務器
   - 然後執行檢查

5. **`upload-all-scripts.bat`** - 上傳所有腳本
   - 將必要的腳本上傳到服務器

### 服務器端腳本（需要上傳）
這些腳本需要在服務器上執行：

1. **`check_deployment.sh`** - 完整的部署檢查腳本
   - 需要上傳到服務器：`/opt/luckyred/check_deployment.sh`
   - 在服務器上執行：`bash /opt/luckyred/check_deployment.sh`

## 使用方法

### 方法 1：直接使用本地腳本（推薦）

最簡單的方式，不需要上傳任何文件：

```bash
# 全自動檢查
.\auto-check-deployment.bat

# 或診斷問題
.\diagnose-and-fix.bat
```

### 方法 2：先上傳再檢查

如果需要使用服務器上的完整檢查腳本：

```bash
# 步驟 1: 上傳檢查腳本
.\upload-all-scripts.bat

# 步驟 2: 自動上傳並檢查
.\auto-upload-and-check.bat

# 或手動在服務器上執行
ssh ubuntu@165.154.254.99 "bash /opt/luckyred/check_deployment.sh"
```

### 方法 3：手動上傳和執行

```bash
# 上傳腳本
scp check_deployment.sh ubuntu@usdt2026.cc:/opt/luckyred/

# SSH 到服務器執行
ssh ubuntu@165.154.254.99
cd /opt/luckyred
bash check_deployment.sh
```

## 快速開始

**推薦流程：**

1. **首次使用** - 執行自動上傳和檢查：
   ```bash
   .\auto-upload-and-check.bat
   ```

2. **日常檢查** - 直接使用本地腳本：
   ```bash
   .\auto-check-deployment.bat
   ```

3. **診斷問題** - 使用診斷腳本：
   ```bash
   .\diagnose-and-fix.bat
   ```

## 注意事項

- 所有 `.bat` 文件在本地 Windows 運行
- `check_deployment.sh` 需要上傳到服務器（Linux）運行
- 確保 SSH 連接正常，可能需要輸入密碼
- 建議配置 SSH 密鑰以避免每次輸入密碼

## 配置 SSH 密鑰（可選）

如果不想每次輸入密碼：

```bash
# 生成 SSH 密鑰（如果還沒有）
ssh-keygen -t ed25519

# 複製公鑰到服務器
ssh-copy-id ubuntu@usdt2026.cc
```

