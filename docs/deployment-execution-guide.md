# 部署执行指南

## 概述

本文档提供完整的部署执行步骤，包括所有代码更改、数据库迁移和配置更新。

---

## 部署步骤总览

### 1. 部署 Nginx 配置

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001

# 1. 复制配置文件
sudo cp deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf

# 2. 创建软链接
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf

# 3. 测试配置
sudo nginx -t

# 4. 重新加载 Nginx
sudo systemctl reload nginx

# 5. 验证访问
curl -I https://admin.usdt2026.cc
```

### 2. 拉取最新代码

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001
git pull origin main
```

### 3. 运行数据库迁移

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001

# 激活虚拟环境
source .venv/bin/activate

# 运行迁移脚本
python3 migrations/add_scheduled_redpacket_rain.py

# 验证表已创建（可选）
# 连接到数据库检查 scheduled_redpacket_rains 表是否存在
```

### 4. 重启后端服务

```bash
# 重启服务
sudo systemctl restart hbgm001-backend

# 检查服务状态
sudo systemctl status hbgm001-backend

# 查看日志（确认无错误）
sudo journalctl -u hbgm001-backend -n 50
```

### 5. 构建前端

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001/admin/frontend

# 安装依赖（如果需要）
npm install

# 构建生产版本
npm run build

# 验证构建产物
ls -la dist/
```

### 6. 生成测试数据（可选）

```bash
# 在服务器上执行
cd /home/ubuntu/hbgm001

# 激活虚拟环境
source .venv/bin/activate

# 运行测试数据脚本
python3 scripts/py/seed_referral_tree.py
```

---

## 功能验证

### 验证 1: Nginx 配置

- [ ] 访问 `https://admin.usdt2026.cc` 显示后台登录页
- [ ] API 代理正常工作（`/api/v1/admin/auth/login`）
- [ ] SPA 路由正常工作（刷新页面不出现 404）

### 验证 2: 红包退款功能

1. 登录后台管理面板
2. 进入"红包管理"页面
3. 选择一个未领取的红包
4. 点击"退款"按钮
5. 验证：
   - [ ] 退款成功提示
   - [ ] 红包状态变为"已退款"
   - [ ] 发送者余额已增加（通过 LedgerService）

### 验证 3: 推荐系统配置

1. 登录后台管理面板
2. 进入"邀请管理"页面
3. 找到"佣金配置"卡片
4. 修改佣金率（例如：一级5%，二级2%）
5. 点击"保存配置"
6. 验证：
   - [ ] 保存成功提示
   - [ ] 配置已更新（刷新页面后配置仍然存在）

### 验证 4: 红包雨调度

1. 登录后台管理面板
2. 进入"红包管理"页面
3. 点击"调度红包雨"按钮
4. 填写表单：
   - 开始时间：未来某个时间（例如：1小时后）
   - 总金额：100 USDT
   - 红包数量：10
   - 目标群组ID：留空（公开红包）
5. 点击"确定"
6. 验证：
   - [ ] 调度成功提示
   - [ ] 调度记录已创建（可在数据库中查看 `scheduled_redpacket_rains` 表）

### 验证 5: 交易管理余额分类

1. 登录后台管理面板
2. 进入"交易管理"页面
3. 查看交易列表
4. 验证：
   - [ ] 每行交易显示"余额分类"列
   - [ ] USDT 交易显示"真实"和"奖励"余额
   - [ ] 其他币种显示 "-"

### 验证 6: 推荐关系树测试数据

1. 登录后台管理面板
2. 进入"邀请管理"页面
3. 在列表中找到一个测试用户（username 以 "test_user_" 开头）
4. 点击"查看关系树"
5. 验证：
   - [ ] 关系树正常显示
   - [ ] 可以看到3层推荐关系

---

## 一键部署脚本

如果需要一键执行所有步骤，可以使用以下脚本：

```bash
#!/bin/bash
# 一键部署脚本

set -e

PROJECT_DIR="/home/ubuntu/hbgm001"
cd $PROJECT_DIR

echo "=========================================="
echo "开始部署系统集成与推广升级"
echo "=========================================="

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 2. 部署 Nginx 配置
echo "🔧 部署 Nginx 配置..."
sudo cp deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf
sudo nginx -t && sudo systemctl reload nginx
echo "✅ Nginx 配置已更新"

# 3. 激活虚拟环境
echo "🐍 激活虚拟环境..."
source .venv/bin/activate

# 4. 运行数据库迁移
echo "🗄️  运行数据库迁移..."
python3 migrations/add_scheduled_redpacket_rain.py
echo "✅ 数据库迁移完成"

# 5. 重启后端服务
echo "🔄 重启后端服务..."
sudo systemctl restart hbgm001-backend
sleep 3
sudo systemctl status hbgm001-backend --no-pager -l || true
echo "✅ 后端服务已重启"

# 6. 构建前端
echo "🏗️  构建前端..."
cd admin/frontend
npm install
npm run build
cd ../..
echo "✅ 前端构建完成"

echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "请验证以下功能："
echo "1. 访问 https://admin.usdt2026.cc 显示后台登录页"
echo "2. 测试红包退款功能"
echo "3. 测试推荐系统配置"
echo "4. 测试红包雨调度"
echo "5. 查看交易管理余额分类"
```

---

## 回滚步骤

如果部署出现问题，可以按以下步骤回滚：

### 回滚代码

```bash
cd /home/ubuntu/hbgm001
git log --oneline -10  # 查看提交历史
git checkout <previous-commit-hash>
sudo systemctl restart hbgm001-backend
```

### 回滚数据库迁移

```bash
cd /home/ubuntu/hbgm001
source .venv/bin/activate
python3 migrations/add_scheduled_redpacket_rain.py down
```

### 回滚 Nginx 配置

```bash
# 如果有备份
sudo cp /etc/nginx/sites-available/admin.usdt2026.cc.conf.backup /etc/nginx/sites-available/admin.usdt2026.cc.conf
sudo nginx -t
sudo systemctl reload nginx
```

---

## 常见问题

### Q1: 数据库迁移失败

**错误**: `Table 'scheduled_redpacket_rains' already exists`

**解决**: 表已存在，跳过迁移或先执行回滚：
```bash
python3 migrations/add_scheduled_redpacket_rain.py down
python3 migrations/add_scheduled_redpacket_rain.py
```

### Q2: 后端服务启动失败

**错误**: `ModuleNotFoundError: No module named 'redis'`

**解决**: 安装缺失的依赖：
```bash
source .venv/bin/activate
pip install redis
sudo systemctl restart hbgm001-backend
```

### Q3: 前端构建失败

**错误**: TypeScript 编译错误

**解决**: 检查代码语法，修复错误后重新构建：
```bash
cd admin/frontend
npm run build
```

### Q4: Nginx 配置测试失败

**错误**: `nginx: [emerg] unknown directive`

**解决**: 检查配置文件语法，确保所有指令正确：
```bash
sudo nginx -t
```

---

## 后续优化建议

1. **红包雨执行器**: 实现后台任务（Celery/APScheduler）来执行调度的红包雨
2. **实时监控**: 添加 WebSocket 推送，实时更新推荐关系树和红包雨状态
3. **批量操作**: 支持批量退款、批量调度等功能
4. **数据分析**: 添加推荐效果分析、红包雨效果分析等报表

---

**文档版本**: v1.0  
**最后更新**: 2025-01-XX

