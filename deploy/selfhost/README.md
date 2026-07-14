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
- `TRACERA_CORS_ORIGINS`: comma-separated explicit browser origins, including the Vercel origin
- `TRACERA_DATABASE_URL`: complete Postgres connection URL used by the server
- `TRACERA_POSTGRES_PASSWORD`: password used to initialize the bundled Postgres service
- `TRACERA_JWT_AUDIENCE`: required JWT audience, for example `tracera-api`
- `TRACERA_JWT_ISSUER`: required JWT issuer
- Exactly one signing key: `TRACERA_JWT_SECRET` for HS256 or `TRACERA_JWT_PUBLIC_KEY` for RS256

The server refuses to start when issuer, audience, or signing-key configuration is missing or
ambiguous. `TRACERA_JWT_SECRET` must contain at least 32 bytes. Protected routes require scoped
bearer tokens; health probes remain public.

The web app uses WorkOS AuthKit directly. Set these at frontend build time:

- `VITE_WORKOS_CLIENT_ID`: required public WorkOS client ID (`client_...`)
- `VITE_WORKOS_API_HOSTNAME`: optional custom Authentication API HTTPS origin,
  for example `https://auth.tracera.example`
- `VITE_API_BASE`: optional Tracera API origin or root-relative path; blank uses
  the same origin

Never expose a WorkOS API key, cookie secret, or access token through a `VITE_*`
variable. AuthKit owns browser session persistence and the application requests
access tokens through `getAccessToken()` when calling Tracera APIs.

## Run

From the repo root:

```bash
docker compose -f deploy/selfhost/docker-compose.selfhost.yml up
```

The stack does three things:

1. Builds and runs `tracera-server` from the production root `Dockerfile`
2. Lets Caddy reverse proxy `http://tracera.pheno.studio` to `tracera-server:8080`
3. Attaches cloudflared to the tunnel token so the hostname is reachable globally through Cloudflare

## Public and private access

- Public access: Cloudflare Tunnel exposes the hostname you set in `TRACERA_PUBLIC_HOSTNAME`
- Private access: Tailscale can reach the same desktop and Caddy listener over the tailnet, so you can keep a private path even if the public tunnel is disabled

## WorkOS AuthKit

The Rust server already validates scoped bearer JWTs. The `Caddyfile` includes a commented
`forward_auth` insertion point for a future browser login/session service; it is not a replacement
for API JWT authorization.

Configure the WorkOS Dashboard for every deployed frontend origin:

1. Add the frontend URL as an exact redirect URI, such as
   `https://tracera.pheno.studio`.
2. Add the frontend origin to **Authentication > Allowed origins**.
3. Set the sign-in endpoint to the frontend `/login` URL, such as
   `https://tracera.pheno.studio/login`.
4. Configure the Tracera server JWT issuer, audience, and JWKS URL to validate
   AuthKit access tokens before exposing protected API routes.

The browser never stores application-managed tokens or sends secrets through
the build environment. Each dashboard refresh obtains one access token from
AuthKit and sends it as `Authorization: Bearer <token>` to protected API calls.
