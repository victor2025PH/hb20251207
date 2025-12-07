# 🔐 Telegram 自动登录修复说明

## 问题描述

Telegram MiniApp 无法自动识别和登录用户，需要手动选择登录方式。

## 修复内容

### 1. 后端认证修复

**文件**: `api/routers/auth.py`

- 修改 `get_current_user_from_token` 函数，现在支持：
  - JWT Token 认证（Web 登录）
  - Telegram initData 认证（MiniApp 自动登录）
- 当检测到 `X-Telegram-Init-Data` 请求头时，自动解析并创建/查找用户

**文件**: `api/routers/users.py`

- 更新 `/v1/users/me` 和 `/v1/users/me/balance` 端点
- 使用统一的 `get_current_user_from_token` 依赖
- 支持 Telegram MiniApp 和 Web 两种认证方式

### 2. 数据库约束修复

**文件**: `scripts/py/fix_tg_id_constraint.py`

- 确保 `users.tg_id` 列可以为 NULL
- 支持非 Telegram 用户（Google、Wallet 等）

## 部署步骤

### 在服务器上执行

```bash
cd /opt/luckyred

# 1. 拉取最新代码
git pull origin master

# 2. 运行数据库迁移和约束修复
cd api
source .venv/bin/activate

# 添加缺失的列
python3 ../scripts/py/migrate_add_uuid_column.py

# 修复 tg_id 约束
python3 ../scripts/py/fix_tg_id_constraint.py

# 3. 重新构建前端
cd ../frontend
npm run build

# 4. 重启 API 服务
sudo systemctl restart luckyred-api

# 5. 重新加载 Nginx
sudo systemctl reload nginx
```

### 或使用一键修复脚本

```bash
cd /opt/luckyred
git pull origin master
bash fix-database.sh
```

## 验证步骤

### 1. Telegram MiniApp 自动登录

1. 在 Telegram 中打开 MiniApp
2. 应该自动识别 Telegram 用户并登录
3. 不需要手动选择登录方式
4. 应该能看到用户信息和余额

### 2. Web 端登录

1. 在浏览器中访问 https://mini.usdt2026.cc
2. 应该显示登录选项（Google、Telegram、Wallet 等）
3. 选择 Google 登录应该成功
4. 登录后应该能看到所有功能

### 3. 检查日志

```bash
# 查看 API 日志
sudo journalctl -u luckyred-api -n 50 --no-pager | grep -i "telegram\|auth"

# 应该看到类似日志：
# Telegram 用戶認證成功: tg_id=123456, user_id=1
```

## 工作原理

### Telegram MiniApp 自动登录流程

1. **前端检测**: `useAuth.ts` 检测到 Telegram 环境
2. **获取 initData**: 从 `window.Telegram.WebApp.initData` 获取
3. **发送请求**: API 请求自动包含 `X-Telegram-Init-Data` 请求头
4. **后端解析**: `get_current_user_from_token` 解析 initData
5. **查找/创建用户**: 使用 `IdentityService` 查找或创建用户
6. **返回用户信息**: 前端收到用户信息，完成登录

### Web 登录流程

1. **用户选择登录方式**: Google、Wallet 等
2. **发送认证请求**: 到 `/api/v1/auth/web/google` 等端点
3. **创建用户**: 使用 `IdentityService` 创建用户（tg_id 为 NULL）
4. **生成 JWT Token**: 返回 JWT token
5. **存储 Token**: 前端存储到 localStorage
6. **后续请求**: 使用 `Authorization: Bearer <token>` 请求头

## 常见问题

### Q: Telegram MiniApp 仍然显示登录界面

**A**: 检查以下几点：
1. 确认 `initData` 不为空：在浏览器控制台运行 `window.Telegram?.WebApp?.initData`
2. 检查 API 日志是否有认证错误
3. 确认数据库 `users` 表有 `tg_id` 列且可以为 NULL

### Q: Google 登录失败，提示 tg_id 不能为 NULL

**A**: 运行约束修复脚本：
```bash
cd /opt/luckyred/api
source .venv/bin/activate
python3 ../scripts/py/fix_tg_id_constraint.py
```

### Q: 前端显示 "认证失败"

**A**: 
1. 检查后端服务是否正常运行：`sudo systemctl status luckyred-api`
2. 查看 API 日志：`sudo journalctl -u luckyred-api -n 100`
3. 确认 `BOT_TOKEN` 环境变量已设置

## 技术细节

### initData 格式

Telegram WebApp 的 `initData` 格式：
```
user=%7B%22id%22%3A123456%2C%22first_name%22%3A%22John%22%7D&auth_date=1234567890&hash=...
```

后端解析后得到：
```json
{
  "id": 123456,
  "first_name": "John",
  "username": "john_doe",
  "language_code": "en"
}
```

### 用户创建逻辑

1. 如果用户已存在（通过 `tg_id` 或 `uuid` 查找），返回现有用户
2. 如果用户不存在，创建新用户：
   - Telegram: 设置 `tg_id`, `username`, `first_name` 等
   - Google: `tg_id` 为 NULL，使用 `email` 作为标识
   - Wallet: `tg_id` 为 NULL，使用 `wallet_address` 作为标识

## 相关文件

- `api/routers/auth.py` - 认证路由
- `api/routers/users.py` - 用户路由
- `api/utils/telegram_auth.py` - Telegram 认证工具
- `api/services/identity_service.py` - 身份服务
- `frontend/src/utils/auth/useAuth.ts` - 前端认证 Hook
- `frontend/src/utils/telegram.ts` - Telegram WebApp 工具
- `frontend/src/utils/auth/AuthGuard.tsx` - 认证守卫组件

