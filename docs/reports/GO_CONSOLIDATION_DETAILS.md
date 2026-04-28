# Go Test Consolidation - Detailed File Mapping

**Generated:** 2026-02-06
**Scope:** Specific file-by-file consolidation targets
**Estimated Savings:** 511 tests (13% reduction)
**Output Location:** docs/reports/GO_PYRAMID_REBALANCE_PLAN.md

---

## Package: internal/search (394 tests → 270 tests, -124 tests)

### Current Structure

```
internal/search/
├── search_test.go                         [37 tests] ← KEEP AS BASE
├── search_comprehensive_test.go            [69 tests] ← MERGE INTO search_test.go
├── search_comprehensive_advanced_test.go   [62 tests] ← KEEP (reduce to 25)
├── search_extended_test.go                 [38 tests] ← MERGE INTO search_test.go
├── search_additional_test.go               [32 tests] ← MOVE EDGE CASES
├── search_edge_cases_test.go               [52 tests] ← CONSOLIDATE
├── search_engine_unit_test.go              [36 tests] ← MERGE INTO search_test.go
├── unit_tests_test.go                      [29 tests] ← DELETE (duplicate)
├── query_builder_test.go                   [14 tests] ← KEEP (focused)
├── indexer_test.go                         [13 tests] ← KEEP (focused)
├── cross_perspective_search_test.go        [8 tests]  ← KEEP (feature-specific)
├── search_integration_test.go              [4 tests]  ← ELEVATE TO E2E
└── search_engine_unit_test.go (stats)      [remaining]
```

### Consolidation Actions

| File | Action | Tests | Target | Savings | Rationale |
|------|--------|-------|--------|---------|-----------|
| search_test.go | Keep + merge | 37 + 69 + 38 + 36 = 180 | 140 | 40 | Base file consolidation |
| search_comprehensive_test.go | DELETE & MERGE | 69 | — | 69 | Pure overlap with search_test |
| search_comprehensive_advanced_test.go | REDUCE & KEEP | 62 → 25 | 25 | 37 | Keep advanced scenarios only |
| search_extended_test.go | DELETE & MERGE | 38 | — | 38 | Extended = comprehensive overlap |
| search_additional_test.go | EXTRACT + DELETE | 32 → 15 (move) | — | 17 | Move edge cases to search_edge_cases_test |
| search_edge_cases_test.go | CONSOLIDATE | 52 + 15 = 67 → 60 | 60 | 7 | Add from search_additional, remove dups |
| search_engine_unit_test.go | DELETE & MERGE | 36 | — | 36 | Overlaps with search_test |
| unit_tests_test.go | DELETE | 29 | — | 29 | Pure duplicate of search_test.go |
| query_builder_test.go | KEEP | 14 | 14 | 0 | Focused module test |
| indexer_test.go | KEEP | 13 | 13 | 0 | Focused module test |
| cross_perspective_search_test.go | KEEP | 8 | 8 | 0 | Feature-specific, important |
| search_integration_test.go | ELEVATE | 4 → 0 (move to E2E) | — | 4 | Move to integration tests |

**Result:** 394 tests → 260 tests (134 removed, 34% reduction)

### Merge Strategy: search_test.go

```go
// Existing tests in search_test.go (37 tests)
// FROM search_comprehensive_test.go:
//   - TestSearchWithMultipleFilters (already in search_test)
//   - TestSearchWithBoost (already in search_test)
//   - TestComplexSearchScenarios (NEW - add most important 5)

// FROM search_extended_test.go:
//   - TestSearchPagination (already in search_test)
//   - TestSearchWithSortOptions (already in search_test)
//   - TestCachingBehavior (NEW - add 3 cache tests)

// FROM search_engine_unit_test.go:
//   - TestIndexing (already covered)
//   - TestTokenization (NEW - add 2 tests)
//   - TestRankingAlgorithm (NEW - add 3 tests)

// Target: 37 + 15 + 8 + 8 = 68 tests → reduce to 50 core tests
// Remove: Generic "comprehensive" duplicates, focus on core search logic
```

### Edge Cases Consolidation: search_edge_cases_test.go

```go
// FROM search_edge_cases_test.go (52 tests)
// FROM search_additional_test.go edge cases (15 tests):
//   - TestSearchWithSpecialCharacters
//   - TestSearchWithUnicodeInput
//   - TestSearchWithVeryLongQuery
//   - TestSearchWithEmptyResults
//   - TestSearchWithNull values

// Remove: Duplicate edge cases already in search_test.go
// Target: 52 + 15 - 7 = 60 tests
```

### Advanced Tests: search_comprehensive_advanced_test.go

```go
// Keep: Advanced scenarios NOT in basic tests
// Remove: 37 duplicate tests that overlap with search_test.go
// Target: 62 → 25 tests
// Keep:
//   - Complex multi-index queries (8)
//   - Performance optimization tests (5)
//   - Concurrency scenarios (5)
//   - Custom analyzer tests (7)
```

---

## Package: internal/services (427 tests → 329 tests, -98 tests)

### Current Structure (Partial - Top Services)

```
internal/services/
├── item_service_test.go                   [31 tests] ← KEEP (reduce to 20)
├── item_integration_test.go               [9 tests]  ← ELEVATE
├── item_service_transaction_test.go       [1 test]   ← MERGE
├── project_service_test.go                [27 tests] ← KEEP (reduce to 20)
├── project_service_transaction_test.go    [1 test]   ← MERGE
├── link_service_test.go                   [20 tests] ← KEEP
├── link_service_transaction_test.go       [2 tests]  ← MERGE
├── services_comprehensive_test.go         [18 tests] ← MERGE INTO respective services
├── services_extended_coverage_test.go     [4 tests]  ← MERGE
├── services_additional_coverage_test.go   [5 tests]  ← MERGE
├── cache_service_test.go                  [20 tests] ← KEEP (reduce to 15)
├── storage_service_test.go                [36 tests] ← KEEP (reduce to 26)
├── storage_integration_test.go            [20 tests] ← ELEVATE
├── edge_cases_integration_test.go         [28 tests] ← ELEVATE (14 integration)
└── ... 40+ other service test files
```

### Consolidation Actions

| Service | Main File | Current | Transaction | Comprehensive | Additional | Edge Cases | Target | Savings |
|---------|-----------|---------|-------------|---------------|-----------|----------|--------|---------|
| item | item_service_test.go | 31 | 1 | 5 | 2 | 8 | 20 | 19 |
| project | project_service_test.go | 27 | 1 | 5 | 1 | 5 | 20 | 14 |
| link | link_service_test.go | 20 | 2 | 3 | 1 | 4 | 15 | 12 |
| cache | cache_service_test.go | 20 | 0 | 2 | 0 | 3 | 15 | 10 |
| storage | storage_service_test.go | 36 | 0 | 3 | 1 | 5 | 26 | 15 |
| graph_analysis | graph_analysis_service_test.go | 10 | 0 | 2 | 0 | 2 | 8 | 4 |
| temporal | temporal_service_test.go | 33 | 0 | 3 | 1 | 3 | 28 | 10 |
| docindex (code) | codeindex_service_test.go | 6 | 0 | 1 | 0 | 1 | 5 | 2 |
| Other 30+ services | various | 192 | 5 | 30 | 15 | 35 | 150 | 27 |

**Result:** 427 tests → 287 tests (140 removed, 33% reduction)

### Merge Strategy: Service Pattern

For each service, consolidate pattern:

```go
// service_test.go structure:
// 1. Service creation & initialization (2-3 tests)
// 2. Core operations: Get, Create, Update, Delete (6-8 tests)
// 3. Error handling & validation (2-3 tests)
// 4. Edge cases (2-3 tests)
// 5. Transaction handling (1-2 tests)

// Remove from separate files:
// - *_transaction_test.go (move 1-2 core transaction tests here)
// - *_comprehensive_test.go (remove 5-8 duplicate tests)
// - *_additional_coverage_test.go (move 1-2 important tests here)
// - *_edge_cases_test.go (remove 3-5 duplicate edge cases)

// Keep separate if:
// - Integration tests (mark for elevation)
// - Performance benchmarks (separate benchmark files)
// - Specialized behavior (rare, keep focused test file)
```

---

## Package: internal/agents (421 tests → 280 tests, -141 tests)

### Current Structure

```
internal/agents/
├── coordinator_test.go                          [25 tests] ← KEEP (reduce to 20)
├── coordinator_comprehensive_test.go            [33 tests] ← DELETE & MERGE
├── coordinator_integration_test.go              [15 tests] ← ELEVATE
├── agents_comprehensive_unit_test.go            [58 tests] ← DELETE & MERGE
├── agents_full_coverage_test.go                 [55 tests] ← DELETE & MERGE
├── protocol_unit_test.go                        [25 tests] ← KEEP
├── coordination_distributed_unit_test.go        [32 tests] ← KEEP
├── coordination_comprehensive_unit_test.go      [53 tests] ← DELETE & MERGE
├── agents_edge_cases_unit_test.go               [47 tests] ← CONSOLIDATE
├── agent_service_test.go                        [1 test]   ← KEEP
├── integration_test.go                          [15 tests] ← ELEVATE
├── integration_workflows_test.go                [14 tests] ← ELEVATE
└── ... other test files
```

### Consolidation Actions

| File | Action | Tests | Target | Savings | Reason |
|------|--------|-------|--------|---------|--------|
| coordinator_test.go | KEEP + MERGE | 25 + 30 + 20 | 50 | 25 | Base file, but remove dups |
| coordinator_comprehensive_test.go | DELETE & MERGE | 33 | — | 33 | Pure comprehensive overlap |
| coordinator_integration_test.go | ELEVATE | 15 | — | 15 | Move to E2E (critical path) |
| agents_comprehensive_unit_test.go | DELETE & MERGE | 58 | — | 30 | High overlap (50%) |
| agents_full_coverage_test.go | DELETE & MERGE | 55 | — | 30 | Naming suggests it's comprehensive |
| protocol_unit_test.go | KEEP | 25 | 25 | 0 | Focused protocol tests |
| coordination_distributed_unit_test.go | KEEP | 32 | 32 | 0 | Specialized distributed tests |
| coordination_comprehensive_unit_test.go | DELETE & MERGE | 53 | — | 28 | Comprehensive overlap |
| agents_edge_cases_unit_test.go | CONSOLIDATE | 47 → 35 | 35 | 12 | Remove dups, keep important |
| integration_test.go | ELEVATE | 15 | — | 15 | Critical E2E candidate |
| integration_workflows_test.go | ELEVATE | 14 | — | 14 | Workflow tests (E2E) |
| Other 10+ files | AUDIT | 50 | 40 | 10 | General cleanup (20%) |

**Result:** 421 tests → 280 tests (141 removed, 33% reduction)

### Consolidation Pattern: Agents

```go
// coordinator_test.go (target: 50 tests)
// 1. Initialization & lifecycle (3)
// 2. Core coordination operations (8-10)
//    - Scheduling
//    - Work distribution
//    - Result collection
// 3. Error handling (3-5)
// 4. Concurrency (3-5)
// 5. State management (2-3)

// protocol_unit_test.go (KEEP: 25 tests)
// - Protocol-specific behavior

// coordination_distributed_unit_test.go (KEEP: 32 tests)
// - Distributed-specific behavior

// agents_edge_cases_unit_test.go (target: 35 tests)
// - Remove: Tests already in coordinator_test.go
// - Keep: True edge cases not covered elsewhere
```

---

## Package: internal/handlers (304 tests → 220 tests, -84 tests)

### Current Structure

```
internal/handlers/
├── handlers_test.go                         [14 tests] ← KEEP (reduce to 12)
├── handlers_comprehensive_test.go           [38 tests] ← DELETE & MERGE
├── handlers_coverage_expansion_test.go      [11 tests] ← DELETE & MERGE
├── handlers_additional_coverage_test.go     [3 tests]  ← DELETE & MERGE
├── handlers_integration_test.go             [25 tests] ← ELEVATE
├── item_handler_test.go                     [35 tests] ← KEEP (reduce to 30)
├── item_handler_coverage_test.go            [5 tests]  ← MERGE
├── graph_handler_test.go                    [7 tests]  ← KEEP
├── graph_handler_refactor_test.go           [7 tests]  ← MERGE
├── link_handler_test.go                     [19 tests] ← KEEP (reduce to 15)
├── project_handler_test.go                  [17 tests] ← KEEP (reduce to 15)
├── auth_handler_test.go                     [10 tests] ← KEEP
├── agent_handler_test.go                    [19 tests] ← KEEP (reduce to 15)
├── agent_handler_extended_test.go           [9 tests]  ← MERGE
├── agent_coordination_handlers_test.go      [7 tests]  ← MERGE
└── ... other handler test files
```

### Consolidation Actions

| File | Action | Tests | Target | Savings | Reason |
|------|--------|-------|--------|---------|--------|
| handlers_test.go | KEEP + MERGE | 14 + 20 = 34 | 12 | 22 | Remove comprehensive dups |
| handlers_comprehensive_test.go | DELETE & MERGE | 38 | — | 38 | Pure comprehensive overlap |
| handlers_coverage_expansion_test.go | DELETE & MERGE | 11 | — | 11 | Coverage expansion = dups |
| handlers_additional_coverage_test.go | DELETE & MERGE | 3 | — | 3 | Merge into handlers_test |
| handlers_integration_test.go | ELEVATE | 25 | — | 25 | Move to E2E candidates |
| item_handler_test.go | KEEP + MERGE | 35 + 5 = 40 → 30 | 30 | 10 | Keep core, merge coverage_test |
| graph_handler_test.go | KEEP + MERGE | 7 + 7 = 14 → 7 | 7 | 7 | Merge refactor_test |
| link_handler_test.go | KEEP (reduce) | 19 → 15 | 15 | 4 | Remove duplicate scenarios |
| project_handler_test.go | KEEP (reduce) | 17 → 15 | 15 | 2 | Remove edge cases (move to integration) |
| auth_handler_test.go | KEEP | 10 | 10 | 0 | Focused auth tests |
| agent_handler_test.go | KEEP + MERGE | 19 + 9 + 7 = 35 → 15 | 15 | 20 | Heavy consolidation (60%) |
| Other 20+ handlers | AUDIT | 130 | 110 | 20 | General cleanup (15%) |

**Result:** 304 tests → 220 tests (84 removed, 28% reduction)

---

## Package: internal/graph (183 tests → 147 tests, -36 tests)

### Consolidation Targets

| File | Type | Action | Tests | Target | Savings |
|------|------|--------|-------|--------|---------|
| graph_test.go | Main | KEEP | 1 | 1 | 0 |
| graph_core_test.go | Core | KEEP | 19 | 19 | 0 |
| graph_algorithms_test.go | Focused | KEEP | 13 | 13 | 0 |
| graph_integration_test.go | Integration | ELEVATE | 2 | — | 2 |
| graph_comprehensive_test.go | Comprehensive | CONSOLIDATE | 34 → 24 | 24 | 10 |
| neo4j_client_test.go | Focused | KEEP | 14 | 14 | 0 |
| neo4j_queries_test.go | Focused | KEEP | 23 | 23 | 0 |
| neo4j_integration_test.go | Integration | ELEVATE | 10 | — | 10 |
| neo4j_advanced_queries_test.go | Advanced | CONSOLIDATE | 18 → 12 | 12 | 6 |
| cache_test.go | Focused | KEEP | 14 | 14 | 0 |
| project_context_middleware_test.go | Focused | KEEP | 18 | 18 | 0 |
| Other 5+ files | Various | AUDIT | 10 | 8 | 2 |

**Result:** 183 tests → 147 tests (36 removed, 20% reduction)

---

## Summary by Package

| Package | Current | Consolidation | Elevation | Target | Savings |
|---------|---------|----------------|-----------|--------|---------|
| internal/search | 394 | 260 | 4 | 260 | 134 |
| internal/services | 427 | 287 | 47 | 287 | 140 |
| internal/agents | 421 | 280 | 44 | 280 | 141 |
| internal/handlers | 304 | 220 | 25 | 220 | 84 |
| internal/graph | 183 | 147 | 10 | 147 | 36 |
| internal/equivalence | 183 | 155 | 0 | 155 | 28 |
| internal/cache | 75 | 68 | 0 | 68 | 7 |
| internal/middleware | 71 | 64 | 0 | 64 | 7 |
| internal/repository | 72 | 60 | 0 | 60 | 12 |
| Other 30+ packages | 784 | 690 | 30 | 690 | 94 |
| **TOTAL** | **3,914** | **2,831** | **160** | **2,831** | **683** |

**Key Insights:**
- Top 5 packages account for 79% of all tests
- Consolidation removes 683 redundant unit tests
- Elevation moves 160 tests to integration/E2E level
- **Result:** 3,914 → 2,831 core unit tests (-28%), +160 integration/E2E tests

---

## E2E Tests to Create (10 critical journeys)

### Journey 1: Create Project → Add Items → Build Graph

```go
// tests/e2e/project_graph_creation_test.go
// 1. POST /projects (create project)
// 2. POST /items (create 3 items)
// 3. POST /links (create 2 edges)
// 4. GET /graph (verify graph structure)
// 5. Verify WebSocket events broadcast to other clients
// Estimated tests: 1 (with subtests)
```

### Journey 2: OAuth Login → Create Project

```go
// tests/e2e/auth_oauth_journey_test.go
// 1. GET /auth/oauth/init
// 2. POST /auth/oauth/callback
// 3. Verify session created
// 4. GET /projects (verify authenticated)
// 5. POST /projects (create first project)
// Estimated tests: 1
```

### Journey 3: Search → Filter → Update

```go
// tests/e2e/search_update_workflow_test.go
// 1. Bulk create 100 items
// 2. POST /search (full-text query)
// 3. GET /items?filter=... (refined filters)
// 4. PATCH /items/{id} (update selected items)
// 5. Verify search index updated
// Estimated tests: 1
```

### Journey 4: Graph Analysis

```go
// tests/e2e/graph_analysis_flow_test.go
// 1. Create graph with 10 nodes, 15 edges
// 2. GET /graph/analyze/dependencies
// 3. GET /graph/analyze/impact
// 4. Verify algorithm results correctness
// Estimated tests: 1
```

### Journey 5: Temporal Workflow Execution

```go
// tests/e2e/temporal_workflow_test.go
// 1. Create workflow execution request
// 2. Verify Temporal worker picks up task
// 3. Wait for workflow completion
// 4. Verify results persisted in DB
// Estimated tests: 1
```

### Journey 6: Real-time Sync (WebSocket)

```go
// tests/e2e/realtime_sync_test.go
// 1. Connect WebSocket client 1
// 2. Create item via API (client 2)
// 3. Verify WebSocket event received (client 1)
// 4. Verify event order preserved
// Estimated tests: 1
```

### Journey 7: Error Recovery

```go
// tests/e2e/error_recovery_test.go
// 1. Start operation
// 2. Simulate network failure (kill connection)
// 3. Verify retry logic triggered
// 4. Verify eventual consistency
// Estimated tests: 1
```

### Journey 8: Performance (Bulk Operations)

```go
// tests/e2e/performance_bulk_test.go
// 1. Bulk import 1M items (CSV)
// 2. Verify search index built
// 3. Run complex query
// 4. Verify execution time < 1s
// Estimated tests: 1 (with benchmarking)
```

### Journey 9: Security (CSRF + XSS + Rate Limit)

```go
// tests/e2e/security_posture_test.go
// 1. Verify CSRF token required
// 2. Verify XSS payload blocked
// 3. Verify rate limit enforced (100 req/min)
// 4. Verify auth headers required
// Estimated tests: 1 (with subtests)
```

### Journey 10: Accessibility (Keyboard + Screen Reader)

```go
// tests/e2e/accessibility_keyboard_test.go (Playwright)
// 1. Tab through UI elements
// 2. Verify focus visible
// 3. Verify enter key triggers action
// 4. Verify screen reader text present
// Estimated tests: 1 (with Playwright)
```

**Total E2E Tests to Create:** 10 (1 per journey, plus subtests)

---

## Implementation Checklist

### Phase 1: Audit & Plan (30 min)
- [ ] Review search package (12 files)
- [ ] Review services package (40+ files)
- [ ] Review agents package (15 files)
- [ ] Review handlers package (20+ files)
- [ ] Create merge plan document
- [ ] Estimate merge time per package

### Phase 2: Execute Consolidations (120 min)
- [ ] Merge search package tests (30 min)
- [ ] Merge services package tests (40 min)
- [ ] Merge agents package tests (30 min)
- [ ] Merge handlers package tests (20 min)

### Phase 3: Create E2E Tests (60 min)
- [ ] Create 10 E2E journey tests (40 min)
- [ ] Integrate with CI/CD (15 min)
- [ ] Document best practices (5 min)

### Phase 4: Verify & Measure (45 min)
- [ ] Run full test suite (15 min)
- [ ] Generate coverage report (10 min)
- [ ] Benchmark execution time (10 min)
- [ ] Team review & sign-off (10 min)

**Total Time:** 255 min (4.25 hours wall-clock)

---

**Status:** Ready for Implementation
**Last Updated:** 2026-02-06
