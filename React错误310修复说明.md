# 🔧 React Error #310 修复说明

## 问题原因

React Error #310 表示 "Rendered more hooks than during the previous render"，这通常发生在：

1. **Hooks 在条件语句中调用**：违反了 React Hooks 规则
2. **Hooks 数量在渲染之间变化**：导致 React 无法正确追踪 hooks

## 修复内容

### 问题代码
在 `AuthGuard.tsx` 中，`useState` 和 `useEffect` 在条件返回之后被调用：

```typescript
// ❌ 错误：hooks 在条件返回之后
if (loading) return <div>加载中...</div>;
if (!requireAuth) return <>{children}</>;
if (isAuthenticated && user) return <>{children}</>;

// 这些 hooks 在早期返回时不会被调用
const [telegramInitTimeout, setTelegramInitTimeout] = React.useState(false);
React.useEffect(() => { ... }, []);
```

### 修复后代码
将所有 hooks 移到组件顶部，在任何条件返回之前：

```typescript
// ✅ 正确：所有 hooks 在组件顶部
export function AuthGuard({ children, requireAuth = true, fallback }: AuthGuardProps) {
  // 1. 所有 hooks 必须在顶部
  const { user, loading, isAuthenticated } = useAuth();
  const [platformInfo, setPlatformInfo] = useState(...);
  const [platformRules, setPlatformRules] = useState(...);
  const [telegramInitTimeout, setTelegramInitTimeout] = useState(false);
  
  useEffect(() => { ... }, []);
  useEffect(() => { ... }, [deps]);

  // 2. 条件返回在 hooks 之后
  if (loading) return <div>加载中...</div>;
  if (!requireAuth) return <>{children}</>;
  if (isAuthenticated && user) return <>{children}</>;
  
  // 3. 其他逻辑...
}
```

## 服务器部署步骤

### 1. 拉取最新代码

```bash
cd /opt/luckyred
git pull origin master
```

### 2. 重新构建前端

```bash
cd frontend
npm run build
```

### 3. 验证构建成功

检查是否有新的 `index-*.js` 文件生成：

```bash
ls -lh dist/assets/index-*.js | tail -1
```

应该看到类似 `index-CaaDKATl.js` 的新文件（不是旧的 `index-TI3zNGEj.js`）

### 4. 重新加载 Nginx

```bash
sudo systemctl reload nginx
```

### 5. 验证修复

1. **清除浏览器缓存**（重要！）
   - Chrome: `Ctrl+Shift+Delete` → 清除缓存
   - 或使用无痕模式

2. **访问网站**: https://mini.usdt2026.cc

3. **检查控制台**:
   - ✅ 不应该有 React error #310
   - ✅ 应该显示登录界面（在浏览器中）
   - ✅ 不应该有 "Minified React error" 错误

## 预期结果

### 浏览器访问
- ✅ 直接显示多种登录选项（Google、Telegram、Facebook、WhatsApp、Wallet、Magic Link）
- ✅ 不再显示 React error #310
- ✅ 页面正常渲染

### Telegram 访问
- ✅ 如果有 `initData`，自动登录
- ✅ 如果没有 `initData`，等待 1.5 秒后显示登录选项
- ✅ 不再显示 React error #310

## 技术细节

### React Hooks 规则

1. **只在顶层调用 Hooks**：不要在循环、条件或嵌套函数中调用
2. **只在 React 函数中调用 Hooks**：不要在普通 JavaScript 函数中调用
3. **Hooks 调用顺序必须一致**：每次渲染时 hooks 的调用顺序必须相同

### 为什么会出现 Error #310？

当组件在早期返回时（如 `if (loading) return ...`），后续的 hooks 不会被调用。但在下一次渲染时，如果条件改变，所有 hooks 都会被调用，导致 hooks 数量不一致，触发错误。

## 验证清单

- [ ] 代码已拉取到最新版本
- [ ] 前端构建成功（无错误）
- [ ] 新的 `index-*.js` 文件已生成
- [ ] Nginx 已重新加载
- [ ] 浏览器缓存已清除
- [ ] 页面正常显示（无 React error #310）
- [ ] 登录界面正常显示
- [ ] 控制台无严重错误

## 如果问题仍然存在

1. **检查服务器代码版本**:
   ```bash
   cd /opt/luckyred
   git log -1
   ```
   应该看到 "fix: 修复React error #310" 的提交

2. **检查前端文件**:
   ```bash
   ls -lh frontend/dist/assets/index-*.js
   ```
   应该看到新的文件名（不是 `index-TI3zNGEj.js`）

3. **强制清除浏览器缓存**:
   - 使用无痕模式
   - 或 `Ctrl+Shift+R` 强制刷新

4. **检查控制台错误**:
   - 打开开发者工具（F12）
   - 查看 Console 标签
   - 截图错误信息

