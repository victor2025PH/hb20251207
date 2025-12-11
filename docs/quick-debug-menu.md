# 快速诊断菜单按钮（复制到浏览器控制台）

## 方法 1：一键诊断（推荐）

**复制以下代码到浏览器控制台（Console），按 Enter 执行：**

```javascript
(() => {
  console.log('🔍 开始诊断...\n');
  
  // 1. 查找按钮
  const buttons = document.querySelectorAll('[data-testid^="menu-link"]');
  console.log(`【1】找到 ${buttons.length} 个按钮`);
  
  if (buttons.length === 0) {
    console.error('❌ 按钮不存在！查找所有可能的按钮:');
    const all = Array.from(document.querySelectorAll('button, a')).filter(b => {
      const text = b.textContent.trim();
      return text.includes('安全') || text.includes('帮助') || text.includes('协议') || text.includes('设置');
    });
    console.log(`找到 ${all.length} 个可能的按钮:`, all);
    return;
  }
  
  // 2. 检查每个按钮
  buttons.forEach((btn, i) => {
    const testId = btn.dataset.testid;
    const text = btn.textContent.trim();
    const styles = window.getComputedStyle(btn);
    const rect = btn.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const elementAtPoint = document.elementFromPoint(centerX, centerY);
    const isBlocked = elementAtPoint !== btn && !btn.contains(elementAtPoint);
    
    console.log(`\n【按钮 ${i + 1}】${testId} - "${text}"`);
    console.log('  样式:', {
      pointerEvents: styles.pointerEvents,
      zIndex: styles.zIndex,
      position: styles.position
    });
    console.log('  是否被覆盖:', isBlocked ? '❌ 是' : '✅ 否');
    if (isBlocked) {
      console.error('  覆盖元素:', elementAtPoint.tagName, elementAtPoint.className);
      elementAtPoint.style.outline = '3px solid red';
    }
    
    // 测试点击
    console.log('  测试点击...');
    try {
      btn.click();
      console.log('  ✅ 点击已触发');
    } catch (e) {
      console.error('  ❌ 点击失败:', e);
    }
  });
  
  console.log('\n✅ 诊断完成');
})();
```

## 方法 2：分步检查

### 步骤 1：检查按钮是否存在

```javascript
const buttons = document.querySelectorAll('[data-testid^="menu-link"]');
console.log('找到按钮数量:', buttons.length);
buttons.forEach((btn, i) => {
  console.log(`${i + 1}. ${btn.dataset.testid}: "${btn.textContent.trim()}"`);
});
```

### 步骤 2：检查覆盖层

```javascript
const btn = document.querySelector('[data-testid="menu-link-security"]');
if (btn) {
  const rect = btn.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;
  const elementAtPoint = document.elementFromPoint(centerX, centerY);
  console.log('按钮:', btn);
  console.log('该位置的元素:', elementAtPoint);
  console.log('是否被覆盖:', elementAtPoint !== btn);
  if (elementAtPoint !== btn) {
    elementAtPoint.style.outline = '3px solid red';
    console.log('已用红色边框标记覆盖元素');
  }
}
```

### 步骤 3：手动触发点击

```javascript
const btn = document.querySelector('[data-testid="menu-link-security"]');
if (btn) {
  console.log('找到按钮，触发点击...');
  btn.click();
} else {
  console.log('按钮未找到');
}
```

## 方法 3：查找所有可能的按钮

如果 `data-testid` 不存在，运行这个：

```javascript
const keywords = ['安全设置', '帮助中心', '用户协议', '设置'];
keywords.forEach(keyword => {
  const elements = Array.from(document.querySelectorAll('*')).filter(el => 
    el.textContent.includes(keyword) && 
    (el.tagName === 'BUTTON' || el.tagName === 'A' || el.tagName === 'DIV')
  );
  if (elements.length > 0) {
    console.log(`包含"${keyword}"的元素:`, elements);
    elements.forEach(el => {
      console.log('  -', el.tagName, el.className, el);
    });
  }
});
```

## 如何运行

1. 打开浏览器，访问应用
2. 按 `F12` 打开开发者工具
3. 点击 **Console**（控制台）标签
4. 点击控制台输入框（显示 `>` 的地方）
5. 复制上面的代码
6. 粘贴到控制台
7. 按 `Enter` 执行
8. 查看输出结果
9. 将完整的输出复制给我

