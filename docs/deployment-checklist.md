# 部署检查清单

## Phase 1: Nginx 配置部署

### 1.1 部署步骤

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001

# 1. 复制配置文件到服务器
sudo cp deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf

# 2. 创建软链接（如果不存在）
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf

# 3. 测试配置
sudo nginx -t

# 4. 如果配置正确，重新加载 Nginx
sudo systemctl reload nginx

# 5. 验证访问
curl -I https://admin.usdt2026.cc
```

### 1.2 验证清单

- [ ] Nginx 配置文件已复制到 `/etc/nginx/sites-available/`
- [ ] 软链接已创建到 `/etc/nginx/sites-enabled/`
- [ ] `nginx -t` 测试通过
- [ ] Nginx 已重新加载
- [ ] 访问 `https://admin.usdt2026.cc` 显示后台登录页
- [ ] API 代理正常工作（`/api/v1/admin/auth/login`）

---

## Phase 2: 后端 API 部署

### 2.1 代码更新

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001

# 1. 拉取最新代码
git pull origin main

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装/更新依赖（如果需要）
pip install -r requirements.txt
```

### 2.2 数据库迁移

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001

# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 运行数据库迁移
alembic upgrade head

# 3. 验证表已创建
# 连接到数据库检查 scheduled_redpacket_rains 表是否存在
```

### 2.3 重启服务

```bash
# 重启后端服务
sudo systemctl restart hbgm001-backend

# 检查服务状态
sudo systemctl status hbgm001-backend

# 查看日志
sudo journalctl -u hbgm001-backend -f
```

### 2.4 验证清单

- [ ] 代码已更新到最新版本
- [ ] 数据库迁移已执行（`scheduled_redpacket_rains` 表已创建）
- [ ] 后端服务已重启
- [ ] 服务状态正常（`systemctl status` 显示 `active (running)`）
- [ ] 日志无错误信息

---

## Phase 3: 前端部署

### 3.1 构建前端

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001/admin/frontend

# 1. 安装依赖（如果需要）
npm install

# 2. 构建生产版本
npm run build

# 3. 验证构建产物
ls -la dist/
```

### 3.2 验证清单

- [ ] 前端依赖已安装
- [ ] 构建成功（`npm run build` 无错误）
- [ ] `dist/` 目录存在且包含 `index.html`
- [ ] 访问 `https://admin.usdt2026.cc` 显示正确的后台界面

---

## Phase 4: 功能测试

### 4.1 红包退款功能测试

1. 登录后台管理面板
2. 进入"红包管理"页面
3. 选择一个未领取的红包
4. 点击"退款"按钮
5. 验证：
   - [ ] 退款成功提示
   - [ ] 红包状态变为"已退款"
   - [ ] 发送者余额已增加

### 4.2 推荐系统配置测试

1. 登录后台管理面板
2. 进入"邀请管理"页面
3. 找到"佣金配置"卡片
4. 修改佣金率（例如：一级5%，二级2%）
5. 点击"保存配置"
6. 验证：
   - [ ] 保存成功提示
   - [ ] 配置已更新

### 4.3 红包雨调度测试

1. 登录后台管理面板
2. 进入"红包管理"页面
3. 点击"调度红包雨"按钮
4. 填写表单：
   - 开始时间：未来某个时间
   - 总金额：100 USDT
   - 红包数量：10
   - 目标群组ID：留空（公开红包）
5. 点击"确定"
6. 验证：
   - [ ] 调度成功提示
   - [ ] 调度记录已创建（可在数据库中查看）

### 4.4 测试数据脚本

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001

# 激活虚拟环境
source .venv/bin/activate

# 运行测试数据脚本
python3 scripts/py/seed_referral_tree.py

# 验证：
# 1. 脚本执行成功
# 2. 在后台"邀请管理"页面可以查看推荐关系树
```

---

## 常见问题排查

### 问题1: Nginx 配置测试失败

```bash
# 检查语法错误
sudo nginx -t

# 查看详细错误信息
sudo nginx -T | grep -A 10 -B 10 "error"
```

### 问题2: 后端服务启动失败

```bash
# 查看详细日志
sudo journalctl -u hbgm001-backend -n 100

# 检查 Python 依赖
source .venv/bin/activate
pip list | grep -E "fastapi|uvicorn|sqlalchemy"
```

### 问题3: 数据库迁移失败

```bash
# 检查当前迁移版本
alembic current

# 查看迁移历史
alembic history

# 手动执行迁移（如果需要）
alembic upgrade head
```

### 问题4: 前端构建失败

```bash
# 清除缓存重新构建
cd admin/frontend
rm -rf node_modules dist
npm install
npm run build
```

---

## 回滚步骤

如果部署出现问题，可以按以下步骤回滚：

### 回滚 Nginx 配置

```bash
# 恢复之前的配置
sudo cp /etc/nginx/sites-available/admin.usdt2026.cc.conf.backup /etc/nginx/sites-available/admin.usdt2026.cc.conf
sudo nginx -t
sudo systemctl reload nginx
```

### 回滚代码

```bash
# 回滚到上一个版本
cd /home/ubuntu/hbgm001
git log --oneline -10  # 查看提交历史
git checkout <previous-commit-hash>
sudo systemctl restart hbgm001-backend
```

### 回滚数据库迁移

```bash
# 回滚到上一个迁移版本
alembic downgrade -1
```

---

**文档版本**: v1.0  
**最后更新**: 2025-01-XX

