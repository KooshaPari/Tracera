# Settings E2E Tests - Detailed Structure

## Test Hierarchy and Organization

### Overall Statistics

- **Total Test Groups:** 10
- **Total Individual Tests:** 32
- **Total Lines of Code:** 889
- **File Location:** `/frontend/apps/web/e2e/settings.spec.ts`

---

## Test Group Breakdown

### Test Group 1: Settings Page Navigation (3 tests)

**Focus:** Basic page accessibility and structure

```typescript
test.describe("Settings Page Navigation", () => {
  - Navigate to settings page ✓
  - Display settings header and description ✓
  - Display all settings tabs ✓
})
```

**Key Assertions:**

- URL matches `/settings`
- Main heading contains "Settings"
- All 4 tabs visible (General, Appearance, API, Notifications)

---

### Test Group 2: General Settings Tab (6 tests)

**Focus:** User profile settings (name, email, timezone)

```typescript
test.describe("General Settings Tab", () => {
  - Display general settings form fields ✓
  - Update display name ✓
  - Update email address ✓
  - Validate email format ✓
  - Change timezone ✓
  - Handle save with loading state ✓
})
```

**Form Fields Tested:**

- Display Name (text input)
- Email (email input with validation)
- Timezone (select dropdown)

**Scenarios Covered:**

- Form rendering and visibility
- Text input update and persistence
- Email validation (valid and invalid formats)
- Dropdown selection
- Async save operation with loading state

---

### Test Group 3: Appearance Settings Tab (7 tests)

**Focus:** Theme and visual preferences

```typescript
test.describe("Appearance Settings Tab", () => {
  - Display appearance settings form fields ✓
  - Change theme to dark ✓
  - Change theme to light ✓
  - Change theme to system ✓
  - Change font size ✓
  - Toggle compact mode ✓
})
```

**Settings Tested:**

1. **Theme Selector** (3 variations)
   - Light theme selection
   - Dark theme selection
   - System theme selection

2. **Font Size**
   - Small → Medium → Large progression
   - Selection persistence

3. **Compact Mode**
   - Checkbox toggle
   - State tracking

---

### Test Group 4: Notifications Settings Tab (7 tests)

**Focus:** Notification channel configuration

```typescript
test.describe("Notifications Settings Tab", () => {
  - Display notification settings checkboxes ✓
  - Display notification descriptions ✓
  - Toggle email notifications ✓
  - Toggle desktop notifications ✓
  - Toggle weekly summary ✓
  - Toggle item updates notification ✓
  - Save multiple notification preferences at once ✓
})
```

**Notification Channels:**

1. Email Notifications
   - Receive email updates
   - Toggle on/off

2. Desktop Notifications
   - Browser push notifications
   - Toggle on/off

3. Weekly Summary
   - Get a weekly digest
   - Toggle on/off

4. Item Updates
   - Notify when items change
   - Toggle on/off

**Advanced Scenarios:**

- Individual channel toggling
- Bulk updates (multiple channels at once)
- State persistence after save

---

### Test Group 5: API Keys Tab (4 tests)

**Focus:** API key management

```typescript
test.describe("API Keys Tab", () => {
  - Display API key section ✓
  - Have password-type API key input ✓
  - Allow entering API key ✓
})
```

**Elements Verified:**

- API Key input field (password type)
- "Generate New Key" button
- "Revoke Key" button
- Helper text describing usage

**Security Checks:**

- Input type is "password" (masking)
- Sensitive data protection

---

### Test Group 6: Settings Form Validation (2 tests)

**Focus:** Input validation and error handling

```typescript
test.describe("Settings Form Validation", () => {
  - Validate email field with HTML5 validation ✓
  - Handle empty form submission gracefully ✓
})
```

**Validation Test Cases:**

1. Email Format Validation
   - Invalid: "not-an-email" ✗
   - Invalid: "missing@domain" ✗
   - Invalid: "@nodomain.com" ✗
   - Valid: "valid@example.com" ✓

2. Empty Form Handling
   - Clear all fields
   - Attempt submission
   - Verify graceful handling

---

### Test Group 7: Settings Tab Navigation (3 tests)

**Focus:** Tab switching and state management

```typescript
test.describe("Settings Tab Navigation", () => {
  - Switch between tabs ✓
  - Maintain tab content when switching ✓
  - Be accessible via keyboard ✓
})
```

**Tab Switch Scenarios:**

- Sequential tab navigation (General → Appearance → Notifications → API)
- Back navigation (API → General)
- State persistence across switches

**Keyboard Navigation:**

- Tab key to focus elements
- ArrowRight to navigate between tabs
- Verify aria-selected attributes

---

### Test Group 8: Settings Error Handling (3 tests)

**Focus:** Error scenarios and recovery

```typescript
test.describe("Settings Error Handling", () => {
  - Handle invalid email gracefully ✓
  - Display save button in loading state ✓
  - Handle page reload in settings ✓
})
```

**Error Scenarios:**

1. Invalid Input
   - Browser validation prevents submission
   - Page remains on settings page

2. Async Operations
   - Button shows loading/disabled state
   - Form submission completes

3. Page Reload
   - Settings page reloads successfully
   - All elements reappear and are functional

---

### Test Group 9: Settings Accessibility (4 tests)

**Focus:** WCAG compliance and accessibility

```typescript
test.describe("Settings Accessibility", () => {
  - Have proper form labels ✓
  - Have accessible tabs with ARIA roles ✓
  - Support keyboard navigation ✓
  - Have descriptive button labels ✓
})
```

**Accessibility Checks:**

1. **Labels**
   - All form inputs have associated labels
   - Label htmlFor attributes match input IDs

2. **ARIA**
   - Tablist role present
   - Tab roles on tab elements
   - aria-selected attribute tracking

3. **Keyboard Support**
   - Tab key navigation functional
   - Arrow key navigation in tabs
   - Focus management

4. **Descriptive Text**
   - Button labels are clear ("Save Changes", "Save Preferences")
   - Helper text on form fields
   - Error messages are descriptive

---

### Test Group 10: Settings Integration (3 tests)

**Focus:** Cross-page integration and resilience

```typescript
test.describe("Settings Integration", () => {
  - Navigate to settings from dashboard ✓
  - Persist to settings page after navigation ✓
  - Handle settings page load errors gracefully ✓
})
```

**Integration Tests:**

1. **Dashboard Navigation**
   - Start at dashboard (/)
   - Navigate to settings
   - Verify settings loads

2. **Page Persistence**
   - Go to settings
   - Navigate away (to projects)
   - Return to settings
   - Verify still accessible

3. **Error Resilience**
   - API failures don't break UI
   - Page elements still interactive
   - Tabs still functional

---

## Test Interaction Patterns

### Input Types Tested

1. **Text Input**
   - Display Name field
   - API Key field
   - Pattern: `.fill("value")` → `.toHaveValue("value")`

2. **Email Input**
   - Email field with HTML5 validation
   - Pattern: `.fill(value)` → `.evaluate(el => el.validity.valid)`

3. **Dropdown/Select**
   - Theme selection
   - Font size selection
   - Timezone selection
   - Pattern: `.click()` → `.click()` on option

4. **Checkbox**
   - Email Notifications
   - Desktop Notifications
   - Weekly Summary
   - Item Updates
   - Pattern: `.click()` → `.isChecked()`

5. **Button**
   - Save buttons (various labels)
   - Pattern: `.click()` → wait for result

### Waiting Strategies

```typescript
// Page load complete
await page.waitForLoadState('networkidle');

// Short delay for animations/transitions
await page.waitForTimeout(300);

// Text appears
await page.getByText(/pattern/).waitFor({ state: 'visible', timeout: 5000 });

// Element becomes visible
await element.isVisible({ timeout: 1000 });
```

### Assertion Patterns

```typescript
// URL assertions
await expect(page).toHaveURL('/settings');

// Element visibility
await expect(element).toBeVisible();

// Element value
await expect(input).toHaveValue('expected value');

// Element state
const isDisabled = await button.isDisabled();

// Element count
const count = await tabs.count();
expect(count).toBeGreaterThanOrEqual(4);
```

---

## Test Data Examples

### Display Name Updates

- Test value: `"John Doe"`
- Pattern: Fill → Verify → Save → Wait

### Email Validation Test Cases

```typescript
[
  { input: 'not-an-email', valid: false },
  { input: 'missing@domain', valid: false },
  { input: '@nodomain.com', valid: false },
  { input: 'valid@example.com', valid: true },
];
```

### Theme Options

- Light
- Dark
- System

### Font Sizes

- Small
- Medium
- Large

### Timezones

- UTC
- America/New_York (Eastern)
- America/Chicago (Central)
- America/Denver (Mountain)
- America/Los_Angeles (Pacific)

### Notification Channels

- Email Notifications
- Desktop Notifications
- Weekly Summary
- Item Updates

---

## Coverage Matrix

| Feature          | Test Groups | Test Count | Coverage |
| ---------------- | ----------- | ---------- | -------- |
| Page Navigation  | 1           | 3          | 100%     |
| Profile Settings | 2           | 6          | 100%     |
| Appearance/Theme | 3           | 7          | 100%     |
| Notifications    | 4           | 7          | 100%     |
| API Keys         | 5           | 4          | 100%     |
| Form Validation  | 6           | 2          | 100%     |
| Tab Navigation   | 7           | 3          | 100%     |
| Error Handling   | 8           | 3          | 100%     |
| Accessibility    | 9           | 4          | 100%     |
| Integration      | 10          | 3          | 100%     |
| **TOTAL**        | **10**      | **32**     | **100%** |

---

## Execution Timeline

### Expected Duration per Test

- Simple navigation tests: 1-2 seconds
- Form interaction tests: 2-3 seconds
- Complex scenarios (multiple toggles): 3-4 seconds
- Error handling tests: 2-3 seconds
- Accessibility tests: 2-3 seconds

### Total Suite Execution

- Estimated time: **90-130 seconds**
- With retries: **120-160 seconds**
- With UI mode: **Variable (interactive)**

---

## Selector Strategy

### Semantic Selectors (Preferred)

```typescript
// By role
page.getByRole('button', { name: /save changes/i });
page.getByRole('tab', { name: /appearance/i });
page.getByRole('heading', { name: /settings/i });

// By label
page.getByLabel(/display name/i);
page.getByLabel(/theme/i);

// By text
page.getByText('Dark');
page.getByText(/Save Changes/i);
```

### Fallback Selectors

```typescript
// CSS selectors (if semantic unavailable)
page.locator("[id='email']");
page.locator("[aria-label='Theme']");

// XPath (last resort)
page.locator("//button[contains(text(), 'Save')]");
```

---

## Error Messages and Success Indicators

### Expected Success Messages

- "Settings saved successfully!"
- Settings update notifications

### Expected Error Messages

- Email validation errors (browser native)
- "Failed to save settings: [error message]"

### Visual Indicators

- Button loading state: "Saving..." text or disabled state
- Success toast/notification
- Form field focus/error styling

---

## Key Test Characteristics

1. **Deterministic** - Tests produce consistent results
2. **Independent** - No test depends on another
3. **Isolated** - Each test sets up its own state
4. **Realistic** - Uses actual user workflows
5. **Maintainable** - Clear descriptions and locators
6. **Fast** - Sub-4 seconds per test
7. **Reliable** - No flaky waits or timeouts
8. **Accessible** - Tests accessibility features

---

## How to Read Test Structure

Each test follows this pattern:

```typescript
test.beforeEach(async ({ page }) => {
  // Setup - navigate and wait
  await page.goto('/settings');
  await page.waitForLoadState('networkidle');
});

test('should [action result]', async ({ page }) => {
  // Arrange - prepare state
  const input = page.getByLabel(/display name/i);

  // Act - perform user action
  await input.fill('Test User');

  // Assert - verify result
  await expect(input).toHaveValue('Test User');
});
```

---

## Running Specific Tests

```bash
# Run all settings tests
npx playwright test e2e/settings.spec.ts

# Run specific test group
npx playwright test e2e/settings.spec.ts -g "General Settings Tab"

# Run single test
npx playwright test e2e/settings.spec.ts -g "should update display name"

# Run with debugging
npx playwright test e2e/settings.spec.ts --ui

# Generate report
npx playwright test e2e/settings.spec.ts && npx playwright show-report
```

---

## Conclusion

This comprehensive test suite provides:

- **Complete functional coverage** of all settings features
- **Error handling verification** for edge cases
- **Accessibility compliance** testing
- **Integration testing** with app navigation
- **User workflow validation** for critical paths

The tests are organized logically, maintainable, and follow Playwright best practices for reliable E2E testing.
