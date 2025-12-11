# 检查构建输出位置

## 问题
构建完成了，但文件时间戳没有更新，说明构建可能输出到了其他位置。

## 检查步骤

### 1. 确认当前工作目录

```bash
cd /home/ubuntu/hbgm001/frontend
pwd
# 应该显示: /home/ubuntu/hbgm001/frontend
```

### 2. 检查构建输出目录

```bash
# 检查 dist 目录的完整路径
ls -lah dist/

# 检查 dist 目录的绝对路径
realpath dist/

# 检查构建产物是否真的在 dist 目录
ls -lh dist/index.html
ls -lh dist/assets/ | head -5
```

### 3. 检查 vite.config.ts 的 outDir 配置

```bash
cd /home/ubuntu/hbgm001/frontend
cat vite.config.ts | grep outDir
```

应该显示：`outDir: 'dist'`

### 4. 重新构建并查看详细输出

```bash
cd /home/ubuntu/hbgm001/frontend

# 删除旧的构建产物
rm -rf dist/

# 重新构建
npm run build

# 立即检查文件时间戳
ls -lh dist/
```

### 5. 检查是否有多个 dist 目录

```bash
# 查找所有 dist 目录
find /home/ubuntu/hbgm001 -type d -name "dist" 2>/dev/null

# 查找所有 index.html
find /home/ubuntu/hbgm001 -name "index.html" 2>/dev/null
```

### 6. 验证构建产物内容

```bash
# 检查新代码是否在构建产物中
grep -r "v2.0.0" /home/ubuntu/hbgm001/frontend/dist/
grep -r "ProfilePage 已更新" /home/ubuntu/hbgm001/frontend/dist/
```

如果找到，说明构建成功；如果找不到，说明代码没有正确构建。

## 快速修复

如果构建输出到了错误的位置，执行：

```bash
cd /home/ubuntu/hbgm001/frontend

# 确保在正确的目录
pwd

# 删除旧构建
rm -rf dist/

# 重新构建
npm run build

# 检查文件时间戳（应该是刚刚的）
ls -lh dist/

# 检查文件内容（应该包含新代码）
grep "v2.0.0" dist/index.html || echo "未找到版本标识"

# 重新加载 Nginx
sudo systemctl reload nginx
```

## 如果还是不行

检查 Nginx 实际使用的文件：

```bash
# 检查 Nginx 配置中的 root 路径
sudo nginx -T | grep -A 2 "server_name mini.usdt2026.cc" | grep root

# 检查该路径下的文件
sudo ls -lh $(sudo nginx -T | grep -A 2 "server_name mini.usdt2026.cc" | grep root | awk '{print $2}' | tr -d ';')
```

