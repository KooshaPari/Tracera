# Test Inventory & Gap Analysis

> **Audit Date:** 2026-06-14  
> **Scope:** Go (`backend/` + `*_test.go`), Python (`src/tracertm/` + `tests/` + `*_test.py`), TypeScript (`frontend/` + `*.test.*` / `*.spec.*`)  
> **Method:** Read-only file-system scan; no builds or tests executed.  

---

## 1. Executive Summary

| Language | Source Files | Test Files | Test:Source Ratio | Unique Src Dirs | Unique Test Dirs |
|----------|-------------|------------|-------------------|-----------------|------------------|
| Go       | 388         | 357        | 0.92              | 76              | 73               |
| Python   | 478         | 517        | 1.08              | ~45             | ~47              |
| TypeScript | 1066      | 343        | 0.32              | 144             | 56               |

**Key Finding:** The Go backend has the strongest directory-level coverage (96% of source directories contain at least one `_test.go`). Python has more test files than source files, but many tests are large, monolithic coverage suites rather than fine-grained unit tests. The TypeScript frontend is the most under-tested: only 39% of source directories have test files, and the test-to-source ratio is 0.32.

---

## 2. Go Backend (`backend/`)

### 2.1 Overall Counts
- **Source files (`.go` excl. `_test.go`):** 388
- **Test files (`*_test.go`):** 357
- **Directories with source files:** 76
- **Directories with test files:** 73

### 2.2 Test Count by Top-Level Package

| Package/Area | Source Files | Test Files | Notes |
|--------------|-------------|------------|-------|
| `internal/services` | 32 | 45 | Well tested; includes `temporal_service.go`, `snapshot_service.go` |
| `internal/handlers` | 35 | 26 | Good coverage; `agent_handler.go`, `item_handler.go` tested |
| `internal/agents` | 17 | 15 | Strong coverage |
| `internal/equivalence` | 17 | 12 | Decent coverage |
| `internal/graph` | 17 | 13 | Good coverage |
| `internal/codeindex` | 15 | 6 | **Moderate gap** |
| `internal/middleware` | 13 | 6 | Moderate gap |
| `internal/events` | 11 | 4 | **Gap** |
| `internal/docindex` | 11 | 5 | Some gap |
| `internal/cache` | 11 | 8 | Good |
| `internal/auth` | 10 | 4 | **Gap** |
| `internal/journey` | 9 | 1 | **Large gap** |
| `internal/search` | 8 | 8 | Good |
| `internal/embeddings` | 8 | 9 | Good |
| `internal/db` | 7 | 5 | Moderate |
| `internal/clients` | 6 | 3 | **Gap** |
| `internal/server` | 6 | 9 | Good |
| `internal/progress` | 6 | 6 | Good |
| `internal/traceability` | 6 | 4 | **Gap** |
| `internal/database` | 6 | 7 | Good |
| `internal/websocket` | 6 | 9 | Good |
| `internal/nats` | 5 | 5 | Good |
| `internal/models` | 5 | 1 | **Gap** |
| `internal/repository` | 5 | 7 | Good |
| `internal/storybook` | 5 | 2 | **Gap** |
| `internal/temporal` | 4 | 3 | Moderate |
| `internal/metrics` | 4 | 1 | **Gap** |
| `internal/figma` | 4 | 1 | **Gap** |
| `internal/infrastructure` | 3 | 3 | Good |
| `internal/testutil` | 3 | 0 | **Zero tests** |
| `internal/config` | 3 | 2 | Moderate |
| `internal/resilience` | 2 | 2 | Good |
| `internal/validation` | 2 | 2 | Good |
| `internal/health` | 2 | 1 | **Gap** |
| `internal/realtime` | 2 | 1 | **Gap** |
| `internal/ratelimit` | 2 | 0 | **Zero tests** |
| `internal/sessions` | 1 | 0 | **Zero tests** |
| `internal/storage` | 1 | 0 | **Zero tests** |
| `internal/vault` | 1 | 0 | **Zero tests** |
| `internal/uuidutil` | 1 | 0 | **Zero tests** |
| `internal/tx` | 1 | 0 | **Zero tests** |

### 2.3 Biggest Untested Go Packages

| Directory | Source Files | Example Untested Files |
|-----------|-------------|------------------------|
| `backend/internal/codeindex/parsers` | 10 | `backend/internal/codeindex/parsers/*.go` (10 files) |
| `backend/cmd/tracertm` | 5 | `backend/cmd/tracertm/main.go` etc. |
| `backend/internal/testutil` | 3 | `backend/internal/testutil/*.go` (3 files) |
| `backend/internal/codeindex/sync` | 2 | `backend/internal/codeindex/sync/*.go` (2 files) |
| `backend/internal/integration` | 1 | `backend/internal/integration/*.go` (1 file) |
| `backend/internal/grpc/testing` | 1 | `backend/internal/grpc/testing/*.go` (1 file) |
| `backend/pkg/proto/tracertm/v1` | 2 | Generated protobuf (`tracertm.pb.go`, `tracertm_grpc.pb.go`) |

> The `backend/internal/codeindex/parsers` package is the largest fully untested Go package with 10 source files. Most `cmd/*` tools are also untested, though they are often entry-point utilities rather than library code.

---

## 3. Python Services (`src/tracertm/` + `tests/`)

### 3.1 Overall Counts
- **Source files (`.py` in `src/tracertm/`):** 478
- **Test files (`.py` in `tests/` + `src/`):** 517
  - `tests/` : 516 files
  - `src/tracertm/mcp/tools/params/query_test.py` : 1 file
- **Test directories:** ~47 distinct directories under `tests/`

### 3.2 Source Files by Top-Level Area

| Area | Source Files | Largest Files (approx. lines) |
|------|-------------|------------------------------|
| `services` | 110 | `src/tracertm/services/spec_analytics_service.py` (~1,973), `src/tracertm/services/stateless_ingestion_service.py` (~747) |
| `api` | 97 | `src/tracertm/api/routers/item_specs.py` (~2,171), `src/tracertm/api/main.py` (~1,596) |
| `mcp` | 68 | `src/tracertm/mcp/tools/param.py` (~1,475) |
| `models` | 56 | `src/tracertm/models/item_spec.py` (~928) |
| `repositories` | 25 | `src/tracertm/repositories/item_spec_repository.py` (~887) |
| `tui` | 21 | `src/tracertm/tui/widgets/*.py` (11 files) |
| `schemas` | 20 | `src/tracertm/schemas/item_spec.py` (~641) |
| `agent` | 11 | `src/tracertm/agent/agent_service.py` etc. |
| `workflows` | 8 | Various workflow files |
| `storage` | 7 | `src/tracertm/storage/local_storage.py` (~1,112), `src/tracertm/storage/sync_engine.py` (~723) |
| `config` | 5 | Config files |
| `infrastructure` | 5 | Infra files |
| `database` | 4 | DB files |
| `core` | 4 | Core files |
| `clients` | 4 | `src/tracertm/clients/linear_client.py` (~593), `src/tracertm/clients/github_client.py` (~578) |
| `observability` | 4 | Observability files |
| `ports` | 3 | Port interfaces |
| `grpc` | 3 | gRPC files |
| `adapters` | 2 | `src/tracertm/adapters/agileplus_adapter.py` etc. |
| `validation` | 2 | Validation files |
| `vault` | 2 | Vault files |
| `utils` | 2 | Utility files |

### 3.3 Test Files by Top-Level Category

| Category | Test Files | Largest Test Files |
|----------|-----------|-------------------|
| `unit/` | 217 | `tests/unit/repositories/test_item_spec_repository.py` (~120,404 bytes, ~2,400 lines), `tests/unit/repositories/test_specification_repository.py` (~113,157 bytes) |
| `integration/` | 149 | `tests/integration/repositories/test_repositories_core_full_coverage.py` (~144,085 bytes, ~4,032 lines), `tests/integration/api/test_api_layer_full_coverage.py` (~125,173 bytes, ~3,334 lines) |
| `component/` | 48 | `tests/component/storage/test_storage_comprehensive.py` (~57,172 bytes, ~1,589 lines) |
| `performance/` | 18 | Performance benchmarks |
| `e2e/` | 11 | End-to-end tests |
| `chaos/` | 11 | Chaos tests |
| `_disabled_tests/` | 11 | Disabled/legacy tests |
| `mcp/` | 9 | MCP tests |
| `phase_five/` | 6 | Phase-5 CLI tests |
| `property/` | 5 | Property-based tests |
| `factories/` | 4 | Test factories |
| `load/` | 4 | Load tests |
| `api/` | 3 | API tests |
| `grpc/` | 2 | gRPC tests |
| `workflows/` | 2 | Workflow tests |
| `fixtures/` | 1 | Test fixtures |
| `manual/` | 1 | Manual tests |

### 3.4 Mapping: Source Areas vs. Test Coverage

The Python tests are organized by *test type* (unit, integration, component) rather than mirroring source directory names. Mapping tests to source areas by filename analysis:

| Source Area | Source Files | Test Files (approx.) | Coverage Level |
|-------------|-------------|---------------------|----------------|
| `services` | 110 | ~69 | Moderate; many large monolithic tests |
| `api` | 97 | ~42 | Moderate |
| `repositories` | 25 | ~45 | **Strong** |
| `mcp` | 68 | ~22 | **Moderate gap** |
| `models` | 56 | ~6 | **Large gap** |
| `tui` | 21 | ~33 | **Strong** |
| `storage` | 7 | ~39 | **Strong** |
| `schemas` | 20 | ~2 | **Large gap** |
| `agent` | 11 | ~4 | **Gap** |
| `workflows` | 8 | ~5 | Moderate |
| `config` | 5 | ~5 | Good |
| `core` | 4 | ~6 | Good |
| `ports` | 3 | ~3 | Good |
| `database` | 4 | ~2 | **Gap** |
| `clients` | 4 | ~2 | **Gap** |
| `infrastructure` | 5 | ~0 | **Zero** |
| `observability` | 4 | ~0 | **Zero** |
| `adapters` | 2 | ~0 | **Zero** |
| `vault` | 2 | ~0 | **Zero** |
| `validation` | 2 | ~4 | Good (but tests may be in `tests/unit/validation`) |

### 3.5 Biggest Untested Python Modules

| Module/Package | Source Files | Key Untested Files |
|----------------|-------------|-------------------|
| `src/tracertm/infrastructure` | 5 | `src/tracertm/infrastructure/*.py` (5 files) |
| `src/tracertm/observability` | 4 | `src/tracertm/observability/*.py` (4 files) |
| `src/tracertm/models` | 56 | `src/tracertm/models/item_spec.py:1`, `src/tracertm/models/*.py` (56 files) |
| `src/tracertm/mcp` | 68 | `src/tracertm/mcp/tools/param.py:1`, `src/tracertm/mcp/tools/*.py` (20 files) |
| `src/tracertm/schemas` | 20 | `src/tracertm/schemas/item_spec.py:1`, `src/tracertm/schemas/*.py` (20 files) |
| `src/tracertm/agent` | 11 | `src/tracertm/agent/agent_service.py:1`, `src/tracertm/agent/*.py` (11 files) |
| `src/tracertm/adapters` | 2 | `src/tracertm/adapters/agileplus_adapter.py:1` |
| `src/tracertm/vault` | 2 | `src/tracertm/vault/*.py` (2 files) |
| `src/tracertm/clients` | 4 | `src/tracertm/clients/linear_client.py:1`, `src/tracertm/clients/github_client.py:1` |
| `src/tracertm/database` | 4 | `src/tracertm/database/*.py` (4 files) |

> **Note:** Many large Python test files (e.g., `test_repositories_core_full_coverage.py` at 144KB, 4,032 lines) are monolithic comprehensive suites. While they provide broad coverage, they make debugging flaky tests difficult and do not isolate individual units.

---

## 4. TypeScript Frontend (`frontend/`)

### 4.1 Overall Counts
- **Source files (`.ts` / `.tsx`, excl. test files, excl. `node_modules`):** 1,066
- **Test files (`.test.*` / `.spec.*`, excl. `node_modules`):** 343
- **Unique source directories:** 144
- **Unique test directories:** 56

### 4.2 Test Files by Top-Level Area

| Area | Test Files | Notes |
|------|-----------|-------|
| `apps/web/e2e` | 53 | Playwright/Cypress E2E specs |
| `apps/web/src/__tests__/api` | 30 | API endpoint tests |
| `apps/web/src/__tests__/hooks` | 28 | Hook tests |
| `packages/ui/src/__tests__` | 24 | UI component tests |
| `apps/web/src/__tests__/components` | 23 | Component tests |
| `apps/web/src/__tests__/components/graph` | 16 | Graph component tests |
| `apps/web/src/__tests__/lib` | 16 | Library tests |
| `apps/web/src/__tests__/views` | 12 | View tests |
| `apps/web/src/__tests__/routes` | 12 | Route tests |
| `apps/web/src/__tests__/stores` | 8 | Store tests |
| `apps/web/src/__tests__/integration` | 8 | Integration tests |
| `apps/web/src/__tests__/security` | 6 | Security tests |
| `apps/web/src/__tests__/a11y` | 6 | Accessibility tests |
| `apps/web/src/__tests__/utils` | 6 | Utility tests |
| `apps/web/src/__tests__/performance` | 6 | Performance tests |
| `apps/web/src/__tests__/workers` | 5 | Worker tests |
| `apps/docs/components/__tests__` | 6 | Docs component tests |
| `apps/docs/app/__tests__` | 5 | Docs app tests |
| `apps/web/src/__tests__/pages` | 4 | Page tests |

### 4.3 Source Files by Major Area (with Test Coverage)

| Area | Source Files | Test Files | Test:Src Ratio |
|------|-------------|------------|----------------|
| `apps/web/src/components` | 319 | 7 | **0.02** |
| `apps/web/src/hooks` | 159 | 3 | **0.02** |
| `apps/web/src/views` | 130 | 1 | **0.01** |
| `apps/web/src/lib` | 72 | 8 | **0.11** |
| `apps/web/src/routes` | 60 | 1 | **0.02** |
| `apps/web/src/api` | 57 | 0 | **0.00** |
| `apps/web/src/pages` | 45 | 0 | **0.00** |
| `apps/web/src/stores` | 17 | 0 | **0.00** |
| `packages/ui/src/components` | 23 | 0 | **0.00** |
| `packages/types/src` | 9 | 0 | **0.00** |
| `apps/docs/components` | 6 | 6 | **1.00** |

### 4.4 Biggest Untested TS Sub-Areas

| Sub-Area | Source Files | Test Files | Key Untested Files |
|----------|-------------|------------|-------------------|
| `apps/web/src/components/graph` | 158 | 3 | `frontend/apps/web/src/components/graph/UnifiedGraphView.tsx:1` (~33KB), `frontend/apps/web/src/components/graph/JourneyExplorer.tsx:1` (~27KB), `frontend/apps/web/src/components/graph/EnhancedGraphView.tsx:1` (~27KB), `frontend/apps/web/src/components/graph/EquivalenceImport.tsx:1` (~26KB), `frontend/apps/web/src/components/graph/PageDecompositionView.tsx:1` (~25KB) |
| `apps/web/src/pages/projects/views` | 42 | 0 | All page views untested |
| `apps/web/src/views/item-detail/components` | 30 | 0 | `frontend/apps/web/src/views/details/RequirementDetailView.tsx:1` (~37KB), `frontend/apps/web/src/views/details/TestDetailView.tsx:1` (~36KB) |
| `apps/web/src/components/forms` | 27 | 1 | `frontend/apps/web/src/components/forms/CreateRequirementItemForm.tsx:1` (~25KB) |
| `apps/web/src/components/ui` | 24 | 0 | All UI components untested |
| `apps/web/src/hooks/item-specs` | 22 | 0 | All item-spec hooks untested |
| `apps/web/src/hooks/use-specifications/api` | 17 | 0 | All spec API hooks untested |
| `apps/web/src/views/items-table` | 15 | 0 | `frontend/apps/web/src/views/ItemsTableViewA11y.tsx:1` (~32KB) |
| `apps/web/src/views/projects-list` | 14 | 0 | Project list views untested |
| `apps/web/src/components/graph/layouts/dag-layout` | 13 | 0 | DAG layout engine untested |
| `apps/web/src/components/layout` | 13 | 0 | `frontend/apps/web/src/components/layout/sidebar-view.tsx:1` (~36KB) |
| `apps/web/src/components/temporal` | 13 | 3 | `frontend/apps/web/src/components/temporal/ProgressDashboard.tsx:1` (~35KB) |
| `apps/web/src/components/specifications/items` | 10 | 0 | Spec item components untested |
| `apps/web/src/components/specifications/contracts` | 9 | 0 | Spec contract components untested |
| `apps/web/src/components/graph/advanced-graph-view` | 7 | 0 | Advanced graph view untested |
| `apps/web/src/workers` | 6 | 0 | `frontend/apps/web/src/workers/graphLayout.worker.ts:1` (~25KB) |
| `apps/web/src/components/chat` | 6 | 0 | Chat components untested |
| `apps/web/src/components/specifications/analytics` | 6 | 0 | Analytics components untested |
| `apps/web/src/components/specifications/bdd` | 6 | 0 | BDD components untested |
| `apps/web/src/components/specifications/adr` | 6 | 0 | ADR components untested |
| `apps/web/src/api` | 57 | 0 | `frontend/apps/web/src/api/schema.ts:1` (~112KB, generated), all API client code untested |
| `apps/web/src/stores` | 17 | 0 | All Zustand stores untested |
| `apps/web/src/routes` | 60 | 1 | `frontend/apps/web/src/routeTree.gen.ts:1` (~64KB, generated), most route files untested |
| `packages/ui/src/components` | 23 | 0 | All shared UI package components untested |
| `packages/types/src` | 9 | 0 | All shared types untested |

---

## 5. Cross-Cutting Concerns

### 5.1 Generated Code
- **Go:** `backend/pkg/proto/tracertm/v1/tracertm.pb.go` (~94KB) and `tracertm_grpc.pb.go` (~31KB) are generated protobuf files; they are not tested directly.
- **TS:** `frontend/apps/web/src/api/schema.ts` (~112KB) and `frontend/apps/web/src/routeTree.gen.ts` (~64KB) are generated files; they are not tested directly.
- **Python:** `src/tracertm/proto/tracertm/v1/` contains generated protobuf files (3 files). These are not tested directly.

### 5.2 Monolithic Test Files
Several test files are very large (>50KB, >1,500 lines), which may indicate low-quality test design:

| File | Size | Approx. Lines |
|------|------|--------------|
| `tests/integration/repositories/test_repositories_core_full_coverage.py` | 144KB | 4,032 |
| `tests/integration/api/test_api_layer_full_coverage.py` | 125KB | 3,334 |
| `tests/unit/repositories/test_item_spec_repository.py` | 120KB | ~2,400 |
| `tests/unit/repositories/test_specification_repository.py` | 113KB | ~2,200 |
| `tests/integration/services/test_services_gap_coverage.py` | 89KB | ~1,800 |
| `tests/integration/tui/test_tui_execution_coverage.py` | 88KB | ~1,700 |
| `tests/phase_five/test_cli_link_comprehensive.py` | 78KB | ~1,500 |
| `tests/integration/tui/test_tui_integration.py` | 77KB | ~1,500 |
| `tests/integration/services/test_services_medium_full_coverage.py` | 76KB | ~1,500 |
| `tests/integration/storage/test_storage_medium_full_coverage.py` | 76KB | ~1,500 |

### 5.3 `_disabled_tests` Directory
There are 11 test files under `tests/_disabled_tests/` that have been disabled. This is a red flag for stale or broken tests.

---

## 6. Recommendations (Ordered by Impact)

1. **TypeScript `components/graph/`** is the single largest untested area (158 source files, 3 tests). Prioritize testing graph rendering, navigation, and layout engines.
2. **TypeScript `api/` and `stores/`** are completely untested (57 + 17 files). These are core to frontend stability; add unit tests for API client and store logic.
3. **Python `models/` and `schemas/`** (56 + 20 files) have very few dedicated tests. Add focused unit tests for model validation and schema serialization.
4. **Go `internal/codeindex/parsers/`** (10 files, 0 tests) is the largest untested Go package. Add parser unit tests.
5. **Python `infrastructure/` and `observability/`** (5 + 4 files, 0 tests) are zero-test modules. Add smoke tests.
6. **Refactor monolithic Python tests** (e.g., `test_repositories_core_full_coverage.py` at 4,032 lines) into smaller, focused test modules.
7. **Review `tests/_disabled_tests/`** (11 files) and either fix or delete them.
8. **Go `internal/journey/`** (9 source files, 1 test) has a large gap; expand journey handler tests.
9. **TypeScript `hooks/`** (159 source files, 3 tests) is severely under-tested; add hook unit tests.
10. **TypeScript `views/`** (130 source files, 1 test) is almost untested; add view-level integration tests.

---

*End of audit.*
