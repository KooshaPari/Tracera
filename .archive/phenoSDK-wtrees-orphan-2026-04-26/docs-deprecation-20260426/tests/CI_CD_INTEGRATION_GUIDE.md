# CI/CD Integration Guide for Phase 4 Tests

## Quick Start

```bash
# Install test dependencies
pip install -e ".[testing]"

# Run all tests
pytest tests/pheno/ -v

# Run with coverage
pytest tests/pheno/ --cov=pheno --cov-report=html --cov-report=term-missing

# Run specific module
pytest tests/pheno/testing/test_mcp_qa.py -v
```

## GitHub Actions Workflow

Create `.github/workflows/phase4-tests.yml`:

```yaml
name: Phase 4 Test Suite

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'src/pheno/testing/**'
      - 'src/pheno/kits/**'
      - 'tests/pheno/**'
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[testing]"

    - name: Run mcp_qa tests
      run: |
        pytest tests/pheno/testing/test_mcp_qa.py \
          -v \
          --cov=pheno.testing.mcp_qa \
          --cov-report=xml \
          --cov-report=term-missing \
          --junitxml=junit/mcp_qa-results.xml

    - name: Run cache tests
      run: |
        pytest tests/pheno/caching/test_cache_systems.py \
          -v \
          --cov=pheno.testing.mcp_qa.core.cache \
          --cov-append \
          --cov-report=xml \
          --junitxml=junit/cache-results.xml

    - name: Run optimization tests
      run: |
        pytest tests/pheno/optimization/test_optimization_utils.py \
          -v \
          --cov=pheno.testing.mcp_qa.core.optimizations \
          --cov-append \
          --cov-report=xml \
          --junitxml=junit/optimization-results.xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      with:
        files: ./coverage.xml
        flags: phase4,python-${{ matrix.python-version }}
        name: phase4-${{ matrix.os }}-py${{ matrix.python-version }}
        fail_ci_if_error: false

    - name: Publish test results
      uses: EnricoMi/publish-unit-test-result-action@v2
      if: always()
      with:
        files: junit/*.xml
        check_name: Phase 4 Tests (${{ matrix.os }}, py${{ matrix.python-version }})

    - name: Archive coverage report
      uses: actions/upload-artifact@v4
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
      with:
        name: coverage-report-html
        path: htmlcov/
        retention-days: 30

  coverage-check:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        pip install -e ".[testing]"

    - name: Run coverage check
      run: |
        pytest tests/pheno/ \
          --cov=pheno \
          --cov-fail-under=85 \
          --cov-report=term-missing

  performance-check:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -e ".[testing]"
        pip install pytest-benchmark

    - name: Run performance tests
      run: |
        pytest tests/pheno/ \
          -v \
          -m performance \
          --benchmark-only \
          --benchmark-autosave \
          --benchmark-save-data

    - name: Upload benchmark results
      uses: actions/upload-artifact@v4
      with:
        name: benchmark-results
        path: .benchmarks/
```

## Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--extend-ignore=E203,W503']

  - repo: local
    hooks:
      - id: pytest-fast
        name: pytest-fast
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args:
          - tests/pheno/testing/test_mcp_qa.py
          - tests/pheno/caching/test_cache_systems.py
          - tests/pheno/optimization/test_optimization_utils.py
          - -v
          - --maxfail=1
          - -x
          - --tb=short

      - id: coverage-check-local
        name: coverage-check-local
        entry: pytest
        language: system
        pass_filenames: false
        stages: [push]
        args:
          - tests/pheno/
          - --cov=pheno
          - --cov-fail-under=80
          - --cov-report=term-missing:skip-covered
```

## pytest Configuration

Update `pytest.ini`:

```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, external deps)
    performance: Performance and benchmark tests
    slow: Slow tests (skip by default)
    asyncio: Async tests

# Coverage options
addopts =
    -v
    --strict-markers
    --tb=short
    --cov-branch
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-report=xml
    --junitxml=junit/test-results.xml

# Async
asyncio_mode = auto

# Timeout
timeout = 300
timeout_method = thread

# Warnings
filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning

# Coverage
[coverage:run]
source = pheno
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

## Makefile Targets

```makefile
.PHONY: test test-fast test-cov test-unit test-integration test-performance

# Run all tests
test:
	pytest tests/pheno/ -v

# Run fast tests only (skip slow/integration)
test-fast:
	pytest tests/pheno/ -v -m "not slow and not integration"

# Run with coverage
test-cov:
	pytest tests/pheno/ \
		--cov=pheno \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml

# Run unit tests only
test-unit:
	pytest tests/pheno/ -v -m unit

# Run integration tests
test-integration:
	pytest tests/pheno/ -v -m integration

# Run performance tests
test-performance:
	pytest tests/pheno/ -v -m performance --benchmark-only

# Clean test artifacts
clean-test:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
	rm -f coverage.xml
	rm -rf junit
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install test dependencies
install-test:
	pip install -e ".[testing]"

# Run pre-commit checks
pre-commit:
	pre-commit run --all-files
```

## tox Configuration

Create `tox.ini`:

```ini
[tox]
envlist = py{310,311,312}, coverage, lint
isolated_build = True

[testenv]
deps =
    pytest>=7.0
    pytest-asyncio>=0.21
    pytest-cov>=4.0
    pytest-timeout>=2.1

commands =
    pytest tests/pheno/ -v --cov=pheno --cov-append

[testenv:coverage]
deps =
    {[testenv]deps}
    coverage[toml]>=7.0

commands =
    coverage erase
    pytest tests/pheno/ --cov=pheno --cov-report=html --cov-report=term
    coverage report --fail-under=85

[testenv:lint]
deps =
    black>=23.0
    flake8>=6.0
    mypy>=1.0

commands =
    black --check src/pheno tests/pheno
    flake8 src/pheno tests/pheno
    mypy src/pheno

[testenv:docs]
deps =
    sphinx>=6.0
    sphinx-rtd-theme>=1.0

commands =
    sphinx-build -W -b html docs docs/_build
```

## Docker Test Container

Create `Dockerfile.test`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml setup.py ./
COPY src/ ./src/

# Install package with test dependencies
RUN pip install --no-cache-dir -e ".[testing]"

# Copy tests
COPY tests/ ./tests/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTEST_ADDOPTS="--color=yes"

# Run tests
CMD ["pytest", "tests/pheno/", "-v", "--cov=pheno", "--cov-report=term-missing"]
```

Run tests in Docker:
```bash
docker build -f Dockerfile.test -t pheno-tests .
docker run --rm pheno-tests
```

## Test Execution Examples

### Local Development

```bash
# Quick check (fast tests only)
make test-fast

# Full test suite with coverage
make test-cov

# Specific module
pytest tests/pheno/testing/test_mcp_qa.py -v

# Watch mode (requires pytest-watch)
ptw tests/pheno/ -- -v
```

### CI/CD Pipeline

```bash
# Full suite (as in CI)
pytest tests/pheno/ \
    -v \
    --cov=pheno \
    --cov-fail-under=85 \
    --cov-report=xml \
    --junitxml=junit/results.xml

# Parallel execution
pytest tests/pheno/ -v -n auto
```

### Performance Testing

```bash
# Run benchmarks
pytest tests/pheno/ \
    -v \
    -m performance \
    --benchmark-only \
    --benchmark-compare

# Profile slow tests
pytest tests/pheno/ \
    --profile \
    --profile-svg
```

## Coverage Reports

### Generate HTML Report
```bash
pytest tests/pheno/ --cov=pheno --cov-report=html
open htmlcov/index.html
```

### Generate XML Report (for CI)
```bash
pytest tests/pheno/ --cov=pheno --cov-report=xml
```

### Terminal Report
```bash
pytest tests/pheno/ --cov=pheno --cov-report=term-missing
```

## Troubleshooting

### Tests Failing Locally But Passing in CI

1. Check Python version compatibility
2. Verify dependency versions
3. Check for environment-specific configurations
4. Ensure all test fixtures are cleaned up

### Slow Test Execution

1. Run with `-v` to identify slow tests
2. Use `-n auto` for parallel execution
3. Mark slow tests with `@pytest.mark.slow`
4. Skip slow tests locally: `pytest -m "not slow"`

### Coverage Not Meeting Threshold

1. Identify uncovered lines: `pytest --cov-report=term-missing`
2. Add tests for missing branches
3. Verify test is actually running the code
4. Check for dead/unreachable code

### Flaky Tests

1. Identify with `pytest --lf` (last failed)
2. Add retry logic for network tests
3. Use fixtures for proper setup/teardown
4. Check for race conditions in async tests

## Best Practices

1. **Run tests before committing:**
   ```bash
   make test-fast
   ```

2. **Check coverage regularly:**
   ```bash
   make test-cov
   ```

3. **Use markers for test organization:**
   ```python
   @pytest.mark.unit
   @pytest.mark.integration
   @pytest.mark.performance
   ```

4. **Keep tests fast:**
   - Mock external dependencies
   - Use fixtures for setup
   - Skip slow tests in development

5. **Write descriptive test names:**
   ```python
   def test_cache_expiry_after_ttl_exceeds()
   ```

6. **Document test failures:**
   - Include reproduction steps
   - Link to related issues
   - Provide expected vs actual

## Monitoring and Alerts

### Coverage Trends

Track coverage over time using Codecov:
- Set coverage targets per module
- Alert on coverage decrease
- Block PRs below threshold

### Performance Regression

Use pytest-benchmark to track:
- Test execution time trends
- Performance regression alerts
- Benchmark comparisons between commits

### Test Flakiness

Monitor test stability:
- Track failure rates
- Identify flaky tests
- Quarantine unstable tests

## Support

For issues or questions:
- Check test logs: `junit/test-results.xml`
- Review coverage report: `htmlcov/index.html`
- Consult `PHASE4_TEST_COVERAGE_REPORT.md`
- Open issue with test failure details
