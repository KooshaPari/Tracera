# Work Package Index & Quick Reference (ESCALATED 95-100%)

**Project:** TraceRTM Code Coverage Enhancement to 95-100%
**Previous Target:** 85%+
**New Target:** 95-100% with 100% per-file targets
**Status:** Ready for Agent Execution
**Timeline:** 12 weeks (4 phases, 3 weeks each)
**Total Tests:** 3,400+ (escalated from 1,200)
**Last Updated:** December 8, 2025 (ESCALATION)

---

## ⚠️ SCOPE ESCALATION NOTICE

**What Changed:**
- Target: 85%+ → 95-100% WITH 100% per-file coverage
- Work Packages: 32 → 17 critical + breadth
- Tests: 1,200 → 3,400+ (175% increase)
- Timeline: 8 weeks → 12 weeks
- Agent Specialization: Enabling deep expertise in specific domains

**Why This Document:**
Quick lookup for all 4 agents to find their Phase 1-4 assignments and understand specialization roles.

---

## Quick Reference: Phase 1 - Find Your Assignment

### Phase 1 Overview (Weeks 1-3, 609 Tests, 45% Coverage)

**Critical Path:** 5 files, 100% coverage each (foundation for all other work)

| File | LOC | Tests | Agent | Priority |
|------|-----|-------|-------|----------|
| **item.py** | 1,720 | 172 | Agent 1 (CLI Lead) | CRITICAL |
| **local_storage.py** | 1,712 | 171 | Agent 2 (Storage Lead) | CRITICAL |
| **conflict_resolver.py** | 861 | 86 | Agent 2 (Storage Lead) | HIGH |
| **link.py** | 967 | 97 | Agent 1 (CLI Lead) | HIGH |
| **stateless_ingestion_service.py** | 829 | 83 | Agent 3 (Services Lead) | HIGH |

---

## Agent Specialization Roles

### Agent 1: CLI Lead (21% allocation, 378 hours)

**Owns:** All 30 CLI files in src/tracertm/cli/

**Phase 1 Assignments (269 tests):**
- **WP-1.1:** item.py - Full Coverage (172 tests, 64 hours) ← START HERE
- **WP-1.4:** link.py - Relationship Management (97 tests, 32 hours)

**Phase 2 Assignments (300+ tests):**
- **WP-2.1:** CLI Medium Files (design, project, sync, init, import, test, migrate) - 300+ tests, 96 hours

**Phase 3 Assignments (120+ tests):**
- **WP-3.2:** CLI Simple Files (12 remaining) - 120+ tests, 80 hours

**Phase 4 Assignments (50+ tests):**
- **WP-4.X:** CLI edge cases & integration - 50+ tests

**Total Timeline:** 378 hours across 12 weeks
**Success Metric:** 100% coverage of all CLI layer (30 files)

---

### Agent 2: Storage Lead (22% allocation, 396 hours)

**Owns:** All storage & sync infrastructure (src/tracertm/storage/)

**Phase 1 Assignments (257 tests):**
- **WP-1.2:** local_storage.py - Hybrid Storage (171 tests, 64 hours) ← START HERE
- **WP-1.3:** conflict_resolver.py - Merge Logic (86 tests, 32 hours)

**Phase 2 Assignments (275 tests):**
- **WP-2.3:** Storage Medium Files (sync_engine, markdown_parser, file_watcher) - 275 tests, 96 hours

**Phase 3 Assignments (200+ tests):**
- **WP-3.3:** Storage utilities & helpers - 200+ tests, 80 hours

**Phase 4 Assignments (100+ tests):**
- **WP-4.X:** Storage edge cases & concurrency - 100+ tests

**Total Timeline:** 396 hours across 12 weeks
**Success Metric:** 100% coverage of all storage layer (12 files)

---

### Agent 3: Services Lead (28% allocation, 504 hours)

**Owns:** All service layer (src/tracertm/services/)

**Phase 1 Assignments (83 tests):**
- **WP-1.5:** stateless_ingestion_service.py - Multi-Format Import (83 tests, 32 hours) ← START HERE

**Phase 2 Assignments (350+ tests):**
- **WP-2.2:** Services Medium Files (8 files: item_service, bulk_operation, cycle_detection, chaos_mode, view_registry, project_backup, impact_analysis, advanced_traceability) - 350+ tests, 96 hours

**Phase 3 Assignments (350+ tests):**
- **WP-3.1:** Services Simple Files (59 files) - 350+ tests, 128 hours

**Phase 4 Assignments (150+ tests):**
- **WP-4.X:** Service edge cases & error handling - 150+ tests

**Total Timeline:** 504 hours across 12 weeks
**Success Metric:** 100% coverage of all services layer (70 files)

---

### Agent 4: API/TUI Lead (29% allocation, 522 hours)

**Owns:** API layer, TUI apps, repositories, core infrastructure

**Phase 1 Assignments (0 tests):**
- Coordination & preparation (support agents 1-3)

**Phase 2 Assignments (280 tests):**
- **WP-2.4:** API Layer (client.py, sync_client.py, main.py) - 280 tests, 96 hours ← START IN PHASE 2

**Phase 3 Assignments (293 tests):**
- **WP-3.3:** TUI Apps/Widgets (10 files) - 200+ tests, 80 hours
- **WP-3.4:** Repositories & Core (10 files) - 93 tests, 64 hours

**Phase 4 Assignments (300+ tests):**
- **WP-4.X:** Integration, concurrency, chaos - 300+ tests

**Total Timeline:** 522 hours across 12 weeks
**Success Metric:** 100% coverage of API/TUI/Core layers (33 files)

---

## Workload Balance

| Agent | Hours | Percentage | Role |
|-------|-------|-----------|------|
| Agent 1 | 378 | 21% | CLI Lead |
| Agent 2 | 396 | 22% | Storage Lead |
| Agent 3 | 504 | 28% | Services Lead |
| Agent 4 | 522 | 29% | API/TUI Lead |
| **TOTAL** | **1,800** | **100%** | - |

**Variance:** 12% (well-balanced, no burnout risk)

---

## All 17 Critical Work Packages At a Glance

### PHASE 1: Critical Path (Weeks 1-3) - Target: 45% Coverage, 609 Tests

| WP ID | Title | File | LOC | Tests | Hours | Agent | Start |
|-------|-------|------|-----|-------|-------|-------|-------|
| **1.1** | item.py CLI | src/tracertm/cli/item.py | 1,720 | 172 | 64 | Agent 1 | Week 1 |
| **1.2** | local_storage.py | src/tracertm/storage/local_storage.py | 1,712 | 171 | 64 | Agent 2 | Week 1 |
| **1.3** | conflict_resolver.py | src/tracertm/storage/conflict_resolver.py | 861 | 86 | 32 | Agent 2 | Week 1 |
| **1.4** | link.py CLI | src/tracertm/cli/link.py | 967 | 97 | 32 | Agent 1 | Week 2 |
| **1.5** | stateless_ingestion_service.py | src/tracertm/services/stateless_ingestion_service.py | 829 | 83 | 32 | Agent 3 | Week 2 |

**Phase 1 Totals:** 5 files, 6,089 LOC, 609 tests, 224 hours, 45% coverage

---

### PHASE 2: High-Value Services (Weeks 4-6) - Target: 75% Coverage, 1,500+ Tests

| WP ID | Title | Files | Tests | Hours | Agent | Start |
|-------|-------|-------|-------|-------|-------|-------|
| **2.1** | CLI Medium | design, project, sync, init, import, test, migrate | 300+ | 96 | Agent 1 | Week 4 |
| **2.2** | Services Medium | 8 service files | 350+ | 96 | Agent 3 | Week 4 |
| **2.3** | Storage Medium | sync_engine, markdown_parser, file_watcher | 200+ | 64 | Agent 2 | Week 5 |
| **2.4** | API Layer | client, sync_client, main | 280+ | 64 | Agent 4 | Week 6 |

**Phase 2 Totals:** 20+ files, 1,500+ tests, 320 hours, 75% coverage

---

### PHASE 3: Breadth Coverage (Weeks 7-9) - Target: 90% Coverage, 900+ Tests

| WP ID | Title | Files | Tests | Hours | Agent | Start |
|-------|-------|-------|-------|-------|-------|-------|
| **3.1** | Services Simple | 59 service files <250 LOC | 350+ | 128 | Agent 3 | Week 7 |
| **3.2** | CLI Simple | 12 CLI files | 120+ | 80 | Agent 1 | Week 7 |
| **3.3** | TUI/Widgets | 10 TUI files | 200+ | 80 | Agent 4 | Week 9 |
| **3.4** | Repos & Core | 10 files | 230+ | 64 | Agents 2,4 | Week 9 |

**Phase 3 Totals:** 50+ files, 900+ tests, 352 hours, 90% coverage

---

### PHASE 4: Integration & Polish (Weeks 10-12) - Target: 95-100% Coverage, 400+ Tests

| WP ID | Title | Focus | Tests | Hours | Start |
|-------|-------|-------|-------|-------|-------|
| **4.1** | Integration | Cross-layer workflows | 200 | 80 | Week 10 |
| **4.2** | Error Paths | All errors & boundaries | 100 | 48 | Week 10 |
| **4.3** | Concurrency | Race conditions, stress | 50 | 24 | Week 12 |
| **4.4** | Chaos Mode | Failure scenarios | 50+ | 24 | Week 12 |

**Phase 4 Totals:** All remaining edge cases, 400+ tests, 176 hours, 95-100% coverage

---

## Detailed Assignment Path: Week-by-Week

### Week 1: Phase 1 Foundation

**Agent 1 (CLI Lead):**
- Start WP-1.1: item.py (172 tests, 64 hours)
- Daily standup: Report progress on item.py coverage

**Agent 2 (Storage Lead):**
- Start WP-1.2: local_storage.py (171 tests, 64 hours)
- Parallel: Begin WP-1.3: conflict_resolver.py scoping
- Daily standup: Report progress on hybrid storage tests

**Agent 3 (Services Lead):**
- Start WP-1.5: stateless_ingestion_service.py (83 tests, 32 hours)
- Parallel: Support Agents 1-2 with test infrastructure
- Daily standup: Report progress on ingestion tests

**Agent 4 (API/TUI Lead):**
- Coordination role: Verify all Phase 1 infrastructure ready
- Support: Help with test infrastructure, TEMPLATE.py usage
- Daily standup: Report infrastructure status, any blockers

**Expected Outcome:**
- Week 1: 200+ tests passing (item.py ~30%, local_storage.py ~30%, conflict_resolver.py start)
- Coverage: 12% → 15-20% (from Phase 1 start)

---

### Week 2: Phase 1 Progress

**Agent 1 (CLI Lead):**
- Continue WP-1.1: item.py (finish 172 tests)
- Start WP-1.4: link.py (97 tests)

**Agent 2 (Storage Lead):**
- Continue WP-1.2: local_storage.py (finish 171 tests)
- Continue WP-1.3: conflict_resolver.py (86 tests)

**Agent 3 (Services Lead):**
- Continue WP-1.5: stateless_ingestion_service.py (finish 83 tests)
- Prepare Phase 2 infrastructure

**Agent 4 (API/TUI Lead):**
- Continue coordination
- Prepare Phase 2 API assignments

**Expected Outcome:**
- Week 2: 150+ tests passing (finish item.py, local_storage.py near complete)
- Cumulative Phase 1: 350+ tests (57% of Phase 1)
- Coverage: 15-20% → 25-30%

---

### Week 3: Phase 1 Complete

**Agent 1 (CLI Lead):**
- Finish WP-1.4: link.py (97 tests)
- Prepare Phase 2 CLI medium files

**Agent 2 (Storage Lead):**
- Finish WP-1.3: conflict_resolver.py (86 tests)
- Prepare Phase 2 storage medium files

**Agent 3 (Services Lead):**
- (WP-1.5 already complete from Week 2)
- Prepare Phase 2 services medium files

**Agent 4 (API/TUI Lead):**
- Prepare Phase 2 API assignments

**Expected Outcome:**
- Week 3: 100+ tests passing (link.py, conflict_resolver.py complete)
- Phase 1 Complete: 609 tests passing ✅
- Coverage: 25-30% → 45% (target achieved)
- **All 5 critical files at 100% coverage ✅**

---

## Phase 2-4: High-Level Timeline

### Weeks 4-6: Phase 2 (1,500+ tests, 75% coverage)
- Agent 1: CLI medium files (300+ tests)
- Agent 2: Storage medium (200+ tests)
- Agent 3: Services medium (350+ tests)
- Agent 4: API layer (280+ tests)
- **Target:** 20+ files at 100% coverage

### Weeks 7-9: Phase 3 (900+ tests, 90% coverage)
- Agent 1: CLI simple (120+ tests)
- Agent 2: Support (cross-layer)
- Agent 3: Services simple (350+ tests)
- Agent 4: TUI/Repos (230+ tests)
- **Target:** 50+ files at 100% coverage

### Weeks 10-12: Phase 4 (400+ tests, 95-100% final)
- All agents: Integration, concurrency, chaos, edge cases
- **Target:** All 181 files at 100% coverage

---

## Getting Help During Execution

### My Assignment is Unclear
1. Read your role summary above (Agent 1-4)
2. Check WORK_PACKAGES_AGENTS.md for detailed WP spec
3. Ask in daily standup

### My WP is Blocked
1. Try TEMPLATE.py for reference test
2. Check AGENT_QUICK_START.md (Pattern sections)
3. Escalate in standup immediately
4. See ESCALATION_PROTOCOL.md if SLA missed

### Tests Are Failing
1. Check PRE_STARTUP_VALIDATION.sh output (environment)
2. Compare against TEMPLATE.py examples
3. Review test acceptance criteria in WP spec
4. Ask in standup with specific error

### Coverage Not Increasing
1. Verify test runs: `pytest your_test.py -v`
2. Check coverage: `pytest --cov=src/file/you/test --cov-report=term-with-missing`
3. Find uncovered lines (marked "0")
4. Add specific tests for those lines

---

## Success Checkpoints

### End of Week 2: Phase 1 On Track
- ✅ 350+ tests passing
- ✅ Coverage: 15-20%
- ✅ No Day 1 blockers
- ✅ All agents productive

### End of Week 3: Phase 1 Complete
- ✅ All 609 Phase 1 tests passing
- ✅ 5 critical files at 100% coverage
- ✅ Coverage: 45%
- ✅ Phase 2 ready to start

### End of Week 6: Phase 2 Complete
- ✅ All 1,500+ Phase 2 tests passing
- ✅ 20+ files at 100% coverage
- ✅ Coverage: 75%
- ✅ Strong momentum entering Phase 3

### End of Week 9: Phase 3 Complete
- ✅ All 900+ Phase 3 tests passing
- ✅ 50+ files at 100% coverage
- ✅ Coverage: 90%
- ✅ Home stretch to 95-100%

### End of Week 12: PROJECT COMPLETE ✅
- ✅ All 400+ Phase 4 tests passing
- ✅ **All 181 files at 100% coverage**
- ✅ **Coverage: 95-100% (TARGET ACHIEVED ✅)**
- ✅ **Project ready for release**

---

## Key Differences: Original vs Escalated

| Aspect | Original | Escalated | Change |
|--------|----------|-----------|--------|
| Coverage Target | 85%+ | 95-100% | +15% |
| Per-File Target | Varied | 100% each | Much stricter |
| Total Tests | 1,200 | 3,400+ | +2,200 |
| Total Effort | 800 hours | 1,800 hours | +1,000 hours |
| Timeline | 8 weeks | 12 weeks | +4 weeks |
| Phase 1 WPs | 7 | 5 | More focused |
| Phase 1 Tests | 160 | 609 | +449 tests |

---

## Related Documents

- **WORK_PACKAGES_AGENTS.md** - Detailed specifications for all 17 WPs
- **AGENT_QUICK_START.md** - 1-hour onboarding (includes test patterns)
- **ESCALATED_WORK_PACKAGES_95_100_PERCENT.md** - Comprehensive scope analysis
- **COVERAGE_ESCALATION_TO_100_PERCENT.md** - Why 95-100% and rationale
- **WORK_TICKET_TEMPLATE.md** - Format for status updates
- **COVERAGE_PROGRESS_DASHBOARD.md** - Track weekly progress
- **TEMPLATE.py** - Copy-paste test reference template

---

**Document:** WORK_PACKAGE_INDEX.md (ESCALATED)
**Created:** December 8, 2025
**Status:** ✅ UPDATED FOR 95-100% WITH 100% PER-FILE TARGETS
**Timeline:** 12 weeks | 17 critical WPs | 3,400+ tests
