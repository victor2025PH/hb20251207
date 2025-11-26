#!/bin/bash
# 部署檢查腳本

echo "=== 1. 檢查服務狀態 ==="
sudo systemctl status luckyred-api --no-pager -l | head -20
echo ""
sudo systemctl status luckyred-bot --no-pager -l | head -20
echo ""

echo "=== 2. 查看API服務錯誤日誌 ==="
sudo journalctl -u luckyred-api -n 50 --no-pager | tail -30
echo ""

echo "=== 3. 檢查環境變量文件 ==="
if [ -f /opt/luckyred/.env ]; then
    echo "✅ .env文件存在"
    echo "環境變量鍵（隱藏敏感值）:"
    cat /opt/luckyred/.env | grep -v '^#' | grep -v '^$' | cut -d'=' -f1 | sort
else
    echo "❌ .env文件不存在！"
fi
echo ""

echo "=== 4. 檢查API目錄結構 ==="
ls -la /opt/luckyred/api/ | head -15
echo ""

echo "=== 5. 檢查虛擬環境 ==="
if [ -d /opt/luckyred/api/.venv ]; then
    echo "✅ 虛擬環境存在"
    ls -la /opt/luckyred/api/.venv/bin/ | grep -E '(python|uvicorn|pip)' | head -5
else
    echo "❌ 虛擬環境不存在！"
fi
echo ""

echo "=== 6. 測試手動啟動API ==="
cd /opt/luckyred/api
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "Python版本:"
    python --version
    echo ""
    echo "測試導入main模塊:"
    python -c "from main import app; print('✅ API模塊導入成功')" 2>&1
else
    echo "❌ 無法激活虛擬環境"
fi
echo ""

echo "=== 7. 檢查數據庫連接 ==="
if [ -f /opt/luckyred/.env ]; then
    source /opt/luckyred/.env 2>/dev/null
    if [ -n "$DATABASE_URL" ]; then
        echo "數據庫URL已設置（隱藏密碼）:"
        echo "$DATABASE_URL" | sed 's/:[^@]*@/:***@/'
    else
        echo "❌ DATABASE_URL未設置"
    fi
fi
echo ""

echo "=== 8. 檢查Nginx狀態 ==="
sudo systemctl status nginx --no-pager | head -10
echo ""
sudo nginx -t
echo ""

echo "=== 9. 檢查端口監聽 ==="
sudo netstat -tlnp | grep -E ':(80|443|8080)' || echo "未發現監聽端口"
echo ""

echo "=== 10. 檢查前端文件 ==="
if [ -d /opt/luckyred/frontend/dist ]; then
    echo "✅ 前端dist目錄存在"
    ls -la /opt/luckyred/frontend/dist/ | head -10
else
    echo "❌ 前端dist目錄不存在"
fi
echo ""

echo "=== 11. 檢查文件權限 ==="
ls -ld /opt/luckyred
ls -ld /opt/luckyred/api
ls -ld /opt/luckyred/.env
echo ""

echo "=== 檢查完成 ==="


