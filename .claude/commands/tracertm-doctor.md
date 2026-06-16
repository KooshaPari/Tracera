---
description: Local preflight checks for TraceRTM environment and required services.
---

# tracertm-doctor

Run a project-aware health and dependency pass before changes.

## Command

```pwsh
cd E:/Dev/Tracera
python scripts/dev health
python scripts/dev status
```

(If `scripts/dev` is on PATH, you can run `scripts/dev health` and `scripts/dev status`.)

## What it verifies

| Check | Details |
|---|---|
| Infra reachability | PostgreSQL, Redis, Neo4j, NATS, Temporal, MinIO/S3 |
| Backend reachability | Python backend `8000`, Go API `8080`, gateway `4000` |
| Env posture | `.env` presence and required variables for local services |
| Task orchestration readiness | ability to run CLI `rtm`/`tracertm` and `tracertm-mcp` entry points |

## Suggested follow-up

- If services are down, start the stack (local process manager/TUI), then re-run health.
- For auth issues, confirm `.env` and runtime token variables rather than editing code defaults.
