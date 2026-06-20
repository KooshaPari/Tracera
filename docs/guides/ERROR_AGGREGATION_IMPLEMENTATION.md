# Frontend Error Aggregation Implementation Guide

## Overview

This document describes the implementation of frontend error aggregation for the TraceRTM application. Errors occurring in React components are now captured by ErrorBoundary components, reported to the backend `/api/errors` endpoint, and logged for monitoring and debugging.

## Architecture

### Frontend Flow
```
React Component Error
  ↓
ErrorBoundary catches error
  ↓
componentDidCatch() triggered
  ↓
POST /api/errors (async, non-blocking)
  ↓
Sentry reporting (if configured)
  ↓
Error UI displayed to user
```

### Backend Flow
```
POST /api/errors request
  ↓
FrontendErrorPayload validation
  ↓
Error logging (ERROR level)
  ↓
Debug logging (full context)
  ↓
202 Accepted response
```

## Components

### 1. Frontend: Enhanced ErrorBoundary Component

**File:** `/frontend/apps/web/src/components/ErrorBoundary.tsx`

**Changes:**
- Added `reportErrorToBackend()` method to ErrorBoundary class
- Sends error details to `/api/errors` endpoint asynchronously
- Includes error message, stack trace, component stack, and context
- Uses 5-second timeout to prevent hanging
- Gracefully handles reporting failures (does not cascade errors)

**Key Features:**
- Non-blocking error reporting (uses fetch with AbortController)
- Includes browser context (URL, user agent)
- Respects error boundary name for categorization
- Silent failure if backend is unavailable

**Error Payload Example:**
```json
{
  "type": "react_error",
  "message": "Cannot read property 'foo' of undefined",
  "stack": "Error: Cannot read property 'foo' of undefined\n  at ...",
  "componentStack": "in MyComponent\n  in ErrorBoundary",
  "boundaryName": "MainAppBoundary",
  "timestamp": "2026-02-06T10:30:45.123Z",
  "url": "https://app.example.com/projects/123",
  "userAgent": "Mozilla/5.0 ..."
}
```

### 2. Backend: Error Aggregation Router

**File:** `/src/tracertm/api/routers/errors.py`

**Endpoint:** `POST /api/errors` (202 Accepted)

**Payload Schema:**
```python
class FrontendErrorPayload(BaseModel):
    type: str              # e.g., "react_error"
    message: str          # Error message
    stack: str            # JavaScript stack trace
    componentStack: str   # React component stack
    boundaryName: str     # Error boundary name
    timestamp: str        # ISO 8601 timestamp
    url: str             # Page URL
    userAgent: str       # Browser user agent
```

**Response:**
```json
{
  "status": "received",
  "message": "Error report received and will be processed"
}
```

**Features:**
- Validates incoming error payloads with Pydantic
- Logs errors at ERROR level with full context
- Logs debug details for detailed investigation
- Extracts client IP from request
- Returns 202 Accepted (asynchronous processing)
- No authentication required (frontend errors must be reportable)

**Logging Example:**
```
ERROR - tracertm.api.routers.errors - Frontend error reported: Cannot read property 'foo' of undefined
  error_type: react_error
  boundary_name: MainAppBoundary
  url: https://app.example.com/projects/123
  client_ip: 192.168.1.1
  component_stack: in MyComponent (truncated to 200 chars)
```

### 3. Router Registration

**File:** `/src/tracertm/api/main.py`

**Changes:**
- Added `errors` to router imports (line 942)
- Registered router after auth endpoints (line 976)
- No `/api/v1` prefix (error endpoint is at `/api/errors`)

```python
from tracertm.api.routers import (
    # ... other routers
    errors,
    # ... other routers
)

# Error aggregation (frontend error reporting - no auth required)
app.include_router(errors.router)
```

### 4. Tests

**File:** `/frontend/apps/web/src/__tests__/components/ErrorBoundary.test.tsx`

**New Test Suite:** "Error Aggregation and Reporting"

**Test Coverage:**
1. ✅ Errors are reported to `/api/errors` endpoint
2. ✅ Error details are included in the report
3. ✅ URL context is captured
4. ✅ Fetch failures are handled gracefully
5. ✅ 5-second timeout prevents hanging
6. ✅ Error UI renders even if reporting fails

## Usage

### For Users
When an error occurs in the React application, users will see:
1. Error message displayed
2. Stack trace (development mode only)
3. Buttons to "Try again" or "Reload page"
4. Backend automatically logs the error

### For Developers

#### Wrapping Components with Error Boundary
```tsx
import { ErrorBoundary } from '@/components/layout/ErrorBoundary';

export function MyFeature() {
  return (
    <ErrorBoundary name="MyFeature">
      <MyComponent />
    </ErrorBoundary>
  );
}
```

#### Custom Fallback UI
```tsx
<ErrorBoundary
  name="FormDialog"
  fallback={(error, reset) => (
    <div>
      <p>Form submission failed: {error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )}
>
  <CreateItemForm />
</ErrorBoundary>
```

#### Error Notification
```tsx
<ErrorBoundary
  name="DataTable"
  onError={(error, errorInfo) => {
    notificationService.error(`Table error: ${error.message}`);
  }}
>
  <DataTable />
</ErrorBoundary>
```

## Monitoring and Debugging

### Backend Logs
Check backend logs to see reported frontend errors:

```bash
# View recent errors
tail -f .process-compose/logs/python-backend.log | grep "Frontend error reported"

# Search for specific boundary
grep "boundary_name: MainAppBoundary" .process-compose/logs/python-backend.log
```

### Error Log Format
```
ERROR - tracertm.api.routers.errors - Frontend error reported: {message}
  error_type: {type}
  error_message: {message}
  component_stack: {truncated to 200 chars}
  js_stack: {truncated to 200 chars}
  boundary_name: {boundary name}
  url: {page URL}
  user_agent: {browser user agent truncated to 100 chars}
  client_ip: {IP address}

DEBUG - tracertm.api.routers.errors - Detailed error report from {boundary_name}
  full_error_type: {type}
  full_error_message: {message}
  full_component_stack: {full stack}
  full_js_stack: {full stack}
  full_user_agent: {full user agent}
  client_ip: {IP address}
```

## Testing the Implementation

### Manual Testing

1. **Start the dev environment:**
   ```bash
   make dev
   ```

2. **Trigger a frontend error:**
   - In your React component, throw an error:
   ```tsx
   throw new Error("Test error aggregation");
   ```

3. **Check backend logs:**
   ```bash
   tail -f .process-compose/logs/python-backend.log | grep "Frontend error"
   ```

4. **Verify error is reported:**
   - Error UI should display
   - Backend log should show ERROR level message with error details

### Automated Testing

Run the test suite:
```bash
bun run --cwd frontend/apps/web test ErrorBoundary
```

Tests verify:
- Error reporting to `/api/errors`
- Error details in payload
- URL context capture
- Graceful failure handling
- 5-second timeout
- Error UI rendering regardless of reporting status

## Performance Considerations

### Frontend
- **Non-blocking:** Error reporting uses async fetch with timeout
- **Timeout:** 5 seconds maximum wait (AbortController)
- **Error UI:** Displays immediately, reporting happens in background
- **No UI jank:** Reporting doesn't block user interactions

### Backend
- **202 Accepted:** Returns immediately, processing is asynchronous
- **Logging only:** Current implementation logs errors for aggregation
- **Future enhancements:** Can add persistence, alerting, or metrics

## Security Considerations

### What's Captured
- Error message and stack traces
- Component/application state implied by stack
- Page URL (user can see this anyway)
- Browser user agent (publicly available)

### What's NOT Captured
- User credentials or authentication tokens
- Sensitive business data
- Personal information beyond what's in the page URL

### Protection
- No authentication required (can't leak credentials)
- Client IP extracted for abuse monitoring
- Error details are truncated in logs (max 200 chars)
- Production stack traces not exposed to users

## Future Enhancements

1. **Error Aggregation Dashboard**
   - Aggregate errors by type, boundary, or URL
   - Track error frequency and trends
   - Alert on error spikes

2. **Persistence**
   - Store errors in database for historical analysis
   - Generate daily/weekly error reports

3. **Smart Categorization**
   - Deduplicate similar errors
   - Suggest fixes based on error patterns
   - Integration with issue tracking

4. **User Session Tracking**
   - Link errors to user sessions
   - Show error timeline for session replay
   - Correlate with performance metrics

5. **Source Map Integration**
   - Map minified stack traces to original code
   - Show exact line numbers in source files

## Files Modified

1. **Frontend:**
   - `/frontend/apps/web/src/components/ErrorBoundary.tsx` - Added error reporting
   - `/frontend/apps/web/src/__tests__/components/ErrorBoundary.test.tsx` - Added test cases

2. **Backend:**
   - `/src/tracertm/api/routers/errors.py` - New error aggregation router
   - `/src/tracertm/api/main.py` - Router import and registration

## References

- Frontend error boundary testing: `ErrorBoundary.test.tsx`
- Backend error handler: `errors.py`
- Payload schemas: `FrontendErrorPayload`, `ErrorResponse` in `errors.py`

## Rollback Plan

If issues occur:

1. **Frontend:** Comment out error reporting call in `ErrorBoundary.tsx` (line 76)
2. **Backend:** Remove router import and registration from `main.py`
3. **Tests:** Error boundary still functions, reporting tests will fail gracefully

Error handling will continue to work without backend reporting if needed.
