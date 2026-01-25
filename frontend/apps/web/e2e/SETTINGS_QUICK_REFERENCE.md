# Settings E2E Tests - Quick Reference

## File Location
```
/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/e2e/settings.spec.ts
```

## Test Count
- **Total:** 32+ tests
- **Groups:** 10 test suites
- **Lines:** 889

## Quick Start

```bash
# Run all settings tests
npx playwright test e2e/settings.spec.ts

# Run with UI (recommended for first run)
npx playwright test e2e/settings.spec.ts --ui

# Run in headed mode (see browser)
npx playwright test e2e/settings.spec.ts --headed

# Run specific test group
npx playwright test e2e/settings.spec.ts -g "General Settings Tab"

# Generate HTML report
npx playwright test e2e/settings.spec.ts && npx playwright show-report
```

## Test Groups

| # | Name | Tests | What It Tests |
|---|------|-------|---|
| 1 | Settings Page Navigation | 3 | Basic page access, headers, tabs |
| 2 | General Settings Tab | 6 | Name, email, timezone updates |
| 3 | Appearance Settings Tab | 7 | Theme, font size, compact mode |
| 4 | Notifications Settings Tab | 7 | Email, desktop, summary, updates |
| 5 | API Keys Tab | 4 | API key input, generate, revoke buttons |
| 6 | Settings Form Validation | 2 | Email validation, empty forms |
| 7 | Settings Tab Navigation | 3 | Tab switching, state persistence |
| 8 | Settings Error Handling | 3 | Invalid input, loading, reload |
| 9 | Settings Accessibility | 4 | Labels, ARIA, keyboard nav |
| 10 | Settings Integration | 3 | Cross-page nav, resilience |

## Coverage Checklist

### General Settings
- [x] Display Name input and save
- [x] Email input with validation
- [x] Timezone dropdown
- [x] Save loading state

### Appearance Settings
- [x] Theme: Light, Dark, System
- [x] Font Size: Small, Medium, Large
- [x] Compact Mode toggle

### Notifications
- [x] Email Notifications toggle
- [x] Desktop Notifications toggle
- [x] Weekly Summary toggle
- [x] Item Updates toggle
- [x] Bulk save multiple at once

### API Keys
- [x] API Key input (password type)
- [x] Generate Key button
- [x] Revoke Key button

### Form & Validation
- [x] Valid email acceptance
- [x] Invalid email rejection
- [x] Empty form handling

### User Experience
- [x] Tab navigation
- [x] Tab content persistence
- [x] Loading states
- [x] Error recovery

### Accessibility
- [x] Form labels
- [x] ARIA roles and attributes
- [x] Keyboard navigation (Tab, Arrow keys)
- [x] Screen reader support

### Integration
- [x] Navigation from dashboard
- [x] Return to settings
- [x] API failure resilience

## Key Test Patterns

### Opening a Tab
```typescript
const tab = page.getByRole("tab", { name: /appearance/i });
await tab.click();
await page.waitForTimeout(300);
```

### Filling a Form Input
```typescript
const input = page.getByLabel(/display name/i);
await input.fill("John Doe");
await expect(input).toHaveValue("John Doe");
```

### Toggling a Checkbox
```typescript
const checkbox = page.getByLabel(/email notifications/i);
const wasChecked = await checkbox.isChecked();
await checkbox.click();
expect(await checkbox.isChecked()).toBe(!wasChecked);
```

### Selecting from Dropdown
```typescript
const select = page.getByLabel(/theme/i);
await select.click();
await page.getByText("Dark").click();
```

### Saving Settings
```typescript
const saveBtn = page.getByRole("button", { name: /save changes/i });
await saveBtn.click();
await page.waitForTimeout(500); // Wait for save to complete
```

## Expected Test Results

```
General Settings Tab
✓ should display general settings form fields (2s)
✓ should update display name (2s)
✓ should update email address (2s)
✓ should validate email format (2s)
✓ should change timezone (2s)
✓ should handle save with loading state (2s)

Appearance Settings Tab
✓ should display appearance settings form fields (2s)
✓ should change theme to dark (2s)
✓ should change theme to light (2s)
✓ should change theme to system (2s)
✓ should change font size (2s)
✓ should toggle compact mode (2s)

... (and 20+ more tests)

==== 32+ tests passed (90-130s total) ====
```

## Debugging

### View Tests with UI
```bash
npx playwright test e2e/settings.spec.ts --ui
```
- Shows test steps visually
- Can pause and inspect elements
- Replay failed tests

### Run in Headed Mode
```bash
npx playwright test e2e/settings.spec.ts --headed
```
- See browser while tests run
- Helpful for understanding failures
- Can interact with page

### Take Screenshot
```typescript
await page.screenshot({ path: 'debug.png', fullPage: true });
```

### Log Network Requests
```typescript
page.on('response', response => console.log(response.url()));
```

## Common Issues & Solutions

### Test Timeout
**Problem:** Test hangs waiting for element
**Solution:** Increase timeout or check selector is correct
```typescript
await element.waitFor({ state: "visible", timeout: 10000 });
```

### Element Not Found
**Problem:** Selector doesn't match any element
**Solution:** Use `--ui` mode to inspect actual selectors
```bash
npx playwright test e2e/settings.spec.ts --ui
```

### Flaky Test (Passes/Fails Randomly)
**Problem:** Test depends on timing
**Solution:** Use proper wait strategies
```typescript
// Bad: Fixed delay
await page.waitForTimeout(1000);

// Good: Wait for element
await element.waitFor({ state: "visible" });
```

## CI/CD Integration

### Add to GitHub Actions
```yaml
- name: Run Settings E2E Tests
  run: npx playwright test e2e/settings.spec.ts
```

### Upload Test Report
```yaml
- name: Upload Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30
```

## Documentation Files

| File | Purpose |
|------|---------|
| settings.spec.ts | Test implementation (889 lines) |
| SETTINGS_TESTS_README.md | Detailed test documentation |
| SETTINGS_TEST_STRUCTURE.md | Technical architecture |
| IMPLEMENTATION_SUMMARY.md | Executive summary |
| SETTINGS_QUICK_REFERENCE.md | This file |

## Performance Metrics

- **Total Tests:** 32+
- **Average Duration:** 2-4 seconds per test
- **Total Suite Time:** 90-130 seconds
- **Estimated CI/CD Time:** 2-3 minutes (with overhead)

## Maintenance Tasks

### Monthly
- Review test results in CI/CD
- Update selectors if UI changes
- Check for deprecated Playwright APIs

### When Settings Page Changes
1. Run tests to identify failures
2. Update affected selectors
3. Add tests for new features
4. Verify all tests pass
5. Update documentation

### Before Release
1. Run full test suite
2. Verify all 32+ tests pass
3. Check execution time
4. Review coverage
5. Get team approval

## Support

### Getting Help
- Check SETTINGS_TESTS_README.md for detailed info
- Review test comments in settings.spec.ts
- Use `--ui` mode for visual debugging
- Check Playwright docs: https://playwright.dev

### Reporting Issues
Include:
- Test name that failed
- Error message
- Browser/OS info
- Steps to reproduce

## Related Resources

- Settings Page: `/src/views/SettingsView.tsx`
- Settings API: `/src/api/settings.ts`
- Settings Route: `/src/routes/settings.index.tsx`
- Component Library: `@tracertm/ui`

## Last Updated
January 23, 2025

## Status
✓ Ready for Production

---

**Next Step:** Run `npx playwright test e2e/settings.spec.ts --ui` to start testing!
