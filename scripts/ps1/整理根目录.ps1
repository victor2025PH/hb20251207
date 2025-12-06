# 整理根目录文件
# 将 .bat, .ps1, .sh, .md, .txt 文件分类整理到对应文件夹

$rootDir = "C:\hbgm001"
Set-Location $rootDir

# 创建文件夹结构
$folders = @(
    "scripts\bat",
    "scripts\ps1", 
    "scripts\sh",
    "scripts\txt",
    "docs\archive"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "创建文件夹: $folder" -ForegroundColor Green
    }
}

# 需要保留在根目录的重要文件
$keepInRoot = @(
    "README.md",
    "requirements.txt",
    "env.example.txt",
    "env-template.txt",
    ".env",
    ".gitignore"
)

# 需要保留的重要脚本（移动到 scripts 但保留在根目录的链接）
$importantScripts = @(
    "部署到服务器.bat",
    "快速功能测试.bat",
    "修复TelegramMiniApp-优化版.bat"
)

# 移动 .bat 文件
Write-Host "`n移动 .bat 文件..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.bat" -File | ForEach-Object {
    if ($_.Name -notin $keepInRoot) {
        $dest = Join-Path "scripts\bat" $_.Name
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  移动: $($_.Name) -> scripts\bat\" -ForegroundColor Cyan
    }
}

# 移动 .ps1 文件
Write-Host "`n移动 .ps1 文件..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.ps1" -File | ForEach-Object {
    if ($_.Name -notin $keepInRoot) {
        $dest = Join-Path "scripts\ps1" $_.Name
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  移动: $($_.Name) -> scripts\ps1\" -ForegroundColor Cyan
    }
}

# 移动 .sh 文件
Write-Host "`n移动 .sh 文件..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.sh" -File | ForEach-Object {
    if ($_.Name -notin $keepInRoot) {
        $dest = Join-Path "scripts\sh" $_.Name
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  移动: $($_.Name) -> scripts\sh\" -ForegroundColor Cyan
    }
}

# 移动 .txt 文件（除了 requirements.txt 和 env 相关）
Write-Host "`n移动 .txt 文件..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.txt" -File | ForEach-Object {
    if ($_.Name -notin $keepInRoot -and $_.Name -ne "requirements.txt") {
        $dest = Join-Path "scripts\txt" $_.Name
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  移动: $($_.Name) -> scripts\txt\" -ForegroundColor Cyan
    }
}

# 移动 .md 文件到 docs\archive（除了 README.md）
Write-Host "`n移动 .md 文件..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.md" -File | ForEach-Object {
    if ($_.Name -notin $keepInRoot -and $_.Name -ne "README.md") {
        # 检查是否已经在 docs 文件夹中
        $relativePath = $_.FullName.Replace($rootDir + "\", "")
        if (-not $relativePath.StartsWith("docs\")) {
            $dest = Join-Path "docs\archive" $_.Name
            # 如果目标文件已存在，添加时间戳
            if (Test-Path $dest) {
                $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
                $nameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
                $ext = [System.IO.Path]::GetExtension($_.Name)
                $dest = Join-Path "docs\archive" "$nameWithoutExt-$timestamp$ext"
            }
            Move-Item -Path $_.FullName -Destination $dest -Force
            Write-Host "  移动: $($_.Name) -> docs\archive\" -ForegroundColor Cyan
        }
    }
}

# 移动 Python 脚本到 scripts 文件夹
Write-Host "`n移动 Python 脚本..." -ForegroundColor Yellow
$pythonScripts = Get-ChildItem -Path . -Filter "*.py" -File | Where-Object { 
    $_.Name -notlike "test_*" -and 
    $_.Name -ne "check_db_schema.py" -and
    $_.Name -notin @("update-menu.py", "test_config.py", "test_miniapp_api.py", "test-bot-connection.py")
}
if (-not (Test-Path "scripts\py")) {
    New-Item -ItemType Directory -Path "scripts\py" -Force | Out-Null
}
foreach ($script in $pythonScripts) {
    $dest = Join-Path "scripts\py" $script.Name
    Move-Item -Path $script.FullName -Destination $dest -Force
    Write-Host "  移动: $($script.Name) -> scripts\py\" -ForegroundColor Cyan
}

Write-Host "`n整理完成！" -ForegroundColor Green
Write-Host "`n重要脚本位置：" -ForegroundColor Yellow
Write-Host "  - scripts\bat\ - 所有 .bat 文件" -ForegroundColor Cyan
Write-Host "  - scripts\ps1\ - 所有 .ps1 文件" -ForegroundColor Cyan
Write-Host "  - scripts\sh\ - 所有 .sh 文件" -ForegroundColor Cyan
Write-Host "  - scripts\txt\ - 所有 .txt 文件（除了 requirements.txt）" -ForegroundColor Cyan
Write-Host "  - docs\archive\ - 所有 .md 文件（除了 README.md）" -ForegroundColor Cyan

