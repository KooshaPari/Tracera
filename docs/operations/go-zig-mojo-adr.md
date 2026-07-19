# ADR-0001: Go-first polyglot execution boundary for Tracera

Date: 2026-07-18  
Status: Approved (Phase-1 complete)

## Decision

- Keep Rust as the API-of-record for all persistence and live service contracts in Phase 1.
- Introduce Go only as a process/orchestration sidecar in later phases.
- Use Zig only as an optional optimization module for deterministic compute transforms after contract gates are stable.
- Defer Mojo until tooling and CI support are proven in an isolated spike.

## Why Go is first

1. Low integration risk with existing REST/CLI workflows.
2. Strong typed stdlib, straightforward containerized deployment, and clean subprocess/IPC control.
3. Fast iteration for orchestration and worker semantics without touching data-plane contracts.

## Contract ownership boundary

1. **Rust (`crates/tracera-server`) retains authoritative contract**
   - HTTP routes under `/health`, `/evidence`, `/sdlc-pm`, `/org-intel`, `/api/v1`.
   - Migration and persistence behavior.
2. **Go sidecar (future) may own:**
   - scheduling/distribution
   - process supervision and heartbeat
   - non-authoritative queue/state helper services
3. **No API contract drift is permitted without updating:**
   - `docs/operations/openapi_contract_guard.md`
   - `frontend-option-a-alignment.md`
   - `polyglot-roadmap-phase1-tasks.md`

## Kill-switches

- `TRACERA_SIDE_CAR_ENABLED=false` (default): disables Go orchestration path.
- `TRACERA_ZIG_OPT_OUT=true`: disables Zig-accelerated transforms if added.
- `TRACERA_MOJO_EXPERIMENT=disabled` default; require explicit activation for any Mojo binary.

## Phase-1 guardrail

Phase 1 is complete only when:
- API contract lock file is authoritative.
- `npm run test:unit`, `npm run smoke:parity`, and `npm run smoke:post` pass in CI.
- Any sidecar introduction is blocked until those gates are green.
