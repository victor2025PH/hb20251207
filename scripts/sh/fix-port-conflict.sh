#!/bin/bash
# 修复端口冲突问题

set -e

echo "=========================================="
echo "  修复端口 8080 冲突"
echo "=========================================="
echo ""

# 检查是否有多个进程占用 8080
echo "[1/4] 检查端口 8080 的进程..."
PROCESSES=$(ps aux | grep "uvicorn.*8080" | grep -v grep || true)

if [ -n "$PROCESSES" ]; then
    echo "找到以下进程:"
    echo "$PROCESSES"
    echo ""
    
    # 检查是否有监听 0.0.0.0:8080 的进程（应该只监听 127.0.0.1）
    OLD_PROCESS=$(echo "$PROCESSES" | grep "0.0.0.0:8080" || true)
    
    if [ -n "$OLD_PROCESS" ]; then
        echo "[2/4] 发现旧进程监听 0.0.0.0:8080，需要停止..."
        OLD_PID=$(echo "$OLD_PROCESS" | awk '{print $2}')
        echo "旧进程 PID: $OLD_PID"
        
        # 停止旧进程
        echo "正在停止旧进程..."
        kill -TERM $OLD_PID 2>/dev/null || true
        sleep 2
        
        # 如果还在运行，强制杀死
        if ps -p $OLD_PID > /dev/null 2>&1; then
            echo "强制停止进程..."
            kill -9 $OLD_PID 2>/dev/null || true
        fi
        
        echo "✅ 旧进程已停止"
    else
        echo "[2/4] ✅ 没有发现冲突的旧进程"
    fi
else
    echo "[2/4] ⚠️ 没有找到 uvicorn 进程"
fi

echo ""

# 检查 systemd 服务状态
echo "[3/4] 检查 systemd 服务状态..."
if sudo systemctl is-active luckyred-api > /dev/null 2>&1; then
    echo "✅ 服务正在运行"
    echo "重启服务以确保使用正确的配置..."
    sudo systemctl restart luckyred-api
    sleep 3
    sudo systemctl status luckyred-api --no-pager | head -15
else
    echo "❌ 服务未运行，正在启动..."
    sudo systemctl start luckyred-api
    sleep 3
    sudo systemctl status luckyred-api --no-pager | head -15
fi

echo ""

# 验证端口监听
echo "[4/4] 验证端口监听状态..."
sleep 2
LISTENING=$(sudo ss -tlnp | grep ":8080" || true)

if [ -n "$LISTENING" ]; then
    echo "端口 8080 监听状态:"
    echo "$LISTENING"
    echo ""
    
    # 检查是否只监听 127.0.0.1
    if echo "$LISTENING" | grep -q "127.0.0.1:8080"; then
        echo "✅ 端口正确监听在 127.0.0.1:8080"
    else
        echo "⚠️ 端口监听配置可能不正确"
    fi
else
    echo "❌ 端口 8080 未被监听"
fi

echo ""
echo "=========================================="
echo "  修复完成"
echo "=========================================="
echo ""
echo "测试本地连接:"
curl -s http://127.0.0.1:8080/api/v1/health 2>/dev/null && echo "✅ 本地 API 连接成功" || echo "❌ 本地 API 连接失败"

