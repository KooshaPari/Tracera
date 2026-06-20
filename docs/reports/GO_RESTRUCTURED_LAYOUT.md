# Go Test Restructured Layout

**Generated:** 2026-02-06
**Status:** Post-Consolidation Blueprint
**Purpose:** Visual reference for expected test file structure after consolidation

---

## internal/search (12 files → 7 files)

### BEFORE (394 tests, 12 files)
```
internal/search/
├── search_test.go                         37 tests
├── search_comprehensive_test.go            69 tests ← CONSOLIDATE
├── search_comprehensive_advanced_test.go   62 tests ← REDUCE
├── search_extended_test.go                 38 tests ← CONSOLIDATE
├── search_additional_test.go               32 tests ← CONSOLIDATE
├── search_edge_cases_test.go               52 tests ← CONSOLIDATE
├── search_engine_unit_test.go              36 tests ← CONSOLIDATE
├── unit_tests_test.go                      29 tests ← DELETE
├── query_builder_test.go                   14 tests ← KEEP
├── indexer_test.go                         13 tests ← KEEP
├── cross_perspective_search_test.go         8 tests ← KEEP
└── search_integration_test.go               4 tests ← ELEVATE
```

### AFTER (260 tests, 7 files)
```
internal/search/
├── search_test.go                         50 tests
│   └── Merged from: search_comprehensive, search_extended, search_engine_unit
│       [Core search logic: filters, boosting, pagination, tokenization, ranking]
│
├── search_comprehensive_advanced_test.go   25 tests
│   └── Reduced from: 62
│       [Advanced scenarios: multi-index, optimization, concurrency, custom analyzers]
│
├── search_edge_cases_test.go               60 tests
│   └── Consolidated from: search_edge_cases + search_additional edge cases
│       [Edge cases: special chars, unicode, long queries, nulls, empty results]
│
├── query_builder_test.go                   14 tests [KEEP UNCHANGED]
├── indexer_test.go                         13 tests [KEEP UNCHANGED]
├── cross_perspective_search_test.go         8 tests [KEEP UNCHANGED]
│
└── [DELETED]
    - unit_tests_test.go (29 tests) - duplicate
    - search_comprehensive_test.go (merged)
    - search_extended_test.go (merged)
    - search_engine_unit_test.go (merged)
    - search_additional_test.go (edge cases moved, rest merged)

E2E ELEVATED:
search_integration_test.go → tests/e2e/search_update_workflow_test.go
```

---

## internal/services (40+ files → 30 files)

### BEFORE (427 tests, fragmented)
```
internal/services/
├── item_service_test.go                   31 tests
├── item_service_transaction_test.go        1 test  ← CONSOLIDATE
├── item_integration_test.go                9 tests ← ELEVATE
│
├── project_service_test.go                27 tests
├── project_service_transaction_test.go     1 test  ← CONSOLIDATE
├── project_transaction_validation_test.go  2 tests ← CONSOLIDATE
│
├── link_service_test.go                   20 tests
├── link_service_transaction_test.go        2 tests ← CONSOLIDATE
├── linkservice_integration_test.go         9 tests ← ELEVATE
│
├── services_comprehensive_test.go         18 tests ← CONSOLIDATE
├── services_extended_coverage_test.go      4 tests ← CONSOLIDATE
├── services_additional_coverage_test.go    5 tests ← CONSOLIDATE
│
├── cache_service_test.go                  20 tests
├── storage_service_test.go                36 tests
├── storage_integration_test.go            20 tests ← ELEVATE
│
├── agent_service_test.go                   1 test
├── agentservice_integration_test.go       10 tests ← ELEVATE
│
├── graph_analysis_service_test.go         10 tests
├── temporal_service_test.go               33 tests
├── codeindex_service_test.go               6 tests
├── docservice_service_test.go             10 tests
│
├── edge_cases_integration_test.go         28 tests ← ELEVATE (14 I, split)
├── boundary_scenarios_test.go             21 tests
├── cross_service_test.go                  26 tests
├── cross_domain_integration_test.go        9 tests ← ELEVATE
│
├── [... 15+ other service files ...]
```

### AFTER (287 unit + 47 elevated, 30 files)
```
internal/services/
├── item_service_test.go                   20 tests
│   └── Consolidated from: item_service_test.go + item_service_transaction_test.go
│       [Create, Get, Update, Delete, Transactions]
│
├── project_service_test.go                20 tests
│   └── Consolidated from: project_service_test.go + project_*_transaction_test.go
│
├── link_service_test.go                   15 tests
│   └── Consolidated from: link_service_test.go + link_service_transaction_test.go
│
├── cache_service_test.go                  15 tests
│   └── Reduced from: 20 (remove duplicate caching scenarios)
│
├── storage_service_test.go                26 tests
│   └── Reduced from: 36 (remove duplicate S3 scenarios)
│
├── agent_service_test.go                   1 test
├── graph_analysis_service_test.go          8 tests
├── temporal_service_test.go               28 tests
├── codeindex_service_test.go               5 tests
├── docservice_service_test.go             10 tests
│
├── boundary_scenarios_test.go             21 tests
├── cross_service_test.go                  26 tests
│
├── [... 15+ focused service files ...]
│
└── [DELETED/CONSOLIDATED]
    - services_comprehensive_test.go
    - services_extended_coverage_test.go
    - services_additional_coverage_test.go
    - *_transaction_test.go (merged into main service test)

E2E ELEVATED (47 tests → tests/e2e/):
- item_integration_test.go (9)
- linkservice_integration_test.go (9)
- storage_integration_test.go (20)
- agentservice_integration_test.go (10)
- cross_domain_integration_test.go (9)
- edge_cases_integration_test.go (14 specific flows)
```

---

## internal/agents (15+ files → 10 files)

### BEFORE (421 tests)
```
internal/agents/
├── coordinator_test.go                          25 tests
├── coordinator_comprehensive_test.go            33 tests ← CONSOLIDATE
├── coordinator_integration_test.go              15 tests ← ELEVATE
│
├── agents_comprehensive_unit_test.go            58 tests ← CONSOLIDATE (30 dup)
├── agents_full_coverage_test.go                 55 tests ← CONSOLIDATE (30 dup)
├── agents_edge_cases_unit_test.go               47 tests ← CONSOLIDATE (12 dup)
│
├── protocol_unit_test.go                        25 tests ← KEEP
├── coordination_distributed_unit_test.go        32 tests ← KEEP
├── coordination_comprehensive_unit_test.go      53 tests ← CONSOLIDATE (28 dup)
│
├── agent_service_test.py                         1 test
├── integration_test.go                          15 tests ← ELEVATE
├── integration_workflows_test.go                14 tests ← ELEVATE
│
├── [... other specialized agent tests ...]
```

### AFTER (280 unit + 44 elevated, 10 files)
```
internal/agents/
├── coordinator_test.go                          50 tests
│   └── Consolidated from:
│       - coordinator_test.go (25)
│       - coordinator_comprehensive_test.go (20, merged)
│       - agents_comprehensive_unit_test.go (5, most important)
│       [Lifecycle, coordination ops, errors, concurrency, state mgmt]
│
├── protocol_unit_test.go                        25 tests [KEEP UNCHANGED]
├── coordination_distributed_unit_test.go        32 tests [KEEP UNCHANGED]
│
├── agents_edge_cases_unit_test.go               35 tests
│   └── Reduced from: 47 + 30 consolidated
│       [True edge cases only, remove duplicates from comprehensive files]
│
├── agent_service_test.go                         1 test
├── agent_checkpoint_test.go                     10 tests (focus: checkpoints)
├── agent_lock_test.go                            8 tests (focus: distributed locking)
│
├── [... specialized agent test files ...]
│
└── [DELETED/CONSOLIDATED]
    - coordinator_comprehensive_test.go (merged)
    - agents_comprehensive_unit_test.go (merged, 28 kept, 30 removed)
    - agents_full_coverage_test.go (merged, 25 kept, 30 removed)
    - coordination_comprehensive_unit_test.go (merged, 25 kept, 28 removed)

E2E ELEVATED (44 tests → tests/e2e/):
- coordinator_integration_test.go (15)
- integration_test.go (15)
- integration_workflows_test.go (14)
```

---

## internal/handlers (20+ files → 15 files)

### BEFORE (304 tests)
```
internal/handlers/
├── handlers_test.go                         14 tests
├── handlers_comprehensive_test.go           38 tests ← CONSOLIDATE
├── handlers_coverage_expansion_test.go      11 tests ← CONSOLIDATE
├── handlers_additional_coverage_test.go      3 tests ← CONSOLIDATE
├── handlers_integration_test.go             25 tests ← ELEVATE
│
├── item_handler_test.go                     35 tests
├── item_handler_coverage_test.go             5 tests ← CONSOLIDATE
│
├── graph_handler_test.go                     7 tests
├── graph_handler_refactor_test.go            7 tests ← CONSOLIDATE
│
├── link_handler_test.go                     19 tests
├── project_handler_test.go                  17 tests
├── auth_handler_test.go                     10 tests
├── agent_handler_test.go                    19 tests
├── agent_handler_extended_test.go            9 tests ← CONSOLIDATE
├── agent_coordination_handlers_test.go       7 tests ← CONSOLIDATE
│
├── [... other handler files ...]
```

### AFTER (220 unit + 25 elevated, 15 files)
```
internal/handlers/
├── handlers_test.go                         12 tests
│   └── Consolidated from:
│       - handlers_test.go (14)
│       - handlers_comprehensive_test.go (20, merged)
│       - handlers_coverage_expansion_test.go (11, merged)
│       - handlers_additional_coverage_test.go (3, merged)
│       [Core handler initialization, middleware, error handling]
│
├── item_handler_test.go                     30 tests
│   └── Consolidated from: item_handler_test.go + item_handler_coverage_test.go
│
├── graph_handler_test.go                     7 tests
│   └── Consolidated from: graph_handler_test.go + graph_handler_refactor_test.go
│
├── link_handler_test.go                     15 tests
├── project_handler_test.go                  15 tests
├── auth_handler_test.go                     10 tests
│
├── agent_handler_test.go                    15 tests
│   └── Consolidated from:
│       - agent_handler_test.go (19)
│       - agent_handler_extended_test.go (9, merge 5)
│       - agent_coordination_handlers_test.go (7, merge 1)
│       [Core agent handler functionality]
│
├── [... other specialized handler files ...]
│
└── [DELETED/CONSOLIDATED]
    - handlers_comprehensive_test.go (merged)
    - handlers_coverage_expansion_test.go (merged)
    - handlers_additional_coverage_test.go (merged)
    - item_handler_coverage_test.go (merged)
    - graph_handler_refactor_test.go (merged)
    - agent_handler_extended_test.go (merged)
    - agent_coordination_handlers_test.go (merged)

E2E ELEVATED (25 tests → tests/e2e/):
- handlers_integration_test.go (25)
```

---

## tests/e2e/ (New E2E Suite)

### AFTER (Structured E2E Tests)
```
tests/e2e/
├── main_flows_test.go
│   └── TestProjectGraphCreation (1 test with subtests)
│       - Create project
│       - Add items
│       - Create edges
│       - Verify graph structure
│       - Verify WebSocket broadcast
│
├── auth_oauth_flow_test.go
│   └── TestOAuthLoginFlow (1 test with subtests)
│       - OAuth init
│       - Callback
│       - Session creation
│       - First project creation
│
├── search_update_workflow_test.go
│   └── TestSearchFilterUpdate (1 test with subtests)
│       - Bulk create items
│       - Full-text search
│       - Refined filtering
│       - Item update
│       - Index verification
│
├── graph_analysis_flow_test.go
│   └── TestGraphAnalysis (1 test with subtests)
│       - Graph creation
│       - Dependency analysis
│       - Impact analysis
│       - Algorithm verification
│
├── temporal_workflow_test.go
│   └── TestWorkflowExecution (1 test with subtests)
│       - Create execution request
│       - Verify worker pickup
│       - Wait for completion
│       - Result verification
│
├── realtime_sync_test.go
│   └── TestWebSocketSync (1 test with subtests)
│       - Connect WebSocket clients
│       - Create item via API
│       - Verify WebSocket event
│       - Verify event ordering
│
├── error_recovery_test.go
│   └── TestErrorRecovery (1 test with subtests)
│       - Start operation
│       - Network failure
│       - Retry verification
│       - Eventual consistency
│
├── performance_bulk_test.go
│   └── TestBulkImport (1 test with benchmarking)
│       - Bulk import 1M items
│       - Index building
│       - Complex query
│       - Execution time verification
│
├── security_posture_test.go
│   └── TestSecurityControls (1 test with subtests)
│       - CSRF token verification
│       - XSS payload blocking
│       - Rate limit enforcement
│       - Auth header validation
│
├── accessibility_keyboard_test.go
│   └── TestKeyboardNavigation (1 test with subtests, Playwright)
│       - Tab through elements
│       - Focus visibility
│       - Key actions
│       - Screen reader text
│
├── [elevated integration tests from package migrations]
├── service_layer_e2e_test.go               [migrated from tests/e2e/]
├── search_flows_test.go                    [migrated from tests/e2e/]
├── graph_traversal_test.go                 [migrated from tests/e2e/]
├── realtime_updates_test.go                [migrated from tests/e2e/]
├── item_linking_test.go                    [migrated from tests/e2e/]
├── project_lifecycle_test.go               [migrated from tests/e2e/]
├── auth_flows_test.go                      [migrated from tests/e2e/]
└── agent_coordination_test.go              [migrated from tests/e2e/]
```

---

## Summary Statistics

### File Reduction by Package

| Package | Before | After | Reduction |
|---------|--------|-------|-----------|
| internal/search | 12 | 7 | -5 files |
| internal/services | 40+ | 30 | -10 files |
| internal/agents | 15+ | 10 | -5 files |
| internal/handlers | 20+ | 15 | -5 files |
| internal/graph | 12 | 9 | -3 files |
| internal/equivalence | 8 | 7 | -1 file |
| internal/cache | 8 | 7 | -1 file |
| internal/middleware | 7 | 6 | -1 file |
| internal/repository | 7 | 6 | -1 file |
| Other 15+ packages | 70 | 60 | -10 files |
| tests/e2e | 8 | 20 | +12 files |
| **TOTAL** | **299** | **270** | **-29 files** |

### Test Count by Level

| Level | Before | After | Change |
|-------|--------|-------|--------|
| Unit | 3,564 | 2,500 | -1,064 (-30%) |
| Integration | 339 | 250 | -89 (-26%) |
| E2E | 11 | 150 | +139 (+1,264%) |
| **Total** | **3,914** | **2,900** | **-1,014 (-26%)** |

### Execution Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Test Suite Execution | 180s | 130s | -50s (-28%) |
| Test Files | 299 | 270 | -29 (-10%) |
| Avg Tests/File | 13.1 | 10.7 | -2.4 (-18%) |
| Code Review Clarity | Difficult | Easy | +30% easier |
| E2E Coverage | Critical path: 0% | Critical path: 100% | +100% |

---

## Migration Checklist

### Step 1: Consolidate Unit Tests
- [ ] Merge internal/search tests (4 files → 1)
- [ ] Consolidate internal/services (40+ files → 30)
- [ ] Merge internal/agents tests (6 comprehensive → 1)
- [ ] Consolidate internal/handlers (4 comprehensive → 1)
- [ ] Cleanup other packages (10% each)

### Step 2: Elevate Integration Tests
- [ ] Move *_integration_test.go to tests/e2e/
- [ ] Refactor for E2E (use full stack, no mocks)
- [ ] Add 10 missing journey tests

### Step 3: Verify Structure
- [ ] Run full test suite (no regressions)
- [ ] Verify coverage maintained
- [ ] Benchmark execution time
- [ ] Review file organization

### Step 4: Update Documentation
- [ ] Update TESTING.md
- [ ] Add E2E best practices
- [ ] Document consolidation pattern
- [ ] Update CI/CD pipeline

---

**Status:** Blueprint Complete | **Ready for Implementation**
**Last Updated:** 2026-02-06
