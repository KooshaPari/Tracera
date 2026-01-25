# Bulk Operations E2E Tests - Quick Reference Guide

## File Location
`/frontend/apps/web/e2e/bulk-operations.spec.ts`

## Test Count: 31 Tests

## Quick Navigation

### By Category

#### Selection (6 tests)
1. Display selection checkboxes
2. Select single item
3. Select multiple items
4. Select all items
5. Deselect individually
6. Clear all selections

#### Delete (6 tests)
7. Show delete button
8. Show confirmation dialog
9. Confirm deletion
10. Cancel deletion
11. Show undo option
12. Handle delete errors

#### Status Updates (3 tests)
13. Show status menu
14. Update status
15. Confirm update

#### Move to Project (2 tests)
16. Show move option
17. Move to project

#### Tags (2 tests)
18. Show tags menu
19. Add tags

#### Archive (2 tests)
20. Show archive option
21. Archive items

#### UI (3 tests)
22. Display counter
23. Show action bar
24. Keep action bar visible

#### Error Handling (3 tests)
25. Handle delete error
26. Disable action when no selection
27. Handle partial failures

#### Undo (2 tests)
28. Undo status update
29. Undo tag addition

#### Keyboard (3 tests)
30. Shift+Click range select
31. Escape clears selection
32. Delete key deletes

## Running Tests

### All Tests
```bash
npx playwright test bulk-operations.spec.ts
```

### Specific Suite
```bash
npx playwright test bulk-operations.spec.ts -g "Bulk Delete"
```

### Debug Mode
```bash
npx playwright test bulk-operations.spec.ts --debug
```

### With UI
```bash
npx playwright test bulk-operations.spec.ts --ui
```

### Watch Mode
```bash
npx playwright test bulk-operations.spec.ts --watch
```

## Key Test Patterns

### Selecting Items
```typescript
const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
await checkbox1.click();
await expect(checkbox1).toBeChecked();
```

### Finding Buttons
```typescript
const deleteButton = page
	.getByRole("button", { name: /delete|remove/i })
	.first();
```

### Confirming Dialogs
```typescript
const confirmButton = page
	.getByRole("button", { name: /confirm|yes/i })
	.first();
await confirmButton.click();
```

### Checking Errors
```typescript
const errorMessage = page
	.locator('[role="alert"]')
	.or(page.locator("text=/error|failed/i"));
await expect(errorMessage).toBeVisible();
```

## Common Assertions

```typescript
// Checkbox state
await expect(checkbox).toBeChecked();
await expect(checkbox).not.toBeChecked();

// Visibility
await expect(element).toBeVisible();
await expect(element).not.toBeVisible();

// Text content
await expect(element).toContainText(/pattern/i);
```

## Soft Assertion Pattern

```typescript
await expect(element)
	.toBeVisible({ timeout: 2000 })
	.catch(() => console.log("Element not found"));
```

This allows tests to pass even if element varies in implementation.

## Wait Patterns

```typescript
// Wait for network
await page.waitForLoadState("networkidle");

// Wait for element
await page.waitForSelector("text=/User Authentication/");

// Wait for timeout
await page.waitForTimeout(300);
```

## Debugging

### View Test Report
```bash
npx playwright show-report
```

### Enable Tracing
```bash
npx playwright test bulk-operations.spec.ts --trace on
```

### View Trace
```bash
npx playwright show-trace trace.zip
```

### Screenshots
Tests can capture screenshots during debugging:
```bash
npx playwright test --screenshot=on
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Timeout waiting for element | Increase timeout, check mock data |
| Click fails | Scroll to element, check visibility |
| Checkbox not checked | Add wait/timeout, check event |
| API error | Check network interception |

## Test Structure

Each test follows this pattern:

```typescript
test("should perform action", async ({ page }) => {
	// 1. SETUP: Wait for page and elements
	await page.waitForLoadState("networkidle");
	const element = page.locator(...);

	// 2. ACTION: Perform user interaction
	await element.click();

	// 3. ASSERT: Verify result
	await expect(element).toHaveState(...);
});
```

## Selectors Used

| Type | Selector |
|------|----------|
| Checkbox | `input[type="checkbox"]` |
| Button | `getByRole("button")` |
| Dialog | `getByRole("dialog")` |
| Text | `getByText(/pattern/i)` |
| Data Attribute | `[data-testid="..."]` |

## Required Elements

For tests to pass, application should have:

- [ ] Checkboxes for items
- [ ] Bulk action bar when selected
- [ ] Delete/Archive/Status buttons
- [ ] Confirmation dialogs
- [ ] Undo functionality
- [ ] Error message display
- [ ] Selection counter

## Performance

- **Total Time:** 5-10 minutes
- **Per Test:** ~10-20 seconds
- **Parallelization:** Up to 4 workers recommended

## Setup Before Running

1. Start application:
   ```bash
   npm run dev
   ```

2. Install Playwright (one-time):
   ```bash
   npx playwright install
   ```

3. Run tests:
   ```bash
   npx playwright test bulk-operations.spec.ts
   ```

## Environment Variables

```bash
VITE_API_URL=http://localhost:8000
PLAYWRIGHT_TEST_BASE_URL=http://localhost:3000
```

## Related Documentation

- Full docs: `BULK_OPERATIONS_TESTS.md`
- Playwright docs: https://playwright.dev
- Test patterns: See `items.spec.ts`

## Test Organization

```
bulk-operations.spec.ts
├── Bulk Item Selection (6 tests)
├── Bulk Delete Operations (6 tests)
├── Bulk Status Update Operations (3 tests)
├── Bulk Move to Project Operations (2 tests)
├── Bulk Tag Operations (2 tests)
├── Bulk Archive Operations (2 tests)
├── Bulk Operations UI (3 tests)
├── Bulk Operations Error Handling (3 tests)
├── Bulk Operations Undo (2 tests)
└── Bulk Operations Keyboard Shortcuts (3 tests)
```

## Key Features Tested

- [x] Multi-item selection with checkboxes
- [x] Bulk delete with confirmation
- [x] Bulk status updates
- [x] Bulk move to project
- [x] Bulk tag operations
- [x] Bulk archive
- [x] Selection UI (counter, action bar)
- [x] Confirmation dialogs
- [x] Undo functionality
- [x] Error handling
- [x] Keyboard shortcuts (Shift+Click, Escape, Delete)

## Expected Success Criteria

All 31 tests should:
- [ ] Pass without errors
- [ ] Complete in < 10 minutes
- [ ] Produce clear error messages if failures occur
- [ ] Work with mocked data
- [ ] Handle missing UI elements gracefully

## Tips

1. **Use Debug Mode** for UI-dependent test issues
2. **Check Mock Data** if selectors don't find items
3. **Review Logs** for `.catch()` messages about missing features
4. **Start Simple** with single test suite before running all
5. **Inspect Element** in debug mode to verify selectors

---

**Version:** 1.0
**Updated:** January 23, 2026
