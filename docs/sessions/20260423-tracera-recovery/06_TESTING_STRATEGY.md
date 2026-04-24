# Testing Strategy

## Gates

| Gate | Command | Purpose |
| --- | --- | --- |
| Governance | `python3 validate_governance.py` | Verifies FR manifest and traceability docs |
| Backend compile | `go test -run '^$' ./cmd/tracertm ./internal/services ./internal/server ./internal/config ./internal/tracing` | Confirms key Go backend packages compile |
| Frontend typecheck | `bun run typecheck` from `frontend/` | Runs compiler-backed TypeScript checks for web and packages |
| Web build | `bunx turbo build --filter=@tracertm/web` from `frontend/` | Builds web app and dependency packages |
| UI package | `bun run build && bun run test` from `frontend/packages/ui` | Validates shared UI package and component tests |

## Type-Aware Lint

`oxlint-tsgolint` is intentionally outside the default `typecheck` gate.
It currently has broad diagnostics and can panic in the web app path, so it is tracked
as a separate quality backlog:

```bash
bun run check:type-aware
```

Compiler correctness remains enforced by `tsc --build --noEmit`.

## Runtime Bring-Up

The next validation layer is a native/process-compose startup pass:

1. Verify required local services and ports.
2. Start the recovered stack.
3. Check API, frontend, database, cache, NATS, Temporal, and observability endpoints.
4. Record exact blockers in `05_KNOWN_ISSUES.md`.
