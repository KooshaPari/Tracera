# Mobile Components Quick Start

## Overview

Complete mobile-optimized component library for TraceRTM with WCAG 2.1 Level AAA compliance.

## Components

### 1. ResponsiveCardView

Displays items as responsive cards that adapt to screen size.

```tsx
import { ResponsiveCardView, type CardItem } from '@/components/mobile';

const items: CardItem[] = [
  {
    id: '1',
    title: 'Item Title',
    subtitle: 'Subtitle',
    badge: <Badge>Type</Badge>,
    status: <StatusBadge />,
    onClick: () => navigate('/item/1'),
  },
];

<ResponsiveCardView items={items} />;
```

**Responsive Layout:**

- Mobile (< 640px): 1 column
- Tablet (640-1024px): 2 columns
- Desktop (> 1024px): 3 columns

### 2. MobileMenu

Hamburger menu for mobile navigation.

```tsx
import { MobileMenu } from '@/components/mobile';

<MobileMenu />;
```

**Features:**

- 44x44px minimum touch target
- Auto-integration in Header
- Hidden on desktop (md: breakpoint)
- Full keyboard navigation

### 3. MobileFormLayout

Optimized form components for touch input.

```tsx
import {
  MobileFormLayout,
  FormField,
  FormGroup,
  FormActions,
  FormInput,
  FormSelect,
  FormTextarea,
} from '@/components/mobile';

<MobileFormLayout title='Create Item'>
  <FormGroup>
    <FormField label='Title' required>
      <FormInput placeholder='Enter title' />
    </FormField>

    <FormField label='Type'>
      <FormSelect>
        <option>Feature</option>
        <option>Bug</option>
      </FormSelect>
    </FormField>
  </FormGroup>

  <FormField label='Description'>
    <FormTextarea placeholder='Enter description' />
  </FormField>

  <FormActions>
    <Button variant='ghost'>Cancel</Button>
    <Button>Submit</Button>
  </FormActions>
</MobileFormLayout>;
```

**Features:**

- 44px minimum input height
- Full-width on mobile
- 2-column on tablet
- Automatic spacing and validation

### 4. BottomSheet

Mobile-native modal that slides up from bottom.

```tsx
import { BottomSheet } from '@/components/mobile';

const [isOpen, setIsOpen] = useState(false);

<BottomSheet isOpen={isOpen} onClose={() => setIsOpen(false)} title='Options'>
  {/* Content */}
</BottomSheet>;
```

**Features:**

- Drag handle indicator
- Dismissible via Escape/backdrop
- Smooth animations
- Prevents body scroll

### 5. MobilePicker

Touch-optimized picker for selections.

```tsx
import { MobilePicker } from '@/components/mobile';

const [selected, setSelected] = useState('low');

<MobilePicker
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title='Select Priority'
  options={[
    { value: 'low', label: 'Low', description: 'Not urgent' },
    { value: 'high', label: 'High', description: 'Important' },
  ]}
  selectedValue={selected}
  onSelect={setSelected}
/>;
```

**Features:**

- 56px+ touch targets
- Large text for readability
- Visual selection state
- Optional descriptions

## Touch Target Requirements

All interactive elements must be minimum 44x44px (WCAG 2.5.5).

### CSS Utilities

```tsx
import { touchTargetClasses } from '@/lib/touch-target-audit';

// Apply to elements
<button className={touchTargetClasses.minTouchTarget}>Action</button>;

// Available classes:
// - minTouchHeight: 'min-h-[44px]'
// - minTouchWidth: 'min-w-[44px]'
// - minTouchTarget: 'min-h-[44px] min-w-[44px]'
// - touchPadding: 'p-2.5'
// - touchPaddingSmall: 'p-2'
```

### Button Patterns

```tsx
// Icon-only (44x44px)
<Button size="icon" className="h-11 w-11">
  <Icon className="h-5 w-5" />
</Button>

// Text + Icon (min 44px height)
<Button className="min-h-[44px] gap-2">
  <Icon className="h-5 w-5" />
  Label
</Button>

// Full-width on mobile
<Button className="w-full min-h-[44px]">
  Action
</Button>
```

## Responsive Breakpoints

```css
/* Base styles: Mobile first (320px+) */
.card {
  @apply p-4 text-sm;
}

/* Small devices */
@media (min-width: 640px) {
  /* sm: */
}

/* Tablets */
@media (min-width: 768px) {
  /* md: */
}

/* Desktops */
@media (min-width: 1024px) {
  /* lg: */
}

/* Large screens */
@media (min-width: 1280px) {
  /* xl: */
}
```

## Accessibility

### WCAG 2.1 Level AAA

- ✅ Touch targets: 44x44px minimum
- ✅ Focus visible: 2px ring
- ✅ Keyboard navigation: Full support
- ✅ Screen readers: Proper ARIA
- ✅ Color contrast: 4.5:1

### Testing

```tsx
import { auditTouchTargets, logTouchTargetAudit } from '@/lib/touch-target-audit';

// Run audit in development
if (import.meta.env.DEV) {
  const issues = auditTouchTargets();
  logTouchTargetAudit(issues);
}
```

## Performance

### Touch Response (< 100ms)

- Use hardware acceleration: `transform: translateZ(0)`
- Avoid expensive properties: width, height, left, top
- Use CSS transforms instead of position changes

### Scroll Performance (60fps)

- Use virtual scrolling for large lists
- Apply `will-change: transform` to animated elements
- Use passive event listeners: `addEventListener('scroll', fn, { passive: true })`

### Bundle Size

- Tree-shake unused features for mobile
- Lazy-load heavy components
- Code split by route
- Use conditional imports

## Common Patterns

### Mobile-only/Desktop-only Content

```tsx
// Show only on mobile (< 768px)
<div className="md:hidden">
  {/* Mobile content */}
</div>

// Show only on desktop (≥ 768px)
<div className="hidden md:block">
  {/* Desktop content */}
</div>
```

### Responsive Grid

```tsx
<div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4'>
  {/* Items automatically adjust */}
</div>
```

### Touch-friendly Form

```tsx
<form className='space-y-4'>
  <input
    type='text'
    className='w-full px-4 py-3 min-h-[44px] rounded-lg border border-border'
    placeholder='Full-width, 44px height'
  />

  <select className='w-full px-4 py-3 min-h-[44px] rounded-lg border border-border'>
    <option>Option 1</option>
    <option>Option 2</option>
  </select>
</form>
```

## Testing

### Unit Tests

```bash
bun run test -- mobile/
```

### E2E Tests

```bash
bun run test:e2e -- mobile-optimization.spec.ts
```

### Visual Tests

```bash
bun run test:visual -- --project=mobile-iphone
```

### Performance Tests

```bash
# Lighthouse mobile
npx lighthouse https://your-site.com --form-factor=mobile
```

## Debugging

### Enable Touch Target Debugging

```typescript
// In development tools or console
import {
  auditTouchTargets,
  highlightTouchTargetIssues,
  logTouchTargetAudit,
} from '@/lib/touch-target-audit';

const issues = auditTouchTargets();
logTouchTargetAudit(issues);
highlightTouchTargetIssues(issues); // Shows red outlines
```

### Check Viewport

```tsx
// DevTools > Device emulation or
<meta name='viewport' content='width=device-width, initial-scale=1' />
```

## Migration Guide

### From Table to Card View

**Before:**

```tsx
<Table>
  <TableRow>
    <TableCell>{item.title}</TableCell>
    {/* More cells */}
  </TableRow>
</Table>
```

**After:**

```tsx
const cardItems = items.map((item) => ({
  id: item.id,
  title: item.title,
  // ... other properties
}));

<ResponsiveCardView items={cardItems} />;
```

### From Dropdown to Mobile Picker

**Before:**

```tsx
<Select value={selected} onValueChange={setSelected}>
  <SelectItem>Option 1</SelectItem>
</Select>
```

**After:**

```tsx
<MobilePicker isOpen={isOpen} options={options} selectedValue={selected} onSelect={setSelected} />
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Touch Target Guidelines](https://web.dev/accessible-tap-targets/)
- [Mobile Best Practices](https://web.dev/mobile/)
- [Complete Documentation](./MOBILE_OPTIMIZATION.md)

## Support

For issues or questions:

1. Check the [complete documentation](./MOBILE_OPTIMIZATION.md)
2. Review component examples
3. Run touch target audit
4. Check E2E tests for patterns

---

**Version:** 1.0
**Status:** Production Ready
**Last Updated:** January 30, 2026
