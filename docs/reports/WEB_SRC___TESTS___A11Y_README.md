# Accessibility Testing Suite

Comprehensive accessibility (a11y) tests for TraceRTM frontend, ensuring WCAG 2.1 Level AA compliance.

## Overview

This test suite uses **jest-axe** to automatically detect accessibility violations in components, forms, pages, and navigation patterns. All tests run in the existing Vitest test environment.

## Coverage

### Components (`components.test.tsx`)

Tests core UI components from `@tracertm/ui`:

- **Button** - Text labels, variants, disabled states, icon-only buttons
- **Input** - Labels, aria-labels, error states, required fields
- **Select** - Options, labels, disabled states
- **Alert** - Live regions, role attributes
- **Badge** - Color contrast across variants
- **Card** - Semantic structure, headings
- **Dialog** - Modal accessibility, focus management
- **Tooltip** - Keyboard accessibility, aria-describedby

### Forms (`forms.test.tsx`)

Tests form accessibility patterns:

- **Labels** - htmlFor associations, aria-label, aria-labelledby
- **Validation** - Required fields, error messages, aria-invalid
- **Fieldsets** - Radio groups, checkbox groups, legends
- **Submission** - Submit/reset/cancel buttons, loading states
- **Autocomplete** - Proper autocomplete attributes
- **Keyboard Navigation** - Tab order, Enter to submit
- **Help Text** - aria-describedby for hints and errors

### Navigation (`navigation.test.tsx`)

Tests keyboard navigation and interactive patterns:

- **Command Palette** - Cmd/Ctrl+K, Escape, arrow keys, Enter
- **Skip Links** - Skip to main content
- **Focus Management** - Modal focus trapping, focus restoration
- **Focus Indicators** - Visible focus rings
- **Landmarks** - header, nav, main, aside, footer roles
- **Tab Order** - Logical navigation order, disabled element handling
- **Custom Controls** - Space/Enter for custom buttons, arrow keys for selects

### Pages (`pages.test.tsx`)

Tests page-level accessibility:

- **Page Structure** - HTML document structure, lang attribute
- **Headings** - Unique h1, proper hierarchy, no skipped levels
- **Dashboard** - Project cards, recent projects section
- **Project List** - Accessible tables, captions, scope attributes
- **Project Detail** - Tab navigation, view switching
- **Empty States** - Status messages, call-to-action
- **Loading States** - aria-busy, screen reader announcements
- **Error States** - Alert role, recovery actions
- **Search/Filter** - Search role, result announcements
- **Breadcrumbs** - aria-current for current page
- **Pagination** - Accessible page controls

## WCAG 2.1 Level AA Standards

Tests verify compliance with:

- **1.1.1 Non-text Content** - All images/icons have text alternatives
- **1.3.1 Info and Relationships** - Semantic HTML, ARIA labels
- **1.4.3 Contrast (Minimum)** - 4.5:1 text contrast, 3:1 UI component contrast
- **2.1.1 Keyboard** - All functionality available via keyboard
- **2.1.2 No Keyboard Trap** - Users can navigate away using keyboard
- **2.4.1 Bypass Blocks** - Skip links available
- **2.4.3 Focus Order** - Logical tab order
- **2.4.7 Focus Visible** - Visible focus indicators
- **3.2.1 On Focus** - No automatic context changes
- **3.3.1 Error Identification** - Errors identified in text
- **3.3.2 Labels or Instructions** - Form fields have labels
- **4.1.1 Parsing** - Valid HTML
- **4.1.2 Name, Role, Value** - Proper ARIA attributes

## Running Tests

```bash
# Run all accessibility tests
bun run test:a11y

# Watch mode (re-run on file changes)
bun run test:a11y:watch

# Interactive UI
bun run test:a11y:ui

# With coverage report
bun run test:a11y:coverage
```

## Test Helpers

### `axe(container)`

Runs axe-core accessibility checks:

```typescript
const { container } = render(<Button>Click me</Button>)
const results = await axe(container)
expect(results).toHaveNoViolations()
```

### Keyboard Helpers

```typescript
import {
  pressKey,
  pressTab,
  pressEnter,
  pressEscape,
  pressArrowDown,
  pressArrowUp,
  getFocusedElement,
  hasFocusIndicator,
  isKeyboardAccessible,
} from './setup';

// Simulate keyboard events
pressKey('k', { metaKey: true });
pressTab(); // Forward
pressTab(true); // Shift+Tab (backward)
pressEnter();
pressEscape();

// Check focus state
const focused = getFocusedElement();
expect(hasFocusIndicator(focused)).toBe(true);
expect(isKeyboardAccessible(button)).toBe(true);
```

## Common Accessibility Patterns

### Buttons

```typescript
// Text button
<Button>Submit</Button>

// Icon-only button (requires accessible name)
<Button aria-label="Close dialog" size="icon">
  <X />
</Button>
```

### Form Fields

```typescript
// With label element
<label htmlFor="email">Email</label>
<Input id="email" type="email" />

// With aria-label
<Input aria-label="Search" type="search" />

// With error
<Input
  id="password"
  aria-invalid="true"
  aria-describedby="password-error"
/>
<span id="password-error" role="alert">
  Password must be at least 8 characters
</span>
```

### Dialogs

```typescript
<Dialog open onOpenChange={setOpen}>
  <div role="dialog" aria-labelledby="dialog-title">
    <h2 id="dialog-title">Dialog Title</h2>
    <p>Content</p>
    <Button onClick={() => setOpen(false)}>Close</Button>
  </div>
</Dialog>
```

### Loading States

```typescript
<div role="status" aria-live="polite" aria-busy="true">
  <span className="sr-only">Loading projects...</span>
  <Spinner aria-hidden="true" />
</div>
```

### Live Regions

```typescript
// Polite (non-urgent)
<div role="status" aria-live="polite">
  5 results found
</div>

// Assertive (urgent)
<div role="alert" aria-live="assertive">
  Error: Connection failed
</div>
```

## Continuous Integration

Accessibility tests run as part of the standard test suite:

```bash
bun run test  # Includes a11y tests
```

Coverage target: **90%+** for all accessibility-related code paths.

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)
- [axe-core Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

## Fixing Violations

When a test fails with violations:

1. **Read the violation message** - axe provides specific guidance
2. **Check the element** - Review the HTML in the error output
3. **Apply the fix** - Add missing attributes, improve semantics
4. **Re-run tests** - Verify the violation is resolved
5. **Test manually** - Use keyboard navigation and screen reader

Common fixes:

- Add `aria-label` to icon-only buttons
- Associate `<label>` with `<input>` using `htmlFor`/`id`
- Add `role="alert"` to error messages
- Ensure sufficient color contrast (4.5:1 for text)
- Add focus indicators with `focus-visible:ring-2`
- Use semantic HTML (`<button>`, `<nav>`, `<main>`)

## Screen Reader Testing

Automated tests catch many issues, but manual testing with screen readers is recommended:

- **macOS**: VoiceOver (Cmd+F5)
- **Windows**: NVDA (free) or JAWS
- **Chrome/Edge**: ChromeVox extension

Common screen reader commands:

- **Navigate**: Tab/Shift+Tab
- **Headings**: H (VoiceOver: Ctrl+Option+Cmd+H)
- **Links**: (VoiceOver: Ctrl+Option+Cmd+L)
- **Forms**: (VoiceOver: Ctrl+Option+Cmd+J)
- **Read all**: (VoiceOver: Ctrl+Option+A)
