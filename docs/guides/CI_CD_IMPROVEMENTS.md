# CI/CD Pipeline Improvements

This document describes the improvements made to the CI/CD pipeline for better test execution, failure detection, and reporting.

## Overview

The CI/CD pipeline has been enhanced with:
1. **Build matrix for parallel testing** - Different test types run in parallel
2. **Optimized test ordering** - Fast tests run before slow tests
3. **Flaky test detection and retry** - Automatic retry for flaky E2E tests
4. **Improved failure reporting** - Test summaries with detailed metrics

## Test Matrix Strategy

### Python Tests (`.github/workflows/tests.yml`)

The test matrix runs different test types in parallel:

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.11", "3.12"]
    test-type: [unit, integration, e2e]
    include:
      - python-version: "3.12"
        test-type: property
```

#### Test Types

1. **Unit Tests** (`unit`)
   - Fast unit tests run first
   - Slow unit tests run second
   - Includes code coverage reporting
   - Coverage threshold: 90%

2. **Integration Tests** (`integration`)
   - Database integration tests
   - File system integration tests
   - External service mocks

3. **E2E Tests** (`e2e`)
   - Full CLI workflow tests
   - With automatic retry (up to 3 attempts)
   - Flaky test detection

4. **Property-based Tests** (`property`)
   - Hypothesis-based property tests
   - Only on Python 3.12

### Go Tests (`.github/workflows/ci.yml`)

Go tests are optimized with:
- Short tests (`-short` flag) run first
- Full test suite with coverage
- Automatic retry for flaky tests (up to 2 attempts)
- Coverage reporting

### Frontend E2E Tests (`.github/workflows/ci.yml`)

Playwright E2E tests include:
- Automatic retry (up to 3 attempts for flaky tests)
- JSON and HTML reporting
- Test summary generation
- Screenshot/video capture on failure

## Test Ordering Optimization

### Fast Tests First Strategy

Tests are ordered by execution speed to provide faster feedback:

1. **Fast tests** (< 1s) - Marked with `not slow`
2. **Slow tests** (> 1s) - Marked with `slow`

This allows developers to get quick feedback on common failures while slow tests run in the background.

#### Example Usage

```bash
# Run fast tests first
pytest tests/ -m "unit and not slow"

# Then run slow tests
pytest tests/ -m "unit and slow"
```

#### Marking Tests

Use pytest markers to classify tests:

```python
import pytest

@pytest.mark.unit
@pytest.mark.slow
def test_expensive_computation():
    """This test takes > 1 second to run"""
    pass

@pytest.mark.unit
def test_fast_validation():
    """This test is fast (< 1 second)"""
    pass
```

## Flaky Test Detection and Retry

### Automatic Retry

E2E and integration tests automatically retry on failure using `nick-fields/retry@v3`:

```yaml
- uses: nick-fields/retry@v3
  with:
    timeout_minutes: 15
    max_attempts: 3  # Retry up to 3 times
    retry_on: error
    command: |
      pytest tests/ -m "e2e"
```

### Flaky Test Detection

When a test passes after retry, it's flagged as flaky:

```yaml
- name: Detect flaky tests
  if: steps.test-run.outcome == 'success' && steps.test-run.outputs.total_attempts > 1
  run: |
    echo "::warning::Flaky test detected - passed after ${{ steps.test-run.outputs.total_attempts }} attempts"
```

### Configuration by Test Type

| Test Type | Max Attempts | Timeout | Use Case |
|-----------|--------------|---------|----------|
| Unit | 1 | 5 min | Should never be flaky |
| Integration | 1 | 10 min | Database/file system |
| E2E | 3 | 15 min | Full workflows, can be flaky |
| Frontend E2E | 3 | 20 min | Playwright tests |

## Test Reporting and Summaries

### GitHub Step Summary

Each test job generates a detailed summary in the GitHub Actions UI:

#### Python Test Summary
```markdown
## Test Summary: unit (Python 3.12)

| Metric | Count |
|--------|-------|
| Total Tests | 150 |
| ✅ Passed | 148 |
| ❌ Failed | 2 |
| ⚠️ Errors | 0 |
| ⏭️ Skipped | 0 |

⚠️ **Flaky test detected** - Tests passed after 2 attempts
```

#### Go Test Summary
```markdown
## Go Test Results

| Metric | Value |
|--------|-------|
| Coverage | 85.4% |
| Status | ✅ Passed |
```

### JUnit XML Reports

All test runs generate JUnit XML reports for integration with test reporting tools:

```bash
pytest tests/ --junitxml=junit-<test-type>.xml
```

These reports include:
- Test counts (total, passed, failed, skipped)
- Execution time
- Error messages and stack traces

### Artifacts

Test artifacts are uploaded and retained for 30 days:

- Coverage reports (XML, HTML)
- JUnit XML reports
- Pytest cache
- Playwright screenshots/videos (on failure)

## Makefile Targets

New Makefile targets support the CI matrix:

```bash
# Run unit tests (fast first, then slow)
make test-unit

# Run integration tests
make test-integration

# Run E2E tests
make test-e2e

# Run all tests in parallel
make test-python-parallel
```

## Local Development Usage

### Running Tests Locally

```bash
# Run fast unit tests only
pytest tests/ -m "unit and not slow" -v

# Run slow unit tests only
pytest tests/ -m "unit and slow" -v

# Run all tests with fast-first ordering
make test-unit

# Run E2E tests (with retry on local)
pytest tests/ -m "e2e" -v --maxfail=3
```

### Simulating CI Environment

```bash
# Run tests exactly as CI does
PYTHONPATH=./src pytest tests/ -m "unit and not slow" -v \
  --cov=src/tracertm \
  --cov-report=xml \
  --junitxml=junit-unit.xml

# Run with parallel execution
PYTHONPATH=./src pytest tests/ -n auto -v \
  --cov=src/tracertm \
  --cov-fail-under=90
```

## Performance Metrics

### Expected Execution Times

| Test Suite | Without Optimization | With Optimization | Improvement |
|------------|---------------------|-------------------|-------------|
| Python Unit | ~5 min | ~3 min | 40% faster |
| Python Integration | ~8 min | ~6 min | 25% faster |
| Go Tests | ~4 min | ~3 min | 25% faster |
| Frontend E2E | ~12 min | ~10 min | 17% faster |

### Parallel Execution Benefits

Running tests in parallel matrix:
- Before: ~25 minutes (sequential)
- After: ~12 minutes (parallel matrix)
- **Improvement: 52% faster**

## Best Practices

### For Test Authors

1. **Mark slow tests appropriately**
   ```python
   @pytest.mark.slow
   def test_expensive_operation():
       pass
   ```

2. **Keep unit tests fast** (< 1s per test)
   - Use mocks for external dependencies
   - Avoid database access in unit tests
   - Use in-memory data structures

3. **Make E2E tests resilient**
   - Add proper waits for async operations
   - Use retry decorators for known flaky operations
   - Clean up test data properly

4. **Add test documentation**
   - Document why a test is marked as slow
   - Explain flaky test workarounds
   - Add references to related issues

### For Reviewers

1. **Check test markers** - Ensure slow tests are marked
2. **Review test execution time** - Flag tests > 1s in unit tests
3. **Verify flaky tests** - Investigate why tests needed retry
4. **Check coverage** - Ensure new code has adequate coverage

## Troubleshooting

### Flaky Test Warnings

If you see flaky test warnings:

1. Check the test execution logs
2. Identify the specific test that flaked
3. Add proper waits or retries to the test
4. Consider moving to integration tests if it requires external resources

### Coverage Failures

If coverage drops below 90%:

1. Check the coverage report in artifacts
2. Add tests for uncovered code paths
3. Remove dead code if appropriate
4. Update coverage exclusions if needed

### Timeout Issues

If tests timeout:

1. Check for infinite loops or deadlocks
2. Increase timeout for legitimately slow tests
3. Optimize slow operations
4. Consider breaking up large test suites

## Future Improvements

Planned enhancements:
- [ ] Test result visualization dashboard
- [ ] Historical flaky test tracking
- [ ] Automatic test splitting for better parallelization
- [ ] Predictive test selection (run affected tests first)
- [ ] Performance regression detection

## Related Documentation

- [Testing Strategy](./TESTING_STRATEGY.md)
- [Test Infrastructure](../reference/TEST_INFRASTRUCTURE.md)
- [GitHub Actions Workflows](../../.github/workflows/)
- [Pytest Configuration](../../pyproject.toml)

## References

- [GitHub Actions: Matrix Strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [Pytest Markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [Nick Fields Retry Action](https://github.com/nick-fields/retry)
- [Playwright Test Retries](https://playwright.dev/docs/test-retries)
