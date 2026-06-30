# Tracera Self-Hosted Deployment

This directory contains a complete self-hosted stack for Tracera using Docker Compose, Caddy, and Cloudflare Tunnel.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Cloudflare account with a Tunnel token (for `CF_TUNNEL_TOKEN`)
- A domain or subdomain pointed to Cloudflare DNS

### Environment Variables

Create a `.env` file in this directory (or set in your shell):

```bash
# Required
CF_TUNNEL_TOKEN=<your-cloudflare-tunnel-token>

# Optional (defaults to tracera.pheno.studio)
HOSTNAME=tracera.pheno.studio
```

### Running the Stack

```bash
docker compose -f docker-compose.selfhost.yml up -d
```

This starts three services:
- **tracera-server** – Tracera app on port 8080
- **caddy** – Reverse proxy with TLS, security headers, and compression
- **cloudflared** – Cloudflare Tunnel for secure ingress

### Accessing Tracera

#### Global (via Cloudflare Tunnel)
Access your instance at: `https://${HOSTNAME}`

#### Private (via Tailscale)
If you have Tailscale installed on the host:
```bash
docker inspect caddy-reverse-proxy | grep IPAddress
# Then access via: http://<container-ip>:80 on your Tailscale network
```

Or forward via Tailscale SSH:
```bash
ssh -L 8080:localhost:8080 <tailscale-host>
# Then access: http://localhost:8080
```

## Configuration

### Caddy (Reverse Proxy)

Edit `Caddyfile` to:
- Customize domain name
- Add authentication (uncomment `forward_auth` for WorkOS AuthKit or similar)
- Adjust security headers
- Configure rate limiting or additional middlewares

### Tracera Server

Container environment variables in `docker-compose.selfhost.yml`:
- `PORT` – HTTP port (default: 8080)
- Add additional env vars (database URL, API keys, etc.) as needed

### Cloudflare Tunnel

Configure your tunnel in [Cloudflare Dashboard](https://dash.cloudflare.com):
1. Create a tunnel with a unique name
2. Copy the tunnel token to `CF_TUNNEL_TOKEN`
3. Set up ingress routing to point to `http://caddy:80`

## Stopping

```bash
docker compose -f docker-compose.selfhost.yml down
```

To remove volumes (WARNING: deletes Caddy data):
```bash
docker compose -f docker-compose.selfhost.yml down -v
```

## Logs

```bash
# All services
docker compose -f docker-compose.selfhost.yml logs -f

# Specific service
docker compose -f docker-compose.selfhost.yml logs -f tracera-server
```

## Production Considerations

- Use secrets management (e.g., Docker secrets, HashiCorp Vault) for `CF_TUNNEL_TOKEN`
- Monitor logs and container health
- Set up backups for Caddy config volume if you customize it
- Ensure firewall rules allow ingress only from Cloudflare and Tailscale endpoints
- Regularly pull latest base images for security updates

## Troubleshooting

**Tracera server not responding:**
```bash
docker compose -f docker-compose.selfhost.yml logs tracera-server
```

**Caddy TLS issues:**
```bash
docker compose -f docker-compose.selfhost.yml logs caddy
```

**Tunnel not connecting:**
- Verify `CF_TUNNEL_TOKEN` is correct
- Check Cloudflare Dashboard for tunnel status
- Confirm DNS is pointed to Cloudflare nameservers
