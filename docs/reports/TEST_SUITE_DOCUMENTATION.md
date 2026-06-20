# Test Suite Documentation - Live vs Mock Data

## Overview

The TraceRTM test suite supports both **mock data** (MSW) and **live API** testing modes. This document explains how to run tests with your test account against real data.

## Test Account Setup ✅ COMPLETE

### Test User Credentials
```
Email:      test@tracertm.io
Profile ID: 86f0050b-7758-460b-8271-0e00dc1b1ae0
Account:    My Account (7f3c8d2a-1b4e-4a9c-9e2d-6f1a8b0c3d4e)
Role:       member
```

### Test Projects Available
```
1. SwiftRide - Ride-sharing Platform
   ID:    cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e
   Items: 5,686 ✅ EXCELLENT FOR SCALE TESTING

2. Platform In-Progress — Trace & Requirements (3 variants)
   Items: 2,200 + 0 + 2,200
   
3. Additional projects for variety
```

## Running Tests

### Mode 1: Mock API Tests (Default)
Uses Mock Service Worker (MSW) for isolated testing.

```bash
# All tests with mocks
npx playwright test

# Specific test file
npx playwright test dashboard.spec.ts

# With UI mode
npx playwright test --ui

# Debug mode
npx playwright test --debug
```

### Mode 2: Live API Tests (NEW)
Tests against real backend with real data.

```bash
# All live tests against real API
VITE_USE_MOCK_DATA=false npx playwright test

# Specific live test file
VITE_USE_MOCK_DATA=false npx playwright test dashboard-live-data.spec.ts

# Live test with UI
VITE_USE_MOCK_DATA=false npx playwright test --ui

# Live test with debugging
VITE_USE_MOCK_DATA=false npx playwright test --debug
```

### Mode 3: Live Tests with Custom Account
Override default test account if needed.

```bash
# Use different email
VITE_USE_MOCK_DATA=false \
TEST_USER_EMAIL=kooshapari@gmail.com \
npx playwright test

# With custom password
VITE_USE_MOCK_DATA=false \
TEST_USER_EMAIL=test@tracertm.io \
TEST_USER_PASSWORD=custom-password \
npx playwright test
```

## Test Categories

### ✅ Mock Data Tests (Use by Default)
```
frontend/apps/web/e2e/
├── auth.spec.ts                      # Authentication flows (mock)
├── dashboard.spec.ts                 # Dashboard with mock data
├── items.spec.ts                     # Item operations (mock)
├── graph.spec.ts                     # Graph visualization (mock)
├── accessibility.a11y.spec.ts        # A11y checks (mock data)
└── ... 50 other test files
```

**Run**: `npx playwright test`

### 🔴 Live Data Tests (NEW)
```
frontend/apps/web/e2e/
└── dashboard-live-data.spec.ts       # Dashboard with 5,686 real items
```

**Run**: `VITE_USE_MOCK_DATA=false npx playwright test dashboard-live-data.spec.ts`

### 📊 Performance Tests
```
frontend/apps/web/e2e/
├── dashboard-perf.spec.ts            # Dashboard performance
├── graph-performance.perf.spec.ts    # Graph rendering performance
└── sigma-performance.perf.spec.ts    # Sigma graph performance
```

**Run with live data**:
```bash
VITE_USE_MOCK_DATA=false npx playwright test --grep "perf"
```

## What Changes Between Modes

| Aspect | Mock Mode | Live Mode |
|--------|-----------|-----------|
| **Base URL** | http://localhost:5173 | http://localhost:4000 |
| **API Server** | MSW interceptor | Real Python backend (8000) |
| **Data Source** | In-memory mocks | PostgreSQL database |
| **Projects** | Fake data | SwiftRide (5,686 items) |
| **Speed** | Fast (mocked) | Slower (real queries) |
| **Realism** | Low (synthetic) | High (production data) |
| **Isolation** | Complete | Depends on DB state |

## Test Data

### Mock Data (Used in Mock Mode)
- Defined in: `frontend/apps/web/src/mocks/data.ts`
- MSW handlers: `frontend/apps/web/src/mocks/handlers.ts`
- Example: 3-5 fake projects, ~100 items each

### Live Data (Used in Live Mode)
- Database: PostgreSQL at localhost:5432
- Test account: test@tracertm.io
- Primary dataset: SwiftRide project with 5,686 items
- Secondary: Platform In-Progress with 2,200+ items

## CI/CD Integration

### GitHub Actions Example
```yaml
# Run mock tests (fast)
- name: Run E2E tests (mock)
  run: npx playwright test
  timeout-minutes: 10

# Run live tests (slower, validate against real backend)
- name: Run E2E tests (live data)
  run: VITE_USE_MOCK_DATA=false npx playwright test
  timeout-minutes: 30
```

### Jenkins Example
```groovy
stage('E2E Tests - Mock') {
  sh 'npx playwright test'
}

stage('E2E Tests - Live') {
  environment {
    VITE_USE_MOCK_DATA = 'false'
    TEST_USER_EMAIL = 'test@tracertm.io'
  }
  sh 'npx playwright test'
}
```

## Troubleshooting

### Tests fail in live mode
**Problem**: Backend not running
```bash
# Check backend status
curl http://localhost:8000/health

# Start backend manually
cd /path/to/trace
python -m uvicorn tracertm.api.main:app --host 0.0.0.0 --port 8000
```

### MSW still intercepting in live mode
**Problem**: Environment variable not passed
```bash
# Make sure to set BEFORE running tests
export VITE_USE_MOCK_DATA=false
npx playwright test

# Or as one-liner
VITE_USE_MOCK_DATA=false npx playwright test
```

### Test account has no access to projects
**Problem**: Account membership changed in DB
```sql
-- Verify test account has access
SELECT au.user_id, au.role, a.name
FROM account_users au
JOIN accounts a ON au.account_id = a.id
WHERE au.user_id = '86f0050b-7758-460b-8271-0e00dc1b1ae0'::text;

-- Should return: test@tracertm.io | member | My Account
```

### Tests timeout in live mode
**Problem**: Large dataset (5,686 items) takes time
```bash
# Increase timeout
npx playwright test --timeout=60000  # 60 seconds

# Or set in playwright.config.ts:
timeout: 60 * 1000,
```

## Debugging

### View test logs
```bash
# Show detailed logs
npx playwright test --reporter=list

# Capture traces and videos
npx playwright test --trace=on --video=on
```

### Inspect API calls
```bash
# In test code
page.on('response', response => {
  console.log('API:', response.url(), response.status());
});

await page.goto('/home');
```

### Check network in Playwright Inspector
```bash
VITE_USE_MOCK_DATA=false npx playwright test --debug

# Browser DevTools equivalent in Playwright
# Step through and inspect each request
```

## Performance Benchmarks

### Expected Load Times (Live Mode)

| Operation | Time | Notes |
|-----------|------|-------|
| Dashboard load (5,686 items) | 2-5s | Real data, real API |
| Project list render | <1s | After API response |
| Item grid scroll (virtual) | <100ms | Smooth scrolling |
| Graph visualization (5,686 nodes) | 3-8s | Depends on GPU |
| Search query | 1-2s | Database query time |

### Memory Usage
- Mock tests: ~150-200 MB (per worker)
- Live tests: ~200-300 MB (real data in browser)

## Best Practices

1. **Use live tests for regression testing**
   - Validates real backend behavior
   - Catches database schema issues
   - Performance-based regressions

2. **Use mock tests for rapid development**
   - Fast feedback loop
   - Isolated from backend changes
   - Easier to debug

3. **Run both in CI/CD**
   - Mock: Quick validation (5-10 min)
   - Live: Comprehensive validation (15-30 min)

4. **Test critical paths with live data**
   - Dashboard loading
   - Large dataset handling
   - API integration

5. **Isolate test data**
   - Use test account (test@tracertm.io)
   - Don't modify production data
   - Clear test data after batch runs

## FAQ

**Q: Can I add my own test data to live tests?**
A: Yes, use database queries in global-setup to seed test data.

**Q: Do live tests modify the database?**
A: No, tests are read-only. Use transactions if you need to modify.

**Q: How do I run a single live test?**
A: `VITE_USE_MOCK_DATA=false npx playwright test dashboard-live-data.spec.ts`

**Q: Can I use live tests on CI/CD?**
A: Yes, but requires backend to be running. See CI/CD section.

**Q: Which mode should I use locally?**
A: Use mock for development, live for validation before push.

**Q: How often should I run live tests?**
A: Before commits, during PR validation, and nightly in CI/CD.

## Links

- [Playwright Documentation](https://playwright.dev)
- [Mock Service Worker (MSW)](https://mswjs.io)
- [Backend API Docs](http://localhost:8000/docs)
- [Test Account Database](postgresql://tracertm:tracertm_password@localhost:5432/tracertm)

## Support

For test failures or questions:
1. Check this documentation
2. Review test output with `--reporter=list`
3. Debug with `npx playwright test --debug`
4. Check backend logs: `tail -f .process-compose/process-compose.log`
