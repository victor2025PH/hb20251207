# PowerShell 运行批处理文件说明

## ❌ 问题原因

在 PowerShell 中，直接输入文件名不会执行当前目录下的文件。这是 PowerShell 的安全特性。

### 错误示例

```powershell
一键启动测试.bat
# 错误：无法将"一键启动测试.bat"项识别为 cmdlet...
```

### 原因

PowerShell 默认不会从当前位置（当前目录）加载命令，需要明确指定路径。

## ✅ 正确的运行方式

### 方法 1: 使用 `.\` 前缀（推荐）

```powershell
.\一键启动测试.bat
```

### 方法 2: 使用完整路径

```powershell
C:\hbgm001\一键启动测试.bat
```

### 方法 3: 使用 `&` 操作符

```powershell
& ".\一键启动测试.bat"
```

### 方法 4: 使用 `cmd` 命令

```powershell
cmd /c "一键启动测试.bat"
```

## 🎯 推荐方式

**最简单的方式**：在 PowerShell 中使用 `.\` 前缀

```powershell
cd c:\hbgm001
.\一键启动测试.bat
```

## 📝 其他启动脚本

所有批处理文件都需要使用 `.\` 前缀：

```powershell
.\全自动启动测试.bat
.\检查Bot状态.bat
.\运行迁移.bat
.\启动机器人-详细.bat
```

## 💡 提示

如果经常使用，可以创建一个 PowerShell 别名：

```powershell
Set-Alias -Name startbot -Value ".\一键启动测试.bat"
# 然后就可以直接使用
startbot
```

---

**记住：在 PowerShell 中运行当前目录的文件，需要使用 `.\` 前缀！** 🎯
