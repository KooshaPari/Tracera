# Accessibility Implementation Guide

Comprehensive accessibility implementation for forms, CommandPalette, and focus management following WCAG 2.1 Level AA standards.

## Overview

This document describes the accessibility features implemented across the application, with focus on:
- **CommandPalette**: Combobox ARIA pattern with keyboard navigation
- **Forms**: aria-describedby connections, required indicators, validation announcements
- **Focus Management**: Focus trapping, restoration, and visible indicators

## Components Updated

### 1. CommandPalette.tsx

Implements the **combobox ARIA pattern** with complete keyboard support.

#### ARIA Structure

```tsx
<div role="dialog" aria-modal="true" aria-labelledby="command-palette-title">
  <input
    role="combobox"
    aria-label="Search commands"
    aria-describedby="command-hint"
    aria-expanded={open}
    aria-controls="command-listbox"
    aria-activedescendant={selectedId}
  />
  <div id="command-listbox" role="listbox">
    <button role="option" aria-selected={isSelected} aria-describedby={descId} />
  </div>
</div>
```

#### Key Features

- **Combobox Pattern**: Input with role="combobox" controlling a listbox
- **aria-activedescendant**: Tracks currently selected item
- **aria-live Region**: Announces search results (polite)
- **Keyboard Support**:
  - `Ctrl/Cmd+K`: Toggle palette
  - `Arrow Up/Down`: Navigate items
  - `Home/End`: Jump to first/last item
  - `Enter`: Select item
  - `Escape`: Close palette
  - `Tab`: Exit palette naturally
- **Focus Management**: Saves and restores focus on open/close
- **Screen Reader Announcements**: Results count and selection feedback

#### Usage

```tsx
import { CommandPalette } from "@/components/CommandPalette";

export function App() {
  return <CommandPalette />;
}
```

### 2. CreateItemForm.tsx

Implements **accessible form patterns** with comprehensive ARIA attributes.

#### ARIA Structure

```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <h2 id="dialog-title">Create Item</h2>
  <p id="dialog-description" className="sr-only">
    Fill in the required fields...
  </p>

  <form>
    <label htmlFor="title">
      Title <span aria-label="required">*</span>
    </label>
    <input
      id="title"
      aria-describedby="title-help title-error"
      aria-required="true"
      aria-invalid={hasError}
    />
    <span id="title-help">Help text</span>
    {error && (
      <p id="title-error" role="alert" aria-live="polite">
        {error}
      </p>
    )}
  </form>
</div>
```

#### Key Features

- **Dialog Pattern**: Modal with aria-modal, aria-labelledby, aria-describedby
- **aria-describedby**: Links inputs to help and error text
- **aria-invalid + aria-required**: Marks field validation states
- **role="alert"**: Error messages announced to screen readers
- **Focus Trap**: Keeps focus within dialog using Tab/Shift+Tab
- **Focus Management**: Focuses first field on open, restores on close
- **Keyboard Support**:
  - `Tab`: Navigate forward through fields
  - `Shift+Tab`: Navigate backward through fields
  - `Escape`: Close dialog
  - `Enter`: Submit form
- **Validation Announcements**: Errors announced via aria-live

#### Usage

```tsx
import { CreateItemForm } from "@/components/forms/CreateItemForm";

export function ItemModal() {
  const [open, setOpen] = useState(false);

  return (
    open && (
      <CreateItemForm
        onSubmit={(data) => console.log(data)}
        onCancel={() => setOpen(false)}
      />
    )
  );
}
```

### 3. Focus Management Utilities

Located in `/src/lib/focus-management.ts`

#### Functions

**Focus Trapping**
```typescript
// Create a focus trap for a modal
const cleanup = createFocusTrap(container, onEscape);

// Later: cleanup();
```

**Focus Saving/Restoring**
```typescript
// Save current focus
const saved = saveFocus();

// Restore later
restoreFocus(saved);
```

**Navigation**
```typescript
// Move focus to first focusable element
focusFirst(container);

// Move focus to last focusable element
focusLast(container);

// Get next/previous focusable element
const next = getNextFocusableElement(current, container);
const prev = getPreviousFocusableElement(current, container);
```

**Screen Reader Announcements**
```typescript
// Announce message to screen readers
announceToScreenReader(
  "5 results found",
  "polite" // or "assertive" for urgent messages
);
```

**Validation Helpers**
```typescript
// Check if element is keyboard accessible
const isAccessible = isKeyboardAccessible(element);

// Check if element has visible focus indicator
const hasFocus = hasFocusIndicator(element);
```

## CSS Enhancements

Added to `/src/index.css`:

### Visible Focus Indicators

```css
button:focus-visible,
input:focus-visible,
/* ... more selectors ... */
{
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}
```

- **2px minimum outline** for WCAG 2.1 AA compliance (Success Criterion 2.4.7)
- **2px offset** for proper spacing
- Applied to all interactive elements

### High Contrast Mode

```css
@media (prefers-contrast: more) {
  /* Increase to 3px outline for high contrast */
}
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  /* Disable animations for users who prefer reduced motion */
}
```

### Screen Reader Only Content

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}
```

## WCAG 2.1 AA Compliance

This implementation addresses the following WCAG 2.1 Level AA success criteria:

### 1.3 Adaptable
- **1.3.1 Info and Relationships**: Semantic HTML, ARIA labels, proper structure

### 2.1 Keyboard Accessible
- **2.1.1 Keyboard**: All functionality available via keyboard
- **2.1.2 No Keyboard Trap**: Focus can escape using keyboard (except modals with proper exit)

### 2.4 Navigable
- **2.4.1 Bypass Blocks**: Focus management and modal patterns
- **2.4.3 Focus Order**: Logical tab order maintained
- **2.4.7 Focus Visible**: 2px visible focus indicators on all interactive elements

### 3.2 Predictable
- **3.2.1 On Focus**: No context changes on focus (only blur)

### 3.3 Input Assistance
- **3.3.1 Error Identification**: Errors identified via role="alert" and aria-invalid
- **3.3.2 Labels or Instructions**: All fields have labels or aria-labels
- **3.3.4 Error Prevention**: Required fields marked with aria-required

### 4.1 Compatible
- **4.1.2 Name, Role, Value**: Proper ARIA attributes on all interactive elements
- **4.1.3 Status Messages**: aria-live regions for announcements

## Testing

### Unit Tests

Located in `/src/__tests__/a11y/`:

- `command-palette.test.tsx` - CommandPalette combobox pattern and keyboard navigation
- `form-accessibility.test.tsx` - Form patterns, aria-describedby, validation
- `forms.test.tsx` - Existing form tests (labels, fieldsets, etc.)

#### Run Tests

```bash
# Run all accessibility tests
bun run test:a11y

# Watch mode
bun run test:a11y:watch

# With coverage
bun run test:a11y:coverage
```

### Manual Testing

#### Screen Readers

Test with actual screen readers for best results:

**macOS**
```bash
# Enable VoiceOver
Cmd + F5
```

**Windows**
- NVDA (free): https://www.nvaccess.org/
- JAWS (paid): https://www.freedomscientific.com/

**Chrome/Edge**
- ChromeVox extension

#### Keyboard Only Navigation

Test without mouse:
1. Press `Tab` to navigate forward
2. Press `Shift+Tab` to navigate backward
3. Press `Space/Enter` on buttons
4. Press `Arrow Up/Down` in select dropdowns
5. Use `Ctrl/Cmd+K` for CommandPalette

#### Browser DevTools

Use browser accessibility inspector:
1. Chrome DevTools → Elements → Accessibility pane
2. Check ARIA attributes, roles, computed names
3. Run axe DevTools audit

## Common Patterns

### Required Field with Error

```tsx
<div>
  <label htmlFor="email">
    Email <span aria-label="required">*</span>
  </label>
  <input
    id="email"
    type="email"
    aria-describedby={error ? "email-error" : "email-help"}
    aria-required="true"
    aria-invalid={!!error}
    required
  />
  {error ? (
    <p id="email-error" role="alert" aria-live="polite" aria-atomic="true">
      {error}
    </p>
  ) : (
    <span id="email-help" className="text-xs text-muted-foreground">
      We'll never share your email
    </span>
  )}
</div>
```

### Accessible Icon Button

```tsx
<button
  aria-label="Close dialog"
  className="focus-visible:ring-2 focus-visible:ring-primary"
>
  <X className="h-5 w-5" aria-hidden="true" />
</button>
```

### Modal Dialog

```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
  className="focus-visible:ring-2 focus-visible:ring-primary"
>
  <h2 id="modal-title">Title</h2>
  <p id="modal-description">Description or instructions</p>
  {/* content */}
</div>
```

### Screen Reader Only Text

```tsx
<p className="sr-only">This text is only read by screen readers</p>
```

## Troubleshooting

### Issue: Focus visible outline not showing

**Solution**: Ensure `focus-visible:ring-2` class is applied. Check that CSS is loaded and no conflicting `outline: none` rules exist.

### Issue: Screen reader not announcing error

**Solution**: Ensure error has `role="alert"` and `aria-live="polite"`. Use `aria-atomic="true"` for entire message.

### Issue: Tab key not navigating in modal

**Solution**: Verify focus trap is created with `createFocusTrap()`. Check that modal is using `role="dialog"` and `aria-modal="true"`.

### Issue: Form submission not announcing success

**Solution**: Use `announceToScreenReader("Success message", "polite")` after form submission.

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)
- [WebAIM Resources](https://webaim.org/)
- [MDN Web Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## Checklist for New Components

When creating new interactive components, ensure:

- [ ] Proper semantic HTML (`<button>`, `<input>`, `<select>`, etc.)
- [ ] All interactive elements keyboard accessible
- [ ] Visible focus indicators (2px outline)
- [ ] ARIA labels on all controls
- [ ] aria-describedby for help/error text
- [ ] ARIA roles for custom components (button, option, etc.)
- [ ] aria-live regions for dynamic content
- [ ] Focus management for modals (trap + restore)
- [ ] Color contrast ≥4.5:1 for text
- [ ] Tests with jest-axe
- [ ] Manual testing with screen reader
