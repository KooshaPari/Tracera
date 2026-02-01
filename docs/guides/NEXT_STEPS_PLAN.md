# Next Steps Plan - Test Coverage & Quality

## Overview
Comprehensive plan to achieve 100% test coverage and fix quality issues across backend and frontend.

---

## 🎯 Backend Next Steps

### Phase 1: Fix Compilation Issues (Priority: HIGH)
**Status**: ✅ Mostly resolved (user fixed many issues)

#### Remaining Issues
1. **internal/embeddings**
   - ✅ Fixed: Removed duplicate test functions
   - ✅ Fixed: Removed unused imports
   - ⏳ Verify: All tests compile and run

2. **internal/nats**
   - ✅ Fixed: Renamed duplicate `TestDefaultConfig` to `TestDefaultConfig_Coverage`
   - ⏳ Verify: No remaining duplicate test names

3. **internal/infrastructure**
   - ✅ Fixed: Renamed test functions to avoid conflicts
   - ⏳ Verify: All tests compile

4. **internal/handlers**
   - ✅ Fixed: Removed unused imports
   - ⏳ Verify: Tests compile and run

#### Actions
```bash
# Verify all packages compile
cd backend
go test ./internal/embeddings/... ./internal/handlers/... ./internal/infrastructure/... ./internal/nats/...

# Check for any remaining compilation errors
go build ./internal/...
```

### Phase 2: Complete Integration Tests (Priority: HIGH)
**Status**: ⏳ In Progress

#### Packages Needing Integration Tests

1. **internal/search** (6.8% → Target: 100%)
   - Current: Unit tests + integration stubs
   - Needed: Real `*pgxpool.Pool` tests using testcontainers
   - Files: `search_integration_test.go`, `indexer_test.go`
   - Pattern: Follow `internal/db/migrations_test.go` example

2. **internal/graph** (0.0% → Target: 100%)
   - Current: Test structure ready
   - Needed: Full integration tests with testcontainers
   - Files: `graph_test.go`

3. **internal/db** (60-70% → Target: 100%)
   - Current: Scanner tests + migrations integration tests
   - Needed: Tests for `queries.sql.go` functions
   - Pattern: Use testcontainers for PostgreSQL

4. **internal/repository** (80-90% → Target: 100%)
   - Current: Unit tests with SQLite
   - Needed: Integration tests with PostgreSQL
   - Pattern: Use testcontainers

#### Actions
```bash
# Create integration test structure
# Follow pattern from internal/db/migrations_test.go

# Example structure:
#go:build integration

package search

import (
    "testing"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestSearchEngine_Integration(t *testing.T) {
    // Setup testcontainers PostgreSQL
    // Run actual search tests
}
```

### Phase 3: Coverage Verification (Priority: MEDIUM)
**Status**: ⏳ Pending

#### Actions
```bash
# Generate coverage report
cd backend
go test -coverprofile=coverage.out ./internal/...

# View coverage
go tool cover -html=coverage.out

# Check coverage per package
go test -cover ./internal/search/...
go test -cover ./internal/db/...
go test -cover ./internal/graph/...
go test -cover ./internal/repository/...
go test -cover ./internal/embeddings/...
go test -cover ./internal/handlers/...
go test -cover ./internal/infrastructure/...
go test -cover ./internal/nats/...
go test -cover ./internal/services/...
```

---

## 🎨 Frontend Next Steps

### Phase 1: Fix Failing Tests (Priority: HIGH)
**Status**: 2 tests failing (98.2% pass rate)

#### Issues
1. **src/__tests__/api/links.test.ts**
   - Problem: `expect(linksApi.list).toHaveBeenCalledWith(undefined)` fails
   - Fix: Change to `expect(linksApi.list).toHaveBeenCalledWith()`

2. **src/__tests__/api/projects.test.ts**
   - Problem: Same issue as above
   - Fix: Change to `expect(projectsApi.list).toHaveBeenCalledWith()`

#### Actions
```bash
cd frontend/apps/web

# Fix the tests
# Edit src/__tests__/api/links.test.ts
# Edit src/__tests__/api/projects.test.ts

# Verify fix
npm test -- --run
```

### Phase 2: Fix Coverage Generation (Priority: HIGH)
**Status**: Coverage generation failing

#### Issue
- Error: `ENOENT: no such file or directory, open 'coverage/.tmp/coverage-10.json'`
- Target: 95% coverage for all metrics

#### Actions
```bash
cd frontend/apps/web

# Create coverage directory
mkdir -p coverage/.tmp

# Run coverage
npm test -- --run --coverage

# View coverage report
open coverage/index.html
```

### Phase 3: Fix Linting Issues (Priority: MEDIUM)
**Status**: 518 errors, 648 warnings

#### Top Issues
1. **Unused Imports** (FIXABLE)
   - Auto-fix: `npm run lint:fix`
   - Manual: Remove unused imports

2. **Explicit `any` Types** (SUSPICIOUS)
   - Fix: Replace with proper types
   - Files: Test files using `any` for mocks

3. **Missing Radix in parseInt** (FIXABLE)
   - Fix: `parseInt(value, 10)`

4. **Accessibility Issues** (A11Y)
   - Fix: Add `type="button"` to buttons
   - Fix: Use semantic elements

5. **Import Organization** (FIXABLE)
   - Auto-fix: `npm run lint:fix`

#### Actions
```bash
cd frontend/apps/web

# Auto-fix fixable issues
npm run lint:fix

# Review remaining issues
npm run lint

# Fix manually:
# 1. Replace `any` types in test files
# 2. Add radix to parseInt calls
# 3. Fix accessibility issues
# 4. Organize imports
```

### Phase 4: Verify Type Checking (Priority: LOW)
**Status**: ✅ Passing (no type errors)

#### Actions
```bash
# Already passing, but verify after fixes
cd frontend/apps/web
npm run typecheck
```

---

## 📊 Coverage Targets

### Backend Coverage Goals

| Package | Current | Target | Status |
|---------|---------|--------|--------|
| `internal/search` | 6.8% | 100% | ⏳ Integration tests needed |
| `internal/db` | 60-70% | 100% | ⏳ Queries tests needed |
| `internal/graph` | 0.0% | 100% | ⏳ Integration tests needed |
| `internal/repository` | 80-90% | 100% | ⏳ Integration tests needed |
| `internal/embeddings` | 21.4% | 100% | ✅ Tests added, verify coverage |
| `internal/handlers` | 19.1% | 100% | ✅ Tests added, verify coverage |
| `internal/infrastructure` | 17.8% | 100% | ✅ Tests added, verify coverage |
| `internal/nats` | 12.1% | 100% | ✅ Tests added, verify coverage |
| `internal/services` | 52.9% | 100% | ⏳ Tests needed |

### Frontend Coverage Goals

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Statements | TBD | 95% | ⏳ Fix coverage generation |
| Branches | TBD | 95% | ⏳ Fix coverage generation |
| Functions | TBD | 95% | ⏳ Fix coverage generation |
| Lines | TBD | 95% | ⏳ Fix coverage generation |

---

## 🚀 Implementation Priority

### Week 1: Critical Fixes
1. ✅ Fix backend compilation issues (DONE by user)
2. ⏳ Fix frontend failing tests (2 tests)
3. ⏳ Fix frontend coverage generation
4. ⏳ Run backend coverage verification

### Week 2: Integration Tests
1. ⏳ Implement `internal/search` integration tests
2. ⏳ Implement `internal/graph` integration tests
3. ⏳ Implement `internal/db/queries` integration tests
4. ⏳ Implement `internal/repository` integration tests

### Week 3: Linting & Quality
1. ⏳ Auto-fix frontend linting issues
2. ⏳ Manually fix remaining linting errors
3. ⏳ Verify all tests pass
4. ⏳ Generate final coverage reports

### Week 4: Final Verification
1. ⏳ Achieve 100% coverage on all target packages
2. ⏳ All tests passing
3. ⏳ All linting issues resolved
4. ⏳ Type checking passing
5. ⏳ Documentation updated

---

## 📝 Quick Reference Commands

### Backend
```bash
# Test all packages
cd backend
go test ./internal/...

# Coverage report
go test -coverprofile=coverage.out ./internal/...
go tool cover -html=coverage.out

# Integration tests
go test -tags=integration ./internal/...
```

### Frontend
```bash
# Run tests
cd frontend/apps/web
npm test -- --run

# Coverage
mkdir -p coverage/.tmp
npm test -- --run --coverage

# Linting
npm run lint
npm run lint:fix

# Type checking
npm run typecheck
```

---

## ✅ Success Criteria

### Backend
- [ ] All packages compile without errors
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] 100% coverage on target packages
- [ ] No duplicate test function names

### Frontend
- [ ] All tests pass (100% pass rate)
- [ ] Coverage generation works
- [ ] 95%+ coverage on all metrics
- [ ] All linting errors fixed
- [ ] Type checking passes

---

## 📚 Resources

- Backend Test Plan: `backend/TEST_COVERAGE_AUDIT_AND_PLAN.md`
- Frontend Quality Report: `frontend/FRONTEND_QUALITY_STATUS.md`
- Test Implementation Summary: `backend/TEST_IMPLEMENTATION_FINAL_SUMMARY.md`

---

## 🎯 Immediate Next Actions

1. **Fix frontend failing tests** (5 minutes)
   - Edit `links.test.ts` and `projects.test.ts`
   - Change `toHaveBeenCalledWith(undefined)` to `toHaveBeenCalledWith()`

2. **Fix frontend coverage** (2 minutes)
   - Run: `mkdir -p frontend/apps/web/coverage/.tmp`
   - Re-run: `npm test -- --run --coverage`

3. **Verify backend compilation** (5 minutes)
   - Run: `go test ./internal/embeddings/... ./internal/handlers/... ./internal/infrastructure/... ./internal/nats/...`
   - Fix any remaining compilation errors

4. **Auto-fix frontend linting** (10 minutes)
   - Run: `npm run lint:fix`
   - Review and commit changes

5. **Generate coverage reports** (10 minutes)
   - Backend: `go test -coverprofile=coverage.out ./internal/...`
   - Frontend: `npm test -- --run --coverage`
   - Review coverage gaps

---

**Ready to proceed with these steps!**
