# E2E Testing Guide - Best Practices

## Quick Reference

### Finding Elements (In Order of Preference)

1. **By text content** (most resilient):

```typescript
page.locator('button').filter({ hasText: /save/i }).first();
```

2. **By role** (accessible):

```typescript
page.getByRole('button', { name: /save/i });
page.getByRole('textbox', { name: /title/i });
```

3. **By placeholder** (for inputs):

```typescript
page.locator('input[placeholder*="search" i]');
```

4. **By ID** (for specific form fields):

```typescript
page.locator('input[id="project-name"]');
```

5. **By href** (for navigation):

```typescript
page.locator('a[href*="/projects/"]');
```

6. **data-testid** (last resort - requires implementation):

```typescript
page.locator('[data-testid="item-card"]');
```

### Resilient Click Pattern

```typescript
// Good - handles missing elements gracefully
const button = page
  .locator('button')
  .filter({ hasText: /delete/i })
  .first();
if (await button.isVisible({ timeout: 2000 }).catch(() => false)) {
  await button.click();
}

// Bad - fails if button doesn't exist
await page.click('button:has-text("Delete")');
```

### Waiting Strategies

```typescript
// Page load - most reliable
await page.waitForLoadState('networkidle');

// URL change - for navigation
await page.waitForURL(/\/items\/.*/);

// Specific element
await page.locator('input').first().isVisible({ timeout: 2000 });

// Custom timeout
await page.waitForTimeout(500); // Last resort
```

### Form Interactions

```typescript
// Text input
await page.fill('input[id="name"]', 'value');

// Textarea
await page.fill('textarea[id="description"]', 'value');

// Select dropdown
await page.selectOption('select[name="type"]', 'option-value');

// Checkbox (get element then evaluate)
const checkbox = page.locator('input[type="checkbox"]').first();
await checkbox.click();

// Radio button
const radio = page.locator('input[type="radio"]').filter({ hasText: /option/i });
await radio.click();
```

### Navigation Patterns

```typescript
// Direct navigation
await page.goto('/projects');

// With search params
await page.goto('/projects?action=create');

// With hash
await page.goto('/settings#advanced');

// Wait for navigation
await page.click('a[href="/items"]');
await page.waitForURL('/items');
```

### Common Workflows

#### Creating a Resource

```typescript
// 1. Navigate to creation page or trigger dialog
await page.goto('/projects?action=create');
await page.waitForLoadState('networkidle');

// 2. Fill form
const nameInput = page.locator('input[id="project-name"]');
if (await nameInput.isVisible({ timeout: 2000 }).catch(() => false)) {
  await nameInput.fill('My Project');

  // 3. Submit
  const submitBtn = page.locator('button').filter({ hasText: /create|save/i });
  await submitBtn.click();

  // 4. Verify navigation or success
  await page.waitForURL(/\/projects\/[^?]+/);
}
```

#### Clicking List Items

```typescript
// Find by text in table
await page
  .locator('tbody tr')
  .filter({ hasText: /Target Item/i })
  .first()
  .click();

// Find by link
await page.locator('a[href*="/items/"]').first().click();
await page.waitForURL(/\/items\/.*/);

// Generic card/div
const card = page
  .locator('div')
  .filter({ hasText: /Target Item/i })
  .first();
await card.click();
```

#### Handling Dialogs

```typescript
// Click to open dialog
await page
  .locator('button')
  .filter({ hasText: /new|create/i })
  .click();
await page.waitForTimeout(300); // Allow animation

// Check if visible (optional feature)
const dialog = page.locator('dialog, [role="dialog"]');
if (await dialog.isVisible({ timeout: 1000 }).catch(() => false)) {
  // Dialog exists - interact with it
  await page.locator('input').first().fill('value');
}
```

### Debugging

```typescript
// Take screenshot
await page.screenshot({ path: 'debug.png' });

// Print current URL
console.log('Current URL:', page.url());

// Get element text
const text = await page.locator('button').first().textContent();
console.log('Button text:', text);

// Check if element exists
const exists = await page
  .locator('[data-testid="item"]')
  .isVisible()
  .catch(() => false);
console.log('Element visible:', exists);

// Get all elements matching selector
const count = await page.locator('tbody tr').count();
console.log('Number of rows:', count);
```

### Common Issues & Fixes

| Issue                          | Cause                   | Fix                                                  |
| ------------------------------ | ----------------------- | ---------------------------------------------------- |
| "Timeout waiting for selector" | Element doesn't exist   | Use `.catch(() => false)` to handle missing elements |
| Click doesn't work             | Element not in viewport | Add `.waitForLoadState()` before interaction         |
| Form submit fails              | Validation error        | Check form validation before submission              |
| Navigation doesn't update      | URL pattern mismatch    | Use regex patterns: `/\/items\/.*/`                  |
| Search results empty           | API not responding      | Check mock setup in `global-setup.ts`                |
| Dialog not appearing           | Animation delay         | Add `waitForTimeout(300)`                            |

## Architecture

### Test Structure

```
e2e/
├── integration-workflows.spec.ts  # Multi-step workflows
├── navigation.spec.ts              # Single-page navigation
├── items.spec.ts                   # Item CRUD operations
├── projects.spec.ts                # Project management
├── global-setup.ts                 # Shared test fixtures
└── fixtures/
    ├── api-mocks.ts                # MSW mock handlers
    ├── test-helpers.ts             # Utility functions
    └── testData.ts                 # Mock data
```

### Playwright Configuration

- **baseURL**: `http://localhost:5173`
- **timeout**: 30,000ms per test
- **workers**: Parallel (5 by default)
- **retries**: 2 on CI, 0 locally
- **screenshot**: On failure
- **video**: On failure

### Running Tests

```bash
# All E2E tests
bun run playwright test

# Specific test file
bun run playwright test e2e/integration-workflows.spec.ts

# Specific test
bun run playwright test -g "should create project"

# Headed mode (see browser)
bun run playwright test --headed

# Debug mode
bun run playwright test --debug

# Generate report
bun run playwright test --reporter=html
open playwright-report/index.html
```

## Recommendations

1. **Prefer text-based selectors** over data-testid
2. **Always add timeout handling** for resilience
3. **Use graceful fallbacks** for optional features
4. **Test navigation workflows** not just UI elements
5. **Keep tests independent** - no shared state
6. **Mock external APIs** consistently
7. **Document complex selectors** with comments
8. **Review test failures** for flakiness patterns

## Resources

- [Playwright Selectors](https://playwright.dev/docs/selectors)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)
- [CI/CD Integration](https://playwright.dev/docs/ci)
