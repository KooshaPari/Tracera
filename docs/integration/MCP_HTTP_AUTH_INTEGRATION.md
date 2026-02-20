# MCP HTTP Authentication Integration

## Overview

This document describes the unified authentication integration between MCP (Model Context Protocol) and FastAPI, allowing the same OAuth/Bearer tokens to work for both REST API and MCP endpoints.

## Architecture

### Dual Transport Mode

The MCP server supports two transport modes:

1. **STDIO Mode** (default): Traditional MCP over stdio
   - Uses MCP's built-in WorkOS auth provider
   - Supports static dev API keys
   - Authentication handled at MCP layer

2. **HTTP Mode**: MCP over HTTP/REST
   - Uses FastAPI's `auth_guard` dependency
   - MCP auth disabled (FastAPI handles it)
   - Authentication handled at API layer

### Authentication Flow

```
Client Request
    ↓
FastAPI Middleware (AuthenticationMiddleware)
    ↓ [Extract token, populate context]
FastAPI Dependency (auth_guard)
    ↓ [Verify token, enforce auth]
    ↓ [Set current_user_id context var]
MCP Router Endpoint
    ↓ [Read user context]
MCP Tool Execution
    ↓ [RLS filters based on user_id]
Database Query
```

## Implementation

### 1. MCP HTTP Router

**File**: `src/tracertm/api/routers/mcp.py`

Provides HTTP endpoints for MCP:

- `POST /api/v1/mcp/messages` - JSON-RPC 2.0 endpoint
- `GET /api/v1/mcp/sse` - Server-Sent Events streaming
- `GET /api/v1/mcp/tools` - Tool discovery
- `OPTIONS /api/v1/mcp/messages` - CORS preflight

All endpoints use `Depends(auth_guard)` for authentication.

### 2. Updated MCP Auth Provider

**File**: `src/tracertm/mcp/auth.py`

The `build_auth_provider()` function now accepts a `transport` parameter:

```python
def build_auth_provider(transport: str = "stdio") -> AuthProvider | None:
    """Build auth provider based on transport mode.

    - transport="stdio": Returns WorkOS + static key auth provider
    - transport="http": Returns None (FastAPI handles auth)
    """
```

### 3. MCP Core Updates

**File**: `src/tracertm/mcp/core.py`

- `build_mcp_server(transport="stdio")` - Creates server with transport-specific auth
- `create_mcp_server(transport)` - Factory function for creating servers

### 4. FastAPI Integration

**File**: `src/tracertm/api/main.py`

MCP router is mounted at `/api/v1/mcp`:

```python
from tracertm.api.routers import mcp

app.include_router(mcp.router, prefix="/api/v1")
```

### 5. User Context Injection

**File**: `src/tracertm/api/deps.py`

The `auth_guard` dependency now sets user context:

```python
def auth_guard(request: Request) -> dict:
    """Authenticate and set user context."""
    claims = verify_token(token)

    # Set context for RLS
    if claims.get("sub"):
        current_user_id.set(claims["sub"])

    return claims
```

## Usage

### Making HTTP Requests to MCP

#### List Tools

```bash
curl -X GET http://localhost:4000/api/v1/mcp/tools \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "tools": [
    {
      "name": "project_manage",
      "description": "Manage projects",
      "inputSchema": {...}
    }
  ]
}
```

#### Call Tool (JSON-RPC)

```bash
curl -X POST http://localhost:4000/api/v1/mcp/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "project_manage",
      "arguments": {
        "action": "list",
        "kind": "project"
      }
    },
    "id": 1
  }'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "ok": true,
    "data": [...]
  },
  "id": 1
}
```

#### Server-Sent Events (SSE)

```bash
curl -N -X GET http://localhost:4000/api/v1/mcp/sse \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Same Token for REST and MCP

The same Bearer token works for both REST API and MCP endpoints:

```bash
# REST API
curl http://localhost:4000/api/v1/specifications/adrs \
  -H "Authorization: Bearer YOUR_TOKEN"

# MCP
curl http://localhost:4000/api/v1/mcp/tools \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Security

### Token Verification

1. **Token Format**: `Authorization: Bearer <token>`
2. **Verification**: Uses TokenBridge (supports RS256 WorkOS + HS256 service tokens)
3. **Claims Extraction**: `sub` (user ID), `org_id` (account ID)

### User Context & RLS

1. **Context Variables**:
   - `current_user_id`: Set from `claims["sub"]`
   - `current_account_id`: Set from `claims["org_id"]`

2. **RLS (Row-Level Security)**:
   - Database queries automatically filter by user context
   - Implemented in `get_db` dependency
   - PostgreSQL: `set_config('app.current_user_id', user_id, false)`

### Authentication Modes

#### Production (Auth Enabled)

```env
# .env
AUTH_ENABLED=true
WORKOS_CLIENT_ID=your_client_id
WORKOS_API_KEY=your_api_key
```

#### Development (Auth Disabled)

```env
# .env
AUTH_ENABLED=false
```

Or use dev API keys:

```env
# .env
TRACERTM_MCP_DEV_API_KEYS=dev_key_1,dev_key_2
TRACERTM_MCP_DEV_SCOPES=read,write
```

## Testing

### Running Tests

```bash
# Run MCP HTTP auth tests
pytest tests/integration/test_mcp_http_auth.py -v

# Run specific test
pytest tests/integration/test_mcp_http_auth.py::TestMCPHTTPAuth::test_tools_list_with_valid_token -v
```

### Test Coverage

The test suite covers:

1. ✅ Valid Bearer token (200 OK)
2. ✅ Missing token (401)
3. ✅ Invalid token (401)
4. ✅ User context injection
5. ✅ RLS verification
6. ✅ CORS preflight
7. ✅ JSON-RPC error format
8. ✅ SSE endpoint auth
9. ✅ Same token for REST + MCP

## Configuration

### Environment Variables

#### MCP Transport Mode

```env
# Force HTTP transport mode for MCP server
TRACERTM_MCP_TRANSPORT=http
```

#### Auth Configuration

```env
# WorkOS AuthKit
TRACERTM_MCP_AUTHKIT_DOMAIN=https://api.workos.com
TRACERTM_MCP_BASE_URL=http://localhost:4000

# Required scopes
TRACERTM_MCP_REQUIRED_SCOPES=read,write

# Dev API keys (for testing)
TRACERTM_MCP_DEV_API_KEYS=dev_key_1,dev_key_2
TRACERTM_MCP_DEV_SCOPES=read,write

# Disable auth
TRACERTM_MCP_AUTH_MODE=disabled
```

#### FastAPI Auth

```env
# Enable/disable auth
AUTH_ENABLED=true

# CORS origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Troubleshooting

### Common Issues

#### 1. 401 Unauthorized

**Symptom**: All requests return 401

**Solutions**:
- Check `AUTH_ENABLED` config
- Verify token format: `Bearer <token>` (note the space)
- Check token validity with WorkOS
- Verify WORKOS_CLIENT_ID and WORKOS_API_KEY

#### 2. User Context Not Set

**Symptom**: RLS filters not working, seeing all data

**Solutions**:
- Check that `current_user_id.set()` is called in `auth_guard`
- Verify `sub` claim exists in token
- Check database RLS policies

#### 3. CORS Errors

**Symptom**: Browser shows CORS error

**Solutions**:
- Add frontend origin to `CORS_ORIGINS`
- Verify OPTIONS endpoint returns correct headers
- Check that middleware is properly configured

#### 4. MCP Tools Not Found

**Symptom**: `/api/v1/mcp/tools` returns empty list

**Solutions**:
- Verify MCP tools are registered
- Check that MCP server is initialized
- Ensure tools are imported in `__init__.py`

## Migration Guide

### From STDIO MCP to HTTP MCP

1. **Update Client Code**:
   ```python
   # Before (STDIO)
   mcp_client = MCPClient(transport="stdio")

   # After (HTTP)
   mcp_client = MCPClient(
       transport="http",
       base_url="http://localhost:4000/api/v1/mcp",
       headers={"Authorization": f"Bearer {token}"}
   )
   ```

2. **Environment Variables**:
   ```env
   # Before
   TRACERTM_MCP_AUTH_MODE=stdio

   # After
   TRACERTM_MCP_TRANSPORT=http
   AUTH_ENABLED=true
   ```

3. **Token Handling**:
   - STDIO: Token passed in MCP auth handshake
   - HTTP: Token passed in Authorization header

## Best Practices

### 1. Token Management

- Use short-lived access tokens (1 hour)
- Implement token refresh logic
- Store tokens securely (never in code/logs)

### 2. Error Handling

- Always check response status codes
- Parse JSON-RPC error objects
- Implement retry logic with exponential backoff

### 3. Context Isolation

- Never share user context between requests
- Always set context at the start of request
- Clean up context after request (automatic with contextvars)

### 4. RLS Verification

- Test that users can only see their own data
- Verify project isolation works correctly
- Check that admin roles have appropriate access

## API Reference

### Endpoints

#### GET /api/v1/mcp/health

Health check endpoint (no auth required).

**Response**:
```json
{
  "status": "healthy",
  "service": "mcp",
  "transport": "http"
}
```

#### GET /api/v1/mcp/tools

List available MCP tools.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "tools": [
    {
      "name": "string",
      "description": "string",
      "inputSchema": {}
    }
  ]
}
```

#### POST /api/v1/mcp/messages

Execute MCP methods via JSON-RPC 2.0.

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "string",
  "params": {},
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {},
  "id": 1
}
```

**Error Response**:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 400,
    "message": "Error message"
  },
  "id": 1
}
```

#### GET /api/v1/mcp/sse

Server-Sent Events stream.

**Headers**: `Authorization: Bearer <token>`

**Events**:
- `connected`: Initial connection
- `heartbeat`: Keep-alive every 30s
- `error`: Error occurred

#### OPTIONS /api/v1/mcp/messages

CORS preflight.

**Response Headers**:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

## Related Documentation

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [WorkOS AuthKit](https://workos.com/docs/authkit)
- [Row-Level Security in PostgreSQL](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

## Changelog

### Phase 2 (Current)

- ✅ Created MCP HTTP router
- ✅ Updated MCP auth for dual transport
- ✅ Updated MCP core for transport modes
- ✅ Mounted MCP router in FastAPI
- ✅ Implemented context injection
- ✅ Created integration tests

### Future Enhancements

- [ ] WebSocket transport for MCP
- [ ] Rate limiting per-user
- [ ] Audit logging for MCP calls
- [ ] Caching for tool discovery
- [ ] Batch tool execution
