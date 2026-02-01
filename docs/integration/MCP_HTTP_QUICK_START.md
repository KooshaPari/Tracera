# MCP HTTP Integration - Quick Start Guide

## 30-Second Setup

### TypeScript/React

```typescript
// 1. Import the client
import { useMCP, useTool } from '@/hooks/useMCP';

// 2. Use in your component
function MyComponent() {
  const { client } = useMCP({
    baseUrl: 'http://localhost:4000',
    token: 'your-token',
  });

  const { execute, data } = useTool(client, 'project_manage');

  return <button onClick={() => execute({ action: 'list' })}>List</button>;
}
```

### Python

```python
# 1. Import the client
from examples.mcp_http_client import MCPHTTPClient

# 2. Use with async context
async with MCPHTTPClient(
    base_url="http://localhost:4000",
    token="your-token"
) as client:
    await client.initialize()
    result = await client.call_tool("project_manage", {"action": "list"})
```

---

## Common Operations

### List Available Tools

**TypeScript**:
```typescript
const client = createMCPClient({ baseUrl: 'http://localhost:4000', token: 'token' });
const { tools } = await client.listTools();
```

**Python**:
```python
tools = await client.list_tools()
```

### Execute a Tool

**TypeScript**:
```typescript
const result = await client.callTool('project_manage', {
  action: 'create',
  params: { name: 'New Project' }
});
```

**Python**:
```python
result = await client.call_tool('project_manage', {
  'action': 'create',
  'params': {'name': 'New Project'}
})
```

### Track Progress (SSE)

**TypeScript**:
```typescript
const unsubscribe = client.subscribeToProgress(
  (notification) => console.log(notification.progress),
  (error) => console.error(error)
);

// Later...
unsubscribe();
```

---

## Authentication

### Static API Key (Development)

```bash
export TRACERTM_MCP_AUTH_MODE=static
export TRACERTM_MCP_DEV_API_KEYS=dev-key-1
```

**Client**:
```typescript
const client = createMCPClient({
  baseUrl: 'http://localhost:4000',
  token: 'dev-key-1'
});
```

### OAuth (Production)

```bash
export TRACERTM_MCP_AUTH_MODE=oauth
export TRACERTM_MCP_OAUTH_CLIENT_ID=your-id
export TRACERTM_MCP_OAUTH_CLIENT_SECRET=your-secret
```

**Client**:
```typescript
const client = createMCPClient({
  baseUrl: 'https://api.example.com',
  token: getOAuthToken() // Your OAuth token
});
```

---

## Error Handling

### TypeScript

```typescript
try {
  const result = await client.callTool('project_manage', { action: 'list' });
} catch (error) {
  if (error instanceof Error) {
    if (error.message.includes('HTTP 401')) {
      // Handle auth error
    } else if (error.message.includes('JSON-RPC Error')) {
      // Handle protocol error
    }
  }
}
```

### Python

```python
try:
    result = await client.call_tool('project_manage', {'action': 'list'})
except ValueError as e:
    # JSON-RPC error
    print(f"Protocol error: {e}")
except httpx.HTTPError as e:
    # HTTP error
    print(f"Network error: {e}")
```

---

## React Hook Patterns

### Basic Tool Execution

```typescript
function ProjectList() {
  const { client } = useMCP({ baseUrl: 'http://localhost:4000', token: getToken() });
  const { execute, data, isLoading, error } = useTool(client, 'project_manage');

  useEffect(() => {
    execute({ action: 'list' });
  }, [execute]);

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;
  return <ProjectTable data={data} />;
}
```

### List All Tools

```typescript
function ToolExplorer() {
  const { client } = useMCP({ baseUrl: 'http://localhost:4000', token: getToken() });
  const { tools, isLoading, refresh } = useTools(client);

  return (
    <div>
      <button onClick={refresh}>Refresh</button>
      {tools.map(tool => <ToolCard key={tool.name} tool={tool} />)}
    </div>
  );
}
```

### Progress Tracking

```typescript
function LongRunningOperation() {
  const { client } = useMCP({ baseUrl: 'http://localhost:4000', token: getToken() });
  const { progress, startTracking, stopTracking } = useProgress(client);

  const handleStart = async () => {
    startTracking();
    await client.callTool('bulk_import', { file: 'large.csv' });
    stopTracking();
  };

  return (
    <div>
      <button onClick={handleStart}>Start</button>
      <ProgressBar value={progress.progress} max={progress.total} />
    </div>
  );
}
```

---

## Testing

### Run TypeScript Tests

```bash
cd frontend/apps/web
bun test src/__tests__/api/mcp-client.test.ts
bun test src/__tests__/hooks/useMCP.test.ts
```

### Run Python Example

```bash
python examples/mcp_http_client.py
```

---

## Debugging

### Check Server Health

```bash
curl http://localhost:4000/mcp/health
```

### Test JSON-RPC Endpoint

```bash
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

### Check SSE Endpoint

```bash
curl -N -H "Authorization: Bearer dev-key-1" \
  http://localhost:4000/mcp/progress
```

---

## Common Issues

### "Connection Refused"
**Solution**: Ensure server is running on port 8000
```bash
uvicorn src.tracertm.api.main:app --port 8000
```

### "HTTP 401 Unauthorized"
**Solution**: Check your token is valid
```typescript
client.setToken('correct-token');
```

### "JSON-RPC Error -32602"
**Solution**: Verify parameters match tool schema
```typescript
// Check tool definition first
const { tools } = await client.listTools();
const tool = tools.find(t => t.name === 'project_manage');
console.log(tool.parameters);
```

### SSE Not Working
**Solution**: Use EventSourcePolyfill for older browsers
```typescript
import { EventSourcePolyfill } from 'event-source-polyfill';
```

---

## File Locations

| Component | File Path |
|-----------|-----------|
| TypeScript Client | `frontend/apps/web/src/api/mcp-client.ts` |
| React Hooks | `frontend/apps/web/src/hooks/useMCP.ts` |
| Python Client | `examples/mcp_http_client.py` |
| Configuration | `scripts/mcp/claude_desktop_config.json` |
| Documentation | `docs/integration/mcp-http-integration.md` |
| Tests | `frontend/apps/web/src/__tests__/api/mcp-client.test.ts` |

---

## Next Steps

1. ✅ Install dependencies: `bun add event-source-polyfill`
2. ✅ Import client: `import { useMCP } from '@/hooks/useMCP'`
3. ✅ Configure auth: Set environment variables
4. ✅ Start using: Create your first component

**Full Documentation**: `docs/integration/mcp-http-integration.md`
