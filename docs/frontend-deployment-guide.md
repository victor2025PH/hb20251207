# 前端部署指南

## 📋 概述

前端 MiniApp 需要单独构建和部署。GitHub Actions 现在会自动构建前端，但也可以手动构建。

## 🚀 自动部署（推荐）

GitHub Actions 现在会在每次 push 到 `main` 分支时自动：
1. 拉取最新代码
2. 安装前端依赖（如果需要）
3. 构建前端（`npm run build`）
4. 重启后端服务

## 🔧 手动部署

如果需要手动构建和部署前端：

```bash
# SSH 到服务器
ssh ubuntu@165.154.254.99

# 进入项目目录
cd /home/ubuntu/hbgm001

# 拉取最新代码
git pull origin main

# 进入前端目录
cd frontend

# 安装依赖（如果需要）
npm install

# 构建前端
npm run build

# 检查构建结果
ls -la dist/
```

## 📁 目录结构

- **源代码**: `/home/ubuntu/hbgm001/frontend/`
- **构建输出**: `/home/ubuntu/hbgm001/frontend/dist/`
- **Nginx 配置**: `/etc/nginx/sites-available/mini.usdt2026.cc.conf`
- **Nginx 根目录**: `/home/ubuntu/hbgm001/frontend/dist`

## ⚙️ Nginx 配置

Nginx 配置指向：
```nginx
root /home/ubuntu/hbgm001/frontend/dist;
index index.html;
```

更新 Nginx 配置：
```bash
sudo cp /home/ubuntu/hbgm001/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf
sudo ln -sf /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-enabled/mini.usdt2026.cc.conf
sudo nginx -t
sudo systemctl reload nginx
```

## 🔍 验证部署

1. **检查构建文件**:
   ```bash
   ls -lh /home/ubuntu/hbgm001/frontend/dist/
   ```

2. **检查 Nginx 配置**:
   ```bash
   sudo nginx -t
   ```

3. **测试访问**:
   ```bash
   curl -I http://mini.usdt2026.cc
   ```

4. **清除浏览器缓存**:
   - 在 Telegram 中打开 MiniApp
   - 强制刷新（Ctrl+F5 或 Cmd+Shift+R）
   - 或者清除 Telegram 缓存

## 🐛 常见问题

### 1. 前端没有更新

**原因**: 浏览器缓存或 Telegram 缓存

**解决方案**:
- 清除浏览器缓存
- 在 Telegram 中重新打开 MiniApp
- 检查 `dist/` 目录的修改时间

### 2. 构建失败

**原因**: 依赖问题或代码错误

**解决方案**:
```bash
cd /home/ubuntu/hbgm001/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 3. Nginx 404 错误

**原因**: Nginx 配置路径不正确

**解决方案**:
```bash
# 检查 Nginx 配置
sudo nginx -T | grep -A 5 "server_name mini.usdt2026.cc"

# 更新配置
sudo cp /home/ubuntu/hbgm001/deploy/nginx/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf
sudo nginx -t
sudo systemctl reload nginx
```

## 📝 构建时间戳

构建后的文件会包含时间戳，可以通过以下方式检查：

```bash
# 检查 index.html 的修改时间
ls -lh /home/ubuntu/hbgm001/frontend/dist/index.html

# 检查最新的 JS 文件
ls -lt /home/ubuntu/hbgm001/frontend/dist/assets/ | head -5
```

## ✅ 部署检查清单

- [ ] 代码已拉取到最新版本
- [ ] 前端依赖已安装
- [ ] 前端构建成功（`npm run build`）
- [ ] `dist/` 目录存在且包含文件
- [ ] Nginx 配置指向正确的路径
- [ ] Nginx 配置测试通过
- [ ] Nginx 已重新加载
- [ ] 可以访问前端页面
- [ ] 清除浏览器/Telegram 缓存后验证

---

**最后更新**: 2025-12-09

