# 检查机器人服务状态

## 快速检查命令

### 1. 检查服务状态

```bash
ssh ubuntu@165.154.254.99
sudo systemctl status luckyred-bot
```

### 2. 查看最近日志

```bash
sudo journalctl -u luckyred-bot -n 50 --no-pager
```

### 3. 实时查看日志

```bash
sudo journalctl -u luckyred-bot -f
```

### 4. 检查服务是否在运行

```bash
ps aux | grep python | grep bot
```

### 5. 重启服务

```bash
sudo systemctl restart luckyred-bot
sudo systemctl status luckyred-bot
```

## 常见问题

### 服务未运行
如果服务状态显示 `inactive` 或 `failed`：

```bash
# 查看详细错误
sudo journalctl -u luckyred-bot -n 100 --no-pager

# 尝试启动
sudo systemctl start luckyred-bot

# 检查启动错误
sudo systemctl status luckyred-bot
```

### 服务运行但无响应
如果服务状态显示 `active` 但没有响应：

```bash
# 检查进程
ps aux | grep bot

# 查看实时日志
sudo journalctl -u luckyred-bot -f

# 重启服务
sudo systemctl restart luckyred-bot
```

### 检查配置文件
```bash
# 检查服务文件
cat /etc/systemd/system/luckyred-bot.service

# 检查环境变量
sudo systemctl show luckyred-bot | grep Environment
```

