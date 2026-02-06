# Backend Go Coverage - Quick Reference
**Updated:** 2026-02-06

## At a Glance

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Overall Coverage | 27.6% | 85% | 🔴 CRITICAL |
| Test Functions | 3,271 | 3,200 | ✅ OK |
| Unit Test % | 96.2% | 70% | ⚠️ IMBALANCED |
| Failing Tests | 26 | 0 | 🔴 CRITICAL |

## Red Flags

1. **Build Failure:** `services/*` (cannot compile)
2. **Panic Test:** `search/cross_perspective_search_test.go:312` (index out of range)
3. **Zero Coverage:** `agents/*` (68 functions untested)
4. **Low Coverage:** `temporal` (40%), `websocket` (63%), `storage` (18%)

## Highest Priority (Must Fix Now)

### Phase 1: Blockers (30-45 min)

```bash
# 1. Fix services build
cd backend && go build ./internal/services/...

# 2. Fix search panic
# File: internal/search/cross_perspective_search_test.go:312
# Issue: Empty slice mock
# Fix: Add test data fixtures

# 3. Fix storybook assertion
# File: internal/storybook/client_test.go:52
# Issue: "storybook" vs "Storybook" case
# Fix: Update expected string
```

### Phase 2: Critical Gaps (90-120 min)

| Package | Coverage | Gap | New Tests |
|---------|----------|-----|-----------|
| agents | 0% | -85% | 65 unit + 15 integration |
| search | 34% | -51% | 25-30 unit + 5 integration |
| storage | 18% | -67% | 40-50 unit |
| embeddings | 79% | -6% | 12-15 unit |
| integrations | 77% | -8% | 15-20 unit |

## Commands

### Run Coverage Report
```bash
cd backend
go test ./... -coverprofile=coverage.out -covermode=atomic
go tool cover -func=coverage.out | grep -E "^github" | head -50
go tool cover -html=coverage.out -o coverage.html
```

### Find Low Coverage Packages
```bash
go tool cover -func=coverage.out | awk '{print $(NF), $0}' | sort -n | head -30
```

### Test Specific Package
```bash
go test ./internal/agents/... -v -cover
go test ./internal/search/... -v -cover
```

## Team Assignments

### Wave 1 (Parallel - 90 min)
- **Team 1:** agents/* (coordinator, coordination, distributed_coordination)
  - 65 unit tests + 15 integration tests
- **Team 2:** search + storage modules
  - Fix panic + add 45 tests
- **Team 3:** embeddings + integrations
  - 35 tests total (15 + 20)
- **Team 4:** websocket + temporal
  - 90 tests total (40 + 50)

### Expected Outcomes
- **After Phase 1 (30 min):** All tests passing
- **After Phase 2 (120 min):** 150+ new tests, ~45% coverage
- **After Phase 3 (120 min):** 70/20/10 pyramid, ~60% coverage
- **After Phase 4 (60 min):** 85% coverage, all critical paths tested

## Coverage Targets by Package

### Critical (Must be 85%+)

```
agents/*                    0%  → 85% (BLOCKING)
search/                    34%  → 85% (BLOCKING - PANIC)
services/*         [BUILD FAILED]→ Fix, then 85%
embeddings/                79%  → 85% (5.6% gap)
integrations/              77%  → 85% (8.2% gap)
handlers/                  81%  → 85% (3.7% gap)
```

### High Priority (85%+ needed)

```
temporal/                  40%  → 85% (44.8% gap)
websocket/                 63%  → 85% (21.7% gap)
storage/                   18%  → 85% (66.5% gap)
sessions/                  28%  → 85% (56.2% gap)
vault/                     28%  → 85% (56.9% gap)
```

### Already Excellent (85%+)

```
tx/context                100%  ✓
validation/               100%  ✓
tracing/                  100%  ✓
uuidutil/                 87%   ✓
```

## Test Pyramid Rebalancing

### Current (IMBALANCED)
```
Unit:        3,151 tests (96.2%)
Integration:  120 tests (3.7%)
E2E:            0 tests (0.1%)
```

### Target (HEALTHY)
```
Unit:        2,289 tests (70%)
Integration:  655 tests (20%)
E2E:          327 tests (10%)
```

### Action Items
1. **Consolidate redundant unit tests** (-862 tests)
2. **Add integration tests** (+535 tests)
3. **Add E2E tests** (+327 tests)

## Failure Analysis

```
Search Package:
  cross_perspective_search_test.go:312 - Panic
  Cause: Empty slice returned by mock
  Fix: Add test data fixtures

Services Package:
  Build failed (import/syntax error)
  Cause: Unknown - needs investigation
  Fix: Debug build errors

Storybook Package:
  client_test.go:52 - Message mismatch
  Expected: "Storybook base URL is required"
  Actual: "storybook base URL is required"
  Fix: Update test assertion (capitalize S)
```

## Success Criteria

- [ ] All tests passing: `go test ./... -v` (no failures)
- [ ] Coverage ≥85%: `go tool cover -func=coverage.out | tail -1`
- [ ] Pyramid 70/20/10: Unit 2,289, Integration 655, E2E 327
- [ ] Critical paths 100%: agents/*, search, storage, handlers
- [ ] Build time <5 min: `time go test ./...`

## Documentation

**Full Report:** `/docs/reports/BACKEND_GO_QUALITY_AUDIT_2026-02-06.md`

Contains:
- Detailed package breakdown
- Phased remediation plan
- Test specifications
- Success metrics
- Root cause analysis
