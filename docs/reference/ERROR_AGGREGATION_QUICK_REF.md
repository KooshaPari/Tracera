# Error Aggregation Quick Reference

## Quick Facts

| Component | Details |
|-----------|---------|
| **Frontend** | ErrorBoundary component at `/frontend/apps/web/src/components/ErrorBoundary.tsx` |
| **Backend** | Error router at `/src/tracertm/api/routers/errors.py` |
| **Endpoint** | `POST /api/errors` |
| **Response** | `202 Accepted` (async processing) |
| **Timeout** | 5 seconds (AbortController) |
| **Logging** | ERROR + DEBUG levels |
| **Auth** | Not required |

## Frontend Usage

### Wrap Components
```tsx
import { ErrorBoundary } from '@/components/layout/ErrorBoundary';

<ErrorBoundary name="MyComponent">
  <MyComponent />
</ErrorBoundary>
```

### Custom Fallback
```tsx
<ErrorBoundary
  name="Form"
  fallback={(error, reset) => (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={reset}>Retry</button>
    </div>
  )}
>
  <MyForm />
</ErrorBoundary>
```

### With Callback
```tsx
<ErrorBoundary
  name="Table"
  onError={(error, errorInfo) => {
    notify.error(`Table failed: ${error.message}`);
  }}
>
  <DataTable />
</ErrorBoundary>
```

## Error Payload

```typescript
{
  type: 'react_error',           // Error type identifier
  message: string,               // Error message
  stack: string,                 // JavaScript stack trace
  componentStack: string,        // React component stack
  boundaryName: string,          // Name of error boundary
  timestamp: string,             // ISO 8601 timestamp
  url: string,                   // Page URL
  userAgent: string             // Browser user agent
}
```

## Backend Logging

### Search for Errors
```bash
# All frontend errors
grep "Frontend error reported" .process-compose/logs/python-backend.log

# Specific boundary
grep "boundary_name: MyComponent" .process-compose/logs/python-backend.log

# Real-time monitoring
tail -f .process-compose/logs/python-backend.log | grep "Frontend error"
```

### Log Format
```
ERROR - tracertm.api.routers.errors - Frontend error reported: {message}
  error_type: {type}
  boundary_name: {boundary}
  url: {url}
  client_ip: {ip}
```

## Testing

### Test Endpoint
```bash
curl -X POST http://localhost:8000/api/errors \
  -H "Content-Type: application/json" \
  -d '{
    "type": "react_error",
    "message": "Test",
    "timestamp": "2026-02-06T00:00:00Z"
  }'
```

### Run Tests
```bash
cd frontend/apps/web
bun run test ErrorBoundary
```

### Test Response
```json
{
  "status": "received",
  "message": "Error report received and will be processed"
}
```

## API Contract

### Request
```
POST /api/errors
Content-Type: application/json

{
  "type": "react_error",
  "message": "Error message",
  "stack": "Error stack trace",
  "componentStack": "React component stack",
  "boundaryName": "BoundaryName",
  "timestamp": "2026-02-06T10:30:45Z",
  "url": "https://app.example.com/page",
  "userAgent": "Mozilla/5.0..."
}
```

### Response
```
HTTP 202 Accepted
Content-Type: application/json

{
  "status": "received",
  "message": "Error report received and will be processed"
}
```

## Files at a Glance

| File | Purpose |
|------|---------|
| `frontend/apps/web/src/components/ErrorBoundary.tsx` | Frontend error catching + reporting |
| `src/tracertm/api/routers/errors.py` | Backend handler |
| `src/tracertm/api/main.py` | Router registration |
| `frontend/apps/web/src/__tests__/components/ErrorBoundary.test.tsx` | Test suite |
| `docs/guides/ERROR_AGGREGATION_IMPLEMENTATION.md` | Full implementation guide |
| `IMPLEMENTATION_SUMMARY.md` | Complete summary |

## Common Tasks

### Add Error Boundary to Page
```tsx
import { ErrorBoundary } from '@/components/layout/ErrorBoundary';

export function ProjectsPage() {
  return (
    <ErrorBoundary name="ProjectsPage">
      <ProjectsList />
    </ErrorBoundary>
  );
}
```

### Monitor Errors
```bash
# Watch live
tail -f .process-compose/logs/python-backend.log | grep "Frontend error"

# Count by boundary
grep "boundary_name:" .process-compose/logs/python-backend.log | cut -d: -f2 | sort | uniq -c
```

### Check Endpoint Health
```bash
# Verify endpoint exists
curl -X OPTIONS http://localhost:8000/api/errors -v

# Test with minimal payload
curl -X POST http://localhost:8000/api/errors \
  -H "Content-Type: application/json" \
  -d '{"message":"test","timestamp":"2026-02-06T00:00:00Z"}'
```

### Run Full Test Suite
```bash
cd frontend/apps/web
bun run test ErrorBoundary --reporter=verbose
```

## Troubleshooting

### Endpoint Returns 404
- Check router is imported in `main.py`
- Verify `app.include_router(errors.router)` is present
- Restart backend: `make dev`

### Errors Not Appearing in Logs
- Check `/api/errors` endpoint is receiving requests (test with curl)
- Verify logging is enabled in Python
- Check log level is DEBUG or ERROR

### Timeout Errors
- 5-second timeout is by design
- If backend is slow, endpoint will abort request
- Consider increasing timeout if needed

### Component Stack Missing
- Ensure error occurs inside an Error Boundary
- Component stack is only available in render phase errors
- Some async errors may not have component stack

## Related Documentation

- [Implementation Guide](../guides/ERROR_AGGREGATION_IMPLEMENTATION.md) - Full implementation details
- [Verification Guide](../reports/VERIFY_ERROR_AGGREGATION.md) - Testing instructions
- [Implementation Summary](../../IMPLEMENTATION_SUMMARY.md) - Complete overview
