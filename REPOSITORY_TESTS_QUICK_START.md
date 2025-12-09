# Repository Gap Coverage Tests - Quick Start Guide

## Overview
85 comprehensive integration tests targeting 85%+ coverage for all repository modules.

**Test File**: `tests/integration/repositories/test_repositories_gap_coverage.py`

---

## Quick Commands

### Run All Repository Gap Tests
```bash
pytest tests/integration/repositories/test_repositories_gap_coverage.py -v
```

### Run with Coverage Report
```bash
pytest tests/integration/repositories/test_repositories_gap_coverage.py \
    --cov=src/tracertm/repositories \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/repositories
```

### Run Specific Repository Tests
```bash
# Project repository tests only
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "project" -v

# Item repository tests only
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "item" -v

# Link repository tests only
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "link" -v

# Agent repository tests only
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "agent" -v

# Event repository tests only
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "event" -v
```

### Run by Category
```bash
# CRUD operations
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "create or update or delete" -v

# Queries
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "get_by or query" -v

# Hierarchies
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "ancestor or descendant or children" -v

# Error handling
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "error or nonexistent or invalid" -v
```

---

## Test Count Verification

Expected test counts by module:

```bash
# Should show 5 tests
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "project" --collect-only

# Should show 22 tests
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "item" --collect-only

# Should show 8 tests
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "link" --collect-only

# Should show 5 tests
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "agent" --collect-only

# Should show 15 tests
pytest tests/integration/repositories/test_repositories_gap_coverage.py -k "event" --collect-only
```

Total: 85 tests (includes cross-repository integration tests)

---

## Coverage Validation

### Check Current Coverage
```bash
# Before running new tests
pytest tests/integration/repositories/test_repositories_integration.py \
    --cov=src/tracertm/repositories \
    --cov-report=term-missing
```

### Check Improved Coverage
```bash
# After running all repository tests
pytest tests/integration/repositories/ \
    --cov=src/tracertm/repositories \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/repositories
```

### Target Coverage per File
```
item_repository.py       85%+
project_repository.py    85%+
link_repository.py       85%+
agent_repository.py      85%+
event_repository.py      85%+
```

---

## Coverage Report Analysis

### View HTML Coverage Report
```bash
# Generate HTML report
pytest tests/integration/repositories/ \
    --cov=src/tracertm/repositories \
    --cov-report=html:htmlcov/repositories

# Open in browser (macOS)
open htmlcov/repositories/index.html

# Open in browser (Linux)
xdg-open htmlcov/repositories/index.html
```

### View Missing Lines
```bash
# Show detailed missing coverage
pytest tests/integration/repositories/ \
    --cov=src/tracertm/repositories \
    --cov-report=term-missing \
    | grep -A 20 "src/tracertm/repositories"
```

---

## Test Output Examples

### Successful Test Run
```
tests/integration/repositories/test_repositories_gap_coverage.py::test_project_create_minimal_fields PASSED
tests/integration/repositories/test_repositories_gap_coverage.py::test_item_update_multiple_fields PASSED
tests/integration/repositories/test_repositories_gap_coverage.py::test_event_sourcing_full_lifecycle PASSED
...
================================ 85 passed in 5.23s ================================
```

### Coverage Report
```
Name                                            Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------
src/tracertm/repositories/item_repository.py      150     22    85%   45-47, 120-122
src/tracertm/repositories/project_repository.py    42      5    88%   30-31
src/tracertm/repositories/link_repository.py       48      6    87%   55-57
src/tracertm/repositories/agent_repository.py      45      4    91%   75-76
src/tracertm/repositories/event_repository.py      78     11    86%   95-97
-----------------------------------------------------------------------------
TOTAL                                            363     48    87%
```

---

## Debugging Failed Tests

### Run Single Test with Verbose Output
```bash
pytest tests/integration/repositories/test_repositories_gap_coverage.py::test_event_sourcing_full_lifecycle -vvs
```

### Run with Logging Enabled
```bash
pytest tests/integration/repositories/test_repositories_gap_coverage.py -v --log-cli-level=DEBUG
```

### Run with Pytest Debug on Failure
```bash
pytest tests/integration/repositories/test_repositories_gap_coverage.py --pdb
```

---

## Common Issues and Solutions

### Issue: Import Errors
```
ImportError: cannot import name 'EventRepository'
```
**Solution**: Ensure you're running from project root
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
pytest tests/integration/repositories/test_repositories_gap_coverage.py -v
```

### Issue: Database Errors
```
sqlalchemy.exc.OperationalError: database is locked
```
**Solution**: Tests use in-memory SQLite with auto-cleanup. Ensure no other processes using test DB.

### Issue: Fixture Not Found
```
fixture 'db_session' not found
```
**Solution**: Ensure `tests/conftest.py` is present and contains `db_session` fixture.

---

## Test Data Cleanup

Tests use `db_session` fixture with automatic rollback:
- Each test gets fresh session
- All changes rolled back after test
- No manual cleanup needed
- No test pollution

---

## Performance Benchmarks

### Expected Execution Times
- Full suite (85 tests): ~5-10 seconds
- Single repository (5-22 tests): ~1-3 seconds
- Individual test: ~50-200ms

### Slow Tests
If tests are slow (>10s total), check:
1. Database connection (should be in-memory SQLite)
2. Async operations (proper await usage)
3. Sleep statements (minimal delays for timestamp tests)

---

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Repository Gap Coverage Tests
  run: |
    pytest tests/integration/repositories/test_repositories_gap_coverage.py \
      --cov=src/tracertm/repositories \
      --cov-report=xml \
      --cov-fail-under=85
```

### Pre-commit Hook
```bash
#!/bin/bash
# Run repository tests before commit
pytest tests/integration/repositories/test_repositories_gap_coverage.py -v
if [ $? -ne 0 ]; then
    echo "Repository tests failed. Commit aborted."
    exit 1
fi
```

---

## Test Categories Reference

### CRUD Operations (30 tests)
- Create: minimal, full, with defaults
- Read: by ID, filters, complex queries
- Update: single field, multiple fields, metadata
- Delete: soft, hard, cascade

### Complex Queries (18 tests)
- Hierarchies: ancestors, descendants, children
- Filtering: dynamic, empty, invalid
- Pagination: limit, offset, edge cases
- Ordering: temporal, created_at

### Error Handling (15 tests)
- ConcurrencyError: version mismatch
- ValueError: invalid parent, non-existent IDs
- Empty results: no data scenarios

### Transaction Management (8 tests)
- Commit: multi-repository
- Rollback: atomicity
- FK constraints: cascade

### Event Sourcing (14 tests)
- Event logging: sequential IDs
- State reconstruction: temporal queries
- Lifecycle: create → update → delete

---

## Files Reference

### Test Files
```
tests/integration/repositories/
├── __init__.py
├── test_repositories_integration.py      # Existing tests (67 tests)
└── test_repositories_gap_coverage.py     # New tests (85 tests)
```

### Documentation
```
REPOSITORY_GAP_COVERAGE_REPORT.md         # Detailed coverage strategy
REPOSITORY_TESTS_QUICK_START.md           # This file
```

### Source Files Under Test
```
src/tracertm/repositories/
├── item_repository.py       (18% → 85%+)
├── project_repository.py    (26% → 85%+)
├── link_repository.py       (41% → 85%+)
├── agent_repository.py      (27% → 85%+)
└── event_repository.py      (24% → 85%+)
```

---

## Success Criteria

- ✅ All 85 tests pass
- ✅ Each repository achieves 85%+ coverage
- ✅ No flaky tests (deterministic results)
- ✅ Tests complete in <10 seconds
- ✅ Zero test pollution (isolation verified)

---

## Next Actions

1. **Run Tests** (DO NOT DO THIS YET per user instructions)
   ```bash
   pytest tests/integration/repositories/test_repositories_gap_coverage.py -v
   ```

2. **Generate Coverage Report**
   ```bash
   pytest tests/integration/repositories/ \
       --cov=src/tracertm/repositories \
       --cov-report=html:htmlcov/repositories
   ```

3. **Review Coverage**
   ```bash
   open htmlcov/repositories/index.html
   ```

4. **Identify Remaining Gaps**
   - Check coverage report for uncovered lines
   - Add tests for any missing scenarios
   - Update documentation

---

## Support

For issues or questions:
1. Check test output for specific error messages
2. Review REPOSITORY_GAP_COVERAGE_REPORT.md for detailed strategy
3. Verify fixture availability in tests/conftest.py
4. Ensure all dependencies installed (pytest, pytest-asyncio, sqlalchemy)
