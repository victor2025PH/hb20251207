# 查看和提取日志指南

## 📋 方法零：服务器 Bot 运行日志（服务器端）

### ⚠️ Bot 启动失败诊断

如果 bot 服务无法启动（status=1/FAILURE），请按以下步骤诊断：

#### 1. 查看详细错误日志

```bash
# 查看最近 100 行日志（包含错误堆栈）
sudo journalctl -u luckyred-bot -n 100 --no-pager

# 查看最近的错误日志（只显示错误级别）
sudo journalctl -u luckyred-bot -p err -n 50 --no-pager

# 实时监控日志（会显示新的错误）
sudo journalctl -u luckyred-bot -f
```

#### 2. 检查常见问题

```bash
# 检查 .env 文件是否存在且包含 BOT_TOKEN
cat /home/ubuntu/hbgm001/.env | grep BOT_TOKEN

# 检查虚拟环境是否存在
ls -la /home/ubuntu/hbgm001/bot/.venv/bin/python

# 检查 Python 依赖是否安装
/home/ubuntu/hbgm001/bot/.venv/bin/python -c "import telegram; print('OK')"

# 手动测试运行（从项目根目录）
cd /home/ubuntu/hbgm001
/home/ubuntu/hbgm001/bot/.venv/bin/python bot/main.py
```

#### 3. 检查服务配置

```bash
# 查看服务配置
sudo systemctl cat luckyred-bot

# 检查服务状态
sudo systemctl status luckyred-bot -l --no-pager
```

### 快速查看命令

#### 1. 实时监控 Bot 日志

```bash
# 实时监控 Bot 服务日志（推荐）
sudo journalctl -u luckyred-bot -f

# 实时监控所有服务（API + Bot）
sudo journalctl -u luckyred-api -u luckyred-bot -f
```

#### 2. 查看最近日志

```bash
# 查看 Bot 最近 100 行日志
sudo journalctl -u luckyred-bot -n 100 --no-pager

# 查看 Bot 最近 50 行日志
sudo journalctl -u luckyred-bot -n 50 --no-pager

# 查看所有服务最近 100 行日志
sudo journalctl -u luckyred-api -u luckyred-bot -n 100 --no-pager
```

#### 3. 按时间范围查看

```bash
# 查看最近 1 小时的日志
sudo journalctl -u luckyred-bot --since "1 hour ago"

# 查看最近 30 分钟的日志
sudo journalctl -u luckyred-bot --since "30 minutes ago"

# 查看今天的日志
sudo journalctl -u luckyred-bot --since today

# 查看指定时间范围的日志
sudo journalctl -u luckyred-bot --since "2025-01-10 08:00:00" --until "2025-01-10 10:00:00"
```

#### 4. 过滤关键词

```bash
# 查找包含"红包"的日志
sudo journalctl -u luckyred-bot | grep -i "红包"

# 查找包含"错误"的日志
sudo journalctl -u luckyred-bot | grep -iE "错误|error|failed"

# 实时监控并过滤关键词
sudo journalctl -u luckyred-bot -f | grep -iE "红包|發送|錯誤|error"

# 查找红包发送相关日志
sudo journalctl -u luckyred-bot --since "1 hour ago" | grep -iE "紅包|發送|群組|send|redpacket"
```

#### 5. 按日志级别过滤

```bash
# 只查看错误日志
sudo journalctl -u luckyred-bot -p err

# 查看警告及以上级别
sudo journalctl -u luckyred-bot -p warning

# 查看最近 1 小时的错误日志
sudo journalctl -u luckyred-bot -p err --since "1 hour ago"
```

#### 6. 查看服务状态

```bash
# 查看 Bot 服务状态
sudo systemctl status luckyred-bot

# 查看服务启动日志
sudo journalctl -u luckyred-bot -b
```

#### 7. 使用脚本查看（如果可用）

```bash
# 查看 Bot 最近 100 行日志
./scripts/sh/view-logs.sh bot 100

# 查看 Bot 最近 50 行包含"红包"的日志
./scripts/sh/view-logs.sh bot 50 红包

# 实时监控所有服务
./scripts/sh/monitor-logs.sh all
```

### 常用命令速查

```bash
# 最常用：实时监控 Bot 日志
sudo journalctl -u luckyred-bot -f

# 查看最近错误
sudo journalctl -u luckyred-bot -p err -n 50 --no-pager

# 查看最近 1 小时的红包相关日志
sudo journalctl -u luckyred-bot --since "1 hour ago" | grep -i "红包"
```

---

## 📋 方法一：浏览器控制台（推荐）

### 步骤 1: 打开开发者工具

**Chrome/Edge:**
- 按 `F12` 或 `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
- 或者右键点击页面 → 选择"检查" / "Inspect"

**Telegram Desktop:**
- 在 Telegram MiniApp 中，按 `F12` 打开开发者工具
- 或者右键点击 MiniApp 窗口 → 选择"检查元素"

### 步骤 2: 切换到 Console 标签

1. 点击顶部的 **"Console"** 标签
2. 确保控制台已清空（点击 🚫 清除按钮）

### 步骤 3: 重现问题

1. 在控制台打开的情况下，点击"设置"按钮
2. 观察控制台输出的日志

### 步骤 4: 提取日志

**方法 A: 复制所有日志**
1. 在控制台中右键点击任意日志
2. 选择 **"Save as..."** 或 **"另存为..."**
3. 保存为文本文件

**方法 B: 手动复制**
1. 在控制台中按 `Ctrl+A` (Windows) / `Cmd+A` (Mac) 全选
2. 按 `Ctrl+C` (Windows) / `Cmd+C` (Mac) 复制
3. 粘贴到文本编辑器（如记事本）中保存

**方法 C: 使用控制台命令导出**
1. 在控制台输入以下命令：
```javascript
// 获取所有日志
console.log('=== 开始提取日志 ===');
// 然后手动复制所有输出
```

### 步骤 5: 过滤相关日志

在控制台的 **"Filter"** 输入框中输入关键词来过滤日志：
- `SettingsPage` - 查看设置页面相关日志
- `MenuLink` - 查看菜单链接相关日志
- `AuthGuard` - 查看认证相关日志
- `Navigation` - 查看导航相关日志
- `Error` - 查看错误日志

## 📋 方法二：使用浏览器网络面板

### 查看网络请求

1. 打开开发者工具
2. 切换到 **"Network"** 标签
3. 点击"设置"按钮
4. 查看是否有失败的请求（红色）
5. 点击失败的请求查看详细信息
6. 在 **"Response"** 标签中查看错误信息

## 📋 方法三：使用 React DevTools（如果已安装）

1. 安装 React DevTools 浏览器扩展
2. 打开开发者工具
3. 切换到 **"Components"** 标签
4. 查看组件树，找到 `SettingsPage` 组件
5. 查看组件的 props 和 state

## 📋 方法四：添加更多调试日志

如果现有日志不够，可以在代码中添加更多日志。以下是关键位置：

### 在 ProfilePage.tsx 中添加日志

```typescript
// 在 MenuLink 的 handleClick 中添加
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  e.preventDefault()
  e.stopPropagation()
  console.log('[MenuLink] 🔵 Button clicked:', title, 'to:', to)
  console.log('[MenuLink] 🔵 Event details:', {
    type: e.type,
    target: e.target,
    currentTarget: e.currentTarget,
    button: e.button,
    bubbles: e.bubbles,
    cancelable: e.cancelable
  })
  // ... 其余代码
}
```

### 在 SettingsPage.tsx 中添加日志

```typescript
export default function SettingsPage() {
  console.log('[SettingsPage] Component mounted')
  console.log('[SettingsPage] Current location:', window.location.href)
  console.log('[SettingsPage] Current pathname:', window.location.pathname)
  
  // ... 其余代码
}
```

## 📋 方法五：使用浏览器性能监控

1. 打开开发者工具
2. 切换到 **"Performance"** 标签
3. 点击录制按钮（⏺️）
4. 点击"设置"按钮
5. 停止录制
6. 查看性能时间线，找到问题发生的时间点

## 📋 需要提取的关键信息

当提取日志时，请确保包含以下信息：

1. **所有 `[SettingsPage]` 相关的日志**
2. **所有 `[MenuLink]` 相关的日志**
3. **所有 `[AuthGuard]` 相关的日志**
4. **所有错误信息（红色）**
5. **所有警告信息（黄色）**
6. **URL 变化情况**（地址栏的 URL 是否从 `/profile` 变为 `/settings`）

## 📋 快速检查清单

在提取日志前，请确认：

- [ ] 控制台已打开
- [ ] 控制台已清空
- [ ] 已切换到 Console 标签
- [ ] 已准备好重现问题
- [ ] 知道如何复制/保存日志

## 📋 示例日志格式

提取的日志应该类似这样：

```
[MenuLink] 🔵 Button clicked: 设置 to: /settings
[MenuLink] 🔵 Attempting navigation to: /settings
[MenuLink] ✅ Navigation executed successfully
[SettingsPage] Component rendered
[SettingsPage] Rendering content
[AuthGuard] Loading complete, checking auth state...
[AuthGuard] User is authenticated, rendering protected content
```

如果有错误，会显示：

```
❌ [Error] Navigation failed: ...
❌ [SettingsPage] Component error: ...
```

## 📋 如果控制台无法打开

如果无法打开浏览器控制台（例如在移动设备上），可以：

1. **使用远程调试**：
   - Android: 使用 Chrome 的远程调试功能
   - iOS: 使用 Safari 的 Web Inspector

2. **添加日志到页面**：
   - 在页面上显示日志（开发模式）
   - 使用 `localStorage` 存储日志

3. **使用网络抓包工具**：
   - 使用 Fiddler 或 Charles Proxy
   - 查看网络请求和响应

## 📋 提交日志时的格式

当您提取日志后，请按以下格式提交：

```
=== 问题描述 ===
点击"设置"按钮后跳转到首页

=== 浏览器信息 ===
Chrome 版本: 120.0.6099.109
操作系统: Windows 11

=== 控制台日志 ===
[在这里粘贴日志]

=== URL 变化 ===
点击前: https://example.com/profile
点击后: https://example.com/ (跳转到首页)

=== 其他信息 ===
[任何其他相关信息]
```

