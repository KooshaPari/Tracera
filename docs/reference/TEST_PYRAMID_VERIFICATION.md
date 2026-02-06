# Test Pyramid Verification

## Overview

The test pyramid verification script ensures that your test suite follows the **inverted pyramid principle**:

```
         /\
        /  \     <- E2E Tests (5-10%)
       /____\
      /      \
     /        \  <- Integration Tests (15-25%)
    /          \
   /____________\ <- Unit Tests (70%+)
```

This structure optimizes for fast feedback, maintainability, and reliability.

## Quick Start

### Run locally
```bash
make test-pyramid                    # Basic verification
make test-pyramid-verbose            # Detailed file listing
bash backend/scripts/verify-test-pyramid.sh
```

### CI/CD Integration
```yaml
# Automatically runs in .github/workflows/test-pyramid.yml
# on push to main/develop and pull requests
```

## Test Categories

### Unit Tests (Required: >= 70%)
Single function/component tests without external dependencies.

**File patterns:**
- **Go**: `*_test.go` (excluding `*_integration_test.go`)
- **TypeScript/React**: `*.test.ts`, `*.test.tsx` (excluding `.integration.` and `.e2e.`)
- **Python**: `test_*.py` (excluding `*_integration*`)

**Examples:**
- `user.test.ts` - Test User component
- `validator_test.go` - Test validation function
- `test_parser.py` - Test parsing logic

### Integration Tests (Recommended: 15-25%)
Tests that use real dependencies: database, Redis, services, etc.

**File patterns:**
- **Go**: `*_integration_test.go`
- **TypeScript/React**: `*.integration.test.ts`
- **Python**: `*_integration_test.py`, `*_integration.py`

**Examples:**
- `repository_integration_test.go` - Test with real database
- `auth.integration.test.ts` - Test with real auth service
- `test_api_integration.py` - Test API with real backend

### E2E Tests (Required: <= 10%)
End-to-end tests using browser or full application stack.

**File patterns:**
- **TypeScript/React**: `e2e/*.spec.ts`, `*.e2e.test.ts`

**Examples:**
- `dashboard.spec.ts` - Test dashboard flow in browser
- `auth-flow.e2e.test.ts` - Test auth flow end-to-end

## Constraints

### Required Constraints (Fail if violated)
1. **Unit tests >= 70%** - Ensures fast feedback
2. **E2E tests <= 10%** - Prevents test brittleness

### Recommended Constraints (Warn if violated)
1. **Integration tests 15-25%** - Balances coverage and speed

## Output

### Example Output
```
Detailed Test Count Report:

Total Tests: 502
├── Unit Tests:        431 (85%)
├── Integration Tests: 21 (4%)
└── E2E Tests:         50 (9%)

Test Pyramid Visualization:

           /\
          /  \  E2E Tests (9%, 50 tests)
         /____\
        /      \
       /        \  Integration Tests (4%, 21 tests)
      /          \
     /____________\
    Unit Tests (85%, 431 tests)

Constraint Analysis:

✓ Unit tests >= 70% (85%)
⚠ Integration tests outside 15-25% range (4%) - not ideal
✓ E2E tests <= 10% (9%)

Pyramid Status:

✓ Test pyramid is HEALTHY
  • Strong unit test foundation (85%)
  • Acceptable E2E test coverage (9%)

Recommendations:

⚠ Integration tests below recommended 15%
  → Consider adding more integration tests
```

### Verbose Output
```bash
make test-pyramid-verbose  # Shows file lists
```

Lists first 5 files in each category:
```
Unit Test Files:
  • backend/internal/temporal/diff_service_test.go
  • backend/internal/metrics/service_metrics_test.go
  • ... and 426 more

Integration Test Files:
  • backend/internal/repository/repository_integration_test.go
  • backend/internal/embeddings/indexer_integration_test.go
  • ... and 16 more

E2E Test Files:
  • frontend/apps/web/e2e/mobile-optimization.spec.ts
  • frontend/apps/web/e2e/example.perf.spec.ts
  • ... and 45 more
```

## Exit Codes

- **0**: Pyramid is healthy (unit >= 70%, E2E <= 10%)
- **1**: Pyramid constraints violated

## Scanned Directories

### Go Backend
- `backend/internal/` - All `*_test.go` and `*_integration_test.go`

### TypeScript/React Frontend
- `frontend/apps/web/src/__tests__/` - All `.test.ts(x)` files
- `frontend/apps/docs/src/__tests__/`
- `frontend/packages/*/src/__tests__/`
- `frontend/apps/web/e2e/` - E2E specs

### Python Backend
- `backend/tests/` - All `test_*.py` files

## Fixing Imbalanced Pyramids

### Too Many E2E Tests (> 10%)
1. **Convert browser tests to integration tests**
   - Use API testing instead of UI testing where possible
   - Mock browser interactions for unit tests

2. **Consolidate E2E scenarios**
   - Combine related flows into single E2E test
   - Remove redundant E2E coverage

3. **Move to integration layer**
   - Test API endpoints directly
   - Test business logic without UI

### Too Few Unit Tests (< 70%)
1. **Add unit tests for untested functions**
   - Focus on error cases and edge cases
   - Test validators, parsers, formatters

2. **Break down integration tests**
   - Extract pure logic into unit tests
   - Keep integration tests for DB/service interactions only

3. **Increase coverage incrementally**
   - Target 1-2 untested modules per sprint
   - Use test coverage reports to identify gaps

### Imbalanced Integration Tests (< 15% or > 25%)
1. **Too few (< 15%)**
   - Add tests for external service interactions
   - Test database transactions and cleanup
   - Add API endpoint integration tests

2. **Too many (> 25%)**
   - Convert integration tests that don't need external deps to unit tests
   - Remove redundant integration coverage (covered by E2E)

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test-pyramid.yml
# Runs on: push to main/develop, all PRs
# Status: Required check for merging
```

**Features:**
- Runs automatically on push and PR
- Posts results to PR comments
- Fails if constraints violated
- Adds summary to workflow run

### Manual CI Trigger
```bash
# Local verification before pushing
make test-pyramid

# Verbose output for debugging
make test-pyramid-verbose
```

## Maintenance

### Update Test Categories
Edit `backend/scripts/verify-test-pyramid.sh`:
```bash
# Update file pattern functions:
count_go_unit_tests()
count_ts_unit_tests()
count_python_tests()
```

### Adjust Constraints
Update percentage thresholds in `verify-test-pyramid.sh`:
```bash
# Change required minimums:
if [[ $unit_pct -ge 70 ]]; then  # <- Adjust here
```

### Add New Test Directories
Update `main()` function paths:
```bash
count_ts_unit_tests \
  "frontend/apps/web/src/__tests__" \
  "frontend/apps/new-app/src/__tests__"  # <- Add here
```

## Testing the Script

### Verify Script Works
```bash
# Run with output
bash backend/scripts/verify-test-pyramid.sh

# Run with verbose output
bash backend/scripts/verify-test-pyramid.sh -v

# Check exit code
bash backend/scripts/verify-test-pyramid.sh
echo $?  # 0 = healthy, 1 = violated
```

### Example Output Validation
```bash
# Should show healthy pyramid
make test-pyramid

# Exit code should be 0
echo $?
```

## See Also

- [Test Coverage Baseline](./COVERAGE_BASELINE.md) - Code coverage targets
- [CI/CD Gating](./CI_GATING_VERIFICATION.md) - Quality gates and checks
- [Quality Reference](./QUALITY_QUICK_REFERENCE.md) - All quality checks
