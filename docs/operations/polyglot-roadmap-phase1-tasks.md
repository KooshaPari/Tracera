# Polyglot Roadmap: Phase 1 Action Tickets (Go/Zig/Mojo)

Date: 2026-07-18  
Status: COMPLETE

## Immediate execution objective
Lock frontend/backend contract semantics and validation gates before introducing Go/Zig/Mojo layers.

## Ticket set

- P1-T1 — Contract lock file [DONE]
  - Use `docs/operations/openapi_contract_guard.md` as canonical required Tracera API surface for Option A.
  - Must list all 12 API endpoints used by the frontend client.
  - Acceptance: Rust route list and frontend helper list match exactly.

- P1-T2 — Automated parity tests [DONE]
  - Maintain test coverage that all 12 endpoints are callable and decodable by `traceraClient`.
  - Keep non-JSON and malformed payload fallback behavior asserted.
- Acceptance: `npm run test:unit` stays green.

- P1-T3 — Runtime parity gates [DONE]
  - Add/confirm `smoke:parity` for GET contract checks:
    - `/health`
    - `/sdlc-pm/sprints`
    - `/org-intel/teams`
    - `/org-intel/metrics`
    - `/evidence`
  - Add/confirm `smoke:post` for POST compute checks:
    - `/api/v1/coverage-matrix`
    - `/api/v1/impact`
    - `/api/v1/confidence`
    - `/api/v1/governance/spec-check`
    - `/api/v1/blast-radius`
    - `/api/v1/trace/forward/:artifact_id`
    - `/api/v1/trace/reverse/:artifact_id`
  - Acceptance: both commands fail fast on mismatch.

- P1-T4 — Frontend parity evidence lock [DONE]
  - Confirm nav IDs and route mapping:
    - `TopNav` includes `trace`.
    - `App` consumes `'trace'`.
  - Acceptance: regression path shows Evidence tab renders when selected and
    `npm run test:routes` remains green.

- P1-T5 — Go phase precheck package [DONE]
  - Add a short ADR note under `docs/operations/` with:
    - why Go is first language layer,
    - boundary ownership,
    - kill-switch toggles.
  - Acceptance: no backend contract changes before approval.

## Execution command list

```bash
cd Tracera/frontend
npm run test:unit
npm run build
npm run smoke:parity   # GET parity smoke (default: http://127.0.0.1:8080)
npm run smoke:post     # POST parity smoke (default: http://127.0.0.1:8080)
```

CI phase-1 gate expectation:
`frontend-contract-checks` should run:
`npm run test:unit`, `npm run smoke:parity`, and `npm run smoke:post` (conditional).

## Exit criteria for Phase 1
- Frontend/backend endpoint contract is locked and tested.
- No contract drift can merge without CI gates.
- Phase 2 Go skeleton may begin only after P1 tickets pass in CI.

## Phase 2 kickoff (go sidecar bootstrap completed)

- P2-T1 — Sidecar scaffolding implemented behind feature flag
  - Added `sidecar/go` module with `TRACERA_SIDE_CAR_ENABLED=false` default.
  - Added startup config parser + tests.
  - Acceptance: `go test ./...` and `go build ./cmd/tracera-sidecar` pass.

- P2-T2 — Contract boundary preserved
  - No Rust API surface touched by sidecar scaffold.
  - Acceptance: frontend parity suite unchanged and green:
    - `npm run test:unit`
    - `npm run smoke:parity`
    - `npm run smoke:post`

## Execution evidence (completed)

- `npm run test:unit` ✅
- `npm run build` ✅
- `npm run smoke:parity` ✅
- `npm run smoke:post` ✅
- `npm run typecheck` (from `frontend`) ✅

Observed runtime target:
- `curl http://127.0.0.1:8080/health` returned `{ "status": "ok" }`.
