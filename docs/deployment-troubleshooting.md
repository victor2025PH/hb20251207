# 部署故障排查指南

## 🔍 快速排查步骤

### 1. 检查 GitHub Secrets 配置

确保以下 Secrets 已正确配置：
- `SERVER_HOST` - 服务器 IP 地址
- `SERVER_USER` - SSH 用户名（通常是 `ubuntu`）
- `SERVER_SSH_KEY` - SSH 私钥（完整内容，包括 `-----BEGIN` 和 `-----END`）
- `SSH_PORT` - SSH 端口（可选，默认 22）

### 2. 检查服务器上的路径

```bash
# SSH 连接到服务器
ssh ubuntu@your-server-ip

# 检查项目目录
ls -la /opt/luckyred

# 检查服务状态
sudo systemctl status luckyred-api

# 检查服务是否存在
systemctl list-unit-files | grep luckyred
```

### 3. 查看工作流日志

在 GitHub Actions 页面：
1. 点击失败的工作流运行
2. 展开 "Deploy to Server" 步骤
3. 查看详细的错误信息

### 4. 常见错误及解决方案

#### 错误 1: SSH 连接失败
```
Permission denied (publickey)
```
**解决方案：**
- 检查 `SERVER_SSH_KEY` 是否正确
- 确保私钥包含完整的 BEGIN/END 标记
- 检查服务器上的 `~/.ssh/authorized_keys`

#### 错误 2: 项目目录不存在
```
❌ 错误: 无法进入项目目录: /opt/luckyred
```
**解决方案：**
```bash
# 在服务器上创建目录并克隆项目
sudo mkdir -p /opt/luckyred
sudo chown ubuntu:ubuntu /opt/luckyred
cd /opt/luckyred
git clone https://github.com/victor2025PH/hb20251207.git .
```

#### 错误 3: 服务不存在
```
❌ 错误: 找不到服务
```
**解决方案：**
```bash
# 检查服务是否存在
systemctl list-unit-files | grep luckyred

# 如果不存在，创建服务文件
sudo cp /opt/luckyred/deploy/systemd/luckyred-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable luckyred-api
```

#### 错误 4: Git 操作失败
```
❌ Git fetch 失败
```
**解决方案：**
```bash
# 检查 Git 仓库状态
cd /opt/luckyred
git remote -v
git status

# 确保有正确的远程仓库
git remote set-url origin https://github.com/victor2025PH/hb20251207.git
```

#### 错误 5: 虚拟环境不存在
```
⚠️  虚拟环境不存在
```
**解决方案：**
```bash
# 创建虚拟环境
cd /opt/luckyred/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 错误 6: 服务重启失败
```
❌ 服务重启失败
```
**解决方案：**
```bash
# 查看服务日志
sudo journalctl -u luckyred-api -n 100

# 检查服务配置
sudo systemctl status luckyred-api

# 手动重启服务
sudo systemctl restart luckyred-api
```

---

## 📋 手动部署步骤（如果自动部署失败）

如果 GitHub Actions 持续失败，可以手动部署：

```bash
# 1. SSH 连接到服务器
ssh ubuntu@your-server-ip

# 2. 进入项目目录
cd /opt/luckyred

# 3. 拉取最新代码
git fetch origin main
git reset --hard origin/main

# 4. 激活虚拟环境
source api/.venv/bin/activate

# 5. 更新依赖（如果需要）
pip install -r api/requirements.txt

# 6. 构建前端（如果需要）
cd frontend
npm install
npm run build
cd ..

# 7. 重启服务
sudo systemctl restart luckyred-api

# 8. 检查服务状态
sudo systemctl status luckyred-api
```

---

## 🔧 验证部署

### 检查服务状态
```bash
sudo systemctl status luckyred-api
```

### 查看服务日志
```bash
# 实时监控
sudo journalctl -u luckyred-api -f

# 最近 100 行
sudo journalctl -u luckyred-api -n 100
```

### 测试 API
```bash
# 健康检查
curl http://localhost:8080/health

# 或从外部
curl https://your-domain.com/api/health
```

---

## 💡 提示

1. **查看详细日志**：GitHub Actions 日志会显示每个步骤的详细输出
2. **检查权限**：确保 SSH 用户有足够的权限执行部署命令
3. **检查网络**：确保服务器可以访问 GitHub
4. **检查服务配置**：确保 systemd 服务文件配置正确

