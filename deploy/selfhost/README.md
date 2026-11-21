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

The server listens on container port 8080 and is published to the host **only**
as `127.0.0.1:8080`. That loopback mapping is the origin used by the separately
managed host-local `tracera-local` connector for `t.tracera.pheno.studio`;
it must never be widened to a LAN/public bind. Caddy separately publishes
HTTP/HTTPS (`80`/`443`) for its own listener and security-header path.
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

1. Builds and runs `tracera-server` with the required in-process bearer token,
   publishing it only as host-loopback `127.0.0.1:8080` for the external shared
   connector.
2. Lets Caddy reverse proxy to `tracera-server:8080` for its separate listener.

It intentionally does **not** start, stop, create, or configure cloudflared. Public
routing is a separate shared-infrastructure concern.

## Public and private access

- Public access: only through the separately managed shared Cloudflare ingress.
  The observed `t.tracera.pheno.studio` route terminates at Cloudflare Access,
  then the host-local connector reaches `127.0.0.1:8080`.
- Private access: Tailscale remains a separate private path; do not infer public
  authorization from tailnet reachability.

## WorkOS AuthKit

The `Caddyfile` includes a commented `forward_auth` block as the insertion point for WorkOS AuthKit middleware.
When you are ready to enforce auth, replace the placeholder with the actual upstream service and headers for your AuthKit deployment.
