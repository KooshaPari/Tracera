# Storage Integration Tests - Quick Start Guide

## Quick Test Commands

### Run All Storage Integration Tests
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
pytest tests/integration/storage/test_storage_integration.py -v
```

### Run with Coverage Report
```bash
pytest tests/integration/storage/test_storage_integration.py \
    --cov=src/tracertm/storage \
    --cov-report=term-missing \
    --cov-report=html
```

### View Coverage Report
```bash
open htmlcov/index.html
```

## Test Coverage Targets

| File | Before | Target | Lines |
|------|--------|--------|-------|
| local_storage.py | 7.63% | **80%+** | 566 |
| sync_engine.py | 28.53% | **80%+** | 279 |
| markdown_parser.py | 16.62% | **80%+** | 263 |
| conflict_resolver.py | 26.22% | **80%+** | 266 |

## Tests Created

- **85 comprehensive integration tests**
- **1,600+ lines of test code**
- **7 test classes** covering all Storage modules
- **Real filesystem and database** integration testing

## Next Steps

1. Run tests: `pytest tests/integration/storage/test_storage_integration.py -v`
2. Check coverage: `pytest --cov=src/tracertm/storage --cov-report=html`
3. Review report: `open htmlcov/index.html`
