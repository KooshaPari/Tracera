# Phase 3C: Patterns Documented

## Pytest-Asyncio Configuration Patterns

### Pattern 1: Explicit Plugin Loading (CRITICAL)

**Problem:** pytest-asyncio not auto-loading despite being installed

**Solution:** Add explicit plugin loading in pyproject.toml
```toml
[tool.pytest.ini_options]
addopts = [
    "-p",
    "asyncio",
]
```

**Why it works:** Forces pytest to load the asyncio plugin before test collection

---

### Pattern 2: Plugin Registration in conftest.py

**Problem:** Async tests need plugin registered early

**Solution:** Add plugin registration before imports
```python
# conftest.py - FIRST LINE after docstring
pytest_plugins = ["pytest_asyncio"]

# Then import other modules
import asyncio
import pytest
...
```

**Why it works:** Ensures plugin is registered before any test collection

---

### Pattern 3: Async Fixture Decorators

**Problem:** Async fixtures using @pytest.fixture cause collection issues

**Solution:** Use @pytest_asyncio.fixture for async fixtures
```python
# WRONG:
@pytest.fixture
async def my_async_fixture():
    ...

# CORRECT:
@pytest_asyncio.fixture
async def my_async_fixture():
    ...
```

**Why it works:** pytest_asyncio decorator properly handles async fixtures

---

### Pattern 4: Strict Mode Configuration

**Problem:** Need consistent async test behavior

**Solution:** Configure strict mode in pyproject.toml
```toml
[tool.pytest_asyncio]
asyncio_mode = "strict"
asyncio_default_fixture_loop_scope = "function"
```

**Why it works:**
- `strict` mode requires explicit `@pytest.mark.asyncio` on tests
- `function` scope creates new event loop per test (isolation)

---

### Pattern 5: Warning Suppression

**Problem:** Harmless pytest assertion rewrite warnings clutter output

**Solution:** Add warning filter
```toml
[tool.pytest.ini_options]
filterwarnings = [
    "ignore::pytest.PytestAssertRewriteWarning",
]
```

**Why it works:** Suppresses non-critical warnings about module imports

---

## Common Async Test Patterns

### Test Structure
```python
import pytest


@pytest.mark.asyncio
async def test_my_async_function():
    """Test async function."""
    result = await my_async_function()
    assert result == expected
```

### Using Async Fixtures
```python
@pytest.mark.asyncio
async def test_with_db_session(db_session):
    """Test using async database session."""
    # db_session is AsyncSession
    db_session.add(item)
    await db_session.flush()
    assert item.id is not None
```

### Service Tests
```python
@pytest.mark.asyncio
async def test_service_method(db_session):
    """Test service with database."""
    service = MyService(db_session)
    result = await service.do_something()
    assert result.success
```

---

## Troubleshooting Guide

### Issue: "async def functions are not natively supported"
**Cause:** pytest-asyncio not loaded
**Fix:** Add `-p asyncio` to addopts in pyproject.toml

### Issue: "AttributeError: 'async_generator' object has no attribute 'add'"
**Cause:** Fixture returns generator instead of session
**Fix:** Ensure fixture uses `async with` pattern and yields session

### Issue: "PytestAssertRewriteWarning: Module already imported"
**Cause:** pytest_asyncio imported after pytest_plugins declaration
**Fix:** Don't import pytest_asyncio, just use pytest_plugins declaration

### Issue: Tests collected as `<Function>` instead of `<PytestAsyncioFunction>`
**Cause:** Plugin not converting async functions
**Fix:** Verify `-p asyncio` in addopts and pytest_plugins in conftest

---

## Configuration Checklist

- [ ] `pytest_plugins = ["pytest_asyncio"]` in conftest.py (first line)
- [ ] `-p asyncio` in pyproject.toml addopts
- [ ] `asyncio_mode = "strict"` in [tool.pytest_asyncio]
- [ ] `asyncio_default_fixture_loop_scope = "function"` in [tool.pytest_asyncio]
- [ ] `@pytest_asyncio.fixture` for async fixtures
- [ ] `@pytest.mark.asyncio` on async tests
- [ ] Warning filter for PytestAssertRewriteWarning

---

## Example Test Files

### Minimal Async Test
```python
# test_example.py
import asyncio
import pytest


@pytest.mark.asyncio
async def test_async_sleep():
    """Test async sleep."""
    await asyncio.sleep(0.001)
    assert True
```

### Service Test with Database
```python
# test_service.py
import pytest
from tracertm.services.my_service import MyService


@pytest.mark.asyncio
async def test_service_create(db_session):
    """Test service create method."""
    service = MyService(db_session)
    result = await service.create(name="test")
    assert result.id is not None
    assert result.name == "test"
```

### Repository Test
```python
# test_repository.py
import pytest
from tracertm.repositories.my_repository import MyRepository


@pytest.mark.asyncio
async def test_repository_get_all(db_session):
    """Test repository get_all method."""
    repo = MyRepository(db_session)
    items = await repo.get_all()
    assert isinstance(items, list)
```

---

## References

- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest Plugin Documentation](https://docs.pytest.org/en/stable/how-to/plugins.html)
- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-02
**Phase:** 3C - Pytest-Asyncio Configuration
