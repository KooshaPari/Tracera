# E2E Test Execution Guide

## Quick Start

### Prerequisites

- Node.js/Bun runtime
- Frontend development environment set up
- Port 5173 available (dev server)

### Setup

```bash
# Install dependencies
bun install

# From the web app directory
cd frontend/apps/web
```

## Test Commands

### 1. Run All E2E Tests

```bash
bun run test:e2e
```

Executes all test files in the `e2e/` directory including:

- routing.spec.ts (40+ tests)
- performance.spec.ts (50+ tests)
- All other E2E test files

**Expected Duration:** 5-10 minutes
**Expected Result:** 90+ tests passing

### 2. Run Specific Test File

#### Routing Tests Only

```bash
bun run test:e2e -- e2e/routing.spec.ts
```

**Expected Duration:** 2-3 minutes
**Test Count:** 40+ tests

#### Performance Tests Only

```bash
bun run test:e2e -- e2e/performance.spec.ts
```

**Expected Duration:** 3-5 minutes
**Test Count:** 50+ tests

### 3. Interactive UI Mode

```bash
bun run test:e2e:ui
```

- Opens interactive test runner
- See test progress in real-time
- Click tests to run individually
- View test reports

**Best For:** Development and debugging

### 4. Headed Mode (Visual)

```bash
bun run test:e2e:headed
```

- Runs tests with visible browser window
- See exact interaction sequences
- Useful for debugging failures

**Best For:** Debugging flaky tests

### 5. Debug Mode

```bash
bun run test:e2e:debug
```

- Opens Playwright Inspector
- Step through tests
- Inspect elements
- Evaluate expressions

**Best For:** Deep debugging

### 6. Generate Test Report

```bash
bun run test:e2e:report
```

Opens HTML report showing:

- Test results summary
- Pass/fail breakdown
- Screenshots of failures
- Video recordings (if enabled)

### 7. Run Single Test

```bash
# Run specific test by name
bun run test:e2e -- --grep "should load dashboard"

# Run tests matching pattern
bun run test:e2e -- --grep "Route Navigation"
```

## Test Execution Workflow

### 1. Before Running Tests

```bash
# Start development server in separate terminal
bun run dev

# Wait for server to be ready
# You should see: "Local: http://localhost:5173"
```

### 2. Run Tests

```bash
# Keep dev server running in another terminal
bun run test:e2e

# Watch for results
```

### 3. Review Results

```bash
# If tests fail, view detailed report
bun run test:e2e:report

# For specific failures, run in debug mode
bun run test:e2e:debug
```

## Expected Test Results

### Routing Tests (routing.spec.ts)

| Test Suite            | Test Count | Status     |
| --------------------- | ---------- | ---------- |
| Static Routes         | 18         | ✓ Pass     |
| Dynamic Routes        | 15         | ✓ Pass     |
| Sidebar Navigation    | 5          | ✓ Pass     |
| Route Transitions     | 6          | ✓ Pass     |
| Error Handling        | 4          | ✓ Pass     |
| Route Guards          | 3          | ✓ Pass     |
| Breadcrumb Navigation | 2          | ✓ Pass     |
| Performance           | 3          | ✓ Pass     |
| **Total**             | **40+**    | **✓ Pass** |

### Performance Tests (performance.spec.ts)

| Test Suite                    | Test Count | Status     |
| ----------------------------- | ---------- | ---------- |
| Load Times                    | 5          | ✓ Pass     |
| Runtime Performance           | 7          | ✓ Pass     |
| Bundle Size                   | 3          | ✓ Pass     |
| Network Optimization          | 5          | ✓ Pass     |
| Rendering Optimization        | 5          | ✓ Pass     |
| Database and API              | 5          | ✓ Pass     |
| Accessibility and Performance | 3          | ✓ Pass     |
| Virtual Scrolling             | 3          | ✓ Pass     |
| Lighthouse Integration        | 4          | ✓ Pass     |
| Memory Management             | 3          | ✓ Pass     |
| **Total**                     | **50+**    | **✓ Pass** |

## Troubleshooting

### Issue: Tests Timeout

**Symptoms:** Tests hang and eventually timeout

**Solutions:**

1. Ensure dev server is running:

   ```bash
   bun run dev
   ```

2. Check if port 5173 is in use:

   ```bash
   lsof -i :5173
   ```

3. Increase timeout in playwright.config.ts:
   ```typescript
   timeout: 60 * 1000; // 60 seconds
   ```

### Issue: Tests Fail with Network Errors

**Symptoms:** 404 or connection errors

**Solutions:**

1. Verify API mocks are loaded
2. Check browser console for errors:

   ```bash
   bun run test:e2e:debug
   ```

3. Ensure mock data is available:
   ```bash
   bun run populate:mock
   ```

### Issue: Performance Tests Fail

**Symptoms:** Load time or memory tests fail

**Solutions:**

1. Close other applications consuming resources
2. Run test in isolation:

   ```bash
   bun run test:e2e -- --grep "should load dashboard"
   ```

3. Check system performance during test:
   ```bash
   # Monitor in another terminal
   top  # macOS/Linux
   ```

### Issue: Visual/Screenshot Differences

**Symptoms:** Visual regression test failures

**Solutions:**

1. Update snapshots if changes are intentional:

   ```bash
   bun run test:visual:update
   ```

2. Review differences in report:
   ```bash
   bun run test:visual:report
   ```

### Issue: Flaky Tests

**Symptoms:** Tests pass sometimes, fail other times

**Solutions:**

1. Increase wait times:

   ```typescript
   await page.waitForLoadState('networkidle');
   await page.waitForTimeout(1000);
   ```

2. Run multiple times to confirm:

   ```bash
   bun run test:e2e -- --repeat-each=3
   ```

3. Run in headed mode to observe:
   ```bash
   bun run test:e2e:headed
   ```

## Performance Baselines

### Load Time Thresholds

```
Dashboard: < 3000ms  (target: 2000ms)
Items Page: < 3000ms (target: 2000ms)
Other Pages: < 3000ms (target: 2000ms)
```

### Core Web Vitals Targets

```
LCP: < 2500ms (Largest Contentful Paint)
FID: < 100ms  (First Input Delay)
CLS: < 0.1    (Cumulative Layout Shift)
TTFB: < 600ms (Time to First Byte)
```

### Memory Targets

```
Initial Memory: < 50MB
After Operations: < 5MB increase
Peak Memory: < 100MB
```

### Bundle Size Targets

```
Total JS: < 500KB (compressed)
Main Bundle: < 200KB
Vendor Bundle: < 150KB
Other Chunks: < 150KB
```

## Continuous Integration

### GitHub Actions Integration

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: oven-sh/setup-bun@v1

      - run: bun install

      - run: cd frontend/apps/web && bun run test:e2e

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/apps/web/playwright-report/
          retention-days: 30
```

## Performance Profiling

### Measure Individual Test

```bash
# Run with trace enabled
bun run test:e2e -- --trace on
```

### View Trace File

```bash
# In Playwright Inspector
bun run test:e2e:debug

# Then open trace file:
# playwright-report/trace.zip
```

## Test Coverage Analysis

### Routes Tested

**Static Routes (18):**

- Dashboard, Projects, Items, Graph, Settings
- Reports, Matrix, Links, Impact, Events
- API Docs (Swagger/ReDoc)
- Authentication (Login, Register, Reset)

**Dynamic Routes (15):**

- Project Details, Item Details
- Project Views, Project Settings
- Project Agents, Features, ADRs, Contracts

**Navigation (5):**

- Sidebar navigation
- Breadcrumb navigation
- Route transitions
- Back/Forward navigation

### Performance Metrics Tested

- **Load Times:** 5 tests
- **Runtime Performance:** 7 tests
- **Bundle Size:** 3 tests
- **Network:** 5 tests
- **Rendering:** 5 tests
- **API:** 5 tests
- **Accessibility:** 3 tests
- **Virtual Scrolling:** 3 tests
- **Lighthouse:** 4 tests
- **Memory:** 3 tests

## Advanced Testing

### Run Tests Against Different Browsers

```bash
# Modify playwright.config.ts to enable multiple browsers
# Then run:
bun run test:e2e
```

### Run Tests in Parallel (if safe)

```bash
# Edit playwright.config.ts:
fullyParallel: true

bun run test:e2e
```

### Generate Performance Report

```bash
# Extract timing information
bun run test:e2e -- --reporter=list
```

### Watch Mode

```bash
# Monitor changes and re-run affected tests
bun run test:e2e -- --watch
```

## Debugging Best Practices

### 1. Use Page Events

```typescript
page.on('console', console.log);
page.on('error', console.error);
page.on('pageerror', console.error);
```

### 2. Add Debug Logs

```typescript
test('should load route', async ({ page }) => {
  console.log('Starting test...');
  await page.goto('/');
  console.log('Page loaded:', page.url());
  // ... assertions
});
```

### 3. Screenshot on Failure

```typescript
// Already enabled in playwright.config.ts
// Check: playwright-report/
```

### 4. Video Recording

```typescript
// Already enabled in playwright.config.ts
// Check: playwright-report/
```

## Performance Optimization Tips

### For Faster Test Execution

1. Use headed: false (default)
2. Disable videos/traces when not needed
3. Run tests in parallel (when possible)
4. Use smaller wait times where applicable

### For Better Debugging

1. Enable headed mode
2. Enable video recording
3. Enable trace on first retry
4. Use screenshot on failure

## Maintenance Schedule

### Daily

- Run full test suite before merge
- Monitor test results

### Weekly

- Review flaky tests
- Update performance baselines
- Check test coverage

### Monthly

- Analyze performance trends
- Update test data/fixtures
- Review and refactor tests

## Contact & Support

### Issues with Tests

1. Check test output for specific error
2. Review Playwright documentation
3. Check if dev server is running
4. Run test in debug mode
5. Create issue with test name and error

### Performance Issues

1. Run performance test in isolation
2. Check system resources
3. Review recent code changes
4. Profile with browser DevTools
5. Check bundle size changes

---

_Last Updated: 2026-01-29_
_Version: 1.0_
