# Tracera Frontend-Backend Option A Alignment

## Current alignment target
This frontend update aligns the web dashboard with the live Rust Tracera API surface.

Active calls from the web dashboard now go through `apps/web/src/services/traceraClient.js`:
- `GET /health`
- `GET /sdlc-pm/sprints`
- `GET /org-intel/teams`
- `GET /org-intel/metrics`
- `GET /evidence`
- Optional POST computation endpoints are now contract-tested and available in client helper:
  - `POST /api/v1/coverage-matrix`
  - `POST /api/v1/impact`
  - `POST /api/v1/confidence`
  - `POST /api/v1/governance/spec-check`
  - `POST /api/v1/blast-radius`
  - `POST /api/v1/trace/forward/:artifact_id`
  - `POST /api/v1/trace/reverse/:artifact_id`

## Runtime behavior
- `Dashboard.jsx` uses one client module for API calls.
- Each call is fetched in parallel with `Promise.allSettled`.
- Partial failures are surfaced in the UI while preserving partial state.
- Non-JSON responses are normalized defensively to avoid hard parser failures.
- Contract source-of-truth for Option A is `docs/operations/openapi_contract_guard.md`.

## Validation commands (required)

```bash
cd Tracera/frontend
npm run build          # web bundle build
npm run test:unit      # traceraClient contract + dashboard state tests (mocked)
npm run smoke:parity   # endpoint parity smoke (default: http://127.0.0.1:8080)
npm run smoke:post     # runtime POST endpoint smoke (server required)
npm run typecheck      # workspace typecheck entrypoint
```

Optional (GUI + electrobun dependencies required for host assertions):

```bash
npm run --prefix apps/desktop test:e2e
npm run --prefix apps/desktop build
```

Desktop validation now includes:

- `npm run --prefix apps/desktop test:e2e` (host/headless aware; log invariants are conditional on DISPLAY/CI)
- `npm run --prefix apps/desktop build` (desktop bundle build)
