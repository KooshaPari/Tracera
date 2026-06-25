# API Reference (Tracera)

This is the endpoint stub used for governance and audit tracing.

## Operational endpoints

- `GET /health`
- `GET /ready`
- `GET /healthz`
- `GET /readyz`

## API surface (24-endpoint audit target)

### Auth

- `GET /api/v1/auth/me`

### Evidence

- `GET /api/v1/evidence`
- `POST /api/v1/evidence`
- `GET /api/v1/evidence/health`

### Impact / Traceability

- `GET /api/v1/impact/forward/{artifact_id}`
- `GET /api/v1/impact/reverse/{artifact_id}`
- `POST /api/v1/impact`
- `POST /api/v1/impact/blast-radius`
- `POST /api/v1/coverage-matrix`
- `POST /api/v1/governance/spec-check`
- `POST /api/v1/confidence`

### SDLC & Org intelligence

- `GET /api/v1/sdlc-pm/health`
- `GET /api/v1/sdlc-pm/sprints`
- `GET /api/v1/sdlc-pm/stories`
- `POST /api/v1/sdlc-pm/sprints`
- `GET /api/v1/org-intel/health`
- `GET /api/v1/org-intel/metrics`
- `GET /api/v1/org-intel/teams`

### Ingestion and comments

- `POST /api/v1/ingest/github`
- `POST /api/v1/ingest/jira`
- `GET /api/v1/items/{item_id}/comments`
- `POST /api/v1/items/{item_id}/comments`
- `DELETE /api/v1/items/{item_id}/comments/{comment_id}`

## Governance linkage

See [`docs/governance/policy/endpoint_traceability_map.md`](docs/governance/policy/endpoint_traceability_map.md)
for the FR→endpoint→test matrix tied to the audit target.
