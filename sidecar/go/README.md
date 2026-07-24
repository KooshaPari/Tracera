# Tracera Sidecar (Go) — Phase 2 Bootstrap

## Scope
- This is a non-authoritative Go bootstrap for orchestration/scheduling work.
- Rust remains the API/data contract owner in Phase 1 and Phase 2 precheck.

## Guardrails
- Contract ownership stays with `crates/tracera-server` and
  `docs/operations/openapi_contract_guard.md`.
- Sidecar is inert by default:
  - `TRACERA_SIDE_CAR_ENABLED=false` (default)
- Disable optional code paths immediately if needed:
  - `TRACERA_ZIG_OPT_OUT=true`
  - `TRACERA_MOJO_EXPERIMENT=disabled`

## Run
```bash
cd Tracera/sidecar/go
go build ./cmd/tracera-sidecar

TRACERA_SIDE_CAR_ENABLED=true TRACERA_API_BASE=http://127.0.0.1:8080 \\
  go run ./cmd/tracera-sidecar
```

Terminate with Ctrl+C.  

## Implementation notes
- Currently logs periodic heartbeats only.
- No Tracera API traffic path is changed by this component until a follow-up is approved.

