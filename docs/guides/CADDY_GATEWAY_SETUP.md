# Caddy API Gateway Setup Guide

## Overview

TraceRTM uses Caddy as a unified API gateway to route requests between the Python FastAPI backend, Go backend, and frontend. This simplifies the architecture and provides a single entry point for all services.

## Installation

### macOS (Homebrew)
```bash
brew install caddy
```

### Linux (Debian/Ubuntu)
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

### Other Platforms
See: https://caddyserver.com/docs/install

## Configuration

The Caddyfile is located in the project root: `/Caddyfile`

### Route Mapping

| Route Pattern | Backend | Port | Purpose |
|--------------|---------|------|---------|
| `/api/v1/specifications/*` | Python | 8000 | Specification management |
| `/api/v1/executions/*` | Python | 8000 | Test execution |
| `/api/v1/mcp/*` | Python | 8000 | Model Context Protocol |
| `/api/v1/quality/*` | Python | 8000 | Quality metrics |
| `/api/v1/notifications/*` | Python | 8000 | Notifications |
| `/api/v1/auth/*` | Python | 8000 | Authentication |
| `/api/v1/projects/*` | Go | 8080 | Project management |
| `/api/v1/items/*` | Go | 8080 | Items/requirements |
| `/api/v1/links/*` | Go | 8080 | Traceability links |
| `/api/v1/graph/*` | Go | 8080 | Graph visualization |
| `/api/v1/search/*` | Go | 8080 | Search functionality |
| `/api/v1/agents/*` | Go | 8080 | AI agents |
| `/api/v1/temporal/*` | Go | 8080 | Temporal tracking |
| `/api/v1/code/*` | Go | 8080 | Code analysis |
| `/api/v1/ws` | Go | 8080 | WebSocket (real-time) |
| `/*` | Frontend | 5173 | UI (default route) |

### Health Checks

- `/health` - Gateway health
- `/health/python` - Python backend health
- `/health/go` - Go backend health

## Usage

### Start Caddy

From the project root:

```bash
caddy run --config Caddyfile
```

Or run in background:

```bash
caddy start --config Caddyfile
```

### Stop Caddy

```bash
caddy stop
```

### Reload Configuration

After modifying the Caddyfile:

```bash
caddy reload --config Caddyfile
```

### Validate Configuration

```bash
caddy validate --config Caddyfile
```

### View Logs

Access logs:
```bash
tail -f /tmp/caddy-tracertm-access.log
```

Error/system logs:
```bash
tail -f /tmp/caddy-tracertm.log
```

## Frontend Configuration

Update your frontend environment file (`frontend/apps/web/.env.local`):

```bash
# Copy from example
cp frontend/apps/web/.env.example frontend/apps/web/.env.local

# Ensure these values are set:
VITE_API_URL=http://localhost
VITE_WS_URL=ws://localhost
```

## Development Workflow

### Full Stack Development

1. **Start Python Backend** (Terminal 1):
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start Go Backend** (Terminal 2):
   ```bash
   cd backend-go
   go run cmd/api/main.go
   ```

3. **Start Frontend** (Terminal 3):
   ```bash
   cd frontend/apps/web
   bun run dev
   ```

4. **Start Caddy Gateway** (Terminal 4):
   ```bash
   caddy run --config Caddyfile
   ```

5. **Access Application**:
   - Frontend: http://localhost (proxied to localhost:5173)
   - All APIs: http://localhost/api/v1/*

### Without Caddy (Direct Access)

If you prefer to develop without the gateway:

```bash
# frontend/apps/web/.env.local
VITE_API_URL=http://localhost:4000
VITE_WS_URL=ws://localhost:4000
```

Then access services directly:
- Frontend: http://localhost:5173
- Python API (via gateway): http://localhost:4000
- Go API: http://localhost:8080

## Admin API

Caddy's admin API is available at `http://localhost:2019` for runtime configuration and monitoring.

### Check Configuration
```bash
curl http://localhost:2019/config/
```

### View Current Routes
```bash
curl http://localhost:2019/config/apps/http/servers
```

## Troubleshooting

### Port Already in Use

If port 80 (default for `localhost`) is already in use:

1. Change the Caddyfile:
   ```
   localhost:8888 {
       # ... rest of config
   }
   ```

2. Update frontend env:
   ```
   VITE_API_URL=http://localhost:8888
   VITE_WS_URL=ws://localhost:8888
   ```

### Backend Not Responding

1. Check backend is running:
   ```bash
   curl http://localhost:4000/api/py/health  # Python via gateway
   curl http://localhost:8080/health  # Go
   ```

2. Check Caddy logs:
   ```bash
   tail -f /tmp/caddy-tracertm.log
   ```

3. Verify route configuration:
   ```bash
   caddy validate --config Caddyfile
   ```

### WebSocket Connection Issues

Ensure:
1. Go backend is running on port 8080
2. WebSocket route is configured: `/api/v1/ws`
3. Frontend is using: `ws://localhost/api/v1/ws`

## Production Considerations

For production deployment:

1. **Enable HTTPS**: Remove `auto_https off` from global options
2. **Use Domain Name**: Replace `localhost` with your domain
3. **Add Rate Limiting**: Configure rate limiting directives
4. **Enable CORS**: Add CORS headers if needed
5. **Logging**: Configure log rotation and external log aggregation
6. **Monitoring**: Integrate with monitoring tools (Prometheus, etc.)

Example production Caddyfile:
```
tracertm.com {
    # TLS automatically enabled

    # Rate limiting
    rate_limit {
        zone api {
            key {remote_host}
            events 100
            window 1m
        }
    }

    # ... rest of routes
}
```

## References

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Reverse Proxy Guide](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [WebSocket Support](https://caddyserver.com/docs/v2-upgrade#websockets)
- [Admin API](https://caddyserver.com/docs/api)
