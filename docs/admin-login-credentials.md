# 后台管理登录凭据

## 默认管理员账号

**用户名**: `admin`  
**密码**: `123456`  
**邮箱**: `admin@example.com`

---

## 创建管理员用户

如果默认管理员用户不存在，可以使用以下脚本创建：

### 方法 1: 使用简单脚本（推荐）

```bash
cd /home/ubuntu/hbgm001
source .venv/bin/activate
python3 scripts/create_admin_simple.py --username admin --password 123456 --email admin@example.com
```

### 方法 2: 使用异步脚本

```bash
cd /home/ubuntu/hbgm001
source .venv/bin/activate
python3 scripts/py/create_admin_user.py admin 123456 admin@example.com
```

### 方法 3: 使用完整脚本

```bash
cd /home/ubuntu/hbgm001
source .venv/bin/activate
python3 scripts/create_admin_user.py --username admin --password 123456 --email admin@example.com
```

---

## 登录地址

**后台管理面板**: https://admin.usdt2026.cc

---

## 安全提示

⚠️ **重要**: 默认密码 `123456` 仅用于测试环境。生产环境请：

1. 立即修改密码
2. 使用强密码（至少12位，包含大小写字母、数字和特殊字符）
3. 定期更换密码
4. 启用双因素认证（如果支持）

---

## 修改密码

登录后，可以在后台管理面板的"个人设置"中修改密码。

---

**最后更新**: 2025-12-09

