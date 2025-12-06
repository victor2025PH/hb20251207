# 手動檢查部署 - 命令列表

## 服務器信息
- **服務器地址**: `ubuntu@165.154.254.99`
- **部署路徑**: `/opt/luckyred`

## 步驟 1: 上傳檢查腳本

```bash
scp check_deployment.sh ubuntu@165.154.254.99:/opt/luckyred/check_deployment.sh
ssh ubuntu@165.154.254.99 "chmod +x /opt/luckyred/check_deployment.sh"
```

## 步驟 2: 執行完整檢查

```bash
ssh ubuntu@165.154.254.99 "bash /opt/luckyred/check_deployment.sh"
```

## 步驟 3: 查看服務狀態

```bash
# 查看所有服務狀態
ssh ubuntu@165.154.254.99 "sudo systemctl status luckyred-api luckyred-bot nginx"

# 查看單個服務狀態
ssh ubuntu@165.154.254.99 "sudo systemctl status luckyred-api --no-pager -l | head -20"
ssh ubuntu@165.154.254.99 "sudo systemctl status luckyred-bot --no-pager -l | head -20"
```

## 步驟 4: 查看錯誤日誌

```bash
# API 服務錯誤日誌
ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-api -n 50 --no-pager | tail -30"

# Bot 服務錯誤日誌
ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-bot -n 50 --no-pager | tail -30"
```

## 步驟 5: 檢查文件

```bash
# 檢查 .env 文件
ssh ubuntu@165.154.254.99 "test -f /opt/luckyred/.env && echo '[OK] .env存在' || echo '[ERROR] .env不存在'"

# 檢查虛擬環境
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/api/.venv && echo '[OK] API虛擬環境存在' || echo '[ERROR] API虛擬環境不存在'"
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/bot/.venv && echo '[OK] Bot虛擬環境存在' || echo '[ERROR] Bot虛擬環境不存在'"

# 檢查前端文件
ssh ubuntu@165.154.254.99 "test -d /opt/luckyred/frontend/dist && echo '[OK] 前端dist目錄存在' || echo '[ERROR] 前端dist目錄不存在'"
```

## 步驟 6: 檢查目錄結構

```bash
ssh ubuntu@165.154.254.99 "ls -la /opt/luckyred | head -15"
ssh ubuntu@165.154.254.99 "ls -la /opt/luckyred/api | head -10"
ssh ubuntu@165.154.254.99 "ls -la /opt/luckyred/bot | head -10"
```

## 步驟 7: 測試模塊導入

```bash
# 測試 API 模塊
ssh ubuntu@165.154.254.99 "cd /opt/luckyred/api && source .venv/bin/activate && python -c 'from main import app; print(\"API模塊導入成功\")'"

# 測試 Bot 模塊
ssh ubuntu@165.154.254.99 "cd /opt/luckyred/bot && source .venv/bin/activate && python -c 'import main; print(\"Bot模塊導入成功\")'"
```

## 步驟 8: 檢查 Nginx

```bash
# 檢查 Nginx 配置
ssh ubuntu@165.154.254.99 "sudo nginx -t"

# 檢查 Nginx 狀態
ssh ubuntu@165.154.254.99 "sudo systemctl status nginx --no-pager | head -10"

# 檢查端口監聽
ssh ubuntu@165.154.254.99 "sudo netstat -tlnp | grep -E ':(80|443|8080)'"
```

## 快速診斷命令

```bash
# 一鍵查看所有服務狀態和錯誤
ssh ubuntu@165.154.254.99 "echo '=== 服務狀態 ===' && sudo systemctl status luckyred-api --no-pager -l | head -15 && echo && sudo systemctl status luckyred-bot --no-pager -l | head -15 && echo && echo '=== 錯誤日誌 ===' && sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15 && echo && sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -15"
```

## 注意事項

1. 每次執行 SSH/SCP 命令時，如果需要輸入密碼，請在提示時輸入
2. 建議配置 SSH 密鑰以避免每次輸入密碼：
   ```bash
   ssh-keygen -t ed25519
   ssh-copy-id ubuntu@165.154.254.99
   ```
3. 如果某個步驟失敗，可以單獨重新執行該步驟
4. 查看完整日誌可以使用 `-f` 參數實時跟蹤：
   ```bash
   ssh ubuntu@165.154.254.99 "sudo journalctl -u luckyred-api -f"
   ```

