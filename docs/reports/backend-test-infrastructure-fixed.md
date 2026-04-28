# Backend Test Infrastructure Fixes

**Date**: 2026-02-01
**Status**: ✅ Resolved
**Task**: Fix pytest-asyncio compatibility and test collection failures

## Summary

Fixed critical pytest-asyncio plugin auto-discovery failure that was preventing all async tests from running. The issue was not a version incompatibility but rather a plugin registration problem requiring manual intervention.

## Issues Identified

### 1. pytest-asyncio Plugin Auto-Discovery Failure ⚠️ CRITICAL

**Problem**: pytest-asyncio was installed and had correct entry points, but pytest was not auto-discovering the plugin, causing all async tests to be skipped.

**Root Cause**: Unknown pytest-asyncio entry point discovery issue in the current Python environment. Despite:
- Correct entry point registration (`pytest11` group)
- Successfully loading via `importlib.metadata.entry_points()`
- No `PYTEST_DISABLE_PLUGIN_AUTOLOAD` set
- Multiple version combinations tested (pytest 8.2.2-8.4.2, pytest-asyncio 0.23.7-1.3.0)

The plugin would not auto-load through normal pytest mechanisms.

**Solution**: Created custom conftest.py that manually registers pytest-asyncio plugin during `pytest_configure` hook.

**Files Modified**:
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/conftest.py` (created)
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/pytest.ini` (updated)

**Final Working Configuration**:
```ini
[pytest]
# pytest.ini
python_files = test_*.py
python_classes = Test*
python_functions = test_*

testpaths = integration

# Asyncio configuration (pytest-asyncio 0.23.7)
asyncio_mode = auto

markers =
    e2e: End-to-end integration tests requiring all infrastructure
    slow: Tests that take more than 5 seconds
    oauth: Tests requiring OAuth mock/setup
    temporal: Tests requiring Temporal test environment
    skip_ci: Tests to skip in CI environment
    asyncio: Async tests using pytest-asyncio

addopts =
    -v
    --strict-markers
    --tb=short
```

```python
# conftest.py (root level)
"""
Root conftest with manual pytest-asyncio integration.
Works around pytest-asyncio auto-discovery issues.
"""
import pytest

def pytest_configure(config):
    """Manually register pytest-asyncio plugin."""
    try:
        from pytest_asyncio import plugin as asyncio_plugin
        config.pluginmanager.register(asyncio_plugin, name="asyncio")
        print("✓ pytest-asyncio plugin registered successfully")
    except Exception as e:
        print(f"✗ Failed to register pytest-asyncio: {e}")

    # Register asyncio marker
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio coroutine"
    )
```

### 2. Version Compatibility Matrix

**Tested Combinations**:

| pytest | pytest-asyncio | Status | Notes |
|--------|----------------|--------|-------|
| 8.4.2 | 0.23.8 | ❌ Failed | Config options not recognized |
| 8.4.2 | 0.24.0 | ❌ Failed | Plugin not auto-discovered |
| 8.4.2 | 1.3.0 | ❌ Failed | Plugin not auto-discovered |
| 8.3.4 | 0.24.0 | ❌ Failed | Plugin not auto-discovered |
| 8.3.4 | 1.3.0 | ❌ Failed | Plugin not auto-discovered |
| 8.2.2 | 0.23.7 | ✅ Works | With manual registration |

**Recommended Versions**:
```
pytest==8.2.2
pytest-asyncio==0.23.7
```

### 3. Integration Test Collection Issues

**Status**: Partially resolved - pytest-asyncio now works, but model import errors block collection.

**Remaining Issues**:
```python
AttributeError: 'str' object has no attribute 'value'
# In: tracertm.models.problem.py:114
# default=ProblemStatus.OPEN.value
```

This is a separate issue from pytest-asyncio and needs to be addressed in the models layer.

## Testing Results

### Simple Async Test ✅
```bash
$ cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests
$ python -m pytest test_async_simple.py -v

✓ pytest-asyncio plugin registered successfully
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-8.2.2, pluggy-1.6.0
rootdir: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests
configfile: pytest.ini
asyncio: mode=Mode.AUTO
collecting ... collected 2 items

test_async_simple.py::test_simple_async PASSED                           [ 50%]
test_async_simple.py::test_simple_async_auto PASSED                      [100%]

============================== 2 passed in 0.05s ===============================
```

### Integration Tests 🟡
```bash
$ python -m pytest --collect-only

# Collection blocked by model import errors (not pytest-asyncio issue)
```

## Implementation Details

### Conftest.py Structure

The solution uses a two-level conftest structure:

1. **Root `/tests/conftest.py`**: Manually registers pytest-asyncio plugin
2. **Integration `/tests/integration/conftest.py`**: Provides test fixtures (PostgreSQL, Neo4j, Redis, MinIO, NATS, Temporal)

### Why Manual Registration Works

The manual registration bypasses pytest's entry point discovery mechanism and directly:
1. Imports the pytest-asyncio plugin module
2. Registers it with pytest's plugin manager
3. Configures the `asyncio` marker

This ensures the plugin hooks are active before test collection begins.

## Verification Steps

1. ✅ Async tests with `@pytest.mark.asyncio` decorator work
2. ✅ Async tests without decorator work (auto mode)
3. ✅ pytest-asyncio fixtures (`@pytest_asyncio.fixture`) work
4. ✅ Test collection shows `asyncio: mode=Mode.AUTO`
5. 🟡 Full integration test suite collection (blocked by model issues)

## Next Steps

### Immediate
1. ✅ pytest-asyncio working - COMPLETE
2. ⏭️ Fix model import errors (ProblemStatus enum)
3. ⏭️ Verify all 54 integration tests collect successfully
4. ⏭️ Address any HTTPX 0.28.x API compatibility issues (if needed)
5. ⏭️ Fix storage service Go test issues (separate from Python)

### Future Improvements
1. Investigate root cause of entry point discovery failure
2. Consider filing bug report with pytest-asyncio if reproducible
3. Document workaround for other developers
4. Add CI check to ensure conftest.py manual registration stays in place

## Configuration Files

### pytest.ini Location
```
/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/pytest.ini
```

### conftest.py Locations
```
/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/conftest.py (root)
/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/integration/conftest.py (fixtures)
```

## References

- pytest-asyncio GitHub: https://github.com/pytest-dev/pytest-asyncio
- pytest Plugin Documentation: https://docs.pytest.org/en/stable/how-to/plugins.html
- Issue Tracking: Task #145 - Fix backend test infrastructure (pytest-asyncio)

## Conclusion

The core pytest-asyncio infrastructure issue is **RESOLVED**. Async tests now execute properly with pytest 8.2.2 and pytest-asyncio 0.23.7 using manual plugin registration. Remaining test collection issues are related to model layer import errors, not the test infrastructure itself.

**Impact**: Unblocks all async test development and execution for the backend test suite.
