# E2E Tests - Quick Start Guide

## Test Suite Overview

**398 tests** | **7,647 lines** | **16 files** | **499 helper lines**

## Running Tests

### Most Common Commands

```bash
# All tests (headless)
bun run test:e2e

# Interactive mode (RECOMMENDED for development)
bun run test:e2e:ui

# Watch browser (headed mode)
bun run test:e2e:headed

# Debug mode (step through tests)
bun run test:e2e:debug

# View HTML report
bun run test:e2e:report
```

### Run Specific Test Files

```bash
# Authentication tests
npx playwright test auth-advanced.spec.ts

# Accessibility tests
npx playwright test accessibility.spec.ts

# Security tests
npx playwright test security.spec.ts

# Performance tests
npx playwright test performance.spec.ts

# Integration workflows
npx playwright test integration-workflows.spec.ts

# Edge cases
npx playwright test edge-cases.spec.ts
```

### Run Specific Test

```bash
# Run single test by name
npx playwright test -g "should login successfully"

# Run tests matching pattern
npx playwright test -g "keyboard navigation"
```

## Test Categories

| Category                 | File                          | Tests | Lines |
| ------------------------ | ----------------------------- | ----- | ----- |
| 🔐 Authentication        | auth-advanced.spec.ts         | 35    | 635   |
| 🔄 Integration Workflows | integration-workflows.spec.ts | 23    | 697   |
| ♿ Accessibility         | accessibility.spec.ts         | 35    | 636   |
| ⚡ Performance           | performance.spec.ts           | 28    | 636   |
| 🔒 Security              | security.spec.ts              | 35    | 638   |
| 🎯 Edge Cases            | edge-cases.spec.ts            | 37    | 661   |
| 🤖 Agents                | agents.spec.ts                | 24    | 582   |
| 📊 Dashboard             | dashboard.spec.ts             | 26    | 313   |
| 🕸️ Graph                 | graph.spec.ts                 | 30    | 560   |
| 📝 Items                 | items.spec.ts                 | 26    | 369   |
| 🔗 Links                 | links.spec.ts                 | 16    | 407   |
| 🧭 Navigation            | navigation.spec.ts            | 15    | 205   |
| 📁 Projects              | projects.spec.ts              | 17    | 272   |
| 🔍 Search                | search.spec.ts                | 23    | 508   |
| 🔄 Sync                  | sync.spec.ts                  | 23    | 449   |
| 🔑 Basic Auth            | auth.spec.ts                  | 5     | 79    |

## Quick Examples

### Using Test Helpers

```typescript
import { TestHelpers } from './fixtures/test-helpers';

test('create and verify item', async ({ page }) => {
  const helpers = new TestHelpers(page);

  await helpers.login();
  await helpers.navigateToItems();
  await helpers.createItem({
    title: 'Test Item',
    description: 'Description',
    type: 'requirement',
  });
  await helpers.assertItemExists('Test Item');
});
```

### Accessibility Testing

```typescript
import AxeBuilder from '@axe-core/playwright';

test('page has no a11y violations', async ({ page }) => {
  await page.goto('/items');

  const results = await new AxeBuilder({ page }).withTags(['wcag2aa']).analyze();

  expect(results.violations).toEqual([]);
});
```

### Performance Testing

```typescript
test('loads within 3 seconds', async ({ page }) => {
  const start = Date.now();
  await page.goto('/items');
  await page.waitForLoadState('networkidle');
  const loadTime = Date.now() - start;

  expect(loadTime).toBeLessThan(3000);
});
```

## Debugging

### Screenshot on Failure

Screenshots automatically saved to `test-results/`

### Trace Viewer

```bash
npx playwright show-trace test-results/trace.zip
```

### Slow Motion

```typescript
test.use({ launchOptions: { slowMo: 1000 } });
```

### Console Logs

```typescript
page.on('console', (msg) => console.log('PAGE:', msg.text()));
```

## Common Issues

### Tests Timeout

- Increase timeout in playwright.config.ts
- Use `waitForLoadState('networkidle')` after navigation

### Element Not Found

- Check selector accuracy
- Use Playwright Inspector: `npx playwright test --debug`
- Try `.first()` for multiple matches

### Port Already in Use

```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

## Test Helper Methods

### Authentication

- `login(email, password)`
- `logout()`

### Navigation

- `navigateTo(route)`
- `navigateToItems()`
- `navigateToProjects()`
- `navigateToAgents()`

### CRUD Operations

- `createItem(data)`
- `createProject(data)`
- `createAgent(data)`

### Search & Filter

- `search(query)`
- `globalSearch(query)`
- `applyFilter(type, value)`

### Assertions

- `assertItemExists(title)`
- `assertProjectExists(name)`
- `assertErrorMessage(message)`
- `assertSuccessMessage(message)`

### Modals

- `openModal(buttonText)`
- `closeModal()`
- `submitModal()`

### Performance

- `measureLoadTime()`
- `getPerformanceMetrics()`

## CI/CD Integration

```yaml
- name: Install dependencies
  run: bun install

- name: Install Playwright
  run: npx playwright install --with-deps

- name: Run E2E tests
  run: bun run test:e2e

- name: Upload report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## More Information

- Full documentation: [README.md](./README.md)
- Test helpers: [fixtures/test-helpers.ts](./fixtures/test-helpers.ts)
- Playwright docs: https://playwright.dev/
