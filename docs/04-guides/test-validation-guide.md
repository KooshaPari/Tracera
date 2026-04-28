# Test Validation Guide

## Overview

This guide covers the comprehensive test validation infrastructure that validates all API routes, WebSocket connections, authentication flows, and frontend functionality across the entire stack.

## Running Comprehensive Tests Locally

### Prerequisites

Ensure the development environment is properly initialized:

```bash
# Start all dev services with hot reload enabled
make dev

# One-time setup: Create test users in WorkOS and database
make test-setup
```

The test setup creates:
- Test user in WorkOS authentication system
- Test user in PostgreSQL database
- Test credentials for all test suites

### Run All Tests

Execute the comprehensive validation suite that validates both frontend and backend:

```bash
# Frontend + Backend comprehensive validation
make test-validate-comprehensive

# View consolidated test results report
make test-validate-report
```

This command:
1. Runs all Playwright E2E tests
2. Executes all Vitest API tests
3. Runs Go backend tests
4. Executes Python backend tests
5. Generates consolidated report with passed/failed routes

### Run Individual Test Suites

#### Frontend E2E Tests (Playwright)

Navigate to the frontend web application and run Playwright tests:

```bash
cd frontend/apps/web

# Run specific E2E validation test file
bun run test:e2e -- websocket-validation.spec.ts      # WebSocket CORS validation
bun run test:e2e -- route-validation.spec.ts         # Route validation
bun run test:e2e -- critical-path.spec.ts            # Critical path workflow tests

# Run all E2E tests
bun run test:e2e

# Run tests in UI mode (interactive)
bun run test:e2e:ui

# Run with specific browser
bun run test:e2e -- --project=chromium
bun run test:e2e -- --project=firefox
```

#### Frontend API Tests (Vitest)

Run unit and integration tests for API functionality:

```bash
cd frontend/apps/web

# Run comprehensive API route validation tests
bun run test -- src/__tests__/api/routes-validation.comprehensive.test.ts

# Run all API tests
bun run test -- src/__tests__/api/

# Run specific test file
bun run test -- src/__tests__/api/endpoints.comprehensive.test.ts

# Run with coverage
bun run test -- --coverage

# Run in watch mode
bun run test -- --watch
```

#### Backend Go Tests

Run Go backend tests for HTTP routes and handlers:

```bash
cd backend

# Run all route validation tests
go test -v ./internal/handlers -run TestAllRoutes

# Run WebSocket CORS headers validation
go test -v ./internal/handlers -run TestWebSocketCORSHeaders

# Run specific handler tests
go test -v ./internal/handlers -run TestProjectHandlers

# Run with coverage
go test -cover ./internal/handlers

# Run all backend tests
go test -v ./...
```

#### Backend Python Tests

Run Python backend tests for API endpoints:

```bash
cd backend

# Run routes validation tests
uv run pytest tests/unit/api/test_routes_validation.py -v

# Run specific test class
uv run pytest tests/unit/api/test_routes_validation.py::TestRoutesValidation -v

# Run with coverage
uv run pytest --cov=src/tracertm tests/

# Run in verbose mode
uv run pytest -v tests/
```

## Test Reports

### Playwright E2E Reports

After running E2E tests, view detailed test reports:

```bash
# Open HTML report in browser
cd frontend/apps/web
npx playwright show-report

# Report location
playwright-report/
├── index.html          # Main report page
├── failed-routes.json  # Summary of failed routes
└── test-results/       # Raw test data
```

Report includes:
- Test timeline and duration
- Screenshots of failed tests
- Video recordings of failures
- Error messages and stack traces
- CORS header validation results

### Vitest API Reports

Frontend API test results are generated in:

```bash
cd frontend/apps/web

# Report location
test-results/
├── index.html          # HTML report
├── junit.xml           # JUnit format for CI/CD
└── coverage/           # Coverage reports

# Generate coverage report
bun run test -- --coverage
```

### Go Test Output

Go tests output results directly to console with detailed pass/fail status for each route:

```bash
# Get coverage information
cd backend
go test -cover ./internal/handlers

# Generate coverage profile
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### Python Test Output

Python tests provide detailed console output with test results:

```bash
cd backend

# Run with coverage report
uv run pytest --cov=src/tracertm --cov-report=html tests/

# View HTML coverage report
open htmlcov/index.html
```

## Test Credentials

All test suites use the same test user account configured during setup:

**Test User Account:**
- Email: `kooshapari@kooshapari.com`
- Password: `testAdmin123`
- Role: Admin
- Status: Active

**Where Created:**
1. **WorkOS Auth System** - Created via WorkOS API during setup
2. **PostgreSQL Database** - Seeded during database initialization
3. **Available to** - All test suites (Playwright, Vitest, Go, Python)

**Test User Features:**
- Can create projects, items, and links
- Can authenticate via JWT
- Can use WebSocket connections
- Has full admin permissions

### Using Test Credentials in Tests

Tests automatically use the test user credentials:

```typescript
// Playwright E2E Tests - Auto-login
await page.goto('/login');
await page.fill('[data-testid="email"]', 'kooshapari@kooshapari.com');
await page.fill('[data-testid="password"]', 'testAdmin123');
await page.click('[data-testid="submit"]');
```

```typescript
// Vitest API Tests - JWT Auth
const response = await apiClient.get('/api/v1/projects', {
  headers: {
    Authorization: `Bearer ${testToken}`,
  },
});
```

```go
// Go Tests - JWT Auth
req, _ := http.NewRequest("GET", "/api/v1/projects", nil)
req.Header.Set("Authorization", "Bearer "+testToken)
```

```python
# Python Tests - JWT Auth
headers = {"Authorization": f"Bearer {test_token}"}
response = requests.get("/api/v1/projects", headers=headers)
```

## CI/CD Integration

Tests run automatically as part of the continuous integration pipeline:

### When Tests Run

- **On Push** - Push to `main` or `develop` branch
- **On Pull Requests** - PR against `main` or `develop` branch
- **Scheduled** - Daily runs at 2 AM UTC (optional)

### CI/CD Workflow Files

**Test validation workflow:**
- File: `.github/workflows/test-validation.yml`
- Runs all test suites in parallel on GitHub Actions
- Reports results to PR comments and status checks

**Quality workflow:**
- File: `.github/workflows/quality.yml`
- Runs linting and code quality checks
- Enforces code standards

**See also:**
- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/ci-cd.yml` - Full CI/CD pipeline

## Debugging Failed Tests

### Frontend E2E Test Failures

When a Playwright E2E test fails:

```bash
cd frontend/apps/web

# Run single failing test with debug output
bun run test:e2e -- websocket-validation.spec.ts --debug

# Run with headed browser (visible)
bun run test:e2e -- websocket-validation.spec.ts --headed

# Run with verbose logging
bun run test:e2e -- websocket-validation.spec.ts --reporter=list

# View test report to see failure details
npx playwright show-report
```

### Frontend API Test Failures

For Vitest failures:

```bash
cd frontend/apps/web

# Run specific test in watch mode
bun run test -- src/__tests__/api/routes-validation.comprehensive.test.ts --watch

# Run with verbose output
bun run test -- src/__tests__/api/routes-validation.comprehensive.test.ts --reporter=verbose

# Run single test case
bun run test -- -t "should validate all GET routes"
```

### Backend Go Test Failures

For Go test issues:

```bash
cd backend

# Run with verbose output
go test -v ./internal/handlers -run TestAllRoutes

# Run single test
go test -v ./internal/handlers -run TestWebSocketCORSHeaders

# Run with race detector
go test -race ./internal/handlers
```

### Backend Python Test Failures

For Python test debugging:

```bash
cd backend

# Run with verbose output and print statements
uv run pytest tests/unit/api/test_routes_validation.py -v -s

# Run with debugging
uv run pytest tests/unit/api/test_routes_validation.py --pdb

# Run single test
uv run pytest tests/unit/api/test_routes_validation.py::TestRoutesValidation::test_get_projects -v
```

## Common Issues and Solutions

### "Test user not found" Error

**Issue:** Tests fail because test user doesn't exist

**Solution:**
```bash
# Re-run test setup
make test-setup

# Verify user was created
psql $DATABASE_URL -c "SELECT email, role FROM users WHERE email = 'kooshapari@kooshapari.com';"
```

### WebSocket Connection Failures

**Issue:** WebSocket tests timeout or fail to connect

**Check:**
1. Dev server is running: `make dev`
2. WebSocket service is available: Check `.process-compose/logs/go-backend.log`
3. CORS headers are correct: See test-routes-quick-reference.md

**Solution:**
```bash
# Restart backend
make dev-stop && make dev

# Check WebSocket endpoint
curl -i http://localhost:3000/api/v1/ws
```

### CORS Header Validation Failures

**Issue:** CORS headers missing or incorrect

**Check the generated failed-routes.json:**
```bash
cat frontend/apps/web/playwright-report/failed-routes.json
```

**Verify CORS configuration:**
- Backend CORS setup in `backend/internal/middleware/cors.go`
- Frontend proxy in `frontend/apps/web/vite.config.ts`
- Test expectations in `*-validation.spec.ts` files

### Timeout Errors in Tests

**Issue:** Tests timeout waiting for responses

**Solution:**
```bash
# Check service logs
tail -f .process-compose/logs/go-backend.log
tail -f .process-compose/logs/python-backend.log

# Increase timeout in test configuration
# Edit playwright.config.ts: timeout: 60000

# Restart services
make dev-stop && make dev
```

## Test Environment Variables

Key environment variables used by tests:

```bash
# Test user credentials
TEST_USER_EMAIL=kooshapari@kooshapari.com
TEST_USER_PASSWORD=testAdmin123

# API endpoints
API_URL=http://localhost:3000
FRONTEND_URL=http://localhost:4000

# Database
DATABASE_URL=postgres://localhost/tracertm_test

# Services
REDIS_URL=redis://localhost:6379
NATS_URL=nats://localhost:4222
```

## Next Steps

- Review [Test Routes Quick Reference](../reference/test-routes-quick-reference.md) for specific routes being validated
- Check individual test files for implementation details
- See Developer Guide for local development setup
- Review CI/CD workflow for automated testing process

## Resources

- **Playwright Documentation:** https://playwright.dev/
- **Vitest Documentation:** https://vitest.dev/
- **Go Testing:** https://golang.org/doc/effective_go#testing
- **Pytest Documentation:** https://docs.pytest.org/
- **GitHub Actions:** https://docs.github.com/en/actions
