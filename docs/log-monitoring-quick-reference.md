# 日志监控快速参考

## 🚀 快速命令

### 实时监控（最常用）

```bash
# 监控所有服务（推荐）
journalctl -u hbgm001-backend -u hbgm001-bot -f

# 监控 API 服务
journalctl -u hbgm001-backend -f

# 监控 Bot 服务
journalctl -u hbgm001-bot -f

# 监控并过滤关键词（红包相关）
journalctl -u hbgm001-backend -f | grep -iE "红包|發送|群組|send|redpacket"
```

### 查看历史日志

```bash
# 最近 100 行
journalctl -u hbgm001-backend -n 100

# 最近 1 小时
journalctl -u hbgm001-backend --since "1 hour ago"

# 今天
journalctl -u hbgm001-backend --since today
```

### 查找红包发送问题

```bash
# 查找最近 1 小时的红包发送日志
journalctl -u hbgm001-backend --since "1 hour ago" | grep -iE "紅包|發送|群組|chat_id|機器人|✅|❌"

# 查找错误日志
journalctl -u hbgm001-backend --since "1 hour ago" -p err | grep -i "红包"
```

---

## 📝 使用脚本（在服务器上）

### 监控脚本

```bash
# 监控所有服务
./scripts/sh/monitor-logs.sh

# 监控 API 服务
./scripts/sh/monitor-logs.sh api

# 监控并过滤
./scripts/sh/monitor-logs.sh all 红包
```

### 查看日志脚本

```bash
# 查看最近 100 行
./scripts/sh/view-logs.sh all 100

# 查看包含"红包"的日志
./scripts/sh/view-logs.sh api 200 红包
```

### 查找红包日志

```bash
# 查找最近 1 小时的红包日志
./scripts/sh/find-redpacket-logs.sh

# 查找最近 30 分钟
./scripts/sh/find-redpacket-logs.sh "30 minutes ago"
```

---

## 🔍 常用过滤关键词

- `红包` / `redpacket` - 红包相关
- `發送` / `send` - 发送相关
- `群組` / `chat_id` - 群组相关
- `機器人` / `bot` - 机器人相关
- `錯誤` / `error` - 错误日志
- `✅` / `❌` / `⚠️` - 状态标记

---

## 💡 提示

1. **使用 `-f` 实时监控**：`journalctl -u SERVICE -f`
2. **使用 `--since` 限制时间范围**：避免输出过多
3. **使用 `grep` 过滤关键词**：快速定位问题
4. **使用 `-p err` 只看错误**：`journalctl -u SERVICE -p err`

