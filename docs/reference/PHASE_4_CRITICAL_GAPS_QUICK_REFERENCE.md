# Phase 4: Critical Gaps Quick Reference

## The 3 Critical Blockers

### 1. OAuth Token Exchange (Lines 191-208)

**File:** `backend/tests/integration/test_oauth_flow.py:191`

**Problem:** OAuth callback doesn't exchange authorization code for access token

**What's missing:**
```python
# Currently: test is skipped
# Needed: Full token exchange implementation
# - Authorization code validation
# - Provider API call (handled by mock server)
# - Access token retrieval
# - Token storage
```

**Fix location:**
- Backend: `backend/internal/auth/oauth.go` (or similar)
- Need mock OAuth server at `http://localhost:5555`

**Test when fixed:**
```bash
pytest backend/tests/integration/test_oauth_flow.py::test_oauth_callback_token_exchange -xvs
```

**Acceptance:** Test passes, access_token in response

---

### 2. WebSocket Authentication (Frontend)

**File:** `frontend/apps/web/src/hooks/useRealtime.ts:29`

**Problem:**
```typescript
// TODO: Replace with your actual auth token retrieval
const token = localStorage.getItem('auth_token');
```

**What's wrong:**
- Tokens in localStorage = XSS vulnerability
- No token refresh on expiry
- No connection validation
- Backend WebSocket middleware doesn't exist

**What to build:**
1. Move token to sessionStorage + React context
2. Add refresh endpoint (POST /auth/refresh)
3. Add WebSocket auth middleware (Go)
4. Implement auto-reconnect with new token

**Test when fixed:**
```bash
# Manual: npm run dev, check Network tab for WebSocket headers
# Automated: src/__tests__/api/websocket.test.ts
npm run test -- websocket.test.ts
```

**Acceptance:**
- Auth header in WebSocket open handshake
- Token refreshes automatically
- Failed auth closes connection

---

### 3. API Error Handling (Frontend)

**File:** `frontend/apps/web/src/components/forms/CreateItemDialog.tsx:71,86`

**Problem:**
```typescript
// TODO: Replace with actual API call (line 71)
// TODO: Show error notification (line 86)
```

**What's wrong:**
- Item creation uses placeholder code
- No error feedback to user
- No retry mechanism
- Mutations can silently fail

**What to build:**
1. Implement actual API call with error handling
2. Add toast notification on error
3. Queue mutation for offline retry
4. Show user-friendly error message

**Test when fixed:**
```bash
# Unit test
npm run test -- CreateItemDialog.test.tsx

# Integration test
npm run test -- app-integration.test.tsx --grep "should generate report"
```

**Acceptance:**
- Item creation works
- Errors show toast message
- Retries work automatically
- Failed mutations queued

---

## Quick Fix Checklist

### For OAuth (3 tasks, do in order)

- [ ] **Task 1:** Create mock OAuth provider at `http://localhost:5555`
  - Endpoint: `POST /token` returns `{"access_token": "...", "expires_in": 3600}`
  - Use: faker + express (2 hour setup)

- [ ] **Task 2:** Implement token exchange in Go backend
  - File: `backend/internal/auth/oauth.go`
  - Calls mock provider, stores token
  - Add endpoint: `POST /auth/oauth/callback`
  - (2 hour implementation)

- [ ] **Task 3:** Validate all 6 OAuth tests pass
  - `pytest backend/tests/integration/test_oauth_flow.py -xvs`
  - Should pass with green checkmarks
  - (1 hour debugging if needed)

### For WebSocket (3 tasks, can parallel to OAuth)

- [ ] **Task 1:** Move token storage to sessionStorage
  - File: `frontend/apps/web/src/api/auth.ts`
  - Implement `getAuthToken()` function
  - Use: React context for reactivity
  - (1.5 hour)

- [ ] **Task 2:** Add token refresh endpoint
  - File: `backend/internal/auth/refresh.go`
  - Endpoint: `POST /auth/refresh`
  - Returns new token if old one expiring
  - (1.5 hour)

- [ ] **Task 3:** Wire WebSocket auth in Go
  - File: `backend/internal/handlers/websocket.go`
  - Check Authorization header on upgrade
  - Reject if token invalid/missing
  - (1.5 hour)

### For Error Handling (2 tasks)

- [ ] **Task 1:** Implement CreateItem API call
  - File: `frontend/apps/web/src/components/forms/CreateItemDialog.tsx`
  - Replace TODO with actual `createItem()` call
  - Add try/catch with error handling
  - (1 hour)

- [ ] **Task 2:** Add toast notifications
  - File: `frontend/apps/web/src/api/client-errors.ts`
  - Implement `showErrorToast(error)` function
  - Export for all API calls to use
  - (0.5 hours)

---

## Testing Checklist

### Before you commit:

**OAuth:**
```bash
# All 6 OAuth tests pass
pytest backend/tests/integration/test_oauth_flow.py -v

# Expected output:
# test_oauth_callback_token_exchange PASSED
# test_oauth_callback_invalid_state PASSED
# test_oauth_session_creation PASSED
# test_oauth_error_handling[...] PASSED (2x)
# test_oauth_rate_limiting PASSED
```

**WebSocket:**
```bash
# WebSocket test passes
npm run test -- websocket.test.ts

# Expected: all tests PASSED
# WebSocket connects with Authorization header
# Token refreshes on expiry
# New token works after reconnect
```

**Error Handling:**
```bash
# Integration tests pass
npm run test -- app-integration.test.tsx

# Expected: tests for reports, search, offline sync all PASSED
```

---

## Debugging Guide

### OAuth not working?

**Check mock server:**
```bash
curl -X POST http://localhost:5555/token \
  -H "Content-Type: application/json" \
  -d '{"code": "test", "grant_type": "authorization_code"}'
# Should return: {"access_token": "...", "expires_in": 3600}
```

**Check backend logs:**
```bash
grep -i oauth .process-compose/logs/go-backend.log
# Should see: "OAuth token exchange", "Session created"
```

### WebSocket auth not working?

**Check headers in browser:**
1. Open DevTools → Network
2. Find WebSocket connection (filter: "ws")
3. Click on it → Frames
4. Look for "Authorization: Bearer ..." in first frame

**Check logs:**
```bash
grep -i websocket .process-compose/logs/go-backend.log
# Should see: "WebSocket upgrade", "Auth valid", "Connected"
```

### API errors not showing?

**Check network:**
1. DevTools → Network
2. Find failed request
3. Click → Response tab
4. Should see error JSON

**Check frontend logs:**
```bash
grep -i "ERROR\|catch" .process-compose/logs/frontend.log
# Should see error handling code running
```

---

## Files to Change

**OAuth:**
- [ ] `backend/internal/auth/oauth.go` - NEW file for OAuth flow
- [ ] `backend/tests/integration/test_oauth_flow.py` - Uncomment 6 tests
- [ ] `backend/internal/handlers/auth.go` - Add callback endpoint
- [ ] `.process-compose.yaml` - Add mock OAuth server

**WebSocket:**
- [ ] `frontend/apps/web/src/api/auth.ts` - Move to sessionStorage
- [ ] `backend/internal/auth/refresh.go` - NEW endpoint
- [ ] `backend/internal/handlers/websocket.go` - Add auth middleware
- [ ] `frontend/apps/web/src/hooks/useRealtime.ts` - Use new auth

**Error Handling:**
- [ ] `frontend/apps/web/src/components/forms/CreateItemDialog.tsx` - Implement API call
- [ ] `frontend/apps/web/src/api/client-errors.ts` - Add error toast function
- [ ] `frontend/apps/web/src/__tests__/integration/app-integration.test.tsx` - Uncomment 8 tests

---

## Success = These All Pass

```bash
# OAuth
pytest backend/tests/integration/test_oauth_flow.py::test_oauth_callback_token_exchange -xvs
pytest backend/tests/integration/test_oauth_flow.py::test_oauth_callback_invalid_state -xvs
pytest backend/tests/integration/test_oauth_flow.py::test_oauth_session_creation -xvs
pytest backend/tests/integration/test_oauth_flow.py::test_oauth_error_handling -xvs
pytest backend/tests/integration/test_oauth_flow.py::test_oauth_rate_limiting -xvs

# WebSocket
npm run test -- websocket.test.ts

# Error Handling
npm run test -- app-integration.test.tsx --grep "should generate report on button click"
npm run test -- app-integration.test.tsx --grep "should perform search on input"
npm run test -- app-integration.test.tsx --grep "should handle offline-to-online sync"

# All together
make test-all
# Should see: ✅ All tests passed (0 failed)
```

---

## Time Estimate

- **OAuth:** 7 hours (with mock server)
- **WebSocket:** 6 hours (token + refresh + middleware)
- **Error Handling:** 3 hours (API + notifications)
- **Testing + debugging:** 4 hours
- **Total:** 20 hours (2.5 days with 3 parallel agents)

---

## Don't Forget

1. **Security:**
   - [ ] No tokens in localStorage
   - [ ] CSRF tokens on state param
   - [ ] Token refresh before expiry
   - [ ] Secure cookie flags set

2. **Error Handling:**
   - [ ] Network errors caught
   - [ ] User sees messages
   - [ ] Offline queue works
   - [ ] Retries happen

3. **Testing:**
   - [ ] All critical tests passing
   - [ ] No flaky tests
   - [ ] Tests run <1 second each
   - [ ] Coverage >95%

4. **Documentation:**
   - [ ] Update README with auth flow
   - [ ] Add OAuth setup instructions
   - [ ] Document error handling
   - [ ] Add troubleshooting guide

---

## Questions?

See full document: `docs/reports/REMAINING_GAPS_AND_PHASE_4_ROADMAP.md`
