# API Reference (Tracera)

## Public operational endpoints

- `GET /health`
- `GET /ready`
- `GET /healthz`
- `GET /readyz`

## API endpoint target set (hybrid surface)

Current Tracera frontend/runtime contract is split:

- **Governance compute endpoints** remain on `/api/v1/*`.
- **Operational and metadata endpoints** are mounted at root paths for compatibility.

This list is the audit-facing contract for governance and traceability evidence.

### Auth

- `GET /api/v1/auth/me` (auth route not currently mounted in `tracera-server`)

### Evidence

- `GET /evidence`
- `POST /evidence`
- `GET /evidence/health`

### Impact / traceability

- `POST /api/v1/trace/forward/{artifact_id}`
- `POST /api/v1/trace/reverse/{artifact_id}`
- `POST /api/v1/impact`
- `POST /api/v1/blast-radius`
- `POST /api/v1/coverage-matrix`
- `POST /api/v1/governance/spec-check`
- `POST /api/v1/confidence`

### SDLC and org intelligence

- `GET /sdlc-pm/health`
- `GET /sdlc-pm/sprints`
- `GET /sdlc-pm/stories`
- `POST /sdlc-pm/sprints`
- `GET /org-intel/health`
- `GET /org-intel/metrics`
- `GET /org-intel/teams`

### Ingestion + comments

- `POST /ingest/github`
- `POST /ingest/jira`
- `GET /api/v1/items/{item_id}/comments`
- `POST /api/v1/items/{item_id}/comments`
- `DELETE /api/v1/items/{item_id}/comments/{comment_id}`

### Code-trace

- `GET /api/v1/code-trace/{component_id}`

## Governance mapping

- FR→endpoint→test mapping: [`governance/policy/endpoint_traceability_map.md`](governance/policy/endpoint_traceability_map.md)
