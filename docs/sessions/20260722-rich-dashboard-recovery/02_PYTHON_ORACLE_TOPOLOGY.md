# Python Oracle Deployment Topology

The approved rich dashboard lineage (`origin/releases/stable`, descended by the
2026-07-17 Grapheon snapshot) expects the TracerTM Python API, not the small Rust
API. This document records an isolated local topology; it must not replace the
current Compose stack until the rich frontend adapter is validated.

## Reserved ports

| Surface | Host port | Container/service port | Rule |
|---|---:|---:|---|
| Grapheon | 8080 | 8080 | **Reserved; never bind or stop** |
| Python oracle | 18080 | 8000 | Isolated FastAPI service |
| Go sidecar | 18081 | 8080 | Isolated Go service |
| Oracle gateway | 18000 | 4000 | Rich frontend API base |
| PostgreSQL | 15432 | 5432 | Dedicated oracle data plane |
| Redis | 16379 | 6379 | Dedicated oracle cache |
| NATS | 14222 | 4222 | Dedicated oracle messaging |

The gateway is the only browser-facing API origin. The rich frontend must use
`VITE_API_BASE=http://127.0.0.1:18000` (or the machine's Tailscale address),
never a direct backend port.

## Python service contract

Run the stable worktree's ASGI application as `tracertm.api.main:app` on
container port 8000. Required names are `DATABASE_URL`, `REDIS_URL`, `NATS_URL`,
and `GO_BACKEND_URL`; authentication and provider variables remain optional until
the auth contract is enabled. Do not copy secret values into this document.

The stable branch's root Compose file is not a safe drop-in: it targets host
ports 80/443 and 8080 and assumes a root `Dockerfile` that is absent from the
stable tree. Build an isolated deployment from an explicit worktree/container
definition after the API adapter is implemented.

## Validation gate

Before any launch, run `python3 scripts/validate-oracle-ports.py` with the
selected ports. It rejects the reserved Grapheon port, duplicate bindings, and
privileged ports. This is a dependency-free preflight only; it does not mutate
processes or containers.
