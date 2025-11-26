# 🧧 Lucky Red (搶紅包)

Telegram 紅包遊戲平台 - 發紅包、搶紅包、簽到賺積分

## 🏗️ 項目結構

```
hbgm001/
├── bot/                    # Telegram Bot
│   ├── main.py
│   ├── handlers/
│   ├── keyboards/
│   └── utils/
├── api/                    # MiniApp & Admin API (FastAPI)
│   ├── main.py
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   └── services/
├── frontend/               # MiniApp 前端 (React + Vite)
│   ├── src/
│   ├── public/
│   └── package.json
├── admin/                  # Admin 後台前端
│   ├── src/
│   └── package.json
├── shared/                 # 共享代碼
│   ├── database/
│   └── config/
├── deploy/                 # 部署腳本
│   ├── nginx/
│   ├── systemd/
│   └── scripts/
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🚀 技術棧

- **前端**: React 18 + TypeScript + Vite + Tailwind CSS
- **後端**: Python 3.11 + FastAPI
- **數據庫**: PostgreSQL
- **Bot**: python-telegram-bot
- **部署**: Nginx + Systemd + Ubuntu 22.04

## 🌐 域名配置

| 服務 | 域名 |
|------|------|
| Telegram Bot | bot.usdt2026.cc |
| Admin 後台 | admin.usdt2026.cc |
| MiniApp | mini.usdt2026.cc |

## ✨ 核心功能

- 💰 發紅包 (USDT/TON/Stars)
- 🎁 搶紅包
- 💳 充值/提現
- 👛 用戶錢包
- 📅 每日簽到
- 👥 邀請返佣
- 🎮 金福寶局 (遊戲跳轉)
- ⚙️ 管理後台

## 🌍 多語言支持

- 繁體中文 (zh-TW)
- 简体中文 (zh-CN)
- English (en)

## 📦 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements.txt
cd frontend && npm install

# 2. 配置環境變量
cp .env.example .env
# 編輯 .env 填入實際值

# 3. 啟動開發服務器
python api/main.py      # API 服務
python bot/main.py      # Bot 服務
cd frontend && npm run dev  # 前端
```

## 📄 License

MIT
