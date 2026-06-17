---
description: Build all detected stack targets (Python package, Go services, Bun frontend) using project Taskfile.
---

# tracertm-build

Run standardized build checks for the full repo.

## Command

```pwsh
cd E:/Dev/Tracera
task build
```

## Fallbacks (targeted)

- Python package only: `uv build`
- Go modules: `go build ./...`
- Frontend: `cd frontend && bun run build`

Use `task build` unless a scoped target is explicitly requested.
