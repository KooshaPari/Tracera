# Sentry Error Tracking - Quick Reference

Quick reference for using Sentry error tracking in TraceRTM.

## Setup (One-Time)

### 1. Get Sentry Credentials

```bash
# Visit https://sentry.io
# Create two projects:
# - tracertm-frontend (React)
# - tracertm-backend (Go)
# Copy DSN for each project
```

### 2. Configure Environment

**Frontend** (`frontend/apps/web/.env.local`):
```bash
VITE_SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

**Backend** (`.env` in project root):
```bash
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

### 3. Verify

```bash
# Frontend
cd frontend/apps/web && bun run dev
# Look for: [Sentry] Initialized for development environment

# Backend
cd backend && make dev
# Look for: [Sentry] Initialized for development environment
```

---

## Frontend Usage

### Import Functions

```typescript
import {
  captureException,
  captureMessage,
  setSentryUser,
  clearSentryUser,
  setSentryContext,
  addSentryBreadcrumb
} from '@/lib/sentry';
```

### Capture Errors

```typescript
// Basic error capture
try {
  riskyOperation();
} catch (error) {
  captureException(error);
}

// With context
captureException(error, {
  context: 'graph-rendering',
  nodeCount: 1000,
  timestamp: Date.now()
});
```

### Capture Messages

```typescript
captureMessage('User exported large graph', 'info');
captureMessage('Slow render detected', 'warning');
captureMessage('Critical system failure', 'error');
```

### Set User Context

```typescript
// After login
setSentryUser(user.id, user.email, user.username);

// After logout
clearSentryUser();
```

### Add Breadcrumbs

```typescript
addSentryBreadcrumb('User clicked export', 'user-action', 'info');
addSentryBreadcrumb('API call failed', 'http', 'error');
```

### Set Custom Context

```typescript
setSentryContext('graph', {
  nodes: 500,
  edges: 1200,
  layout: 'force-directed'
});
```

---

## Backend Usage

### Import Package

```go
import sentrylib "github.com/kooshapari/tracertm-backend/internal/sentry"
```

### Capture Errors

```go
// Basic error capture
if err != nil {
  sentrylib.CaptureException(err)
  return err
}

// In HTTP handlers (automatic via middleware)
// Errors are automatically captured when returned
```

### Capture Messages

```go
sentrylib.CaptureMessage("Batch processing started")
```

### Set User Context

```go
sentrylib.SetUser(userID, email, username)

// Clear user
sentrylib.ClearUser()
```

### Add Custom Context

```go
sentrylib.SetContext("database", map[string]interface{}{
  "query_count": 10,
  "slow_queries": 2,
})
```

### Add Breadcrumbs

```go
import "github.com/getsentry/sentry-go"

sentrylib.AddBreadcrumb(
  "Processing batch",
  "batch",
  sentry.LevelInfo,
)
```

### Custom Scope

```go
sentrylib.WithScope(func(scope *sentry.Scope) {
  scope.SetTag("feature", "graph-analysis")
  scope.SetLevel(sentry.LevelError)
  sentrylib.CaptureException(err)
})
```

---

## Common Patterns

### React Component Error Boundary

```typescript
import { captureException } from '@/lib/sentry';

class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    captureException(error, {
      context: 'error-boundary',
      componentStack: errorInfo.componentStack
    });
  }
}
```

### API Error Handler

```typescript
async function fetchData() {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    captureException(error, {
      context: 'api-call',
      endpoint: '/data',
      method: 'GET'
    });
    throw error;
  }
}
```

### Go HTTP Handler

```go
func (h *Handler) GetItems(c echo.Context) error {
  items, err := h.repo.GetAll(c.Request().Context())
  if err != nil {
    // Error automatically captured by middleware
    return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
  }
  return c.JSON(http.StatusOK, items)
}
```

### Go Service Layer

```go
func (s *Service) ProcessBatch(ctx context.Context, items []Item) error {
  sentrylib.AddBreadcrumb("Starting batch", "batch", sentry.LevelInfo)

  for i, item := range items {
    if err := s.processItem(ctx, item); err != nil {
      sentrylib.WithScope(func(scope *sentry.Scope) {
        scope.SetContext("batch", map[string]interface{}{
          "index": i,
          "item_id": item.ID,
        })
        sentrylib.CaptureException(err)
      })
    }
  }

  return nil
}
```

---

## Configuration Reference

### Frontend Environment Variables

| Variable | Production | Development |
|----------|-----------|-------------|
| `VITE_SENTRY_DSN` | Required | Optional |
| `VITE_SENTRY_ORG` | Required* | - |
| `VITE_SENTRY_PROJECT` | Required* | - |
| `VITE_SENTRY_AUTH_TOKEN` | Required* | - |
| `VITE_APP_VERSION` | Recommended | Optional |

\* For source map upload

### Backend Environment Variables

| Variable | Production | Development |
|----------|-----------|-------------|
| `SENTRY_DSN` | Required | Optional |
| `SENTRY_ENVIRONMENT` | Required | Optional |
| `SENTRY_RELEASE` | Recommended | Optional |
| `SENTRY_TRACES_SAMPLE_RATE` | 0.1 | 1.0 |
| `SENTRY_DEBUG` | false | false |

---

## Sampling Rates

### Frontend

```typescript
// Production
tracesSampleRate: 0.1           // 10% of transactions
replaysSessionSampleRate: 0.1   // 10% of sessions
replaysOnErrorSampleRate: 1.0   // 100% of error sessions

// Development
tracesSampleRate: 1.0           // 100% of transactions
replaysSessionSampleRate: 0.0   // Disabled
```

### Backend

```bash
# Production
SENTRY_TRACES_SAMPLE_RATE=0.1   # 10% of transactions

# Development
SENTRY_TRACES_SAMPLE_RATE=1.0   # 100% of transactions
```

---

## Testing

### Frontend

```javascript
// Open browser console and run:
throw new Error('Test Sentry Frontend');

// Check Sentry dashboard
```

### Backend

```bash
# Create test endpoint (development only):
curl http://localhost:8080/api/v1/test-error

# Check server logs and Sentry dashboard
```

---

## Disabling Sentry

### Temporary (Environment)

```bash
# Frontend: Remove or comment out
# VITE_SENTRY_DSN=

# Backend: Remove or comment out
# SENTRY_DSN=
```

### Permanent (Code)

```typescript
// Frontend: src/lib/sentry.ts
export function initSentry(): void {
  return; // Disabled
}
```

```go
// Backend: internal/sentry/sentry.go
func Initialize(cfg Config) error {
  return nil // Disabled
}
```

---

## Troubleshooting

### No Errors in Sentry

1. Check DSN is set correctly
2. Verify initialization logs
3. Check network tab for API calls
4. Ensure error isn't filtered

### Too Many Errors

1. Lower sample rates
2. Add error filters
3. Check `beforeSend` hooks

### Missing Context

1. Set user context after auth
2. Add breadcrumbs before errors
3. Use custom scopes

---

## Links

- [Full Setup Guide](../guides/SENTRY_ERROR_TRACKING_GUIDE.md)
- [Sentry Dashboard](https://sentry.io/)
- [Sentry React Docs](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry Go Docs](https://docs.sentry.io/platforms/go/)
