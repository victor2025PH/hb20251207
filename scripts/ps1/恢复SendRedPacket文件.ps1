# 从服务器恢复 SendRedPacket.tsx 文件

Write-Host "正在从服务器恢复文件..." -ForegroundColor Yellow

$serverPath = "/opt/luckyred/frontend/src/pages/SendRedPacket.tsx"
$localPath = "frontend/src/pages/SendRedPacket.tsx"
$server = "ubuntu@165.154.254.99"

# 方法1: 使用 scp
Write-Host "`n方法1: 使用 scp 下载..." -ForegroundColor Cyan
scp "${server}:${serverPath}" $localPath 2>&1

if (Test-Path $localPath) {
    $content = Get-Content $localPath -Raw
    if ($content.Length -gt 1000 -and $content -match "import.*useState") {
        Write-Host "✓ 文件已成功恢复！" -ForegroundColor Green
        Write-Host "文件大小: $($content.Length) 字符" -ForegroundColor Gray
        Write-Host "`n前10行内容:" -ForegroundColor Cyan
        Get-Content $localPath | Select-Object -First 10
        exit 0
    }
}

# 方法2: 使用 ssh + 重定向
Write-Host "`n方法2: 使用 ssh 下载..." -ForegroundColor Cyan
ssh $server "cat $serverPath" > $localPath 2>&1

if (Test-Path $localPath) {
    $content = Get-Content $localPath -Raw
    if ($content.Length -gt 1000 -and $content -match "import.*useState") {
        Write-Host "✓ 文件已成功恢复！" -ForegroundColor Green
        Write-Host "文件大小: $($content.Length) 字符" -ForegroundColor Gray
        Write-Host "`n前10行内容:" -ForegroundColor Cyan
        Get-Content $localPath | Select-Object -First 10
        exit 0
    }
}

# 方法3: 从 git 恢复
Write-Host "`n方法3: 从服务器 git 仓库恢复..." -ForegroundColor Cyan
$gitContent = ssh $server "cd /opt/luckyred && git show HEAD:frontend/src/pages/SendRedPacket.tsx" 2>&1

if ($gitContent -and $gitContent.Length -gt 1000 -and $gitContent -match "import.*useState") {
    [System.IO.File]::WriteAllText((Resolve-Path .).Path + "\" + $localPath, $gitContent, [System.Text.Encoding]::UTF8)
    Write-Host "✓ 文件已从 git 恢复！" -ForegroundColor Green
    Write-Host "文件大小: $($gitContent.Length) 字符" -ForegroundColor Gray
    Write-Host "`n前10行内容:" -ForegroundColor Cyan
    Get-Content $localPath | Select-Object -First 10
    exit 0
}

Write-Host "`n✗ 所有方法都失败了。请手动从服务器复制文件。" -ForegroundColor Red
Write-Host "服务器路径: $serverPath" -ForegroundColor Yellow
Write-Host "本地路径: $localPath" -ForegroundColor Yellow
