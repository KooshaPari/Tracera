# Accessibility Quick Reference Guide

## Keyboard Navigation Shortcuts

| Key Combination | Action                   | Context                         |
| --------------- | ------------------------ | ------------------------------- |
| `TAB`           | Move focus forward       | Any page                        |
| `SHIFT + TAB`   | Move focus backward      | Any page                        |
| `ENTER`         | Activate button/link     | When focused on button/link     |
| `SPACE`         | Activate button/checkbox | When focused on button/checkbox |
| `ESCAPE`        | Close modal/dialog       | When modal is open              |
| First `TAB`     | Focus Skip link          | Home page                       |

## File Reference

### Layout Components

```
src/components/layout/
├── Layout.tsx          ← Skip link + main content ID
├── Header.tsx          ← role="banner"
└── Sidebar.tsx         ← role="navigation"
```

### Form Components

```
src/components/forms/
└── CreateItemForm.tsx  ← Modal focus trap + ARIA
```

### Test Files

```
e2e/
└── accessibility.spec.ts  ← All accessibility tests
```

## Common ARIA Patterns

### Skip Link

```tsx
<a href='#main-content' onClick={handleSkip}>
  Skip to main content
</a>
```

### Landmark Regions

```tsx
<header role="banner">...</header>
<nav role="navigation" aria-label="Main nav">...</nav>
<main id="main-content" role="main">...</main>
<footer role="contentinfo">...</footer>
```

### Modal Dialog

```tsx
<div role='dialog' aria-modal='true' aria-labelledby='dialog-title' tabIndex={-1}>
  <h2 id='dialog-title'>Title</h2>
  {/* content */}
</div>
```

### Form Input

```tsx
<label htmlFor="input-id">Label</label>
<input id="input-id" />
```

### Select as Combobox

```tsx
<select role='combobox' aria-expanded='false'>
  <option>Option</option>
</select>
```

### Error Message

```tsx
<p role='alert' aria-live='polite'>
  {error}
</p>
```

## Checklist for New Components

When adding new interactive components:

- [ ] Keyboard accessible (Tab, Enter, Space, Escape)
- [ ] Visible focus indicator (`focus:ring-2`)
- [ ] ARIA role if not semantic HTML
- [ ] aria-label or aria-labelledby
- [ ] aria-live for dynamic content
- [ ] Test with keyboard only
- [ ] Test with screen reader
- [ ] No keyboard traps (except modals with escape)

## Common Issues & Fixes

### Issue: Button not focusable

**Fix:** Ensure button is not `display: none` and has no `tabindex="-1"`

### Issue: Link not working with Tab

**Fix:** Use semantic `<a>` or `<button>` tags, not divs

### Issue: Modal doesn't trap focus

**Fix:** Add keydown listener and check for Tab key, prevent default and redirect

### Issue: Screen reader can't read error

**Fix:** Add `role="alert"` and `aria-live="polite"` to error message

### Issue: Focus not visible

**Fix:** Ensure `focus:ring-2 focus:ring-primary` or equivalent is applied

## Testing Commands

```bash
# Run all accessibility tests
bun run test:e2e -- e2e/accessibility.spec.ts

# Run specific test
bun run test:e2e -- e2e/accessibility.spec.ts -g "should navigate"

# Debug mode
bun run test:e2e -- e2e/accessibility.spec.ts --debug

# With UI
bun run test:e2e -- e2e/accessibility.spec.ts --ui
```

## Keyboard Testing Procedure

1. **Load page** - Open URL in browser
2. **Press TAB once** - Skip link appears and is focused
3. **Press ENTER** - Focus jumps to main content
4. **Press TAB repeatedly** - Cycle through all interactive elements
5. **Press SHIFT+TAB** - Go backwards through elements
6. **Click button for modal** - Modal opens, first input focused
7. **Press TAB in modal** - Cycles through modal fields only
8. **Press ESCAPE** - Modal closes
9. **Press TAB after modal** - Focus back in main content

## Screen Reader Testing (NVDA)

```
1. Start NVDA
2. Use Arrow Keys to navigate content
3. Use H to jump between headings
4. Use N to jump to next landmark (navigation, main, etc.)
5. Use B to jump between buttons
6. Use L to jump between lists
7. Use Tab to navigate with focus indicators
```

## Performance Considerations

- Focus trap: Only active in modals, minimal overhead
- ARIA attributes: Zero runtime cost
- Skip link: No performance impact
- **Overall:** ~2KB CSS, negligible JS impact

## Browser DevTools

### Chrome DevTools

1. Press F12
2. Open Accessibility panel
3. Inspect element tree
4. Check ARIA properties
5. View contrast ratios

### Firefox DevTools

1. Press F12
2. Open Inspector
3. Check Accessibility panel
4. Verify ARIA attributes
5. Test keyboard navigation

## Common ARIA Values

### roles

- `button` - Clickable element
- `link` - Navigation link
- `navigation` - Navigation landmark
- `main` - Main content
- `dialog` - Modal dialog
- `alert` - Alert message
- `combobox` - Dropdown select

### aria-\* attributes

- `aria-label` - Label for button/icon
- `aria-labelledby` - References element that labels this
- `aria-live` - "polite" | "assertive" | "off"
- `aria-expanded` - "true" | "false"
- `aria-modal` - "true" | "false"
- `aria-hidden` - "true" | "false"

## Resources

- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- ARIA Guide: https://www.w3.org/WAI/ARIA/apg/
- MDN Accessibility: https://developer.mozilla.org/docs/Web/Accessibility
- Axe DevTools: https://www.deque.com/axe/devtools/

## Quick Help

**Q: How do I test keyboard navigation?**
A: Press Tab to cycle through focusable elements, Shift+Tab to go backwards, Enter to activate, Escape to close modals.

**Q: How do I add an ARIA label?**
A: Add `aria-label="descriptive text"` attribute to the element.

**Q: How do I announce error messages?**
A: Add `role="alert"` and `aria-live="polite"` to the error message container.

**Q: How do I implement focus trap?**
A: Listen for Tab key, find all focusable elements, prevent default, redirect to first/last as needed.

**Q: How do I skip navigation?**
A: Add a "Skip to main content" link that jumps to `id="main-content"`.

---

**Keep pages accessible, one Tab at a time!**
