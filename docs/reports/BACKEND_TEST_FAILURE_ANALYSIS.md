# Backend Test Failure Analysis

**Date**: 2026-02-01
**Task**: #132 - Fix remaining backend test failures

## Summary

The task requested fixing 15 backend test failures across three categories:
- Cache: 3 tests
- Search: 2 tests
- Handlers: ~10 tests

## Investigation Findings

### Test Infrastructure Issues

#### 1. Backend Integration Tests (`backend/tests/integration/`)

**Status**: Currently unable to run due to pytest-asyncio configuration issues

**Issues Found**:
- Missing `__init__.py` files in test directories (**FIXED**)
- Async fixtures returning values instead of yielding (**FIXED**):
  - `postgres_sessionmaker` - now yields
  - `nats_jetstream` - now yields
  - `event_publisher` - now yields
- pytest-asyncio v1.3.0 incompatibility with pytest 9.0.2
  - Error: "async def functions are not natively supported"
  - Error: "requested an async fixture with no plugin or hook that handled it"

**Files Modified**:
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/__init__.py` - Created
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/integration/__init__.py` - Created
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/integration/conftest.py` - Fixed 3 async fixtures
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/pytest.ini` - Updated asyncio configuration

**Python Integration Tests** (54 tests total):
- `test_checkpoint_resume.py` - 10 tests
- `test_full_agent_lifecycle.py` - 3 tests
- `test_minio_snapshots.py` - 8 tests
- `test_nats_events.py` - 11 tests
- `test_oauth_flow.py` - 13 tests
- `test_session_persistence.py` - 9 tests

**Remaining Issue**:
The pytest-asyncio plugin is not properly recognizing async test functions despite:
- Being installed (v1.3.0)
- Being explicitly loaded via `-p pytest_asyncio`
- Having async fixtures decorated with `@pytest_asyncio.fixture`
- Having async tests marked with `@pytest.mark.asyncio`

This appears to be a version compatibility issue between pytest 9.0.2 and pytest-asyncio 1.3.0.

#### 2. Main Unit Tests (`tests/unit/`)

**Status**: Collection errors prevent running cache/search/handler tests

**Collection Errors Found**:

1. **HTTPX Client API Change** (5 files):
   - `test_analysis_api.py`
   - `test_api_endpoints_final.py`
   - `test_api_routes.py`
   - `test_items_api.py`
   - `test_links_api.py`
   - Error: `TypeError: Client.__init__() got an unexpected keyword argument 'app'`
   - **Cause**: HTTPX v0.28.x removed the `app` parameter; use `transport` with `ASGITransport` instead

2. **Import Error**:
   - `test_sync_comprehensive.py`
   - Error: `ImportError: cannot import name '_format_datetime'`
   - **Cause**: Function `_format_datetime` doesn't exist in `tracertm.cli.commands.sync`

3. **NameError**:
   - `test_specification_service.py`
   - Error: `NameError: name 'Date' is not defined`
   - **Cause**: Missing import for `Date` type

**Test Count**: 215 tests selected with `-k "cache or search or handler"` filter (out of 6989 total)

#### 3. Go Backend Tests (`backend/tests/`)

**Status**: Build failures due to missing dependencies

**Go Tests Exist**:
- `integration/cache/redis_integration_test.go`
- `integration/search/fulltext_integration_test.go`
- `integration/search/vector_integration_test.go`
- Various handler tests (`agent_handler_test.go`, `item_handler_test.go`, `link_handler_test.go`)

**Issues**:
- Missing `go.sum` entries for vault API
- Missing `go.sum` entry for miniredis
- API syntax errors (`server.Close()` returns no value but used as value)
- Docker daemon not running for testcontainers

## Recommended Fixes

### High Priority

1. **Upgrade pytest-asyncio** to version compatible with pytest 9.x:
   ```bash
   pip install --upgrade pytest-asyncio
   ```

2. **Fix HTTPX Client Usage** in 5 API test files:
   ```python
   # OLD (broken):
   from httpx import Client
   client = Client(app=app)

   # NEW (working):
   from httpx import AsyncClient, ASGITransport
   transport = ASGITransport(app=app)
   async with AsyncClient(transport=transport, base_url="http://test") as client:
       # test code
   ```

3. **Fix Missing Imports**:
   - Add `Date` import to `test_specification_service.py`
   - Remove `_format_datetime` import from `test_sync_comprehensive.py` or implement the function

### Medium Priority

4. **Fix Go Dependencies**:
   ```bash
   cd backend/tests
   go get github.com/kooshapari/tracertm-backend/internal/vault@v0.0.0
   go get -t github.com/kooshapari/tracertm-backend/tests/integration
   ```

5. **Fix Go API Syntax Errors** in `backend/tests/api/agents_test.go` and `api/graph_test.go`:
   ```go
   // OLD:
   defer server.Close()

   // NEW:
   server.Close()
   ```

### Low Priority

6. **Start Infrastructure** for integration tests:
   - PostgreSQL on port 5432
   - Neo4j on port 7687
   - Redis on port 6379
   - MinIO on port 9000
   - NATS on port 4222

## Test Failure Breakdown

Based on task description expectations:

| Category | Expected Failures | Actual Status |
|----------|-------------------|---------------|
| Cache | 3 tests | Unable to run - collection/config errors |
| Search | 2 tests | Unable to run - collection/config errors |
| Handlers | ~10 tests | Unable to run - collection/config errors |
| **Total** | **15 tests** | **0 ran, all blocked** |

## Next Steps

1. Upgrade pytest-asyncio to latest version
2. Fix HTTPX Client API usage in 5 test files
3. Fix remaining import errors (2 files)
4. Re-run test suite to identify actual test failures
5. Fix Go test build errors
6. Document which specific cache/search/handler tests are failing

## Files Requiring Fixes

### Python Test Files

1. `tests/unit/api/test_analysis_api.py` - HTTPX Client API
2. `tests/unit/api/test_api_endpoints_final.py` - HTTPX Client API
3. `tests/unit/api/test_api_routes.py` - HTTPX Client API
4. `tests/unit/api/test_items_api.py` - HTTPX Client API
5. `tests/unit/api/test_links_api.py` - HTTPX Client API
6. `tests/unit/cli/commands/test_sync_comprehensive.py` - Missing import
7. `tests/unit/services/test_specification_service.py` - Missing Date import

### Go Test Files

8. `backend/tests/api/agents_test.go` - server.Close() syntax
9. `backend/tests/api/graph_test.go` - server.Close() syntax
10. `backend/tests/go.mod` - Add missing dependencies

### Configuration Files

11. `backend/tests/pytest.ini` - Already updated
12. `backend/tests/integration/conftest.py` - Already fixed

## Conclusion

The backend tests cannot currently run due to infrastructure and configuration issues. The immediate blockers are:

1. pytest-asyncio version incompatibility
2. HTTPX API changes
3. Missing imports
4. Go dependency issues

Once these are resolved, the actual test failures in cache, search, and handler components can be identified and fixed.
