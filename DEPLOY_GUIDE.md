# GitHub Actions 自动部署指南

本指南将帮助你设置 GitHub Actions 自动部署流程，实现代码推送到 `master` 分支时自动部署到服务器。

## 📋 目录

1. [前置要求](#前置要求)
2. [服务器端配置](#服务器端配置)
3. [GitHub 配置](#github-配置)
4. [部署流程](#部署流程)
5. [故障排查](#故障排查)

---

## 前置要求

### 服务器需要安装的软件

在开始之前，确保服务器已安装以下软件：

```bash
# 在服务器上执行
sudo apt update
sudo apt install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    postgresql \
    curl \
    wget
```

### 项目要求

- 项目已克隆到服务器：`/opt/luckyred`
- 已配置 systemd 服务：`luckyred-api`
- 已创建虚拟环境：`/opt/luckyred/api/.venv`
- 已配置 `.env` 文件：`/opt/luckyred/.env`

---

## 服务器端配置

### 步骤 1: 生成 SSH 密钥对

在服务器上生成一个专门用于 GitHub Actions 的 SSH 密钥对：

```bash
# 在服务器上执行
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy
```

**重要提示：**
- 不要设置密码（直接按 Enter）
- 密钥文件将保存在 `~/.ssh/github_actions_deploy`（私钥）和 `~/.ssh/github_actions_deploy.pub`（公钥）

### 步骤 2: 将公钥添加到 authorized_keys

将公钥添加到服务器的 `authorized_keys` 文件中：

```bash
# 在服务器上执行
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

**文件位置：**
- 公钥文件：`~/.ssh/github_actions_deploy.pub`
- 授权文件：`~/.ssh/authorized_keys`

### 步骤 3: 配置 Systemd 服务

如果还没有配置 systemd 服务，运行以下命令：

```bash
# 在服务器上执行
cd /opt/luckyred
sudo bash deploy/scripts/setup-systemd-service.sh
```

这将：
- 复制服务文件到 `/etc/systemd/system/`
- 创建虚拟环境（如果不存在）
- 设置正确的权限
- 启用并启动服务

### 步骤 4: 测试服务

确保服务正常运行：

```bash
# 在服务器上执行
sudo systemctl status luckyred-api
sudo journalctl -u luckyred-api -n 50
```

---

## GitHub 配置

### 步骤 1: 获取私钥

在服务器上查看私钥内容：

```bash
# 在服务器上执行
cat ~/.ssh/github_actions_deploy
```

**重要：** 复制整个输出，包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----` 之间的所有内容。

### 步骤 2: 添加 GitHub Secrets

1. 打开你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret** 添加以下三个 secrets：

#### Secret 1: `SSH_HOST`
- **Name:** `SSH_HOST`
- **Value:** 你的服务器 IP 地址或域名
  - 例如：`10.11.156.159` 或 `your-server.com`

#### Secret 2: `SSH_USERNAME`
- **Name:** `SSH_USERNAME`
- **Value:** SSH 用户名
  - 例如：`ubuntu` 或 `root`

#### Secret 3: `SSH_PRIVATE_KEY`
- **Name:** `SSH_PRIVATE_KEY`
- **Value:** 私钥的完整内容（从步骤 1 复制的整个内容）
  - 包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`

#### Secret 4: `SSH_PORT` (可选)
- **Name:** `SSH_PORT`
- **Value:** SSH 端口（默认 22）
  - 如果使用默认端口 22，可以省略此 secret

### 步骤 3: 验证配置

配置完成后，你的 GitHub Secrets 应该包含：
- ✅ `SSH_HOST`
- ✅ `SSH_USERNAME`
- ✅ `SSH_PRIVATE_KEY`
- ⚪ `SSH_PORT` (可选)

---

## 部署流程

### 自动部署

配置完成后，每次你推送代码到 `master` 分支时，GitHub Actions 会自动：

1. ✅ 连接到服务器
2. ✅ 进入项目目录 `/opt/luckyred`
3. ✅ 拉取最新代码 (`git pull`)
4. ✅ 更新 Python 依赖 (`pip install -r api/requirements.txt`)
5. ✅ 重启服务 (`sudo systemctl restart luckyred-api`)

### 手动触发部署

你也可以手动触发部署：

1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Deploy to Production** workflow
4. 点击 **Run workflow** 按钮

### 查看部署日志

1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择最新的 workflow run
4. 查看 **Deploy to Server** 步骤的日志

---

## 故障排查

### 问题 1: SSH 连接失败

**错误信息：** `Permission denied (publickey)`

**解决方案：**
1. 检查 `SSH_PRIVATE_KEY` secret 是否正确（包括完整的 BEGIN/END 标记）
2. 检查 `SSH_HOST` 和 `SSH_USERNAME` 是否正确
3. 在服务器上验证公钥是否正确添加到 `~/.ssh/authorized_keys`：
   ```bash
   cat ~/.ssh/authorized_keys | grep github-actions-deploy
   ```

### 问题 2: Git pull 失败

**错误信息：** `fatal: not a git repository`

**解决方案：**
1. 确保项目目录存在：`/opt/luckyred`
2. 确保该目录是一个 git 仓库
3. 检查 git 远程配置：
   ```bash
   cd /opt/luckyred
   git remote -v
   ```

### 问题 3: 服务重启失败

**错误信息：** `Failed to restart luckyred-api.service`

**解决方案：**
1. 检查服务文件是否存在：
   ```bash
   sudo systemctl status luckyred-api
   ```
2. 查看服务日志：
   ```bash
   sudo journalctl -u luckyred-api -n 100
   ```
3. 检查虚拟环境是否存在：
   ```bash
   ls -la /opt/luckyred/api/.venv
   ```
4. 检查 `.env` 文件是否存在：
   ```bash
   ls -la /opt/luckyred/.env
   ```

### 问题 4: 权限错误

**错误信息：** `Permission denied`

**解决方案：**
1. 确保部署用户有 sudo 权限（用于重启服务）
2. 配置 sudoers 文件（推荐使用 NOPASSWD）：
   ```bash
   # 在服务器上执行
   sudo visudo
   # 添加以下行（替换 username 为实际用户名）
   username ALL=(ALL) NOPASSWD: /bin/systemctl restart luckyred-api
   username ALL=(ALL) NOPASSWD: /bin/systemctl status luckyred-api
   ```

### 问题 5: 虚拟环境不存在

**错误信息：** `No such file or directory: .venv`

**解决方案：**
1. 手动创建虚拟环境：
   ```bash
   cd /opt/luckyred/api
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 安全建议

### 1. 限制 SSH 密钥权限

只允许该密钥执行必要的操作，可以创建一个专门的部署用户：

```bash
# 创建部署用户
sudo adduser deployer
sudo usermod -aG sudo deployer

# 切换到部署用户
su - deployer

# 生成密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy
```

### 2. 使用 SSH 配置文件

创建 `~/.ssh/config` 文件限制连接：

```
Host github-actions
    HostName your-server.com
    User deployer
    IdentityFile ~/.ssh/github_actions_deploy
    IdentitiesOnly yes
```

### 3. 定期轮换密钥

建议每 3-6 个月轮换一次 SSH 密钥。

---

## 常用命令

### 服务器端

```bash
# 查看服务状态
sudo systemctl status luckyred-api

# 查看服务日志
sudo journalctl -u luckyred-api -f

# 重启服务
sudo systemctl restart luckyred-api

# 查看最近的部署日志
sudo journalctl -u luckyred-api --since "10 minutes ago"
```

### GitHub Actions

```bash
# 查看 workflow 运行历史
# 在 GitHub 仓库的 Actions 标签中查看
```

---

## 下一步

配置完成后，你可以：

1. ✅ 推送代码到 `master` 分支测试自动部署
2. ✅ 在 GitHub Actions 中查看部署日志
3. ✅ 配置通知（Slack、Email 等）接收部署状态
4. ✅ 添加部署前测试步骤（单元测试、集成测试等）

---

## 支持

如果遇到问题，请检查：

1. GitHub Actions 日志
2. 服务器系统日志：`sudo journalctl -u luckyred-api`
3. 服务器 SSH 日志：`sudo tail -f /var/log/auth.log`

---

**最后更新：** 2025-01-07

