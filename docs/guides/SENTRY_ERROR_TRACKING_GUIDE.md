# Sentry Error Tracking Integration Guide

This guide explains how to set up and use Sentry error tracking in TraceRTM for both frontend and backend.

## Overview

Sentry provides real-time error tracking, performance monitoring, and crash reporting for both the frontend (React) and backend (Go). This integration helps you:

- **Track Errors**: Automatically capture and report errors with full stack traces
- **Monitor Performance**: Track slow requests and transactions
- **Debug Issues**: View user sessions, breadcrumbs, and context
- **Set Alerts**: Get notified when errors occur or thresholds are exceeded

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Sentry Account Setup](#sentry-account-setup)
3. [Frontend Configuration](#frontend-configuration)
4. [Backend Configuration](#backend-configuration)
5. [Testing the Integration](#testing-the-integration)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Sentry account (free tier available at https://sentry.io)
- Access to TraceRTM frontend and backend repositories
- Environment variable access

---

## Sentry Account Setup

### 1. Create a Sentry Account

Visit https://sentry.io and sign up for a free account.

### 2. Create Projects

Create two separate projects in Sentry:

1. **Frontend Project**
   - Platform: React
   - Project Name: `tracertm-frontend`

2. **Backend Project**
   - Platform: Go
   - Project Name: `tracertm-backend`

### 3. Get Project Credentials

For each project, navigate to **Settings > Client Keys (DSN)** and copy:

- **DSN**: The Data Source Name URL (e.g., `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`)

### 4. Create Auth Token (for Source Maps)

For the frontend project only:

1. Go to **Settings > Account > API** or visit https://sentry.io/settings/account/api/auth-tokens/
2. Click **Create New Token**
3. Name: `TraceRTM Source Maps`
4. Scopes:
   - `project:releases`
   - `project:write`
5. Copy the generated token

---

## Frontend Configuration

### 1. Update Environment Variables

Edit `frontend/apps/web/.env.local` (create if it doesn't exist):

```bash
# Sentry Error Tracking
VITE_SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
VITE_SENTRY_ORG=your-org-name
VITE_SENTRY_PROJECT=tracertm-frontend

# For production builds with source maps
VITE_SENTRY_AUTH_TOKEN=your-auth-token

# Optional: Version tracking
VITE_APP_VERSION=1.0.0
VITE_BUILD_ID=local
```

### 2. Verify Installation

The Sentry SDK is already installed via:

```bash
cd frontend/apps/web
bun add @sentry/react @sentry/vite-plugin
```

### 3. Configuration Details

The frontend Sentry integration includes:

- **Automatic Error Capture**: All uncaught errors are sent to Sentry
- **Performance Monitoring**: Tracks page loads and API calls (10% sample rate in production)
- **Session Replay**: Records user sessions when errors occur (production only)
- **Source Maps**: Production builds include source maps for debugging
- **Error Filtering**: Filters out known non-critical errors (network issues, chunk loading)

### 4. Manual Error Tracking

Use the exported functions from `@/lib/sentry`:

```typescript
import {
  captureException,
  captureMessage,
  setSentryUser,
  addSentryBreadcrumb
} from '@/lib/sentry';

// Capture an exception with context
try {
  // risky operation
} catch (error) {
  captureException(error, {
    context: 'graph-rendering',
    nodeCount: 1000
  });
}

// Set user context after login
setSentryUser(user.id, user.email, user.username);

// Add breadcrumb for debugging
addSentryBreadcrumb('User clicked export button', 'user-action', 'info');

// Capture a message
captureMessage('Graph render took too long', 'warning');
```

---

## Backend Configuration

### 1. Update Environment Variables

Edit `.env` in the project root:

```bash
# Sentry Error Tracking (Backend)
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
SENTRY_ENVIRONMENT=development  # or production
SENTRY_RELEASE=1.0.0
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
SENTRY_DEBUG=false
```

### 2. Verify Installation

The Sentry SDK is already installed via:

```bash
cd backend
go get github.com/getsentry/sentry-go
```

### 3. Configuration Details

The backend Sentry integration includes:

- **Automatic Error Capture**: All panics and errors are sent to Sentry
- **Performance Monitoring**: Tracks HTTP request duration and slow queries
- **Request Context**: Includes request method, URL, IP, user agent
- **Error Filtering**: Filters out expected errors (context canceled, EOF)
- **Breadcrumbs**: Tracks slow requests (> 1 second)

### 4. Manual Error Tracking

Use the exported functions from the `sentry` package:

```go
import sentrylib "github.com/kooshapari/tracertm-backend/internal/sentry"

// Capture an exception
if err != nil {
  sentrylib.CaptureException(err)
}

// Set user context
sentrylib.SetUser(userID, email, username)

// Add custom context
sentrylib.SetContext("database", map[string]interface{}{
  "query_count": 10,
  "slow_queries": 2,
})

// Add breadcrumb
sentrylib.AddBreadcrumb("Processing batch", "batch", sentry.LevelInfo)

// Capture with custom scope
sentrylib.WithScope(func(scope *sentry.Scope) {
  scope.SetTag("feature", "graph-analysis")
  scope.SetLevel(sentry.LevelError)
  sentrylib.CaptureException(err)
})
```

---

## Testing the Integration

### Frontend Testing

1. **Development Mode**:
   ```bash
   cd frontend/apps/web
   bun run dev
   ```

2. **Trigger Test Error**:
   - Open browser console
   - Run: `throw new Error('Test Sentry Frontend')`
   - Check Sentry dashboard for the error

3. **Check Initialization**:
   - Look for `[Sentry] Initialized for development environment` in console
   - If no DSN: `[Sentry] Skipping initialization (no DSN or test environment)`

### Backend Testing

1. **Start Backend**:
   ```bash
   cd backend
   make dev
   ```

2. **Check Logs**:
   - Look for: `[Sentry] Initialized for development environment`
   - Or: `[Sentry] Skipping initialization (no DSN provided)`

3. **Trigger Test Error**:
   ```bash
   # Create a test endpoint that panics (for testing only)
   curl http://localhost:8080/api/v1/test-error
   ```

4. **Check Sentry Dashboard**:
   - Log into Sentry
   - Navigate to your backend project
   - Check for the error under **Issues**

---

## Best Practices

### Error Filtering

Both frontend and backend filter out common non-critical errors:

**Frontend:**
- Network failures (user offline)
- Chunk loading errors (transient)
- Browser extension errors
- ResizeObserver errors

**Backend:**
- Context canceled (expected)
- EOF errors (network issues)
- Health check failures

### Performance Sampling

To reduce costs and bandwidth:

**Production:**
- Frontend: 10% trace sampling
- Backend: 10% trace sampling
- Session Replay: 10% normal sessions, 100% error sessions

**Development:**
- Frontend: 100% trace sampling
- Backend: 100% trace sampling
- Session Replay: Disabled

### User Privacy

**Frontend Session Replay:**
- All text is masked
- All inputs are masked
- All media is blocked
- Only captures user interactions and navigation

**Backend:**
- No sensitive data in error messages
- Sanitize error context before sending
- User IDs only (no PII)

### Release Tracking

Always set version information:

```bash
# Frontend
VITE_APP_VERSION=1.2.3
VITE_BUILD_ID=prod-20260201-abc123

# Backend
SENTRY_RELEASE=1.2.3
```

This enables:
- Error grouping by release
- Regression detection
- Deploy tracking

---

## Troubleshooting

### Frontend Issues

**No errors appearing in Sentry:**

1. Check browser console for Sentry initialization message
2. Verify `VITE_SENTRY_DSN` is set correctly
3. Check browser network tab for Sentry API calls
4. Ensure errors aren't being filtered (check `beforeSend` in `sentry.ts`)

**Source maps not working:**

1. Verify `VITE_SENTRY_AUTH_TOKEN` is set
2. Check token has correct scopes (`project:releases`, `project:write`)
3. Ensure `VITE_SENTRY_ORG` and `VITE_SENTRY_PROJECT` match Sentry settings
4. Check Vite build logs for source map upload confirmation

**Too many errors:**

1. Adjust error filtering in `frontend/apps/web/src/lib/sentry.ts`
2. Add more patterns to `ignoreErrors` array
3. Customize `beforeSend` hook

### Backend Issues

**No errors appearing in Sentry:**

1. Check server logs for Sentry initialization message
2. Verify `SENTRY_DSN` is set correctly
3. Check that errors are being captured (not filtered)
4. Ensure middleware is registered in `server.go`

**Too many events:**

1. Adjust `SENTRY_TRACES_SAMPLE_RATE` (lower value = fewer events)
2. Customize error filtering in `internal/sentry/sentry.go`
3. Add more error patterns to `BeforeSend` hook

**Performance overhead:**

1. Lower trace sample rate in production
2. Disable debug mode (`SENTRY_DEBUG=false`)
3. Increase slow request threshold in middleware

### Common Issues

**Rate limiting:**

Free tier limits:
- 5,000 errors/month
- 10,000 transactions/month

Solutions:
- Lower sample rates
- Filter more aggressively
- Upgrade to paid plan

**Missing context:**

Always set context before capturing errors:

```typescript
// Frontend
setSentryUser(user.id, user.email);
setSentryContext('component', { name: 'GraphView' });

// Backend
sentrylib.SetUser(userID, email, username);
sentrylib.SetContext("request", requestData);
```

---

## Environment Variables Reference

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_SENTRY_DSN` | Yes* | - | Sentry project DSN |
| `VITE_SENTRY_ORG` | No** | - | Sentry organization name |
| `VITE_SENTRY_PROJECT` | No** | - | Sentry project name |
| `VITE_SENTRY_AUTH_TOKEN` | No** | - | Auth token for source maps |
| `VITE_APP_VERSION` | No | "unknown" | Application version |
| `VITE_BUILD_ID` | No | "local" | Build identifier |

\* Required to enable Sentry
\*\* Required for production source map upload

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | Yes* | - | Sentry project DSN |
| `SENTRY_ENVIRONMENT` | No | `ENV` value | Environment name |
| `SENTRY_RELEASE` | No | "unknown" | Release version |
| `SENTRY_TRACES_SAMPLE_RATE` | No | 0.1 | Trace sampling (0.0-1.0) |
| `SENTRY_DEBUG` | No | false | Enable debug logging |

\* Required to enable Sentry

---

## Additional Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Sentry React Guide](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry Go Guide](https://docs.sentry.io/platforms/go/)
- [Sentry Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Sentry Session Replay](https://docs.sentry.io/product/session-replay/)

---

## Support

For issues with this integration:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Sentry documentation
3. Contact the TraceRTM team

For Sentry-specific issues:
- [Sentry Community Forum](https://forum.sentry.io/)
- [Sentry Support](https://sentry.io/support/)
