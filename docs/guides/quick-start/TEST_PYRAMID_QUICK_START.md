# Test Pyramid Verification - Quick Start

## TL;DR

```bash
# Run test pyramid verification
make test-pyramid

# Verbose output with file lists
make test-pyramid-verbose

# Check exit code (0=healthy, 1=violated)
echo $?
```

## What It Does

Verifies your test suite follows the healthy **test pyramid** pattern:

```
         /\
        /  \     70-85%: Unit tests (fast, isolated)
       /____\
      /      \
     /        \  15-25%: Integration tests (real deps)
    /          \
   /____________\ 5-10%: E2E tests (full app flow)
```

## Current Status

```
Total Tests: 502
├── Unit Tests:        431 (85%)  ✓ Exceeds 70% requirement
├── Integration Tests: 21 (4%)    ⚠ Below 15% ideal
└── E2E Tests:         50 (9%)    ✓ Within 10% max
```

**Result: HEALTHY PYRAMID** ✓

## Quick Commands

### Local Verification
```bash
make test-pyramid                # Basic check
make test-pyramid-verbose        # Show test files
bash backend/scripts/verify-test-pyramid.sh
```

### Script Location
```
backend/scripts/verify-test-pyramid.sh
```

### Makefile Targets
```bash
make test-pyramid          # Run verification
make test-pyramid-verbose  # Detailed output
```

### CI/CD
```
.github/workflows/test-pyramid.yml  # Auto-runs on push/PR
```

## Understanding Results

### Healthy Pyramid (Exit 0)
```
✓ Unit tests >= 70%
✓ E2E tests <= 10%
✓ Test pyramid is HEALTHY
```

### Imbalanced Pyramid (Exit 1)
```
✗ Unit tests < 70%        # Too many E2E/integration
✗ E2E tests > 10%         # Too many browser tests
```

## What Gets Scanned

| Language | Pattern | Location |
|----------|---------|----------|
| Go | `*_test.go`, `*_integration_test.go` | `backend/internal/` |
| TypeScript | `*.test.ts`, `*.test.tsx`, `*.e2e.test.ts` | `frontend/apps/web/src/__tests__` |
| React | `*.spec.ts` in e2e | `frontend/apps/web/e2e/` |
| Python | `test_*.py` | `backend/tests/` |

## Test Categories

### Unit Tests
Single function/component, no external deps.
```
backend/internal/users/user_test.go
frontend/apps/web/src/__tests__/components/Button.test.tsx
```

### Integration Tests
Real database, API, or service calls.
```
backend/internal/repository/db_integration_test.go
frontend/apps/web/src/__tests__/api.integration.test.ts
```

### E2E Tests
Full browser or application flow.
```
frontend/apps/web/e2e/auth.spec.ts
frontend/apps/web/e2e/dashboard.e2e.test.ts
```

## Fixing Issues

### Too Many E2E Tests
1. Convert browser tests to API/integration tests
2. Mock interactions instead of testing through UI
3. Consolidate related scenarios

### Too Few Unit Tests
1. Add tests for error cases and edge cases
2. Extract pure logic from integration tests
3. Focus on validators, parsers, formatters

### Too Few Integration Tests
1. Add DB transaction tests
2. Add external service integration tests
3. Test API endpoints directly

## CI Integration

The script runs automatically:
- ✓ On every push to `main` or `develop`
- ✓ On every pull request
- ✓ Fails if constraints violated
- ✓ Posts results to PR comments

## More Details

See [TEST_PYRAMID_VERIFICATION.md](../../reference/TEST_PYRAMID_VERIFICATION.md) for:
- Detailed constraint explanations
- Remediation guides
- Script customization
- Directory configuration

## Support

Script: `backend/scripts/verify-test-pyramid.sh`
Documentation: `docs/reference/TEST_PYRAMID_VERIFICATION.md`
