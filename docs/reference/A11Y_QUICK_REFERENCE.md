# Accessibility Testing - Quick Reference

## Running Tests

```bash
# Run all a11y tests
bun run test:a11y

# Watch mode (TDD)
bun run test:a11y:watch

# Interactive UI
bun run test:a11y:ui

# Coverage report
bun run test:a11y:coverage
```

## Writing New A11y Tests

### 1. Basic Component Test

```typescript
import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { axe } from './setup'
import { YourComponent } from '@/components/YourComponent'

describe('YourComponent Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<YourComponent />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

### 2. Keyboard Navigation Test

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

describe('Keyboard Navigation', () => {
  it('should navigate with Tab key', async () => {
    const user = userEvent.setup()
    render(
      <div>
        <button>First</button>
        <button>Second</button>
      </div>
    )

    const first = screen.getByRole('button', { name: 'First' })
    const second = screen.getByRole('button', { name: 'Second' })

    first.focus()
    expect(first).toHaveFocus()

    await user.tab()
    expect(second).toHaveFocus()
  })
})
```

### 3. Form Field Test

```typescript
describe('Form Field Accessibility', () => {
  it('should associate label with input', async () => {
    const { container } = render(
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" />
      </div>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()

    const input = screen.getByLabelText('Email')
    expect(input).toHaveAttribute('type', 'email')
  })

  it('should show error with aria-invalid', async () => {
    const { container } = render(
      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          aria-invalid="true"
          aria-describedby="error"
        />
        <span id="error" role="alert">Password is required</span>
      </div>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

## Common Patterns

### Buttons

```typescript
// Text button
<Button>Submit</Button>

// Icon-only (needs accessible name)
<Button aria-label="Close" size="icon">
  <X />
</Button>

// With loading state
<Button disabled aria-busy="true">
  Saving...
</Button>
```

### Form Fields

```typescript
// Standard label
<label htmlFor="name">Name</label>
<Input id="name" required aria-required="true" />

// With error
<Input
  id="email"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<span id="email-error" role="alert">
  Invalid email format
</span>

// With help text
<Input
  id="password"
  aria-describedby="password-help"
/>
<span id="password-help">
  Must be 8+ characters
</span>
```

### Dialogs

```typescript
<Dialog open={open} onOpenChange={setOpen}>
  <div role="dialog" aria-labelledby="title">
    <h2 id="title">Confirm Action</h2>
    <p>Are you sure?</p>
    <Button onClick={() => setOpen(false)}>Cancel</Button>
    <Button onClick={handleConfirm}>Confirm</Button>
  </div>
</Dialog>
```

### Loading States

```typescript
<div role="status" aria-live="polite" aria-busy="true">
  <span className="sr-only">Loading...</span>
  <Spinner aria-hidden="true" />
</div>
```

### Error States

```typescript
<div role="alert" aria-live="assertive">
  <h2>Error loading data</h2>
  <p>Please try again</p>
  <Button onClick={retry}>Retry</Button>
</div>
```

### Live Regions

```typescript
// Polite (non-urgent updates)
<div role="status" aria-live="polite">
  Search results: {count} found
</div>

// Assertive (urgent notifications)
<div role="alert" aria-live="assertive">
  Your session is about to expire
</div>
```

## ARIA Attributes Reference

### Labels

- `aria-label` - Text label for element
- `aria-labelledby` - ID(s) of labeling element(s)
- `aria-describedby` - ID(s) of describing element(s)

### States

- `aria-invalid="true"` - Field has validation error
- `aria-required="true"` - Field is required
- `aria-busy="true"` - Element is loading
- `aria-disabled="true"` - Element is disabled
- `aria-selected="true"` - Element is selected
- `aria-current="page"` - Current page in nav

### Roles

- `role="alert"` - Important message
- `role="status"` - Status update
- `role="dialog"` - Modal dialog
- `role="search"` - Search form
- `role="navigation"` - Navigation section
- `role="main"` - Main content
- `role="button"` - Custom button

### Relationships

- `aria-controls="id"` - Element controls another
- `aria-owns="id"` - Element owns another
- `aria-activedescendant="id"` - Active descendant

## Keyboard Shortcuts

### Test Helpers

```typescript
import { pressKey, pressTab, pressEnter, pressEscape, pressArrowDown, pressArrowUp } from './setup';

// Simulate key presses
pressKey('k', { metaKey: true }); // Cmd+K
pressKey('k', { ctrlKey: true }); // Ctrl+K
pressTab(); // Tab forward
pressTab(true); // Shift+Tab backward
pressEnter(); // Enter
pressEscape(); // Escape
pressArrowDown(); // Arrow Down
pressArrowUp(); // Arrow Up
```

### Expected Keyboard Behavior

- **Tab** - Move focus forward
- **Shift+Tab** - Move focus backward
- **Enter** - Activate button/link
- **Space** - Activate button, toggle checkbox
- **Escape** - Close dialog/menu
- **Arrow Keys** - Navigate lists/menus
- **Home/End** - First/last item

## Screen Reader Testing

### macOS VoiceOver

```bash
# Enable/disable
Cmd+F5

# Navigate
Ctrl+Option+Arrow keys

# Read all
Ctrl+Option+A

# Headings list
Ctrl+Option+Cmd+H

# Links list
Ctrl+Option+Cmd+L
```

### Windows NVDA (free)

```bash
# Toggle speech
NVDA+S

# Navigate
Arrow keys

# Read all
NVDA+Down Arrow

# Elements list
NVDA+F7
```

## Checklist for New Components

✅ Component has no axe violations
✅ All interactive elements are keyboard accessible
✅ Focus indicators are visible
✅ Images/icons have text alternatives
✅ Form fields have labels
✅ Errors use aria-invalid + role="alert"
✅ Loading states use aria-busy
✅ Modals trap focus and restore on close
✅ Headings follow proper hierarchy
✅ Color contrast meets 4.5:1 (text) / 3:1 (UI)

## Common Violations & Fixes

### Missing Button Label

```typescript
// ❌ Bad
<button><Icon /></button>

// ✅ Good
<button aria-label="Delete item">
  <Icon />
</button>
```

### Missing Form Label

```typescript
// ❌ Bad
<input type="text" placeholder="Name" />

// ✅ Good
<label htmlFor="name">Name</label>
<input id="name" type="text" />
```

### Poor Color Contrast

```typescript
// ❌ Bad (3:1 contrast)
<p className="text-gray-400">Secondary text</p>

// ✅ Good (4.5:1+ contrast)
<p className="text-gray-700">Secondary text</p>
```

### Missing Error Association

```typescript
// ❌ Bad
<input id="email" />
<span className="error">Invalid email</span>

// ✅ Good
<input
  id="email"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<span id="email-error" role="alert">
  Invalid email
</span>
```

### Non-Keyboard Accessible

```typescript
// ❌ Bad
<div onClick={handleClick}>Click me</div>

// ✅ Good
<button onClick={handleClick}>Click me</button>

// ✅ Also good (custom control)
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }}
>
  Click me
</div>
```

## Files Reference

```
frontend/apps/web/src/__tests__/a11y/
├── setup.ts                # Test helpers & axe config
├── components.test.tsx     # UI component tests (24 tests)
├── forms.test.tsx         # Form pattern tests (26 tests)
├── navigation.test.tsx    # Keyboard nav tests (18 tests)
├── pages.test.tsx        # Page structure tests (12 tests)
└── README.md             # Full documentation
```

## CI/CD Integration

Tests run automatically in CI:

```yaml
# Example GitHub Actions
- name: Run accessibility tests
  run: bun run test:a11y
```

Coverage target: **90%+**

Current status: **72/80 tests passing (90%)**

## Resources

- [Full README](./README.md) - Complete testing guide
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Practices](https://www.w3.org/WAI/ARIA/apg/)
- [axe-core Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
