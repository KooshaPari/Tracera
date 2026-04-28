# Phase 4 File Size Baseline Report

**Date**: 2026-02-02
**Goal**: <500 lines per file across entire codebase
**Status**: 🔴 172 files exceeding 500 lines

---

## Executive Summary

**Total Violations**: 172 files >500 lines
- **Python**: 20 files (largest: 9,768 lines)
- **Go**: 16 files (largest: 6,799 lines - auto-generated)
- **Frontend**: 136 files (largest: 4,004 lines - schema)

**Largest Violators**:
1. Python main.py: 9,768 lines (19.5x over limit!)
2. Frontend schema.ts: 4,004 lines (8x over limit!)
3. Go docs.go: 6,799 lines (auto-generated, excluded)

---

## Python Violations: 20 files

### Tier 1: Critical (>5,000 lines)
1. `src/tracertm/api/main.py` - **9,768 lines** ⚠️ CRITICAL PRIORITY

### Tier 2: Very High (2,000-5,000 lines)
2. `src/tracertm/api/routers/item_specs.py` - **3,203 lines**
3. `src/tracertm/services/spec_analytics_service.py` - **2,664 lines**
4. `src/tracertm/cli/commands/item.py` - **2,059 lines**

### Tier 3: High (1,000-2,000 lines) - 12 files
5. `src/tracertm/mcp/tools/param.py` - 1,822 lines
6. `src/tracertm/storage/local_storage.py` - 1,712 lines
7. `src/tracertm/cli/commands/project.py` - 1,388 lines
8. `src/tracertm/repositories/item_spec_repository.py` - 1,350 lines
9. `src/tracertm/api/client.py` - 1,335 lines
10. `src/tracertm/api/routers/specifications.py` - 1,304 lines
11. `src/tracertm/schemas/item_spec.py` - 1,223 lines
12. `src/tracertm/services/stateless_ingestion_service.py` - 1,072 lines
13. `src/tracertm/storage/sync_engine.py` - 1,068 lines
14. `src/tracertm/models/item_spec.py` - 1,066 lines
15. `src/tracertm/services/item_spec_service.py` - 1,036 lines
16. `src/tracertm/cli/commands/import_cmd.py` - 1,027 lines
17. `src/tracertm/cli/commands/link.py` - 1,017 lines

### Tier 4: Medium (500-1,000 lines) - 4 files
18. `src/tracertm/services/ai_tools.py` - 993 lines
19. `src/tracertm/cli/commands/design.py` - 897 lines
20. `src/tracertm/repositories/specification_repository.py` - 850 lines

---

## Go Violations: 16 files

### Auto-Generated (EXCLUDE from refactoring) - 4 files
- ❌ `backend/docs/tracertm_docs.go` - 6,799 lines (swagger)
- ❌ `backend/docs/docs.go` - 6,799 lines (swagger)
- ❌ `backend/internal/db/queries.sql.go` - 4,045 lines (sqlc)
- ❌ `backend/pkg/proto/tracertm/v1/tracertm.pb.go` - 2,005 lines (protobuf)

### Integration Tests (5 files) - Split by feature
1. `backend/tests/integration/service_integration_test.go` - 1,490 lines
2. `backend/tests/integration/endpoints_test.go` - 1,479 lines
3. `backend/internal/handlers/item_handler_test.go` - 1,238 lines
4. `backend/internal/services/temporal_service_test.go` - 1,214 lines
5. `backend/internal/equivalence/handler_test.go` - 1,159 lines

### Handlers (7 files) - Extract by responsibility
6. `backend/internal/equivalence/handler.go` - 1,310 lines
7. `backend/tests/e2e/service_layer_e2e_test.go` - 1,149 lines
8. `backend/internal/handlers/handlers_integration_test.go` - 1,129 lines
9. `backend/internal/server/server.go` - 1,109 lines
10. `backend/internal/services/item_service_test.go` - 1,067 lines
11. `backend/internal/db/queries_test.go` - 1,055 lines
12. `backend/internal/equivalence/service_test.go` - 1,030 lines

---

## Frontend Violations: 136 files

### Tier 1: Critical (>2,000 lines) - 3 files
1. `frontend/apps/web/src/api/schema.ts` - **4,004 lines** (auto-generated OpenAPI schema)
2. `frontend/apps/web/src/mocks/enhanced-data.ts` - **2,466 lines** (mock data)
3. `frontend/apps/web/src/hooks/useItemSpecs.ts` - **2,095 lines**

### Tier 2: Very High (1,500-2,000 lines) - 2 files
4. `frontend/apps/web/src/pages/projects/views/IntegrationsView.tsx` - 1,815 lines
5. `frontend/apps/web/src/hooks/useSpecifications.ts` - 1,528 lines

### Tier 3: High (1,000-1,500 lines) - 10 files
6. `frontend/apps/web/src/views/ItemsTableView.tsx` - 1,514 lines
7. `frontend/apps/web/src/components/layout/Sidebar.tsx` - 1,451 lines
8. `frontend/apps/web/src/routeTree.gen.ts` - 1,400 lines (auto-generated router)
9. `frontend/apps/web/src/views/ItemDetailView.tsx` - 1,232 lines
10. `frontend/apps/web/src/components/graph/UnifiedGraphView.tsx` - 1,167 lines
11. `frontend/apps/web/src/components/graph/FlowGraphViewInner.tsx` - 1,166 lines
12. `frontend/apps/web/src/__tests__/pages/ProjectsList.test.tsx` - 1,135 lines
13. `frontend/apps/web/src/__tests__/integration/app-integration.test.tsx` - 1,095 lines
14. `frontend/apps/web/src/__tests__/api/endpoints.comprehensive.test.ts` - 1,087 lines
15. `frontend/apps/web/src/views/details/RequirementDetailView.tsx` - 1,073 lines

### Tier 4: Medium-High (500-1,000 lines) - 121 files
- 121 files between 500-1,000 lines (components, views, hooks, tests)

### E2E Tests (22 files >500 lines)
- Largest: bulk-operations.spec.ts (1,142 lines)
- Most tests range 500-1,200 lines

### Packages (6 files >500 lines)
- `frontend/packages/types/src/index.ts` - 1,268 lines
- `frontend/packages/types/src/entity-hierarchy.ts` - 680 lines
- `frontend/packages/types/src/temporal.ts` - 612 lines
- `frontend/packages/types/src/canonical.ts` - 611 lines
- `frontend/packages/types/src/progress.ts` - 580 lines

---

## Summary by Language

| Language | Total Violations | Largest File | Avg Violation Size |
|----------|-----------------|--------------|-------------------|
| Python | 20 | 9,768 lines | 1,711 lines |
| Go | 16 (12 manual) | 1,490 lines* | 1,219 lines* |
| Frontend | 136 | 4,004 lines | 852 lines |
| **TOTAL** | **172** | **9,768** | **973 lines** |

*Excluding auto-generated files

---

## Extraction Estimates

### Python: 20 files → ~66 modules
- main.py (9,768) → 20 modules (~450 lines each)
- Tier 1-2 (4 files, 11,694 lines) → 26 modules
- Tier 3 (12 files, 14,514 lines) → 36 modules
- Tier 4 (4 files, 2,740 lines) → 8 modules

### Go: 12 files → ~36 modules
- Integration tests (5 files) → 15 modules
- Handlers (7 files) → 21 modules

### Frontend: 136 files → ~204 modules
- Tier 1 (3 files) → 9 modules (schema is auto-gen, may exclude)
- Tier 2-3 (12 files) → 36 modules
- Tier 4 (121 files) → 159 modules (split larger ones 2-3 ways)

**Total Modules to Create**: ~306 modules
**Total Agent-Hours**: 150-200 hours
**Wall Clock (async swarm)**: 15-25 hours

---

## Priority Order (Recommended)

**Phase 4.1**: Python main.py (CRITICAL)
- 1 file → 20 modules
- 26 agents, 3-5 hours wall clock
- **HIGHEST IMPACT**: Eliminates worst violation

**Phase 4.2**: Frontend Critical (3 files)
- schema.ts (auto-gen, may exclude)
- enhanced-data.ts (mock data) → 5 modules
- useItemSpecs.ts (2,095) → 5 modules
- 10 agents, 2-3 hours wall clock

**Phase 4.3**: Python Tier 1-2 (4 files)
- 4 files → 26 modules
- 8 agents, 4-6 hours wall clock

**Phase 4.4**: Go Tests & Handlers (12 files)
- 12 files → 36 modules
- 24 agents, 2-4 hours wall clock

**Phase 4.5**: Frontend Tier 2-3 (12 files)
- 12 files → 36 modules
- 24 agents, 3-5 hours wall clock

**Phase 4.6**: Remaining 137 files (Python Tier 3-4 + Frontend Tier 4)
- 137 files → 214 modules
- 50-100 agents, 8-12 hours wall clock

---

## Auto-Generated Files (Exclude)

**Python**: None identified
**Go**: 4 files (docs, sqlc, protobuf)
**Frontend**: 2-3 files
- `api/schema.ts` (4,004 lines) - OpenAPI auto-gen
- `routeTree.gen.ts` (1,400 lines) - TanStack Router auto-gen
- `types/dist/index.d.ts` (942 lines) - TypeScript build output

**Action**: Exclude these from refactoring, add to allow-list in file size checker

---

## Next Steps

1. **Immediate**: Launch Phase 4.1 (main.py decomposition)
2. **Short-term**: Phases 4.2-4.4 (critical files)
3. **Medium-term**: Phase 4.6 (remaining files)
4. **Infrastructure**: File size pre-commit hook + CI check

---

**Baseline Status**: 🟢 COMPLETE
**Phase 4 Status**: 🟡 READY TO LAUNCH
**First Target**: main.py (9,768 → <500 lines)
**Owner**: BMAD Master / Tech Lead
