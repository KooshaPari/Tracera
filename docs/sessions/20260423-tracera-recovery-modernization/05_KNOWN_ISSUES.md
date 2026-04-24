---
audience: [developers, agents]
status: active
---

# Known Issues

## REC-001: Local `Tracera/` is tainted

The local `Tracera/` directory is not the full implementation. It is a docs-only snapshot and
should not be used as source for restoration.

## REC-002: Root case collisions

Remote `origin/main` tracks both uppercase and lowercase governance files:

- `AGENTS.md`
- `agents.md`
- `CLAUDE.md`
- `claude.md`

This causes dirty checkouts on case-insensitive macOS filesystems. Canonical target is uppercase.

## REC-003: Promtail EOL

Resolved in this session for the local process-compose stack: the active log collector is now
Grafana Alloy. Remaining work is parity validation for labels, dashboards, and packaged deploy
surfaces.

Local macOS note: Homebrew's `grafana-alloy` formula conflicts with `alloy-analyzer` because both
own an `alloy` binary. The validated local path is the official Grafana release binary installed
as `$HOME/.local/bin/grafana-alloy`; wrappers now discover that path automatically.

## REC-007: Legacy Jaeger is explicit-only

Resolved in the active runtime surfaces. The default local observability graph no longer requires
Jaeger, and the prod-like compose plus k8s backend env now point at Tempo/shared collector
contracts. Any remaining Jaeger references should stay behind explicit compatibility flags or
historical documentation.

Current follow-up:

- `deploy/monitoring/alloy-local.alloy` now uses a `tempo` exporter label while keeping the same
  OTLP endpoint.
- Remaining Jaeger references are documentation-only and should not be revived as active defaults.

## REC-004: Redis responsibilities are too broad

Current configs and dependencies still expose the service through Redis protocol clients and
`REDIS_URL`, but Dragonfly is now the preferred runtime for cache, rate-limit, and session-shaped
work. This session moved Go SSE notification fan-out to NATS JetStream and made Dragonfly the
local default.

Classification from this session:

- Keep Dragonfly-backed Redis-compatible: cache, rate limiting, session/OAuth CSRF state,
  health/bootstrap/exporter
  wiring.
- Move to NATS JetStream: notification pub/sub (implemented for Go SSE notifications).
- Move to PostgreSQL: feature flags and operational config.

Remaining work:

- Move feature flags and operational config out of Redis-backed paths.
- Install/smoke the Dragonfly binary locally.
- Validate notification redelivery and duplicate behavior with multiple backend instances.

## REC-005: Traceability architecture is over-split

Multiple services and models cover adjacent traceability, history, event sourcing, workflow,
snapshot, and advanced traceability concerns. Completion risk is high until domains are consolidated.

## REC-006: Rust is archived, not active

Rust/Tauri exists in archived desktop example material, but no active Rust backend or frontend
runtime is present on current `origin/main`.

## Validation Note: webhooks import blocker

The full `tracertm.api.main` import is still blocked by an unrelated syntax issue in
`src/tracertm/api/routers/webhooks.py`. The QA/test router extraction was validated by
compiling the touched files and checking the extracted router tables directly.

## Current Extraction State

The `/api/v1/problems/*` cluster is now extracted into
`src/tracertm/api/routers/problems.py`, including the project stats endpoint.
`src/tracertm/api/main.py` now only registers the router and no longer owns the
problem handlers directly.
