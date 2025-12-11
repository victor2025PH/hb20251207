# 简单的诊断命令（直接输入，不需要粘贴）

## 在控制台直接输入以下命令

### 步骤 1：允许粘贴（可选）

如果以后想粘贴代码，先输入：
```
allow pasting
```
然后按 Enter。

### 步骤 2：查找按钮

在控制台输入框（显示 `>` 的地方）输入：

```javascript
document.querySelectorAll('[data-testid^="menu-link"]')
```

按 Enter，会显示找到的按钮数组。

### 步骤 3：检查第一个按钮是否存在

输入：

```javascript
document.querySelector('[data-testid="menu-link-security"]')
```

如果显示按钮元素，说明按钮存在。如果显示 `null`，说明按钮不存在。

### 步骤 4：检查按钮样式

输入：

```javascript
const btn = document.querySelector('[data-testid="menu-link-security"]'); if(btn) { const s = window.getComputedStyle(btn); console.log('pointerEvents:', s.pointerEvents, 'zIndex:', s.zIndex); }
```

### 步骤 5：检查是否有覆盖层

输入：

```javascript
const btn = document.querySelector('[data-testid="menu-link-security"]'); if(btn) { const r = btn.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); console.log('覆盖元素:', e !== btn ? e.tagName : '无'); if(e !== btn) e.style.outline = '3px solid red'; }
```

### 步骤 6：手动触发点击

输入：

```javascript
document.querySelector('[data-testid="menu-link-security"]')?.click()
```

如果页面跳转了，说明按钮可以点击。如果没有跳转，说明有问题。

## 如果按钮不存在，查找所有按钮

输入：

```javascript
Array.from(document.querySelectorAll('button')).filter(b => b.textContent.includes('安全') || b.textContent.includes('帮助') || b.textContent.includes('协议'))
```

这会显示所有包含"安全"、"帮助"或"协议"文本的按钮。

## 最简单的测试

**只输入这一行：**

```javascript
document.querySelector('[data-testid="menu-link-security"]')?.click()
```

告诉我结果：
- 如果页面跳转了 → 按钮存在且可以点击
- 如果显示 `undefined` → 按钮不存在
- 如果没有任何反应 → 按钮存在但点击无效

