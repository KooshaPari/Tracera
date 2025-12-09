# Phase 2 WP-2.4: Quick Reference - 15 API Test Failures

## Status: 15 Failed / 123 Passed (10.9% failure rate)

## 3-Category Classification

### CATEGORY A: Easy Fixes (Test/Assertion Issues) - 3 tests

| Test | Issue | Fix | Time |
|------|-------|-----|------|
| `test_client_timeout_configuration` | httpx returns `Timeout` object, not float | Change `== 45.0` to `.timeout == 45.0` | 2 min |
| `test_ssl_configuration_passed_to_client` | `AsyncClient` doesn't expose `verify` attribute | Store `verify_ssl` in ApiClient OR remove assertion | 5 min |
| `test_webhook_retry_on_failure` | Mock call count not tracking properly | Fix mock async setup | 10 min |

**Total Time: 17 minutes** | **Fixability: 100%**

---

### CATEGORY B: Exception Handling (Implementation) - 3 tests

| Test | Issue | Fix | File | Time |
|------|-------|-----|------|------|
| `test_request_timeout_error` | `httpx.TimeoutException` not wrapped | Wrap in `NetworkError` | sync_client.py:330 | 10 min |
| `test_conflict_error_409` | 409 responses caught as generic `ApiError` | Add specific `ConflictError` handler | sync_client.py:330 | 10 min |
| `test_empty_response_body` | `health_check()` catches ValueError, suppresses it | Change to re-raise error | sync_client.py:410 | 5 min |

**Total Time: 25 minutes** | **Fixability: 100%**

---

### CATEGORY C: Session Isolation (Data Layer) - 7 tests

| Test | Issue | Root Cause | Fix | Time |
|------|-------|-----------|-----|------|
| `test_query_items_basic` | Returns 0 items | Session mismatch | Verify `query_items()` uses `self._session` | 15 min |
| `test_query_items_with_filter` | Returns 0 items | Session mismatch | Verify `query_items()` uses `self._session` | 5 min |
| `test_get_item_by_id` | Returns None | Session mismatch | Verify `get_item()` uses `self._session` | 5 min |
| `test_update_item_basic` | Item not found | Session mismatch | Verify `update_item()` uses `self._session` | 5 min |
| `test_delete_item` | Item not found | Session mismatch | Verify `delete_item()` uses `self._session` | 5 min |
| `test_batch_update_items` | Returns 0 updates | Session mismatch | Verify `batch_update_items()` uses `self._session` | 5 min |
| `test_batch_delete_items` | Returns 0 deletes | Session mismatch | Verify `batch_delete_items()` uses `self._session` | 5 min |

**Total Time: 45 minutes** | **Fixability: 95% (depends on code review)**

---

### CATEGORY D: Advanced (Not yet diagnosed) - 2 tests

| Test | Issue | Investigation |
|------|-------|-----------------|
| `test_get_agent_activity` | Returns 0 events | Session mismatch or query filter issue |
| `test_get_assigned_items` | Returns 0 items | Session mismatch or query filter issue |

**These are likely Category C issues once session audit is complete**

---

## By Difficulty Level

### TRIVIAL (5 minutes each)
- `test_client_timeout_configuration` - 1 line change in test

### EASY (10 minutes each)
- `test_ssl_configuration_passed_to_client` - Small implementation or test update
- `test_webhook_retry_on_failure` - Mock setup fix
- `test_request_timeout_error` - Add exception wrapper
- `test_conflict_error_409` - Add 409 handler
- `test_empty_response_body` - Change error handling

### MEDIUM (15 minutes each)
- Session isolation issues (7 tests) - Requires audit + verification

---

## Files to Modify

### Primary
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/api/sync_client.py`
  - Exception handling in `_retry_request()` (line 330)
  - `health_check()` error handling (line 410)

- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/api/client.py`
  - Query methods session usage verification
  - Batch operation methods

### Secondary
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/api/test_api_layer_full_coverage.py`
  - Line 864: Timeout assertion
  - Line 2074: SSL verification assertion
  - Line 1895: Mock setup

---

## Isolation vs Implementation Matrix

```
ISOLATION ISSUES (reset_mocks fixture should fix):
  - test_webhook_retry_on_failure (probably Mock state leak)
  └─ Status: Minor, already has reset_mocks fixture

SESSION/DATA ISSUES (isolation between tests):
  - test_query_items_* (7 tests)
  └─ Status: NOT isolation between tests, but session reuse within test
  └─ Root: Client methods not using provided session

IMPLEMENTATION ISSUES (code doesn't match test expectations):
  - test_client_timeout_configuration (httpx API change)
  - test_ssl_configuration_passed_to_client (httpx API limitation)
  - test_request_timeout_error (missing exception wrapper)
  - test_conflict_error_409 (missing 409 handler)
  - test_empty_response_body (error suppression)
  └─ Status: Code works but doesn't match test contract
```

---

## Test Execution Checklist

```
BEFORE YOU FIX:
- [ ] Read PHASE_2_WP_2_4_API_FAILURE_ANALYSIS.md (full details)
- [ ] Run pytest to confirm 15 failures
- [ ] Review client.py query methods for session usage

FIXING PHASE 1 (Easy - Test Updates):
- [ ] Fix test_client_timeout_configuration (test file line 864)
- [ ] Fix test_ssl_configuration_passed_to_client (test file line 2074)
- [ ] Fix test_webhook_retry_on_failure (test file line 1895)
- [ ] Run tests: expect 12 failures

FIXING PHASE 2 (Exception Handling):
- [ ] Add timeout exception wrapper in sync_client.py
- [ ] Add 409 conflict handler in sync_client.py
- [ ] Fix health_check() error handling in sync_client.py
- [ ] Run tests: expect 9 failures

FIXING PHASE 3 (Session Isolation - Critical):
- [ ] Audit query_items() - ensure uses self._session
- [ ] Audit get_item() - ensure uses self._session
- [ ] Audit update_item() - ensure uses self._session
- [ ] Audit delete_item() - ensure uses self._session
- [ ] Audit batch_update_items() - ensure uses self._session
- [ ] Audit batch_delete_items() - ensure uses self._session
- [ ] Audit get_agent_activity() - ensure uses self._session
- [ ] Audit get_assigned_items() - ensure uses self._session
- [ ] Run tests: expect 0 failures
```

---

## One-Liner Verification Commands

```bash
# Check timeout handling
grep -A 5 "def _retry_request" src/tracertm/api/sync_client.py | grep -i timeout

# Check 409 handling
grep -i "409\|conflict" src/tracertm/api/sync_client.py

# Check session usage in client
grep -n "self._session\|self._get_session\|Session(" src/tracertm/api/client.py | head -20

# Check health_check error handling
grep -A 10 "async def health_check" src/tracertm/api/sync_client.py

# Re-run tests
pytest tests/integration/api/test_api_layer_full_coverage.py -v --tb=short 2>&1 | grep -E "FAILED|passed"
```

---

## Estimated Total Fix Time

| Phase | Tests | Time | Difficulty |
|-------|-------|------|-----------|
| Phase 1: Test Updates | 3 | 20 min | TRIVIAL |
| Phase 2: Exception Handling | 3 | 25 min | EASY |
| Phase 3: Session Isolation | 7 | 45 min | MEDIUM |
| Phase 3b: Activity/Assigned | 2 | 15 min | MEDIUM |
| **TOTAL** | **15** | **1.5-2 hours** | **MEDIUM** |

---

## Success Criteria

✓ All 15 tests passing
✓ No new test failures introduced
✓ Code review confirms:
  - Exception types match test expectations
  - Session consistency across all methods
  - No hardcoded assumptions about httpx API

## Maintainability Notes

- Mark tests with `@pytest.mark.requires_session_audit` to track session-dependent tests
- Add docstring to all query methods: `"""Uses self._session if available, else creates new session."""`
- Document expected exception types in ApiClient docstring
- Consider adding a SessionValidator utility to catch these issues early
