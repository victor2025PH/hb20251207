# 修复 502 Bad Gateway 错误

## 问题诊断

从控制台日志看到：
- `502 Bad Gateway` 错误
- Nginx 无法连接到后端 FastAPI (127.0.0.1:8080)
- WebSocket 连接失败

## 快速诊断命令

SSH 到服务器后，按顺序运行以下命令：

### 1. 检查后端服务是否运行

```bash
# 检查 systemd 服务状态
sudo systemctl status luckyred-api

# 如果服务不存在，检查是否有进程在运行
ps aux | grep -E "uvicorn|main:app|api" | grep -v grep

# 检查端口 8080 是否被监听
sudo netstat -tlnp | grep 8080
# 或者使用 ss
sudo ss -tlnp | grep 8080
```

### 2. 检查服务日志

```bash
# 如果服务存在，查看日志
sudo journalctl -u luckyred-api -n 100 --no-pager

# 查看最近的错误
sudo journalctl -u luckyred-api --since "10 minutes ago" | grep -i error
```

### 3. 检查 Nginx 配置

```bash
# 检查 Nginx 配置是否正确
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

## 修复步骤

### 方案 1: 重启后端服务

```bash
# 如果服务存在
sudo systemctl restart luckyred-api
sudo systemctl status luckyred-api

# 等待几秒后检查
sleep 3
curl http://127.0.0.1:8080/api/v1/health || echo "服务未响应"
```

### 方案 2: 如果服务不存在，手动启动

```bash
# 进入项目目录
cd /home/ubuntu/hbgm001

# 激活虚拟环境
source api/.venv/bin/activate

# 检查服务文件是否存在
ls -la /etc/systemd/system/luckyred-api.service

# 如果不存在，创建服务文件
sudo cp deploy/systemd/luckyred-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable luckyred-api
sudo systemctl start luckyred-api
sudo systemctl status luckyred-api
```

### 方案 3: 如果服务启动失败，查看详细错误

```bash
# 查看服务状态详情
sudo systemctl status luckyred-api -l --no-pager

# 查看完整日志
sudo journalctl -u luckyred-api -n 200 --no-pager

# 尝试手动启动（查看实时错误）
cd /home/ubuntu/hbgm001
source api/.venv/bin/activate
cd api
python3 -m uvicorn main:app --host 127.0.0.1 --port 8080
```

### 方案 4: 检查端口占用

```bash
# 检查是否有其他进程占用 8080 端口
sudo lsof -i :8080

# 如果有，杀死进程
sudo kill -9 <PID>

# 然后重启服务
sudo systemctl restart luckyred-api
```

### 方案 5: 检查数据库连接

```bash
# 检查 PostgreSQL 是否运行
sudo systemctl status postgresql

# 检查数据库连接配置
cd /home/ubuntu/hbgm001
cat shared/config/.env | grep -i database
```

## 一键诊断脚本

在服务器上运行：

```bash
#!/bin/bash
echo "=== 诊断 502 错误 ==="
echo ""

echo "1. 检查服务状态..."
sudo systemctl status luckyred-api --no-pager | head -20

echo ""
echo "2. 检查端口监听..."
sudo ss -tlnp | grep 8080 || echo "端口 8080 未被监听"

echo ""
echo "3. 检查进程..."
ps aux | grep -E "uvicorn|main:app" | grep -v grep || echo "没有找到 API 进程"

echo ""
echo "4. 检查服务日志（最近 20 行）..."
sudo journalctl -u luckyred-api -n 20 --no-pager

echo ""
echo "5. 测试本地连接..."
curl -s http://127.0.0.1:8080/api/v1/health || echo "❌ 本地连接失败"

echo ""
echo "6. 检查 Nginx 错误日志（最近 10 行）..."
sudo tail -10 /var/log/nginx/error.log
```

## 常见问题

### 问题 1: 服务文件路径错误

**症状**: `203/EXEC` 错误

**解决**: 检查服务文件中的路径是否正确

```bash
sudo cat /etc/systemd/system/luckyred-api.service
# 确保 WorkingDirectory 和 ExecStart 路径正确
```

### 问题 2: 虚拟环境路径错误

**症状**: `ModuleNotFoundError` 或找不到 uvicorn

**解决**: 检查虚拟环境路径

```bash
# 检查虚拟环境是否存在
ls -la /home/ubuntu/hbgm001/api/.venv/bin/uvicorn

# 如果不存在，重新创建
cd /home/ubuntu/hbgm001/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 问题 3: 数据库连接失败

**症状**: 日志显示数据库连接错误

**解决**: 检查数据库配置和连接

```bash
# 检查 PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"
```

### 问题 4: 权限问题

**症状**: 权限被拒绝错误

**解决**: 检查文件权限

```bash
# 确保服务用户有权限
sudo chown -R ubuntu:ubuntu /home/ubuntu/hbgm001
# 或者根据服务文件中的 User 设置权限
```

## 验证修复

修复后，在浏览器控制台应该看到：

1. ✅ API 请求成功（200 状态码）
2. ✅ WebSocket 连接成功
3. ✅ 页面可以正常加载数据

测试命令：

```bash
# 在服务器上测试
curl http://127.0.0.1:8080/api/v1/health

# 在浏览器控制台测试
fetch('/api/v1/health').then(r => r.json()).then(console.log)
```

