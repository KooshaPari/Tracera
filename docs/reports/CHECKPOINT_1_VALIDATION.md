# Phase 5 Checkpoint 1: Validation Procedures

**Status:** ACTIVE - 2026-02-06 02:30 UTC (T+15 minute checkpoint)
**Expected Reports:** 3 agents (Tasks #6, #7, #8) reporting Phase 1 completion

---

## VALIDATION CHECKLIST

### For Coordinator (visual-regression-architect)

Upon receipt of Phase 1 completion reports from all 3 agents, execute:

#### Step 1: Frontend Compilation Check
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
bun run build

# Expected output:
# ✅ Build succeeds with no errors
# ✅ No TypeScript errors in Gap 5.3 / 5.5 changes
```

**Acceptance:** Build completes without errors

#### Step 2: Backend Compilation Check
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend

# Check Go build
go build ./internal/cliproxy
go build ./internal/temporal

# Expected output:
# ✅ Go build succeeds (no undefined references, no interface mismatch)
# ✅ All imports resolve correctly
```

**Acceptance:** All Go packages build without errors

#### Step 3: Python Module Check
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/python

# Check syntax and imports
python3 -m py_compile src/tracertm/temporal/activities.py
python3 -m py_compile src/tracertm/temporal/workflows.py

# Expected output:
# ✅ No syntax errors
# ✅ All imports available
```

**Acceptance:** Python modules compile without errors

#### Step 4: Acknowledgment & Phase 2 Clearance

Once all 3 compilation checks pass:

```bash
# Send individual acknowledgments to each agent
# (see ACKNOWLEDGMENT MESSAGES section below)

# Timeline update:
# ✅ Checkpoint 1 VALIDATED
# ✅ Clear all 3 agents to Phase 2
# ✅ Update TaskList with Phase 2 metadata
# ✅ Notify team-lead of Phase 2 transition
```

---

## EXPECTED PHASE 1 COMPLETIONS

### Gap 5.3 (integration-tests-architect) - Task #6
**Phase 1 Report Should Include:**
- ✅ MSW handlers added to mocks/handlers.ts
  - Endpoints: GET /api/v1/reports/templates, GET /api/v1/search, POST /api/v1/reports/export
- ✅ Test data extended in mocks/data.ts
  - mockReports, mockItems, mockSearch arrays populated
- ✅ Files modified: 2 (handlers.ts, data.ts)
- ✅ Files created: 0
- ✅ Tests still skipped (Step 2-5 pending in Phase 2-4)

**Verification:**
- [ ] Check `frontend/apps/web/src/__tests__/mocks/handlers.ts` contains 3 new routes
- [ ] Check `frontend/apps/web/src/__tests__/mocks/data.ts` contains mockReports + mockItems
- [ ] Confirm TypeScript compilation passes (bun run build)

### Gap 5.4 (general-purpose) - Task #7
**Phase 1 Report Should Include:**
- ✅ activities.go created with 3 activity functions
  - QuerySnapshot(ctx, sessionID string) → SnapshotMetadata
  - CreateSnapshot(ctx, sessionID, data) → snapshotID string
  - UploadSnapshot(ctx, snapshotID, tarPath) → storageURL string
- ✅ workflows.go started (placeholder structure)
- ✅ Files created: 2 (activities.go, workflows.go skeleton)
- ✅ Files modified: 0 in Phase 1

**Verification:**
- [ ] Check `backend/internal/temporal/activities.go` exists and compiles
- [ ] Check `backend/internal/temporal/workflows.go` exists (skeleton)
- [ ] Confirm Go build passes: `go build ./internal/temporal`

### Gap 5.5 (general-purpose) - Task #8
**Phase 1 Report Should Include:**
- ✅ tableTestItems array created in testData.ts
  - 10+ items with varied types (feature, bug, requirement), status (open, in_progress, done), priority (high, medium, low)
- ✅ API handlers added for items endpoint
- ✅ Files modified: 2 (testData.ts, handlers.ts)
- ✅ Files created: 0

**Verification:**
- [ ] Check `frontend/apps/web/src/__tests__/mocks/data.ts` contains tableTestItems with 10+ items
- [ ] Check `frontend/apps/web/src/__tests__/mocks/handlers.ts` contains items endpoint handler
- [ ] Confirm TypeScript compilation passes (bun run build)

---

## ACKNOWLEDGMENT MESSAGES

Once all compilations pass, send these confirmations:

### Message to integration-tests-architect (Gap 5.3)
```
✅ Checkpoint 1 VALIDATED

Phase 1 Status: COMPLETE
- MSW handlers: 3 endpoints added
- Test data: mockReports + mockItems populated
- Compilation: ✅ PASS (bun run build)

Clear to Phase 2:
1. Add global cleanup in setup.ts
2. Implement async test helpers (waitForData, etc)
3. Re-enable 8 integration tests
4. Verify 5x flake-free runs

Timeline: Phase 2 start T+20 min, complete T+45 min
Awaiting Phase 2 completion report.
```

### Message to general-purpose (Gap 5.4)
```
✅ Checkpoint 1 VALIDATED

Phase 1 Status: COMPLETE
- activities.go: 3 activities created (Query, Create, Upload)
- workflows.go: Skeleton structure in place
- Compilation: ✅ PASS (go build ./internal/temporal)

Clear to Phase 2:
1. Complete workflows.go with retry policies
2. Implement test setup for Temporal
3. Wire service.go integration
4. Run 1 temporal test

Timeline: Phase 2 start T+20 min, complete T+50 min
Awaiting Phase 2 completion report.
```

### Message to general-purpose (Gap 5.5)
```
✅ Checkpoint 1 VALIDATED

Phase 1 Status: COMPLETE
- tableTestItems: 10+ items with varied types/status/priority
- API handlers: items endpoint added
- Compilation: ✅ PASS (bun run build)

Clear to Phase 2:
1. Add fixture setup in global setup
2. Re-enable 6 accessibility tests
3. Run WCAG validation with jest-axe
4. Verify keyboard navigation

Timeline: Phase 2 start T+20 min, complete T+40 min
Awaiting Phase 2 completion report.
```

### Message to team-lead (Coordination Update)
```
**Checkpoint 1 COMPLETE**

✅ All Phase 1 compilations verified:
- Frontend (Gap 5.3, 5.5): bun run build PASS
- Backend (Gap 5.4): go build ./internal/temporal PASS
- All modules compile without errors

✅ All 3 agents cleared to Phase 2:
- Gap 5.3: Start cleanup + async helpers (15 min)
- Gap 5.4: Complete workflows + service wiring (20 min)
- Gap 5.5: Add fixtures + WCAG validation (15 min)

**Timeline Update:**
- T+15 min: Checkpoint 1 COMPLETE ✓
- T+20 min: All Phase 2s start in parallel
- T+40-50 min: Phase 2 completion (all tests ready)
- T+60 min: Checkpoint 2 + transition to Phase 3

**Wave 1 Status** (Gaps 5.1-5.2):
- visual-regression-implementer: Fully deployed, executing in parallel
- Gap 5.1: Un-skip tests + visual specs (~30 min, T+0 to T+30)
- Gap 5.2: Event publisher + JetStream (~25 min, T+0 to T+25)
- Expected Wave 1 completion: T+30 min

**Next Actions:**
1. Monitor Phase 2 progress (checkpoint T+35 min)
2. Receive Wave 1 completion report (~T+30 min)
3. Prepare Wave 3 trigger (when Gap 5.4 test passes, expect T+50 min)
```

---

## COMPILATION CHECK COMMANDS (Quick Reference)

```bash
# Frontend
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend && bun run build

# Backend
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend && \
  go build ./internal/cliproxy && \
  go build ./internal/temporal

# Python
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/python && \
  python3 -m py_compile src/tracertm/temporal/activities.py && \
  python3 -m py_compile src/tracertm/temporal/workflows.py
```

---

## EXPECTED TIMING

| Checkpoint | Time | Action |
|-----------|------|--------|
| **Checkpoint 1** | T+15 min | Compile checks + Phase 2 clearance (NOW) |
| **Checkpoint 2** | T+35-40 min | Phase 2 completion + Phase 3 start |
| **Checkpoint 3** | T+50-60 min | Phase 3 completion + validation phase |
| **Checkpoint 4** | T+70 min | All tests passing + final commits |

---

## NEXT ACTIONS (Coordinator)

1. **Await Phase 1 Reports** - 3 agents will report via message
2. **Run Compilation Checks** - Execute commands above
3. **Send Acknowledgments** - Use messages above for each agent
4. **Update Tasks** - Mark Phase 2 start with TaskUpdate
5. **Monitor Wave 1** - visual-regression-implementer should also report progress

**Status:** Standing by for Phase 1 reports from all 3 agents.

