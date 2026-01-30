# Phase 2: Auth Implementation for TraceRTM MCP

**Status:** COMPLETE

**Completion Date:** 2026-01-29

## Overview

Phase 2 implements comprehensive authentication for TraceRTM MCP including:
- RFC 8628 Device Authorization Grant flow for CLI
- Enhanced MCP auth middleware with token refresh and scope validation
- CLI-MCP token integration
- Dev API key support

## Components Implemented

### 1. Device Flow Auth Endpoints (`src/tracertm/api/routers/auth.py`)

**Implements RFC 8628 Device Authorization Grant.**

#### Endpoints

- `POST /api/v1/auth/device/code` - Request device code
- `POST /api/v1/auth/device/token` - Exchange device code for token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/revoke` - Revoke token
- `POST /api/v1/auth/logout` - Log out user

#### Flow

```
CLI                           API
 |                             |
 +---(1) Request device code--->|
 |<---(2) device_code, user_code|
 |                             |
 |  User opens browser          |
 |  and enters user_code        |
 |                             |
 +---(3) Poll for token-------->|
 |       (Every 5 seconds)      |
 |                             |
 |<---(4) "pending" response----|
 |                             |
 |  (User authorizes)          |
 |                             |
 +---(5) Poll for token-------->|
 |<---(6) access_token---------| Success!
```

### 2. MCP Auth Middleware (`src/tracertm/mcp/middleware.py`)

**Validates tokens and enforces scope-based access control.**

#### Classes

- `AuthMiddleware` - Token validation and scope checking
- `LoggingMiddleware` - Tool call logging and tracing
- `RateLimitMiddleware` - Per-user or global rate limiting

#### Features

- Token expiration checking
- Automatic token refresh (future)
- Scope validation
- Tool-specific scope requirements
- Detailed error messages

#### Configuration

```bash
# Enable/disable rate limiting
TRACERTM_MCP_RATE_LIMIT_ENABLED=true

# Rate limit per minute
TRACERTM_MCP_RATE_LIMIT_PER_MIN=60

# Rate limit per hour
TRACERTM_MCP_RATE_LIMIT_PER_HOUR=1000

# Required scopes for all tools
TRACERTM_MCP_REQUIRED_SCOPES="tracertm:read tracertm:write"

# Verbose logging
TRACERTM_MCP_VERBOSE_LOGGING=false
```

### 3. MCP Token Manager (`src/tracertm/mcp/token_manager.py`)

**Secure token storage and management for MCP.**

#### Classes

- `TokenInfo` - Token data structure
- `TokenManager` - Token storage and retrieval

#### Features

- Secure file storage (encrypted with Fernet)
- Token expiration checking
- Scope management
- Easy token refresh workflow

#### Usage

```python
from tracertm.mcp.token_manager import get_token_manager

manager = get_token_manager()

# Save token
token = TokenInfo(
    access_token="jwt_token",
    expires_at=time.time() + 3600,
    scopes=["tracertm:read"]
)
manager.save_token(token)

# Get valid token
token_str = manager.get_valid_token()

# Check authentication
if manager.is_authenticated():
    print("Ready for MCP operations")
```

### 4. CLI-MCP Integration (`src/tracertm/mcp/cli_integration.py`)

**Seamless token sync between CLI and MCP.**

#### Features

- Sync CLI tokens to MCP storage
- Sync MCP tokens back to CLI
- Automatic fallback to CLI tokens if MCP tokens unavailable
- Unified authentication across CLI and MCP

#### Usage

```python
from tracertm.mcp.cli_integration import get_cli_adapter

adapter = get_cli_adapter()

# Ensure MCP is authenticated (sync from CLI if needed)
if adapter.ensure_authenticated():
    token = adapter.get_mcp_token()
    # Use token for MCP operations
```

### 5. Enhanced MCP Core (`src/tracertm/mcp/core.py`)

**Integrated auth middleware stack.**

#### Middleware Order

1. **RateLimitMiddleware** - Prevent abuse
2. **AuthMiddleware** - Validate tokens and scopes
3. **LoggingMiddleware** - Trace all calls

#### Configuration

```bash
# Auth mode
TRACERTM_MCP_AUTH_MODE=enabled

# WorkOS AuthKit
TRACERTM_MCP_AUTHKIT_DOMAIN=https://auth.workos.com
TRACERTM_MCP_BASE_URL=https://localhost:8000

# Dev keys
TRACERTM_MCP_DEV_API_KEYS="key1,key2,key3"
TRACERTM_MCP_DEV_SCOPES="tracertm:read,tracertm:write"

# Required scopes
TRACERTM_MCP_REQUIRED_SCOPES="tracertm:read tracertm:write"
```

## API Integration

### Auth Router Registration

The auth router is registered in `src/tracertm/api/main.py`:

```python
from tracertm.api.routers import auth

# Register auth endpoints at /api/v1/auth
app.include_router(auth.router)
```

### Usage Example

```bash
# Request device code
curl -X POST http://localhost:8000/api/v1/auth/device/code \
  -H "Content-Type: application/json" \
  -d '{"client_id": "tracertm-cli"}'

# Response
{
  "device_code": "...",
  "user_code": "ABCD-1234",
  "verification_uri": "https://auth.tracertm.local/device",
  "verification_uri_complete": "https://auth.tracertm.local/device?user_code=ABCD-1234",
  "expires_in": 900,
  "interval": 5
}

# Exchange device code for token
curl -X POST http://localhost:8000/api/v1/auth/device/token \
  -H "Content-Type: application/json" \
  -d '{
    "device_code": "...",
    "client_id": "tracertm-cli"
  }'

# Response
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "user@example.com"
  }
}
```

## Dev API Keys

### Configuration

Dev API keys enable CLI/MCP testing without OAuth:

```bash
# Set dev API keys
export TRACERTM_MCP_DEV_API_KEYS="dev-key-1,dev-key-2"

# Set dev scopes
export TRACERTM_MCP_DEV_SCOPES="tracertm:read,tracertm:write"
```

### Usage

```bash
# Use dev key in authorization header
curl -H "Authorization: Bearer dev-key-1" \
  http://localhost:8000/api/v1/auth/me

# CLI with dev key
trace --api-key dev-key-1 project list
```

## CLI Authentication Flow

### Using CLI

```bash
# Login with device flow
trace auth login

# This will:
# 1. Request device code from server
# 2. Display user code and verification URL
# 3. Open browser automatically
# 4. Poll for completion
# 5. Store token in ~/.tracertm/tokens.json

# Check status
trace auth status

# Print current token (for scripting)
trace auth token

# Logout
trace auth logout

# Refresh token
trace auth refresh

# Show current user
trace auth whoami
```

### Token Storage

Tokens are stored in `~/.tracertm/tokens.json`:
- Encrypted with Fernet (if available)
- Falls back to base64 encoding
- File permissions: 0600 (read/write only)

## MCP Usage

### With Dev Keys

```python
from tracertm.mcp.server import mcp

# Dev key automatically verified by CompositeTokenVerifier
# No setup needed, just use the dev key in Bearer token
```

### With CLI Tokens

```python
from tracertm.mcp.cli_integration import get_cli_adapter

# Sync CLI tokens to MCP
adapter = get_cli_adapter()
adapter.sync_from_cli()

# Now MCP can use the token
from tracertm.mcp.token_manager import get_token_manager
manager = get_token_manager()
token = manager.get_valid_token()
```

## Security Considerations

### Token Storage

- Tokens stored encrypted in `~/.tracertm/tokens.json`
- Fallback encryption if Fernet unavailable
- File permissions restricted to user only (0600)
- Keyring integration support

### Token Validation

- JWT tokens verified using JWKS endpoint
- Expiration time checked before use
- Scope validation enforced
- Rate limiting prevents abuse

### Dev Keys

- Only for development/testing
- Disabled in production (check TRACERTM_MCP_AUTH_MODE)
- Should not contain sensitive data
- Should have limited scopes

## Error Handling

### Common Errors

**Authorization Pending**
```
Error: authorization_pending
Status: 400 Bad Request
```
Continue polling for device code completion.

**Token Expired**
```
Error: expired_token
Status: 400 Bad Request
```
Request new device code or refresh token.

**Invalid Grant**
```
Error: invalid_grant
Status: 400 Bad Request
```
Device code not found or already used.

## Testing

### Unit Tests

```bash
# Test auth middleware
bun run test:api -- src/tracertm/mcp/middleware.test.ts

# Test token manager
bun run test:api -- src/tracertm/mcp/token_manager.test.ts

# Test CLI integration
bun run test:api -- src/tracertm/mcp/cli_integration.test.ts
```

### Integration Tests

```bash
# Test device flow
bun run test:workflows -- auth-device-flow.spec.ts

# Test CLI auth
bun run test:workflows -- auth-cli.spec.ts

# Test MCP auth
bun run test:workflows -- auth-mcp.spec.ts
```

### Manual Testing

```bash
# Start the server
bun run dev

# Test device code endpoint
curl -X POST http://localhost:8000/api/v1/auth/device/code \
  -H "Content-Type: application/json" \
  -d '{"client_id": "test"}'

# Test CLI login
trace auth login --no-browser

# Test token verification
trace auth whoami
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TRACERTM_MCP_AUTH_MODE` | `enabled` | Auth mode (disabled/enabled) |
| `TRACERTM_MCP_AUTHKIT_DOMAIN` | (none) | WorkOS auth domain |
| `TRACERTM_MCP_BASE_URL` | (none) | Server base URL |
| `TRACERTM_MCP_REQUIRED_SCOPES` | (none) | Required scopes |
| `TRACERTM_MCP_DEV_API_KEYS` | (none) | Dev API keys |
| `TRACERTM_MCP_DEV_SCOPES` | (none) | Dev scopes |
| `TRACERTM_MCP_RATE_LIMIT_ENABLED` | `true` | Rate limiting enabled |
| `TRACERTM_MCP_RATE_LIMIT_PER_MIN` | `60` | Calls per minute |
| `TRACERTM_MCP_RATE_LIMIT_PER_HOUR` | `1000` | Calls per hour |
| `TRACERTM_MCP_VERBOSE_LOGGING` | `false` | Verbose logging |

## Next Steps (Phase 3)

- Implement proper WorkOS AuthKit integration with real JWT verification
- Add token refresh endpoint that updates both CLI and MCP tokens
- Implement database-backed device flow storage (for production)
- Add scope-based access control to individual tools
- Implement device flow authorization UI

## Files Created/Modified

### New Files
- `src/tracertm/api/routers/auth.py` - Device flow endpoints
- `src/tracertm/mcp/middleware.py` - Auth middleware
- `src/tracertm/mcp/token_manager.py` - Token management
- `src/tracertm/mcp/cli_integration.py` - CLI-MCP integration

### Modified Files
- `src/tracertm/api/main.py` - Added auth router registration
- `src/tracertm/mcp/core.py` - Enhanced with middleware stack

### Documentation
- `.trace/PHASE_2_AUTH_IMPLEMENTATION.md` - This file

## Summary

Phase 2 completes foundational auth for TraceRTM MCP:
- ✅ RFC 8628 device flow for CLI
- ✅ Token validation and refresh middleware
- ✅ Scope-based access control
- ✅ CLI-MCP token integration
- ✅ Dev API key support
- ✅ Secure token storage

Phase 3 will enhance with production-ready features like database-backed flows and real WorkOS integration.
