# Network and deployment doctrine

Status: canonical for the Tracera recovery branch as of 2026-10-04.

This repo shares the portfolio network doctrine with AgilePlus.

## Core rule

Tailscale is the private organizational network fabric. Product-facing names
remain owned product domains; machine names and `.ts.net` names are plumbing.

Default private/operator path:

```
product domain
 -> split DNS
 -> Tailscale service / tailnet route
 -> one host-level Caddy
 -> localhost application process
```

Cloudflare Tunnel is optional future public ingress, not the private network
foundation.

## DNS and naming

- Porkbun: registrar.
- Cloudflare: public authoritative DNS.
- Tailscale split DNS/internal resolver: private service resolution.
- Prefer stable service identity over a physical desktop node.
- Do not redirect the entire public product zone internally unless the internal
  resolver deliberately mirrors it.

Candidate names:

- `tracera.pheno.studio` — browser/product identity.
- `api.tracera.pheno.studio` — product API.
- `mcp.tracera.pheno.studio` — MCP surface.
- `*.infra.pheno.studio` — organizational infrastructure.

Exact names may evolve; physical host identity must not leak into the product
contract.

## Reverse proxy

Run one Caddy process per physical host. Tracera contributes routing fragments
to that host edge; it should not require a project-local Caddy chained behind a
global Caddy.

Do not add Traefik or another proxy without a demonstrated capability gap.

## TLS

Use certificates for the owned product hostname. For private-only targets,
DNS-01 against Cloudflare is appropriate when public HTTP validation cannot
reach the origin. Do not make a `.ts.net` certificate/name the product UX.

## Desktop host

The owner's desktop is the zero-cost stateful compute host.

Long-term target:

```
systemd/process supervisor
  tailscaled
  caddy
  internal DNS if required
  tracera-server
  Tracera workers/services
  justified shared stateful services
```

Compose is bootstrap/test packaging, not a mandatory production layer.

## Frontend

Vercel Hobby remains the zero-cost frontend/static target when plan limits and
usage terms fit the release. The browser must never contain an operator bearer
secret. Private/operator auth should prefer tailnet identity or another
identity-aware path.

## Public release

When arbitrary non-tailnet users become a release requirement, add exactly one
public ingress layer in front of the same host edge. Cloudflare Tunnel is one
candidate at that stage. Adding public ingress must not require changing
Tracera's backend service identity or application semantics.
