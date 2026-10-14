# Tracera self-host stack

This stack runs Tracera on your desktop behind Caddy. It deliberately does **not** start Cloudflare Tunnel: the live `tracera-local` tunnel is shared infrastructure and its lifecycle is managed outside this repository.

## Layout

- `docker-compose.selfhost.yml`: Tracera server + Caddy only; no cloudflared replica
- `Caddyfile`: TLS reverse proxy plus security headers
- `README.md`: runbook and environment variables

## Prerequisites

- Docker Desktop or a compatible Docker Engine
- Optional: Tailscale installed on the desktop for private tailnet access
- For public reachability, the separately managed shared infrastructure must already route the intended hostname to this host. Do not pass a shared tunnel token into this compose stack.

## Environment variables

Set these before starting the stack:

- `TRACERA_PUBLIC_HOSTNAME`: public hostname served by the tunnel, for example `tracera.pheno.studio`
- `TRACERA_PUBLIC_BIND_MODE`: must be exactly `authenticated-proxy`; set it
  only after Caddy has an active authentication directive. The Rust gateway
  otherwise refuses non-loopback binding at startup.
- `TRACERA_AUTH_TOKEN`: non-empty bearer token supplied to the Rust gateway;
  every non-health route requires `Authorization: Bearer <token>`.

WorkOS AuthKit is not wired in yet, but these placeholders show where its settings would live:

- `WORKOS_API_KEY`
- `WORKOS_CLIENT_ID`
- `WORKOS_COOKIE_SECRET`
- `WORKOS_REDIRECT_URI`
- `WORKOS_BASE_URL`
- Any other `WORKOS_*` values required by your AuthKit middleware

## Ingress security gate

The server is intentionally bound to `0.0.0.0:8080` only inside the compose
network; Caddy is the ingress boundary and port 8080 must not be published.
The compose stack publishes Caddy's HTTP/HTTPS ports (`80` and `443`); Caddy
obtains a certificate automatically for `TRACERA_PUBLIC_HOSTNAME`.
Run the secret-free private-boundary check before every deployment:

```sh
./scripts/verify-deployment-security.sh --mode private

# Validate build inputs, ports, probes, and secret-free manifests
./scripts/verify-deployment-manifests.sh
```

The checked-in Caddyfile contains an AuthKit insertion point, but its
`forward_auth` block is commented and therefore does **not** protect public
traffic. Before shared infrastructure routes public traffic here, configure an active
`forward_auth`, `basic_auth`, or JWT directive, then set
`TRACERA_PUBLIC_BIND_MODE=authenticated-proxy` and run the strict gate:

```sh
./scripts/verify-deployment-security.sh --mode public
```

The strict gate fails closed until authentication and an HTTPS listener are
present. It does not inspect or require credentials, so it is safe to run in CI.

## Run

From the repo root (macOS/Linux):

```sh
docker compose -f deploy/selfhost/docker-compose.selfhost.yml up
```

The stack does two things:

1. Builds and runs `tracera-server` from the repo on `0.0.0.0:8080` with the
   required in-process bearer token.
2. Lets Caddy reverse proxy to `tracera-server:8080`.

It intentionally does **not** start, stop, create, or configure cloudflared. Public
routing is a separate shared-infrastructure concern.

## Public and private access

- Public access: only through the separately managed shared Cloudflare ingress after its route is explicitly configured.
- Private access: Tailscale can reach the same desktop and Caddy listener over the tailnet.

## WorkOS AuthKit

The `Caddyfile` includes a commented `forward_auth` block as the insertion point for WorkOS AuthKit middleware.
When you are ready to enforce auth, replace the placeholder with the actual upstream service and headers for your AuthKit deployment.
