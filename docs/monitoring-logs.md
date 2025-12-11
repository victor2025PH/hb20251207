# 日志监控命令

## ⚠️ 重要：首先检查服务名称和状态

在实际使用前，请先确认服务名称：

```bash
# 列出所有 luckyred 相关的服务
sudo systemctl list-units --all | grep -i lucky

# 或者查看所有服务
sudo systemctl list-units --type=service | grep -i lucky

# 列出所有服务文件（包括未运行的）
sudo systemctl list-unit-files | grep -i lucky

# 检查实际的项目目录（根据您的环境可能是 /opt/luckyred 或 /home/ubuntu/hbgm001）
ls -la /opt/luckyred 2>/dev/null || ls -la /home/ubuntu/hbgm001 2>/dev/null

# 如果 API 服务不存在，查找正在运行的 API 进程
ps aux | grep -E "uvicorn|main:app|api" | grep -v grep

# 查看进程的详细信息（包括启动命令）
ps auxf | grep python
```

## 🔍 如果 API 服务不存在，如何查看日志

**问题诊断**：如果 `luckyred-api.service` 服务不存在，API 可能是手动启动的。手动启动的进程的日志通常不会被 journald 捕获。

### 诊断步骤

```bash
# 1. 找到 API 进程ID
API_PID=$(ps aux | grep "uvicorn.*main:app\|uvicorn.*api.main" | grep -v grep | awk '{print $2}')
echo "API 进程ID: $API_PID"

# 2. 查看进程的详细信息（包括如何启动的）
ps -fp $API_PID

# 3. 查看进程的文件描述符（看输出重定向到哪里）
sudo ls -la /proc/$API_PID/fd/ | grep -E "0|1|2"

# 4. 检查进程是否在 screen/tmux 会话中
ps aux | grep $API_PID
```

### 查看日志的方法

```bash
# 方法1: 查看进程的标准输出/错误（如果进程仍在运行）
# 注意：如果进程不是通过 systemd 启动，journalctl 可能无法查看日志
sudo journalctl _PID=$API_PID -f
# 如果上面没有输出，说明进程的输出没有被 journald 捕获

# 方法2: 查看进程的输出重定向文件
# 检查是否有 nohup.out 或其他日志文件
find /home/ubuntu -name "nohup.out" -o -name "api*.log" 2>/dev/null | head -5
tail -f ~/nohup.out 2>/dev/null

# 方法3: 查看 screen 会话（如果使用了 screen）
screen -ls
# 如果找到会话，可以 attach 查看
screen -r <session_id>

# 方法4: 查看 tmux 会话（如果使用了 tmux）
tmux list-sessions
# 如果找到会话，可以 attach 查看
tmux attach -t <session_name>

# 方法5: 通过 strace 查看进程的系统调用（高级调试）
sudo strace -p $API_PID -e write -s 200 2>&1 | grep -v "+++ exited"

# 方法6: 查看应用自己的日志文件
find /home/ubuntu/hbgm001 -type f -name "*.log" -o -name "app.log" 2>/dev/null | head -5
tail -f /home/ubuntu/hbgm001/api/logs/*.log 2>/dev/null

# 方法7: 查看所有 Python 进程的日志（如果它们有日志）
sudo journalctl _COMM=python3 --since "1 hour ago" | grep -E "api|uvicorn|fastapi" | tail -50
```

### ⚠️ 如果找不到日志

如果进程是手动启动的且输出没有被重定向，日志可能已经丢失。建议：

1. **创建 systemd 服务**（推荐）：
```bash
# 复制服务文件
sudo cp /home/ubuntu/hbgm001/deploy/systemd/luckyred-api.service /etc/systemd/system/

# 修改服务文件中的路径（如果需要）
sudo nano /etc/systemd/system/luckyred-api.service

# 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl enable luckyred-api
sudo systemctl start luckyred-api

# 然后就可以正常查看日志了
sudo journalctl -u luckyred-api -f
```

2. **重新启动 API 并重定向输出**：
```bash
# 停止当前进程
kill $API_PID

# 重新启动并重定向输出到文件
cd /home/ubuntu/hbgm001
source .venv/bin/activate
nohup python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8080 --workers 4 > /tmp/api.log 2>&1 &

# 查看日志
tail -f /tmp/api.log
```

## 1. 监控 API 服务日志（实时）

```bash
# 实时查看 API 服务日志（最新 100 行）
sudo journalctl -u luckyred-api -f -n 100

# 查看最近 200 行日志
sudo journalctl -u luckyred-api -n 200

# 查看今天的日志
sudo journalctl -u luckyred-api --since today

# 查看最近 1 小时的日志
sudo journalctl -u luckyred-api --since "1 hour ago"
```

## 2. 监控 Bot 服务日志（实时）

```bash
# 实时查看 Bot 服务日志
sudo journalctl -u luckyred-bot -f -n 100

# 查看最近 200 行日志
sudo journalctl -u luckyred-bot -n 200

# 查看今天的日志
sudo journalctl -u luckyred-bot --since today
```

## 3. 同时监控多个服务

```bash
# 同时监控 API 和 Bot 服务
sudo journalctl -u luckyred-api -u luckyred-bot -f
```

## 4. 查看服务状态

```bash
# 查看 API 服务状态
sudo systemctl status luckyred-api

# 查看 Bot 服务状态
sudo systemctl status luckyred-bot

# 查看所有相关服务
sudo systemctl status luckyred-api luckyred-bot
```

## 5. 查看服务配置文件

```bash
# 查看 API 服务配置
sudo systemctl cat luckyred-api

# 查看 Bot 服务配置
sudo systemctl cat luckyred-bot
```

## 6. 搜索特定错误

```bash
# 搜索错误信息
sudo journalctl -u luckyred-api -p err

# 搜索包含特定关键词的日志
sudo journalctl -u luckyred-api | grep -i "error\|exception\|failed"

# 搜索最近的错误（最近 1000 行）
sudo journalctl -u luckyred-api -n 1000 | grep -i error
```

## 7. 查看系统日志（所有服务）

```bash
# 查看所有系统日志（实时）
sudo journalctl -f

# 查看最近的系统日志
sudo journalctl -n 100
```

## 8. GitHub Actions 部署日志

访问 GitHub 仓库页面查看：
```
https://github.com/victor2025PH/hb20251207/actions
```

或者使用 GitHub CLI（如果已安装）：
```bash
# 查看最近的 workflow runs
gh run list

# 查看最新的 run 日志
gh run view --log
```

## 9. 查看应用日志文件（如果有）

```bash
# 如果应用有日志文件（通常在 /opt/luckyred/logs 或 /var/log）
ls -lah /opt/luckyred/logs/

# 实时查看应用日志
tail -f /opt/luckyred/logs/*.log

# 查看最近的错误
grep -i error /opt/luckyred/logs/*.log | tail -20
```

## 10. 监控前端构建日志

```bash
# 进入前端目录
cd /opt/luckyred/frontend

# 查看构建输出（如果有构建日志）
tail -f dist/build.log 2>/dev/null || echo "No build log found"

# 手动构建并查看日志
npm run build 2>&1 | tee build.log
```

## 11. 一键查看所有关键信息

```bash
# 创建监控脚本
cat > /tmp/monitor-all.sh << 'EOF'
#!/bin/bash
echo "=== API Service Status ==="
sudo systemctl status luckyred-api --no-pager -l | head -10
echo ""
echo "=== Bot Service Status ==="
sudo systemctl status luckyred-bot --no-pager -l | head -10
echo ""
echo "=== Recent API Errors (last 20) ==="
sudo journalctl -u luckyred-api -p err -n 20 --no-pager
echo ""
echo "=== Recent Bot Errors (last 20) ==="
sudo journalctl -u luckyred-bot -p err -n 20 --no-pager
EOF

chmod +x /tmp/monitor-all.sh
/tmp/monitor-all.sh
```

## 12. SSH 远程监控（从本地）

如果您需要从本地机器监控服务器日志：

```bash
# SSH 连接到服务器并实时监控 API 日志
ssh user@your-server "sudo journalctl -u luckyred-api -f"

# 或者使用 SSH 执行一次性检查
ssh user@your-server "sudo systemctl status luckyred-api"
```

## 常用命令组合

### 监控 + 自动重启（如果服务崩溃）
```bash
# 监控日志，如果检测到严重错误，自动重启服务
sudo journalctl -u luckyred-api -f | while read line; do
  if echo "$line" | grep -q "Fatal\|Critical\|Cannot start"; then
    echo "Detected critical error, restarting service..."
    sudo systemctl restart luckyred-api
  fi
done
```

### 导出日志到文件
```bash
# 导出最近 1000 行日志
sudo journalctl -u luckyred-api -n 1000 > api-logs-$(date +%Y%m%d-%H%M%S).log

# 导出今天的日志
sudo journalctl -u luckyred-api --since today > api-logs-today.log
```

