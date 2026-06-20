# Phase 2 Auth Implementation - Quick Start

## Development Setup

### Start the Server

```bash
# Set environment variables
export TRACERTM_MCP_AUTH_MODE=enabled
export TRACERTM_MCP_DEV_API_KEYS="dev-key-1,dev-key-2"
export TRACERTM_MCP_DEV_SCOPES="tracertm:read,tracertm:write"

# Start API server
bun run dev
```

### Test Device Flow

```bash
# Request device code
curl -X POST http://localhost:8000/api/v1/auth/device/code \
  -H "Content-Type: application/json" \
  -d '{"client_id": "tracertm-cli"}'

# Expected response
{
  "device_code": "...",
  "user_code": "ABCD-1234",
  "verification_uri": "https://auth.tracertm.local/device",
  "verification_uri_complete": "https://auth.tracertm.local/device?user_code=ABCD-1234",
  "expires_in": 900,
  "interval": 5
}

# Exchange device code (manually mark as authorized first)
curl -X POST http://localhost:8000/api/v1/auth/device/token \
  -H "Content-Type: application/json" \
  -d '{
    "device_code": "<device_code_from_above>",
    "client_id": "tracertm-cli"
  }'
```

### Test Dev API Keys

```bash
# Verify dev key works
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer dev-key-1"

# Expected response
{
  "user": {
    "id": "dev-key-1",
    "email": "user@example.com"
  },
  "claims": {
    "sub": "dev-key-1",
    "iat": 1234567890,
    "exp": 1234571490
  }
}
```

### Test CLI Auth

```bash
# Login with device flow
trace auth login

# This will:
# 1. Request device code
# 2. Display user code and URL
# 3. Open browser
# 4. Poll for completion
# 5. Store token in ~/.tracertm/tokens.json

# Check status
trace auth status

# Verify authenticated
trace auth whoami

# Get token for scripting
TRACERTM_TOKEN=$(trace auth token)

# Logout
trace auth logout
```

## MCP Integration

### Using CLI Tokens with MCP

```python
from tracertm.mcp.cli_integration import get_cli_adapter

# Get adapter
adapter = get_cli_adapter()

# Ensure MCP is authenticated (sync from CLI if needed)
if adapter.ensure_authenticated():
    # Get token for MCP operations
    token = adapter.get_mcp_token()
    print(f"Ready for MCP: {token[:20]}...")
```

### Using Dev Keys with MCP

```python
from tracertm.mcp.server import mcp

# Dev keys automatically validated by CompositeTokenVerifier
# Just use the dev key in Bearer token when calling MCP

# Example with httpx client
import httpx

headers = {"Authorization": "Bearer dev-key-1"}
async with httpx.AsyncClient() as client:
    # Call MCP tools with dev key
    pass
```

### Token Management

```python
from tracertm.mcp.token_manager import get_token_manager, TokenInfo
import time

manager = get_token_manager()

# Save a token
token = TokenInfo(
    access_token="jwt_token_here",
    expires_at=time.time() + 3600,
    scopes=["tracertm:read", "tracertm:write"]
)
manager.save_token(token)

# Get valid token
token_str = manager.get_valid_token()

# Check authentication
if manager.is_authenticated():
    print("Ready for MCP operations")

# Clear tokens
manager.clear_token()
```

## Middleware Configuration

### Enable Middleware

```python
import os
from tracertm.mcp.core import mcp

# Middleware is auto-enabled via environment variables

# Disable rate limiting
os.environ["TRACERTM_MCP_RATE_LIMIT_ENABLED"] = "false"

# Set rate limits
os.environ["TRACERTM_MCP_RATE_LIMIT_PER_MIN"] = "60"
os.environ["TRACERTM_MCP_RATE_LIMIT_PER_HOUR"] = "1000"

# Set required scopes
os.environ["TRACERTM_MCP_REQUIRED_SCOPES"] = "tracertm:read tracertm:write"

# Rebuild MCP to apply changes (or restart)
from tracertm.mcp.core import _build_mcp_server
mcp = _build_mcp_server()
```

### Register Tool-Specific Scopes

```python
from tracertm.mcp.core import mcp
from tracertm.mcp.middleware import AuthMiddleware

# Find auth middleware
auth_middleware = None
for middleware in mcp.middleware_list:
    if isinstance(middleware, AuthMiddleware):
        auth_middleware = middleware
        break

if auth_middleware:
    # Register tool with specific scopes
    auth_middleware.register_tool_scopes(
        "items_create",
        ["tracertm:write", "tracertm:items"]
    )
```

## Common Issues & Solutions

### Issue: "authorization_pending"

**Cause:** Device flow still waiting for user authorization.

**Solution:** Continue polling until user completes authorization in browser.

```bash
# Check browser for device authorization UI at:
# https://auth.tracertm.local/device?user_code=ABCD-1234
```

### Issue: "expired_token"

**Cause:** Device code expired (15 minutes default).

**Solution:** Request a new device code.

```bash
curl -X POST http://localhost:8000/api/v1/auth/device/code \
  -H "Content-Type: application/json" \
  -d '{"client_id": "tracertm-cli"}'
```

### Issue: Dev keys not working

**Cause:** Dev keys not configured in environment.

**Solution:** Set environment variables before starting server.

```bash
export TRACERTM_MCP_DEV_API_KEYS="key1,key2"
export TRACERTM_MCP_DEV_SCOPES="tracertm:read,tracertm:write"
bun run dev
```

### Issue: CLI tokens not syncing to MCP

**Cause:** CLI adapter not initialized.

**Solution:** Ensure CLI auth module is available and import adapter.

```python
from tracertm.mcp.cli_integration import ensure_cli_mcp_sync

# Call this at startup to sync tokens
ensure_cli_mcp_sync()
```

## Testing

### Run Auth Tests

```bash
# All auth tests
bun run test:api -- '**/*.auth.test.ts'

# Specific test
bun run test:api -- auth.middleware.test.ts

# With coverage
bun run test:api -- --coverage '**/*.auth.*'
```

### Manual E2E Test

```bash
# Terminal 1: Start server
bun run dev

# Terminal 2: Test device flow
trace auth login --no-browser
# Note the user code

# Terminal 3: Check status
trace auth status

# Terminal 4: Call API with token
curl -H "Authorization: Bearer $(trace auth token)" \
  http://localhost:8000/api/v1/auth/me
```

## Next Steps

1. **Implement OAuth integration** - Connect to real WorkOS AuthKit
2. **Add token refresh** - Auto-refresh tokens before expiration
3. **Database persistence** - Store device flows and tokens in database
4. **Scope enforcement** - Add scope validation to tools
5. **API key management** - Dashboard for managing API keys

## Files to Review

- Device flow implementation: `src/tracertm/api/routers/auth.py`
- Middleware: `src/tracertm/mcp/middleware.py`
- Token storage: `src/tracertm/mcp/token_manager.py`
- CLI integration: `src/tracertm/mcp/cli_integration.py`
- MCP setup: `src/tracertm/mcp/core.py`
- Full docs: `.trace/PHASE_2_AUTH_IMPLEMENTATION.md`
