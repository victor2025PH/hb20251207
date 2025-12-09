# Deployment Commands

Quick deployment commands for server execution.

## First Deployment (Complete Installation)

Execute on server:

```bash
cd /home/ubuntu && \
git clone https://github.com/victor2025PH/hb20251207.git hbgm001 && \
cd hbgm001 && \
python3 -m venv .venv && \
source .venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt
```

## Update Deployment (If project already exists)

Execute on server:

```bash
cd /home/ubuntu/hbgm001 && \
git pull origin main && \
source .venv/bin/activate && \
pip install -r requirements.txt && \
sudo systemctl restart hbgm001-backend && \
sudo systemctl status hbgm001-backend
```

## Manual Deployment Steps

1. **Login to server:**
   ```bash
   ssh ubuntu@165.154.254.99
   ```

2. **Clone code:**
   ```bash
   cd /home/ubuntu
   git clone https://github.com/victor2025PH/hb20251207.git hbgm001
   cd hbgm001
   ```

3. **Setup virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp env-template.txt .env
   nano .env  # Edit configuration file
   ```

5. **Restart service:**
   ```bash
   sudo systemctl restart hbgm001-backend
   sudo systemctl status hbgm001-backend
   ```
