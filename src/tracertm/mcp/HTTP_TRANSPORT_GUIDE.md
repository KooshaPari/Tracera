# TraceRTM MCP HTTP Transport Guide

## Overview

TraceRTM MCP Server supports dual transport modes:
- **STDIO**: For Claude Desktop and command-line MCP clients
- **HTTP/SSE**: For web applications and HTTP-based clients

This guide covers the HTTP transport implementation using FastMCP 3.0.

## Quick Start

### STDIO Mode (Default)

```bash
# For Claude Desktop integration
python -m tracertm.mcp
```

### HTTP Mode

```bash
# Basic HTTP transport
python -m tracertm.mcp --transport http --host 0.0.0.0 --port 8765

# Streamable HTTP with SSE support (recommended)
python -m tracertm.mcp --transport streamable-http --host 0.0.0.0 --port 8765

# Using environment variable
TRACERTM_MCP_TRANSPORT=streamable-http python -m tracertm.mcp
```

## Architecture

### Transport Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **stdio** | Standard input/output | Claude Desktop, CLI clients |
| **http** | HTTP POST with JSON-RPC 2.0 | Simple HTTP clients |
| **streamable-http** | HTTP with bidirectional streaming | Modern web apps, SSE support |
| **sse** | Server-Sent Events only | Legacy SSE clients |

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (FastMCP 3.0)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Tools      │  │  Resources   │  │   Prompts    │     │
│  │   (21+)      │  │   (BMM +     │  │   (BMM)      │     │
│  │              │  │   TraceRTM)  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                    Transport Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   STDIO      │  │     HTTP     │  │     SSE      │     │
│  │  (default)   │  │  (JSON-RPC)  │  │ (streaming)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                  Integration Options                        │
│  ┌──────────────┐              ┌──────────────┐           │
│  │  Standalone  │              │   FastAPI    │           │
│  │   Server     │              │  Integration │           │
│  └──────────────┘              └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## HTTP Transport Usage

### 1. Standalone HTTP Server

Run MCP as a standalone HTTP server:

```python
from tracertm.mcp.http_transport import run_http_server

# Start server
await run_http_server(
    host="0.0.0.0",
    port=8765,
    path="/mcp",
    transport="streamable-http",
)
```

Access at: `http://localhost:8765/mcp`

### 2. FastAPI Integration

Mount MCP to existing FastAPI app:

```python
from fastapi import FastAPI
from tracertm.mcp.http_transport import mount_mcp_to_fastapi

app = FastAPI()

# Mount MCP
mount_mcp_to_fastapi(
    app,
    path="/api/v1/mcp",
    transport="streamable-http",
)

# Now accessible at /api/v1/mcp
```

### 3. Existing Router (Already Implemented)

TraceRTM already has a FastAPI router at `/api/v1/mcp`:

```python
# In src/tracertm/api/routers/mcp.py
router = APIRouter(prefix="/mcp", tags=["MCP"])

# Endpoints:
# POST   /api/v1/mcp/messages - JSON-RPC 2.0 endpoint
# GET    /api/v1/mcp/sse - SSE streaming endpoint
# GET    /api/v1/mcp/tools - Tool discovery
# GET    /api/v1/mcp/health - Health check
```

## JSON-RPC 2.0 Format

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "project_manage",
    "arguments": {
      "action": "list"
    }
  },
  "id": 1
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Projects: ..."
      }
    ]
  },
  "id": 1
}
```

### Error Format

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 400,
    "message": "Tool not found: invalid_tool"
  },
  "id": 1
}
```

## SSE Streaming

### Progress Reporting

MCP tools can report progress via SSE when using HTTP transport:

```python
from fastmcp import Context

@mcp.tool()
async def long_running_task(ctx: Context | None = None):
    """Example tool with progress reporting."""
    for i in range(10):
        # Report progress
        if ctx:
            await ctx.report_progress(
                progress=i,
                total=10,
            )
            await ctx.info(f"Processing step {i}")

        # Do work
        await do_work()

    return {"status": "complete"}
```

### SSE Endpoint

Connect to SSE endpoint:

```javascript
const eventSource = new EventSource('/api/v1/mcp/sse?task_id=123');

eventSource.addEventListener('connected', (e) => {
  console.log('Connected:', JSON.parse(e.data));
});

eventSource.addEventListener('progress', (e) => {
  const data = JSON.parse(e.data);
  console.log(`Progress: ${data.progress}/${data.total}`);
});

eventSource.addEventListener('heartbeat', (e) => {
  console.log('Heartbeat:', JSON.parse(e.data));
});
```

### Progress Stream Structure

```typescript
// Event types
type SSEEvent =
  | { event: 'connected', data: { status: string, user_id: string } }
  | { event: 'progress', data: { task_id: string, progress: number, total: number } }
  | { event: 'heartbeat', data: { status: string, timestamp: number } }
  | { event: 'stream_start', data: { task_id: string, status: string } }
  | { event: 'stream_complete', data: { task_id: string, status: string } }
  | { event: 'stream_error', data: { task_id: string, error: string } }
```

## Transport Switching

### Environment Variables

```bash
# STDIO mode (default)
TRACERTM_MCP_TRANSPORT=stdio python -m tracertm.mcp

# HTTP mode
TRACERTM_MCP_TRANSPORT=http python -m tracertm.mcp

# Streamable HTTP (recommended for web)
TRACERTM_MCP_TRANSPORT=streamable-http python -m tracertm.mcp

# SSE only
TRACERTM_MCP_TRANSPORT=sse python -m tracertm.mcp
```

### Command Line Flags

```bash
# Full configuration
python -m tracertm.mcp \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8765 \
  --path /mcp \
  --log-level debug
```

### Programmatic Selection

```python
from tracertm.mcp.http_transport import get_transport_type

# Get transport from environment or default
transport = get_transport_type()  # Returns: "stdio" | "http" | "streamable-http" | "sse"
```

## Client Examples

### Python Client (httpx)

```python
import httpx
import json

async def call_mcp_tool(tool_name: str, arguments: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8765/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                },
                "id": 1,
            },
        )
        return response.json()

# Example call
result = await call_mcp_tool("project_manage", {"action": "list"})
print(result)
```

### JavaScript Client (fetch)

```javascript
async function callMCPTool(toolName, arguments) {
  const response = await fetch('http://localhost:8765/mcp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: arguments,
      },
      id: 1,
    }),
  });

  return await response.json();
}

// Example call
const result = await callMCPTool('project_manage', { action: 'list' });
console.log(result);
```

### cURL

```bash
# List tools
curl -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

# Call a tool
curl -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "project_manage",
      "arguments": {
        "action": "list"
      }
    },
    "id": 2
  }'
```

## Testing

### Run Integration Tests

```bash
# All HTTP transport tests
pytest tests/integration/test_mcp_http_transport.py -v

# Specific test class
pytest tests/integration/test_mcp_http_transport.py::TestStandaloneHTTPServer -v

# With coverage
pytest tests/integration/test_mcp_http_transport.py --cov=tracertm.mcp.http_transport
```

### Manual Testing

```bash
# Terminal 1: Start server
python -m tracertm.mcp --transport streamable-http --log-level debug

# Terminal 2: Test with curl
curl -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Terminal 3: Monitor SSE
curl -N http://localhost:8765/mcp/sse
```

## Performance Considerations

### Concurrent Requests

HTTP transport supports concurrent requests with proper isolation:

```python
# All requests are handled independently
tasks = [
    client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": i})
    for i in range(100)
]
results = await asyncio.gather(*tasks)
```

### Connection Pooling

For high-throughput scenarios, use connection pooling:

```python
import httpx

# Create a client with connection pooling
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
    ),
    timeout=30.0,
)
```

### SSE Keep-Alive

SSE connections send heartbeats every 30 seconds to prevent timeouts:

```python
# In the SSE endpoint
while True:
    await asyncio.sleep(30)
    yield {
        "event": "heartbeat",
        "data": json.dumps({"status": "alive"})
    }
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused

```bash
# Check if server is running
curl http://localhost:8765/mcp/health

# Verify port is not in use
lsof -i :8765
```

#### 2. CORS Errors

```python
# Enable CORS in standalone mode
from tracertm.mcp.http_transport import create_standalone_http_app

app = create_standalone_http_app(enable_cors=True)
```

#### 3. Progress Not Streaming

```python
# Ensure ctx is passed to tools
@mcp.tool()
async def my_tool(ctx: Context | None = None):
    if ctx:
        await ctx.report_progress(progress=1, total=10)
```

#### 4. Transport Not Detected

```bash
# Check environment variable
echo $TRACERTM_MCP_TRANSPORT

# Override with flag
python -m tracertm.mcp --transport streamable-http
```

### Debug Mode

```bash
# Enable debug logging
python -m tracertm.mcp --transport http --log-level debug

# Check FastMCP logs
FASTMCP_DEBUG=1 python -m tracertm.mcp --transport http
```

## Production Deployment

### Recommended Configuration

```bash
# Production settings
TRACERTM_MCP_TRANSPORT=streamable-http
TRACERTM_MCP_LOG_LEVEL=warning
TRACERTM_MCP_STRUCTURED_LOGGING=true
TRACERTM_MCP_JSON_LOGS=true

# Start server
python -m tracertm.mcp \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8765 \
  --log-level warning
```

### Behind Reverse Proxy

```nginx
# Nginx configuration
location /mcp {
    proxy_pass http://localhost:8765/mcp;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;

    # SSE support
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 86400;
}
```

### Monitoring

```python
# Health check endpoint
GET /api/v1/mcp/health

# Expected response
{
  "status": "healthy",
  "service": "mcp",
  "transport": "http"
}
```

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [JSON-RPC 2.0 Spec](https://www.jsonrpc.org/specification)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

## Migration from STDIO to HTTP

### For Existing Clients

1. **Update connection code**:
   ```python
   # Old (STDIO)
   from tracertm.mcp import run_server
   run_server()

   # New (HTTP)
   from tracertm.mcp.http_transport import run_http_server
   await run_http_server(transport="streamable-http")
   ```

2. **Change message format**: Use JSON-RPC 2.0 instead of STDIO messages

3. **Enable progress streaming**: Use SSE endpoint for progress updates

### Backward Compatibility

STDIO mode remains the default for backward compatibility:

```bash
# This still works
python -m tracertm.mcp
```

## Next Steps

- ✅ Phase 1: Core tools (STDIO) - Complete
- ✅ Phase 2: FastAPI router - Complete
- ✅ Phase 3: HTTP/SSE transport - **Complete**
- ⏳ Phase 4: Production features (auth, caching, rate limiting)
