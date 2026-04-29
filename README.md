# OT Watchdog Agent

[![Pylint](https://github.com/incyi/ot-watchdog-agent/actions/workflows/pylint.yml/badge.svg)](https://github.com/incyi/ot-watchdog-agent/actions/workflows/pylint.yml)
[![Docker Image CI](https://github.com/incyi/ot-watchdog-agent/actions/workflows/docker-image.yml/badge.svg)](https://github.com/incyi/ot-watchdog-agent/actions/workflows/docker-image.yml)


🔍 **Lightweight monitoring agent for OT devices (PLC, HMI, Switch, Modem)**

Sends device status to [ot-watchdog WordPress plugin](https://github.com/incyi/ot-watchdog) via REST API.

## Features

- ✅ Multi-device ping-based monitoring
- ✅ Real-time status updates (configurable interval)
- ✅ Docker & Docker Compose ready
- ✅ Raspberry Pi compatible
- ✅ REST API integration with WordPress
- ✅ Comprehensive logging
- ✅ Environment-based configuration
- ✅ Health checks included

## Architecture

```
Raspberry Pi (Docker)
    ↓
OT Watchdog Agent (Python)
    ├─ Ping: PLC (192.168.1.10)
    ├─ Ping: HMI (192.168.1.11)
    ├─ Ping: Switch (192.168.1.20)
    └─ Ping: Modem (192.168.1.1)
    ↓
POST: /wp-json/ot/v1/update (every 30s)
    ↓
WordPress ot-watchdog Plugin
    ├─ Stores in database
    ├─ Shows in admin dashboard
    └─ Displays via [ot_status] shortcode
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.8+ (for local development)
- `ping` command available (most systems have it)

### Option 1: Local Development (Docker Compose)

```bash
# Clone repository
git clone https://github.com/incyi/ot-watchdog-agent.git
cd ot-watchdog-agent

# Start full stack (WordPress + MySQL + Agent)
chmod +x start.sh
./start.sh start

# View logs
./start.sh logs

# Stop
./start.sh stop
```

**Access:**
- Agent: Running in container

### Option 2: Production (Raspberry Pi)

#### Step 1: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```bash
WORDPRESS_URL=https://your-wordpress.com
OT_WATCHDOG_API_KEY=your-secret-key
OT_DEVICES={
  "PLC-Main": "192.168.1.10",
  "HMI-Panel": "192.168.1.11",
  "Switch": "192.168.1.20",
  "Modem": "192.168.1.1"
}
CHECK_INTERVAL=30
```

#### Step 2: Build & Run

```bash
# Build Docker image
docker build -t ot-watchdog-agent .

# Run container
docker run -d \
  --name ot-watchdog-agent \
  --restart unless-stopped \
  --env-file .env \
  ot-watchdog-agent

# View logs
docker logs -f ot-watchdog-agent
```

#### Step 3: Docker Compose (Recommended)

Edit `docker-compose.yml` and update environment variables, then:

```bash
docker-compose up -d
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WORDPRESS_URL` | ✅ | - | WordPress base URL |
| `OT_WATCHDOG_API_KEY` | ✅ | - | API key (must match WordPress config) |
| `OT_DEVICES` | ✅ | - | JSON with devices to monitor |
| `CHECK_INTERVAL` | ❌ | 30 | Seconds between checks |
| `LOG_LEVEL` | ❌ | INFO | DEBUG/INFO/WARNING/ERROR |

### Device Configuration

JSON format:

```json
{
  "Device-Name": "IP-Address",
  "PLC-Main": "192.168.1.10",
  "HMI-Panel": "192.168.1.11",
  "Network-Switch": "192.168.1.20",
  "Modem": "192.168.1.1"
}
```

### WordPress Configuration

In your WordPress `wp-config.php`:

```php
define('OT_WATCHDOG_API_KEY', 'your-secret-key');
```

## Scripts

### Helper Script: `start.sh`

```bash
./start.sh start    # Start stack
./start.sh stop     # Stop stack
./start.sh logs     # View logs
./start.sh status   # Container status
./start.sh restart  # Restart stack
./start.sh build    # Build image
./start.sh clean    # Remove containers
```

## Docker Commands

```bash
# Build image
docker build -t ot-watchdog-agent .

# Run container
docker run -d --name ot-watchdog-agent --env-file .env ot-watchdog-agent

# View logs
docker logs -f ot-watchdog-agent

# Stop container
docker stop ot-watchdog-agent

# Remove container
docker rm ot-watchdog-agent

# Docker Compose (full stack)
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Troubleshooting

### Agent can't reach WordPress

```bash
# Check WordPress URL
docker logs ot-watchdog-agent | grep "WordPress"

# Test connectivity
docker exec ot-watchdog-agent curl http://wordpress/wp-json/
```

### API Key mismatch

```bash
# Verify API key matches WordPress config
echo $OT_WATCHDOG_API_KEY
grep "OT_WATCHDOG_API_KEY" /path/to/wp-config.php
```

### Devices not responding

```bash
# Test ping from container
docker exec ot-watchdog-agent ping -c 1 192.168.1.10

# Check firewall rules
# Ensure ICMP (ping) is allowed
```

### View detailed logs

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG
docker-compose up

# Or in docker run:
docker run --env LOG_LEVEL=DEBUG ...
```

## Integration with ot-watchdog Plugin

The agent sends status to the WordPress plugin endpoint:

```
POST /wp-json/ot/v1/update
X-API-Key: {OT_WATCHDOG_API_KEY}

Body (JSON):
{
  "PLC-Main": "online",
  "HMI-Panel": "online",
  "Switch": "offline",
  "Modem": "online"
}
```

The plugin stores this and displays via:

- **Admin Dashboard**: `OT Watchdog` menu
- **Frontend**: `[ot_status]` shortcode

## Development

### Local Testing (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
export WORDPRESS_URL=http://localhost:8000
export OT_WATCHDOG_API_KEY=test-key
export OT_DEVICES='{"Test": "8.8.8.8"}'

# Run agent
python3 watchdog-agent.py
```

### Code Style

```bash
# Format code
black watchdog-agent.py

# Check style
flake8 watchdog-agent.py
```

## Performance

- **CPU**: Minimal (ping-based, not resource-intensive)
- **Memory**: ~30-50MB per container
- **Network**: ~1KB per update
- **Interval**: Configurable (default 30 seconds)

## Security

- API key required for all requests
- HTTPS supported (configure `WORDPRESS_URL`)
- No credentials stored in code
- Environment-based configuration

## License

GPL-2.0-or-later (same as WordPress plugin)

## Support

- 📖 [WordPress Plugin Docs](https://github.com/incyi/ot-watchdog)
- 🐛 [Report Issues](https://github.com/incyi/ot-watchdog-agent/issues)
- 💬 [Discussions](https://github.com/incyi/ot-watchdog-agent/discussions)

## Related Projects

- [ot-watchdog](https://github.com/incyi/ot-watchdog) - WordPress plugin
- [ot-watchdog-agent](https://github.com/incyi/ot-watchdog-agent) - This agent
