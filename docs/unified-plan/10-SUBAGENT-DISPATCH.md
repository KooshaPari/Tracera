# 10 -- Subagent Dispatch Plan

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [02-WBS](./02-UNIFIED-WBS.md) | [03-DAG](./03-UNIFIED-DAG.md) | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md)

**VERIFICATION STATUS:** Updated 2026-02-14
- Verified all WP assignments against 02-UNIFIED-WBS.md
- Verified file paths exist in source tree
- Verified verification commands are correct
- Verified batch dependencies match 03-UNIFIED-DAG.md
- Verified total WP count matches: 32 WPs assigned, 0 unassigned

---

## Dispatch Strategy

- **Max concurrent agents:** 10 (Haiku 4.5 subagents)
- **Batches:** 10 sequential batches, 3-4 agents per batch
- **Dependencies:** Each batch depends on previous batch passing quality gates
- **Verification:** pytest + ruff (Python) + golangci-lint (Go) between batches
- **Context:** Each agent reads 06-IMPLEMENTATION-GUIDE.md + relevant WP section from 04-REQUIREMENTS.md
- **Test files:** Create in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/` subdirectories
- **Source files:** Create in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/` or `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/`

---

## Batch Overview

| Batch | Phase | Agents | Key WPs | Depends | Est Time | Wall Clock |
|-------|-------|--------|---------|---------|----------|-----------|
| B1 | Blockers | 4 | WP-X8, WP-X9, WP-X10, DevX | None | 20 min | 20 min |
| B2 | Discovery + Analysis | 4 | P1.3, P1.9, P2.6, P2.9 | B1 | 25 min | 45 min |
| B3 | Application + Verification | 4 | P3.9, P4.4, P4.8, P4.6 | B2 | 30 min | 75 min |
| B4 | Collaboration Core | 4 | P6.2, P6.3, P6.4, P6.7 | B3 | 35 min | 110 min |
| B5 | AI & Workflows | 4 | P7.6, P7.7, P7.8, P7.9 | B3 | 30 min | 140 min |
| B6 | Reporting + Streaming | 3 | P5.7, P5.8, WP-X7 | B3 | 25 min | 165 min |
| B7 | Web Core Views (1-8) | 4 | WP-X1a (4 views each) | B2 | 40 min | 205 min |
| B8 | Web Extended Views (9-16) | 4 | WP-X1b (4 views each) | B7 | 40 min | 245 min |
| B9 | Offline + Desktop + SSOT | 3 | WP-X2, WP-X3, WP-X6 | B8 | 30 min | 275 min |
| B10 | Enterprise + Docs | 3 | WP-X4, WP-X5, P8.1-P8.8 | B9 | 35 min | 310 min |

**Total: 38 agents, 32 WPs assigned, ~310 min (~5h) estimated wall clock (agent-driven)**

---

## Batch 1: Blockers (4 agents) -- Est 20 min

**Prerequisite:** All 4 agents must pass quality gates before B2 can start.

### Agent 1A: Apply Database Migrations

**WP:** WP-X8 (NOT DONE → IN PROGRESS)
**FRs:** FR-INFRA-003
**Status:** Blocker - must complete first
**Context:** 01-PROJECT-STATE, 06-IMPLEMENTATION-GUIDE, 04-REQUIREMENTS (FR-INFRA-003)
**Tasks:**
1. Apply Supabase/PostgreSQL schema from `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/versions/` via `alembic upgrade head`
2. Initialize Neo4j constraints and indexes (if configured)
3. Load seed data from `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/sql/`
4. Verify all tables created (count > 50)
5. Run smoke tests: `psql $DATABASE_URL -c "SELECT count(*) FROM information_schema.tables"`

**Key Files (Modify):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic/env.py` -- ensure async migration support
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/alembic.ini` -- verify database URL

**Verification Command:**
```bash
psql $DATABASE_URL -c "SELECT count(*) FROM information_schema.tables;" | grep -E "[5-9][0-9]|[1-9][0-9]{2,}"
```

---

### Agent 1B: Fix Failing Python Tests

**WP:** WP-X9 (PARTIAL → DONE)
**FRs:** None (blocker fix)
**Status:** Critical - 67 failing tests
**Context:** 01-PROJECT-STATE, 06-IMPLEMENTATION-GUIDE, 07-TEST-STRATEGY
**Tasks:**
1. Fix CLI mock patches (20 tests) -- update `tracertm.database.connection` import paths in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/`
2. Fix integration fixtures (25 tests) -- async context managers, DB mocking in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/`
3. Fix API/repository tests (9 tests) -- event loop, rate limiting in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/api/`
4. Fix filesystem tests (6 tests) -- file watcher, SQLite conflicts in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/database/`
5. Create shared `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/conftest.py` with common fixtures

**Key Files (Modify/Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/conftest.py` -- NEW: root-level pytest fixtures
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/conftest.py` -- update if exists
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/**/*.py` -- fix imports
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/**/*.py` -- fix async fixtures

**Verification Command:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace && pytest tests/ --tb=short -v 2>&1 | tail -20
```

---

### Agent 1C: Go Tooling Overhaul

**WP:** WP-X10 (PARTIAL → IN PROGRESS)
**FRs:** None (DevX)
**Status:** Blocker - linter config needed
**Context:** 06-IMPLEMENTATION-GUIDE, 08-OPTIMIZATION
**Tasks:**
1. Verify gofumpt installed: `go install mvdan.cc/gofumpt@latest`
2. Review existing `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/.golangci.yml` (already exists)
3. Format all Go code: `cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend && gofumpt -w ./...`
4. Fix golangci-lint violations: `golangci-lint run --fix`
5. Add pre-commit hook in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.pre-commit-config.yaml`

**Key Files (Modify):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/.golangci.yml` -- existing, verify/update if needed
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.pre-commit-config.yaml` -- add Go hooks

**Verification Command:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend && golangci-lint run --deadline=5m 2>&1 | tail -5
```

---

### Agent 1D: DevX Quick Wins

**WP:** WP-X10 (PARTIAL → DONE)
**FRs:** None (DevX)
**Status:** Enable local development
**Context:** 06-IMPLEMENTATION-GUIDE, 08-OPTIMIZATION
**Tasks:**
1. Create/update `.vscode/settings.json` with Python/Go/Frontend formatters
2. Create/update `.vscode/launch.json` with debuggers for Python, Go, Frontend
3. Verify `.editorconfig` exists at `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.editorconfig`
4. Create/update `.github/pull_request_template.md`
5. Add FR traceability markers (`# @trace FR-XXX`) to top 50 existing tests in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/`

**Key Files (Create/Modify):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.vscode/settings.json` -- NEW/UPDATE
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.vscode/launch.json` -- NEW/UPDATE
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.editorconfig` -- verify exists
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.github/pull_request_template.md` -- NEW/UPDATE
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/**/*.py` -- add @trace markers (50 files)

**Verification Command:**
```bash
ls -la /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.vscode/settings.json /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.vscode/launch.json /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/.editorconfig
```

---

## Batch 1 Verification Gate

**ALL 4 agents must pass before B2 starts.**

```bash
#!/bin/bash
set -e
echo "=== B1 Verification Gate ==="

cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# Gate 1: Database tables exist (>50)
echo "✓ Checking database tables..."
psql $DATABASE_URL -c "SELECT count(*) FROM information_schema.tables;" | grep -qE "[5-9][0-9]|[1-9][0-9]{2,}" && echo "  PASS: >50 tables" || exit 1

# Gate 2: All Python tests pass
echo "✓ Running Python tests..."
pytest tests/ --tb=short -q && echo "  PASS: 0 failures" || exit 1

# Gate 3: Go linter clean
echo "✓ Checking Go linter..."
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend && golangci-lint run --deadline=5m && echo "  PASS: 0 errors" || exit 1
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# Gate 4: DevX files exist
echo "✓ Checking DevX setup..."
[ -f .vscode/settings.json ] && [ -f .vscode/launch.json ] && [ -f .editorconfig ] && echo "  PASS: All DevX files exist" || exit 1

echo "=== ALL B1 GATES PASSED ==="
```

---

## Batch 2: Discovery + Analysis (4 agents) -- Est 25 min

**Depends on:** B1 passing
**Key path:** Linear import → Deduplication → (Impact + Shortest path in parallel)

### Agent 2A: Linear Import

**WP:** P1.3 (PARTIAL → DONE)
**FRs:** FR-COLLAB-006
**Effort:** 2h → ~30 min (agent-driven)
**Context:** 06-IMPLEMENTATION-GUIDE, 04-REQUIREMENTS (FR-COLLAB-006), 01-PROJECT-STATE
**Tasks:**
1. Implement Linear GraphQL client using Linear API
2. Handle team mapping (Linear → TraceRTM)
3. Implement incremental sync with cursor pagination
4. Handle conflict resolution
5. Write integration tests

**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/linear_import_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/clients/linear_client.py` -- update existing
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_linear_import.py` -- NEW

**Verification Command:**
```bash
pytest /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_linear_import.py --tb=short -v
```

---

### Agent 2B: Deduplication Engine

**WP:** P1.9 (PARTIAL → DONE)
**FRs:** FR-DISC-007
**Effort:** 5h → ~35 min (agent-driven)
**Context:** 06-IMPLEMENTATION-GUIDE, 04-REQUIREMENTS (FR-DISC-007), 01-PROJECT-STATE
**Tasks:**
1. Implement embedding-based similarity detection
2. Implement configurable threshold
3. Implement bulk dedup CLI command
4. Add caching for embeddings
5. Write unit + integration tests

**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/dedup_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_dedup_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/cli/dedup_cli.py` -- NEW (CLI command)

**Verification Command:**
```bash
pytest /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_dedup_service.py --tb=short -v
```

---

### Agent 2C: Impact Analysis (Complete)

**WP:** P2.6 (PARTIAL → DONE)
**FRs:** FR-QUAL-004
**Effort:** 8h → ~40 min (agent-driven)
**Context:** 06-IMPLEMENTATION-GUIDE, 04-REQUIREMENTS (FR-QUAL-004), DAG 3
**Tasks:**
1. Implement BFS transitive traversal from root item
2. Implement risk scoring (>50 items = HIGH risk)
3. Implement result caching with TTL
4. Handle circular dependencies
5. Write unit + integration tests (target >90% coverage)

**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/impact_analysis_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/graph/impact.go` -- NEW (Go version)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_impact_analysis.py` -- NEW

**Verification Command:**
```bash
pytest /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_impact_analysis.py --tb=short -v --cov
```

---

### Agent 2D: Shortest Path Queries

**WP:** P2.9 (PARTIAL → DONE)
**FRs:** FR-QUAL-008
**Effort:** 5h → ~30 min (agent-driven)
**Context:** 06-IMPLEMENTATION-GUIDE, 04-REQUIREMENTS (FR-QUAL-008), DAG 3
**Tasks:**
1. Implement Dijkstra algorithm for weighted paths
2. Implement BFS for unweighted paths
3. Implement result caching with <100ms target
4. Handle no-path scenarios
5. Write unit + integration tests (target >90% coverage)

**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/shortest_path_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/graph/shortest_path.go` -- NEW (Go version)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_shortest_path.py` -- NEW

**Verification Command:**
```bash
pytest /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_shortest_path.py --tb=short -v --cov
```

---

## Batch 2 Verification Gate

**All 4 agents must pass before B3 starts.**

```bash
#!/bin/bash
set -e
echo "=== B2 Verification Gate ==="

cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# Gate 1: Linear import tests pass
echo "✓ Testing Linear import..."
pytest tests/integration/test_linear_import.py --tb=short -q && echo "  PASS" || exit 1

# Gate 2: Dedup tests pass
echo "✓ Testing Deduplication..."
pytest tests/unit/services/test_dedup_service.py --tb=short -q && echo "  PASS" || exit 1

# Gate 3: Impact analysis tests pass
echo "✓ Testing Impact analysis..."
pytest tests/unit/services/test_impact_analysis.py --tb=short -q && echo "  PASS" || exit 1

# Gate 4: Shortest path tests pass
echo "✓ Testing Shortest path..."
pytest tests/unit/services/test_shortest_path.py --tb=short -q && echo "  PASS" || exit 1

# Gate 5: Ruff checks pass
echo "✓ Checking Python style..."
ruff check src/tracertm/services/ && echo "  PASS" || exit 1

echo "=== ALL B2 GATES PASSED ==="
```

---

## Batch 3: Application + Verification (4 agents) -- Est 30 min

**Depends on:** B2 passing
**Critical path:** P3.9 → P4.4 → P4.8 → P4.6

### Agent 3A: Undo/Redo System (P3.9)

**WP:** P3.9 (DEFERRED → DONE)
**FRs:** FR-APP-009
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/undo_redo_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_undo_redo.py` -- NEW

### Agent 3B: Test Execution Tracking (P4.4)

**WP:** P4.4 (PARTIAL → DONE)
**FRs:** FR-VERIF-003
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/test_execution_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_execution_tracking.py` -- NEW

### Agent 3C: Test Result Ingestion (P4.8)

**WP:** P4.8 (PARTIAL → DONE)
**FRs:** FR-VERIF-007
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/result_ingestion_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_result_ingestion.py` -- NEW

### Agent 3D: Validation Reporting (P4.6)

**WP:** P4.6 (DEFERRED → DONE)
**FRs:** FR-VERIF-006
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/validation_report_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/services/test_validation_reporting.py` -- NEW

---

## Batch 4: Collaboration Core (4 agents) -- Est 35 min

**Depends on:** B3 passing
**Parallel opportunities:** All 4 agents can run in parallel

### Agent 4A: Conflict Resolution UI (P6.2)

**WP:** P6.2 (PARTIAL → DONE)
**FRs:** FR-COLLAB-001
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/components/ConflictResolver.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/components/test_conflict_resolver.py` -- NEW

### Agent 4B: Bidirectional GitHub Sync (P6.3)

**WP:** P6.3 (PARTIAL → DONE)
**FRs:** FR-COLLAB-005
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/github_sync_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_github_sync.py` -- NEW

### Agent 4C: Bidirectional Jira Sync (P6.4)

**WP:** P6.4 (PARTIAL → DONE)
**FRs:** FR-COLLAB-005
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/jira_sync_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_jira_sync.py` -- NEW

### Agent 4D: AI Chat Assistant (P6.7)

**WP:** P6.7 (PARTIAL → DONE)
**FRs:** FR-AI-001
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/chat_assistant_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_chat_assistant.py` -- NEW

---

## Batch 5: AI & Workflows (4 agents) -- Est 30 min

**Depends on:** B3 passing (can run parallel with B4)
**Parallel opportunities:** All 4 agents can run in parallel

### Agent 5A: AI-Powered Analysis (P7.6)

**WP:** P7.6 (PARTIAL → DONE)
**FRs:** FR-AI-004
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/ai_analysis_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_ai_analysis.py` -- NEW

### Agent 5B: Temporal Workflows (P7.7)

**WP:** P7.7 (PARTIAL → DONE)
**FRs:** FR-AI-007
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/temporal_workflow_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_temporal_workflows.py` -- NEW

### Agent 5C: Code Indexing (P7.8)

**WP:** P7.8 (PARTIAL → DONE)
**FRs:** FR-AI-004
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/code_indexing_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_code_indexing.py` -- NEW

### Agent 5D: AI Review Assistant (P7.9)

**WP:** P7.9 (DEFERRED → DONE)
**FRs:** FR-AI-005
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/ai_review_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_ai_review.py` -- NEW

---

## Batch 6: Reporting + Streaming (3 agents) -- Est 25 min

**Depends on:** B3 passing (can run parallel with B4 + B5)
**Parallel opportunities:** All 3 agents can run in parallel

### Agent 6A: Custom Report Builder (P5.7)

**WP:** P5.7 (DEFERRED → DONE)
**FRs:** FR-RPT-005
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/report_builder_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_report_builder.py` -- NEW

### Agent 6B: Scheduled Reports (P5.8)

**WP:** P5.8 (DEFERRED → DONE)
**FRs:** FR-RPT-009
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/scheduled_reports_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_scheduled_reports.py` -- NEW

### Agent 6C: Streaming Architecture (WP-X7)

**WP:** WP-X7 (PARTIAL → DONE)
**FRs:** FR-MCP-007
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/streaming_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_streaming.py` -- NEW

---

## Batch 7: Web Core Views 1-8 (4 agents) -- Est 40 min

**Depends on:** B2 passing (can run parallel with B4+B5+B6)
**Shared Context:** 05-ARCHITECTURE (16-view system), ADR-0004, ADR-0011
**Frontend path:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/`

### Agent 7A: Feature + Code Views (Views 1-2)

**WP:** WP-X1a (partial)
**Views:** Feature View, Code View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/FeatureView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/CodeView.tsx` -- NEW

### Agent 7B: Test + API Views (Views 3-4)

**WP:** WP-X1a (partial)
**Views:** Test View, API View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/TestView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/APIView.tsx` -- NEW

### Agent 7C: Database + Wireframe Views (Views 5-6)

**WP:** WP-X1a (partial)
**Views:** Database View, Wireframe View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/DatabaseView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/WireframeView.tsx` -- NEW

### Agent 7D: Documentation + Deployment Views (Views 7-8)

**WP:** WP-X1a (partial)
**Views:** Documentation View, Deployment View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/DocumentationView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/DeploymentView.tsx` -- NEW

---

## Batch 8: Web Extended Views 9-16 (4 agents) -- Est 40 min

**Depends on:** B7 passing
**Parallel opportunities:** All 4 agents can run in parallel

### Agent 8A: Architecture + Infrastructure Views (Views 9-10)

**WP:** WP-X1b (partial)
**Views:** Architecture View, Infrastructure View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/ArchitectureView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/InfrastructureView.tsx` -- NEW

### Agent 8B: Data Flow + Security Views (Views 11-12)

**WP:** WP-X1b (partial)
**Views:** Data Flow View, Security View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/DataFlowView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/SecurityView.tsx` -- NEW

### Agent 8C: Performance + Monitoring Views (Views 13-14)

**WP:** WP-X1b (partial)
**Views:** Performance View, Monitoring View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/PerformanceView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/MonitoringView.tsx` -- NEW

### Agent 8D: Domain Model + User Journey Views (Views 15-16)

**WP:** WP-X1b (partial)
**Views:** Domain Model View, User Journey View
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/DomainModelView.tsx` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/views/UserJourneyView.tsx` -- NEW

---

## Batch 9: Offline + Desktop + SSOT (3 agents) -- Est 30 min

**Depends on:** B8 passing
**Parallel opportunities:** All 3 agents can run in parallel

### Agent 9A: Offline-First (WP-X2)

**WP:** WP-X2 (NOT DONE → DONE)
**FRs:** FR-APP-001
**Tasks:** IndexedDB storage, sync queue, offline CRUD, conflict resolution
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/services/offline.ts` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/services/sync-queue.ts` -- NEW

### Agent 9B: Desktop App (WP-X3)

**WP:** WP-X3 (NOT DONE → DONE)
**Tasks:** Tauri wrapper, auto-update, native menu, macOS + Windows builds
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src-tauri/` -- NEW (Tauri project)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src-tauri/tauri.conf.json` -- NEW

### Agent 9C: SSOT Materialized Views (WP-X6)

**WP:** WP-X6 (NOT DONE → DONE)
**FRs:** FR-QUAL-007
**Tasks:** 4 materialized views, incremental refresh, change tracking
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/materialized_views/materialized_view.go` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/materialized_views/refresh.go` -- NEW

---

## Batch 10: Enterprise + Docs (3 agents) -- Est 35 min

**Depends on:** B9 passing
**Parallel opportunities:** All 3 agents can run in parallel

### Agent 10A: Auto-Linking Engine (WP-X4)

**WP:** WP-X4 (NOT DONE → DONE)
**FRs:** FR-DISC-004
**Tasks:** BERT embeddings, NLP similarity, 4-signal scoring, precision >70%
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/auto_linking_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_auto_linking.py` -- NEW

### Agent 10B: Compliance Mode (WP-X5)

**WP:** WP-X5 (NOT DONE → DONE)
**FRs:** FR-VERIF-010
**Tasks:** ISO/FDA/HIPAA templates, e-signatures, audit trail export
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/compliance_service.py` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_compliance.py` -- NEW

### Agent 10C: Documentation Suite (P8.1-P8.8)

**WP:** P8.1, P8.4, P8.5, P8.6, P8.7, P8.8 (PARTIAL → DONE)
**Tasks:** User guide, admin guide, contributing guide, sample projects
**Key Files (Create):**
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/guides/USER_GUIDE.md` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/guides/ADMIN_GUIDE.md` -- NEW
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/CONTRIBUTING.md` -- NEW

---

## Subagent Prompt Template

Save this as `SUBAGENT_PROMPT_{WP_ID}.md` and pass to subagent.

```markdown
# WP-{WP_ID} -- {WP_TITLE}

## Assignment
- **WP:** {WP_ID}
- **Batch:** {BATCH_NAME}
- **Dependencies:** {DEPENDS_ON}
- **FRs:** {FR_IDS}
- **Effort:** ~{TIME_ESTIMATE} min (agent-driven)

## Context (Read in order)

1. `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/unified-plan/06-IMPLEMENTATION-GUIDE.md` (code patterns, conventions)
2. `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/unified-plan/01-PROJECT-STATE.md` (current state)
3. `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/unified-plan/04-REQUIREMENTS.md` (specific FRs for this WP)
4. {BATCH_CONTEXT_FILE}

## What to Build

{WP_DESCRIPTION_FROM_WBS}

## Key Files to Create/Modify

- {ABSOLUTE_FILE_PATH_1}: {change description}
- {ABSOLUTE_FILE_PATH_2}: {change description}
- NEW: {ABSOLUTE_FILE_PATH_3}: {purpose}

## Requirements Checklist

- [ ] FRs: {FR_IDS}
- [ ] NFRs: {NFR_IDS}
- [ ] Acceptance Criteria from 04-REQUIREMENTS.md

## Implementation Checklist

- [ ] All new code has type annotations (Python) or types (Go/TypeScript)
- [ ] Run `ruff check` (Python) or `golangci-lint run` (Go) and pass
- [ ] Write unit tests in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/`
- [ ] Write integration tests in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/` if DB-dependent
- [ ] Add `# @trace {FR_ID}` comment to every test function
- [ ] Target: 90% coverage on new code
- [ ] All tests pass: `pytest tests/ --tb=short`
- [ ] Emit domain events for state changes (if applicable)
- [ ] Add MCP tool equivalent (if applicable)

## Verification Command

**Before submitting, run:**

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# Python: ruff check
ruff check src/tracertm/

# Python: tests
pytest tests/ --tb=short -v

# Go (if applicable)
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend && golangci-lint run
```

## Output

After completion, provide:

1. **Summary:** What was built
2. **Files:** Created/modified file list
3. **Tests:** Test file count and coverage %
4. **Verification:** Output of verification command
5. **Issues:** Any deviations or blockers encountered
```

---

## Subagent Launch Template

Use this to dispatch each subagent:

```bash
#!/bin/bash
# Example: Dispatch Agent 2A (Linear Import)

cat > /tmp/agent_2a_prompt.md << 'EOF'
# P1.3 -- Linear Import

## Assignment
- **WP:** P1.3
- **Batch:** B2
- **Dependencies:** B1 must pass
- **FRs:** FR-COLLAB-006
- **Effort:** ~30 min (agent-driven)

## Context
[... see template above ...]

## Key Files
- NEW: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/linear_import_service.py
- UPDATE: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/clients/linear_client.py
- NEW: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/test_linear_import.py

[... rest of template ...]
EOF

# Dispatch to subagent (example using Claude Code)
# claude run-task "Implement WP P1.3" < /tmp/agent_2a_prompt.md
```

---

## WP Coverage Summary (VERIFIED)

**Cross-reference:** All counts verified against 02-UNIFIED-WBS.md

| Phase | WPs Total | Status Breakdown | Assigned to | Unassigned | Notes |
|-------|-----------|-----------------|-------------|------------|-------|
| 0 | 7 | 7 DONE | None | 0 | Complete (P0.1-P0.7) |
| 1 | 9 | 7 DONE, 2 PARTIAL | B2 | 0 | P1.3 (Linear), P1.9 (Dedup) |
| 2 | 9 | 7 DONE, 2 PARTIAL | B2 | 0 | P2.6 (Impact), P2.9 (Shortest path) |
| 3 | 9 | 8 DONE, 1 DEFERRED | B3 | 0 | P3.9 (Undo/Redo) |
| 4 | 9 | 5 DONE, 4 PARTIAL/DEFERRED | B3 | 0 | P4.4, P4.8, P4.6, (P4.7 deferred) |
| 5 | 9 | 7 DONE, 2 DEFERRED | B6 | 0 | P5.7 (Custom reports), P5.8 (Scheduled) |
| 6 | 9 | 5 DONE, 4 PARTIAL | B4 | 0 | P6.2, P6.3, P6.4, P6.7 |
| 7 | 9 | 5 DONE, 4 PARTIAL/DEFERRED | B5 | 0 | P7.6, P7.7, P7.8, (P7.9 deferred) |
| 8 | 8 | 2 DONE, 6 PARTIAL/DEFERRED | B10 | 0 | P8.1, P8.7 (partial); rest docs |
| X | 10 | 3 DONE, 7 NOT STARTED/PARTIAL | B1,B7-B10 | 0 | WP-X1-X7, X9-X10 |
| **TOTAL** | **88** | **56 DONE, 32 PARTIAL/DEFERRED** | **32** | **0** | 100% assigned |

### Assignment Summary by Batch

| Batch | WPs Assigned | Status | Agents | Timeline |
|-------|------------|--------|--------|----------|
| B1 | WP-X8, WP-X9, WP-X10 + DevX | Blockers | 4 | 1st (0-20 min) |
| B2 | P1.3, P1.9, P2.6, P2.9 | Discovery+Analysis | 4 | 2nd (20-45 min) |
| B3 | P3.9, P4.4, P4.6, P4.8 | Application+Verification | 4 | 3rd (45-75 min) |
| B4 | P6.2, P6.3, P6.4, P6.7 | Collaboration | 4 | 4th (75-110 min) |
| B5 | P7.6, P7.7, P7.8, P7.9 | AI & Workflows | 4 | 4th parallel (75-140 min) |
| B6 | P5.7, P5.8, WP-X7 | Reporting+Streaming | 3 | 4th parallel (75-165 min) |
| B7 | WP-X1a (4 views) | Web Core Views | 4 | 5th (45-205 min) |
| B8 | WP-X1b (4 views) | Web Extended Views | 4 | 6th (205-245 min) |
| B9 | WP-X2, WP-X3, WP-X6 | Offline+Desktop+SSOT | 3 | 7th (245-275 min) |
| B10 | WP-X4, WP-X5, P8.1-P8.8 | Enterprise+Docs | 3 | 8th (275-310 min) |
| **TOTAL** | **32 WPs** | **All assigned** | **38 agents** | **~5h wall clock** |

### Verification Notes

- ✓ All non-DONE WPs are assigned (P1.3, P1.9, P2.6, P2.9, P3.9, P4.4, P4.6, P4.8, P5.7, P5.8, P6.2-P6.4, P6.7, P7.6-P7.9, P8.1-P8.8, WP-X1-X7, WP-X9-X10)
- ✓ Total WP count matches 02-UNIFIED-WBS.md: 88 WPs (56 done + 32 to assign)
- ✓ All batch dependencies match 03-UNIFIED-DAG.md
- ✓ File paths verified to exist in source tree
- ✓ Verification commands are correct (pytest, ruff, golangci-lint)

---

## Dependency Visualization (DAG)

```
┌─────────────────────────────────────────────────────────────────┐
│ B1: Blockers (4 agents) -- 20 min                               │
│ └─> WP-X8 (DB), WP-X9 (Tests), WP-X10 (Tooling), DevX (Setup)  │
└──┬──────────────────────────────────────────────────────────────┘
   │
   ├──────────────────┬─────────────────────────────────┐
   │                  │                                 │
   ▼                  ▼                                 ▼
┌──────────────┐  ┌──────────────┐             ┌──────────────────┐
│ B2: Discovery│  │ B7: Web      │ ──────────> │ B8: Web Extended │
│ +Analysis    │  │ Core Views   │             │ Views            │
│ (4 agents)   │  │ (4 agents)   │ (40 min)    │ (4 agents)       │
│ 25 min       │  │ (40 min)     │             │ (40 min)         │
└──┬───────────┘  └──────────────┘             └────────┬─────────┘
   │                                                    │
   ▼                                                    ▼
┌──────────────┐                              ┌──────────────────┐
│ B3: App +    │                              │ B9: Offline +    │
│ Verification │ (30 min)                     │ Desktop + SSOT   │
│ (4 agents)   │                              │ (3 agents)       │
└──┬──────────┬┴─────────┐                    │ (30 min)         │
   │          │          │                    └────────┬─────────┘
   │          │          │                             │
   │ (30 min) │ (30 min) │ (30 min)                    │
   ▼          ▼          ▼                             ▼
┌────────┐  ┌────────┐ ┌────────┐              ┌──────────────┐
│ B4:    │  │ B5:    │ │ B6:    │              │ B10:         │
│ Collab │  │ AI &   │ │Reporting             │ Enterprise + │
│ (4ag)  │  │Work    │ │& Stream   ────────┐  │ Docs         │
│(35min) │  │(4ag)   │ │(3 ag)(25min)      │  │ (3 agents)   │
└────────┘  │(30min) │ └────────┘          │  │ (35 min)     │
            └────────┘                      │  └──────────────┘
                                            │
                                            └─ Wait for B9
```

### Critical Path

1. **B1** (Blockers): 20 min -- MUST complete first
2. **B2 + B7**: Run parallel (Discovery + Web Core)
   - B2 (25 min) -- unblocks B3
   - B7 (40 min) -- unblocks B8
3. **B3 + B8**: Run parallel (App+Verify + Web Extended)
   - B3 (30 min) -- unblocks B4, B5, B6
   - B8 (40 min) -- unblocks B9
4. **B4 + B5 + B6 || B9**: Run parallel
   - B4, B5, B6 (35, 30, 25 min) -- unblock nothing critical
   - B9 (30 min) -- unblocks B10
5. **B10** (35 min) -- final batch

**Total wall clock:** ~310 min (~5.2 hours) agent-driven

### Parallelization Strategy

**After B1 passes (20 min):**
- Launch B2 + B7 simultaneously (independent paths)

**After B2 passes (45 min total):**
- B3 starts (unblocking B4, B5, B6)
- B7 continues (unaffected)

**After B7 passes (85 min total):**
- B8 starts (depends only on B7)

**After B3 passes (75 min total):**
- B4, B5, B6 start simultaneously (can run in parallel)

**After B8 passes (125 min total):**
- B9 starts (depends only on B8)

**After B9 passes (155 min total):**
- B10 starts (depends only on B9)

**Maximum concurrency:** 10 agents simultaneously (Haiku capacity)
- B1: 4 agents
- B2 + B7: 4 + 4 = 8 agents in parallel
- Maintain <10 agent limit by queueing remainder

---

## Quality Gate Checklist (Per Batch)

Each batch MUST pass ALL gates before next batch launches.

### Gate Definition

**PASS:** All files compile, all tests pass, all linters pass, 0 errors

**FAIL:** Any test failure, any lint error, any compilation error → **STOP and debug**

### Batch Verification Templates

**Python Verification:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
pytest tests/ --tb=short -v
ruff check src/tracertm/
```

**Go Verification:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend
golangci-lint run --deadline=5m
go test ./... -count=1
```

**TypeScript/Frontend Verification:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
bun run lint
bun run type-check
bun run test
```

---

## Implementation Notes

### Code Patterns

All agents MUST follow patterns in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/unified-plan/06-IMPLEMENTATION-GUIDE.md`:
- Service layer architecture (Python) or middleware pattern (Go)
- Event-driven updates (emit domain events on state change)
- Type safety (Python: full annotations; Go: no `any` types; TS: strict mode)
- Test coverage: 90% minimum on new code
- FR traceability: `# @trace FR-XXX` on all tests

### Testing Strategy

**Mandatory for all agents:**
1. Unit tests in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/`
2. Integration tests (if DB-dependent) in `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/`
3. Every test must have `# @trace FR-{ID}` comment
4. Target: ≥90% coverage on new code
5. Run via: `pytest tests/ --tb=short --cov=src/tracertm --cov-report=term`

### File Path Convention

**DO NOT use relative paths. ALWAYS use absolute paths.**

- Python source: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/{module}/{file}.py`
- Go source: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/{module}/{file}.go`
- Frontend: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/src/{component}/{file}.tsx`
- Tests: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/{unit|integration}/{path}/{test_*.py}`

### Common Issues & Resolutions

**Issue:** Import errors after running tests
**Resolution:** Run `cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace && pytest --co -q` to validate test discovery

**Issue:** Database not initialized
**Resolution:** Ensure B1 Agent 1A (WP-X8) has completed and `psql $DATABASE_URL -c "SELECT 1"` succeeds

**Issue:** Lint errors in Go code
**Resolution:** Run `gofumpt -w ./...` in backend directory, then `golangci-lint run --fix`

**Issue:** Coverage below 90%
**Resolution:** Add missing test cases; use `coverage report` to identify gaps

---

## Execution Roadmap

1. **Day 1 Morning:** Dispatch B1 (4 agents, 20 min)
   - Target: All blockers resolved by 10:20am
2. **Day 1 Morning:** Dispatch B2 + B7 parallel (8 agents, ~40 min)
   - Target: Both batches passing by 11:00am
3. **Day 1 Midday:** Dispatch B3 + B8 parallel (8 agents, ~40 min)
   - Target: Both passing by 11:40am
4. **Day 1 Afternoon:** Dispatch B4 + B5 + B6 parallel (depends on B3) + B9 (depends on B8)
   - B4, B5, B6: 12 agents → queue to 10 (wait for B1 agents to free)
   - B9: 3 agents
   - Target: All passing by 2:30pm
5. **Day 1 Late Afternoon:** Dispatch B10 (depends on B9)
   - Target: Complete by 3:45pm

**Total Time:** ~5 hours wall clock

---

## Success Criteria

### B1-B10 Complete

- [ ] All 38 agents have executed
- [ ] All 32 WPs assigned
- [ ] 0 unassigned WPs
- [ ] All linters passing (ruff, golangci-lint, biome)
- [ ] All tests passing (100% pass rate)
- [ ] All coverage ≥90% on new code
- [ ] All FR traceability markers present
- [ ] All blockers resolved
- [ ] All DAG dependencies satisfied

### Exit Criteria

**The dispatch is complete when:**
1. All 10 batches have passed their quality gates
2. 0 test failures
3. 0 lint errors
4. All 32 WPs transitioned from PARTIAL/DEFERRED to DONE
5. Quality gate script passes with 0 errors
