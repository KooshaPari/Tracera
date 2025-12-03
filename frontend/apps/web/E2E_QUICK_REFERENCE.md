# TraceRTM E2E Testing - Quick Reference

## Running Tests

```bash
# Run all E2E tests
bun run test:e2e

# Interactive UI mode (recommended)
bun run test:e2e:ui

# Watch mode with browser
bun run test:e2e:headed

# Debug mode
bun run test:e2e:debug

# View HTML report
bun run test:e2e:report

# Run specific test file
bunx playwright test links.spec.ts

# Run specific test by name
bunx playwright test -g "should create link"

# Run all tests (unit + E2E + visual)
bun run test:all
```

## Test Files (205 total tests)

| File | Tests | Coverage |
|------|-------|----------|
| `agents.spec.ts` | 24 | Agent management, status, tasks, config |
| `auth.spec.ts` | 5 | Authentication, session, route access |
| `dashboard.spec.ts` | 26 | Overview, metrics, widgets, charts |
| `graph.spec.ts` | 30 | Visualization, interactions, filtering |
| `items.spec.ts` | 26 | CRUD, views (table/kanban/tree), search |
| `links.spec.ts` | 16 | Create/delete links, navigation, stats |
| `navigation.spec.ts` | 15 | Routing, command palette, breadcrumbs |
| `projects.spec.ts` | 17 | CRUD operations, search, filtering |
| `search.spec.ts` | 23 | Global search, filters, command palette |
| `sync.spec.ts` | 23 | Sync status, offline mode, WebSocket |

## Test Fixtures

### Import Fixtures
```typescript
import {
  // Data generators
  generateTestProject,
  generateTestItem,
  generateTestLink,

  // Page helpers
  navigateToProjects,
  fillProjectForm,
  submitForm,
  assertSuccessMessage,

  // Form data
  formInputs,
  filters,
  searchQueries
} from './fixtures'
```

### Common Patterns

#### Navigation
```typescript
await navigateToProjects(page)
await navigateToItems(page)
await navigateToGraph(page)
await navigateToAgents(page)
```

#### Command Palette
```typescript
await openCommandPalette(page)  // Cmd/Ctrl+K
await searchInCommandPalette(page, 'items')
await executeCommand(page, 'create project')
```

#### Forms
```typescript
await fillProjectForm(page, {
  name: 'Test Project',
  description: 'Description'
})
await submitForm(page)
await assertSuccessMessage(page)
```

#### Search & Filter
```typescript
await searchGlobal(page, 'authentication')
await applyFilter(page, /type/i, /requirement/i)
await clearFilters(page)
```

#### CRUD Operations
```typescript
await createProject(page, { name: 'New Project' })
await createItem(page, { title: 'New Item', type: 'feature' })
await deleteItem(page, 'Item Name')
await updateItemStatus(page, 'Item Name', 'completed')
```

#### Assertions
```typescript
await assertSuccessMessage(page)
await assertErrorMessage(page, /invalid/i)
await assertPageTitle(page, /projects/i)
```

#### Offline Mode
```typescript
await goOffline(page)
// Test offline functionality
await goOnline(page)
```

## Key User Flows

### Flow 1: Create Project → Add Items → Link Items → View Graph
```typescript
test('complete workflow', async ({ page }) => {
  // Create project
  await navigateToProjects(page)
  await page.getByRole('button', { name: /create/i }).click()
  await fillProjectForm(page, { name: 'Test Project' })
  await submitForm(page)

  // Add items
  await navigateToItems(page)
  await page.getByRole('button', { name: /create/i }).click()
  await fillItemForm(page, {
    title: 'Requirement 1',
    type: 'requirement'
  })
  await submitForm(page)

  // Create link
  await page.getByRole('button', { name: /add link/i }).click()
  // ... fill link form

  // View graph
  await navigateToGraph(page)
  const graph = page.locator('[data-testid="graph-container"]')
  await expect(graph).toBeVisible()
})
```

### Flow 2: Search → Filter → Navigate
```typescript
test('search and navigate', async ({ page }) => {
  // Search
  await searchGlobal(page, 'authentication')

  // Filter
  await applyFilter(page, /type/i, /requirement/i)

  // Navigate to result
  const result = page.getByRole('link', { name: /user authentication/i })
  await result.click()
  await expect(page).toHaveURL(/\/items\//)
})
```

### Flow 3: Offline Mode
```typescript
test('offline workflow', async ({ page, context }) => {
  // Load data while online
  await navigateToItems(page)

  // Go offline
  await context.setOffline(true)
  await page.reload()

  // Verify offline indicator
  const offline = page.getByText(/offline/i)
  await expect(offline).toBeVisible()

  // Access cached data
  await navigateToItems(page)
  const items = page.locator('[data-testid="item-row"]')
  expect(await items.count()).toBeGreaterThan(0)

  // Go back online
  await context.setOffline(false)
})
```

## Configuration

### Playwright Config
- **Base URL**: `http://localhost:5173`
- **Timeout**: 30s per test
- **Retries**: 2 on CI, 0 locally
- **Browser**: Chromium
- **Dev server**: Auto-starts on port 5173

### Environment
- **MSW**: Enabled by default via `VITE_ENABLE_MSW=true`
- **Mock data**: `src/mocks/data.ts`

## Debugging

### View Test in Browser
```bash
bun run test:e2e:headed
```

### Debug Specific Test
```bash
bunx playwright test links.spec.ts --debug
```

### View Trace
```bash
bunx playwright show-trace trace.zip
```

### Screenshots & Videos
- Location: `test-results/`
- Captured on failure
- Videos retained on failure

## Common Selectors

### By Role (Preferred)
```typescript
page.getByRole('button', { name: /create/i })
page.getByRole('link', { name: /projects/i })
page.getByRole('heading', { name: /dashboard/i })
page.getByRole('dialog')
```

### By Label
```typescript
page.getByLabel(/name/i)
page.getByLabel(/type/i)
page.getByLabel(/status/i)
```

### By Text
```typescript
page.getByText(/user authentication/i)
page.getByText(/created successfully/i)
```

### By Test ID
```typescript
page.locator('[data-testid="project-card"]')
page.locator('[data-testid="item-row"]')
page.locator('[data-testid="graph-container"]')
```

## Soft Assertions

Many tests use `.catch()` for optional features:

```typescript
// Will log if element not found, but won't fail test
const optionalBtn = page.getByRole('button', { name: /optional/i })
await expect(optionalBtn).toBeVisible({ timeout: 5000 }).catch(() => {
  console.log('Optional feature not implemented yet')
})
```

This allows tests to serve as documentation for expected features while not blocking on incomplete implementations.

## Best Practices

1. **Use semantic selectors**: Prefer `getByRole`, `getByLabel`, `getByText`
2. **Wait for load states**: `await page.waitForLoadState('networkidle')`
3. **Use soft assertions**: `.catch()` for optional UI elements
4. **Use helper functions**: Import from `./fixtures`
5. **Test isolation**: Each test should be independent
6. **Clear test names**: Describe what is being tested
7. **Add console logs**: Help debug failed tests in CI

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run E2E Tests
  run: bun run test:e2e

- name: Upload Test Results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Coverage Goals

- **Current**: 205 tests covering major user flows
- **Target**: 80%+ coverage
- **Future**: 280-315 tests for 100% coverage

## Related Documentation

- Full documentation: [e2e/README.md](./e2e/README.md)
- Test summary: [E2E_TEST_SUMMARY.md](./E2E_TEST_SUMMARY.md)
- MSW setup: [MSW_SETUP.md](./MSW_SETUP.md)
- Playwright docs: https://playwright.dev/

## Quick Tips

- **Stuck?** Run in UI mode: `bun run test:e2e:ui`
- **Slow tests?** Check for `waitForLoadState('networkidle')`
- **Flaky tests?** Add explicit waits or increase timeouts
- **Need help?** Check `fixtures/pageHelpers.ts` for reusable functions
