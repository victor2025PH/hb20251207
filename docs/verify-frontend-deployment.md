# 验证前端部署指南

## 问题症状
- 代码已提交到 GitHub
- GitHub Actions 部署成功
- 但浏览器中看不到任何变化
- 没有看到版本标识条
- 没有看到控制台日志

## 可能的原因

1. **Nginx 没有重新加载** - 构建了新文件，但 Nginx 还在使用旧文件
2. **浏览器缓存** - 浏览器缓存了旧的 JavaScript 文件
3. **构建产物路径不正确** - Nginx 配置指向的路径与构建输出路径不一致

## 验证步骤

### 1. 检查构建产物是否存在

SSH 到服务器，检查构建产物：

```bash
ssh ubuntu@165.154.254.99
cd /opt/luckyred/frontend
ls -lh dist/
```

应该看到：
- `index.html`
- `assets/` 目录（包含 JavaScript 和 CSS 文件）
- 文件时间戳应该是最近的（刚刚构建的）

### 2. 检查 Nginx 配置

```bash
sudo cat /etc/nginx/sites-available/mini.usdt2026.cc.conf | grep root
```

应该显示：
```
root /opt/luckyred/frontend/dist;
```

### 3. 检查 Nginx 是否指向正确的目录

```bash
sudo nginx -T | grep -A 5 "server_name mini.usdt2026.cc"
```

### 4. 手动重新加载 Nginx

```bash
sudo nginx -t  # 检查配置是否正确
sudo systemctl reload nginx  # 重新加载 Nginx
```

### 5. 检查文件权限

```bash
ls -la /opt/luckyred/frontend/dist/
```

确保文件可读。

### 6. 清除浏览器缓存

在浏览器中：
1. 打开开发者工具（F12）
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"（Empty Cache and Hard Reload）

或者在 Telegram 中：
1. 关闭 MiniApp
2. 清除 Telegram 缓存（如果可能）
3. 重新打开 MiniApp

### 7. 验证新代码是否已部署

在浏览器控制台（F12）中，检查：

```javascript
// 检查是否有版本标识
document.querySelector('.bg-green-500\\/20')

// 或者直接查看页面源码
document.body.innerHTML.includes('v2.0.0')
```

## 快速修复命令

如果构建产物存在但 Nginx 没有更新，执行：

```bash
# SSH 到服务器
ssh ubuntu@165.154.254.99

# 进入项目目录
cd /opt/luckyred

# 拉取最新代码（如果需要）
git pull origin main

# 进入前端目录
cd frontend

# 重新构建
npm run build

# 检查构建产物
ls -lh dist/

# 重新加载 Nginx
sudo nginx -t && sudo systemctl reload nginx

# 验证
curl -I https://mini.usdt2026.cc
```

## 检查构建产物中的代码

如果想确认新代码是否在构建产物中：

```bash
# 在服务器上
grep -r "v2.0.0" /opt/luckyred/frontend/dist/
grep -r "ProfilePage 已更新" /opt/luckyred/frontend/dist/
```

如果找到，说明构建成功；如果找不到，说明代码没有正确构建。

## 如果仍然看不到变化

1. **检查 GitHub Actions 日志** - 确认构建是否真的成功
2. **检查服务器上的实际文件** - 确认文件是否真的更新了
3. **检查 Nginx 错误日志** - `sudo tail -f /var/log/nginx/error.log`
4. **尝试直接访问构建产物** - 检查文件是否真的存在且可读

