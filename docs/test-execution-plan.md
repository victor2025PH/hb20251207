# 功能测试执行计划

## 🎯 测试目标

验证以下功能是否正常工作：
1. ✅ 后台管理面板访问
2. ✅ 红包退款功能
3. ✅ 交易管理余额分类显示
4. ✅ 推荐系统配置管理
5. ✅ 红包雨调度功能
6. ✅ 推荐关系树可视化（可选）

---

## 📋 测试步骤

### 步骤 1: 验证后台访问

**操作**:
1. 打开浏览器，访问：`https://admin.usdt2026.cc`
2. 检查页面是否正常加载

**预期结果**:
- ✅ 页面显示登录界面
- ✅ 没有 404 错误
- ✅ HTTPS 证书有效（浏览器显示锁图标）

**如果失败**:
```bash
# 检查 Nginx 配置
ssh ubuntu@165.154.254.99 "sudo nginx -t"

# 检查前端文件
ssh ubuntu@165.154.254.99 "ls -la /home/ubuntu/hbgm001/admin/frontend/dist/index.html"
```

---

### 步骤 2: 登录后台管理面板

**操作**:
1. 使用管理员账号登录
2. 验证登录是否成功

**预期结果**:
- ✅ 登录成功，跳转到后台首页
- ✅ 可以看到所有菜单项（红包管理、交易管理、邀请管理等）

**如果失败**:
```bash
# 查看后端日志
ssh ubuntu@165.154.254.99 "sudo journalctl -u hbgm001-backend -n 30 --no-pager | grep -i error"
```

---

### 步骤 3: 测试红包退款功能

**操作**:
1. 进入 **"红包管理"** 页面
2. 找到一个**未领取**或**已过期**的红包
3. 点击 **"退款"** 按钮
4. 确认退款操作

**预期结果**:
- ✅ 显示"退款成功"提示
- ✅ 红包状态变为"已退款"
- ✅ 发送者余额已增加（可通过"用户管理"查看）

**验证命令**:
```bash
# 查看后端日志中的退款操作
ssh ubuntu@165.154.254.99 "sudo journalctl -u hbgm001-backend -n 50 --no-pager | grep -i refund"
```

---

### 步骤 4: 测试交易管理余额分类

**操作**:
1. 进入 **"交易管理"** 页面
2. 查看交易列表
3. 检查 USDT 交易的余额分类显示

**预期结果**:
- ✅ 每行交易显示 **"余额分类"** 列
- ✅ USDT 交易显示：
  - **"真实余额"**（绿色标签）
  - **"奖励余额"**（橙色标签）
- ✅ 其他币种显示 "-"

**验证要点**:
- 真实余额：用户充值或提现的金额
- 奖励余额：游戏奖励、推荐佣金等

---

### 步骤 5: 测试推荐系统配置

**操作**:
1. 进入 **"邀请管理"** 页面
2. 找到 **"佣金配置"** 卡片
3. 修改配置：
   - 一级佣金率：`5%` (0.05)
   - 二级佣金率：`2%` (0.02)
   - 代理奖励阈值：`100`
4. 点击 **"保存配置"** 按钮
5. 刷新页面，验证配置是否保存

**预期结果**:
- ✅ 显示"保存成功"提示
- ✅ 刷新页面后，配置仍然存在
- ✅ 配置已保存到数据库

**验证命令**:
```bash
# 检查数据库中的配置
ssh ubuntu@165.154.254.99 "cd /home/ubuntu/hbgm001 && source .venv/bin/activate && python3 -c \"
from shared.database.connection import AsyncSessionLocal
from sqlalchemy import text
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text('SELECT key, value FROM system_config WHERE key LIKE \\'%commission%\\' OR key LIKE \\'%invite%\\''))
        rows = result.fetchall()
        print('推荐系统配置:')
        for row in rows:
            print(f'  {row[0]}: {row[1]}')

asyncio.run(check())
\""
```

---

### 步骤 6: 测试红包雨调度功能

**操作**:
1. 进入 **"红包管理"** 页面
2. 点击 **"调度红包雨"** 按钮
3. 填写表单：
   - **开始时间**：未来某个时间（例如：1小时后）
   - **总金额**：`100` USDT
   - **红包数量**：`10`
   - **目标群组ID**：留空（公开红包）
   - **消息**：`测试红包雨`
4. 点击 **"确定"** 按钮

**预期结果**:
- ✅ 显示"调度成功"提示
- ✅ 调度记录已创建

**验证命令**:
```bash
# 检查调度记录
ssh ubuntu@165.154.254.99 "cd /home/ubuntu/hbgm001 && source .venv/bin/activate && python3 -c \"
from shared.database.connection import AsyncSessionLocal
from sqlalchemy import text
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text('SELECT id, start_time, total_amount, packet_count, status FROM scheduled_redpacket_rains ORDER BY created_at DESC LIMIT 5'))
        rows = result.fetchall()
        print('最近5条调度记录:')
        for row in rows:
            print(f'  ID: {row[0]}, 开始时间: {row[1]}, 总金额: {row[2]}, 数量: {row[3]}, 状态: {row[4]}')

asyncio.run(check())
\""
```

---

### 步骤 7: 生成并测试推荐关系树（可选）

**操作**:
1. 在服务器上运行测试数据脚本：
```bash
ssh ubuntu@165.154.254.99 "cd /home/ubuntu/hbgm001 && source .venv/bin/activate && python3 scripts/py/seed_referral_tree.py"
```

2. 在后台管理面板中：
   - 进入 **"邀请管理"** 页面
   - 在列表中找到一个测试用户（username 以 `test_` 开头）
   - 点击 **"查看关系树"** 按钮

**预期结果**:
- ✅ 关系树正常显示
- ✅ 可以看到3层推荐关系
- ✅ 每个节点显示用户信息

**推荐关系结构**:
```
test_root_user
  ├── test_user_1
  │   ├── test_user_1_1
  │   └── test_user_1_2
  └── test_user_2
      └── test_user_2_1
```

---

## 🔍 问题排查

### 如果某个功能不工作

1. **检查后端服务状态**:
   ```bash
   ssh ubuntu@165.154.254.99 "sudo systemctl status hbgm001-backend"
   ```

2. **查看后端日志**:
   ```bash
   ssh ubuntu@165.154.254.99 "sudo journalctl -u hbgm001-backend -n 100 --no-pager | tail -50"
   ```

3. **检查 API 端点**:
   ```bash
   ssh ubuntu@165.154.254.99 "curl -s http://127.0.0.1:8080/api/v1/admin/health"
   ```

4. **检查前端控制台**:
   - 打开浏览器开发者工具（F12）
   - 查看 Console 和 Network 标签
   - 检查是否有错误信息

---

## ✅ 测试完成标准

所有功能测试完成后，应该满足：

- [x] 后台管理面板可以正常访问
- [x] 可以正常登录
- [x] 红包退款功能正常工作
- [x] 交易管理显示余额分类
- [x] 推荐系统配置可以保存和读取
- [x] 红包雨调度功能可以创建调度记录
- [x] 推荐关系树可以正常显示（如果生成了测试数据）

---

## 📝 测试记录模板

```
测试日期: ___________
测试人员: ___________

功能测试结果:
□ 后台访问 - 通过 / 失败
□ 登录功能 - 通过 / 失败
□ 红包退款 - 通过 / 失败
□ 交易余额分类 - 通过 / 失败
□ 推荐系统配置 - 通过 / 失败
□ 红包雨调度 - 通过 / 失败
□ 推荐关系树 - 通过 / 失败

发现问题:
1. _________________________________
2. _________________________________

备注:
_________________________________
```

---

**开始测试**: 按照上述步骤逐一验证每个功能！

