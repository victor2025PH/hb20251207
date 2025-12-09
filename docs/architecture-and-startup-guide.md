# 📋 Architecture and Startup Guide

## 1. 📂 Project Structure

```
hbgm001/
├── api/                    # FastAPI Backend Service (RESTful API)
│   ├── main.py            # API entry point ⭐
│   ├── routers/           # API routes (auth, users, redpackets, wallet, etc.)
│   ├── services/          # Business logic service layer
│   ├── middleware/        # Middleware (rate limit, monitoring, anti-sybil)
│   ├── utils/             # Utility functions (auth, Telegram verification)
│   └── workers/           # Background task workers
│
├── bot/                    # Telegram Bot Service
│   ├── main.py            # Bot entry point ⭐
│   ├── handlers/          # Message handlers (commands, callbacks, messages)
│   ├── keyboards/         # Keyboard layouts (reply keyboard, inline keyboard)
│   └── utils/             # Bot utility functions
│
├── admin/                  # Admin Dashboard (optional)
│   └── src/main.py        # Admin dashboard entry point
│
├── frontend/               # Frontend MiniApp (React + TypeScript)
│   └── src/               # Frontend source code
│
├── shared/                 # Shared modules (used by both Bot and API)
│   ├── config/            # Configuration management (reads from .env)
│   └── database/           # Database connection and models
│
├── deploy/                 # Deployment files
│   ├── first-deploy.sh    # First deployment script
│   ├── update-deploy.sh   # Update deployment script
│   └── systemd/           # systemd service configuration files
│
├── scripts/                # Utility scripts
│   ├── py/                # Python utility scripts
│   ├── sh/                # Shell scripts
│   └── bat/               # Windows batch scripts
│
├── requirements.txt        # Python dependencies (root directory)
├── .env                    # Environment variables (needs to be created manually)
└── env-template.txt        # Environment variables template
```

### Core Directory Descriptions

- **`api/`**: FastAPI backend service providing RESTful API endpoints
- **`bot/`**: Telegram Bot service handling user interactions
- **`shared/`**: Shared configuration and database modules used by both Bot and API
- **`frontend/`**: Telegram MiniApp frontend application
- **`deploy/`**: Deployment scripts and configuration files

---

## 2. 🚀 Startup Entry Points (Most Important)

### ❌ Wrong Way

```bash
# ❌ Error: No main.py in root directory
python3 main.py
```

### ✅ Correct Startup Commands (Linux Server)

#### **Method 1: Start API Backend (Recommended)**

```bash
# From project root directory
cd /home/ubuntu/hbgm001

# Activate virtual environment (if using)
source .venv/bin/activate

# Start API - MUST run from project root
python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8080 --workers 4
```

**✅ Correct**: `python3 -m uvicorn api.main:app` (from root directory)

#### **Method 2: Start Telegram Bot**

```bash
# From project root directory
cd /home/ubuntu/hbgm001

# Activate virtual environment (if using)
source .venv/bin/activate

# Start Bot
python3 bot/main.py
```

**✅ Correct**: `python3 bot/main.py` (from root directory)

#### **Method 3: Start Both Services (Two Terminals)**

**Terminal 1 - API:**
```bash
cd /home/ubuntu/hbgm001
source .venv/bin/activate
python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8080
```

**Terminal 2 - Bot:**
```bash
cd /home/ubuntu/hbgm001
source .venv/bin/activate
python3 bot/main.py
```

#### **Method 4: Use systemd Service (Production)**

```bash
# Start API service
sudo systemctl start hbgm001-backend

# Start Bot service
sudo systemctl start luckyred-bot

# Check service status
sudo systemctl status hbgm001-backend
sudo systemctl status luckyred-bot

# Or use unified startup script (if systemd services are configured)
bash scripts/sh/啟動所有服務.sh
```

### 📝 Important Notes

1. **Root directory has NO `main.py`** - That's why `python3 main.py` fails
2. **API must run from root**: `python3 -m uvicorn api.main:app` (not from `api/` directory)
3. **Bot must run from root**: `python3 bot/main.py` (not from `bot/` directory)
4. **Both services need to run simultaneously** - API and Bot are separate processes

---

## 3. ⚙️ Core Runtime Logic

### Architecture Diagram

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ Telegram Bot │   │  MiniApp     │
│  (bot/)      │   │  (frontend/) │
└──────┬───────┘   └──────┬───────┘
       │                  │
       │                  │
       └────────┬─────────┘
                │
                ▼
        ┌──────────────┐
        │  FastAPI     │
        │  (api/)      │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │  Database    │
        │ (PostgreSQL/ │
        │   SQLite)    │
        └──────────────┘
```

### Interaction Flow

#### **1. Bot and API Interaction (Hybrid Model)**

The Bot uses a **hybrid approach** - sometimes calling API, sometimes directly accessing database:

**A. Bot → API (via HTTP)**
- Bot uses `bot/utils/api_client.py` to call API endpoints
- Used for complex operations, consistency, and when MiniApp also needs the same functionality
- Example: Creating red packets, complex wallet operations

**B. Bot → Database (Direct)**
- Bot directly accesses database using `shared/database/connection.py`
- Used for simple operations, faster response, and operations specific to Bot
- Example: Simple check-in, user queries, balance display

**Example Flow A (Bot calls API)**:
```
User clicks "Send Red Packet" button in Bot
  ↓
Bot handler receives callback (bot/handlers/redpacket.py)
  ↓
Bot calls API: POST /api/redpackets/create (via bot/utils/api_client.py)
  ↓
API processes request (api/routers/redpackets.py)
  ↓
API queries/updates database (shared/database/)
  ↓
API returns result to Bot
  ↓
Bot formats and sends confirmation message to user
```

**Example Flow B (Bot directly accesses DB)**:
```
User sends /checkin command
  ↓
Bot handler receives command (bot/handlers/checkin.py)
  ↓
Bot directly queries database (shared/database/connection.py)
  ↓
Bot updates user check-in status directly
  ↓
Bot sends confirmation message to user
```

**Why Hybrid?**
- **Direct DB access**: Faster for simple operations, less overhead
- **API calls**: Better for complex operations, ensures consistency with MiniApp, centralized business logic

#### **2. MiniApp and API Interaction**

- **MiniApp** (`frontend/`) is a React frontend application
- User opens MiniApp in Telegram
- MiniApp **always** calls **API** endpoints via HTTP requests (never directly accesses database)
- API verifies Telegram `initData` for authentication
- API returns JSON data, MiniApp renders interface

**Example Flow**:
```
User opens MiniApp in Telegram
  ↓
MiniApp gets Telegram initData (frontend/src/utils/telegram.ts)
  ↓
MiniApp calls API: GET /api/v1/users/me (with X-Telegram-Init-Data header)
  ↓
API verifies initData (api/utils/telegram_auth.py)
  ↓
API queries database for user info (shared/database/)
  ↓
API returns JSON data
  ↓
MiniApp renders user interface (React components)
```

**Key Difference from Bot**:
- **MiniApp**: Always uses API (no direct database access)
- **Bot**: Uses hybrid approach (API + direct DB access)

#### **3. Database Interaction**

- Both **Bot** and **API** use `shared/database/` module
- **Bot** uses **synchronous** database connection (SQLAlchemy sync)
- **API** uses **asynchronous** database connection (SQLAlchemy async)
- Both share the same database and model definitions

**Database Configuration**:
- Development: SQLite (`luckyred.db`)
- Production: PostgreSQL
- Configured in `.env` file as `DATABASE_URL`

---

## 4. 🔧 Environment Configuration

### Required Environment Variables (`.env` file)

```bash
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/luckyred
# Or SQLite (development)
# DATABASE_URL=sqlite:///./luckyred.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080

# JWT Secret
JWT_SECRET=your-secret-key-here

# Domains (production)
MINIAPP_DOMAIN=mini.usdt2026.cc
ADMIN_DOMAIN=admin.usdt2026.cc
```

### Create `.env` File

```bash
cd /home/ubuntu/hbgm001
cp env-template.txt .env
nano .env  # Edit configuration
```

---

## 5. 📝 Quick Startup Checklist

### Before First Startup

- [ ] Created `.env` file and configured all required variables
- [ ] Installed Python dependencies: `pip install -r requirements.txt`
- [ ] Database created and configured (PostgreSQL or SQLite)
- [ ] Virtual environment created (optional but recommended)

### Startup Steps

1. **Start API**:
   ```bash
   cd /home/ubuntu/hbgm001
   python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8080
   ```

2. **Start Bot** (new terminal):
   ```bash
   cd /home/ubuntu/hbgm001
   python3 bot/main.py
   ```

3. **Verify Services**:
   - API: Visit `http://localhost:8080/docs` to view API documentation
   - Bot: Send `/start` command to Bot in Telegram

---

## 6. 🐛 Common Issues

### Q: Running `python3 main.py` gives "file not found" error

**A**: There is no `main.py` in root directory. Correct startup methods:
- API: `python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8080`
- Bot: `python3 bot/main.py`

### Q: How to verify services are running correctly?

**A**: 
- API: Visit `http://localhost:8080/health` or `http://localhost:8080/docs`
- Bot: Send `/start` command in Telegram

### Q: Do Bot and API need to run simultaneously?

**A**: Yes, both need to run:
- **API** provides backend services (database operations, business logic, serves MiniApp)
- **Bot** provides Telegram interaction interface (can call API or access DB directly)

### Q: When user clicks a button in Bot, does Bot handle it directly or call API?

**A**: It depends on the operation:
- **Simple operations** (like `/checkin`): Bot directly accesses database for faster response
- **Complex operations** (like creating red packets): Bot calls API to ensure consistency with MiniApp
- **Check the handler code** in `bot/handlers/` to see which approach is used

---

## 7. 📚 Related Documentation

- Deployment Guide: `DEPLOY_GUIDE.md`
- API Documentation: `docs/API接口文档.md`
- Development Standards: `docs/开发规范.md`

---

**Last Updated**: 2025-01-07

