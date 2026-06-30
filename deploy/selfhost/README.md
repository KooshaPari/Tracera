# Tracera self-host stack

This stack runs Tracera on your desktop, publishes it through Caddy, and exposes it globally with a Cloudflare Tunnel.

## Layout

- `docker-compose.selfhost.yml`: Tracera server, Caddy, and cloudflared tunnel
- `Caddyfile`: local reverse proxy plus security headers
- `README.md`: runbook and environment variables

## Prerequisites

- Docker Desktop or a compatible Docker Engine
- A Cloudflare Tunnel already created for your hostname
- `cloudflared` tunnel token for that tunnel
- Optional: Tailscale installed on the desktop for private tailnet access

## Environment variables

Set these before starting the stack:

- `CF_TUNNEL_TOKEN`: Cloudflare Tunnel token for the named tunnel
- `TRACERA_PUBLIC_HOSTNAME`: public hostname served by the tunnel, for example `tracera.pheno.studio`

WorkOS AuthKit is not wired in yet, but these placeholders show where its settings would live:

- `WORKOS_API_KEY`
- `WORKOS_CLIENT_ID`
- `WORKOS_COOKIE_SECRET`
- `WORKOS_REDIRECT_URI`
- `WORKOS_BASE_URL`
- Any other `WORKOS_*` values required by your AuthKit middleware

## Run

From the repo root:

```powershell
docker compose -f deploy/selfhost/docker-compose.selfhost.yml up
```

The stack does three things:

1. Builds and runs `tracera-server` from the repo on `0.0.0.0:8080`
2. Lets Caddy reverse proxy `http://tracera.pheno.studio` to `tracera-server:8080`
3. Attaches cloudflared to the tunnel token so the hostname is reachable globally through Cloudflare

## Public and private access

- Public access: Cloudflare Tunnel exposes the hostname you set in `TRACERA_PUBLIC_HOSTNAME`
- Private access: Tailscale can reach the same desktop and Caddy listener over the tailnet, so you can keep a private path even if the public tunnel is disabled

## WorkOS AuthKit

The `Caddyfile` includes a commented `forward_auth` block as the insertion point for WorkOS AuthKit middleware.
When you are ready to enforce auth, replace the placeholder with the actual upstream service and headers for your AuthKit deployment.
