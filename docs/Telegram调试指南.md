# Telegram MiniApp 调试指南

## 问题：无法使用 F12 打开开发者工具

在 Telegram MiniApp 中，应用是在 Telegram 客户端内运行的，不是独立的浏览器窗口，所以无法直接使用 F12 打开开发者工具。

## 解决方案

### 方法一：使用调试面板（推荐）✅

我已经创建了一个内置的调试面板，可以直接在页面上显示所有调试信息。

#### 如何启用调试面板

1. **在 URL 中添加 `?debug=true` 参数**
   - 例如：`https://mini.usdt2026.cc/?debug=true`
   - 或者在 Telegram Bot 中打开应用时，在 URL 后面添加 `?debug=true`

2. **或者使用开发环境**
   - 开发环境会自动启用调试面板

#### 调试面板功能

调试面板会显示：
- 📱 **Telegram 信息**：initData、用户信息、平台信息
- 🌐 **环境信息**：URL、User Agent、是否在 Telegram 中
- 📡 **API 请求**：最近的 API 请求和请求头
- 📋 **日志**：所有认证相关的日志（[Auth]、[API]、[Telegram]）

#### 如何使用

1. 在 Telegram MiniApp 中打开应用，URL 添加 `?debug=true`
2. 点击右下角的 🐛 按钮打开调试面板
3. 查看所有调试信息
4. 可以点击"复制调试信息"按钮，将信息复制到剪贴板

### 方法二：使用桌面版 Telegram 的开发者工具

#### Windows/Mac 桌面版

1. 打开 Telegram Desktop
2. 打开 MiniApp
3. 右键点击 MiniApp 窗口
4. 选择"检查元素"或"开发者工具"（如果可用）

**注意**：不是所有版本的 Telegram Desktop 都支持此功能。

### 方法三：查看服务器端日志

这是最可靠的方法，因为所有认证请求都会记录在服务器日志中。

#### 查看实时日志

```bash
# 在服务器 ubuntu@10-11-156-159 上执行：
sudo journalctl -u luckyred-api -f --since '5 minutes ago'
```

#### 查看最近的错误

```bash
# 在服务器 ubuntu@10-11-156-159 上执行：
sudo journalctl -u luckyred-api --since '10 minutes ago' | grep -i "telegram\|auth\|error"
```

#### 查找关键日志

在日志中查找以下关键词：
- `[Auth] Telegram-first strategy` - 确认使用了 Telegram 优先策略
- `[Auth] 開始處理 Telegram initData` - 确认后端收到了 initData
- `[Auth] Telegram 用戶認證成功` - 认证成功 ✅
- `[Auth] Telegram initData hash 驗證失敗` - hash 验证失败 ❌
- `[Auth] Telegram initData 中沒有用戶信息` - initData 中没有用户数据 ❌

### 方法四：使用 Chrome DevTools 远程调试（高级）

如果使用 Telegram Desktop（基于 Electron），可以尝试：

1. 打开 Chrome 浏览器
2. 访问 `chrome://inspect`
3. 查找 Telegram 进程
4. 点击"inspect"打开开发者工具

**注意**：这需要 Telegram Desktop 是基于 Electron 的版本。

## 推荐的调试流程

### 步骤 1：启用调试面板

在 Telegram MiniApp URL 中添加 `?debug=true`，例如：
```
https://mini.usdt2026.cc/?debug=true
```

### 步骤 2：打开调试面板

点击右下角的 🐛 按钮

### 步骤 3：查看 Telegram 信息

检查：
- ✅ `hasInitData: true`
- ✅ `initDataLength > 0`
- ✅ `user.id` 存在

### 步骤 4：查看 API 请求

检查最近的 API 请求：
- ✅ 请求头中是否包含 `X-Telegram-Init-Data`
- ✅ 请求的 URL 是否正确

### 步骤 5：查看日志

检查日志中的错误信息：
- ❌ 如果有 "hash 驗證失敗"，检查 BOT_TOKEN 配置
- ❌ 如果有 "沒有用戶信息"，检查 initData 是否完整

### 步骤 6：查看服务器日志

如果调试面板无法解决问题，查看服务器日志：

```bash
# 在服务器上执行：
cd /opt/luckyred && sudo journalctl -u luckyred-api -f --since '5 minutes ago'
```

## 常见问题

### Q: 调试面板没有显示？

A: 确保：
1. URL 中包含 `?debug=true` 参数
2. 或者是在开发环境（`npm run dev`）

### Q: 调试面板显示 initData 为空？

A: 可能的原因：
1. 不是在真正的 Telegram MiniApp 中打开
2. Telegram WebApp SDK 还没有完全加载（等待几秒）
3. 需要刷新页面

### Q: 如何分享调试信息？

A: 在调试面板中点击"复制调试信息"按钮，然后将内容发送给开发者。

## 快速诊断命令

```bash
# 在服务器 ubuntu@10-11-156-159 上执行：

# 1. 运行诊断工具
cd /opt/luckyred && git pull origin master && bash diagnose-telegram-auth.sh

# 2. 查看实时 API 日志
sudo journalctl -u luckyred-api -f --since '5 minutes ago'

# 3. 查看最近的错误
sudo journalctl -u luckyred-api --since '10 minutes ago' | grep -i error
```

## 总结

**最简单的方法**：在 URL 中添加 `?debug=true`，然后点击 🐛 按钮查看调试面板。

**最可靠的方法**：查看服务器端日志，所有认证请求都会记录在那里。

