# Phase 3: Production Blockers Remediation Plan

**Duration:** 24h wall-clock (43-56h effort)
**Critical Path:** Phase 3.4 Sync Engine (24h) - blocks all downstream phases
**Execution Model:** Parallel Phase 3.1-3.3 (9h total), concurrent with Phase 3.4 (24h), with parallel support work

## Phase 3.1: Authentication System (6-9h effort, 1-2h wall-clock)

### Objectives
1. Remove WorkOS mocks and replace with real auth handler
2. Implement complete OAuth flow with state management
3. Integrate with session service and database
4. Add comprehensive auth tests

### Tasks
**T3.1.1: Remove WorkOS Mocks (1h)**
- Files: `frontend/apps/web/src/__tests__/mocks/handlers.ts` (already added basic handlers in Phase 1)
- Remove all WorkOS-specific mock responses
- Keep auth handler structure intact

**T3.1.2: Implement Auth Handler (2h) - CRITICAL**
- File: `backend/internal/handlers/auth_handler.go` (new)
- Implement:
  - `HandleLogin()` - email/password validation
  - `HandleLogout()` - session cleanup
  - `HandleRefresh()` - JWT refresh logic
  - `HandleGetUser()` - current user profile
- Integration: Wire to session_service (Phase 4.1)

**T3.1.3: Wire Auth Routes (1h)**
- File: `backend/internal/routes/auth.go` (new)
- Register routes:
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/logout`
  - `POST /api/v1/auth/refresh`
  - `GET /api/v1/auth/user`

**T3.1.4: Add Auth Tests (2-4h)**
- File: `backend/internal/handlers/auth_handler_test.go` (new)
- Test coverage:
  - Valid login/logout flow
  - Invalid credentials
  - Token refresh
  - Session expiry
  - Rate limiting (if applicable)

### Success Criteria
- ✅ All auth endpoints return proper responses
- ✅ Session service integration verified
- ✅ 90%+ test coverage for auth handler
- ✅ End-to-end auth flow working

---

## Phase 3.2: Handler Registration (4-6h effort, 2h wall-clock)

### Objectives
1. Wire all existing handler implementations to routes
2. Verify 100% of API endpoints are registered
3. Add missing handler implementations
4. Test all routes with proper mocks

### Tasks
**T3.2.1: Handler Inventory (1h)**
- Search: `grep -r "func Handle" backend/internal/handlers/ --include="*.go" | wc -l`
- Expected: 40+ handlers
- Create list of handlers with their routes

**T3.2.2: Wire Existing Handlers (2h)**
- Files: `backend/internal/routes/[*.go]`
- For each handler:
  - Verify route registration
  - Check middleware application
  - Validate auth requirements
- Focus on: API keys, projects, items, graphs, storage endpoints

**T3.2.3: Implement Missing Handlers (2h)**
- From handler inventory, identify missing implementations
- Typical gaps: DELETE routes, batch operations, admin endpoints
- Create placeholder implementations with proper error responses

**T3.2.4: Add Route Tests (2h)**
- File: `backend/internal/routes/routes_test.go` (new)
- Test:
  - All routes registered
  - Correct HTTP methods
  - Auth middleware applied
  - 404 on invalid routes

### Success Criteria
- ✅ 100% of handlers registered and callable
- ✅ All routes have tests
- ✅ No orphaned handler functions
- ✅ Full route coverage map generated

---

## Phase 3.3: API Type Safety (6-9h effort, 3h wall-clock)

### Objectives
1. Complete OpenAPI specification
2. Set up codegen for TypeScript client
3. Replace manual type definitions with generated types
4. Add API contract tests

### Tasks
**T3.3.1: Complete OpenAPI Spec (2-3h)**
- File: `docs/openapi.yaml` or `backend/api/openapi.json`
- Add all endpoints with:
  - Request/response schemas
  - Auth requirements
  - Error responses
  - Proper type definitions
- Coverage: auth, projects, items, graphs, storage, admin

**T3.3.2: Set Up Codegen (1h)**
- Tool: OpenAPI Generator or similar
- Configuration: TypeScript fetch client
- Script: `npm run generate:api` in package.json
- Output directory: `frontend/apps/web/src/api/generated/`

**T3.3.3: Replace Manual Types (2-3h)**
- Files: `frontend/apps/web/src/api/*.ts`
- Replace manual type definitions with generated types
- Update all API calls to use generated client
- Remove outdated type files (keep generated folder only)

**T3.3.4: Add API Contract Tests (2h)**
- File: `backend/api/contract_test.go` (new)
- Test:
  - All endpoints match OpenAPI spec
  - Response formats correct
  - Status codes match spec
  - Auth requirements enforced

### Success Criteria
- ✅ OpenAPI spec 100% complete
- ✅ Codegen working and reproducible
- ✅ All API types from generated code
- ✅ Zero manual type definitions
- ✅ API contract tests passing

---

## Phase 3.4: Sync Engine Completion (24h effort, 24h wall-clock) 🔴 CRITICAL PATH

### Objectives
1. Complete all 4 TODO stubs in sync engine
2. Full end-to-end sync testing
3. Production-ready state management
4. Comprehensive error handling

### Files & TODOs

**File:** `src/tracertm/storage/sync_engine.py`

**T3.4.1: Change Detection (8h) - Line 621**
```python
# TODO: Implement change detection logic
# Current: Empty stub at line 621
```
**Implementation:**
- Compare current state vs baseline (using semantic diff)
- Detect: additions, deletions, modifications
- Handle: nested structures, arrays, complex types
- Performance: <100ms for typical payloads
- Testing: 15+ unit tests for edge cases

**T3.4.2: Pull Logic (4h) - Line 704**
```python
# TODO: Implement pull synchronization
# Current: Empty stub at line 704
```
**Implementation:**
- Fetch remote state (from server/API)
- Merge with local state (3-way merge with last-known-good)
- Handle: conflicts, partial updates, network errors
- Testing: 8+ unit tests

**T3.4.3: Application Logic (4h) - Line 781**
```python
# TODO: Implement state application
# Current: Empty stub at line 781
```
**Implementation:**
- Apply changes to local state
- Transaction semantics (all-or-nothing)
- Undo/rollback support
- Testing: 10+ unit tests

**T3.4.4: Conflict File Creation (2h) - Line 813**
```python
# TODO: Implement conflict file handling
# Current: Empty stub at line 813
```
**Implementation:**
- Create `.conflict` files for unresolved conflicts
- Include: original, remote, local versions
- User-readable format
- Testing: 5+ unit tests

**T3.4.5: Comprehensive Testing (6h)**
- End-to-end sync tests: 10 scenarios
- Integration with storage layer
- Performance benchmarks
- Error recovery tests

### Code Structure Reference

```python
class SyncEngine:
    def detect_changes(self, current, baseline):
        """T3.4.1: Implement change detection"""
        # Lines 621-650: Implementation here
        pass

    def pull(self, remote_state, merge_strategy='three-way'):
        """T3.4.2: Implement pull synchronization"""
        # Lines 704-740: Implementation here
        pass

    def apply_changes(self, changes, state):
        """T3.4.3: Implement state application"""
        # Lines 781-810: Implementation here
        pass

    def handle_conflicts(self, conflicts, output_dir):
        """T3.4.4: Implement conflict file creation"""
        # Lines 813-830: Implementation here
        pass
```

### Dependencies
- None - isolated module
- Blocks: Frontend state management (#3.5), Route implementations (#3.6), Integration tests (#3.7)

### Success Criteria
- ✅ All 4 TODOs implemented with full functionality
- ✅ 35+ sync tests passing
- ✅ Edge cases handled (network errors, conflicts, timeouts)
- ✅ Performance <100ms for typical payloads
- ✅ Production-ready error messages

---

## Parallel Work During Phase 3.4 (Phase 3.5-3.7)

While Phase 3.4 (24h) executes, run these tasks in parallel:

### Phase 3.5: Frontend State Updates (3h)
- Integrate SyncEngine with React state
- Update useItems, useProjects hooks
- Add sync status UI
- Parallel with Phase 3.4

### Phase 3.6: Route Implementations (4h)
- Implement placeholder route handlers
- Add proper error responses
- Wire to services
- Parallel with Phase 3.4

### Phase 3.7: Integration Tests (5h)
- Full-stack sync tests
- Auth + sync flow
- Error recovery scenarios
- Can start after Phase 3.1 auth complete

---

## Execution Schedule

```
Time    │ Phase 3.1 (Auth) │ Phase 3.2 (Handlers) │ Phase 3.3 (API) │ Phase 3.4 (Sync) │ Phase 3.5-7 (Parallel)
─────────┼──────────────────┼─────────────────────┼─────────────────┼──────────────────┼──────────────────────
0:00-1:00│ T1 (1h) ✓ remove │ ───────────────────── │ ──────────────── │ T1 (START)       │ (waiting for Phase 3.1)
1:00-2:00│ T2 (2h) ✓ auth  │ ───────────────────── │ ──────────────── │ T1 (8h)          │ (waiting for Phase 3.1)
2:00-3:00│ T3+T4 (1-4h)    │ T1 (START, 1h)       │ (waiting)       │ T1 (8h)          │ (waiting for Phase 3.1)
3:00-4:00│ ✓ DONE          │ T2 (2h)              │ T1 (START, 2-3h)│ T1 (8h)          │ T1 T2 (START, 3h)
4:00-5:00│                 │ T3 (2h)              │ T1 (2-3h)       │ T2 (4h)          │ T1 T2 (3h)
...      │                 │ T4 (2h)              │ T2-T4 (continue)│ T2 T3 T4 T5 (24h)│ T3 T4 T5 (continue)
24:00    │                 │ ✓ DONE (2h)         │ ✓ DONE (3h)    │ ✓ DONE (24h)    │ ✓ DONE (parallel)
```

---

## Risk Mitigation

### Critical Path Risk: Sync Engine (Phase 3.4)

**Risk:** 24h sequential task blocks downstream work

**Mitigation:**
1. **Checkpoints:** Save progress every 4h with git commits
2. **Modularity:** Each TODO stub is independent - can be completed in any order
3. **Testing:** Unit tests for each TODO before moving to next
4. **Fallback:** If one stub stuck, move to next and return (parallel development)
5. **Code Review:** Each TODO stub reviewed for correctness before integration

**Checkpoint Schedule:**
- T+4h: T3.4.1 (change detection) complete
- T+8h: T3.4.2 (pull logic) complete
- T+12h: T3.4.3 (application logic) complete
- T+14h: T3.4.4 (conflicts) complete
- T+24h: T3.4.5 (testing) complete

### Parallel Work Risks

**If Phase 3.1 Auth blocks:**
- Skip Phase 3.7 integration tests
- Focus on Phase 3.5-3.6 (frontend state, routes)
- Return to auth after sync engine basics done

**If Phase 3.2 Handler registration blocks:**
- Phase 3.6 route implementations may have wrong signatures
- Verify API contract (Phase 3.3) first to stabilize signatures

---

## Validation & Handoff

After Phase 3 complete:

```bash
# Full system health check
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace

# Auth flow
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
# Expected: JWT token in response

# Sync engine
cd src && pytest tracertm/storage/test_sync_engine.py -v
# Expected: 35+ tests passing

# API validation
cd backend && go test ./internal/routes/... -v
# Expected: All route tests passing

# Integration
make test:integration
# Expected: Auth + sync flow working end-to-end
```

---

## Next Phase: Phase 4 (Test Infrastructure Recovery)

After Phase 3 complete, move to Phase 4:
- Timing/async fixes (8-10h)
- React Query fixes (6-8h)
- Graph layout fixes (6-8h)
- Mock infrastructure (4-6h)

**Phase 4 Target:** 536 → 50 failing tests, 95%+ pass rate

---

**Document Status:** Ready for Phase 3 dispatch (awaiting Phase 1-2 completion and gate validation)
