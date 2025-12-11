# 手动触发部署指南

## 问题
代码已推送到 GitHub，但部署失败（因为之前的 TypeScript 编译错误）。现在错误已修复，需要重新触发部署。

## 解决方案

### 方法 1: 手动触发 GitHub Actions（推荐）

1. 打开 GitHub 仓库：https://github.com/victor2025PH/hb20251207
2. 点击 **Actions** 标签
3. 在左侧选择 **Deploy to Production** workflow
4. 点击右上角的 **Run workflow** 按钮
5. 选择 **main** 分支
6. 点击 **Run workflow** 按钮

### 方法 2: 推送一个空提交触发自动部署

```bash
git commit --allow-empty -m "trigger: 重新触发部署"
git push
```

### 方法 3: 在服务器上手动部署

如果 GitHub Actions 仍然失败，可以在服务器上手动部署：

```bash
# SSH 到服务器
ssh ubuntu@your-server-ip

# 进入项目目录
cd /opt/luckyred

# 拉取最新代码
git pull origin main

# 进入前端目录
cd frontend

# 安装依赖（如果需要）
npm install

# 构建前端
npm run build

# 返回项目根目录
cd ..

# 重启服务
sudo systemctl restart luckyred-api
sudo systemctl restart luckyred-bot
```

## 验证部署

1. 检查 GitHub Actions 状态：
   - 打开 https://github.com/victor2025PH/hb20251207/actions
   - 查看最新的 workflow run 是否成功

2. 检查服务器上的代码：
   ```bash
   ssh ubuntu@your-server-ip
   cd /opt/luckyred
   git log --oneline -1
   # 应该显示最新的提交：ef40390
   ```

3. 检查前端构建：
   ```bash
   ls -lh /opt/luckyred/frontend/dist/
   # 应该看到构建后的文件
   ```

4. 测试应用：
   - 在 Telegram 中打开 MiniApp
   - 测试导航按钮是否正常工作

## 常见问题

### 问题 1: GitHub Actions 仍然失败

**原因**: 可能是其他错误（不是 TypeScript 错误）

**解决**: 
1. 查看 GitHub Actions 日志，找到具体的错误信息
2. 根据错误信息修复问题
3. 重新触发部署

### 问题 2: 代码已更新但前端没有变化

**原因**: 浏览器缓存或 Telegram 缓存

**解决**:
1. 清除浏览器缓存
2. 在 Telegram 中强制刷新（关闭并重新打开 MiniApp）
3. 或者等待几分钟让缓存过期

### 问题 3: 服务重启失败

**原因**: 服务配置问题

**解决**:
```bash
# 检查服务状态
sudo systemctl status luckyred-api
sudo systemctl status luckyred-bot

# 查看服务日志
sudo journalctl -u luckyred-api -n 50
sudo journalctl -u luckyred-bot -n 50
```

