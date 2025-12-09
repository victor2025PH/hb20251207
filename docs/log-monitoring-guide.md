# 日志监控指南

本指南介绍如何监控和查看项目日志，帮助排查问题。

## 📋 目录

1. [日志位置](#日志位置)
2. [快速命令](#快速命令)
3. [实时监控](#实时监控)
4. [查看历史日志](#查看历史日志)
5. [过滤日志](#过滤日志)
6. [常见问题排查](#常见问题排查)

---

## 日志位置

项目使用 `systemd` 管理服务，日志存储在 systemd journal 中。

### 服务名称

- **API 服务**: `hbgm001-backend`
- **Bot 服务**: `hbgm001-bot`

### 日志存储位置

- systemd journal: `/var/log/journal/` (二进制格式)
- 通过 `journalctl` 命令查看

---

## 快速命令

### 1. 实时监控所有日志

```bash
# 监控所有服务
./scripts/sh/monitor-logs.sh

# 或直接使用 journalctl
journalctl -u hbgm001-backend -u hbgm001-bot -f
```

### 2. 查看最近日志

```bash
# 查看最近 100 行
./scripts/sh/view-logs.sh all 100

# 查看 API 服务最近 50 行
./scripts/sh/view-logs.sh api 50

# 查看 Bot 服务最近 50 行
./scripts/sh/view-logs.sh bot 50
```

### 3. 查找红包相关日志

```bash
# 查找最近 1 小时的红包日志
./scripts/sh/find-redpacket-logs.sh

# 查找最近 30 分钟的红包日志
./scripts/sh/find-redpacket-logs.sh "30 minutes ago"
```

---

## 实时监控

### 监控所有服务

```bash
# 使用脚本
./scripts/sh/monitor-logs.sh all

# 或直接使用 journalctl
journalctl -u hbgm001-backend -u hbgm001-bot -f
```

### 监控单个服务

```bash
# API 服务
./scripts/sh/monitor-logs.sh api
# 或
journalctl -u hbgm001-backend -f

# Bot 服务
./scripts/sh/monitor-logs.sh bot
# 或
journalctl -u hbgm001-bot -f
```

### 监控并过滤关键词

```bash
# 监控包含"红包"的日志
./scripts/sh/monitor-logs.sh all 红包

# 监控包含"错误"的日志
journalctl -u hbgm001-backend -u hbgm001-bot -f | grep -i "错误\|error"

# 监控红包发送相关日志
journalctl -u hbgm001-backend -f | grep -iE "红包|發送|群組|send|redpacket"
```

---

## 查看历史日志

### 查看最近日志

```bash
# 最近 100 行
journalctl -u hbgm001-backend -n 100

# 最近 50 行，包含时间戳
journalctl -u hbgm001-backend -n 50 --no-pager
```

### 按时间范围查看

```bash
# 最近 1 小时
journalctl -u hbgm001-backend --since "1 hour ago"

# 最近 30 分钟
journalctl -u hbgm001-backend --since "30 minutes ago"

# 今天
journalctl -u hbgm001-backend --since today

# 指定时间范围
journalctl -u hbgm001-backend --since "2025-12-10 08:00:00" --until "2025-12-10 10:00:00"
```

### 查看特定时间段的日志

```bash
# 查看今天 08:00 到 10:00 的日志
journalctl -u hbgm001-backend --since "2025-12-10 08:00:00" --until "2025-12-10 10:00:00"
```

---

## 过滤日志

### 按关键词过滤

```bash
# 查找包含"红包"的日志
journalctl -u hbgm001-backend | grep -i "红包"

# 查找包含"错误"的日志
journalctl -u hbgm001-backend | grep -iE "错误|error|failed"

# 查找红包发送相关日志
journalctl -u hbgm001-backend | grep -iE "红包|發送|群組|send|redpacket|chat_id"
```

### 按日志级别过滤

```bash
# 只查看错误日志
journalctl -u hbgm001-backend -p err

# 查看警告及以上级别
journalctl -u hbgm001-backend -p warning
```

### 组合过滤

```bash
# 最近 1 小时，包含"红包"和"发送"的日志
journalctl -u hbgm001-backend --since "1 hour ago" | grep -iE "红包.*發送|發送.*紅包"

# 最近 30 分钟，包含"错误"的日志
journalctl -u hbgm001-backend --since "30 minutes ago" | grep -i "错误\|error"
```

---

## 常见问题排查

### 1. 红包发送失败

```bash
# 查找红包发送相关日志
journalctl -u hbgm001-backend --since "1 hour ago" | grep -iE "紅包|發送|群組|send|redpacket"

# 查找错误日志
journalctl -u hbgm001-backend --since "1 hour ago" -p err | grep -i "红包"
```

### 2. 机器人未发送消息

```bash
# 查找机器人相关日志
journalctl -u hbgm001-backend --since "1 hour ago" | grep -iE "機器人|bot|chat_id|群組"

# 查找发送消息的日志
journalctl -u hbgm001-backend --since "1 hour ago" | grep -iE "發送|send.*message|✅|❌"
```

### 3. API 错误

```bash
# 查看所有错误
journalctl -u hbgm001-backend -p err --since "1 hour ago"

# 查看警告
journalctl -u hbgm001-backend -p warning --since "1 hour ago"
```

### 4. 服务状态

```bash
# 查看服务状态
sudo systemctl status hbgm001-backend
sudo systemctl status hbgm001-bot

# 查看服务启动日志
journalctl -u hbgm001-backend -b
```

---

## 高级用法

### 导出日志到文件

```bash
# 导出最近 1 小时的日志
journalctl -u hbgm001-backend --since "1 hour ago" > /tmp/api-logs.txt

# 导出包含"红包"的日志
journalctl -u hbgm001-backend --since "1 hour ago" | grep -i "红包" > /tmp/redpacket-logs.txt
```

### 统计错误数量

```bash
# 统计最近 1 小时的错误数量
journalctl -u hbgm001-backend --since "1 hour ago" -p err | wc -l
```

### 查看日志并高亮关键词

```bash
# 使用 grep 高亮
journalctl -u hbgm001-backend -f | grep --color=always -iE "错误|error|红包|發送"
```

---

## 提示

1. **使用 `-f` 参数实时监控**：`journalctl -u SERVICE -f`
2. **使用 `--since` 指定时间范围**：避免查看过多日志
3. **使用 `grep` 过滤关键词**：快速定位问题
4. **使用 `-p` 过滤日志级别**：只看错误或警告
5. **使用 `-n` 限制行数**：避免输出过多

---

## 快速参考

```bash
# 实时监控所有服务
journalctl -u hbgm001-backend -u hbgm001-bot -f

# 查看最近 100 行
journalctl -u hbgm001-backend -n 100

# 查看最近 1 小时的红包日志
journalctl -u hbgm001-backend --since "1 hour ago" | grep -i "红包"

# 查看错误日志
journalctl -u hbgm001-backend -p err --since "1 hour ago"

# 查找特定关键词
journalctl -u hbgm001-backend -f | grep -i "关键词"
```

