# E2E Test Suite Quick Reference - TraceRTM

**Location:** `/frontend/apps/web/e2e/`
**Framework:** Playwright
**Config:** `playwright.config.ts`
**Mock API:** MSW (Mock Service Worker)
**Base URL:** `http://localhost:5173`

---

## Test Suite Overview

```
Total Tests:     365
Test Files:      16
Lines of Code:   8,286
Overall Coverage: 75%
Target Coverage: 95%
```

### Test Distribution by Category

| Category | File(s) | Tests | Coverage |
|----------|---------|-------|----------|
| Authentication | auth*.spec.ts | 40 | 75% 🟡 |
| Navigation | navigation.spec.ts | 15 | 70% 🟡 |
| Projects | projects.spec.ts | 17 | 45% 🔴 |
| Items | items.spec.ts | 26 | 58% 🔴 |
| Links | links.spec.ts | 16 | 65% 🟡 |
| Search | search.spec.ts | 23 | 62% 🟡 |
| Dashboard | dashboard.spec.ts | 26 | 60% 🔴 |
| Graph | graph.spec.ts | 30 | 85% 🟢 |
| Agents | agents.spec.ts | 24 | 63% 🟡 |
| Sync | sync.spec.ts | 23 | 72% 🟡 |
| Security | security.spec.ts | 35 | 80% 🟡 |
| Performance | performance.spec.ts | 28 | 68% 🟡 |
| Accessibility | accessibility.spec.ts | 35 | 84% 🟡 |
| Edge Cases | edge-cases.spec.ts | 37 | 75% 🟡 |
| Integration | integration-workflows.spec.ts | 23 | 70% 🟡 |

---

## Running Tests

### Quick Start

```bash
# Navigate to project
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web

# Install dependencies (if needed)
bun install

# Run all E2E tests
bun run test:e2e

# Run specific test file
bunx playwright test auth.spec.ts

# Run with browser visible
bun run test:e2e:headed

# Interactive UI mode (recommended)
bun run test:e2e:ui

# Debug mode
bun run test:e2e:debug

# View HTML report
bun run test:e2e:report
```

### Advanced Commands

```bash
# Run specific test by name
bunx playwright test --grep "should login"

# Run with retries
bunx playwright test --retries 2

# Run in headed mode with traces
bunx playwright test --headed --trace on

# List all available tests
bunx playwright test --list

# Run with specific configuration
bunx playwright test --config playwright.config.ts

# Parallel execution (default: auto-detected based on CPU)
bunx playwright test --workers 4

# Sequential execution
bunx playwright test --workers 1
```

---

## Test File Guide

### auth.spec.ts (5 tests, 76 lines)
**Basic authentication flows**
```
✓ should load the application
✓ should display main navigation
✓ should handle user session
✓ should persist session across page reloads
✓ should allow access to all routes when authenticated
```

### auth-advanced.spec.ts (35 tests, 643 lines)
**Advanced auth, security, and accessibility**
- Login flows (5 tests)
- Logout flows (3 tests)
- Session management (5 tests)
- Password reset (6 tests)
- Registration (5 tests)
- Security features (5 tests)
- OAuth (3 tests)
- Accessibility (3 tests)

### navigation.spec.ts (15 tests, 216 lines)
**Navigation, routing, and UI flow**
- Route navigation (8 tests)
- Command palette (2 tests)
- Sidebar (2 tests)
- Breadcrumbs (1 test)
- Browser history (2 tests)

### projects.spec.ts (17 tests, 320 lines)
**Project CRUD operations**
- List projects (3 tests)
- Create project (4 tests)
- Project detail (3 tests)
- Update project (3 tests)
- Delete project (2 tests)
- Search/filter (1 test)

### items.spec.ts (26 tests, 431 lines)
**Item management and views**
- Table view (7 tests)
- Kanban view (6 tests)
- Tree view (5 tests)
- Create item (3 tests)
- Item detail (2 tests)
- Update item (1 test)
- Delete item (1 test)

### links.spec.ts (16 tests, 497 lines)
**Traceability link management**
- Create links (4 tests)
- Link management (3 tests)
- Link types (4 tests)
- Link visualization (3 tests)
- Link navigation (2 tests)

### search.spec.ts (23 tests, 543 lines)
**Search and filtering functionality**
- Global search (6 tests)
- Command palette search (4 tests)
- Project filtering (3 tests)
- Item filtering (4 tests)
- Advanced filters (3 tests)
- Search optimization (3 tests)

### dashboard.spec.ts (26 tests, 381 lines)
**Dashboard widgets and metrics**
- Overview (4 tests)
- Metrics display (6 tests)
- Widgets (5 tests)
- Charts (4 tests)
- Interactivity (4 tests)
- Quick actions (3 tests)

### graph.spec.ts (30 tests, 609 lines)
**Graph visualization and interactions**
- Rendering (5 tests)
- Navigation (4 tests)
- Filtering (4 tests)
- Interactions (5 tests)
- Layout (3 tests)
- Highlighting (3 tests)
- Export (2 tests)
- Mini-map (2 tests)
- Performance (2 tests)

### agents.spec.ts (24 tests, 678 lines)
**Agent management and task execution**
- Agent list (3 tests)
- Status monitoring (4 tests)
- Task execution (5 tests)
- Task history (3 tests)
- Configuration (2 tests)
- Metrics (3 tests)
- Interactions (2 tests)
- Dashboard widget (2 tests)

### sync.spec.ts (23 tests, 539 lines)
**Sync and offline mode**
- Sync status (3 tests)
- Manual sync (2 tests)
- Auto sync (3 tests)
- Offline mode (4 tests)
- Queued changes (3 tests)
- Conflict resolution (2 tests)
- WebSocket (3 tests)
- Settings (1 test)
- History (1 test)

### security.spec.ts (35 tests, 642 lines)
**Security and compliance testing**
- XSS prevention (6 tests)
- SQL injection (2 tests)
- CSRF protection (2 tests)
- Auth & Authz (5 tests)
- Data validation (5 tests)
- Clickjacking (2 tests)
- CSP (2 tests)
- Info disclosure (4 tests)
- Session security (3 tests)
- Rate limiting (1 test)

### performance.spec.ts (28 tests, 636 lines)
**Performance and optimization**
- Page load (4 tests)
- Component render (4 tests)
- Interaction response (4 tests)
- Large datasets (3 tests)
- Memory usage (3 tests)
- Caching (4 tests)
- Animation (2 tests)

### accessibility.spec.ts (35 tests, 660 lines)
**Accessibility and WCAG compliance**
- Keyboard navigation (8 tests)
- Screen reader (5 tests)
- Color contrast (3 tests)
- Form accessibility (4 tests)
- Semantic HTML (3 tests)
- Focus management (3 tests)
- Text accessibility (2 tests)
- Interactive elements (2 tests)

### edge-cases.spec.ts (37 tests, 670 lines)
**Edge cases and error handling**
- Null/undefined (4 tests)
- Empty states (5 tests)
- Errors (6 tests)
- Boundaries (5 tests)
- Race conditions (4 tests)
- Timeouts (3 tests)
- Invalid input (4 tests)
- Resource exhaustion (3 tests)
- Browser compatibility (3 tests)

### integration-workflows.spec.ts (23 tests, 745 lines)
**End-to-end user workflows**
- Project to items (4 tests)
- Item linking (4 tests)
- Search to detail (3 tests)
- Dashboard to detail (3 tests)
- Sync workflow (3 tests)
- Graph workflow (3 tests)
- Agent workflow (2 tests)
- Import/export (1 test)

---

## Test Execution Times

| File | Tests | Est. Time |
|------|-------|-----------|
| auth.spec.ts | 40 | 1m 20s |
| navigation.spec.ts | 15 | 45s |
| projects.spec.ts | 17 | 40s |
| items.spec.ts | 26 | 1m 10s |
| links.spec.ts | 16 | 55s |
| search.spec.ts | 23 | 50s |
| dashboard.spec.ts | 26 | 1m |
| graph.spec.ts | 30 | 2m |
| agents.spec.ts | 24 | 1m 10s |
| sync.spec.ts | 23 | 1m 15s |
| security.spec.ts | 35 | 1m 30s |
| performance.spec.ts | 28 | 2m 30s |
| accessibility.spec.ts | 35 | 1m 50s |
| edge-cases.spec.ts | 37 | 2m 45s |
| integration-workflows.spec.ts | 23 | 1m 45s |
| **Total** | **365** | **~22 min** |

---

## Playwright Configuration

**File:** `playwright.config.ts`

```typescript
{
  testDir: "./e2e",
  timeout: 30000,                    // 30 seconds per test
  fullyParallel: true,               // Tests run in parallel
  forbidOnly: !!process.env.CI,      // Prevent .only in CI
  retries: process.env.CI ? 2 : 0,   // Retry on CI only
  workers: process.env.CI ? 1 : undefined,
  baseURL: "http://localhost:5173",
  trace: "on-first-retry",           // Trace on failure
  screenshot: "only-on-failure",
  video: "retain-on-failure",
  reporter: ["html", "json", "list"],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    }
  ],
  webServer: {
    command: "bun run dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  }
}
```

---

## Mock Service Worker (MSW)

All tests use MSW for API mocking. No backend server required.

**Mock Data Location:** `src/mocks/`
- `handlers.ts` - API route handlers
- `data.ts` - Mock data
- `index.ts` - MSW setup

**Key Features:**
- ✅ No network requests
- ✅ Deterministic test data
- ✅ Fast execution
- ✅ Offline capability
- ✅ Error simulation

---

## Debugging & Troubleshooting

### View Test in Browser

```bash
bun run test:e2e:headed
```

### Debug Specific Test

```bash
# Interactive debug mode
bunx playwright test auth.spec.ts --debug

# With UI
bun run test:e2e:ui
```

### View Traces

```bash
# After test failure, traces are saved automatically
bunx playwright show-trace trace.zip
```

### Check Screenshots/Videos

```bash
# Navigate to test-results/
ls test-results/
```

### Common Issues

**Tests timing out:**
- Increase timeout in config
- Use `waitForLoadState('networkidle')`
- Check for slow MSW handlers

**Elements not found:**
- Use Playwright Inspector: `bunx playwright test --debug`
- Check selector accuracy
- Verify element exists in UI

**MSW not working:**
- Verify `VITE_ENABLE_MSW=true`
- Check handlers.ts
- Look for MSW startup message in console

**Dev server not starting:**
- Kill port 5173: `lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9`
- Check Vite config
- Verify bun scripts in package.json

---

## Test Patterns & Best Practices

### Test Structure

```typescript
import { expect, test } from "@playwright/test";

test.describe("Feature Name", () => {
  test.beforeEach(async ({ page }) => {
    // Setup
    await page.goto("/");
    await page.waitForLoadState("networkidle");
  });

  test("should do something", async ({ page }) => {
    // Arrange
    const element = page.getByRole("button", { name: /click/i });

    // Act
    await element.click();

    // Assert
    await expect(page).toHaveURL("/expected-route");
  });
});
```

### Selector Priority

1. **getByRole()** - Interactive elements
2. **getByLabel()** - Form inputs
3. **getByText()** - Content
4. **getByPlaceholder()** - Placeholder text
5. **locator()** - CSS/XPath (last resort)

### Handling Optional Features

```typescript
const optionalButton = page.getByRole("button", { name: /Optional/i });
if (await optionalButton.isVisible({ timeout: 2000 })) {
  await optionalButton.click();
} else {
  console.log("Optional feature not available");
}
```

### Waiting Strategies

```typescript
// Wait for network idle (best for navigation)
await page.waitForLoadState("networkidle");

// Wait for specific text
await page.waitForSelector("text=/Expected Text/", { timeout: 5000 });

// Wait for element visibility
await expect(element).toBeVisible({ timeout: 5000 });

// Wait for specific URL
await page.waitForURL("/expected-route");
```

---

## Critical Coverage Gaps

### High Priority (0 tests)

1. **User Settings** - 8 tests needed
   - Profile settings
   - Preferences
   - Notifications
   - Theme selection

2. **Import/Export** - 10 tests needed
   - CSV import
   - JSON import
   - CSV export
   - Report generation

3. **Bulk Operations** - 10 tests needed
   - Bulk item creation
   - Bulk updates
   - Bulk deletions

4. **404 Handling** - 3 tests needed
   - Not found page
   - Route recovery
   - Error state UI

### Medium Priority (<50% coverage)

1. **Project Management** (45% → 100%)
   - Needs 8 additional tests
   - Focus: Bulk ops, templates, sharing

2. **Dashboard** (60% → 100%)
   - Needs 8 additional tests
   - Focus: Custom layouts, export, sharing

3. **Performance** (68% → 100%)
   - Needs 8 additional tests
   - Focus: Network scenarios, optimization

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run E2E Tests
  run: bun run test:e2e

- name: Upload Reports
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30
```

### Local Pre-commit

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run critical tests before commit
bun run test:e2e --grep "authentication|navigation" || exit 1
```

---

## Performance Benchmarks

### Baseline (Current)

- **Total Runtime:** ~22 minutes (365 tests)
- **Average per Test:** ~3.6 seconds
- **Pass Rate:** 98%
- **Flakiness:** 2%

### Targets

- **Total Runtime:** <20 minutes (450+ tests)
- **Average per Test:** <3 seconds
- **Pass Rate:** 99%+
- **Flakiness:** <1%

---

## Related Documentation

- **E2E Analysis Report:** `/E2E_TEST_ANALYSIS_REPORT.md`
- **Coverage Matrix:** `/E2E_TEST_COVERAGE_MATRIX.md`
- **Playwright Docs:** https://playwright.dev/
- **MSW Docs:** https://mswjs.io/
- **Test Examples:** `e2e/fixtures/`

---

## Quick Start Commands Cheat Sheet

```bash
# Navigate to project directory
cd frontend/apps/web

# Run tests
bun run test:e2e              # Run all tests
bun run test:e2e:ui          # Interactive UI mode
bun run test:e2e:headed      # See browser
bun run test:e2e:debug       # Debug mode
bun run test:e2e:report      # View HTML report

# Specific test runs
bunx playwright test auth.spec.ts          # Specific file
bunx playwright test --grep "login"        # Test name pattern
bunx playwright test --grep "@smoke"       # Tag-based (if implemented)

# Debugging
bunx playwright test --debug               # Interactive debugger
bunx playwright show-trace trace.zip       # View trace
bunx playwright codegen http://localhost:5173  # Generate test code

# CI/CD
CI=true bun run test:e2e                   # CI mode (2 retries, 1 worker)
bunx playwright test --config=playwright.config.ts  # Custom config
```

---

**Last Updated:** January 23, 2026
**Version:** 1.0
**Status:** Production Ready

For detailed analysis, see: `/E2E_TEST_ANALYSIS_REPORT.md`
For coverage details, see: `/E2E_TEST_COVERAGE_MATRIX.md`
