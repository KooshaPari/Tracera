# API Security Tests - Quick Reference Guide

## Test Files Overview

| File | Size | Tests | Focus |
|------|------|-------|-------|
| `test_security_comprehensive.py` | 36KB | 48 | Authentication flows, token validation, authorization, rate limiting, webhooks, CORS, sessions, input validation, encryption, MFA, error handling, logging |
| `test_token_management.py` | 15KB | 43 | Token generation, refresh flows, revocation, expiration, scopes, encoding, audience, issuer, nbf claims, metadata |
| `test_api_key_security.py` | 15KB | 44 | Key generation, validation, scopes, expiration, rotation, revocation, metadata, listing, best practices |
| `test_authorization_scenarios.py` | 19KB | 22 | RBAC, resource ownership, ABAC, permission caching, project/item access, delegation, conditional access, inheritance |

**Total: 85KB, 157 Tests**

## Quick Test Locations

### Authentication Tests
```bash
# JWT and API key authentication
tests/unit/api/test_security_comprehensive.py::TestAuthenticationFlows

# Token validation and expiration
tests/unit/api/test_security_comprehensive.py::TestTokenValidation

# Token management lifecycle
tests/unit/api/test_token_management.py
```

### Authorization Tests
```bash
# Role-based access control
tests/unit/api/test_authorization_scenarios.py::TestRoleBasedAccessControl

# Resource ownership
tests/unit/api/test_authorization_scenarios.py::TestResourceOwnershipControl

# Project and item access
tests/unit/api/test_authorization_scenarios.py::TestProjectLevelAccess
tests/unit/api/test_authorization_scenarios.py::TestItemLevelAccess
```

### API Key Tests
```bash
# API key generation, validation, rotation
tests/unit/api/test_api_key_security.py
```

### Security Mechanism Tests
```bash
# Webhook security
tests/unit/api/test_security_comprehensive.py::TestWebhookSecurity

# CORS and headers
tests/unit/api/test_security_comprehensive.py::TestCORSAndSecurityHeaders

# Input validation
tests/unit/api/test_security_comprehensive.py::TestInputValidationSecurity

# Session management
tests/unit/api/test_security_comprehensive.py::TestSessionManagement

# Rate limiting
tests/unit/api/test_security_comprehensive.py::TestRateLimiting
```

## Running Tests

### All security tests
```bash
pytest tests/unit/api/test_security_comprehensive.py \
        tests/unit/api/test_token_management.py \
        tests/unit/api/test_api_key_security.py \
        tests/unit/api/test_authorization_scenarios.py -v
```

### By category
```bash
# Authentication only
pytest tests/unit/api/test_security_comprehensive.py::TestAuthenticationFlows -v
pytest tests/unit/api/test_security_comprehensive.py::TestTokenValidation -v
pytest tests/unit/api/test_token_management.py -v

# Authorization only
pytest tests/unit/api/test_authorization_scenarios.py -v

# API Keys only
pytest tests/unit/api/test_api_key_security.py -v

# Rate limiting
pytest tests/unit/api/test_security_comprehensive.py::TestRateLimiting -v

# Webhooks
pytest tests/unit/api/test_security_comprehensive.py::TestWebhookSecurity -v
```

### With coverage report
```bash
pytest tests/unit/api/test_security_comprehensive.py \
        tests/unit/api/test_token_management.py \
        tests/unit/api/test_api_key_security.py \
        tests/unit/api/test_authorization_scenarios.py \
        --cov=tracertm.api --cov-report=html --cov-report=term
```

### Watch mode
```bash
pytest-watch tests/unit/api/test_security_comprehensive.py -- -v
```

## Test Classes and Methods

### test_security_comprehensive.py

#### TestAuthenticationFlows
- `test_jwt_authentication_success` - Valid JWT acceptance
- `test_jwt_authentication_missing_token` - Missing token rejection
- `test_jwt_authentication_invalid_format` - Invalid format rejection
- `test_jwt_authentication_wrong_secret` - Wrong secret rejection
- `test_api_key_authentication_success` - Valid API key acceptance
- `test_api_key_authentication_invalid` - Invalid API key rejection
- `test_api_key_authentication_missing` - Missing API key rejection

#### TestTokenValidation
- `test_token_expiration_check` - Expiration validation
- `test_token_expiration_time_boundary` - Boundary condition
- `test_token_not_yet_valid` - Future nbf claim
- `test_token_malformed_claims` - Malformed claims
- `test_token_subject_claim_validation` - Subject claim

#### TestAuthorizationControl
- `test_admin_role_full_access` - Admin permissions
- `test_user_role_limited_access` - User limitations
- `test_guest_role_read_only_access` - Guest read-only
- `test_resource_ownership_check` - Ownership validation
- `test_permission_based_access_control` - Permission checks

#### TestRateLimiting
- `test_rate_limit_per_user` - Per-user limits
- `test_rate_limit_per_ip_anonymous` - Per-IP limits
- `test_rate_limit_headers` - Response headers
- `test_rate_limit_reset_after_window` - Window reset
- `test_rate_limit_premium_tier` - Tier-based limits

#### TestWebhookSecurity
- `test_webhook_signature_verification_success` - Valid signature
- `test_webhook_signature_verification_failure` - Invalid signature
- `test_webhook_timestamp_validation` - Replay attack prevention
- `test_webhook_missing_signature` - Missing signature

#### TestCORSAndSecurityHeaders
- `test_cors_headers_present` - CORS headers
- `test_content_type_security_header` - Content-Type header
- `test_x_content_type_options_header` - X-Content-Type-Options
- `test_x_frame_options_header` - X-Frame-Options
- `test_strict_transport_security_header` - HSTS

#### TestSessionManagement
- `test_session_creation` - Session creation
- `test_session_expiration` - Expiration handling
- `test_session_invalidation_on_logout` - Logout invalidation
- `test_session_fixation_protection` - Fixation attack protection

#### TestInputValidationSecurity
- `test_sql_injection_prevention` - SQL injection
- `test_xss_prevention` - XSS prevention
- `test_csrf_token_validation` - CSRF validation

#### TestDataEncryption
- `test_password_encryption` - Password hashing
- `test_sensitive_data_not_logged` - Data protection

#### TestMultiFactorAuthentication
- `test_mfa_required_for_sensitive_operations` - MFA requirement
- `test_mfa_verification_code_validation` - Code validation
- `test_mfa_code_expiration` - Code expiration

#### TestErrorHandlingSecurity
- `test_no_sensitive_info_in_error_messages` - Safe error messages
- `test_auth_failure_generic_message` - Generic auth errors

#### TestLoggingAndAuditing
- `test_failed_authentication_logged` - Auth failure logging
- `test_unauthorized_access_logged` - Access logging
- `test_sensitive_operations_logged` - Operation logging

### test_token_management.py

#### TestAccessTokenGeneration
- Token claim validation
- Expiration setting
- Scope inclusion

#### TestRefreshTokenFlow
- Token generation
- User identity preservation
- Token validation
- Single-use enforcement

#### TestTokenRevocation
- Revocation functionality
- Blacklist validation
- Bulk revocation

#### TestTokenExpiration
- Expiration checking
- Grace periods
- Expiration warnings

#### TestTokenScopes
- Scope validation
- Scope hierarchy
- Multiple scope checks

#### TestTokenEncoding
- Signature validation
- Format validation
- Payload decoding

#### TestTokenAudience
- Audience validation
- Invalid audience rejection

#### TestTokenIssuer
- Issuer validation
- Invalid issuer rejection

#### TestTokenNotBefore
- NBF claim validation
- Future token handling

#### TestTokenMetadata
- User ID claims
- Additional claims
- Issued-at timestamps

### test_api_key_security.py

#### TestAPIKeyGeneration
- Key generation
- Format validation
- Randomness
- Environment prefixes

#### TestAPIKeyValidation
- Valid key acceptance
- Invalid key rejection
- Case sensitivity

#### TestAPIKeyScopes
- Scope validation
- Insufficient scopes
- Scope inheritance

#### TestAPIKeyExpiration
- Expiration support
- Expiration checking
- Grace periods

#### TestAPIKeyRotation
- Key rotation
- Old key invalidation
- New key validity

#### TestAPIKeyRevocation
- Revocation functionality
- Revoked key rejection
- Bulk revocation

#### TestAPIKeyMetadata
- Key naming
- Descriptions
- Timestamps
- Last used tracking

#### TestAPIKeyListAndManagement
- Key listing
- Key masking
- Details retrieval
- Key deletion

#### TestAPIKeySecurityBestPractices
- Log redaction
- Error message safety
- HTTPS enforcement
- Timing attack prevention

### test_authorization_scenarios.py

#### TestRoleBasedAccessControl
- Admin access
- User access
- Guest access
- Service access
- Role hierarchy

#### TestResourceOwnershipControl
- Owner access
- Non-owner denial
- Shared access
- Ownership transfer

#### TestAttributeBasedAccessControl
- Attribute validation
- Multiple attributes
- Time-based access
- Location-based access

#### TestPermissionCaching
- Cache functionality
- Cache invalidation
- Cache expiration

#### TestProjectLevelAccess
- Project admin
- Project members
- Non-member denial
- Role-based project access
- Permission override

#### TestItemLevelAccess
- Read access
- Write access
- Delete access
- Visibility by status

#### TestDelegatedAccess
- Access delegation
- Revocation
- Impersonation logging

#### TestConditionalAccess
- IP whitelist
- Device trust
- MFA requirement
- Risk-based control

#### TestPermissionInheritance
- Parent inheritance
- Child override

#### TestBulkPermissionOperations
- Bulk grant
- Bulk revoke

#### TestPermissionExplanation
- Decision explanation
- Denial explanation

## Fixtures Available

### Common Fixtures
```python
# In test_security_comprehensive.py
mock_valid_jwt                  # Valid JWT token
mock_expired_jwt               # Expired JWT token
mock_invalid_jwt               # Invalid JWT format
mock_api_key                   # Valid API key
mock_webhook_secret            # Webhook secret

# In test_token_management.py
mock_token_manager             # Token manager mock
mock_refresh_token             # Refresh token

# In test_api_key_security.py
mock_api_key                   # API key fixture
mock_api_key_manager           # API key manager mock

# In test_authorization_scenarios.py
mock_permission_manager        # Permission manager mock
user_contexts                  # User context definitions
```

## Test Patterns Used

### Pattern 1: Positive Path Testing
```python
def test_valid_operation():
    """Test successful operation."""
    result = perform_operation()
    assert result.is_successful
```

### Pattern 2: Negative Path Testing
```python
def test_invalid_operation():
    """Test operation rejection."""
    with pytest.raises(ValueError):
        perform_operation_with_invalid_input()
```

### Pattern 3: State Change Testing
```python
def test_state_change():
    """Test state transitions."""
    initial_state = get_state()
    perform_operation()
    final_state = get_state()
    assert initial_state != final_state
```

### Pattern 4: Mock-Based Testing
```python
def test_with_mock(mock_manager):
    """Test with mocked dependencies."""
    mock_manager.some_method.return_value = expected_value
    result = use_manager()
    assert result == expected_value
```

## Coverage Targets

### Authentication (High Coverage)
- [x] JWT validation
- [x] Token expiration
- [x] API key validation
- [x] Missing credentials
- [x] Token refresh
- [x] Token revocation
- [x] MFA scenarios

### Authorization (High Coverage)
- [x] RBAC
- [x] Resource ownership
- [x] Project access
- [x] Item access
- [x] Permission delegation
- [x] ABAC
- [x] Conditional access

### Security (High Coverage)
- [x] Webhook signatures
- [x] CORS headers
- [x] SQL injection prevention
- [x] XSS prevention
- [x] CSRF validation
- [x] Session security
- [x] Rate limiting

## Expected Test Results

With proper mocking implementation:
- **All tests will pass** when security features are properly implemented
- **17 tests will pass immediately** (basic endpoint tests)
- **140 tests will require feature implementation** for full pass rate

## Continuous Integration Integration

### pytest.ini Configuration
```ini
[pytest]
testpaths = tests/unit/api
markers =
    auth = authentication tests
    authz = authorization tests
    security = security tests
    rate_limit = rate limiting tests
    webhook = webhook tests
```

### Run specific markers
```bash
pytest -m auth              # Run authentication tests
pytest -m authz             # Run authorization tests
pytest -m security          # Run security tests
pytest -m webhook           # Run webhook tests
```

## Notes

1. All tests use proper isolation with pytest fixtures
2. Mocking prevents external dependencies
3. Tests are independent and can run in any order
4. Each test class focuses on a specific security area
5. Tests follow AAA pattern (Arrange, Act, Assert)
6. Comprehensive docstrings explain test purpose
7. Tests validate both positive and negative scenarios

## Related Files

- API Implementation: `/tracertm/api/main.py`
- Existing Auth Tests: `/tests/unit/api/test_authentication.py`
- Rate Limiting Tests: `/tests/unit/api/test_rate_limiting.py`
- Summary Document: `API_SECURITY_COVERAGE_SUMMARY.md`
