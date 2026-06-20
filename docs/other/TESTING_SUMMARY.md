# Testing Summary

## Quick Stats

**Current Status** (as of Phase 8):
```
Tests Passing: 2,086 / 2,270 (92.6%)
Tests Failing: 166 (7.3%)
Tests Skipped: 18 (0.8%)
Code Coverage: 53.24%
```

**Progress Since Start**:
```
Phase 7 Start: 1,800 / 2,066 passing (87.1%)
Phase 8 Start: 2,048 / 2,266 passing (90.4%)
Phase 8 End:   2,086 / 2,270 passing (92.6%)

Improvement: +5.5 percentage points overall
Tests Added: +204 new tests
Tests Fixed: +286 tests now passing
```

## Test Organization

### Directory Structure
```
tests/
├── unit/               # Unit tests (fast, isolated)
│   ├── api/           # API endpoint tests
│   ├── cli/           # CLI command tests
│   ├── models/        # Model tests
│   ├── repositories/  # Repository tests
│   ├── services/      # Service layer tests
│   ├── storage/       # Storage backend tests
│   └── tui/           # TUI component tests
├── e2e/               # End-to-end tests (integration)
│   ├── test_cli_*.py  # CLI workflow tests
│   └── test_api_*.py  # API workflow tests
└── conftest.py        # Shared fixtures
```

### Test Counts by Category
```
CLI Tests:       487 (334 passing, 153 failing)
API Tests:        60 (59 passing, 1 failing)
E2E Tests:        36 (28 passing, 8 failing)
Model Tests:     200 (200 passing, 0 failing)
Repository:      150 (148 passing, 2 failing)
Service Tests:   400 (398 passing, 2 failing)
Storage Tests:   850 (850 passing, 0 failing)
TUI Tests:        87 (69 passing, 0 failing, 18 skipped)
```

## Coverage by Module

### High Coverage (>80%)
- ✅ `models/*` - 90-100%
- ✅ `storage/local_storage.py` - 81.88%
- ✅ `storage/conflict_resolver.py` - 87.20%
- ✅ `cli/storage_helper.py` - 90.78%
- ✅ `services/view_registry_service.py` - 88.73%

### Medium Coverage (50-80%)
- ⚠️ `cli/commands/*` - 50-70%
- ⚠️ `storage/file_watcher.py` - 61.51%
- ⚠️ `storage/markdown_parser.py` - 65.44%
- ⚠️ `services/impact_analysis_service.py` - 70.89%

### Low Coverage (<50%)
- ❌ `services/stateless_ingestion_service.py` - 20.04%
- ❌ `services/traceability_matrix_service.py` - 31.40%
- ❌ `storage/sync_engine.py` - 44.34%
- ❌ `tui/apps/*` - 20-30%

## Running Tests

### Quick Commands
```bash
# Run all tests
pytest tests/

# Run with coverage
coverage run -m pytest tests/
coverage report --include="src/*"

# Run specific category
pytest tests/unit/cli/
pytest tests/unit/api/
pytest tests/e2e/

# Run single test file
pytest tests/unit/cli/test_backup_commands.py

# Run single test
pytest tests/unit/cli/test_backup_commands.py::TestBackupCommand::test_backup_project_basic

# Run with verbose output
pytest tests/ -xvs

# Run failed tests only
pytest tests/ --lf

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

### Useful Flags
```bash
-q                  # Quiet output
-v                  # Verbose
-x                  # Stop on first failure
-s                  # Show print statements
--tb=short          # Short traceback
--tb=no             # No traceback
--lf                # Run last failed
--ff                # Run failed first
--durations=10      # Show 10 slowest tests
-k "test_name"      # Run tests matching pattern
-m "slow"           # Run tests with marker
--cov=src           # Coverage for src/
--cov-report=html   # HTML coverage report
```

## Common Test Patterns

### 1. CLI Command Testing
```python
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

runner = CliRunner()

@patch("tracertm.cli.storage_helper.get_current_project")
@patch("tracertm.storage.LocalStorageManager")
def test_command(mock_storage, mock_project):
    mock_project.return_value = ("proj-id", "Project")
    mock_storage.return_value = MagicMock()

    result = runner.invoke(app, ["command", "args"])

    assert result.exit_code == 0
    assert "expected output" in result.stdout
```

### 2. API Endpoint Testing
```python
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

@patch("tracertm.repositories.item_repository.ItemRepository")
def test_endpoint(mock_repo):
    repo_instance = MagicMock()
    repo_instance.get_by_project = AsyncMock(return_value=[])
    mock_repo.return_value = repo_instance

    client = TestClient(app)
    response = client.get("/api/v1/items?project_id=test")

    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}
```

### 3. Service Testing
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_service():
    service = MyService(db_session)
    result = await service.process()

    assert result is not None
```

### 4. Storage Testing
```python
def test_storage():
    storage = LocalStorageManager()
    item = storage.create_item(title="Test")

    assert item.id is not None
    assert storage.get_item(item.id) == item
```

## Mock Patterns

### Patching Rules
1. **Always patch at source**, not at import location
2. **Use AsyncMock** for async functions
3. **Patch decorators** at their definition location
4. **Use patch.object()** for monkey-patching instances

### Correct Patch Locations
```python
# ✓ CORRECT - Patch at source
@patch("tracertm.config.manager.ConfigManager")
@patch("tracertm.storage.LocalStorageManager")
@patch("tracertm.database.connection.DatabaseConnection")
@patch("tracertm.repositories.item_repository.ItemRepository")

# ✗ WRONG - Patch at import
@patch("tracertm.cli.commands.config.ConfigManager")
@patch("tracertm.cli.commands.backup.LocalStorageManager")
```

### Async Mocking
```python
from unittest.mock import AsyncMock

# For async methods
mock_repo = MagicMock()
mock_repo.get_item = AsyncMock(return_value=item)

# For async functions
with patch("module.async_func", new_callable=AsyncMock) as mock:
    mock.return_value = result
```

## Test Fixtures

### Common Fixtures (conftest.py)
```python
@pytest.fixture
def mock_config():
    """Mock ConfigManager with default values."""
    with patch("tracertm.config.manager.ConfigManager") as mock:
        config = MagicMock()
        config.get.side_effect = lambda k: {
            "database_url": "sqlite:///test.db",
            "current_project_id": "test-proj"
        }.get(k)
        mock.return_value = config
        yield mock

@pytest.fixture
def mock_storage():
    """Mock LocalStorageManager."""
    with patch("tracertm.storage.LocalStorageManager") as mock:
        storage = MagicMock()
        mock.return_value = storage
        yield storage

@pytest.fixture
def cli_runner():
    """CLI test runner."""
    return CliRunner()
```

## Known Issues & Workarounds

### Issue 1: Decorator Testing
**Problem**: Decorators execute before mocks
**Workaround**: Patch decorator functions at source
```python
# Instead of patching the wrapped function
@patch("tracertm.cli.storage_helper.get_current_project")
def test_command(mock_project):
    mock_project.return_value = ("id", "name")
```

### Issue 2: Import Timing
**Problem**: Import happens before patch
**Workaround**: Use `patch.object()` or import inside test
```python
# Use patch.object
with patch.object(module, "function", return_value=value):
    result = module.function()
```

### Issue 3: Complex Mock Chains
**Problem**: Multiple levels of mocking needed
**Workaround**: Use MagicMock with spec
```python
mock_storage = MagicMock()
mock_project_storage = MagicMock()
mock_item_storage = MagicMock()
mock_storage.get_project_storage.return_value = mock_project_storage
mock_project_storage.get_item_storage.return_value = mock_item_storage
```

## Test Development Workflow

### 1. Writing New Tests
```bash
# 1. Create test file
touch tests/unit/cli/test_new_command.py

# 2. Run to verify failure
pytest tests/unit/cli/test_new_command.py -x

# 3. Implement test
# 4. Run until passing
pytest tests/unit/cli/test_new_command.py -xvs

# 5. Run all related tests
pytest tests/unit/cli/ -q

# 6. Check coverage
pytest tests/unit/cli/test_new_command.py --cov=src/tracertm/cli/commands/new_command
```

### 2. Fixing Failing Tests
```bash
# 1. Identify failure
pytest tests/unit/cli/test_failing.py -xvs

# 2. Check mocks
grep "@patch" tests/unit/cli/test_failing.py

# 3. Check source imports
grep "import\|from" src/tracertm/cli/commands/failing.py

# 4. Fix patch location
# 5. Rerun
pytest tests/unit/cli/test_failing.py -xvs
```

### 3. Debugging Tests
```bash
# Add breakpoint in test
import pdb; pdb.set_trace()

# Run with pdb
pytest tests/unit/cli/test_failing.py -x --pdb

# Print mock calls
print(mock_function.call_args_list)
print(mock_function.call_count)
```

## CI/CD Integration

### GitHub Actions (planned)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [coverage.py documentation](https://coverage.readthedocs.io/)

### Project Documentation
- `PHASE_8_COMPLETION_REPORT.md` - Detailed Phase 8 results
- `PHASE_8_NEXT_STEPS.md` - Action plan for completing tests
- `tests/README.md` - Test suite documentation (to be created)

## Contact & Support

For questions about tests:
1. Check this document first
2. Review test examples in `tests/unit/`
3. Check Phase 8 reports for recent patterns
4. Ask in project chat/issues

---

*Last Updated: 2025-12-02*
*Phase: 8 (Test Suite Improvement)*
*Status: In Progress (92.6% pass rate)*
