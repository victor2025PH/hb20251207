@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   檢查服務器上的部署路徑
echo ========================================
echo.

set SERVER=ubuntu@165.154.254.99

echo 正在檢查服務器上的路徑...
echo.

echo [1] 檢查 /opt/luckyred 是否存在
ssh -o ConnectTimeout=10 %SERVER% "if [ -d /opt/luckyred ]; then echo '[OK] /opt/luckyred 存在'; ls -la /opt/luckyred | head -10; else echo '[ERROR] /opt/luckyred 不存在'; fi"
echo.

echo [2] 檢查 /home/ubuntu/hbgm001 是否存在
ssh -o ConnectTimeout=10 %SERVER% "if [ -d /home/ubuntu/hbgm001 ]; then echo '[OK] /home/ubuntu/hbgm001 存在'; ls -la /home/ubuntu/hbgm001 | head -10; else echo '[ERROR] /home/ubuntu/hbgm001 不存在'; fi"
echo.

echo [3] 檢查當前用戶主目錄
ssh -o ConnectTimeout=10 %SERVER% "echo '當前目錄:' && pwd && echo && echo '主目錄內容:' && ls -la ~ | head -10"
echo.

echo [4] 查找可能的部署目錄
ssh -o ConnectTimeout=10 %SERVER% "echo '查找包含 luckyred 的目錄:' && find /opt /home -type d -name '*luckyred*' 2>/dev/null | head -10 || echo '未找到'"
echo.

echo [5] 檢查服務文件中的路徑
ssh -o ConnectTimeout=10 %SERVER% "if [ -f /etc/systemd/system/luckyred-api.service ]; then echo '[OK] 服務文件存在'; grep -E 'WorkingDirectory|ExecStart' /etc/systemd/system/luckyred-api.service; else echo '[ERROR] 服務文件不存在'; fi"
echo.

echo ========================================
echo   檢查完成
echo ========================================
echo.
echo 請根據上面的結果確定實際的部署路徑
echo.

