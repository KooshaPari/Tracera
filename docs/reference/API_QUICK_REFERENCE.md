# API Quick Reference

**TracerTM Requirements Traceability Matrix System**

---

## API Overview

| API | Endpoints | Focus | Access Pattern |
|-----|-----------|-------|-----------------|
| **Gateway** | 333 | Client entry point | HTTP/REST via :4000 |
| **Go Backend** | 83 | High-performance services | Internal (:8080), routed via gateway |
| **Python Services** | 256 | Domain logic, AI/ML | Internal (:4000), routed via gateway |
| **TOTAL** | **672** | Full system | Single unified gateway |

---

## Feature Areas (Top 15)

| Feature | Endpoints | Key Use Cases |
|---------|-----------|---------------|
| **Projects** | 98 | CRUD, versioning, export/import, stats, graphs |
| **Integrations** | 60 | GitHub, Linear, webhooks, OAuth, sync |
| **Auth** | 28 | Login, OAuth, device auth, token refresh |
| **Test Runs** | 24 | Execution, results, bulk operations |
| **Problems** | 22 | Issue tracking, RCA, status, workarounds |
| **Test Cases** | 22 | Definition, coverage, approval, deprecation |
| **Webhooks** | 22 | Event delivery, logs, regeneration |
| **Processes** | 20 | Versioning, execution, deprecation |
| **Test Suites** | 20 | Suite management, test grouping |
| **Graph** | 18 | Analysis, visualization, validation, caching |
| **Features** | 18 | Feature definition, scenarios |
| **Coverage** | 18 | Gap analysis, matrix, verification |
| **Blockchain** | 16 | Version chains, embeddings, baselines |
| **Items** | 14 | Requirements, metadata, pivot views |
| **Analysis** | 14 | Impact, cycles, gaps, health, shortest-path |

---

## Authentication

**Endpoints:** `/api/v1/auth/*`, `/api/v1/csrf-token`

```
POST   /api/v1/auth/login              → Session token
POST   /api/v1/auth/signup             → New account
POST   /api/v1/auth/refresh            → Refresh token
POST   /api/v1/auth/logout             → Clear session
GET    /api/v1/auth/me                 → Current user
POST   /api/v1/auth/verify             → Token verification
POST   /api/v1/auth/callback           → OAuth callback
GET    /api/v1/csrf-token              → CSRF protection
```

---

## Projects (Main Workspace)

**Endpoints:** `/api/v1/projects/*`

```
GET    /api/v1/projects                     → List all
POST   /api/v1/projects                     → Create
GET    /api/v1/projects/{id}                → Read
PUT    /api/v1/projects/{id}                → Update
DELETE /api/v1/projects/{id}                → Delete

# Versioning & Comparison
GET    /api/v1/projects/{id}/versions/compare              → Versions diff
POST   /api/v1/projects/{id}/versions/compare/bulk         → Bulk compare
GET    /api/v1/projects/{id}/versions/compare/summary      → Summary

# Graphs & Visualization
GET    /api/v1/projects/{id}/graph                         → Current graph
GET    /api/v1/projects/{id}/graphs                        → List graphs
GET    /api/v1/projects/{id}/graphs/{id}/diff              → Graph diff
GET    /api/v1/projects/{id}/graphs/{id}/report            → Report
POST   /api/v1/projects/{id}/graphs/{id}/snapshot          → Create snapshot
POST   /api/v1/projects/{id}/graphs/{id}/validate          → Validate

# Export/Import
POST   /api/v1/projects/{id}/export                        → Export data
POST   /api/v1/projects/{id}/import                        → Import data

# Statistics
GET    /api/v1/projects/{id}/coverage/stats                → Coverage metrics
GET    /api/v1/projects/{id}/problems/stats                → Problem count
GET    /api/v1/projects/{id}/test-cases/stats              → Test metrics
GET    /api/v1/projects/{id}/test-runs/stats               → Execution metrics
GET    /api/v1/projects/{id}/test-suites/stats             → Suite metrics

# Execution Management
GET    /api/v1/projects/{id}/execution-config              → Get config
PUT    /api/v1/projects/{id}/execution-config              → Update config
GET    /api/v1/projects/{id}/executions                    → List executions
POST   /api/v1/projects/{id}/executions                    → Start execution

# Search
POST   /api/v1/projects/{id}/search/advanced               → Advanced search
```

---

## Requirements Traceability

**Items** - Requirements definitions
```
GET    /api/v1/items                     → List all
POST   /api/v1/items                     → Create
GET    /api/v1/items/{id}                → Read
PUT    /api/v1/items/{id}                → Update
DELETE /api/v1/items/{id}                → Delete
POST   /api/v1/items/bulk-update         → Batch update
GET    /api/v1/items/summary             → Statistics
GET    /api/v1/items/{id}/pivot          → Pivot view
GET    /api/v1/items/{id}/pivot-targets  → Pivot targets
```

**Links** - Traceability relationships
```
GET    /api/v1/links                     → List all
POST   /api/v1/links                     → Create link
GET    /api/v1/links/{id}                → Read
PUT    /api/v1/links/{id}                → Update
DELETE /api/v1/links/{id}                → Delete
GET    /api/v1/links/grouped             → Grouped view
```

**Coverage** - Coverage analysis
```
GET    /api/v1/coverage                  → All coverage records
POST   /api/v1/coverage                  → Create
GET    /api/v1/coverage/{id}             → Read
PUT    /api/v1/coverage/{id}             → Update
DELETE /api/v1/coverage/{id}             → Delete
POST   /api/v1/coverage/{id}/verify      → Verify coverage
GET    /api/v1/coverage/gaps             → Identify gaps
GET    /api/v1/coverage/matrix           → Coverage matrix
```

---

## Testing & Quality

**Test Cases** (22 endpoints)
```
GET    /api/v1/test-cases                → List all
POST   /api/v1/test-cases                → Create
GET    /api/v1/test-cases/{id}           → Read
PUT    /api/v1/test-cases/{id}           → Update
DELETE /api/v1/test-cases/{id}           → Delete
POST   /api/v1/test-cases/{id}/approve   → Approve
POST   /api/v1/test-cases/{id}/submit-review → Submit review
GET    /api/v1/test-cases/{id}/coverage  → Coverage linkage
POST   /api/v1/test-cases/{id}/deprecate → Mark deprecated
```

**Test Runs** (24 endpoints)
```
GET    /api/v1/test-runs                 → List all
POST   /api/v1/test-runs                 → Create
GET    /api/v1/test-runs/{id}            → Read
DELETE /api/v1/test-runs/{id}            → Delete
POST   /api/v1/test-runs/{id}/start      → Start execution
POST   /api/v1/test-runs/{id}/complete   → Mark complete
POST   /api/v1/test-runs/{id}/cancel     → Cancel run
GET    /api/v1/test-runs/{id}/results    → Get results
POST   /api/v1/test-runs/{id}/results    → Record results
POST   /api/v1/test-runs/{id}/bulk-results → Bulk record
```

**QA Metrics** (12 endpoints)
```
GET    /api/v1/qa/metrics/summary        → Dashboard summary
GET    /api/v1/qa/metrics/coverage       → Coverage metrics
GET    /api/v1/qa/metrics/pass-rate      → Pass rates
GET    /api/v1/qa/metrics/defect-density → Defect metrics
GET    /api/v1/qa/metrics/flaky-tests    → Flaky test analysis
GET    /api/v1/qa/metrics/execution-history → Historical data
```

---

## Graph Analysis

**Endpoints:** `/api/v1/graph/analysis/*`

```
POST   /api/v1/graph/analysis/dependencies    → Dependencies
POST   /api/v1/graph/analysis/dependents      → Dependents
POST   /api/v1/graph/analysis/impact          → Impact analysis
POST   /api/v1/graph/analysis/cycles          → Cycle detection
POST   /api/v1/graph/analysis/centrality      → Centrality metrics
POST   /api/v1/graph/analysis/coverage        → Coverage analysis
POST   /api/v1/graph/analysis/metrics         → Compute metrics
POST   /api/v1/graph/analysis/shortest-path   → Shortest path
POST   /api/v1/graph/analysis/cache/invalidate → Clear cache
```

---

## Integrations

**GitHub** (20+ endpoints)
```
POST   /api/v1/integrations/github/app/install-url                → Get install URL
GET    /api/v1/integrations/github/app/installations              → List installs
POST   /api/v1/integrations/github/app/installations/{id}/link    → Link install
GET    /api/v1/integrations/github/projects                       → List projects
POST   /api/v1/integrations/github/projects/auto-link             → Auto-link
GET    /api/v1/integrations/github/projects/linked                → Linked projects
DELETE /api/v1/integrations/github/projects/{id}/unlink           → Unlink
GET    /api/v1/integrations/github/repos                          → List repos
GET    /api/v1/integrations/github/repos/{owner}/{repo}/issues    → List issues
```

**Linear** (8 endpoints)
```
GET    /api/v1/integrations/linear/teams                          → List teams
GET    /api/v1/integrations/linear/teams/{id}/issues              → Team issues
GET    /api/v1/integrations/linear/projects                       → List projects
```

**Webhooks** (22 endpoints)
```
GET    /api/v1/webhooks                  → List all
POST   /api/v1/webhooks                  → Create
GET    /api/v1/webhooks/{id}             → Read
PUT    /api/v1/webhooks/{id}             → Update
DELETE /api/v1/webhooks/{id}             → Delete
GET    /api/v1/webhooks/{id}/logs        → Event logs
GET    /api/v1/webhooks/{id}/status      → Status
POST   /api/v1/webhooks/{id}/regenerate-secret → New secret
```

**Sync** (4 endpoints)
```
POST   /api/v1/integrations/sync/trigger → Start sync
GET    /api/v1/integrations/sync/status  → Sync status
GET    /api/v1/integrations/sync/queue   → Queue status
```

---

## AI & Automation

**AI Services** (2 endpoints)
```
POST   /api/v1/ai/analyze                → Analyze content
POST   /api/v1/ai/stream-chat            → Streaming chat
```

**Workflows** (14 endpoints)
```
POST   /api/v1/workflows/trigger             → Trigger workflow
POST   /api/v1/workflows/graph-diff          → Graph diff workflow
POST   /api/v1/workflows/graph-export        → Graph export workflow
POST   /api/v1/workflows/graph-snapshot      → Graph snapshot
POST   /api/v1/workflows/graph-validate      → Graph validation
POST   /api/v1/workflows/integrations-sync   → Sync workflow
POST   /api/v1/workflows/integrations-retry  → Retry workflow
```

---

## HTTP Methods Summary

| Method | Count | % | Typical Use |
|--------|-------|---|------------|
| GET | 315 | 47% | Listing, searching, retrieval |
| POST | 251 | 37% | Creation, complex ops, streaming |
| DELETE | 58 | 9% | Deletion, cleanup |
| PUT | 46 | 7% | Full updates |
| OPTIONS | 2 | 0% | CORS preflight |

---

## Response Status Codes (Standard)

```
200 OK              → Success, data included
201 Created         → Resource created
204 No Content      → Success, no data
400 Bad Request     → Invalid input
401 Unauthorized    → Auth required
403 Forbidden       → Access denied
404 Not Found       → Resource missing
409 Conflict        → Data conflict
422 Unprocessable   → Validation failed
429 Rate Limited    → Too many requests
500 Server Error    → Internal error
503 Unavailable     → Service down
```

---

## Common Query Patterns

```
# Pagination
GET /api/v1/items?page=1&limit=50

# Filtering
GET /api/v1/items?status=active&type=requirement

# Sorting
GET /api/v1/items?sort=-created_at,name

# Search
POST /api/v1/projects/{id}/search/advanced
  { "query": "...", "filters": {...} }

# Bulk operations
POST /api/v1/items/bulk-update
  { "items": [{...}, {...}] }
```

---

## Gateway Routing (Port 4000)

```
http://localhost:4000
├── /api/v1/*          → Go API (:8080)
├── /api/py/*          → Python API (:4000 internal)
├── /docs              → API docs
├── /health            → Health check
├── /prometheus/*      → Metrics
├── /grafana/*         → Dashboards
└── /ws/*              → WebSockets
```

---

## Critical Endpoints

**Must test for system integrity:**
1. `/api/v1/auth/login` - Authentication
2. `/api/v1/projects` - Project management
3. `/api/v1/items` - Requirements
4. `/api/v1/links` - Traceability
5. `/api/v1/test-runs` - Testing
6. `/api/v1/graph/analysis/dependencies` - Graph analysis
7. `/api/v1/integrations/sync/trigger` - Sync operations
8. `/api/v1/health` - System health

---

## Documentation References

- Full details: `/docs/reports/FUNCTIONAL_REQUIREMENTS_EXTRACTION.md`
- Implementation guides: `/docs/guides/`
- OpenAPI specs: `/openapi/` (gateway-api.json, go-api.json, python-api.json)
- Test files: `/tests/`, `/backend/tests/`, `/frontend/`

---

**Last Updated:** 2026-02-11
