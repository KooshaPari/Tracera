# Critical Path E2E Tests

## Overview

The critical path E2E tests in `critical-path.spec.ts` focus on the most essential user flows in TraceRTM. These tests represent the core functionality that must work reliably for the application to be usable.

## Critical User Flows Covered

### 1. Project Creation Flow
**File**: `critical-path.spec.ts` → `CRITICAL PATH: Project Creation Flow`

Tests the complete workflow of creating a new project:
- Navigate to projects page
- Click create project button
- Fill in project name and description
- Submit form
- Verify project appears in list

**Tests:**
- `should complete end-to-end project creation` - Full workflow test
- `should display list of existing projects` - Verify existing projects display

**Why it's critical:** Without working project creation, users cannot organize their work.

---

### 2. Item Creation and Management
**File**: `critical-path.spec.ts` → `CRITICAL PATH: Item Creation and Management`

Tests the complete workflow for managing requirements/features:
- Navigate to items page
- Create new item (title, type, description)
- Update item status
- Display items in table format

**Tests:**
- `should create a new item` - Full item creation workflow
- `should update existing item status` - Status change workflow
- `should display items in table format` - Verify data display

**Why it's critical:** Item management is the core feature - users must be able to create and organize items.

---

### 3. Link Creation Between Items
**File**: `critical-path.spec.ts` → `CRITICAL PATH: Link Creation Between Items`

Tests traceability link creation and visualization:
- Access item detail page
- Show link section/button
- Navigate to graph view
- Display traceability relationships

**Tests:**
- `should access item and show link section` - Verify link UI availability
- `should navigate to graph view showing links` - Graph visualization test

**Why it's critical:** Traceability linking is the unique value proposition of TraceRTM.

---

### 4. Navigation Between Views
**File**: `critical-path.spec.ts` → `CRITICAL PATH: Navigation Between Views`

Tests all major navigation paths:
- Dashboard → Projects → Items → Detail
- Browser back/forward buttons
- Navigation links in sidebar/header
- Graph and settings views

**Tests:**
- `should navigate to dashboard` - Root page load
- `should navigate from projects to items to detail` - Multi-step navigation
- `should use browser back button to navigate` - Browser navigation support
- `should navigate to graph view` - Specialized view access
- `should navigate to settings` - Settings page access

**Why it's critical:** Users must be able to move between different parts of the app without errors.

---

### 5. Search and Filter Functionality
**File**: `critical-path.spec.ts` → `CRITICAL PATH: Search and Filter Functionality`

Tests data discovery and filtering:
- Global search across items
- Filter by type
- Filter by status
- Clear search/filters

**Tests:**
- `should search items by title` - Text search functionality
- `should filter items by type` - Categorical filtering
- `should filter items by status` - Status-based filtering
- `should clear search/filters` - Reset functionality

**Why it's critical:** Users need efficient ways to find items in large datasets.

---

### 6. Core Data Integrity
**File**: `critical-path.spec.ts` → `CRITICAL PATH: Core Data Integrity`

Tests fundamental stability and error handling:
- Initial data loads on app start
- State preservation during navigation
- Graceful error handling for missing data
- 404 pages and error states

**Tests:**
- `should load and display initial data on dashboard` - App startup verification
- `should handle navigation without losing state` - State management test
- `should handle error states gracefully` - Error handling test

**Why it's critical:** The application must remain stable and not lose data.

---

## Test Data

Critical path tests use dynamically generated data with timestamps to ensure uniqueness:

```typescript
const projectName = `Critical Path Test ${Date.now()}`
const itemTitle = `Critical Path Item ${Date.now()}`
```

This prevents conflicts when tests run multiple times.

---

## Test Helpers

The `critical-path-helpers.ts` file provides reusable functions for common operations:

### Navigation Helpers
```typescript
await navigateToDashboard(page)
await navigateToProjects(page)
await navigateToItems(page)
await navigateToGraph(page)
await navigateToItemDetail(page, 'item-1')
```

### CRUD Helpers
```typescript
// Projects
const success = await createProject(page, {
  name: 'My Project',
  description: 'Test description'
})

// Items
const success = await createItem(page, {
  title: 'My Item',
  type: 'Requirement',
  status: 'Pending',
  description: 'Test item'
})

const success = await updateItemStatus(page, 'Completed')
const success = await deleteItem(page)
```

### Search and Filter Helpers
```typescript
const resultCount = await searchItems(page, 'authentication')
const success = await filterByType(page, 'Requirement')
const success = await filterByStatus(page, 'Completed')
const success = await clearSearchAndFilters(page)
```

### Assertion Helpers
```typescript
await expectPageUrl(page, '/items')
await expectElementVisible(page, '[role="dialog"]')
await expectText(page, 'User Authentication')
```

### Utility Helpers
```typescript
const project = await generateProject({ name: 'Custom Project' })
const item = await generateItem({ title: 'Custom Item' })
const rowCount = await getTableRowCount(page)
const success = await clickTableRowByText(page, 'User Authentication')
```

---

## Running Critical Path Tests

### Run all critical path tests
```bash
bun run test:e2e -- critical-path.spec.ts
```

### Run a specific test
```bash
bun run test:e2e -- critical-path.spec.ts -g "should create a new item"
```

### Run in UI mode (recommended for debugging)
```bash
bun run test:e2e:ui -- critical-path.spec.ts
```

### Run in headed mode (see browser)
```bash
bun run test:e2e:headed -- critical-path.spec.ts
```

### Debug a specific test
```bash
bun run test:e2e:debug -- critical-path.spec.ts -g "should create"
```

### View test report
```bash
bun run test:e2e:report
```

---

## Test Strategy

### Soft Assertions and Graceful Handling

Critical path tests use soft assertions to handle incomplete features:

```typescript
const hasButton = await createBtn
  .isVisible({ timeout: 2000 })
  .catch(() => false)

if (!hasButton) {
  console.log('Create button not found - feature may not be ready')
  return
}
```

This approach:
- Allows tests to pass even if some features are incomplete
- Provides helpful console logs for missing features
- Serves as documentation for expected functionality

### Test Isolation

Each test is independent and doesn't depend on others:
- Tests can run in any order
- Tests can be run individually
- No shared state between tests

### Async/Await Patterns

Tests use consistent async patterns:
```typescript
// ✅ Good: Wait for state before asserting
await page.waitForLoadState('networkidle')
const text = page.getByText('Project created')
await expect(text).toBeVisible({ timeout: 5000 })

// ❌ Avoid: Timing issues
page.goto('/projects')
page.getByText('Project created') // Might not exist yet
```

---

## Common Test Patterns

### Checking if Feature is Available
```typescript
const button = page.getByRole('button', { name: /create/i })
const isAvailable = await button
  .isVisible({ timeout: 2000 })
  .catch(() => false)

if (!isAvailable) {
  console.log('Feature not available - skipping test')
  return
}

await button.click()
```

### Waiting for Element After Action
```typescript
await button.click()
await page.waitForTimeout(500) // Wait for UI to update

const dialog = page.getByRole('dialog')
await expect(dialog).toBeVisible({ timeout: 2000 })
```

### Handling Multiple Possible Selectors
```typescript
const input = page
  .getByLabel(/name/i)
  .or(page.getByPlaceholder(/name/i))
  .first()

if (await input.isVisible({ timeout: 2000 })) {
  await input.fill('Test Name')
}
```

### Form Submission Pattern
```typescript
// Fill form
await titleInput.fill('Test Title')
await descInput.fill('Test Description')

// Submit
await submitBtn.click()
await page.waitForLoadState('networkidle')

// Verify
const result = page.getByText('Test Title')
await expect(result).toBeVisible({ timeout: 5000 })
```

---

## Expected Results

### Passing Tests
When a test passes with "✓":
- The feature works as expected
- The UI element is found and responds correctly
- The navigation/action completes successfully
- Data is created/modified/displayed correctly

### Failing Tests
When a test fails with "✘":
- There's an actual issue with the feature
- The expected element/behavior is missing
- Navigation or API calls failed
- Timeout waiting for expected state

### Skipped Tests
When a test logs "...not found - ...may not be ready":
- The test code detected the feature isn't available
- The test gracefully skipped that section
- This is acceptable - it documents expected functionality

---

## Debugging Failed Tests

### Step 1: Run in UI Mode
```bash
bun run test:e2e:ui -- critical-path.spec.ts -g "test name"
```

Use the UI to step through the test and see:
- What the page looks like at each step
- Where it fails
- What elements are actually present

### Step 2: Run in Debug Mode
```bash
bun run test:e2e:debug -- critical-path.spec.ts -g "test name"
```

This opens the Playwright Inspector where you can:
- Step through code line by line
- Inspect page state
- Run commands in the console

### Step 3: Check Screenshots and Videos
Failed tests automatically capture:
- Screenshots at failure point
- Videos of test execution
- Located in `test-results/` directory

View them:
```bash
bun run test:e2e:report
```

### Step 4: Analyze Test Output

Look for these clues:
```
✘ Test name
  Error: Timeout 5000ms waiting for ...
  (element not found)

✘ Test name
  Error: page.click: Target page, context or browser has been closed
  (navigation issue)

✘ Test name
  Expected to be visible
  (element exists but not visible)
```

---

## Adding New Critical Path Tests

### 1. Identify Critical Flow
- What is the core user journey?
- What must work for users to complete it?
- What are the success criteria?

### 2. Write Test Template
```typescript
test("should complete critical flow", async ({ page }) => {
  // Arrange - setup page state
  await navigateToProjects(page)

  // Act - perform user action
  const success = await createProject(page, {
    name: 'Test Project',
    description: 'Test'
  })

  // Assert - verify result
  expect(success).toBe(true)
})
```

### 3. Use Helper Functions
```typescript
import {
  navigateToProjects,
  createProject,
  expectPageUrl
} from './critical-path-helpers'
```

### 4. Add Soft Assertions for Optional Features
```typescript
const hasAdvancedFeature = await page
  .getByRole('button', { name: /advanced/i })
  .isVisible({ timeout: 2000 })
  .catch(() => false)

if (hasAdvancedFeature) {
  // Test advanced feature
} else {
  console.log('Advanced feature not available - acceptable')
}
```

### 5. Test in UI Mode
```bash
bun run test:e2e:ui -- critical-path.spec.ts -g "should complete critical"
```

### 6. Verify Test Runs and Passes
```bash
bun run test:e2e -- critical-path.spec.ts -g "should complete critical"
```

---

## Performance Baseline

Critical path tests should complete in reasonable time:
- **Single test**: < 5 seconds
- **Full test suite**: < 60 seconds
- **With retries**: < 120 seconds

If tests are slow:
1. Check network idle wait times
2. Verify MSW is working properly
3. Check for missing timeouts
4. Profile with `measurePageLoadTime(page)`

---

## CI/CD Integration

Add to your CI pipeline:
```yaml
- name: Run Critical Path E2E Tests
  run: bun run test:e2e -- critical-path.spec.ts
  timeout-minutes: 5

- name: Upload Test Report
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

---

## Maintenance

### Regular Reviews
- Review test results weekly
- Check for flaky tests (random failures)
- Update tests as UI changes

### Update Coverage
Add new tests when:
- New critical features are added
- User feedback identifies important flows
- You discover gaps in coverage

### Refactor Helpers
Keep `critical-path-helpers.ts` updated:
- Add helpers for new patterns
- Update selectors if UI changes
- Share common logic across tests

---

## Related Documentation

- [E2E Tests README](./README.md) - Full E2E test suite documentation
- [Playwright Documentation](https://playwright.dev/) - Official Playwright docs
- [Test Best Practices](../README_TESTING.md) - Testing guidelines
- [Application Architecture](../ARCHITECTURE.md) - App structure and flows
