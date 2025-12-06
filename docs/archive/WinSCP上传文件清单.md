# WinSCP 上传文件清单

## ✅ 已修复的文件

### 1. ExchangePage.tsx（已修复类型错误）
- **本地路径**: `C:\hbgm001\frontend\src\pages\ExchangePage.tsx`
- **服务器路径**: `/opt/luckyred/frontend/src/pages/ExchangePage.tsx`
- **修复内容**: 修复了 `safePlaySound` 函数的类型错误

### 2. api.ts（包含所需函数）
- **本地路径**: `C:\hbgm001\frontend\src\utils\api.ts`
- **服务器路径**: `/opt/luckyred/frontend/src/utils/api.ts`
- **说明**: 包含 `exchangeCurrency` 和 `getExchangeRate` 函数

---

## 📁 需要上传的文件列表

### 必须上传的文件（修复构建错误）：

1. **ExchangePage.tsx**
   - 本地: `C:\hbgm001\frontend\src\pages\ExchangePage.tsx`
   - 服务器: `/opt/luckyred/frontend/src/pages/ExchangePage.tsx`

2. **api.ts**
   - 本地: `C:\hbgm001\frontend\src\utils\api.ts`
   - 服务器: `/opt/luckyred/frontend/src/utils/api.ts`

### 之前需要上传的文件（币种相关）：

3. **SendRedPacket.tsx**
   - 本地: `C:\hbgm001\frontend\src\pages\SendRedPacket.tsx`
   - 服务器: `/opt/luckyred/frontend/src/pages/SendRedPacket.tsx`

4. **Recharge.tsx**
   - 本地: `C:\hbgm001\frontend\src\pages\Recharge.tsx`
   - 服务器: `/opt/luckyred/frontend/src/pages/Recharge.tsx`

5. **Withdraw.tsx**
   - 本地: `C:\hbgm001\frontend\src\pages\Withdraw.tsx`
   - 服务器: `/opt/luckyred/frontend/src/pages/Withdraw.tsx`

6. **I18nProvider.tsx**
   - 本地: `C:\hbgm001\frontend\src\providers\I18nProvider.tsx`
   - 服务器: `/opt/luckyred/frontend/src/providers/I18nProvider.tsx`

---

## 🚀 WinSCP 上传步骤

### 1. 连接到服务器
- 主机名：`165.154.254.99`
- 用户名：`ubuntu`
- 密码：您的服务器密码

### 2. 上传文件到对应目录

#### 上传到 `/opt/luckyred/frontend/src/pages/` 目录：
- `SendRedPacket.tsx`
- `Recharge.tsx`
- `Withdraw.tsx`
- `ExchangePage.tsx` ⭐ **重要：已修复类型错误**

#### 上传到 `/opt/luckyred/frontend/src/utils/` 目录：
- `api.ts` ⭐ **重要：包含缺失的函数**

#### 上传到 `/opt/luckyred/frontend/src/providers/` 目录：
- `I18nProvider.tsx`

---

## ✅ 上传后验证步骤

### 在服务器上执行（SSH 连接）：

```bash
# 1. 验证文件已上传
cd /opt/luckyred/frontend/src/pages
grep -n "'Stars'" SendRedPacket.tsx
# 应该看到：430:            {['USDT', 'TON', 'Stars'].map((c) => (

# 2. 验证 api.ts 包含所需函数
cd ../utils
grep -n "export.*exchangeCurrency\|export.*getExchangeRate" api.ts
# 应该看到两行输出

# 3. 验证 ExchangePage.tsx 类型已修复
cd ../pages
grep -A 2 "safePlaySound" ExchangePage.tsx | head -3
# 应该看到类型定义，不是 string

# 4. 清除构建缓存
cd /opt/luckyred/frontend
rm -rf dist node_modules/.vite

# 5. 重新构建
npm run build

# 6. 检查构建是否成功（应该没有错误）
# 如果看到 "✓ built in X.XXs" 说明成功

# 7. 重启服务
cd /opt/luckyred
sudo systemctl restart luckyred-api
sudo systemctl restart luckyred-bot
sudo systemctl reload nginx
```

---

## 🔍 验证构建成功

构建成功后，您应该看到类似这样的输出：

```
✓ 1838 modules transformed.
dist/index.html                            0.72 kB │ gzip:  0.41 kB
dist/assets/index-DCK_bgri.css            76.20 kB │ gzip: 11.00 kB
...
✓ built in 8.37s
```

**不应该看到任何 TypeScript 错误！**

---

## ⚠️ 如果构建仍然失败

如果上传后构建仍然失败，请检查：

1. **文件是否真的上传成功**：
   ```bash
   ls -lh /opt/luckyred/frontend/src/pages/ExchangePage.tsx
   ls -lh /opt/luckyred/frontend/src/utils/api.ts
   ```

2. **文件内容是否正确**：
   ```bash
   # 检查 ExchangePage.tsx 的类型
   grep -A 2 "safePlaySound" /opt/luckyred/frontend/src/pages/ExchangePage.tsx
   
   # 检查 api.ts 的函数
   grep -n "exchangeCurrency\|getExchangeRate" /opt/luckyred/frontend/src/utils/api.ts
   ```

3. **查看完整的构建错误**：
   ```bash
   cd /opt/luckyred/frontend
   npm run build 2>&1 | tee build.log
   cat build.log
   ```

---

## 📝 快速检查清单

上传文件后，在服务器上执行这个命令快速检查：

```bash
cd /opt/luckyred/frontend/src && \
echo "=== 检查文件 ===" && \
echo "1. SendRedPacket.tsx:" && \
grep -n "'Stars'" pages/SendRedPacket.tsx | head -1 && \
echo "2. api.ts 函数:" && \
grep -n "export.*exchangeCurrency\|export.*getExchangeRate" utils/api.ts && \
echo "3. ExchangePage.tsx 类型:" && \
grep -A 1 "safePlaySound" pages/ExchangePage.tsx | head -2
```

如果所有检查都通过，说明文件已正确上传。

---

## ✅ 总结

**需要上传的文件**：
1. ✅ ExchangePage.tsx（已修复）
2. ✅ api.ts
3. ✅ SendRedPacket.tsx
4. ✅ Recharge.tsx
5. ✅ Withdraw.tsx
6. ✅ I18nProvider.tsx

**上传后必须执行**：
- 清除构建缓存
- 重新构建
- 重启服务

**验证**：
- 构建应该没有 TypeScript 错误
- 浏览器中应该显示 "Stars"（不是 "Star"）
