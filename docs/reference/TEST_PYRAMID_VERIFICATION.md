# Test Pyramid Verification

A script and framework for verifying test pyramid shape across a multi-language project (Go, TypeScript, Python).

## Overview

The test pyramid is a foundational testing strategy that emphasizes:
- **Unit tests (60-75%)**: Fast, isolated, low-cost tests
- **Integration tests (15-35%)**: Mid-level tests verifying component interaction
- **E2E tests (3-15%)**: Slow, expensive tests covering full workflows

This verification tool scans your entire codebase, classifies tests by type, and validates the pyramid shape is healthy.

## Quick Start

Run the verification script:

```bash
scripts/verify-test-pyramid.sh
```

With JSON output:

```bash
scripts/verify-test-pyramid.sh false /tmp/pyramid-report.json
cat /tmp/pyramid-report.json
```

With strict mode (fail on imbalance):

```bash
scripts/verify-test-pyramid.sh true
```

## Test Classification

Tests are automatically classified using build tags and file naming patterns:

### Go Tests (`backend/`)

Classified via `//go:build` comments:

| Type | Pattern | Example |
|------|---------|---------|
| **Unit** | No build tag OR `!integration && !e2e` | `func TestFoo_t() {}` (no tag) |
| **Integration** | `//go:build integration && !e2e` | `//go:build integration && !e2e` |
| **E2E** | `//go:build e2e` | `//go:build e2e` |

```go
// Unit test (no build tag)
func TestAuthFlow(t *testing.T) {
  // Fast, isolated test
}

// Integration test
//go:build integration && !e2e
func TestOAuthIntegration(t *testing.T) {
  // Tests database + cache interaction
}

// E2E test
//go:build e2e
func TestCompleteUserJourney(t *testing.T) {
  // Tests full auth flow end-to-end
}
```

### TypeScript Tests (`frontend/`)

Classified via file location and naming:

| Type | Pattern | Location |
|------|---------|----------|
| **Unit** | `*.test.ts(x)` | `__tests__/components/` |
| **Integration** | `.integration.test.ts(x)` | `__tests__/integration/` or `*.integration.test.ts` |
| **E2E** | `.spec.ts(x)` | `e2e/*.spec.ts` |

```typescript
// Unit test
// src/__tests__/components/Button.test.tsx
describe('Button', () => {
  it('renders with label', () => {
    // Tests component in isolation
  });
});

// Integration test
// src/__tests__/integration/api-client.integration.test.ts
describe('API Client Integration', () => {
  it('fetches items and updates state', async () => {
    // Tests API client + state management
  });
});

// E2E test
// e2e/user-dashboard.spec.ts
test('User can create and view items', async ({ page }) => {
  // Tests complete user workflow
});
```

### Python Tests (`src/`)

Classified via file location and naming:

| Type | Pattern | Location |
|------|---------|----------|
| **Unit** | `test_*.py` or `*_test.py` | `src/tracertm/` (not in integration) |
| **Integration** | `test_*.py` | `src/tracertm/tests/integration/` |
| **E2E** | `test_*.py` | `src/tracertm/tests/e2e/` |

```python
# Unit test
# src/tracertm/models/test_item.py
def test_item_creation():
    """Tests Item model in isolation"""
    item = Item(name="Test")
    assert item.id is not None

# Integration test
# src/tracertm/tests/integration/test_database_service.py
def test_item_service_with_database():
    """Tests service layer with actual database"""
    service = ItemService(db)
    item = service.create_item(...)
    assert service.get_item(item.id) == item

# E2E test
# src/tracertm/tests/e2e/test_api_flows.py
def test_create_item_workflow():
    """Tests complete API workflow"""
    # Create item via API
    # Verify in database
    # Check via another API call
```

## Output Interpretation

### Summary Metrics

```
Total Tests: 576
  Unit Tests: 384 (66.0%)        ✓ Within 60-75%
  Integration Tests: 58 (10.0%)  ⚠ Below 15-35%
  E2E Tests: 134 (23.0%)         ⚠ Above 3-15%
```

### Pyramid Shape Checks

```
✓ Unit tests > Integration tests        (384 > 58)
⚠ Integration tests < E2E tests         (58 < 134)  ← Pyramid inverted!
```

A healthy pyramid has:
- `unit > integration > e2e`
- Counts: 60-70% unit, 20-30% integration, 5-10% e2e

### JSON Report Format

```json
{
  "timestamp": "2026-02-06T08:15:10Z",
  "summary": {
    "total": 576,
    "unit": {
      "count": 384,
      "percentage": 66,
      "target_range": "60-75%",
      "status": "pass"
    },
    "integration": {
      "count": 58,
      "percentage": 10,
      "target_range": "15-35%",
      "status": "warn"
    },
    "e2e": {
      "count": 134,
      "percentage": 23,
      "target_range": "3-15%",
      "status": "warn"
    }
  },
  "pyramid_shape": {
    "unit_gt_integration": true,
    "integration_gt_e2e": false,
    "status": "imbalanced"
  }
}
```

## Integration with CI

### GitHub Actions

Add to `.github/workflows/quality.yml`:

```yaml
- name: Verify Test Pyramid
  run: scripts/verify-test-pyramid.sh false /tmp/pyramid-report.json

- name: Upload Pyramid Report
  uses: actions/upload-artifact@v3
  with:
    name: test-pyramid-report
    path: /tmp/pyramid-report.json
```

### Makefile Target

```makefile
.PHONY: verify-pyramid
verify-pyramid:
	@scripts/verify-test-pyramid.sh

.PHONY: verify-pyramid-strict
verify-pyramid-strict:
	@scripts/verify-test-pyramid.sh true
```

Usage:

```bash
make verify-pyramid        # Informational report
make verify-pyramid-strict # Fail on imbalance
```

## Exit Codes

| Code | Meaning | Strict Mode |
|------|---------|-------------|
| `0` | Success (healthy or imbalanced) | Healthy only |
| `2` | Imbalance detected | Always fails |
| `3` | Validation issues | Return issue count |

## Recommended Actions

If your pyramid is imbalanced:

### Too Few Integration Tests (Below 15%)

**Problem:** Direct jumps from unit to E2E, missing interaction testing.

**Solutions:**
1. Add integration tests for service layers
2. Test API handlers with mocked database
3. Verify component interactions with mock state

### Too Many E2E Tests (Above 15%)

**Problem:** Inefficient testing, slow pipelines, brittleness.

**Solutions:**
1. Push API tests down to integration level
2. Mock external services instead of hitting real endpoints
3. Test browser interactions only for critical paths

### Unit Tests Below 60%

**Problem:** Insufficient unit test coverage, risky refactoring.

**Solutions:**
1. Add unit tests for utilities, validators, formatters
2. Test error paths and edge cases
3. Mock external dependencies

## Performance Considerations

The script scans the entire codebase with `find` and `grep`:

- **Frontend:** Only `frontend/apps/web/src/__tests__` (excludes `node_modules`)
- **Backend:** Only `backend/` (excludes `ARCHIVE`)
- **Python:** Only `src/` (excludes `.pytest_cache`, `__pycache__`)

Typical runtime: **5-15 seconds**

## Troubleshooting

### Script Says "No Tests Found"

Check that test files exist in expected directories:

```bash
# Go tests
find backend -name "*_test.go" | head -5

# TypeScript tests
find frontend -name "*.test.ts*" | head -5

# Python tests
find src -name "test_*.py" -o -name "*_test.py" | head -5
```

### Counts Seem Off

Verify file patterns match your naming conventions:

```bash
# Check Go build tags
grep -r "^//go:build" backend --include="*_test.go" | head -10

# Check TypeScript integration tests
find frontend -name "*.integration.test.ts*" | head -10
```

## Best Practices

1. **Organize by type**: Keep unit, integration, and e2e tests in separate directories
2. **Use build tags consistently**: All Go tests should have explicit build tags
3. **Name clearly**: Use `.integration.test` and `.spec` patterns for clarity
4. **Run regularly**: Add to CI pipeline to catch pyramid drift
5. **Monitor trends**: Store JSON reports to track pyramid health over time

## Related Documentation

- [CI Quality Gates](./ci-gates-quick-reference.md)
- [Backend Coverage Quick Reference](./backend-coverage-quick-reference.md)
- [Frontend Coverage Audit](../reports/frontend-coverage-audit-executive-summary.md)

## See Also

- **Test Pyramid**: [Martin Fowler - Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- **Go Build Constraints**: [Go Build Constraints](https://golang.org/doc/effective_go#build-constraints)
- **Vitest**: [Vitest Documentation](https://vitest.dev/)
- **Pytest**: [Pytest Best Practices](https://docs.pytest.org/)
