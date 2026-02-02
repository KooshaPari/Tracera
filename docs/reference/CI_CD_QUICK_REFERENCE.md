# CI/CD Quick Reference

Quick reference for the improved CI/CD pipeline.

## Test Matrix

### Python Test Types

| Type | Marker | Description | Retry | Coverage |
|------|--------|-------------|-------|----------|
| `unit` | `@pytest.mark.unit` | Fast unit tests | No | Yes |
| `integration` | `@pytest.mark.integration` | Database/FS tests | No | No |
| `e2e` | `@pytest.mark.e2e` | Full workflows | 3x | No |
| `property` | `@pytest.mark.property` | Hypothesis tests | No | No |

### Test Speed Markers

```python
# Fast test (< 1s) - default
@pytest.mark.unit
def test_fast():
    pass

# Slow test (> 1s) - mark explicitly
@pytest.mark.unit
@pytest.mark.slow
def test_slow():
    pass
```

## Makefile Commands

```bash
# Unit tests (fast → slow)
make test-unit

# Integration tests
make test-integration

# E2E tests
make test-e2e

# All tests in parallel
make test-python-parallel

# All backend tests
make test

# Go tests only
make test-go
```

## Local Test Execution

```bash
# Fast unit tests only
pytest tests/ -m "unit and not slow"

# Slow unit tests only
pytest tests/ -m "unit and slow"

# E2E tests with retry
pytest tests/ -m "e2e" --maxfail=3

# Parallel execution
pytest tests/ -n auto

# With coverage
pytest tests/ -m unit --cov=src/tracertm --cov-report=html
```

## CI/CD Workflows

### `.github/workflows/tests.yml`

**Matrix strategy** - Runs test types in parallel:
- Python 3.11 + 3.12
- Test types: unit, integration, e2e, property

**Features:**
- ✅ Parallel test execution
- ✅ Fast tests run before slow tests
- ✅ Flaky E2E test retry (3x)
- ✅ Test summaries with metrics
- ✅ Coverage reporting

### `.github/workflows/ci.yml`

**Full CI pipeline** - Python + Go + Frontend:
- Python: Fast → slow ordering
- Go: Short tests → full suite
- Frontend: E2E with retry (3x)

**Features:**
- ✅ Test summaries for all suites
- ✅ Flaky test detection
- ✅ Artifact retention (30 days)
- ✅ Multi-service setup

## Test Summaries

### Python
```
## Test Summary: unit (Python 3.12)
| Metric      | Count |
|-------------|-------|
| Total Tests | 150   |
| ✅ Passed   | 148   |
| ❌ Failed   | 2     |
| ⚠️ Errors   | 0     |
| ⏭️ Skipped  | 0     |
```

### Go
```
## Go Test Results
| Metric   | Value  |
|----------|--------|
| Coverage | 85.4%  |
| Status   | ✅ Pass |
```

## Retry Configuration

| Test Type | Attempts | Timeout | Use Case |
|-----------|----------|---------|----------|
| Unit | 1 | 5m | No retry |
| Integration | 1 | 10m | No retry |
| E2E | 3 | 15m | Retry flaky |
| Frontend E2E | 3 | 20m | Retry flaky |

## Flaky Test Detection

### Automatic Detection
```yaml
if: steps.test-run.outcome == 'success' &&
    steps.test-run.outputs.total_attempts > 1
```

### Warning Message
```
⚠️ Flaky test detected - passed after 2 attempts
```

## Artifacts

**Retention:** 30 days

### Python
- `htmlcov/` - Coverage HTML report
- `coverage.xml` - Coverage XML
- `junit-*.xml` - JUnit test reports
- `.pytest_cache/` - Pytest cache

### Go
- `coverage.out` - Coverage data
- `coverage.html` - Coverage HTML

### Frontend
- `playwright-report/` - Playwright HTML report
- `test-results/` - Test screenshots/videos
- `results.json` - Playwright JSON report

## Performance

### Execution Times (Optimized)

| Suite | Time | Improvement |
|-------|------|-------------|
| Python Unit | ~3 min | 40% ⬇️ |
| Python Integration | ~6 min | 25% ⬇️ |
| Go Tests | ~3 min | 25% ⬇️ |
| Frontend E2E | ~10 min | 17% ⬇️ |

**Total (parallel):** ~12 min (52% faster than sequential)

## Common Issues

### Coverage Failure
```bash
# Check coverage report
open htmlcov/index.html

# Add tests or update threshold
pytest tests/ --cov=src/tracertm --cov-fail-under=85
```

### Flaky Test
```python
# Add retry decorator
@pytest.mark.e2e
@pytest.mark.flaky(reruns=3)
def test_flaky():
    pass
```

### Timeout
```python
# Mark as slow
@pytest.mark.slow
def test_long_running():
    pass
```

## Best Practices

### ✅ Do
- Mark slow tests with `@pytest.mark.slow`
- Keep unit tests < 1s
- Use mocks for external dependencies
- Add proper waits in E2E tests
- Document flaky test workarounds

### ❌ Don't
- Add database access to unit tests
- Make E2E tests without cleanup
- Ignore flaky test warnings
- Skip adding test markers
- Use `sleep()` in tests (use proper waits)

## Quick Links

- [Full Documentation](../guides/CI_CD_IMPROVEMENTS.md)
- [Test Infrastructure](./TEST_INFRASTRUCTURE.md)
- [GitHub Workflows](../../.github/workflows/)
- [Pytest Config](../../pyproject.toml)
