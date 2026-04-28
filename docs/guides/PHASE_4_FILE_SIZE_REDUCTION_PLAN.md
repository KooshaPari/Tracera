# Phase 4: File Size Reduction - <500 Lines Per File

**Date**: 2026-02-02
**Phase**: 4 (File Size Enforcement)
**Goal**: Reduce ALL files to <500 lines
**Status**: 🟡 READY TO LAUNCH
**Execution Model**: Async agent swarm (5-50 concurrent agents)

---

## Executive Summary

**Objective**: Enforce strict <500 line limit on all source files across Python, Go, and TypeScript/React codebases through systematic decomposition and module extraction.

**Current State**:
- **Python**: 20 files >500 lines (largest: main.py at 9,768 lines)
- **Go**: 16 files >500 lines (excluding 4 auto-generated files)
- **Frontend**: TBD (needs source-only scan)

**Target State**:
- **Python**: 0 files >500 lines
- **Go**: 0 files >500 lines (excluding auto-generated)
- **Frontend**: 0 files >500 lines

**Estimated Effort**: 50-100 agent-hours (8-16 hours wall clock with async swarm)

---

## Scope and Targets

### Wave 1: Python main.py Mega-Decomposition 🔴 CRITICAL

**Target**: `src/tracertm/api/main.py` (9,768 lines → <500 lines)

**Challenge**: This requires extracting **~95% of the file** into modules

**Strategy**: Extract ALL endpoints into routers, ALL middleware into config modules

**Modules to Create** (20+ modules):

#### Config Modules (already created, need integration verification)
- ✅ `config/startup.py` (517 lines) - CREATED
- ✅ `config/rate_limiting.py` (160 lines) - CREATED

#### Handler Modules (5 created, 10+ more needed)
- ✅ `handlers/websocket.py` (224 lines) - CREATED
- ✅ `handlers/items.py` (245 lines) - CREATED
- ✅ `handlers/links.py` (437 lines) - CREATED
- 🔜 `handlers/oauth.py` - Extract oauth_callback (C=16, ~200 lines)
- 🔜 `handlers/github.py` - Extract list_github_repos, create_github_repo, list_github_projects (C=15, 8, 8)
- 🔜 `handlers/chat.py` - Extract stream_chat, generate (C=12, 9)
- 🔜 `handlers/health.py` - Extract api_health_check (C=13)
- 🔜 `handlers/device.py` - Extract device_complete_endpoint (C=11)
- 🔜 `handlers/auth.py` - Extract auth_me_endpoint (C=9)
- 🔜 `handlers/integrations.py` - Extract get_integration_stats (C=9)
- 🔜 `handlers/webhooks.py` - Extract github_app_webhook (C=8)

#### Router Modules (new, extract ALL endpoint groups)
- 🔜 `routers/projects.py` - Extract all `/projects/*` endpoints (~500 lines)
- 🔜 `routers/items.py` - Extract all `/items/*` endpoints (~800 lines)
- 🔜 `routers/links.py` - Extract all `/links/*` endpoints (~300 lines)
- 🔜 `routers/github.py` - Extract all `/github/*` endpoints (~600 lines)
- 🔜 `routers/oauth.py` - Extract all `/oauth/*` endpoints (~200 lines)
- 🔜 `routers/websocket.py` - Extract WebSocket routes (~100 lines)
- 🔜 `routers/health.py` - Extract health/metrics endpoints (~150 lines)
- 🔜 `routers/integrations.py` - Extract integration endpoints (~400 lines)
- 🔜 `routers/chat.py` - Extract chat/AI endpoints (~200 lines)
- 🔜 `routers/device.py` - Extract device flow endpoints (~150 lines)

#### Middleware Modules
- 🔜 `middleware/auth.py` - Extract auth middleware (~200 lines)
- 🔜 `middleware/cors.py` - Extract CORS config (~100 lines)
- 🔜 `middleware/logging.py` - Extract request logging (~150 lines)
- 🔜 `middleware/error_handling.py` - Extract error handlers (~200 lines)

**Extraction Plan**:
1. Extract all handlers (10 modules, ~2,000 lines)
2. Extract all routers (10 modules, ~3,500 lines)
3. Extract all middleware (4 modules, ~650 lines)
4. Extract all dependencies (auth guards, DB session, etc.) (~500 lines)
5. Remaining main.py should be ~450 lines (app initialization + router registration)

**Success Criteria**:
- ✅ main.py <500 lines (currently 9,768)
- ✅ All extracted modules <500 lines each
- ✅ Zero test failures
- ✅ All imports working
- ✅ CI green

**Agent Allocation**: 20-25 agents (1 per module + integration + testing)

---

### Wave 2: Python Large Files (19 files) 🟡 HIGH PRIORITY

#### Tier 1: >2,000 lines (4 files)

**1. `api/routers/item_specs.py` (3,203 lines → split into 7 routers)**
- Extract: item_specs CRUD, validation, analytics, search, export, import, history
- Create: 7 router modules at ~450 lines each

**2. `services/spec_analytics_service.py` (2,664 lines → split into 6 services)**
- Extract: metrics calculation, aggregation, reporting, visualization, export, caching
- Create: 6 service modules at ~440 lines each

**3. `cli/commands/item.py` (2,059 lines → split into 5 command groups)**
- Extract: create, read, update, delete, search commands
- Create: 5 command modules at ~400 lines each

**4. `mcp/tools/param.py` (1,822 lines → split into 4 modules)**
- Extract: param validation, conversion, serialization, utilities
- Create: 4 modules at ~450 lines each

**Agent Allocation**: 4-8 agents (1-2 per file)

#### Tier 2: 1,000-2,000 lines (12 files)

**Files**:
- `storage/local_storage.py` (1,712 lines) → split into 4 modules
- `cli/commands/project.py` (1,388 lines) → split into 3 modules
- `repositories/item_spec_repository.py` (1,350 lines) → split into 3 modules
- `api/client.py` (1,335 lines) → split into 3 modules
- `api/routers/specifications.py` (1,304 lines) → split into 3 modules
- `schemas/item_spec.py` (1,223 lines) → split into 3 modules
- `services/stateless_ingestion_service.py` (1,072 lines) → split into 3 modules
- `storage/sync_engine.py` (1,068 lines) → split into 3 modules
- `models/item_spec.py` (1,066 lines) → split into 3 modules
- `services/item_spec_service.py` (1,036 lines) → split into 3 modules
- `cli/commands/import_cmd.py` (1,027 lines) → split into 3 modules
- `cli/commands/link.py` (1,017 lines) → split into 3 modules

**Strategy**: Extract by responsibility (CRUD vs analytics vs validation vs export)

**Agent Allocation**: 12-24 agents (1-2 per file)

#### Tier 3: 500-1,000 lines (4 files)

**Files**:
- `services/ai_tools.py` (993 lines) → split into 2 modules
- `cli/commands/design.py` (897 lines) → split into 2 modules
- `repositories/specification_repository.py` (850 lines) → split into 2 modules

**Strategy**: Extract by feature area

**Agent Allocation**: 4-6 agents (1-2 per file)

---

### Wave 3: Go Large Files (16 files) 🟢 MEDIUM PRIORITY

#### Auto-Generated Files (EXCLUDE from refactoring)
- ❌ `backend/docs/tracertm_docs.go` (6,799 lines) - swagger auto-gen
- ❌ `backend/docs/docs.go` (6,799 lines) - swagger auto-gen
- ❌ `backend/internal/db/queries.sql.go` (4,045 lines) - sqlc auto-gen
- ❌ `backend/pkg/proto/tracertm/v1/tracertm.pb.go` (2,005 lines) - protobuf auto-gen

#### Integration Test Files (5 files - split by feature)

**1. `tests/integration/service_integration_test.go` (1,490 lines → 3 files)**
- Split: service_auth_test.go, service_items_test.go, service_integrations_test.go

**2. `tests/integration/endpoints_test.go` (1,479 lines → 3 files)**
- Split: endpoints_projects_test.go, endpoints_items_test.go, endpoints_links_test.go

**3. `internal/handlers/item_handler_test.go` (1,238 lines → 3 files)**
- Split: item_create_test.go, item_read_test.go, item_update_delete_test.go

**4. `internal/services/temporal_service_test.go` (1,214 lines → 3 files)**
- Split: temporal_workflows_test.go, temporal_activities_test.go, temporal_integration_test.go

**5. `internal/equivalence/handler_test.go` (1,159 lines → 3 files)**
- Split: equivalence_check_test.go, equivalence_resolve_test.go, equivalence_integration_test.go

**Agent Allocation**: 5-10 agents (1-2 per file)

#### Handler Files (6 files - extract by responsibility)

**1. `internal/equivalence/handler.go` (1,310 lines → 3 files)**
- Extract: checker.go, resolver.go, validator.go

**2. Other test files** (5 files at 1,000-1,200 lines each)
- Extract by feature/responsibility

**Agent Allocation**: 6-12 agents (1-2 per file)

---

### Wave 4: Frontend Large Files 🟡 PENDING

**Action Required**: Run source-only scan first
```bash
find frontend/apps -name "*.ts" -o -name "*.tsx" | grep -v node_modules | xargs wc -l | awk '$1 > 500 {print}'
```

**Expected Targets**:
- Large component files → split into subcomponents
- Large page files → split into sections
- Large util files → split by responsibility

**Agent Allocation**: TBD after scan (estimated 10-20 agents)

---

## Phased Execution Plan (WBS + DAG)

### Phase 4.1: main.py Mega-Decomposition (Week 1)

**Dependencies**: Phase 3 complete (✅ DONE)

**Workstreams** (parallel):
1. **Handlers Extraction** (10 agents, 2-4 hours)
   - oauth.py, github.py, chat.py, health.py, device.py
   - auth.py, integrations.py, webhooks.py
   - Dependencies: None (all independent)

2. **Routers Extraction** (10 agents, 3-5 hours)
   - projects.py, items.py, links.py, github.py, oauth.py
   - websocket.py, health.py, integrations.py, chat.py, device.py
   - Dependencies: Handlers complete (for imports)

3. **Middleware Extraction** (4 agents, 1-2 hours)
   - auth.py, cors.py, logging.py, error_handling.py
   - Dependencies: None (all independent)

4. **Integration & Testing** (2 agents, 2-3 hours)
   - Update main.py to use extracted modules
   - Run full test suite
   - Fix import/type errors
   - Dependencies: ALL extractions complete

**Total Effort**: 26 agents, 8-14 hours (parallel: 3-5 hours wall clock)

**Success Gate**: main.py <500 lines, all tests passing

---

### Phase 4.2: Python Large Files (Week 2)

**Dependencies**: Phase 4.1 complete

**Workstreams** (parallel):
1. **Tier 1 Files** (8 agents, 4-6 hours)
   - item_specs.py, spec_analytics_service.py, item.py, param.py
   - Dependencies: None

2. **Tier 2 Files** (24 agents, 3-5 hours)
   - 12 files at 1,000-2,000 lines
   - Dependencies: None

3. **Tier 3 Files** (6 agents, 2-3 hours)
   - 4 files at 500-1,000 lines
   - Dependencies: None

4. **Integration & Testing** (2 agents, 2-3 hours)
   - Run full test suite for each tier
   - Dependencies: Each tier complete

**Total Effort**: 40 agents, 11-17 hours (parallel: 4-6 hours wall clock)

**Success Gate**: 0 Python files >500 lines, all tests passing

---

### Phase 4.3: Go Large Files (Week 3)

**Dependencies**: Phase 4.2 complete (or can run parallel)

**Workstreams** (parallel):
1. **Integration Tests** (10 agents, 2-4 hours)
   - 5 test files → 15 smaller files
   - Dependencies: None

2. **Handler Files** (12 agents, 2-4 hours)
   - 6 handler files → 18 smaller files
   - Dependencies: None

3. **Integration & Testing** (2 agents, 1-2 hours)
   - Run full test suite
   - Dependencies: ALL extractions complete

**Total Effort**: 24 agents, 5-10 hours (parallel: 2-4 hours wall clock)

**Success Gate**: 0 Go files >500 lines (excluding auto-generated), all tests passing

---

### Phase 4.4: Frontend Large Files (Week 4)

**Dependencies**: Phase 4.3 complete (or can run parallel with 4.2/4.3)

**Workstreams** (TBD after scan):
1. **Component Decomposition** (10-15 agents, 3-5 hours)
2. **Page Decomposition** (5-10 agents, 2-4 hours)
3. **Util Decomposition** (5 agents, 1-2 hours)
4. **Integration & Testing** (2 agents, 1-2 hours)

**Total Effort**: 22-32 agents, 7-13 hours (parallel: 3-5 hours wall clock)

**Success Gate**: 0 Frontend files >500 lines, all tests passing

---

## Custom File LOC Enforcement

### Pre-commit Hook (Create New)

**File**: `.git/hooks/pre-commit.d/check-file-size.sh`

```bash
#!/bin/bash
# Phase 4: File size enforcement (<500 lines)

MAX_LINES=500
VIOLATIONS=()

# Python files
while IFS= read -r file; do
    lines=$(wc -l < "$file")
    if [ "$lines" -gt $MAX_LINES ]; then
        VIOLATIONS+=("$file: $lines lines (max: $MAX_LINES)")
    fi
done < <(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

# Go files (exclude auto-generated)
while IFS= read -r file; do
    # Skip auto-generated files
    if [[ "$file" =~ (docs\.go|queries\.sql\.go|\.pb\.go)$ ]]; then
        continue
    fi
    lines=$(wc -l < "$file")
    if [ "$lines" -gt $MAX_LINES ]; then
        VIOLATIONS+=("$file: $lines lines (max: $MAX_LINES)")
    fi
done < <(git diff --cached --name-only --diff-filter=ACM | grep '\.go$')

# TypeScript files
while IFS= read -r file; do
    lines=$(wc -l < "$file")
    if [ "$lines" -gt $MAX_LINES ]; then
        VIOLATIONS+=("$file: $lines lines (max: $MAX_LINES)")
    fi
done < <(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx)$')

# Report violations
if [ ${#VIOLATIONS[@]} -gt 0 ]; then
    echo "❌ FILE SIZE VIOLATIONS:"
    printf '%s\n' "${VIOLATIONS[@]}"
    echo ""
    echo "Files must be <500 lines. Extract modules to fix."
    exit 1
fi

echo "✅ File size check passed (all files <500 lines)"
exit 0
```

---

### CI Check (Add to quality.yml)

```yaml
- name: Check file sizes (<500 lines)
  run: |
    ./scripts/shell/check-file-size-violations.sh
```

---

### Naming Explosion Integration

**Update**: `scripts/shell/check-naming-explosion-python.sh`

Add file size check to existing naming explosion guard:
```bash
# After naming checks, add:
echo "Checking file sizes..."
find src -name "*.py" -exec bash -c 'lines=$(wc -l < "$1"); if [ $lines -gt 500 ]; then echo "$1: $lines lines"; fi' _ {} \;
```

---

## Agent Swarm Strategy (CLAUDE.md Async Orchestration)

### Launch Pattern

**Per Phase**:
1. Launch 20-50 agents in parallel (async swarm)
2. Each agent handles 1 file or 1 module extraction
3. Monitor completion, reawaken on each finish
4. Spawn follow-up agents (integration, testing) as extractions complete
5. Consolidate results when all agents done

**Example Launch (Phase 4.1)**:
```
1. Launch 10 handler extraction agents (parallel)
2. Launch 10 router extraction agents (parallel)
3. Launch 4 middleware extraction agents (parallel)
4. Monitor completion (~3-5 hours wall clock)
5. When ALL complete: launch 2 integration agents
6. When integration complete: launch 2 testing agents
7. When tests pass: mark Phase 4.1 COMPLETE
```

**Monitoring**:
- Track agent completion via task IDs
- Collect extracted modules as they complete
- Run incremental tests per agent
- Consolidate commits when wave complete

---

## Success Criteria

### Phase 4 Complete When:

**Python** ✅:
- [ ] 0 files >500 lines
- [ ] main.py <500 lines (currently 9,768)
- [ ] All 20 large files decomposed
- [ ] All tests passing
- [ ] Zero import errors
- [ ] Zero type errors

**Go** ✅:
- [ ] 0 files >500 lines (excluding auto-generated)
- [ ] All 16 large files decomposed
- [ ] All tests passing
- [ ] golangci-lint green

**Frontend** ✅:
- [ ] 0 files >500 lines
- [ ] All tests passing
- [ ] oxlint green

**Infrastructure** ✅:
- [ ] Pre-commit hook active
- [ ] CI check active
- [ ] Naming explosion guard updated
- [ ] Documentation complete

---

## Risk Assessment

### High Risk ⚠️

**main.py Decomposition**:
- **Risk**: Breaking existing endpoints during extraction
- **Mitigation**: Extract one router at a time, test after each
- **Rollback**: Keep main.py.backup until all tests pass

**Import Cycle Creation**:
- **Risk**: Circular imports between new modules
- **Mitigation**: Use dependency injection, avoid cross-imports
- **Detection**: Run import tests after each extraction

### Medium Risk ⚠️

**Test File Splits**:
- **Risk**: Breaking test discovery or fixtures
- **Mitigation**: Maintain naming conventions, shared fixtures
- **Testing**: Run full test suite after each split

**Type Errors**:
- **Risk**: Type errors from module boundaries
- **Mitigation**: Run mypy after each extraction
- **Fix**: Agents resolve type errors before completing

### Low Risk ✅

**Auto-generated Files**:
- **Risk**: Accidentally modifying auto-generated code
- **Mitigation**: Explicit exclusion in scripts and docs
- **Validation**: Check file headers for generation markers

---

## Rollback Strategy

**Per Wave**:
1. Create branch before wave: `git checkout -b phase_four-wave1`
2. Commit after each agent success
3. If wave fails: `git checkout main && git branch -D phase_four-wave1`
4. If wave succeeds: `git checkout main && git merge phase_four-wave1`

**Per Agent**:
1. Each agent creates backup: `file.py.backup`
2. If agent fails: restore from backup
3. If agent succeeds: delete backup

---

## Timeline and Milestones

### Week 1: main.py Mega-Decomposition
- **Day 1-2**: Handler + Router extraction (20 agents)
- **Day 3**: Middleware extraction (4 agents)
- **Day 4-5**: Integration + Testing (4 agents)
- **Milestone**: main.py <500 lines ✅

### Week 2: Python Large Files
- **Day 1-2**: Tier 1 files (8 agents)
- **Day 3-4**: Tier 2 files (24 agents)
- **Day 5**: Tier 3 files (6 agents)
- **Milestone**: 0 Python files >500 lines ✅

### Week 3: Go Large Files
- **Day 1-3**: Test + Handler files (22 agents)
- **Day 4-5**: Integration + Testing (2 agents)
- **Milestone**: 0 Go files >500 lines ✅

### Week 4: Frontend + Infrastructure
- **Day 1-3**: Frontend files (22-32 agents)
- **Day 4**: Pre-commit hooks + CI
- **Day 5**: Documentation + final verification
- **Milestone**: Phase 4 COMPLETE ✅

**Total Duration**: 4 weeks (28 days)
**Total Agent-Hours**: 136-192 hours
**Wall Clock**: 12-24 hours (with async swarm)

---

## Next Steps

### Immediate (Next 1-2 hours)

1. **User Approval**: Get go-ahead for Phase 4 execution
2. **Create Custom Scripts**:
   - `scripts/shell/check-file-size-violations.sh`
   - Pre-commit hook for file size
3. **Scan Frontend**: Run source-only file size scan
4. **Launch Phase 4.1**: Deploy 26 agents for main.py decomposition

### Short-term (Next 4-8 hours)

1. **Monitor Phase 4.1**: Track handler/router/middleware extraction
2. **Integration Testing**: Verify main.py works with extracted modules
3. **Type Resolution**: Fix any import/type errors
4. **Commit Results**: Consolidate Phase 4.1 commits

### Medium-term (Next 1-2 weeks)

1. **Phase 4.2**: Launch 40 agents for Python large files
2. **Phase 4.3**: Launch 24 agents for Go large files
3. **Phase 4.4**: Launch 22-32 agents for Frontend files
4. **Infrastructure**: Deploy pre-commit hooks and CI checks

---

## Appendix A: Module Extraction Patterns

### Pattern 1: Router Extraction (FastAPI)

**Before** (in main.py):
```python
@app.get("/items/{item_id}")
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
    # implementation
```

**After** (in routers/items.py):
```python
router = APIRouter(prefix="/items", tags=["items"])

@router.get("/{item_id}")
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
    # implementation
```

**main.py**:
```python
from tracertm.api.routers import items
app.include_router(items.router)
```

---

### Pattern 2: Handler Extraction

**Before** (in main.py):
```python
async def complex_handler(request: Request):
    # 200 lines of logic
```

**After** (in handlers/feature.py):
```python
async def handle_feature(request: Request):
    # 200 lines of logic
    # broken into 5 helper functions
```

**main.py**:
```python
from tracertm.api.handlers.feature import handle_feature
```

---

### Pattern 3: Test File Split (Go)

**Before** (service_test.go, 1,500 lines):
```go
func TestServiceAuth(t *testing.T) { ... }
func TestServiceItems(t *testing.T) { ... }
func TestServiceLinks(t *testing.T) { ... }
```

**After** (3 files at ~500 lines each):
- `service_auth_test.go`: All auth tests
- `service_items_test.go`: All item tests
- `service_links_test.go`: All link tests

---

## Appendix B: File Size Violation Report (Current State)

See: `docs/reports/LINTER_ANTIPATTERN_CAPABILITIES.md`

**Summary**:
- Python: 20 files >500 lines (largest: 9,768)
- Go: 16 files >500 lines (excluding auto-generated)
- Frontend: TBD

**Total Violations**: 36+ files

---

**Plan Status**: 🟢 READY FOR EXECUTION
**Next Action**: User approval + Phase 4.1 launch
**Owner**: BMAD Master / Tech Lead
**Estimated Completion**: 2026-02-30 (4 weeks)
