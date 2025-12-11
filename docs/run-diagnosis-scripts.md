# 在服务器上运行诊断脚本

## 快速步骤

### 1. 拉取最新代码

```bash
cd /home/ubuntu/hbgm001
git pull origin main
```

### 2. 运行诊断脚本

```bash
# 给脚本添加执行权限
chmod +x scripts/sh/diagnose-502.sh
chmod +x scripts/sh/fix-port-conflict.sh

# 运行诊断脚本
bash scripts/sh/diagnose-502.sh

# 如果发现端口冲突，运行修复脚本
bash scripts/sh/fix-port-conflict.sh
```

## 完整操作流程

### 步骤 1: 进入项目目录

```bash
cd /home/ubuntu/hbgm001
```

### 步骤 2: 拉取最新代码

```bash
git pull origin main
```

如果提示需要输入密码或认证，可能需要配置 SSH 密钥。

### 步骤 3: 检查脚本是否存在

```bash
ls -la scripts/sh/diagnose-502.sh
ls -la scripts/sh/fix-port-conflict.sh
```

### 步骤 4: 添加执行权限

```bash
chmod +x scripts/sh/*.sh
```

### 步骤 5: 运行诊断

```bash
bash scripts/sh/diagnose-502.sh
```

### 步骤 6: 根据诊断结果修复

如果诊断发现端口冲突：

```bash
bash scripts/sh/fix-port-conflict.sh
```

## 一键执行命令

复制以下命令到服务器终端，一次性执行：

```bash
cd /home/ubuntu/hbgm001 && \
git pull origin main && \
chmod +x scripts/sh/*.sh && \
echo "=== 运行诊断 ===" && \
bash scripts/sh/diagnose-502.sh
```

## 如果 git pull 失败

如果 `git pull` 失败，可以手动下载脚本：

```bash
# 创建脚本目录（如果不存在）
mkdir -p scripts/sh

# 下载诊断脚本（需要从 GitHub 获取）
# 或者直接从本地复制
```

## 验证修复

修复后，测试 API 连接：

```bash
# 测试本地连接
curl http://127.0.0.1:8080/api/v1/health

# 检查服务状态
sudo systemctl status luckyred-api

# 检查端口监听
sudo ss -tlnp | grep 8080
```

## 常见问题

### 问题 1: 脚本不存在

**错误**: `bash: scripts/sh/diagnose-502.sh: No such file or directory`

**解决**: 
```bash
# 确保在项目根目录
cd /home/ubuntu/hbgm001

# 检查文件是否存在
ls -la scripts/sh/

# 如果不存在，拉取最新代码
git pull origin main
```

### 问题 2: 权限被拒绝

**错误**: `Permission denied`

**解决**:
```bash
chmod +x scripts/sh/diagnose-502.sh
chmod +x scripts/sh/fix-port-conflict.sh
```

### 问题 3: Git 需要认证

**错误**: `Permission denied (publickey)` 或需要输入密码

**解决**: 使用 HTTPS 方式拉取（如果配置了）
```bash
git pull https://github.com/victor2025PH/hb20251207.git main
```

或者配置 SSH 密钥。

