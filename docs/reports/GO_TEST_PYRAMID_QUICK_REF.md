# Go Test Pyramid - Quick Reference

**Status:** Ready for Implementation | **Date:** 2026-02-06 | **Effort:** 4.25 hours

---

## The Problem (In 30 Seconds)

**Current State:** 3,914 tests (91% unit / 9% integration / 0.3% E2E)
**Target State:** 3,150 tests (70% unit / 20% integration / 10% E2E)

**Issue:** Tests that pass individually fail in integration. High maintenance burden. No critical user journeys tested.

**Solution:**
1. Remove 683 redundant unit tests (-17%)
2. Elevate 160 integration tests to E2E (10 critical journeys)
3. **Result:** Faster execution, higher confidence, lower maintenance

---

## Current vs Target

```
CURRENT (Inverted Pyramid)     TARGET (Healthy Pyramid)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
░░░░░░░░░░░░░░░░░░░░  91%      ▓▓▓▓▓▓▓  10% E2E
░░░░░░░░ 9% Integration         ▓▓▓▓▓▓▓▓▓▓▓▓▓  20% Integration
░░ 0.3% E2E                     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 70% Unit
```

---

## Quick Facts

| Metric | Value |
|--------|-------|
| Test Files | 299 |
| Total Tests | 3,914 |
| Redundant Tests | 683 |
| E2E Gaps | 10 critical journeys |
| Time to Fix | 4.25 hours |
| Execution Time Saved | 50 seconds/run (28% faster) |

---

## Top 5 Consolidation Targets

| Package | Current | Target | Savings |
|---------|---------|--------|---------|
| internal/search | 394 | 260 | 134 |
| internal/services | 427 | 287 | 140 |
| internal/agents | 421 | 280 | 141 |
| internal/handlers | 304 | 220 | 84 |
| internal/graph | 183 | 147 | 36 |
| **5-Package Total** | **1,729** | **1,194** | **535** |

**Pattern:** Each package has 3-4 "comprehensive" test files with 50-90% overlap.

---

## 10 E2E Journeys to Create

| # | Journey | Status | Priority |
|---|---------|--------|----------|
| 1 | Create Project → Add Items → Build Graph | 0 tests | CRITICAL |
| 2 | OAuth Login → Create Project | 0 tests | CRITICAL |
| 3 | Search → Filter → Update Items | 0 tests | HIGH |
| 4 | Graph Analysis & Dependencies | 0 tests | HIGH |
| 5 | Temporal Workflow Execution | 0 tests | MEDIUM |
| 6 | Real-time WebSocket Sync | 0 tests | MEDIUM |
| 7 | Error Recovery & Retry Logic | 0 tests | MEDIUM |
| 8 | Bulk Import Performance | 0 tests | LOW |
| 9 | Security (CSRF/XSS/Rate Limit) | 0 tests | HIGH |
| 10 | Accessibility (Keyboard/Screen Reader) | 0 tests | MEDIUM |

---

## Consolidation by Package (High-Level)

### internal/search (394 → 260 tests, -134)
**Problem:** 12 files with massive overlap
```
DELETE: unit_tests_test.go (29)
DELETE: search_comprehensive_test.go (69) → merge into search_test.go
DELETE: search_extended_test.go (38) → merge into search_test.go
DELETE: search_engine_unit_test.go (36) → merge into search_test.go
REDUCE: search_comprehensive_advanced_test.go (62 → 25)
```
**Action:** 5 files, 2-hour consolidation work

### internal/services (427 → 287 tests, -140)
**Problem:** Each service has 5+ test files (main + transaction + comprehensive + edge_cases + coverage)
```
CONSOLIDATE: *_transaction_test.go (merge into main)
CONSOLIDATE: *_comprehensive_test.go (merge into main)
CONSOLIDATE: *_additional_coverage_test.go (merge into main)
ELEVATE: *_integration_test.go (47 tests → E2E)
```
**Action:** 40+ files, 2.5-hour consolidation work

### internal/agents (421 → 280 tests, -141)
**Problem:** 3 comprehensive files with heavy overlap
```
DELETE: agents_comprehensive_unit_test.go (58 → 30, merge rest)
DELETE: agents_full_coverage_test.go (55 → 30, merge rest)
DELETE: coordinator_comprehensive_test.go (33 → merge)
DELETE: coordination_comprehensive_unit_test.go (53 → 28, merge rest)
ELEVATE: coordinator_integration_test.go (15 → E2E)
ELEVATE: integration_workflows_test.go (14 → E2E)
```
**Action:** 15 files, 1.5-hour consolidation work

### internal/handlers (304 → 220 tests, -84)
**Problem:** Multiple coverage expansion files
```
DELETE: handlers_comprehensive_test.go (38 → merge)
DELETE: handlers_coverage_expansion_test.go (11 → merge)
DELETE: handlers_additional_coverage_test.go (3 → merge)
DELETE: *_coverage_test.go (consolidate into main handler tests)
ELEVATE: handlers_integration_test.go (25 → E2E)
```
**Action:** 20+ files, 1-hour consolidation work

### Others (5 packages, -115 tests)
```
internal/graph: 183 → 147 (-36)
internal/equivalence: 183 → 155 (-28)
internal/cache: 75 → 68 (-7)
internal/middleware: 71 → 64 (-7)
internal/repository: 72 → 60 (-12)
```
**Action:** General 10-15% cleanup across all packages

---

## Execution Phases (4.25 hours total)

### Phase 1: Plan (30 min)
- [ ] Review consolidation targets
- [ ] Map all overlapping tests
- [ ] Create merge strategy per package

### Phase 2: Execute (2 hours)
- [ ] search (30 min) - merge 4 comprehensive files
- [ ] services (40 min) - consolidate all service test files
- [ ] agents (30 min) - merge 3 comprehensive files
- [ ] handlers (20 min) - merge coverage files

### Phase 3: Elevate (1 hour)
- [ ] Create 10 E2E tests (40 min)
- [ ] Integrate with CI (15 min)
- [ ] Document patterns (5 min)

### Phase 4: Verify (45 min)
- [ ] Run full test suite (15 min)
- [ ] Check coverage (10 min)
- [ ] Benchmark time (10 min)
- [ ] Sign-off (10 min)

---

## Success Criteria

- [ ] Total tests: 3,914 → 3,150 (-764, -20%)
- [ ] Unit tests: 3,564 → 2,500 (-1,064, -30%)
- [ ] Integration tests: 339 → 500 (+161, +48%)
- [ ] E2E tests: 11 → 150 (+139, +1,264%)
- [ ] All tests pass (no regressions)
- [ ] Execution time: 180s → 130s (-28%)
- [ ] Code review: 30% easier (fewer duplicates)

---

## Key Files

**Main Report:** `docs/reports/GO_PYRAMID_REBALANCE_PLAN.md`
- Complete analysis with all metrics
- Risk mitigation strategies
- Phase-by-phase implementation plan

**Implementation Details:** `docs/reports/GO_CONSOLIDATION_DETAILS.md`
- File-by-file consolidation mapping
- Merge strategies for each package
- E2E test specifications

**Quick Ref:** This file (`GO_TEST_PYRAMID_QUICK_REF.md`)
- At-a-glance summary
- Execution checklist
- Quick facts

---

## Common Questions

**Q: Will consolidation remove important tests?**
A: No. Redundant means the same scenario tested 5+ times. We keep all unique scenarios, remove duplicates.

**Q: How do I know which tests to keep?**
A: See `GO_CONSOLIDATION_DETAILS.md` for package-by-package merge strategy.

**Q: What about test discovery/naming?**
A: Consolidation improves this. Fewer files, clearer naming (e.g., `search_edge_cases_test.go` for all edge cases).

**Q: Will E2E tests slow down CI?**
A: No. E2E tests run in parallel. Plus, consolidated unit tests execute 28% faster overall.

**Q: Can I revert consolidation?**
A: Yes. All work tracked in git. Can revert any consolidation if issues arise.

---

## Next Steps

1. **Read** `GO_PYRAMID_REBALANCE_PLAN.md` (full analysis)
2. **Review** `GO_CONSOLIDATION_DETAILS.md` (implementation plan)
3. **Discuss** with team (30 min sync)
4. **Execute** Phase 1 (30 min planning)
5. **Consolidate** Phase 2 (2 hours)
6. **Elevate** Phase 3 (1 hour)
7. **Verify** Phase 4 (45 min)

**Total Effort:** 4.25 hours wall-clock
**ROI:** 28% faster tests, 30% easier reviews, 100% more E2E coverage

---

**Status:** Ready to Execute | **Decision:** Approve Consolidation Plan
