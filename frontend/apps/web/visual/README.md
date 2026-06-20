# Visual Regression Testing - TraceRTM

Comprehensive visual regression testing suite for TraceRTM frontend using Playwright.

## Overview

This test suite ensures visual consistency across:

- **Components**: Buttons, inputs, cards, badges, forms
- **Themes**: Light and dark mode consistency
- **Responsive**: Mobile, tablet, and desktop layouts
- **Browsers**: Chromium, Firefox, WebKit

## Test Structure

```
visual/
├── components.spec.ts    # Core UI component screenshots
├── pages.spec.ts         # Full page layout screenshots
├── themes.spec.ts        # Light/dark theme consistency
├── responsive.spec.ts    # Mobile/tablet/desktop layouts
├── helpers/
│   └── visual-test-helpers.ts  # Reusable test utilities
└── README.md
```

## Running Tests

### All Visual Tests

```bash
bun run test:visual
```

### Update Baselines

```bash
bun run test:visual:update
```

### Specific Test File

```bash
bun run test:visual -- components.spec.ts
```

### UI Mode (Interactive)

```bash
bun run test:visual:ui
```

### Specific Browser/Viewport

```bash
bun run test:visual -- --project=chromium-desktop
bun run test:visual -- --project=mobile-iphone
bun run test:visual -- --project=tablet-ipad
```

## Screenshot Organization

Baseline screenshots are stored in `visual-snapshots/` with the following structure:

```
visual-snapshots/
├── chromium-desktop/
│   ├── components.spec.ts/
│   │   ├── buttons-variants.png
│   │   ├── inputs-variants.png
│   │   └── cards-variants.png
│   ├── themes.spec.ts/
│   │   ├── theme-light-full.png
│   │   └── theme-dark-full.png
│   └── responsive.spec.ts/
│       └── desktop-layout.png
├── firefox-desktop/
├── webkit-desktop/
├── tablet-ipad/
├── mobile-iphone/
└── mobile-android/
```

## Test Categories

### 1. Component Tests (`components.spec.ts`)

Tests visual consistency of individual UI components:

- **Button States**: Default, hover, disabled, loading
- **Button Variants**: Primary, destructive, outline, secondary, ghost, link
- **Button Sizes**: Small, default, large, icon
- **Input States**: Default, filled, disabled, error
- **Form Elements**: Text inputs, selects, textareas, checkboxes, radio buttons
- **Cards**: Standard, with actions, hoverable, selected
- **Badges**: All color variants, with icons
- **Alerts**: Info, success, warning, error, with actions
- **Loading States**: Spinners, skeletons
- **Empty States**: No data placeholders

**Key Tests:**

- ✅ All button variants render correctly
- ✅ Hover states are visually distinct
- ✅ Disabled states have reduced opacity
- ✅ Form inputs have consistent styling
- ✅ Cards maintain shadow and border consistency
- ✅ Alert variants display appropriate colors
- ✅ Checkboxes and radio buttons show correct states

### 2. Page Tests (`pages.spec.ts`)

Tests complete page layouts and user journeys:

- **Dashboard Page**: Stats cards, activity timeline, recent projects
- **Projects List**: Project cards with metadata and actions
- **Items Table**: Searchable table with type and status badges
- **Settings Page**: Profile, appearance, and notification settings
- **Empty States**: Empty projects, empty items
- **Error States**: 404 page, general error state
- **Command Palette**: Open state with search and results

**Key Tests:**

- ✅ Dashboard displays stats and activity correctly
- ✅ Project cards show all metadata
- ✅ Items table renders with proper formatting
- ✅ Settings forms are properly laid out
- ✅ Empty states are centered and actionable
- ✅ Error pages provide helpful recovery options
- ✅ Command palette overlay and keyboard shortcuts display

### 3. Theme Tests (`themes.spec.ts`)

Tests light/dark mode consistency:

- **Full Page Themes**: Complete page in light and dark mode
- **Theme Toggle**: Animation between themes
- **Color Palette**: All semantic colors rendered correctly
- **Typography**: Font sizes and colors in both themes
- **Accessibility**: Focus states visible in both themes

**Key Tests:**

- ✅ Light theme uses correct color palette
- ✅ Dark theme uses correct color palette
- ✅ Theme toggle transitions smoothly
- ✅ Focus rings visible in both themes
- ✅ Text contrast meets accessibility standards

### 4. Responsive Tests (`responsive.spec.ts`)

Tests layouts across different viewport sizes:

- **Mobile Layout**: Single column, bottom navigation
- **Mobile Forms**: Stack vertically, full-width buttons
- **Tablet Layout**: 2-column grids, side navigation
- **Desktop Layout**: Sidebar + main content, multi-column grids
- **Breakpoint Transitions**: Smooth layout changes at breakpoints

**Viewports Tested:**

- Mobile Small: 375×667 (iPhone SE)
- Mobile Large: 428×926 (iPhone 12)
- Tablet: 768×1024 (iPad)
- Desktop: 1280×800
- Desktop Large: 1920×1080

**Key Tests:**

- ✅ Mobile shows single-column layout
- ✅ Tablet shows 2-column grid
- ✅ Desktop shows sidebar navigation
- ✅ Buttons stack on mobile, inline on desktop
- ✅ Typography scales appropriately

## Visual Regression Thresholds

Default thresholds for different test types:

| Test Type  | Max Diff Pixels | Threshold % |
| ---------- | --------------- | ----------- |
| Components | 100             | 20%         |
| Themes     | 150             | 25%         |
| Layouts    | 200             | 30%         |

These can be adjusted per-test using:

```typescript
await expect(page).toHaveScreenshot('test.png', {
  maxDiffPixels: 50,
  threshold: 0.1,
});
```

## Writing New Visual Tests

### Basic Component Test

```typescript
import { test, expect } from '@playwright/test';
import { setupVisualTest } from './helpers/visual-test-helpers';

test('my component visual test', async ({ page }) => {
  await setupVisualTest(page);

  await page.evaluate(() => {
    document.getElementById('root')!.innerHTML = `
      <div class="p-8">
        <button class="bg-primary text-primary-foreground px-4 py-2 rounded">
          My Button
        </button>
      </div>
    `;
  });

  await expect(page.locator('#root')).toHaveScreenshot('my-component.png');
});
```

### Theme Test

```typescript
import { test, expect } from '@playwright/test';
import { setupVisualTest, setTheme, testAllThemes } from './helpers/visual-test-helpers';

test('component in both themes', async ({ page }) => {
  await setupVisualTest(page);

  await testAllThemes(page, async (theme) => {
    await page.evaluate(() => {
      document.getElementById('root')!.innerHTML = `<div class="bg-background p-8">Content</div>`;
    });

    await expect(page).toHaveScreenshot(`component-${theme}.png`);
  });
});
```

### Responsive Test

```typescript
import { test, expect, devices } from '@playwright/test';
import { setupVisualTest } from './helpers/visual-test-helpers';

test.use({ ...devices['iPhone 12'] });

test('mobile responsive layout', async ({ page }) => {
  await setupVisualTest(page);

  await page.evaluate(() => {
    document.getElementById('root')!.innerHTML = `
      <div class="p-4">Mobile layout</div>
    `;
  });

  await expect(page).toHaveScreenshot('mobile.png', { fullPage: true });
});
```

## Best Practices

### 1. Disable Animations

Always disable animations for consistent screenshots:

```typescript
import { disableAnimations } from './helpers/visual-test-helpers';

await disableAnimations(page);
```

### 2. Wait for Fonts

Ensure fonts are loaded before screenshots:

```typescript
import { waitForFonts } from './helpers/visual-test-helpers';

await waitForFonts(page);
```

### 3. Hide Flakey Elements

Hide time-based or dynamic content:

```typescript
import { hideFlakeyElements } from './helpers/visual-test-helpers';

await hideFlakeyElements(page, ['.timestamp', '.live-indicator']);
```

### 4. Mock Time

For consistent timestamp displays:

```typescript
import { mockTime } from './helpers/visual-test-helpers';

await mockTime(page, new Date('2025-01-01T12:00:00Z'));
```

### 5. Use Stable Selectors

Use semantic selectors for better test maintenance:

```typescript
// ✅ Good
await expect(page.locator('[data-testid="primary-button"]')).toHaveScreenshot();

// ❌ Avoid
await expect(page.locator('.css-xyz123')).toHaveScreenshot();
```

## Troubleshooting

### Tests Failing After Design Changes

If legitimate design changes cause failures:

1. Review the visual diff in the HTML report
2. If correct, update baselines:
   ```bash
   bun run test:visual:update
   ```

### Flaky Visual Tests

Common causes and solutions:

| Issue            | Solution                                 |
| ---------------- | ---------------------------------------- |
| Animations       | Use `disableAnimations()`                |
| Fonts not loaded | Use `waitForFonts()`                     |
| Timestamps       | Use `mockTime()`                         |
| Hover states     | Use explicit `hover()` before screenshot |
| Layout shifts    | Use `waitForStableElement()`             |

### CI/CD Failures

If tests pass locally but fail in CI:

1. Check font availability in CI environment
2. Verify viewport size consistency
3. Ensure animations are disabled
4. Check for timezone-dependent content

## Configuration

Visual test configuration is in `playwright-visual.config.ts`:

```typescript
export default defineConfig({
  testDir: './visual',
  snapshotDir: './visual-snapshots',

  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100,
      threshold: 0.2,
      animations: 'disabled',
    },
  },

  projects: [
    { name: 'chromium-desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-iphone', use: { ...devices['iPhone 12'] } },
    // ... more projects
  ],
});
```

## Coverage Goals

Target coverage for visual regression:

- ✅ 100% of UI components in `packages/ui/`
- ✅ All theme color variants
- ✅ All responsive breakpoints (mobile, tablet, desktop)
- ✅ Button, input, card, badge, form states
- ✅ Light and dark themes for all components

## Related Documentation

- [Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [TraceRTM Component Library](../packages/ui/README.md)
- [TraceRTM Testing Strategy](../README_TESTING.md)

## Support

For questions or issues with visual testing:

1. Check the troubleshooting section above
2. Review Playwright's visual testing docs
3. Check existing test examples in this directory
