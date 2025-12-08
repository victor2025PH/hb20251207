# Telegram MiniApp 登录调试指南

## 问题诊断

当在 Telegram MiniApp 中遇到登录问题时，需要收集以下日志：

### 1. 服务器端日志（最重要）

**打开方式：**
```bash
# SSH 连接到服务器
ssh ubuntu@165.154.254.99

# 实时查看后端服务日志
sudo journalctl -u hbgm001-backend -f
```

**关键日志信息：**
- `[Auth] Attempting Telegram authentication` - 开始 Telegram 认证
- `[Auth] BOT_TOKEN 配置狀態` - BOT_TOKEN 是否配置
- `[Auth] Telegram initData hash 驗證成功/失敗` - initData 验证结果
- `[Auth] 從 initData 中提取到 tg_id` - 提取到的 Telegram 用户 ID
- `[Auth] Telegram 用戶認證成功` - 认证成功
- `[Auth] No Telegram initData, falling back to JWT token auth` - 没有 initData，回退到 JWT

### 2. 前端浏览器日志（Telegram MiniApp）

**在 Telegram MiniApp 中查看日志的方法：**

#### 方法 A：使用 Telegram Desktop（推荐）
1. 在电脑上打开 Telegram Desktop
2. 打开 MiniApp
3. 按 `F12` 或 `Ctrl+Shift+I` 打开开发者工具
4. 切换到 `Console` 标签
5. 查看以下关键日志：
   - `[Telegram] WebApp initialized` - Telegram WebApp 初始化
   - `[Telegram] initData 已准备就绪` - initData 状态
   - `[Auth] Initializing authentication...` - 认证初始化
   - `[Auth] Detected Telegram environment` - 检测到 Telegram 环境
   - `[API Request]` - API 请求日志（包含 initData 预览）

#### 方法 B：使用 Android/iOS 调试工具
1. **Android**: 使用 Chrome 的 `chrome://inspect` 连接设备
2. **iOS**: 使用 Safari 的 Web Inspector（需要 Mac）

#### 方法 C：在代码中添加调试面板（已实现）
- 前端会自动在页面上显示调试信息
- 查看页面上的调试面板，包含：
  - `initData` 长度
  - `Telegram WebApp` 状态
  - 用户信息

### 3. Nginx 访问日志

**查看 Nginx 日志：**
```bash
# SSH 连接到服务器
ssh ubuntu@165.154.254.99

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

**关键信息：**
- 502 Bad Gateway - 后端服务不可用
- 504 Gateway Timeout - 后端响应超时
- 请求路径和状态码

## 常见问题诊断

### 问题 1: 502 Bad Gateway

**原因：**
- 后端服务未启动或崩溃
- Python 语法错误（如刚才的缩进错误）

**检查步骤：**
```bash
# 1. 检查服务状态
sudo systemctl status hbgm001-backend

# 2. 查看服务日志
sudo journalctl -u hbgm001-backend -n 50

# 3. 检查 Python 语法
cd /home/ubuntu/hbgm001
python3 -m py_compile api/routers/auth.py

# 4. 手动测试后端
curl http://localhost:8080/health
```

### 问题 2: initData 为空

**症状：**
- 前端日志显示 `initData length: 0`
- 后端日志显示 `No Telegram initData`

**可能原因：**
1. 不是在真正的 Telegram MiniApp 中打开（在浏览器中直接访问）
2. Telegram WebApp SDK 未完全加载
3. initData 被某些安全策略阻止

**解决方案：**
- 确保在 Telegram 客户端中打开 MiniApp
- 等待 2-3 秒让 WebApp SDK 完全初始化
- 检查 `window.Telegram?.WebApp?.initData` 是否存在

### 问题 3: initData hash 验证失败

**症状：**
- 后端日志显示 `Telegram initData hash 驗證失敗`

**可能原因：**
1. `BOT_TOKEN` 配置错误
2. initData 已过期（通常 24 小时内有效）
3. initData 被篡改

**解决方案：**
```bash
# 检查 BOT_TOKEN 配置
cd /home/ubuntu/hbgm001
grep BOT_TOKEN .env

# 如果 BOT_TOKEN 未配置，可以暂时跳过验证（仅开发环境）
# 后端会自动跳过验证并记录警告日志
```

### 问题 4: 用户认证成功但前端仍显示登录页面

**症状：**
- 后端日志显示认证成功
- 前端 `isAuthenticated: true` 但 `hasUser: false`

**可能原因：**
- 前端状态更新延迟
- `getCurrentUser()` 返回的数据格式不正确

**解决方案：**
- 检查前端 `useAuth.ts` 中的状态更新逻辑
- 确保后端返回的 `UserResponse` 包含所有必需字段

## 完整调试流程

### 步骤 1: 收集服务器日志
```bash
ssh ubuntu@165.154.254.99
sudo journalctl -u hbgm001-backend -f
```

### 步骤 2: 在 Telegram MiniApp 中尝试登录
- 打开 MiniApp
- 点击 "使用Telegram登录"
- 观察页面上的调试面板

### 步骤 3: 分析日志
- **服务器端**：查看认证流程日志
- **前端**：查看 Console 日志（如果可用）
- **Nginx**：查看访问和错误日志

### 步骤 4: 提供诊断数据
请提供以下信息：
1. **服务器日志**（最近 50 行）：
   ```bash
   sudo journalctl -u hbgm001-backend -n 50 --no-pager
   ```

2. **服务状态**：
   ```bash
   sudo systemctl status hbgm001-backend --no-pager
   ```

3. **前端 Console 日志**（如果可用）：
   - 截图或复制 Console 输出

4. **Nginx 错误日志**（如果有 502/504）：
   ```bash
   sudo tail -20 /var/log/nginx/error.log
   ```

## 快速检查命令

```bash
# 一键检查所有状态
ssh ubuntu@165.154.254.99 << 'EOF'
echo "=== 服务状态 ==="
sudo systemctl status hbgm001-backend --no-pager | head -15

echo -e "\n=== 最近错误日志 ==="
sudo journalctl -u hbgm001-backend -n 20 --no-pager | grep -i error

echo -e "\n=== 后端健康检查 ==="
curl -s http://localhost:8080/health || echo "后端不可用"

echo -e "\n=== Nginx 错误日志 ==="
sudo tail -10 /var/log/nginx/error.log
EOF
```

## 联系支持

如果问题仍然存在，请提供：
1. 完整的服务器日志（最近 100 行）
2. 前端 Console 日志（如果可用）
3. 具体的错误信息截图
4. 操作步骤和时间点

