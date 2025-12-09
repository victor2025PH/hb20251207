# 快速测试指南

## 🚀 立即开始测试

### 1. 访问后台管理面板

打开浏览器，访问：**https://admin.usdt2026.cc**

---

### 2. 测试核心功能

#### ✅ 红包退款
- 进入 **"红包管理"** → 选择红包 → 点击 **"退款"**

#### ✅ 交易余额分类
- 进入 **"交易管理"** → 查看 USDT 交易的 **"真实余额"** 和 **"奖励余额"** 列

#### ✅ 推荐系统配置
- 进入 **"邀请管理"** → 找到 **"佣金配置"** → 修改并保存

#### ✅ 红包雨调度
- 进入 **"红包管理"** → 点击 **"调度红包雨"** → 填写表单并提交

---

### 3. 生成测试数据（可选）

```bash
ssh ubuntu@165.154.254.99 "cd /home/ubuntu/hbgm001 && source .venv/bin/activate && python3 scripts/py/seed_referral_tree.py"
```

然后在 **"邀请管理"** 中查看测试用户的推荐关系树。

---

## 📚 详细文档

- **完整验证清单**: `docs/next-steps-verification.md`
- **部署总结**: `docs/deployment-complete-summary.md`
- **实现文档**: `docs/system-integration-upgrade.md`

---

**所有功能已部署完成，可以开始测试！** 🎉

