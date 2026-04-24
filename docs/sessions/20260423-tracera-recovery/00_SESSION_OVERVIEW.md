# Tracera Recovery Session

## Goal

Restore the live `Tracera` tree from the recovered implementation source and re-align
the governance docs and observability wiring around the native OTLP collector path.

## Status

- Recovered implementation source mirrored into `Tracera`
- Governance validation passes
- Remaining historical tracing references are being treated as archival only

## Scope

- Core backend, frontend, Python services, tests, deployment, and config surfaced from
  `Tracera-recovered`
- Live Tracera FR coverage repaired for `FR-TRAC-004` through `FR-TRAC-006`
- Runtime backend manifest switched from the legacy tracing env var to the shared OTLP collector endpoint
