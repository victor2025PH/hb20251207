# 📁 脚本文件说明

本文件夹包含项目中的所有脚本文件，按类型分类存放。

## 📂 文件夹结构

```
scripts/
├── bat/          # Windows 批处理脚本 (.bat)
├── ps1/          # PowerShell 脚本 (.ps1)
├── sh/           # Shell 脚本 (.sh) - 用于 Linux/服务器
├── py/           # Python 脚本 (.py)
└── txt/          # 文本文件 (.txt) - 手动命令、配置说明等
```

## 🔍 常用脚本

### 部署相关
- `scripts/bat/部署到服务器.bat` - 部署到服务器
- `scripts/bat/快速功能测试.bat` - 快速功能测试
- `scripts/bat/修复TelegramMiniApp-优化版.bat` - 修复 MiniApp SSL

### 开发相关
- `scripts/bat/start-dev.bat` - 启动开发环境
- `scripts/ps1/start-local-dev.ps1` - 启动本地开发

### 服务器相关
- `scripts/sh/server-deploy.sh` - 服务器部署脚本
- `scripts/sh/quick-deploy.sh` - 快速部署脚本

## 📝 使用说明

### Windows 本地脚本
在项目根目录执行：
```cmd
scripts\bat\脚本名称.bat
```

### PowerShell 脚本
```powershell
.\scripts\ps1\脚本名称.ps1
```

### 服务器脚本
上传到服务器后执行：
```bash
bash scripts/sh/脚本名称.sh
```

## ⚠️ 注意事项

1. **不要将脚本文件放在根目录**
   - 所有新创建的脚本都应该放在对应的 `scripts/` 子文件夹中

2. **脚本命名规范**
   - 使用有意义的名称
   - 避免使用特殊字符
   - 中文脚本名也可以，但建议使用英文

3. **文档文件**
   - 所有 `.md` 文件应该放在 `docs/` 文件夹
   - 临时文档可以放在 `docs/archive/`

## 🔄 如何添加新脚本

1. **确定脚本类型**
   - `.bat` → `scripts/bat/`
   - `.ps1` → `scripts/ps1/`
   - `.sh` → `scripts/sh/`
   - `.py` → `scripts/py/`

2. **创建脚本文件**
   - 在对应的文件夹中创建新文件
   - 不要放在根目录

3. **更新文档**
   - 如果是重要脚本，更新本 README
   - 添加使用说明

## 📚 相关文档

- 项目主 README: `../README.md`
- 部署文档: `../docs/`
- 测试文档: `../docs/archive/下一步测试清单.md`

