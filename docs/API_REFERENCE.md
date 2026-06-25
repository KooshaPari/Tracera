# API Reference (Tracera)

## Public operational endpoints

- `GET /health`
- `GET /ready`
- `GET /healthz`
- `GET /readyz`

## API endpoint target set (24-business + governance slice, `/api/v1`)

This list is the audit-facing contract for governance and traceability evidence.

### Auth

- `GET /api/v1/auth/me`

### Evidence

- `GET /api/v1/evidence`
- `POST /api/v1/evidence`
- `GET /api/v1/evidence/health`

### Impact / traceability

- `GET /api/v1/impact/forward/{artifact_id}`
- `GET /api/v1/impact/reverse/{artifact_id}`
- `POST /api/v1/impact`
- `POST /api/v1/impact/blast-radius`
- `POST /api/v1/coverage-matrix`
- `POST /api/v1/governance/spec-check`
- `POST /api/v1/confidence`

### SDLC and org intelligence

- `GET /api/v1/sdlc-pm/health`
- `GET /api/v1/sdlc-pm/sprints`
- `GET /api/v1/sdlc-pm/stories`
- `POST /api/v1/sdlc-pm/sprints`
- `GET /api/v1/org-intel/health`
- `GET /api/v1/org-intel/metrics`
- `GET /api/v1/org-intel/teams`

### Ingestion + comments

- `POST /api/v1/ingest/github`
- `POST /api/v1/ingest/jira`
- `GET /api/v1/items/{item_id}/comments`
- `POST /api/v1/items/{item_id}/comments`
- `DELETE /api/v1/items/{item_id}/comments/{comment_id}`

### Code-trace

- `GET /api/v1/code-trace/{component_id}`

## Governance mapping

- FR→endpoint→test mapping: [`governance/policy/endpoint_traceability_map.md`](governance/policy/endpoint_traceability_map.md)
