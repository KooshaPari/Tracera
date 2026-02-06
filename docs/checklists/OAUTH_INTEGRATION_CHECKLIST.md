# OAuth Integration Implementation Checklist

**Phase:** 4.1 Critical Gap #1
**Status:** Core infrastructure complete, integration pending
**Date Created:** 2026-02-05

## Pre-Integration Verification

- [ ] All unit tests pass locally
  ```bash
  cd backend
  go test ./internal/auth/... -v
  go test ./internal/cliproxy/... -v
  go test ./internal/sessions/... -v
  ```

- [ ] Database migration ready
  ```bash
  # File: internal/db/migrations/20260205000000_create_sessions_table.sql
  # Status: ✅ Created
  ```

- [ ] Dependencies verified
  - [ ] Redis client: `github.com/redis/go-redis/v9`
  - [ ] Crypto libraries: standard `crypto/*`
  - [ ] Database: `pgx` for PostgreSQL
  - [ ] Echo framework: `github.com/labstack/echo/v4`

## Task #7: Create Mock OAuth Provider

**Assignee:** oauth-implementer
**Estimated Time:** 1 hour
**Complexity:** Medium

### Implementation Steps

- [ ] Create file: `backend/tests/mocks/oauth_provider.go`
  - [ ] Mock OAuth provider struct
  - [ ] Start/stop methods
  - [ ] Configurable behavior (success/failure scenarios)

- [ ] Implement endpoints
  - [ ] GET `/authorize` → returns auth code in query params
  - [ ] POST `/token` → exchanges code for token
  - [ ] State parameter validation
  - [ ] Error responses (invalid_grant, invalid_request, etc)

- [ ] RFC 6749 Compliance
  - [ ] Proper error response format
  - [ ] Correct HTTP status codes
  - [ ] Required/optional fields in responses

- [ ] Testing
  - [ ] Mock provider can start/stop cleanly
  - [ ] Token endpoint validates client credentials
  - [ ] State parameter is validated
  - [ ] Error scenarios return correct errors

### Acceptance Criteria

- ✅ Mock provider implements RFC 6749 endpoints
- ✅ Proper error handling for all scenarios
- ✅ No external dependencies (use httptest.Server)
- ✅ Can be used in Python integration tests via conftest.py

### Code Location

**File:** `backend/tests/mocks/oauth_provider.go`

**Example Usage:**
```go
provider := NewMockOAuthProvider()
defer provider.Close()

// Use provider.URL in ProviderConfig
config := &cliproxy.ProviderConfig{
    BaseURL: provider.URL,
}
```

---

## Task #8: Wire Service.go + Error Handling

**Assignee:** oauth-implementer
**Estimated Time:** 1.5 hours
**Complexity:** Medium-High

### Implementation Steps

- [ ] Update `internal/cliproxy/service.go`
  - [ ] Add StateTokenManager field
  - [ ] Add SessionService field
  - [ ] Initialize in NewService()

- [ ] Update handleAuthorize()
  - [ ] Generate state token
  - [ ] Include state in authorization URL
  - [ ] Store state in Redis (already done in StateTokenManager)

- [ ] Update handleCallback()
  - [ ] Extract code, state, provider from query params
  - [ ] Validate provider exists
  - [ ] Call ValidateStateAndExchangeToken()
  - [ ] Create session via SessionService
  - [ ] Return access_token + session_id to client

- [ ] Error Handling
  - [ ] Missing code → 400 Bad Request
  - [ ] Missing state → 400 Bad Request
  - [ ] Invalid state → 400 Bad Request (with security logging)
  - [ ] Unknown provider → 400 Bad Request
  - [ ] Token exchange failure → 500 Internal Server Error
  - [ ] Session creation failure → 500 Internal Server Error

- [ ] Logging
  - [ ] Log state validation
  - [ ] Log token exchange (NO tokens in logs)
  - [ ] Log session creation
  - [ ] Include request ID for tracing
  - [ ] Do NOT log: tokens, credentials, private data

- [ ] Response Format
  - [ ] Success: { access_token, token_type, expires_in, session_id }
  - [ ] Error: { error, error_description, state }

### Code Modifications

**File:** `internal/cliproxy/service.go`

**handleCallback() Pseudocode:**
```go
func (service *Service) handleCallback(echoCtx echo.Context) error {
    code := echoCtx.QueryParam("code")
    state := echoCtx.QueryParam("state")
    provider := echoCtx.QueryParam("provider")

    // Validate inputs
    if code == "" { return 400 "missing code" }
    if provider == "" { provider = service.config.DefaultProvider }

    providerCfg := service.getProvider(provider)
    if providerCfg == nil { return 400 "unknown provider" }

    // Exchange token + validate state
    tokenResp, err := service.ValidateStateAndExchangeToken(
        echoCtx.Request().Context(),
        service.stateManager,
        providerCfg,
        state,
        code,
    )
    if err != nil { return 400 with error details }

    // Create session
    sessionReq := &sessions.CreateSessionRequest{
        UserID:      extractUserIDFromToken(tokenResp),
        Provider:    provider,
        AccessToken: tokenResp.AccessToken,
        ExpiresIn:   time.Duration(tokenResp.ExpiresIn) * time.Second,
    }

    sessionResp, err := service.sessionService.CreateSession(
        echoCtx.Request().Context(),
        sessionReq,
    )
    if err != nil { return 500 "session creation failed" }

    // Return response
    return echoCtx.JSON(200, map[string]interface{}{
        "access_token": tokenResp.AccessToken,
        "token_type": tokenResp.TokenType,
        "expires_in": tokenResp.ExpiresIn,
        "session_id": sessionResp.SessionID,
    })
}
```

### Acceptance Criteria

- ✅ handleCallback() validates state parameter
- ✅ handleCallback() exchanges code for token
- ✅ handleCallback() creates session in PostgreSQL + Neo4j
- ✅ All error responses follow RFC 6749 format
- ✅ No tokens/credentials in logs
- ✅ Proper HTTP status codes (400, 500)
- ✅ Request ID tracking for debugging

---

## Task #9: Enable Python Integration Tests

**Assignee:** test-runner
**Estimated Time:** 45 minutes
**Complexity:** Low

### Implementation Steps

- [ ] Create conftest.py test fixture
  - [ ] Mock OAuth provider fixture
  - [ ] Start provider before tests
  - [ ] Stop provider after tests
  - [ ] Configure CLIProxy to use mock provider

- [ ] Update test_oauth_flow.py
  - [ ] Line 191: Remove `@pytest.mark.skip` from test_oauth_callback_token_exchange
  - [ ] Line 234: Remove `@pytest.mark.skip` from test_oauth_callback_invalid_state
  - [ ] Line 272: Remove `@pytest.mark.skip` from test_oauth_session_creation
  - [ ] (Optional) Line 325: test_oauth_provider_timeout
  - [ ] (Optional) Line 341: test_oauth_provider_error
  - [ ] (Optional) Line 389: test_oauth_rate_limiting

- [ ] Wire mock provider into tests
  - [ ] Pass mock provider URL to ProviderConfig
  - [ ] Ensure state tokens work with mock provider
  - [ ] Verify token exchange completes

- [ ] Run test suite
  ```bash
  cd backend
  python -m pytest tests/integration/test_oauth_flow.py -v
  ```

- [ ] Verify test results
  - [ ] ✅ test_oauth_callback_token_exchange PASSED
  - [ ] ✅ test_oauth_callback_invalid_state PASSED
  - [ ] ✅ test_oauth_session_creation PASSED
  - [ ] ✅ Coverage ≥90%
  - [ ] ✅ No failures

### Code Changes

**File:** `backend/tests/integration/conftest.py`

**Example Fixture:**
```python
import pytest
from tests.mocks.oauth_provider import MockOAuthProvider

@pytest.fixture(scope="session")
def mock_oauth_provider():
    provider = MockOAuthProvider()
    provider.start()
    yield provider
    provider.stop()

@pytest.fixture(scope="function")
def oauth_config(mock_oauth_provider):
    return {
        "name": "claude",
        "type": "anthropic",
        "client_id": "test-client",
        "client_secret": "test-secret",
        "redirect_uri": "http://localhost:8080/oauth/callback",
        "base_url": mock_oauth_provider.url,
    }
```

**File:** `backend/tests/integration/test_oauth_flow.py`

**Example Test:**
```python
@pytest.mark.e2e
@pytest.mark.oauth
@pytest.mark.asyncio
# Remove: @pytest.mark.skip(reason="...")
async def test_oauth_callback_token_exchange():
    """Test OAuth callback with valid code exchanges for token."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CLIPROXY_BASE_URL}/oauth/callback",
            params={
                "code": "mock-authorization-code",
                "provider": "claude",
                "state": "mock-state",
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["access_token"] is not None
        assert "session_id" in data
```

### Acceptance Criteria

- ✅ All 6 OAuth tests enabled and passing
- ✅ test_oauth_callback_token_exchange passes
- ✅ test_oauth_callback_invalid_state passes
- ✅ test_oauth_session_creation passes
- ✅ Coverage ≥90%
- ✅ No test failures
- ✅ Tests can be run repeatedly (idempotent)

---

## Integration Testing

### Before Merging

- [ ] Run all unit tests
  ```bash
  cd backend
  go test ./... -v -cover
  ```

- [ ] Run Python integration tests
  ```bash
  python -m pytest tests/integration/test_oauth_flow.py -v --cov
  ```

- [ ] Check code coverage
  ```bash
  # Should be ≥90% for new code
  ```

- [ ] Run linters
  ```bash
  go vet ./internal/auth/...
  go vet ./internal/cliproxy/...
  go vet ./internal/sessions/...
  ```

- [ ] Manual testing
  - [ ] Start backend locally
  - [ ] Trigger /oauth/authorize endpoint
  - [ ] Verify state token is generated
  - [ ] Trigger /oauth/callback with mock code
  - [ ] Verify token is exchanged
  - [ ] Verify session is created in PostgreSQL
  - [ ] Verify user node created in Neo4j

### Deployment

- [ ] Database migration applied
- [ ] OAuth provider credentials configured
- [ ] Environment variables set
- [ ] Redis running and accessible
- [ ] Test suite passes with ≥90% coverage
- [ ] Security review completed
- [ ] Monitoring/alerting configured

---

## Checklist Completion

When all items are checked:

1. Update this file: Mark as COMPLETE
2. Update docs/reports/PHASE_4.1_OAUTH_IMPLEMENTATION_SUMMARY.md: Mark as COMPLETE
3. Create docs/reports/PHASE_4.1_OAUTH_COMPLETION_REPORT.md
4. Commit all changes with PR
5. Close issue/epic

---

## Related Documentation

- **OAuth Implementation Guide:** `docs/reports/PHASE_4.1_OAUTH_IMPLEMENTATION_SUMMARY.md`
- **Architecture Guide:** `OAUTH_IMPLEMENTATION_GUIDE.md`
- **State Token Manager:** `internal/auth/oauth_state.go`
- **OAuth Handler:** `internal/cliproxy/oauth_handler.go`
- **Session Service:** `internal/sessions/session_service.go`
- **Database Schema:** `internal/db/migrations/20260205000000_create_sessions_table.sql`

---

**Last Updated:** 2026-02-05
**Status:** Ready for integration work
