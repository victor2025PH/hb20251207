# 后台登录问题排查

## 默认登录凭据

**用户名**: `admin`  
**密码**: `123456`

**登录地址**: https://admin.usdt2026.cc

---

## 常见问题

### 问题 1: 提示"用户名或密码错误"

**可能原因**:
1. 密码输入错误
2. 管理员用户不存在
3. 密码哈希方式不匹配

**解决方法**:

1. **检查管理员用户是否存在**:
```bash
ssh ubuntu@165.154.254.99 "cd /home/ubuntu/hbgm001 && source .venv/bin/activate && python3 scripts/create_admin_simple.py --username admin --password 123456 --email admin@example.com"
```

2. **测试登录API**:
```bash
curl -X POST http://127.0.0.1:8080/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

3. **查看后端日志**:
```bash
ssh ubuntu@165.154.254.99 "sudo journalctl -u hbgm001-backend -n 50 --no-pager | grep -i login"
```

---

### 问题 2: 502 Bad Gateway

**可能原因**:
- 后端服务未运行或崩溃

**解决方法**:
```bash
# 检查服务状态
ssh ubuntu@165.154.254.99 "sudo systemctl status hbgm001-backend"

# 重启服务
ssh ubuntu@165.154.254.99 "sudo systemctl restart hbgm001-backend"

# 查看日志
ssh ubuntu@165.154.254.99 "sudo journalctl -u hbgm001-backend -n 100 --no-pager"
```

---

### 问题 3: 账户已被禁用

**解决方法**:
```bash
# 激活管理员账户
ssh ubuntu@165.154.254.99 "cd /home/ubuntu/hbgm001 && source .venv/bin/activate && python3 -c \"
from shared.database.connection import SyncSessionLocal
from shared.database.models import AdminUser
db = SyncSessionLocal()
try:
    admin = db.query(AdminUser).filter(AdminUser.username == 'admin').first()
    if admin:
        admin.is_active = True
        db.commit()
        print('✅ 管理员账户已激活')
    else:
        print('❌ 管理员用户不存在')
finally:
    db.close()
\""
```

---

## 创建新管理员用户

如果需要创建新的管理员用户：

```bash
cd /home/ubuntu/hbgm001
source .venv/bin/activate

# 使用简单脚本（推荐）
python3 scripts/create_admin_simple.py --username YOUR_USERNAME --password YOUR_PASSWORD --email YOUR_EMAIL

# 或使用异步脚本
python3 scripts/py/create_admin_user.py YOUR_USERNAME YOUR_PASSWORD YOUR_EMAIL
```

---

## 验证登录

### 方法 1: 使用 curl 测试

```bash
curl -X POST https://admin.usdt2026.cc/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

**成功响应示例**:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

### 方法 2: 在浏览器中登录

1. 访问 https://admin.usdt2026.cc
2. 输入用户名: `admin`
3. 输入密码: `123456`
4. 点击登录

---

## 密码哈希说明

当前系统使用 **SHA256** 哈希存储密码（用于测试环境）。

**生产环境建议**:
- 使用 bcrypt 或其他安全的密码哈希算法
- 启用密码复杂度要求
- 实施密码过期策略

---

**最后更新**: 2025-12-09

