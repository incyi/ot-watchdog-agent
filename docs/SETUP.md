# OT Watchdog Agent - Complete Setup Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Setup (Raspberry Pi)](#production-setup-raspberry-pi)
4. [Docker Setup](#docker-setup)
5. [WordPress Configuration](#wordpress-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Linux (Raspberry Pi), macOS, or Windows with Docker
- **Docker**: 20.10+
- **Docker Compose**: 1.29+
- **Python**: 3.8+ (for local development)
- **Network**: Access to devices and WordPress server

### Required Packages

```bash
# Ubuntu/Debian (Raspberry Pi OS)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose python3-pip git

# Add user to docker group (to run without sudo)
sudo usermod -aG docker $USER
newgrp docker
```

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/incyi/ot-watchdog-agent.git
cd ot-watchdog-agent
```

### Step 2: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 3: Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

### Step 4: Run Agent

```bash
python3 watchdog-agent.py
```

---

## Production Setup (Raspberry Pi)

### Step 1: SSH into Raspberry Pi

```bash
ssh pi@192.168.1.100  # Replace with your Pi's IP
```

### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/incyi/ot-watchdog-agent.git
cd ot-watchdog-agent
chmod +x start.sh
```

### Step 3: Configure Environment

```bash
cp .env.example .env
nano .env
```

Important settings:

```bash
# Your WordPress instance
WORDPRESS_URL=https://your-domain.com

# Must match WordPress wp-config.php
OT_WATCHDOG_API_KEY=your-secure-key-here

# Your OT devices
OT_DEVICES={
  "PLC-Main": "192.168.1.10",
  "HMI": "192.168.1.11",
  "Switch": "192.168.1.20",
  "Modem": "192.168.1.1"
}

# How often to check (seconds)
CHECK_INTERVAL=30

# Log level
LOG_LEVEL=INFO
```

### Step 4: Start Agent

```bash
# Quick start
./start.sh start

# View logs
./start.sh logs

# Stop
./start.sh stop
```

### Step 5: Enable Autostart (Optional)

```bash
# Create systemd service
sudo nano /etc/systemd/system/ot-watchdog-agent.service
```

Paste:

```ini
[Unit]
Description=OT Watchdog Agent
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ot-watchdog-agent
ExecStart=/usr/bin/docker-compose up
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ot-watchdog-agent
sudo systemctl start ot-watchdog-agent

# Check status
sudo systemctl status ot-watchdog-agent
```

---

## Docker Setup

### Option A: Docker Compose (Recommended)

```bash
# Start full stack (WordPress + MySQL + Agent)
docker-compose up -d

# View logs
docker-compose logs -f ot-watchdog-agent

# Stop
docker-compose down
```

### Option B: Docker Direct

```bash
# Build image
docker build -t ot-watchdog-agent .

# Run container
docker run -d \
  --name ot-watchdog-agent \
  --restart unless-stopped \
  --env-file .env \
  ot-watchdog-agent

# View logs
docker logs -f ot-watchdog-agent

# Stop
docker stop ot-watchdog-agent
```

### Option C: With External WordPress

```bash
# Run with network access to external WordPress
docker run -d \
  --name ot-watchdog-agent \
  --restart unless-stopped \
  --network host \
  -e WORDPRESS_URL=https://your-domain.com \
  -e OT_WATCHDOG_API_KEY=your-key \
  -e OT_DEVICES='{"Device": "192.168.1.10"}' \
  ot-watchdog-agent
```

---

## WordPress Configuration

### Step 1: Install ot-watchdog Plugin

1. Download plugin from [GitHub](https://github.com/incyi/ot-watchdog)
2. Upload to WordPress: Plugins → Add New → Upload Plugin
3. Activate plugin

### Step 2: Configure wp-config.php

```php
// In your WordPress wp-config.php, add:
define('OT_WATCHDOG_API_KEY', 'your-secure-key-here');
```

### Step 3: Verify REST API

```bash
# Test REST API endpoint (from your Pi)
curl -H "X-API-Key: your-secure-key" \
  https://your-domain.com/wp-json/ot/v1/update \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"TestDevice": "online"}'
```

Expected response:

```json
{
  "success": true,
  "message": "Status updated",
  "received": {"TestDevice": "online"}
}
```

---

## Testing

### Test 1: Verify Device Connectivity

```bash
# From the container
docker exec ot-watchdog-agent ping -c 1 192.168.1.10
```

### Test 2: Verify WordPress Connection

```bash
# From the container
docker exec ot-watchdog-agent curl http://wordpress/wp-json/
```

### Test 3: Manual Status Update

```bash
# Test API directly
curl -v \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"TestDevice": "online"}' \
  http://localhost/wp-json/ot/v1/update
```

### Test 4: Check WordPress Dashboard

1. Go to WordPress Admin
2. Navigate to OT Watchdog menu
3. Verify devices appear with status

---

## Troubleshooting

### Agent won't start

```bash
# Check logs
docker logs ot-watchdog-agent

# Common issues:
# 1. Missing environment variables
# 2. Invalid JSON in OT_DEVICES
# 3. Docker not installed
```

### Connection refused

```bash
# Check if WordPress is reachable
docker exec ot-watchdog-agent ping wordpress
docker exec ot-watchdog-agent curl http://wordpress/

# Check firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Devices show offline

```bash
# Verify ping works from container
docker exec ot-watchdog-agent ping -c 1 192.168.1.10

# Check network connectivity
ip route
arp -a

# Enable debug logging
LOG_LEVEL=DEBUG docker-compose up
```

### API Key mismatch

```bash
# Verify key matches
echo $OT_WATCHDOG_API_KEY
grep "OT_WATCHDOG_API_KEY" /path/to/wp-config.php

# Must be identical (case-sensitive)
```

### High CPU/Memory

```bash
# Check resource usage
docker stats ot-watchdog-agent

# Increase CHECK_INTERVAL if needed
CHECK_INTERVAL=60  # Check every 60 seconds instead of 30
```

---

## Monitoring

### Check Agent Status

```bash
# Docker Compose
docker-compose ps

# Or systemd
sudo systemctl status ot-watchdog-agent
```

### View Logs

```bash
# Real-time
docker-compose logs -f

# Last 100 lines
docker logs --tail 100 ot-watchdog-agent

# With timestamps
docker logs -t ot-watchdog-agent
```

### Health Check

```bash
# Container should have healthy status
docker ps | grep ot-watchdog-agent

# Manual check
docker exec ot-watchdog-agent ps aux | grep watchdog
```

---

## Performance Tuning

### Adjust Check Interval

```bash
# More frequent checks (load on devices)
CHECK_INTERVAL=10

# Less frequent checks (save resources)
CHECK_INTERVAL=60
```

### Resource Limits

```bash
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 128M
    reservations:
      cpus: '0.25'
      memory: 64M
```

---

## Backup & Recovery

### Backup Configuration

```bash
# Backup .env
cp .env .env.backup

# Backup data
docker-compose exec db mysqldump -u wordpress -pwordpress wordpress > backup.sql
```

### Restore Configuration

```bash
# Restore from backup
cp .env.backup .env

# Restore database
docker-compose exec db mysql -u wordpress -pwordpress wordpress < backup.sql
```

---

## Uninstall

```bash
# Stop and remove containers
docker-compose down -v

# Remove image
docker rmi ot-watchdog-agent

# Disable systemd service (if enabled)
sudo systemctl stop ot-watchdog-agent
sudo systemctl disable ot-watchdog-agent
```

---

## Support

- 📖 [README](../README.md)
- 🐛 [Issues](https://github.com/incyi/ot-watchdog-agent/issues)
- 💬 [Discussions](https://github.com/incyi/ot-watchdog-agent/discussions)
