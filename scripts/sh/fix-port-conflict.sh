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
    
    # 停止所有非 systemd 管理的 uvicorn 进程
    echo "[2/4] 检查并停止所有旧进程..."
    
    # 获取 systemd 服务的主进程 PID
    SYSTEMD_PID=$(sudo systemctl show luckyred-api --property=MainPID --value 2>/dev/null || echo "")
    
    # 停止所有 uvicorn 进程（除了 systemd 管理的）
    STOPPED_COUNT=0
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            PID=$(echo "$line" | awk '{print $2}')
            # 跳过 systemd 管理的进程
            if [ -n "$SYSTEMD_PID" ] && [ "$PID" = "$SYSTEMD_PID" ]; then
                continue
            fi
            # 检查是否是 systemd 服务的子进程
            IS_SYSTEMD_CHILD=false
            if [ -n "$SYSTEMD_PID" ]; then
                # 检查进程的父进程是否是 systemd 服务的主进程
                PPID=$(ps -o ppid= -p $PID 2>/dev/null | tr -d ' ')
                if [ "$PPID" = "$SYSTEMD_PID" ]; then
                    IS_SYSTEMD_CHILD=true
                fi
            fi
            
            if [ "$IS_SYSTEMD_CHILD" = "false" ]; then
                echo "发现旧进程 PID: $PID，正在停止..."
                kill -TERM $PID 2>/dev/null || true
                STOPPED_COUNT=$((STOPPED_COUNT + 1))
            fi
        fi
    done <<< "$PROCESSES"
    
    # 等待进程停止
    if [ $STOPPED_COUNT -gt 0 ]; then
        echo "等待进程停止..."
        sleep 3
        
        # 强制杀死仍在运行的进程
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                PID=$(echo "$line" | awk '{print $2}')
                if [ -n "$SYSTEMD_PID" ] && [ "$PID" = "$SYSTEMD_PID" ]; then
                    continue
                fi
                if ps -p $PID > /dev/null 2>&1; then
                    echo "强制停止进程 PID: $PID..."
                    kill -9 $PID 2>/dev/null || true
                fi
            fi
        done <<< "$PROCESSES"
        
        echo "✅ 已停止 $STOPPED_COUNT 个旧进程"
    else
        echo "[2/4] ✅ 没有发现需要停止的旧进程"
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
echo "等待服务完全启动..."
sleep 5
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

