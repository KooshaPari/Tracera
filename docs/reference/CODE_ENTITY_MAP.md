# TracerTM: Code Entity Map

## Backend (Go)

| Entity | Path | Maps To |
|--------|------|---------|
| API Server | `backend/cmd/tracertm/main.go` | FR-TRACE-001, FR-ITEM-001 |
| Auth middleware | `backend/internal/auth/` | FR-AUTH-001, FR-AUTH-002 |
| Item handlers | `backend/internal/handlers/` | FR-ITEM-001, FR-RT-003 |
| Graph engine | `backend/internal/graph/` | FR-TRACE-001, FR-TRACE-003, FR-GRAPH-001 |
| NATS event bus | `backend/internal/nats/` | FR-RT-001 |
| Events system | `backend/internal/events/` | FR-RT-001, FR-RT-003 |
| Code indexer | `backend/internal/codeindex/` | FR-AGENT-002 |
| Embeddings | `backend/internal/embeddings/` | FR-AGENT-003 |
| Agent integration | `backend/internal/agents/` | FR-AGENT-001 |
| Doc indexer | `backend/internal/docindex/` | FR-ITEM-003 |
| Doc service | `backend/internal/docservice/` | FR-ITEM-003 |
| Figma client | `backend/internal/figma/` | FR-ITEM-002 |
| Metrics | `backend/internal/metrics/` | FR-OBS-001 |
| Config | `backend/internal/config/` | All |
| Database layer | `backend/internal/database/`, `backend/internal/db/` | FR-TRACE-001 |
| Cache | `backend/internal/cache/` | FR-TRACE-001 |
| Health checks | `backend/internal/health/` | FR-OBS-001 |

## Frontend (React/TypeScript)

| Entity | Path | Maps To |
|--------|------|---------|
| Web app | `frontend/apps/web/` | FR-GRAPH-001, FR-GRAPH-002, FR-GRAPH-003 |
| Desktop app | `frontend/apps/desktop/` | FR-GRAPH-001 |
| Docs site | `frontend/apps/docs/` | FR-ITEM-003 |
| Storybook | `frontend/apps/storybook/` | - |

## Infrastructure

| Entity | Path | Maps To |
|--------|------|---------|
| Alembic migrations | `alembic/` | FR-TRACE-001 |
| Process Compose | `process-compose.yml` | FR-OBS-001 |
| Caddy config | `backend/configs/` | FR-AUTH-001 |
