# Tracera Frontend/API Contract Guard (Option A baseline)

## Scope

This document locks the frontend runtime contract the Rust Tracera server must preserve for
Option A parity. It is the compatibility source-of-truth for the frontend dashboard and
any future language-sidecar layers (Go/Zig/Mojo).

## Contract surface (MUST-MATCH)

### GET endpoints

| Method | Path | Consumer | Expected shape |
|---|---|---|---|
| GET | `/health` | `traceraClient.getHealth`, Dashboard status widget | Object (default `{ status: 'unknown' }`) |
| GET | `/readyz` | `traceraClient.getReadiness`, deployment/readiness probes | Object (default `{ status: 'unknown' }`) |
| GET | `/sdlc-pm/sprints` | `traceraClient.getSprints`, Dashboard sprints view | Array |
| GET | `/org-intel/teams` | `traceraClient.getTeams`, Dashboard teams card | Array |
| GET | `/org-intel/metrics` | `traceraClient.getMetrics`, Dashboard metrics cards | Object |
| GET | `/evidence` | `traceraClient.getEvidence`, Trace viewer | `{ count?: number, items?: array }` accepted; defaults supported |

### POST endpoints (extended parity)

| Method | Path | Consumer | Expected shape |
|---|---|---|---|
| POST | `/api/v1/coverage-matrix` | `traceraClient.postCoverageMatrix` | Object |
| POST | `/api/v1/impact` | `traceraClient.postImpact` | Object |
| POST | `/api/v1/confidence` | `traceraClient.postConfidence` | Object |
| POST | `/api/v1/governance/spec-check` | `traceraClient.postSpecCheck` | Object |
| POST | `/api/v1/blast-radius` | `traceraClient.postBlastRadius` | Object |
| POST | `/api/v1/trace/forward/:artifact_id` | `traceraClient.postTraceForward` | Object |
| POST | `/api/v1/trace/reverse/:artifact_id` | `traceraClient.postTraceReverse` | Object |

## Evidence for enforcement

- Runtime client parity:
  - `frontend/apps/web/src/services/traceraClient.js`
- Contract tests:
  - `frontend/scripts/test-tracera-client.mjs`
  - `frontend/scripts/test-contract-doc.mjs` (checks every documented path against the client)
- Runtime parity smoke:
  - `npm run smoke:parity` (GET surface)
  - `npm run smoke:post` (POST surface)
- CI gate:
  - `.github/workflows/frontend-contract-checks.yml` runs:
    - `test:unit`
    - `smoke:parity` (conditional on `TRACERA_API_BASE`)
    - `smoke:post` (conditional on `TRACERA_API_BASE`)

The contract-document parity check is part of `npm run test:unit`; changing the markdown
without updating the client fails CI before sidecar work can merge.

## Governance rule

No code movement into Go/Zig/Mojo is approved until this contract remains green across:
1) client contract tests,
2) parity smoke gates,
3) CI workflow execution evidence.

## Browser deployment transport policy

`VITE_API_BASE` is consumed by browser JavaScript. A non-loopback `http://` value is
rejected by `npm run test:api-base` because it causes mixed-content failures from an
HTTPS dashboard and exposes API traffic without transport encryption. Production builds
must use an HTTPS ingress (for example `https://tracera.pheno.studio`).

`ALLOW_INSECURE_API_BASE=1` is an explicit local-development escape hatch only; it must
not be set in deployment or CI environments.
