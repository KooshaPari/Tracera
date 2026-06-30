# Tracera Self-Hosted Deployment

Complete Docker Compose stack for self-hosting Tracera with reverse proxy (Caddy) and optional Cloudflare Tunnel support.

## Architecture

```
┌─────────────┐
│   Clients   │
└──────┬──────┘
       │ HTTPS (80/443)
       ▼
┌─────────────────────────────────────┐
│ Caddy (Reverse Proxy + TLS)         │
│ - Security headers                  │
│ - WebSocket support                 │
│ - Forward auth placeholder          │
└──────┬──────────────────────────────┘
       │ HTTP (8080)
       ▼
┌─────────────────────────────────────┐
│ Tracera Server                      │
│ - REST API                          │
│ - WebSocket (real-time updates)     │
│ - Health check endpoint (/health)   │
└─────────────────────────────────────┘
       │
       ▼
[Database] [External Services]


Optional Cloudflare Tunnel (for global ingress):
┌──────────────────────────┐
│ Cloudflare Tunnel        │
│ (cloudflared daemon)     │
└──────────┬───────────────┘
           │
           ▼
    [Cloudflare Edge]
```

## Quick Start

### 1. Build the Tracera Server Image

Ensure you have a Dockerfile or pre-built image. If building locally:

```bash
cd /path/to/tracera
docker build -t tracera:latest .
```

### 2. Create `.env.selfhost` Configuration

Copy this template and fill in your values:

```bash
cat > .env.selfhost << 'EOF'
# Reverse proxy hostname (Caddy will listen on this)
HOSTNAME=tracera.your-domain.com

# Database connection string
# Example: postgresql://user:password@db.example.com:5432/tracera
DATABASE_URL=

# WorkOS authentication (optional but recommended)
WORKOS_API_KEY=your_workos_api_key
WORKOS_CLIENT_ID=your_workos_client_id

# Cloudflare Tunnel token (only if using cloudflared)
# Leave empty to disable Cloudflare Tunnel
CF_TUNNEL_TOKEN=

# Optional: Slack, GitHub, or other integrations
# SLACK_BOT_TOKEN=
# GITHUB_PAT=
EOF
```

**Important:** Never commit `.env.selfhost` to version control. Add to `.gitignore`:

```
.env.selfhost
.env.*.local
```

### 3. Start the Stack

```bash
# Start all services (Caddy + Tracera)
docker compose -f deploy/selfhost/docker-compose.selfhost.yml \
  --env-file .env.selfhost up -d

# Or, include Cloudflare Tunnel:
docker compose -f deploy/selfhost/docker-compose.selfhost.yml \
  --env-file .env.selfhost \
  --profile cloudflare up -d
```

### 4. Verify Health

```bash
# Check if all containers are running
docker compose -f deploy/selfhost/docker-compose.selfhost.yml ps

# View Caddy logs
docker compose -f deploy/selfhost/docker-compose.selfhost.yml logs -f caddy

# Check Tracera health
curl https://tracera.your-domain.com/health
```

### 5. Manage Services

```bash
# Stop the stack
docker compose -f deploy/selfhost/docker-compose.selfhost.yml down

# Restart Tracera only
docker compose -f deploy/selfhost/docker-compose.selfhost.yml restart tracera-server

# View all logs
docker compose -f deploy/selfhost/docker-compose.selfhost.yml logs -f

# Clean up volumes (WARNING: deletes data!)
docker compose -f deploy/selfhost/docker-compose.selfhost.yml down -v
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `HOSTNAME` | Domain name for Caddy to listen on | `tracera.pheno.studio` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@pg.example.com:5432/tracera` |

### Optional (Authentication)

| Variable | Description | Source |
|----------|-------------|--------|
| `WORKOS_API_KEY` | WorkOS API secret key | [WorkOS Dashboard](https://dashboard.workos.com) |
| `WORKOS_CLIENT_ID` | WorkOS client ID for your deployment | [WorkOS Dashboard](https://dashboard.workos.com) |

### Optional (Integrations)

| Variable | Description |
|----------|-------------|
| `SLACK_BOT_TOKEN` | Slack bot token for notifications |
| `GITHUB_PAT` | GitHub personal access token for sync |

### Cloudflare Tunnel

| Variable | Description |
|----------|-------------|
| `CF_TUNNEL_TOKEN` | Cloudflare Tunnel token (leave empty to disable) |

Generate a token:

```bash
# Install cloudflared CLI
curl -L https://pkg.cloudflare.com/cloudflare-release-key.gpg | sudo apt-key add -
sudo apt-get install cloudflared

# Authenticate and create a tunnel
cloudflared tunnel login
cloudflared tunnel create tracera
cloudflared tunnel token tracera

# Copy the token to .env.selfhost
```

## Networking

### Local Development

For testing without a registered domain:

```bash
# Use Docker's internal DNS
curl http://tracera-server:8080/health

# Or localhost via Caddy's secondary listener
curl http://localhost:8081/
```

### Private Network (Tailscale)

Tracera is reachable via Tailscale if both client and server are on the same Tailscale network:

1. Install Tailscale on the server running Docker
2. Add Tailscale IP to `/etc/hosts` or use DNS:
   ```bash
   curl https://tracera-server.tailXXXX.ts.net/health
   ```

3. Clients must be on the same Tailscale network

### Public Access (Cloudflare Tunnel)

With `CF_TUNNEL_TOKEN` set:

1. Tunnel is globally accessible via Cloudflare edge
2. Your domain is automatically proxied through Cloudflare
3. No static IP or port forwarding required
4. Zero-trust policies can be applied in Cloudflare dashboard

## Security

### Caddy Security Headers

The `Caddyfile` enforces:

- **HSTS**: Forces HTTPS for 1 year
- **X-Content-Type-Options**: Prevents MIME sniffing
- **X-Frame-Options**: Disables framing (clickjacking protection)
- **CSP**: Restricts inline scripts and external resources
- **Permissions-Policy**: Disables geo, mic, camera by default

### TLS Certificates

Caddy automatically provisions Let's Encrypt certificates. To use a custom certificate:

```bash
docker run -v caddy-config:/config caddy caddy untrust
# Manual config in Caddyfile:
# tls /path/to/cert.pem /path/to/key.pem
```

### Database Security

**Always:**

- Use strong passwords
- Restrict database access to internal Docker network
- Enable SSL/TLS for PostgreSQL connections
- Use read-only database replicas if available
- Rotate credentials regularly

### API Authentication

**Recommended:**

- Enable WorkOS for human user authentication
- Use API keys or OAuth for service-to-service calls
- Rotate API keys monthly
- Monitor access logs for suspicious activity

## Forward Auth Integration (Optional)

To add centralized authentication with WorkOS AuthKit:

1. **Set up an auth sidecar** (outside this stack):

```yaml
# In your main docker-compose (NOT in selfhost stack)
workos-authkit:
  image: workos-authkit:latest
  ports:
    - "9091:9091"
  environment:
    WORKOS_CLIENT_ID: ${WORKOS_CLIENT_ID}
    WORKOS_API_KEY: ${WORKOS_API_KEY}
  networks:
    - tracera-net
```

2. **Uncomment the forward_auth block in Caddyfile**:

```caddy
@protected {
    path /api/* /projects/* /admin*
}

route @protected {
    forward_auth workos-authkit:9091 {
        uri /auth
        copy_headers Authorization Cookie
        rewrite_uri /auth
    }
}
```

3. **Restart Caddy**:

```bash
docker compose restart caddy
```

## Troubleshooting

### Caddy won't start

```bash
# Check Caddyfile syntax
docker run -v $(pwd)/deploy/selfhost:/etc/caddy caddy caddy validate

# View detailed logs
docker compose logs caddy
```

### Tracera server not responding

```bash
# Check if service is running
docker compose ps tracera-server

# View server logs
docker compose logs tracera-server

# Check health endpoint directly
docker compose exec tracera-server curl http://localhost:8080/health
```

### Cloudflare Tunnel not connecting

```bash
# Check tunnel logs
docker compose logs cloudflared

# Verify CF_TUNNEL_TOKEN is set
echo $CF_TUNNEL_TOKEN

# List tunnels
cloudflared tunnel list

# Recreate tunnel token if needed
cloudflared tunnel token tracera
```

### Database connection fails

```bash
# Test PostgreSQL connectivity
docker compose exec tracera-server psql "$DATABASE_URL" -c "SELECT 1"

# Check DATABASE_URL format
# Should be: postgresql://user:password@host:5432/database
```

### Permission denied errors

```bash
# Ensure Docker daemon permissions
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker compose up
```

## Monitoring

### Container Health Status

```bash
docker compose ps

# STATUS column shows: Up (healthy) or Up (unhealthy)
```

### Log Aggregation

```bash
# Tail all services
docker compose logs -f

# Tail single service
docker compose logs -f tracera-server

# View last 100 lines
docker compose logs --tail 100

# Follow with timestamps
docker compose logs --timestamps -f
```

### Metrics Endpoint

If Tracera exposes metrics at `/metrics`:

```bash
curl https://tracera.your-domain.com/metrics
```

Use Prometheus + Grafana for persistent monitoring:

```yaml
# Add to docker-compose.selfhost.yml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    GF_SECURITY_ADMIN_PASSWORD: admin
```

## Backups

### Database Backup

```bash
# One-off backup
docker compose exec tracera-db pg_dump -U postgres tracera > backup.sql

# Automated daily backup (via cron or systemd timer)
0 2 * * * docker compose exec tracera-db pg_dump -U postgres tracera > /backups/tracera-$(date +\%Y\%m\%d).sql
```

### Volume Backup

```bash
# Backup Tracera data volume
docker run --rm -v tracera-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/tracera-data.tar.gz -C /data .

# Restore from backup
docker run --rm -v tracera-data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/tracera-data.tar.gz -C /data
```

## Updates

### Update Tracera Server Image

```bash
# Pull latest image
docker pull tracera:latest

# Restart service
docker compose up -d tracera-server

# Verify
docker compose logs tracera-server
```

### Update Caddy

```bash
docker compose pull caddy
docker compose up -d caddy
```

## Production Checklist

- [ ] Database backups automated and tested
- [ ] HTTPS certificates auto-renewing (verify with Caddy logs)
- [ ] Health checks passing (`/health` endpoint responsive)
- [ ] Environment variables (.env.selfhost) in `.gitignore`
- [ ] Secrets not logged or exposed (check container logs)
- [ ] Rate limiting configured in Caddy or application
- [ ] Monitoring/alerting set up (logs, metrics, uptime)
- [ ] Regular security updates (Docker images, OS)
- [ ] Disaster recovery plan documented
- [ ] Access logs retained for compliance

## Support

For issues:

1. Check logs: `docker compose logs -f`
2. Verify configuration: `docker compose config`
3. Test connectivity: `docker compose exec tracera-server curl http://localhost:8080/health`
4. Review [Tracera docs](../../docs) and Caddy docs

---

**Generated:** 2026-06-29  
**Version:** 1.0  
**Status:** Production-ready
