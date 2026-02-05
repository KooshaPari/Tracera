# Test Routes Quick Reference

## Overview

This quick reference documents all API routes validated by the comprehensive test validation suite. Each route is tested for response status, CORS headers, authentication, and error handling across all test frameworks.

## Routes Covered by Validation Suite

### WebSocket Routes

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/api/v1/ws` | GET | Required (JWT) | ✅ Validated |

**CORS Headers Validated:**
- `Access-Control-Allow-Origin: http://localhost:4000`
- `Access-Control-Allow-Credentials: true`
- `Access-Control-Allow-Methods: GET, OPTIONS`
- `Upgrade: websocket`

### Projects API

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/api/v1/projects` | GET | Required | ✅ Validated |
| `/api/v1/projects` | POST | Required | ✅ Validated |
| `/api/v1/projects/{id}` | GET | Required | ✅ Validated |
| `/api/v1/projects/{id}` | PUT | Required | ✅ Validated |
| `/api/v1/projects/{id}` | DELETE | Required | ✅ Validated |

**CORS Headers Validated:**
- `Access-Control-Allow-Origin: http://localhost:4000`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`
- `Access-Control-Max-Age: 86400`

### Items API

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/api/v1/items` | GET | Required | ✅ Validated |
| `/api/v1/items` | POST | Required | ✅ Validated |
| `/api/v1/items/{id}` | GET | Required | ✅ Validated |
| `/api/v1/items/{id}` | PUT | Required | ✅ Validated |
| `/api/v1/items/{id}` | DELETE | Required | ✅ Validated |

**CORS Headers Validated:**
- `Access-Control-Allow-Origin: http://localhost:4000`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

### Links API

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/api/v1/links` | GET | Required | ✅ Validated |
| `/api/v1/links` | POST | Required | ✅ Validated |
| `/api/v1/links/{id}` | GET | Required | ✅ Validated |
| `/api/v1/links/{id}` | PUT | Required | ✅ Validated |
| `/api/v1/links/{id}` | DELETE | Required | ✅ Validated |

**CORS Headers Validated:**
- `Access-Control-Allow-Origin: http://localhost:4000`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

### Search API

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/api/v1/search` | POST | Required | ✅ Validated |

**CORS Headers Validated:**
- `Access-Control-Allow-Origin: http://localhost:4000`
- `Access-Control-Allow-Methods: POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

### Notifications API

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/api/v1/notifications` | GET | Required | ✅ Validated |
| `/api/v1/notifications/{id}/read` | POST | Required | ✅ Validated |

**CORS Headers Validated:**
- `Access-Control-Allow-Origin: http://localhost:4000`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

### Health Check

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/health` | GET | None | ✅ Validated |

**Expected Response:**
- Status: 200 OK
- Body: `{"status": "ok"}`
- CORS: Not required (public endpoint)

### System API

| Route | Method | Authentication | Status |
|-------|--------|----------------|--------|
| `/api/v1/system/status` | GET | None | ✅ Validated |
| `/api/v1/system/version` | GET | None | ✅ Validated |

**CORS Headers Validated:**
- `Access-Control-Allow-Origin: http://localhost:4000`
- `Access-Control-Allow-Methods: GET, OPTIONS`

## What's Validated for Each Route

### 1. Response Status

```
✅ Route is reachable
✅ Status code is returned (not -1 or timeout)
✅ No server errors (status < 500)
✅ Authentication errors handled (401/403)
```

### 2. CORS Headers

```
✅ Access-Control-Allow-Origin is set
✅ Access-Control-Allow-Methods includes route method
✅ Access-Control-Allow-Headers includes required headers
✅ Access-Control-Allow-Credentials set when needed
✅ Access-Control-Max-Age set for performance
```

### 3. Content Type

```
✅ Content-Type header is present
✅ Content-Type matches response body
✅ JSON responses have application/json
```

### 4. Authentication

```
✅ Protected routes require JWT token
✅ Missing token returns 401 Unauthorized
✅ Invalid token returns 401 Unauthorized
✅ Valid token allows access
✅ Token is validated in Authorization header
```

### 5. Error Handling

```
✅ Invalid requests return 400 Bad Request
✅ Unauthorized access returns 401 Unauthorized
✅ Forbidden access returns 403 Forbidden
✅ Not found returns 404 Not Found
✅ Server errors return 500 Internal Server Error
```

### 6. Response Format

```
✅ Responses have required fields
✅ Data types are correct
✅ No unexpected null values
✅ Error responses include message
```

### 7. Performance

```
✅ Response time is measured
✅ No timeout errors
✅ Large responses don't exceed limits
```

### 8. Console/Logging

```
✅ No JavaScript errors in console
✅ No unhandled exceptions
✅ Proper error messages logged
✅ Debug information available
```

## Response Status Codes

### Success Responses

| Status | Meaning | When |
|--------|---------|------|
| 200 | OK | Successful GET, POST, PUT requests |
| 201 | Created | Successful resource creation |
| 204 | No Content | Successful DELETE requests |

### Client Error Responses

| Status | Meaning | Validation |
|--------|---------|-----------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Resource doesn't exist |

### Server Error Responses

| Status | Meaning | Validation |
|--------|---------|-----------|
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service is down |

## CORS Header Examples

### Standard CORS Response (Authenticated)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: http://localhost:4000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400

{...data...}
```

### WebSocket Upgrade Response

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: [key]
Access-Control-Allow-Origin: http://localhost:4000
Access-Control-Allow-Credentials: true
```

### Health Check Response (No Auth)

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "ok"}
```

## Failed Routes Report

When tests fail, a `failed-routes.json` report is generated in the Playwright report directory:

```json
{
  "timestamp": "2026-02-05T22:00:00Z",
  "totalTests": 45,
  "passedTests": 43,
  "failedTests": 2,
  "passRate": "95.6%",
  "failedRoutes": [
    "GET /api/v1/search",
    "POST /api/v1/items"
  ],
  "details": [
    {
      "route": "GET /api/v1/search",
      "method": "GET",
      "expectedStatus": 200,
      "actualStatus": 500,
      "corsHeadersMissing": [],
      "error": "Internal server error",
      "timestamp": "2026-02-05T22:00:15Z"
    },
    {
      "route": "POST /api/v1/items",
      "method": "POST",
      "expectedStatus": 201,
      "actualStatus": 400,
      "corsHeadersMissing": ["Access-Control-Allow-Methods"],
      "error": "Bad request: missing required field 'type'",
      "timestamp": "2026-02-05T22:00:20Z"
    }
  ],
  "summary": {
    "corsIssues": 1,
    "authenticationIssues": 0,
    "statusCodeIssues": 1,
    "serverErrors": 1,
    "clientErrors": 1
  }
}
```

### Using the Failed Routes Report

**Identify failing routes:**
```bash
# View all failed routes
cat frontend/apps/web/playwright-report/failed-routes.json | grep failedRoutes

# Get specific route error details
cat frontend/apps/web/playwright-report/failed-routes.json | jq '.details[] | select(.route == "GET /api/v1/search")'
```

**Fix and re-test:**
1. Identify route in failed-routes.json
2. Check server logs for error details
3. Fix the underlying issue
4. Re-run test suite to validate fix
5. Verify route passes in failed-routes.json

## Test File Locations

### Playwright E2E Tests
```
frontend/apps/web/e2e/
├── websocket-validation.spec.ts       # WebSocket CORS validation
├── route-validation.spec.ts           # All route validation
├── critical-path.spec.ts              # Critical workflows
└── fixtures/                          # Test data and helpers
```

### Vitest API Tests
```
frontend/apps/web/src/__tests__/api/
├── routes-validation.comprehensive.test.ts  # Comprehensive route tests
├── endpoints.comprehensive.test.ts          # Endpoint validation
└── auth.comprehensive.test.ts               # Auth flow tests
```

### Go Backend Tests
```
backend/internal/handlers/
├── handlers_test.go                    # HTTP handler tests
├── websocket_test.go                   # WebSocket tests
└── middleware_test.go                  # CORS middleware tests
```

### Python Backend Tests
```
backend/tests/unit/api/
├── test_routes_validation.py           # Route validation tests
├── test_endpoints.py                   # Endpoint tests
└── test_auth.py                        # Authentication tests
```

## Quick Commands

### Run All Route Validations
```bash
# Run comprehensive validation
make test-validate-comprehensive

# View report
make test-validate-report
```

### Test Specific Routes
```bash
# Test WebSocket routes
cd frontend/apps/web && bun run test:e2e -- websocket-validation.spec.ts

# Test projects API
cd frontend/apps/web && bun run test -- -t "projects API"

# Test Go routes
cd backend && go test -v ./internal/handlers -run TestAllRoutes
```

### Debug Failed Routes
```bash
# View failed routes summary
cat frontend/apps/web/playwright-report/failed-routes.json | jq '.failedRoutes'

# Run failed test with debug
bun run test:e2e -- --debug <test-file>

# Check server logs
tail -f .process-compose/logs/go-backend.log
```

## Authentication for Validation Tests

All validation tests use the test user account:

**Credentials:**
- Email: `kooshapari@kooshapari.com`
- Password: `testAdmin123`

**Token Format (JWT):**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token included in:**
- HTTP Authorization header
- WebSocket connection parameters
- Cookie (if session-based)

## Common Test Failures and Fixes

### CORS Headers Missing

**Error:** `Access-Control-Allow-Methods header missing`

**Fix:**
1. Check backend CORS middleware configuration
2. Verify route is registered with correct methods
3. Check test expectations match backend setup
4. Restart backend service

### Authentication Failed

**Error:** `401 Unauthorized on GET /api/v1/projects`

**Fix:**
1. Run `make test-setup` to recreate test user
2. Verify JWT token generation
3. Check token expiration
4. Verify Authorization header format

### WebSocket Connection Timeout

**Error:** `WebSocket connection timeout on GET /api/v1/ws`

**Fix:**
1. Verify WebSocket service is running
2. Check network connectivity
3. Review WebSocket configuration
4. Check firewall/proxy settings
5. Restart backend service

### Route Not Found

**Error:** `404 Not Found on POST /api/v1/items`

**Fix:**
1. Verify route is implemented in backend
2. Check HTTP method is correct
3. Verify route prefix/path
4. Check backend service is running

## Performance Baseline

Expected response times for route validation:

| Route Type | Expected Time | Max Acceptable |
|------------|---------------|----------------|
| Health check | <50ms | 200ms |
| Simple GET | 50-200ms | 1000ms |
| POST/PUT | 100-300ms | 1500ms |
| Search | 200-500ms | 2000ms |
| WebSocket connect | 50-150ms | 500ms |

## Next Steps

- See [Test Validation Guide](../guides/test-validation-guide.md) for detailed instructions
- Review test files in `frontend/apps/web/e2e/` and `backend/tests/` for implementation details
- Check GitHub Actions workflow for automated testing
- Report issues to the development team with failed-routes.json details

