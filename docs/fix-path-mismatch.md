# 修复路径不匹配问题

## 问题
- 部署脚本在 `/opt/luckyred` 构建前端
- 但 Nginx 配置指向 `/home/ubuntu/hbgm001/frontend/dist`
- 导致构建的文件无法被 Nginx 提供

## 快速修复

### 方法 1: 在正确的位置重新构建（推荐）

```bash
ssh ubuntu@165.154.254.99
cd /home/ubuntu/hbgm001/frontend
npm run build
sudo systemctl reload nginx
```

### 方法 2: 复制构建产物到正确位置

```bash
ssh ubuntu@165.154.254.99

# 确保目标目录存在
mkdir -p /home/ubuntu/hbgm001/frontend/dist

# 复制构建产物（如果已经在 /opt/luckyred 构建了）
cp -r /opt/luckyred/frontend/dist/* /home/ubuntu/hbgm001/frontend/dist/

# 重新加载 Nginx
sudo systemctl reload nginx
```

### 方法 3: 检查并修复 Nginx 配置

如果你想使用 `/opt/luckyred` 作为项目目录，需要修改 Nginx 配置：

```bash
ssh ubuntu@165.154.254.99
sudo nano /etc/nginx/sites-available/mini.usdt2026.cc.conf
```

将 `root` 改为：
```nginx
root /opt/luckyred/frontend/dist;
```

然后：
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 验证

构建完成后，验证文件是否在正确位置：

```bash
# 检查构建产物
ls -lh /home/ubuntu/hbgm001/frontend/dist/

# 检查 Nginx 配置
sudo nginx -T | grep "root.*frontend/dist"

# 应该显示：
# root /home/ubuntu/hbgm001/frontend/dist;
```

## 下一步

修复后，强制刷新浏览器（Ctrl+Shift+R），应该能看到：
- 绿色的版本标识条
- 控制台中的版本日志
- 按钮点击日志

