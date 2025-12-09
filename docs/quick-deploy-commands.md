# 快速部署命令

## 在服务器上执行以下命令

```bash
# ==========================================
# 1. 进入项目目录并拉取最新代码
# ==========================================
cd /home/ubuntu/hbgm001
git pull origin main

# ==========================================
# 2. 部署 Nginx 配置
# ==========================================
sudo cp deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf
sudo nginx -t
sudo systemctl reload nginx

# ==========================================
# 3. 激活虚拟环境并运行数据库迁移
# ==========================================
source .venv/bin/activate
python3 migrations/add_scheduled_redpacket_rain.py

# ==========================================
# 4. 重启后端服务
# ==========================================
sudo systemctl restart hbgm001-backend
sleep 3
sudo systemctl status hbgm001-backend --no-pager -l

# ==========================================
# 5. 构建前端
# ==========================================
cd admin/frontend
npm install
npm run build
cd ../..

# ==========================================
# 6. 验证部署（可选）
# ==========================================
curl -I https://admin.usdt2026.cc
echo "✅ 部署完成！"
```

## 一键执行（复制粘贴到服务器）

```bash
cd /home/ubuntu/hbgm001 && \
git pull origin main && \
sudo cp deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf && \
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf && \
sudo nginx -t && sudo systemctl reload nginx && \
source .venv/bin/activate && \
python3 migrations/add_scheduled_redpacket_rain.py && \
sudo systemctl restart hbgm001-backend && \
sleep 3 && \
cd admin/frontend && npm install && npm run build && cd ../.. && \
echo "✅ 部署完成！"
```

