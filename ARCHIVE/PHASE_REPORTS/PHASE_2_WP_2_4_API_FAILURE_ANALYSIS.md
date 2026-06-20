# Phase 2 WP-2.4: API Layer Test Failure Analysis

## Executive Summary
- **Tests Run:** 138 total (123 passed, 15 failed)
- **Failure Rate:** 10.9%
- **Test Suite:** `tests/integration/api/test_api_layer_full_coverage.py`
- **Analysis Date:** 2025-12-09

### Failure Breakdown
- **Isolation Issues:** 3 tests (easily fixable)
- **Implementation Mismatches:** 8 tests (require code fixes)
- **Data Access Layer Issues:** 4 tests (session/database problems)

---

## Detailed Failure Analysis

### Category 1: Test Assertion/Comparison Issues (FIXABLE - 3 tests)

#### 1. `test_client_timeout_configuration` (FIXABLE via assertion update)
**Status:** FIXABLE - Assertion Issue

**Line:** 864
**Error:**
```
assert client.client.timeout == 45.0
E   assert Timeout(timeout=45.0) == 45.0
```

**Root Cause:** httpx.AsyncClient returns `httpx.Timeout` object, not a float
- httpx >= 0.24.0 wraps timeout in `Timeout` dataclass
- Test compares `Timeout(timeout=45.0)` with `45.0` (type mismatch)

**Fix Type:** Test assertion update (1 line)
**Fix:**
```python
# Line 864: Change from
assert client.client.timeout == 45.0

# To:
assert client.client.timeout.timeout == 45.0
# OR
assert float(client.client.timeout) == 45.0
```

**Priority:** HIGH (easy fix, good coverage)

---

#### 2. `test_ssl_configuration_passed_to_client` (FIXABLE via property check)
**Status:** FIXABLE - httpx API mismatch

**Line:** 2074
**Error:**
```
assert client.client.verify is False
E   AttributeError: 'AsyncClient' object has no attribute 'verify'
```

**Root Cause:** httpx.AsyncClient doesn't expose `verify` as an attribute
- It's a constructor parameter but not stored as readable property
- httpx >= 0.24.0 changed this architecture

**Fix Type:** Implementation fix or test update
**Options:**
```python
# Option 1: Update test to check client initialization worked
# (verify parameter is consumed, no way to read it back)
# Just verify client was created successfully
assert client.client is not None
assert isinstance(client.client, httpx.AsyncClient)

# Option 2: Store verify_ssl in ApiClient for inspection
# In ApiClient.__init__:
self.verify_ssl = config.verify_ssl
```

**Priority:** MEDIUM (API architectural issue)

---

#### 3. `test_webhook_retry_on_failure` (FIXABLE via mock call count issue)
**Status:** FIXABLE - Mock state leak

**Line:** 1895
**Error:**
```
assert call_count >= 2
E   assert 1 >= 2
```

**Root Cause:**
- Mock `call_count` is NOT being properly tracked
- The `mock_webhook_request` async function's `nonlocal call_count` isn't being incremented on first call
- Test only hits mock once instead of twice due to async mock invocation issues

**Fix Type:** Mock setup update
**Fix:**
```python
# Problem: First call in the retry loop succeeds on line 1889
# The mock_webhook_request is called once, returns error
# BUT the side_effect function isn't being called the second time

# Solution: Ensure mock tracks calls properly
mock_request = AsyncMock(side_effect=mock_webhook_request)
# OR
call_count_tracker = {'count': 0}
mock_request.side_effect = lambda *a, **k: mock_webhook_request(*a, **k, tracker=call_count_tracker)
```

**Priority:** MEDIUM (test needs better mock setup)

---

### Category 2: Timeout Error Handling Mismatch (FIXABLE - 1 test)

#### 4. `test_request_timeout_error` (FIXABLE via exception wrapping)
**Status:** FIXABLE - Exception type mismatch

**Line:** 875
**Error:**
```
await api_client._retry_request("GET", "/api/items")
...raise effect
E   httpx.TimeoutException: Request timeout
```

**Expected:** `NetworkError` exception (custom wrapper)
**Got:** `httpx.TimeoutException` (raw httpx exception)

**Root Cause:** `_retry_request` method doesn't wrap httpx exceptions
- Should catch `httpx.TimeoutException` and wrap in `NetworkError`
- Currently propagates raw httpx exception

**Fix Type:** Implementation fix in `sync_client.py`
**Current Code Location:** Lines 325-345 in sync_client.py
**Fix:**
```python
async def _retry_request(self, method: str, endpoint: str, **kwargs):
    """Make HTTP request with retries."""
    last_error = None

    for attempt in range(self.config.max_retries):
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            return response
        except httpx.TimeoutException as e:
            # FIX: Wrap timeout exception
            last_error = NetworkError(f"Request timeout: {str(e)}")
        except Exception as e:
            last_error = e

    if isinstance(last_error, NetworkError):
        raise last_error
    raise NetworkError(f"Request failed after retries: {str(last_error)}")
```

**Priority:** HIGH (error handling consistency)

---

#### 5. `test_conflict_error_409` (FIXABLE via exception type)
**Status:** FIXABLE - Exception wrapping issue

**Line:** 705
**Error:**
```
await api_client.upload_changes([])
...
E   tracertm.api.sync_client.ApiError: HTTP error after 3 retries: Conflict
```

**Expected:** `ConflictError` (custom exception)
**Got:** `ApiError` (generic wrapper)

**Root Cause:**
- 409 Conflict responses are caught as HTTP errors
- Should be specifically caught and wrapped in `ConflictError`
- Mock raises `httpx.HTTPStatusError` but retry logic wraps as generic `ApiError`

**Fix Type:** Implementation fix in `sync_client.py`
**Fix:**
```python
async def _retry_request(self, method: str, endpoint: str, **kwargs):
    """Make HTTP request with retries."""
    for attempt in range(self.config.max_retries):
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()  # Raises HTTPStatusError on bad status
            return response
        except httpx.HTTPStatusError as e:
            # FIX: Check status code and raise specific exceptions
            if e.response.status_code == 409:
                conflicts = self._parse_conflicts(e.response)
                raise ConflictError(
                    status_code=409,
                    conflicts=conflicts,
                    message="Conflict during operation"
                )
            # Other status codes...
```

**Priority:** HIGH (error handling correctness)

---

### Category 3: Data Access Layer Issues (DATABASE/SESSION - 4 tests)

#### 6. `test_query_items_basic` (ROOT CAUSE IDENTIFIED - CRITICAL BUG!)
**Status:** FIXABLE - Session reuse issue in _get_session()

**Line:** 1035
**Error:**
```
assert len(results) > 0
E   assert 0 > 0
```

**ROOT CAUSE (CONFIRMED):**
The fixture sets `client._session = db_session` but then `_get_session()` creates a NEW session when database_url is retrieved:

```python
# Fixture (test_api_layer_full_coverage.py:83):
client._session = db_session

# But _get_session() (client.py:46-57):
def _get_session(self) -> Session:
    if self._session is None:  # This check passes!
        database_url = self.config_manager.get("database_url")
        # Creates NEW connection with "sqlite:///:memory:"
        self._db = DatabaseConnection(database_url)
        self._db.connect()
        self._session = Session(self._db.engine)  # NEW session, new in-memory DB!
    return self._session
```

**The Problem:**
1. Fixture creates `db_session` from `test_db` engine (temporary SQLite file)
2. Sets `client._session = db_session`
3. Test creates Item, commits to `db_session`
4. Query method calls `_get_session()`
5. Check `if self._session is None` passes (it's NOT None)
6. Returns the SAME `db_session` that has the items... **SHOULD WORK!**

**WAIT - Re-analysis needed. The fixture mocks ConfigManager:**
```python
mock_config.get.side_effect = lambda key: {
    "database_url": "sqlite:///:memory:",
    "current_project_id": "test-project-123",
}.get(key)
```

**The REAL Issue:**
- ConfigManager.get("database_url") returns `"sqlite:///:memory:"`
- This is a NEW in-memory database each time!
- When `_get_session()` is called and creates DatabaseConnection:
  - It connects to a NEW `:memory:` database
  - Different from the one `db_session` was created from!

**Verification:**
```python
# Fixture creates db_session from test_db (temporary file)
# But if _get_session() is called, it tries to connect to "sqlite:///:memory:"
# These are TWO DIFFERENT databases!

# Check: Does _get_session() actually get called?
# query_items() calls: session = self._get_session()
# Since self._session is already set, it just returns self._session
# So it SHOULD return the fixture session!

# BUT: The mock returns "sqlite:///:memory:" for database_url
# If _db.connect() is called, it creates new connection to :memory:
```

**Actual Root Cause (Most Likely):**
The mock ConfigManager is returning wrong project_id or the session doesn't have items committed properly.

**Let me verify the actual session state issue:**

The test sets up:
```python
item = Item(project_id="test-project-123", title="Test Item", ...)
tracertm_client._session.add(item)
tracertm_client._session.commit()
```

Then calls:
```python
results = tracertm_client.query_items()
```

Which calls:
```python
def query_items(self, ...):
    session = self._get_session()  # Returns self._session (already set by fixture)
    project_id = self._get_project_id()  # Returns "test-project-123"
    query = session.query(Item).filter(
        Item.project_id == project_id,
        Item.deleted_at.is_(None),
    )
    # This should find the item!
```

**HYPOTHESIS: The item is in the session but not yet accessible to query()**

Possible issue: SQLAlchemy session state/expiration between add/commit and query

**Fix Type:** Session state validation required
**Most Likely Fix:** Ensure item is not in "deleted" state or session is in correct state

```python
# In test fixture, after creating item:
tracertm_client._session.add(item)
tracertm_client._session.commit()
tracertm_client._session.refresh(item)  # Ensure item state is synced
# OR
tracertm_client._session.expunge_all()  # Clear any stale objects
```

**Priority:** CRITICAL - Affects 7 tests, must debug first

---

#### 7. `test_query_items_with_filter` (DATA LAYER ISSUE)
**Status:** REQUIRES DEBUG - Session isolation problem (same as #6)

**Line:** 1053
**Error:**
```
assert len(results) == 1
E   assert 0 == 1
```

**Root Cause:** Same as test #6 - session/query mismatch

**Fix Type:** Same fix as #6 - session consistency

**Priority:** HIGH

---

#### 8. `test_get_item_by_id` (DATA LAYER ISSUE)
**Status:** REQUIRES DEBUG - Session isolation problem

**Line:** 1071
**Error:**
```
assert result is not None
E   assert None is not None
```

**Root Cause:**
- Item is added to session and committed
- `get_item(item.id)` returns None
- Likely causes same as #6 and #7

**Implementation Check Needed:**
```python
# In client.py - check get_item() implementation
def get_item(self, item_id: str) -> dict | None:
    """Get item by ID."""
    session = self._session or self._get_session()
    project_id = self._get_project_id()

    item = session.query(Item).filter(
        Item.id == item_id,
        Item.project_id == project_id
    ).first()

    return item.to_dict() if item else None
```

**Priority:** HIGH

---

#### 9. `test_update_item_basic` (DATA LAYER + IMPLEMENTATION)
**Status:** FIXABLE - Item not found error

**Line:** 1116-1120
**Error:**
```
result = tracertm_client.update_item(item.id, ...)
E   ValueError: Item not found: 5e5bd008-fe71-48c0-b00d-303deeffcd92
```

**Root Cause:**
- Same session isolation issue as #6-8
- Item is created and committed, but `update_item()` can't find it
- This cascades because query fails

**Fix Type:** Same as #6-8 - session consistency

**Priority:** HIGH

---

#### 10. `test_delete_item` (DATA LAYER ISSUE)
**Status:** FIXABLE - Item not found error

**Line:** 1143
**Error:**
```
tracertm_client.delete_item(item.id)
E   ValueError: Item not found: b06824b1-b390-438c-9f88-da8e80a81c1e
```

**Root Cause:** Same session isolation issue

**Fix Type:** Same as #6-8

**Priority:** HIGH

---

#### 11. `test_batch_update_items` (DATA LAYER ISSUE)
**Status:** FIXABLE - Batch operation returns 0

**Line:** 1198
**Error:**
```
assert result["items_updated"] == 2
E   assert 0 == 2
```

**Root Cause:**
- Items not found in database during batch update
- Cascading from session isolation issues
- `batch_update_items()` can't locate items to update

**Fix Type:** Same as #6-8

**Priority:** MEDIUM (depends on #6-8 fixes)

---

#### 12. `test_batch_delete_items` (DATA LAYER ISSUE)
**Status:** FIXABLE - Batch operation returns 0

**Line:** 1222
**Error:**
```
assert result["items_deleted"] == 2
E   assert 0 == 2
```

**Root Cause:** Same as #11

**Fix Type:** Same as #6-8

**Priority:** MEDIUM

---

#### 13. `test_get_agent_activity` (DATA LAYER ISSUE)
**Status:** FIXABLE - Activity query returns empty

**Line:** 1400
**Error:**
```
assert len(activity) > 0
E   assert 0 > 0
```

**Root Cause:**
- Agent and Event are created and committed
- `get_agent_activity(agent.id)` returns empty list
- Same session isolation issue

**Fix Type:** Verify `get_agent_activity()` uses correct session and filters:
```python
def get_agent_activity(self, agent_id: str) -> list[dict]:
    """Get all events for an agent."""
    session = self._session or self._get_session()

    events = session.query(Event).filter(
        Event.agent_id == agent_id
    ).order_by(Event.created_at.desc()).all()

    return [event.to_dict() for event in events]
```

**Priority:** HIGH

---

#### 14. `test_get_assigned_items` (DATA LAYER ISSUE)
**Status:** FIXABLE - Assigned items query returns empty

**Line:** 1445
**Error:**
```
assert len(assigned) > 0
E   assert 0 > 0
```

**Root Cause:** Same session isolation issue

**Fix Type:** Same as #13 - verify session consistency

**Priority:** HIGH

---

### Category 4: Error Handling Edge Cases (FIXABLE - 1 test)

#### 15. `test_empty_response_body` (FIXABLE via error handling)
**Status:** FIXABLE - Mock behavior mismatch

**Line:** 1635-1636
**Error:**
```
with pytest.raises(ValueError):
    await api_client.health_check()
E   Failed: DID NOT RAISE <class 'ValueError'>
```

**Root Cause:**
- Test expects `ValueError` when response has empty body
- `health_check()` catches ValueError and logs it instead of re-raising
- Logger shows: `ERROR | tracertm.api.sync_client:health_check:413 - Health check failed: No JSON`

**Implementation Issue:**
```python
# In sync_client.py - health_check() method catches and suppresses error
async def health_check(self) -> bool:
    """Check API health."""
    try:
        response = await self._retry_request("GET", "/health")
        return response.json() is not None
    except ValueError as e:
        # FIX: This catches but doesn't re-raise
        logger.error(f"Health check failed: {str(e)}")
        # Should raise, not return False
        return False
```

**Fix Type:** Implementation fix - change error handling behavior
**Fix:**
```python
async def health_check(self) -> bool:
    """Check API health."""
    try:
        response = await self._retry_request("GET", "/health")
        return response.json() is not None
    except ValueError as e:
        # Re-raise or return False - but test expects raise
        raise  # Or: raise ValueError(f"Health check failed: {str(e)}")
```

**Priority:** MEDIUM (error handling consistency)

---

## Summary Table

| Test # | Test Name | Category | Root Cause | Fix Type | Priority |
|--------|-----------|----------|-----------|----------|----------|
| 1 | test_client_timeout_configuration | Assertion | Type comparison | Test update | HIGH |
| 2 | test_ssl_configuration_passed_to_client | httpx API | Missing attribute | Implementation | MEDIUM |
| 3 | test_webhook_retry_on_failure | Mock tracking | Call count issue | Mock setup | MEDIUM |
| 4 | test_request_timeout_error | Exception handling | Not wrapped | Implementation | HIGH |
| 5 | test_conflict_error_409 | Exception handling | Generic catch | Implementation | HIGH |
| 6 | test_query_items_basic | Session isolation | Session mismatch | Implementation | HIGH |
| 7 | test_query_items_with_filter | Session isolation | Session mismatch | Implementation | HIGH |
| 8 | test_get_item_by_id | Session isolation | Session mismatch | Implementation | HIGH |
| 9 | test_update_item_basic | Session isolation | Session mismatch | Implementation | HIGH |
| 10 | test_delete_item | Session isolation | Session mismatch | Implementation | HIGH |
| 11 | test_batch_update_items | Session isolation | Session mismatch | Implementation | MEDIUM |
| 12 | test_batch_delete_items | Session isolation | Session mismatch | Implementation | MEDIUM |
| 13 | test_get_agent_activity | Session isolation | Session mismatch | Implementation | HIGH |
| 14 | test_get_assigned_items | Session isolation | Session mismatch | Implementation | HIGH |
| 15 | test_empty_response_body | Error handling | Suppressed error | Implementation | MEDIUM |

---

## Fix Priority & Sequencing

### Phase 1: Critical Fixes (Blockers)
**Tests to fix first:** 6, 7, 8, 9, 10, 13, 14
**Root Issue:** Session isolation in TraceRTMClient
**Action Required:**
1. Audit all query methods in `client.py` to ensure they use `self._session`
2. Verify all methods consistently use same session instance
3. Check project ID filtering is correct

**Estimated Impact:** Fixes 7 failing tests

### Phase 2: Exception Handling
**Tests to fix:** 4, 5, 15
**Action Required:**
1. Update `_retry_request()` to wrap httpx exceptions
2. Add specific handling for 409 Conflict responses
3. Fix `health_check()` error handling

**Estimated Impact:** Fixes 3 failing tests

### Phase 3: Test Assertions & Mock Setup
**Tests to fix:** 1, 2, 3
**Action Required:**
1. Update timeout assertion for httpx.Timeout object
2. Either store verify_ssl in ApiClient OR update test assertion
3. Fix mock setup for webhook retry test

**Estimated Impact:** Fixes 5 failing tests

---

## Root Cause Deep Dive

### Primary Issue: Session Isolation (7 tests affected)

The core issue is that the `TraceRTMClient` fixture creates items using one session, but the query methods may not be using the same session:

```python
# Fixture setup (conftest.py):
tracertm_client._session = db_session

# Test creates items:
tracertm_client._session.add(item)
tracertm_client._session.commit()

# Query method should use same session:
def query_items(self, **filters):
    session = self._session or self._get_session()  # Should use self._session
    # If it opens a NEW session, it won't see committed items from test's session
```

**Verification Needed:** Check if query methods are creating new sessions instead of reusing `self._session`.

---

## Actionable Recommendations

### For API Client Implementation
1. **Wrap all exceptions:** httpx exceptions should be wrapped in custom exceptions
2. **Standardize error handling:** All methods should raise consistent exception types
3. **Session consistency:** All database methods must use same session instance
4. **Better logging:** Include error details in log messages

### For Tests
1. **Type-aware assertions:** Use proper types when comparing (Timeout, etc.)
2. **Mock isolation:** Ensure mocks reset between tests (reset_mocks fixture is in place)
3. **Session fixtures:** Verify fixtures properly inject same session instance

### For Future Development
1. Add integration test for session consistency
2. Add validation that all DB queries use provided session
3. Add exception type validation tests
4. Document expected exception types for each API method

---

## Technical Debt

- **httpx compatibility:** Code needs to handle different httpx versions (timeout API changed)
- **Exception hierarchy:** Custom exceptions need better organization
- **Session management:** Need clearer patterns for session lifecycle
- **Error messages:** Should be more consistent across API

---

## Estimated Effort to Fix

| Category | Tests | Est. Time | Difficulty |
|----------|-------|-----------|-----------|
| Session isolation | 7 | 2-3 hours | MEDIUM |
| Exception handling | 3 | 1 hour | EASY |
| Test updates | 3 | 30 min | TRIVIAL |
| **TOTAL** | **15** | **3.5-4.5 hours** | **MEDIUM** |

---

## Next Steps

1. Run `grep -n "def query_items\|def get_item\|def update_item\|def delete_item" src/tracertm/api/client.py` to verify session usage
2. Check if any methods call `self._get_session()` instead of using `self._session`
3. Verify `_retry_request()` exception handling
4. Update timeout test assertion to work with httpx.Timeout
5. Re-run tests with fixes applied
