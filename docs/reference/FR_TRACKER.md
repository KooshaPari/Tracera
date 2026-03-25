# TracerTM: FR Implementation Tracker

| FR ID | Description | Status | Code Location |
|-------|-------------|--------|---------------|
| FR-TRACE-001 | Bidirectional requirement-artifact links | In Progress | `backend/internal/graph/`, `backend/internal/models/` |
| FR-TRACE-002 | 5 architectural lenses | In Progress | `backend/internal/features/` |
| FR-TRACE-003 | Impact analysis | In Progress | `backend/internal/graph/` |
| FR-TRACE-004 | Coverage reporting | Planned | - |
| FR-GRAPH-001 | Interactive dependency graphs | In Progress | `frontend/apps/web/` |
| FR-GRAPH-002 | Impact propagation highlight | Planned | - |
| FR-GRAPH-003 | Graph filtering and search | Planned | - |
| FR-RT-001 | WebSocket live updates | In Progress | `backend/internal/nats/`, `backend/internal/events/` |
| FR-RT-002 | Presence indicators | Planned | - |
| FR-RT-003 | Audit trail | In Progress | `backend/internal/handlers/` |
| FR-AGENT-001 | AI link suggestion | In Progress | `backend/internal/agents/` |
| FR-AGENT-002 | Commit-triggered re-index | In Progress | `backend/internal/codeindex/` |
| FR-AGENT-003 | Semantic similarity search | In Progress | `backend/internal/embeddings/` |
| FR-OBS-001 | Prometheus metrics | In Progress | `backend/internal/metrics/` |
| FR-OBS-002 | Structured logging | Implemented | `backend/internal/` (all services) |
| FR-OBS-003 | Distributed tracing | In Progress | `backend/internal/middleware/` |
| FR-ITEM-001 | Item CRUD | Implemented | `backend/internal/handlers/`, `backend/internal/models/` |
| FR-ITEM-002 | Figma integration | In Progress | `backend/internal/figma/` |
| FR-ITEM-003 | Full-text document search | In Progress | `backend/internal/docindex/`, `backend/internal/docservice/` |
| FR-AUTH-001 | Session auth with CSRF | Implemented | `backend/internal/auth/` |
| FR-AUTH-002 | RBAC on API endpoints | Implemented | `backend/internal/middleware/` |
