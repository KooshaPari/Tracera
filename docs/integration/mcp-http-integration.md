# MCP HTTP Integration Guide

## Overview

TraceRTM MCP Server supports both STDIO and HTTP transport modes, allowing flexible integration with various clients:

- **STDIO Mode**: Direct subprocess communication (default for Claude Desktop)
- **HTTP Mode**: RESTful API with JSON-RPC 2.0 over HTTP/SSE

This guide covers HTTP mode integration for web applications and remote clients.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Authentication](#authentication)
3. [Client Libraries](#client-libraries)
4. [Usage Examples](#usage-examples)
5. [STDIO vs HTTP Comparison](#stdio-vs-http-comparison)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Architecture

### HTTP Transport Stack

```
┌─────────────────────────────────────────┐
│         Client Application              │
│  (TypeScript/Python/Any HTTP Client)    │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTP/HTTPS
                  │ JSON-RPC 2.0
                  ▼
┌─────────────────────────────────────────┐
│        FastAPI HTTP Server              │
│      (src/tracertm/api/main.py)         │
└─────────────────┬───────────────────────┘
                  │
                  │ In-process calls
                  ▼
┌─────────────────────────────────────────┐
│         MCP Server Core                 │
│    (src/tracertm/mcp/server.py)         │
└─────────────────────────────────────────┘
```

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mcp/rpc` | POST | JSON-RPC 2.0 requests |
| `/mcp/progress` | GET | Server-Sent Events (SSE) for progress |
| `/mcp/health` | GET | Health check |

---

## Authentication

### Bearer Token Authentication

HTTP mode uses Bearer tokens in the `Authorization` header:

```http
POST /mcp/rpc HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {...}
}
```

### Authentication Modes

Configure via `TRACERTM_MCP_AUTH_MODE` environment variable:

#### 1. Static API Keys (Development)

```bash
export TRACERTM_MCP_AUTH_MODE=static
export TRACERTM_MCP_DEV_API_KEYS=dev-key-1,dev-key-2
```

Use in requests:
```
Authorization: Bearer dev-key-1
```

#### 2. OAuth (Production)

```bash
export TRACERTM_MCP_AUTH_MODE=oauth
export TRACERTM_MCP_OAUTH_CLIENT_ID=your-client-id
export TRACERTM_MCP_OAUTH_CLIENT_SECRET=your-client-secret
export TRACERTM_MCP_OAUTH_TOKEN_URL=https://auth.example.com/token
```

#### 3. Database (Enterprise)

```bash
export TRACERTM_MCP_AUTH_MODE=database
export TRACERTM_MCP_DATABASE_URL=postgresql://localhost/tracertm
```

---

## Client Libraries

### TypeScript Client

Location: `frontend/apps/web/src/api/mcp-client.ts`

#### Installation

```bash
cd frontend/apps/web
bun add event-source-polyfill
```

#### Basic Usage

```typescript
import { createMCPClient } from '@/api/mcp-client';

// Create client
const client = createMCPClient({
  baseUrl: 'http://localhost:4000',
  token: 'your-token-here',
  timeout: 30000,
});

// Initialize session
const serverInfo = await client.initialize();
console.log('Connected to:', serverInfo.serverInfo.name);

// List tools
const tools = await client.listTools();
console.log('Available tools:', tools.tools.length);

// Call a tool
const result = await client.callTool('project_manage', {
  action: 'list',
  params: {},
});

// Close session
await client.close();
```

#### React Hooks

```typescript
import { useMCP, useTool, useProgress } from '@/hooks/useMCP';

function MyComponent() {
  // Initialize MCP client
  const { client, isInitialized, error } = useMCP({
    baseUrl: 'http://localhost:4000',
    token: getAuthToken(),
  });

  // Use a specific tool
  const { data, isLoading, execute } = useTool(client, 'project_manage');

  // Track progress
  const { progress, startTracking } = useProgress(client);

  return (
    <div>
      {isInitialized && (
        <button onClick={() => execute({ action: 'list' })}>
          List Projects
        </button>
      )}
      {isLoading && <Spinner />}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
```

### Python Client

Location: `examples/mcp_http_client.py`

#### Installation

```bash
pip install httpx pydantic
```

#### Basic Usage

```python
from examples.mcp_http_client import MCPHTTPClient

# Context manager (recommended)
async with MCPHTTPClient(
    base_url="http://localhost:4000",
    token="your-token-here",
) as client:
    # Initialize
    await client.initialize()

    # List tools
    tools = await client.list_tools()
    print(f"Found {len(tools['tools'])} tools")

    # Call tool
    result = await client.call_tool(
        "project_manage",
        {"action": "list", "params": {}},
    )
    print(result)

# Manual lifecycle
client = MCPHTTPClient(base_url="http://localhost:4000", token="token")
try:
    await client.initialize()
    result = await client.call_tool("project_manage", {"action": "list"})
finally:
    await client.close()
```

---

## Usage Examples

### Example 1: List and Execute Tools

#### TypeScript

```typescript
import { createMCPClient } from '@/api/mcp-client';

async function listAndExecuteTools() {
  const client = createMCPClient({
    baseUrl: 'http://localhost:4000',
    token: process.env.MCP_TOKEN,
  });

  try {
    // Initialize
    await client.initialize();

    // Get available tools
    const { tools } = await client.listTools();

    // Execute project list tool
    const projectTool = tools.find(t => t.name === 'project_manage');
    if (projectTool) {
      const projects = await client.callTool('project_manage', {
        action: 'list',
      });
      console.log('Projects:', projects);
    }
  } finally {
    await client.close();
  }
}
```

#### Python

```python
async def list_and_execute_tools():
    async with MCPHTTPClient(
        base_url="http://localhost:4000",
        token=os.getenv("MCP_TOKEN"),
    ) as client:
        await client.initialize()

        # Get available tools
        tools_response = await client.list_tools()

        # Execute project list tool
        projects = await client.call_tool(
            "project_manage",
            {"action": "list"},
        )
        print(f"Projects: {projects}")
```

### Example 2: Progress Tracking with SSE

```typescript
import { createMCPClient } from '@/api/mcp-client';

const client = createMCPClient({
  baseUrl: 'http://localhost:4000',
  token: 'your-token',
});

// Subscribe to progress
const unsubscribe = client.subscribeToProgress(
  (notification) => {
    console.log(`Progress: ${notification.progress}/${notification.total}`);
    console.log(`Message: ${notification.message}`);
  },
  (error) => {
    console.error('Progress error:', error);
  }
);

// Execute long-running operation
await client.callTool('bulk_import', { file: 'large.csv' });

// Clean up
unsubscribe();
await client.close();
```

### Example 3: Error Handling

```typescript
import { createMCPClient } from '@/api/mcp-client';

async function robustToolExecution() {
  const client = createMCPClient({
    baseUrl: 'http://localhost:4000',
    token: 'your-token',
    timeout: 60000, // 60 seconds
  });

  try {
    await client.initialize();

    const result = await client.callTool('project_manage', {
      action: 'create',
      params: { name: 'New Project' },
    });

    return result;
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('HTTP 401')) {
        console.error('Authentication failed');
      } else if (error.message.includes('HTTP 404')) {
        console.error('Endpoint not found');
      } else if (error.message.includes('JSON-RPC Error')) {
        console.error('MCP protocol error:', error.message);
      } else {
        console.error('Unexpected error:', error);
      }
    }
    throw error;
  } finally {
    await client.close();
  }
}
```

### Example 4: React Component Integration

```typescript
import { useMCP, useTools, useTool } from '@/hooks/useMCP';
import { useState } from 'react';

function MCPToolExecutor() {
  const [token] = useState(() => getAuthToken());

  // Initialize MCP
  const { client, isInitialized, serverInfo } = useMCP({
    baseUrl: 'http://localhost:4000',
    token,
  });

  // List all tools
  const { tools, isLoading: loadingTools } = useTools(client);

  // Execute specific tool
  const { execute, data, isLoading, error } = useTool(
    client,
    'project_manage'
  );

  return (
    <div>
      <h1>MCP Server: {serverInfo?.name}</h1>

      {loadingTools ? (
        <p>Loading tools...</p>
      ) : (
        <ul>
          {tools.map(tool => (
            <li key={tool.name}>{tool.name}</li>
          ))}
        </ul>
      )}

      <button
        onClick={() => execute({ action: 'list' })}
        disabled={!isInitialized || isLoading}
      >
        List Projects
      </button>

      {error && <div className="error">{error.message}</div>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
```

---

## STDIO vs HTTP Comparison

| Feature | STDIO | HTTP |
|---------|-------|------|
| **Latency** | Low (in-process) | Higher (network) |
| **Multiple Clients** | No | Yes |
| **Remote Access** | No | Yes |
| **Authentication** | Process-level | Token-based |
| **Progress Updates** | Limited | SSE streaming |
| **Firewall** | N/A | May need config |
| **Use Cases** | Claude Desktop | Web apps, APIs |
| **Setup Complexity** | Simple | Moderate |
| **Scalability** | Single client | Horizontal |

### When to Use STDIO

- Running Claude Desktop locally
- Single-user development environment
- Lowest latency required
- No network access needed

### When to Use HTTP

- Web application integration
- Multiple concurrent clients
- Remote server deployment
- Centralized MCP service
- Microservices architecture

---

## Deployment

### Local Development

```bash
# Start FastAPI server with MCP endpoints
uvicorn src.tracertm.api.main:app --reload --port 8000

# Test with curl
curl -X POST http://localhost:4000/mcp/rpc \
  -H "Authorization: Bearer dev-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### Production Deployment

#### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -e .

ENV TRACERTM_MCP_AUTH_MODE=oauth
ENV TRACERTM_MCP_OAUTH_CLIENT_ID=prod-client
ENV PORT=8000

CMD ["uvicorn", "src.tracertm.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t tracertm-mcp .
docker run -p 8000:8000 \
  -e TRACERTM_MCP_OAUTH_CLIENT_SECRET=secret \
  tracertm-mcp
```

#### Using Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracertm-mcp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: mcp-server
        image: tracertm-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: TRACERTM_MCP_AUTH_MODE
          value: "oauth"
        - name: TRACERTM_MCP_OAUTH_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: client-id
```

---

## Troubleshooting

### Connection Refused

**Problem**: Client cannot connect to server

**Solutions**:
1. Verify server is running: `curl http://localhost:4000/mcp/health`
2. Check firewall rules
3. Verify correct port in client config

### Authentication Failed

**Problem**: HTTP 401 or 403 errors

**Solutions**:
1. Verify token is correct and not expired
2. Check `TRACERTM_MCP_AUTH_MODE` matches token type
3. Ensure `Authorization` header is set correctly

### JSON-RPC Errors

**Problem**: JSON-RPC error responses

**Solutions**:
1. Verify request format matches JSON-RPC 2.0 spec
2. Check method name is correct (case-sensitive)
3. Validate parameters match tool schema
4. Check server logs for detailed error messages

### SSE Connection Issues

**Problem**: Progress updates not received

**Solutions**:
1. Ensure SSE endpoint is accessible: `/mcp/progress`
2. Verify browser/client supports EventSource
3. Check for proxy/load balancer timeout settings
4. Use EventSourcePolyfill for older browsers

### Performance Issues

**Problem**: Slow response times

**Solutions**:
1. Enable connection pooling in HTTP client
2. Use HTTP/2 if supported
3. Consider STDIO mode for local clients
4. Check network latency with `ping`
5. Review server resource usage

---

## Next Steps

- **Testing**: See `frontend/apps/web/src/__tests__/api/mcp-client.test.ts`
- **API Reference**: See `docs/api/mcp-endpoints.md`
- **Examples**: See `examples/` directory
- **Support**: Open issue on GitHub

---

## Related Documentation

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
