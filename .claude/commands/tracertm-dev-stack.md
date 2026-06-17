---
description: Start and inspect the multi-service local stack and related logs.
---

# tracertm-dev-stack

Run/inspect the local stack required by TraceRTM.

## Command

```pwsh
cd E:/Dev/Tracera
task dev:tui
# or for direct stack start per team process
task dev
```

## Inspect and debug

- Health: `python scripts/dev health`
- Status/processes: `python scripts/dev status`
- Logs: `python scripts/dev logs --service gateway`, `python scripts/dev logs --service python`, `python scripts/dev logs --service go`
- Seed/cleanup helpers (if local services are running): `python scripts/dev seed`, `python scripts/dev clear --all`, `python scripts/dev reset --yes`

Use short, explicit service names and avoid conflating python/go/backend health with infra health.
