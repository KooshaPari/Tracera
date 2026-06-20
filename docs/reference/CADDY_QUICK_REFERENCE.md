# Caddy Gateway Quick Reference

## Essential Commands

### Start/Stop/Reload

```bash
# Start Caddy (foreground)
caddy run --config Caddyfile

# Start Caddy (background)
caddy start --config Caddyfile

# Stop Caddy
caddy stop

# Reload configuration
caddy reload --config Caddyfile

# Validate configuration
caddy validate --config Caddyfile
```

### View Logs

```bash
# System logs
tail -f /tmp/caddy-tracertm.log

# Access logs
tail -f /tmp/caddy-tracertm-access.log

# JSON pretty print
tail -f /tmp/caddy-tracertm.log | jq .
```

## Route Mapping

| Path | Backend | Port |
|------|---------|------|
| `/api/v1/specifications/*` | Python | 8000 |
| `/api/v1/executions/*` | Python | 8000 |
| `/api/v1/mcp/*` | Python | 8000 |
| `/api/v1/quality/*` | Python | 8000 |
| `/api/v1/notifications/*` | Python | 8000 |
| `/api/v1/auth/*` | Python | 8000 |
| `/api/v1/projects/*` | Go | 8080 |
| `/api/v1/items/*` | Go | 8080 |
| `/api/v1/links/*` | Go | 8080 |
| `/api/v1/graph/*` | Go | 8080 |
| `/api/v1/search/*` | Go | 8080 |
| `/api/v1/agents/*` | Go | 8080 |
| `/api/v1/temporal/*` | Go | 8080 |
| `/api/v1/code/*` | Go | 8080 |
| `/api/v1/ws` | Go | 8080 |
| `/*` | Frontend | 5173 |

## Health Checks

```bash
# Gateway health
curl http://localhost/health

# Python backend
curl http://localhost/health/python

# Go backend
curl http://localhost/health/go
```

## Admin API

```bash
# View config
curl http://localhost:2019/config/

# View routes
curl http://localhost:2019/config/apps/http/servers | jq .
```

## Frontend Environment

```bash
# frontend/apps/web/.env.local
VITE_API_URL=http://localhost
VITE_WS_URL=ws://localhost
```

## Full Stack Startup

```bash
# Terminal 1: Python Backend
cd backend && python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Go Backend
cd backend-go && go run cmd/api/main.go

# Terminal 3: Frontend
cd frontend/apps/web && bun run dev

# Terminal 4: Caddy Gateway
caddy run --config Caddyfile
```

Access: http://localhost

## Troubleshooting

### Port in use?
```bash
# Check what's using port 80
sudo lsof -i :80

# Use different port in Caddyfile
localhost:8888 {
    # ... config
}
```

### Backend not responding?
```bash
# Test backends directly
curl http://localhost:4000/health  # Python
curl http://localhost:8080/health  # Go
```

### Configuration errors?
```bash
# Validate syntax
caddy validate --config Caddyfile

# Check logs
tail -n 50 /tmp/caddy-tracertm.log
```

## Installation

```bash
# macOS
brew install caddy

# Linux (Debian/Ubuntu)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

## Quick Test

```bash
# 1. Validate
caddy validate --config Caddyfile

# 2. Start gateway
caddy run --config Caddyfile

# 3. Test health (new terminal)
curl http://localhost/health

# 4. Should see: "OK - TraceRTM Gateway v1.0"
```
