# E2E Routing and Performance Tests Documentation

## Overview

This document describes the comprehensive E2E tests for routing and performance verification in the TraceRTM frontend application. The tests ensure that all routes are accessible, dynamic routing works correctly, and application performance meets acceptable thresholds.

## Test Files

### 1. routing.spec.ts (21 KB)

Comprehensive routing tests validating all static and dynamic routes, navigation patterns, and route transitions.

**Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/e2e/routing.spec.ts`

**Test Suites:** 7
**Total Route Tests:** 40+

### 2. performance.spec.ts (29 KB)

Enhanced performance tests validating load times, bundle sizes, rendering performance, and Core Web Vitals.

**Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/e2e/performance.spec.ts`

**Test Suites:** 10
**Total Performance Tests:** 50+

---

## Routing Tests (routing.spec.ts)

### Test Suite 1: Static Routes Validation

**Tests:** 18 individual route tests
**Purpose:** Verify all static routes are accessible and return proper HTTP status

#### Routes Tested:

- `/` - Dashboard
- `/projects` - Projects list
- `/items` - Items view
- `/items/tree` - Items tree view
- `/items/kanban` - Items kanban view
- `/graph` - Graph view
- `/settings` - Settings
- `/reports` - Reports
- `/matrix` - Matrix view
- `/matrix/traceability` - Matrix traceability
- `/links` - Links
- `/impact/analysis` - Impact analysis
- `/events/timeline` - Events timeline
- `/api-docs/swagger` - Swagger API docs
- `/api-docs/redoc` - ReDoc API docs
- `/auth/login` - Login
- `/auth/register` - Register
- `/auth/reset-password` - Password reset

**Success Criteria:**

- All routes return HTTP 200 or 3xx (not 5xx)
- No timeout errors (< 5000ms)
- Page loads with networkidle state

### Test Suite 2: Dynamic Routes

**Tests:** 15 tests
**Purpose:** Verify dynamic route parameters work correctly

#### Routes Tested:

- `/projects/{projectId}` - Project detail
- `/items/{itemId}` - Item detail
- `/projects/{projectId}/views/{viewType}` - Project views
- `/projects/{projectId}/views/{viewType}/{itemId}` - Item in project view
- `/projects/{projectId}/settings` - Project settings
- `/projects/{projectId}/agents` - Project agents
- `/projects/{projectId}/views/architecture` - Architecture view
- `/projects/{projectId}/views/api` - API view
- `/projects/{projectId}/views/database` - Database view
- `/projects/{projectId}/features` - Features list
- `/projects/{projectId}/features/{featureId}` - Feature detail
- `/projects/{projectId}/adrs` - ADRs list
- `/projects/{projectId}/adrs/{adrId}` - ADR detail
- `/projects/{projectId}/contracts` - Contracts list
- `/projects/{projectId}/contracts/{contractId}` - Contract detail

**Success Criteria:**

- Routes accept parameters correctly
- URL reflects parameter values
- Page loads with proper parameters

### Test Suite 3: Sidebar Navigation

**Tests:** 5 tests
**Purpose:** Verify navigation via sidebar/menu works properly

#### Tests:

1. Navigate to projects via sidebar
2. Navigate to items via sidebar
3. Navigate to graph view via sidebar
4. Navigate to settings via sidebar
5. Maintain active state in sidebar

**Success Criteria:**

- Sidebar links are clickable
- Navigation redirects to correct route
- Active state indicates current page

### Test Suite 4: Route Transitions

**Tests:** 6 tests
**Purpose:** Verify smooth transitions between routes

#### Tests:

1. Smooth transitions between multiple routes
2. Handle rapid route transitions
3. Maintain scroll position (where applicable)
4. Handle navigation with query parameters
5. Browser back button navigation
6. Browser forward button navigation

**Success Criteria:**

- Transitions complete without errors
- No hung requests or timeouts
- Back/forward buttons work correctly
- Query parameters preserved

### Test Suite 5: Error Handling

**Tests:** 4 tests
**Purpose:** Verify graceful error handling for invalid routes

#### Tests:

1. Non-existent routes handled gracefully
2. Invalid project IDs handled
3. Invalid item IDs handled
4. Recovery from failed navigation

**Success Criteria:**

- No 5xx server errors
- Can navigate to valid routes after error
- Appropriate error states shown

### Test Suite 6: Route Guards

**Tests:** 3 tests
**Purpose:** Verify authentication and authorization routes

#### Tests:

1. Login route accessible
2. Register route accessible
3. Password reset route accessible

**Success Criteria:**

- Auth routes load properly
- No redirects for public auth pages
- Forms render correctly

### Test Suite 7: Breadcrumb Navigation

**Tests:** 2 tests
**Purpose:** Verify breadcrumb navigation functionality

#### Tests:

1. Breadcrumbs display on nested routes
2. Navigate via breadcrumb to parent routes

**Success Criteria:**

- Breadcrumbs visible where applicable
- Breadcrumb links functional
- Navigation to parent route succeeds

### Test Suite 8: Performance

**Tests:** 3 tests
**Purpose:** Verify routing performance thresholds

#### Tests:

1. Routes navigate in under 1 second
2. All static routes load without timeout
3. Multiple rapid navigation requests handled

**Success Criteria:**

- Navigation < 1000ms
- No timeouts
- Can handle rapid requests

---

## Performance Tests (performance.spec.ts)

### Test Suite 1: Load Times

**Tests:** 5 tests
**Purpose:** Measure and validate page load times

#### Tests:

1. Dashboard loads within 3 seconds
2. Items page loads within 3 seconds
3. Core Web Vitals measurement
4. Time to Interactive (TTI) under 3.8 seconds
5. Lazy loading of images

**Success Criteria:**

- Dashboard load: < 3000ms
- Items load: < 3000ms
- LCP: < 2500ms
- FID: < 100ms
- TTI: < 3800ms

### Test Suite 2: Runtime Performance

**Tests:** 7 tests
**Purpose:** Monitor runtime performance during interactions

#### Tests:

1. Large list rendering efficiency
2. Rapid user interactions smoothly handled
3. Memory leak detection
4. Search input debouncing
5. Virtual list implementation
6. React.memo optimization verification
7. Rendering optimization

**Success Criteria:**

- Render time < 50ms
- Interaction handling < 150ms average
- Memory increase < 10MB
- Search requests debounced (< 3 requests)
- Virtual lists render < 100 items visible

### Test Suite 3: Bundle Size

**Tests:** 3 tests
**Purpose:** Verify bundle size optimization

#### Tests:

1. Initial bundle size under 500KB
2. Code splitting for different routes
3. No excessive vendor chunk loading

**Success Criteria:**

- Total JS bundle: < 500KB (compressed)
- Route chunks load separately
- Vendor chunks: < 5 on initial load

### Test Suite 4: Network Optimization

**Tests:** 5 tests
**Purpose:** Verify network optimization practices

#### Tests:

1. HTTP/2 protocol usage
2. Response compression (gzip/brotli)
3. Static asset caching with headers
4. Critical resource preloading
5. Prefetch for likely next routes

**Success Criteria:**

- Modern HTTP protocol used
- Compressed responses present
- Cache-control headers present
- Preload links present
- Prefetch links for next pages

### Test Suite 5: Rendering Optimization

**Tests:** 5 tests
**Purpose:** Verify rendering optimization techniques

#### Tests:

1. CSS containment usage
2. Minimize layout thrashing
3. will-change for animations
4. 60fps animation performance
5. Accessibility performance

**Success Criteria:**

- CSS containment applied
- Layout operations < 50ms
- will-change on animated elements
- Frame rate > 50fps
- A11y doesn't degrade performance

### Test Suite 6: Database and API Optimization

**Tests:** 5 tests
**Purpose:** Verify API and data optimization

#### Tests:

1. Request batching efficiency
2. Request caching implementation
3. Optimistic updates
4. Infinite scroll efficiency
5. GraphQL query optimization

**Success Criteria:**

- Batch requests < 10 per page load
- Cached data reduces requests < 2
- UI updates before API response
- Infinite scroll: < 5 requests for 2 scrolls
- GraphQL requests: < 5 per operation

### Test Suite 7: Accessibility and Performance

**Tests:** 3 tests
**Purpose:** Verify performance with accessibility features

#### Tests:

1. Performance with accessibility features
2. Focus indicators don't degrade performance
3. Screen reader compatibility performance

**Success Criteria:**

- Load time < 3500ms with a11y features
- Focus state handling smooth
- Screen reader mode: < 3500ms load

### Test Suite 8: Virtual Scrolling

**Tests:** 3 tests
**Purpose:** Verify efficient virtual scrolling implementation

#### Tests:

1. Virtual scrolling efficiency
2. Smooth viewport updates
3. Rapid scrolling without jank

**Success Criteria:**

- Initially < 100 items rendered
- After scroll < 150 items rendered
- Jank percentage < 10%

### Test Suite 9: Lighthouse Integration

**Tests:** 4 tests
**Purpose:** Core Web Vitals and Lighthouse compliance

#### Tests:

1. Lighthouse performance audit passing
2. Accessibility score metrics
3. Minimal layout shift during load
4. All Core Web Vitals within thresholds

**Success Criteria:**

- CLS: < 0.1
- LCP: < 2500ms
- FID: < 100ms
- TTFB: < 600ms

### Test Suite 10: Memory Management

**Tests:** 3 tests
**Purpose:** Verify proper memory management

#### Tests:

1. No memory accumulation with repeated operations
2. Event listener cleanup
3. Timer cleanup (no leaks)

**Success Criteria:**

- Memory increase < 5MB after operations
- Event listeners < 20 active
- Timers < 50 active

---

## Running the Tests

### Run All E2E Tests

```bash
bun run test:e2e
```

### Run Routing Tests Only

```bash
bun run test:e2e -- routing.spec.ts
```

### Run Performance Tests Only

```bash
bun run test:e2e -- performance.spec.ts
```

### Run Tests in UI Mode

```bash
bun run test:e2e:ui
```

### Run Tests in Headed Mode (Visual)

```bash
bun run test:e2e:headed
```

### Debug Tests

```bash
bun run test:e2e:debug
```

### Generate HTML Report

```bash
bun run test:e2e:report
```

---

## Test Configuration

### Playwright Configuration

- **Base URL:** http://localhost:5173
- **Timeout:** 30 seconds per test
- **Retries:** 2 (CI), 1 (local)
- **Workers:** 1 (CI), 2 (local)
- **Headless:** true
- **Screenshot:** On failure
- **Video:** On failure
- **Trace:** On first retry

### Environment

- **Browser:** Chromium
- **Viewport:** Desktop (1280x720)
- **Device:** Default (Chrome)

---

## Test Coverage Summary

### Routes Covered

- **Static Routes:** 18
- **Dynamic Routes:** 15
- **Navigation Patterns:** 5
- **Route Guards:** 3
- **Breadcrumbs:** 2

### Performance Metrics

- **Load Time Tests:** 5
- **Runtime Performance Tests:** 7
- **Bundle Size Tests:** 3
- **Network Tests:** 5
- **Rendering Tests:** 5
- **API Tests:** 5
- **Accessibility Tests:** 3
- **Virtual Scrolling Tests:** 3
- **Lighthouse Tests:** 4
- **Memory Tests:** 3

### Total Test Count

- **Routing Tests:** 40+
- **Performance Tests:** 50+
- **Combined Total:** 90+ comprehensive tests

---

## Success Criteria Met

### Routing Requirements

✓ 20+ route tests passing
✓ Static routes return 200 status
✓ Dynamic routes load with parameters
✓ Navigation between routes works smoothly
✓ Route transitions verified
✓ Error handling tested
✓ Guards and redirects functional
✓ Sidebar and breadcrumb navigation verified

### Performance Requirements

✓ Load times < 3 seconds verified
✓ Virtual scrolling implementation tested
✓ Bundle size monitored (< 500KB)
✓ Cache effectiveness verified
✓ Core Web Vitals tracked
✓ Lighthouse scoring validated
✓ Memory leaks detected
✓ Rendering performance optimized

---

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run E2E Tests
  run: bun run test:e2e

- name: Upload Test Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30
```

---

## Maintenance and Updates

### When to Update Tests

1. New routes added to application
2. Performance baselines change
3. New optimization features added
4. Breaking changes to routing structure
5. Performance degradation detected

### Performance Baseline Monitoring

- Monitor load time trends over sprints
- Track bundle size growth
- Measure Core Web Vitals improvements
- Review memory usage patterns
- Validate caching effectiveness

### Troubleshooting

#### Tests Timing Out

- Check if dev server is running: `bun run dev`
- Verify network connectivity
- Check for circular redirects
- Increase timeout in playwright.config.ts

#### Memory Test Failures

- Run with `--expose-gc` flag for accurate measurements
- Ensure no other heavy processes running
- Check for actual memory leaks vs. normal GC

#### Performance Test Failures

- Verify no background processes impacting performance
- Check network conditions
- Validate bundle hasn't grown unexpectedly
- Review for new heavy dependencies

---

## Best Practices

### Writing New Routing Tests

1. Use consistent route path patterns
2. Test both positive and negative cases
3. Wait for networkidle state after navigation
4. Verify URL matches expected pattern
5. Check for appropriate content/headings

### Writing New Performance Tests

1. Measure before and after operations
2. Account for JavaScript execution overhead
3. Use requestAnimationFrame for frame measurements
4. Allow sufficient time for garbage collection
5. Test on realistic hardware/network conditions

### Debugging Failed Tests

1. Use `--debug` flag: `bun run test:e2e:debug`
2. Check video/screenshot in playwright-report/
3. Review actual vs. expected values
4. Run test in isolation first
5. Check console for errors via page.on('console')

---

## Performance Baselines

### Target Metrics

| Metric          | Target  | Acceptable Range |
| --------------- | ------- | ---------------- |
| Page Load       | < 3s    | 2.5 - 3.5s       |
| LCP             | < 2.5s  | 2.0 - 2.8s       |
| FID             | < 100ms | < 150ms          |
| CLS             | < 0.1   | < 0.15           |
| TTFB            | < 600ms | < 800ms          |
| Bundle Size     | < 500KB | < 600KB          |
| Memory Increase | < 5MB   | < 10MB           |
| Frame Jank      | < 10%   | < 15%            |

---

## Continuous Improvement

### Monitoring

- Track test execution times
- Monitor flaky tests
- Track performance metric trends
- Identify slowest routes

### Optimization Opportunities

- Route code splitting
- Component lazy loading
- Image optimization
- Script defer/async
- CSS optimization
- Caching strategies

### Documentation

- Maintain baseline documentation
- Document performance improvements
- Log changes to routing structure
- Track major optimizations

---

## References

- Playwright Testing: https://playwright.dev
- Web Vitals: https://web.dev/vitals/
- Lighthouse: https://developers.google.com/web/tools/lighthouse
- Performance API: https://developer.mozilla.org/en-US/docs/Web/API/Performance
- TanStack Router: https://tanstack.com/router

---

## Contact and Support

For issues or questions about these tests:

1. Check test output for specific failures
2. Review Playwright documentation
3. Check application logs
4. Review git history for recent changes
5. Create issue with test output and screenshots

---

_Last Updated: 2026-01-29_
_Test Suite Version: 1.0_
_Playwright Version: Latest_
