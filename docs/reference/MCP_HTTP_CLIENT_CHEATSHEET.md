# MCP HTTP Client Cheatsheet

## Quick Start (30 seconds)

### TypeScript
```typescript
import { useMCP, useTool } from '@/hooks/useMCP';

const { client } = useMCP({ baseUrl: 'http://localhost:4000', token: 'token' });
const { execute, data } = useTool(client, 'project_manage');
await execute({ action: 'list' });
```

### Python
```python
from examples.mcp_http_client import MCPHTTPClient

async with MCPHTTPClient(base_url="http://localhost:4000", token="token") as client:
    result = await client.call_tool("project_manage", {"action": "list"})
```

---

## File Locations

| Component | Path |
|-----------|------|
| **TS Client** | `frontend/apps/web/src/api/mcp-client.ts` |
| **React Hooks** | `frontend/apps/web/src/hooks/useMCP.ts` |
| **Python Client** | `examples/mcp_http_client.py` |
| **Config** | `scripts/mcp/claude_desktop_config.json` |
| **Docs** | `docs/integration/mcp-http-integration.md` |
| **Tests** | `frontend/apps/web/src/__tests__/api/mcp-client.test.ts` |

---

## Common Operations

### Initialize Client

**TypeScript**:
```typescript
import { createMCPClient } from '@/api/mcp-client';

const client = createMCPClient({
  baseUrl: 'http://localhost:4000',
  token: 'your-token',
  timeout: 30000,
});

await client.initialize();
```

**Python**:
```python
client = MCPHTTPClient(base_url="http://localhost:4000", token="your-token")
await client.initialize()
```

### List Tools

**TypeScript**: `const { tools } = await client.listTools();`

**Python**: `tools = await client.list_tools()`

### Execute Tool

**TypeScript**: `await client.callTool('tool_name', { param: 'value' })`

**Python**: `await client.call_tool('tool_name', {'param': 'value'})`

### Track Progress

**TypeScript**:
```typescript
const unsubscribe = client.subscribeToProgress(
  (n) => console.log(n.progress),
  (e) => console.error(e)
);
```

### Close Client

**TypeScript**: `await client.close();`

**Python**: `await client.close()`

---

## React Hooks

### useMCP (Client Lifecycle)
```typescript
const { client, isInitialized, isInitializing, error, serverInfo } = useMCP({
  baseUrl: 'http://localhost:4000',
  token: getToken(),
});
```

### useTool (Execute Tool)
```typescript
const { execute, data, isLoading, error } = useTool(client, 'project_manage');
await execute({ action: 'list' });
```

### useTools (List Tools)
```typescript
const { tools, isLoading, error, refresh } = useTools(client);
```

### useProgress (Track Progress)
```typescript
const { progress, total, message, startTracking, stopTracking } = useProgress(client);
```

---

## Authentication

### Static API Keys (Development)
```bash
export TRACERTM_MCP_AUTH_MODE=static
export TRACERTM_MCP_DEV_API_KEYS=dev-key-1
```
**Client**: `token: 'dev-key-1'`

### OAuth (Production)
```bash
export TRACERTM_MCP_AUTH_MODE=oauth
export TRACERTM_MCP_OAUTH_CLIENT_ID=your-id
export TRACERTM_MCP_OAUTH_CLIENT_SECRET=your-secret
```
**Client**: `token: getOAuthToken()`

### Dynamic Token Update
```typescript
client.setToken('new-token');
```

---

## Error Handling

### TypeScript
```typescript
try {
  const result = await client.callTool('tool', args);
} catch (error) {
  if (error.message.includes('HTTP 401')) {
    // Auth error
  } else if (error.message.includes('JSON-RPC Error')) {
    // Protocol error
  }
}
```

### Python
```python
try:
    result = await client.call_tool('tool', args)
except ValueError as e:
    # JSON-RPC error
except httpx.HTTPError as e:
    # HTTP error
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

### Manual Testing
```bash
# Health check
curl http://localhost:4000/mcp/health

# List tools
curl -X POST http://localhost:4000/mcp/rpc \
  -H "Authorization: Bearer dev-key-1" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Connection refused** | `uvicorn src.tracertm.api.main:app --port 8000` |
| **HTTP 401** | `client.setToken('correct-token')` |
| **JSON-RPC error** | Check params match tool schema |
| **SSE not working** | `bun add event-source-polyfill` |

---

## Deployment

### Development
```bash
uvicorn src.tracertm.api.main:app --reload --port 8000
```

### Production (Docker)
```dockerfile
FROM python:3.12-slim
CMD ["uvicorn", "src.tracertm.api.main:app", "--host", "0.0.0.0"]
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mcp/rpc` | POST | JSON-RPC 2.0 requests |
| `/mcp/progress` | GET | Server-Sent Events |
| `/mcp/health` | GET | Health check |

---

## Full Documentation

📖 **Complete Guide**: `docs/integration/mcp-http-integration.md`
🚀 **Quick Start**: `docs/integration/MCP_HTTP_QUICK_START.md`
📋 **Index**: `docs/integration/MCP_INTEGRATION_INDEX.md`
✅ **Phase 4**: `docs/integration/MCP_PHASE_4_COMPLETION.md`

---

## Support

- Check documentation first
- Review examples in `examples/`
- Check test files for usage patterns
- Open GitHub issue with `[MCP]` prefix

---

**Version**: 1.0.0 | **Status**: Production Ready | **Date**: Jan 30, 2026
