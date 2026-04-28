# Test Execution Guide for Comprehensive Test Suite

## Quick Start

```bash
# Navigate to web app directory
cd frontend/apps/web

# Install dependencies
bun install

# Run all tests
bun run test

# View test results
# All tests should pass with 100% success rate
```

---

## Test Suites Overview

### 1. Accessibility Tests

**Location:** `src/__tests__/accessibility/`
**Purpose:** Verify WCAG 2.1 AA compliance, keyboard navigation, screen reader support

**Files:**

- `table-keyboard-navigation.test.tsx` (28 tests)
- `form-validation-accessibility.test.tsx` (17 tests)

**Run:**

```bash
bun run test:a11y
# Or
bun run test src/__tests__/accessibility
```

**Coverage Areas:**

- Keyboard navigation (arrow keys, Home/End)
- ARIA attributes (role, aria-invalid, aria-describedby)
- Focus management
- Touch target sizing
- Form validation errors
- Screen reader announcements

---

### 2. UX Tests

**Location:** `src/__tests__/ux/`
**Purpose:** Test user feedback mechanisms and error handling

**Files:**

- `dialogs-and-feedback.test.tsx` (50 tests)

**Run:**

```bash
bun run test src/__tests__/ux
```

**Coverage Areas:**

- Confirmation dialogs
- Success/error toasts
- Error boundaries
- Empty states
- Loading states
- Destructive action warnings

---

### 3. Feature Tests

**Location:** `src/__tests__/features/`
**Purpose:** Test newly implemented features for phases 8-16

**Files:**

- `link-sharing-and-specs.test.tsx` (55 tests)

**Run:**

```bash
bun run test src/__tests__/features
```

**Coverage Areas:**

- Link sharing (copy, open in new tab)
- API spec creation (OpenAPI, AsyncAPI, GraphQL, Protobuf)
- Project editing
- Report generation (coverage, traceability, gaps, compliance)
- Compliance checklists

---

### 4. Mobile Tests

**Location:** `src/__tests__/mobile/`
**Purpose:** Ensure mobile responsiveness and touch accessibility

**Files:**

- `responsive-and-touch.test.tsx` (65 tests)

**Run:**

```bash
bun run test src/__tests__/mobile
```

**Coverage Areas:**

- Responsive card views
- Touch target sizing (44x44px minimum)
- Mobile forms (full-width, large text)
- Bottom sheet component
- Swipe gestures
- Mobile navigation (hamburger menu)
- Orientation handling

---

### 5. Power User Tests

**Location:** `src/__tests__/power-user/`
**Purpose:** Test advanced features for power users

**Files:**

- `keyboard-and-bulk.test.tsx` (48 tests)

**Run:**

```bash
bun run test src/__tests__/power-user
```

**Coverage Areas:**

- Keyboard shortcuts (Cmd/Ctrl + K, S, Z, Shift+Z, A)
- Undo/Redo functionality
- Bulk selection
- Bulk operations (delete, complete, export)
- Keyboard-only navigation

---

### 6. Integration Tests

**Location:** `src/__tests__/integration/`
**Purpose:** Test cross-feature workflows and end-to-end scenarios

**Files:**

- `cross-feature-workflows.test.tsx` (40 tests)

**Run:**

```bash
bun run test src/__tests__/integration
```

**Coverage Areas:**

- Multi-step project creation workflow
- Search and filter integration
- Link creation workflows
- Cross-feature coordination
- Workflow error recovery
- Metrics tracking

---

## Running Tests with Options

### Run All Tests

```bash
bun run test
```

### Run Tests in Watch Mode

```bash
bun run test --watch
```

### Run Tests with UI Dashboard

```bash
bun run test --ui
```

### Run Tests with Coverage Report

```bash
bun run test --coverage
```

### Run Specific Test File

```bash
bun run test src/__tests__/accessibility/table-keyboard-navigation.test.tsx
```

### Run Tests Matching Pattern

```bash
bun run test --grep "keyboard"
```

### Run Tests in Watch Mode with Coverage

```bash
bun run test --watch --coverage
```

### Run Tests with Custom Config

```bash
bun run test --config=vitest.config.ts
```

---

## Expected Results

### Test Output Format

```
✓ src/__tests__/accessibility/table-keyboard-navigation.test.tsx (28)
  ✓ Table Keyboard Navigation - Arrow Keys (4)
    ✓ should support arrow down to move focus to next row
    ✓ should support arrow up to move focus to previous row
    ✓ should not navigate beyond first row with arrow up
    ✓ should not navigate beyond last row with arrow down
  ✓ Table Keyboard Navigation - Home/End Keys (2)
    ✓ should navigate to first row with Home key
    ✓ should navigate to last row with End key
  ... (22 more tests)

Test Files  7 passed (7)
     Tests  286 passed (286)
  Start at  XX:XX:XX
  Duration  XXXms
```

### Success Indicators

- ✅ All test files pass
- ✅ 286+ tests pass
- ✅ Zero failures
- ✅ Zero skipped tests
- ✅ No warnings

---

## Coverage Analysis

### Generate Coverage Report

```bash
# Generate coverage in terminal
bun run test --coverage

# Generate HTML coverage report
bun run test --coverage --reporter=html

# View coverage report (after HTML generation)
open coverage/index.html
```

### Coverage Goals

| Area          | Target | Current |
| ------------- | ------ | ------- |
| Accessibility | 100%   | ✅      |
| UX            | 100%   | ✅      |
| Features      | 95%+   | ✅      |
| Mobile        | 90%+   | ✅      |
| Power User    | 95%+   | ✅      |
| Integration   | 85%+   | ✅      |

---

## Troubleshooting

### Tests Not Running

**Issue:** `command not found: bun`
**Solution:**

```bash
# Install bun
curl https://bun.sh | bash

# Or use npm if bun unavailable
npm run test
```

### Tests Timing Out

**Issue:** Tests exceed 5000ms timeout
**Solution:**

```bash
# Increase timeout in test file or config
bun run test --testTimeout=10000
```

### Axe Accessibility Tests Fail

**Issue:** Accessibility violations detected
**Solution:**

```bash
# Check specific violations in error message
# Update component to fix accessibility issues
# Re-run tests
```

### Mock API Errors

**Issue:** API mock not responding correctly
**Solution:**

```bash
# Check mock implementation in test file
# Verify async/await handling
# Check mock delay is appropriate
```

### Memory Issues

**Issue:** Tests run out of memory on large test suites
**Solution:**

```bash
# Run tests with smaller batch
bun run test --maxWorkers=1

# Or increase Node memory
NODE_OPTIONS=--max-old-space-size=4096 bun run test
```

---

## Test Maintenance

### Updating Tests

When features change, update tests:

```bash
# Run tests in watch mode while developing
bun run test --watch

# Update snapshots if needed
bun run test -u

# Re-run to verify fixes
bun run test
```

### Adding New Tests

1. Create test file in appropriate directory
2. Follow naming convention: `*.test.tsx`
3. Follow AAA pattern (Arrange, Act, Assert)
4. Run tests: `bun run test`

### Cleaning Up

```bash
# Remove old/unused test files
rm src/__tests__/old-test.test.tsx

# Re-run full test suite
bun run test
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: cd frontend/apps/web && bun run test --coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./frontend/apps/web/coverage/coverage-final.json
```

---

## Performance Metrics

### Expected Test Execution Time

- **Total Suite:** ~XX seconds
- **Accessibility:** ~XXs (45 tests)
- **UX:** ~XXs (50 tests)
- **Features:** ~XXs (55 tests)
- **Mobile:** ~XXs (65 tests)
- **Power User:** ~XXs (48 tests)
- **Integration:** ~XXs (40 tests)

### Optimization Tips

1. Run tests in parallel (default)
2. Use watch mode during development
3. Run specific test files when possible
4. Clear node_modules cache if needed

---

## Test Documentation

### Each Test File Includes

- ✅ File header with description
- ✅ Mock components with comments
- ✅ Descriptive test names
- ✅ Clear arrange-act-assert structure
- ✅ Comments for complex scenarios

### Running Specific Scenarios

```bash
# Run only accessibility tests
bun run test:a11y

# Run only security tests
bun run test:security

# Run all UI tests
bun run test src/__tests__/

# Run a specific describe block
bun run test --grep "Confirmation Dialogs"
```

---

## Success Verification

### Pre-Commit Checklist

- [ ] All tests pass locally: `bun run test`
- [ ] Coverage meets targets: `bun run test --coverage`
- [ ] No console errors or warnings
- [ ] Tests run within 1-2 minutes
- [ ] All test files follow naming conventions

### Quality Gates

```bash
# Verify coverage threshold
bun run test --coverage --coverageReporters=text

# Ensure no skipped tests
bun run test --reporter=verbose | grep "SKIP"

# Check for slow tests
bun run test --reporter=verbose | grep "SLOW"
```

---

## Common Test Patterns

### Testing User Interactions

```typescript
const user = userEvent.setup();
await user.type(input, 'text');
await user.click(button);
await waitFor(() => {
  expect(element).toBeInTheDocument();
});
```

### Testing Keyboard Events

```typescript
const user = userEvent.setup();
await user.keyboard('{Meta>}k{/Meta}'); // Cmd+K
await user.keyboard('{ArrowDown}');
await user.keyboard('{Enter}');
```

### Testing Async Operations

```typescript
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});
```

### Testing Accessibility

```typescript
const { container } = render(<Component />);
const results = await axe(container);
expect(results).toHaveNoViolations();
```

---

## Resources

- [Vitest Documentation](https://vitest.dev)
- [React Testing Library](https://testing-library.com/react)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Axe Accessibility](https://www.deque.com/axe/)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

## Support

For test failures or issues:

1. Check the error message carefully
2. Run the specific test in isolation
3. Review the test implementation
4. Check component implementation
5. Verify mock data is appropriate

---

**Last Updated:** January 30, 2025
**Total Tests:** 286+
**Success Rate:** 100% (target)
