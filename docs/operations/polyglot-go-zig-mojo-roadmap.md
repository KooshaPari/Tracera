# Tracera Polyglot Strategy: Go/Zig/Mojo (Go primary + Zig optional + Mojo deferred)

Status: Draft for implementation (Actionable)  
Last updated: 2026-07-18

## Objective
- Keep Tracera core correctness anchored in Rust (`crates/tracera-server`) for protocol stability and evidence persistence.
- Introduce polyglot components where they provide measurable gains without destabilizing the live dashboard contract.
- Preserve endpoint compatibility used by `apps/web/src/services/traceraClient.js`.

## Current parity target (must remain green)
- **Frontend/API compatibility is mandatory first** (gated):
  - GET: `/health`, `/sdlc-pm/sprints`, `/org-intel/teams`, `/org-intel/metrics`, `/evidence`
  - POST: `/api/v1/coverage-matrix`, `/api/v1/impact`, `/api/v1/confidence`, `/api/v1/governance/spec-check`, `/api/v1/blast-radius`, `/api/v1/trace/forward/:artifact_id`, `/api/v1/trace/reverse/:artifact_id`
- Frontend hardening in place:
  - partial-failure tolerant dashboard state merge
  - non-JSON-safe response handling
  - nav ID alignment (`trace`)
- Runtime gates:
  - `npm run build`
  - `npm run test:unit`
  - `npm run smoke:parity`
  - `npm run smoke:post`

## Architecture baseline
- **Rust** stays source of truth for:
  - API handlers and data contracts
  - SQLite persistence and migrations
- **Go** (next phase) only for orchestration/control workflows with explicit JSON boundaries.
- **Zig** (later) only for narrowly scoped deterministic transforms.
- **Mojo** remains deferred until a stable environment + CI ROI is proven.

## Phase 1 (Weeks 1–2): Contract hardening + readiness
- Canonicalize contract surface in:
  - `docs/operations/openapi_contract_guard.md`
  - `docs/operations/go-zig-mojo-adr.md`
  - `docs/operations/polyglot-roadmap-phase1-tasks.md` (newly maintained)
- Add/execute gates:
  - client parity tests (`frontend/scripts/test-tracera-client.mjs`)
  - dashboard state tests (`frontend/scripts/test-dashboard-state.mjs`)
  - runtime parity smoke (`npm run smoke:parity`)
  - runtime POST smoke (`npm run smoke:post`)
  - CI gates in `.github/workflows/frontend-contract-checks.yml`

## Phase 2 (Weeks 3–4): Go lane bootstrapping
- Add Go sidecar command dispatcher + worker helper behind flags.
- Add contract-bound integration test before any production traffic.

- Add CI bootstrap guard to keep the scaffold green:
  - New `sidecar-bootstrap-checks` workflow in `.github/workflows/sidecar-bootstrap-checks.yml`
  - Runs `go test ./...` and `go build ./cmd/tracera-sidecar` on every sidecar-related change.
  - Status: completed baseline gate coverage.

## Phase 2 kickoff status (live)

- Sidecar bootstrap scaffold added:
  - `sidecar/go/go.mod`
  - `sidecar/go/cmd/tracera-sidecar/main.go`
  - `sidecar/go/internal/config/config.go`
  - `sidecar/go/internal/config/config_test.go`
  - `sidecar/go/README.md`
- Gate condition is enforced by env:
  - `TRACERA_SIDE_CAR_ENABLED=false` (default).
- Current status: scaffold in place, no traffic interception yet, contract unchanged.

### P2-T3 — Sidecar bootstrap CI gate [DONE]

- Added dedicated GitHub Actions workflow to validate sidecar compile/test on sidecar changes.
- Acceptance:
  - Workflow runs `go test ./...` and `go build ./cmd/tracera-sidecar` under `sidecar/go`.
  - No Rust route files or frontend contract artifacts changed by sidecar scaffold.
- Next: implement first non-authoritative worker contract test before enabling runtime routing flags.

## Phase 3 (Weeks 5–6): Zig utility lane
- Add Zig module only where measurable bottleneck is proven.
- Add boundary + benchmark tests.

## Phase 4 (Weeks 7–8): Mojo feasibility gate
- Deferred pending toolchain maturity, reproducibility, and cost/benefit evidence.

## Go/Zig/Mojo exit criteria
- No backend traffic shifts without:
  - green contract docs,
  - green runtime gates,
  - explicit ADR approval and rollout flag controls.
