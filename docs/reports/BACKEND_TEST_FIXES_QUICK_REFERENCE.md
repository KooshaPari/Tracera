# Backend Test Fixes - Quick Reference

**Date**: 2026-02-01
**Status**: Fixes Applied

## Summary of Changes

### 1. Fixed Async Fixture Issues (✅ COMPLETE)

**Files Modified**:
- `backend/tests/__init__.py` - Created to make tests a proper Python package
- `backend/tests/integration/__init__.py` - Created to make integration tests importable
- `backend/tests/integration/conftest.py` - Fixed 3 async fixtures
- `backend/tests/pytest.ini` - Updated to load pytest-asyncio plugin

**Changes in conftest.py**:

```python
# BEFORE (BROKEN):
@pytest_asyncio.fixture(scope="session")
async def postgres_sessionmaker(postgres_engine):
    """Create session factory."""
    return async_sessionmaker(  # ❌ Direct return in async fixture
        postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

# AFTER (FIXED):
@pytest_asyncio.fixture(scope="session")
async def postgres_sessionmaker(postgres_engine):
    """Create session factory."""
    sessionmaker = async_sessionmaker(
        postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield sessionmaker  # ✅ Proper yield
```

Similar fixes applied to:
- `nats_jetstream` fixture
- `event_publisher` fixture

### 2. Removed Missing Import (✅ COMPLETE)

**File**: `backend/tests/integration/conftest.py`

```python
# BEFORE (BROKEN):
from tracertm.workflows.activities import (
    create_session_checkpoint,
    cleanup_old_checkpoints,  # ❌ Function doesn't exist
)

# AFTER (FIXED):
from tracertm.workflows.activities import (
    create_session_checkpoint,
)
```

## Remaining Issues (❌ BLOCKING)

### Issue #1: pytest-asyncio Incompatibility with pytest 9.x

**Symptom**:
```
Failed: async def functions are not natively supported.
ERROR: '' requested an async fixture 'neo4j_driver', with no plugin or hook that handled it.
```

**Root Cause**:
- pytest 9.0.2 (latest) has breaking changes
- pytest-asyncio 1.3.0 is not compatible with pytest 9.x
- Configuration options `asyncio_mode` and `asyncio_default_fixture_loop_scope` are not recognized

**Solution**:
```bash
# Option A: Downgrade pytest
pip install 'pytest<9.0' pytest-asyncio==1.3.0

# Option B: Upgrade pytest-asyncio (when available)
pip install --upgrade pytest-asyncio  # Requires version 2.x or later

# Option C: Pin to compatible versions
pip install pytest==8.3.4 pytest-asyncio==0.24.0
```

**Affected Tests**: All 54 Python integration tests in `backend/tests/integration/`

### Issue #2: HTTPX/Starlette TestClient API Change

**Symptom**:
```
TypeError: Client.__init__() got an unexpected keyword argument 'app'
```

**Root Cause**:
- httpx 0.28.x removed the `app` parameter from Client.__init__()
- TestClient from starlette/fastapi internally uses httpx.Client
- Module-level TestClient instantiation fails during test collection

**Solution**:

```python
# BEFORE (BROKEN):
from fastapi.testclient import TestClient
from tracertm.api.main import app

client = TestClient(app)  # ❌ Fails with httpx 0.28.x

class TestSomething:
    def test_endpoint(self):
        response = client.get("/endpoint")
        assert response.status_code == 200

# AFTER (FIXED - Option A: Fixture):
import pytest
from fastapi.testclient import TestClient
from tracertm.api.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

class TestSomething:
    def test_endpoint(self, client):
        response = client.get("/endpoint")
        assert response.status_code == 200

# AFTER (FIXED - Option B: Context Manager):
from fastapi.testclient import TestClient
from tracertm.api.main import app

class TestSomething:
    def test_endpoint(self):
        with TestClient(app) as client:
            response = client.get("/endpoint")
            assert response.status_code == 200

# AFTER (FIXED - Option C: Downgrade httpx):
pip install 'httpx<0.28'
```

**Affected Files** (5 total):
1. `tests/unit/api/test_analysis_api.py`
2. `tests/unit/api/test_api_endpoints_final.py`
3. `tests/unit/api/test_api_routes.py`
4. `tests/unit/api/test_items_api.py`
5. `tests/unit/api/test_links_api.py`

### Issue #3: Missing Import - `_format_datetime`

**File**: `tests/unit/cli/commands/test_sync_comprehensive.py`

**Error**:
```python
ImportError: cannot import name '_format_datetime' from 'tracertm.cli.commands.sync'
```

**Solution**:
```python
# BEFORE (BROKEN):
from tracertm.cli.commands.sync import (
    sync,
    _format_datetime,  # ❌ Function doesn't exist
)

# AFTER (FIXED - Option A: Remove unused import):
from tracertm.cli.commands.sync import sync

# AFTER (FIXED - Option B: Implement the function if needed):
# In tracertm/cli/commands/sync.py:
from datetime import datetime

def _format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
```

### Issue #4: Missing Import - `Date`

**File**: `tests/unit/services/test_specification_service.py`

**Error**:
```python
NameError: name 'Date' is not defined
```

**Solution**:
```python
# Add missing import at top of file:
from datetime import date as Date  # or
from typing import Date  # depending on usage
```

## Quick Fix Script

```bash
#!/bin/bash
# Quick fix for backend test issues

echo "Step 1: Fix pytest/pytest-asyncio versions"
pip install pytest==8.3.4 pytest-asyncio==0.24.0

echo "Step 2: Fix httpx version (temporary workaround)"
pip install 'httpx<0.28'

echo "Step 3: Test if fixes work"
cd backend/tests
python -m pytest integration/test_checkpoint_resume.py::test_checkpoint_creation -v

echo "Step 4: Run all integration tests"
python -m pytest integration/ -v --tb=short

echo "Step 5: Run unit tests"
cd ../..
python -m pytest tests/unit/ -v -k "cache or search or handler" --tb=line
```

## Test Execution Commands

### Backend Integration Tests
```bash
cd backend/tests
python -m pytest integration/ -v --tb=short
python -m pytest integration/test_checkpoint_resume.py -v
python -m pytest integration/test_full_agent_lifecycle.py -v
```

### Main Unit Tests (Cache, Search, Handler)
```bash
python -m pytest tests/unit/ -v -k "cache"
python -m pytest tests/unit/ -v -k "search"
python -m pytest tests/unit/ -v -k "handler"
python -m pytest tests/unit/ -v -k "cache or search or handler"
```

### Go Backend Tests
```bash
cd backend/tests
go test -v ./...
go test -v ./integration/cache/...
go test -v ./integration/search/...
```

## Expected Test Counts

Based on task #132:
- Cache tests: 3 failures expected
- Search tests: 2 failures expected
- Handler tests: ~10 failures expected
- **Total**: ~15 tests to fix

Actual test counts found:
- Python integration tests: 54 tests (all blocked)
- Python unit tests matching filter: 215 tests (7 collection errors blocking)
- Go tests: Unknown (build failures prevent collection)

## Next Actions

1. ✅ **DONE**: Fix async fixture returns → yields
2. ✅ **DONE**: Remove missing import (`cleanup_old_checkpoints`)
3. ✅ **DONE**: Add `__init__.py` files to test directories
4. ⏳ **TODO**: Fix pytest/pytest-asyncio version compatibility
5. ⏳ **TODO**: Fix HTTPX TestClient usage (5 files)
6. ⏳ **TODO**: Fix missing imports (2 files)
7. ⏳ **TODO**: Re-run tests to identify actual failures
8. ⏳ **TODO**: Fix identified test logic failures

## File Manifest

### Modified Files (3):
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/integration/conftest.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/pytest.ini`
- (Import fix - no file change needed, function doesn't exist)

### Created Files (2):
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/__init__.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/integration/__init__.py`

### Files Requiring Fixes (7):
1. `tests/unit/api/test_analysis_api.py` - TestClient usage
2. `tests/unit/api/test_api_endpoints_final.py` - TestClient usage
3. `tests/unit/api/test_api_routes.py` - TestClient usage
4. `tests/unit/api/test_items_api.py` - TestClient usage
5. `tests/unit/api/test_links_api.py` - TestClient usage
6. `tests/unit/cli/commands/test_sync_comprehensive.py` - Missing import
7. `tests/unit/services/test_specification_service.py` - Missing import

## Documentation

- Analysis: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/reports/BACKEND_TEST_FAILURE_ANALYSIS.md`
- Quick Reference: This file
