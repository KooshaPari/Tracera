# Tracera desktop-hosted backend

Canonical network doctrine:
`docs/architecture/NETWORK_DEPLOYMENT_DOCTRINE.md`

## Default private/operator topology

- Frontend: Vercel Hobby.
- Private network: Tailscale tailnet.
- Backend: `tracera-server` on the owner's desktop.
- Service identity: prefer stable tailnet service naming over a physical node.
- Host edge: one host-level Caddy.
- DNS: owned product names resolved privately for tailnet-only API services.
- Incremental hosting spend: $0.

Cloudflare Tunnel is not required for the private/operator release. It remains
an optional future public-ingress profile.

## Runtime protection

The Rust gateway retains bearer-token protection as a defense-in-depth/operator
API mechanism. Do not embed `TRACERA_AUTH_TOKEN` in a public frontend bundle.
The browser release needs an identity-aware path before it can call protected
backend operations directly.

## Bootstrap

Uncommitted environment:

```env
TRACERA_PUBLIC_HOSTNAME=api.tracera.pheno.studio
TRACERA_PUBLIC_BIND_MODE=private
TRACERA_AUTH_TOKEN=
```

Optional public-ingress profile only:

```env
CF_TUNNEL_TOKEN=
```

Bootstrap packaging:

```sh
docker compose -f deploy/selfhost/docker-compose.selfhost.yml up -d
```

Compose is not the required long-term host architecture. Prefer native process
supervision for tailscaled, Caddy, tracera-server and justified shared services
once the private alpha is established.

## Tailnet route

Logical private path:

```
api.tracera.pheno.studio
 -> split DNS
 -> Tailscale service/tailnet address
 -> host-level Caddy
 -> tracera-server
```

Do not expose a physical `.ts.net` device name as Tracera's product identity.

## Security verification

Run the existing secret-free deployment checks and keep non-health application
routes authenticated. Public-ingress mode requires stronger browser/user
authentication and must not be enabled merely because a tunnel token exists.

## Optional future public ingress

When non-tailnet users become a release requirement:

```sh
docker compose -f deploy/selfhost/docker-compose.selfhost.yml \
  --profile public-ingress up -d
```

The public-ingress layer must terminate in the same host edge; adding it must
not change Tracera product semantics or backend identity.

## Release gates

1. native product persistence/application tests execute and pass;
2. product API naming resolves over the tailnet;
3. Caddy routes the owned hostname to the real backend;
4. browser contains no operator bearer secret;
5. HJ-PRE-001 product open/select closes remotely;
6. HJ-PRE-002 inventory closes remotely;
7. HJ-PRE-003 graph fixture is correct remotely;
8. restart persistence works;
9. backup/restore works;
10. no stub/fallback data is presented as real product state.
