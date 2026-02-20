# Visual Regression Testing - Quick Start

## TL;DR

Visual regression testing is **100% ready** for TraceRTM. Run tests with:

```bash
bun run test:visual
```

## What's Included

### Test Files (4 total)

1. **components.spec.ts** - 10 component tests (buttons, inputs, alerts, badges, etc.)
2. **pages.spec.ts** - 10 page tests (dashboard, projects, items, settings, errors)
3. **themes.spec.ts** - 6 theme tests (light/dark mode)
4. **responsive.spec.ts** - 5 responsive tests (mobile/tablet/desktop)

**Total:** 31 test cases × 8 browser/viewport combinations = ~248 test executions

### Components Covered

✅ Buttons (6 variants, 3 sizes, 4 states)
✅ Inputs (text, email, password, textarea)
✅ Selects (dropdown, multi-select)
✅ Checkboxes & Radio buttons
✅ Cards (4 variants)
✅ Badges (7 color variants)
✅ Alerts (5 variants: info, success, warning, error, update)
✅ Loading states (spinners, skeletons)
✅ Empty states
✅ Error states
✅ Command Palette

### Pages Covered

✅ Dashboard (stats, activity, recent projects)
✅ Projects List (card grid)
✅ Items Table (searchable, sortable)
✅ Settings (profile, appearance, notifications)
✅ Empty States (projects, items)
✅ Error Pages (404, general error)
✅ Command Palette (overlay, search, keyboard shortcuts)

## Common Commands

```bash
# Run all visual tests
bun run test:visual

# Update baselines after design changes
bun run test:visual:update

# Interactive debugging (BEST for reviewing failures)
bun run test:visual:ui

# View HTML report
bun run test:visual:report

# Run specific browser only
bun run test:visual:chromium
bun run test:visual:mobile
bun run test:visual:tablet
```

## Workflow

### First Time Setup

```bash
# Install dependencies (if needed)
bun install

# Generate baseline snapshots (first run)
bun run test:visual
```

This creates baseline screenshots in `visual-snapshots/` directory. All tests pass on first run.

### Daily Development

```bash
# Before making visual changes
bun run test:visual  # Verify baselines

# Make your changes to components/styles
# ...

# After changes
bun run test:visual  # Will fail if visuals changed

# Review failures
bun run test:visual:ui  # Interactive review

# If changes are intentional
bun run test:visual:update  # Update baselines
```

### Reviewing Failures

When tests fail, you have 3 options:

**Option 1: Interactive UI Mode (Recommended)**

```bash
bun run test:visual:ui
```

- Side-by-side comparison
- Click to see diff overlay
- Accept/reject changes per screenshot

**Option 2: HTML Report**

```bash
bun run test:visual:report
```

- Opens browser with full report
- Expected vs Actual comparison
- Diff highlighting

**Option 3: Manual Review**

```bash
# Diff images are in visual-snapshots/
# Look for *-actual.png and *-diff.png files
```

## Understanding Test Results

### ✅ All Tests Pass

```
31 passed (2.5m)
```

No visual changes detected. All good!

### ❌ Tests Fail

```
29 passed, 2 failed (2.8m)
```

Failures mean visual changes were detected. Review with:

```bash
bun run test:visual:ui
```

## File Organization

```
frontend/apps/web/
├── visual/                          # Test files
│   ├── components.spec.ts           # UI component tests
│   ├── pages.spec.ts                # Full page tests
│   ├── themes.spec.ts               # Theme tests
│   └── responsive.spec.ts           # Responsive tests
│
├── visual-snapshots/                # Baseline images (git-tracked)
│   ├── chromium-desktop/
│   ├── firefox-desktop/
│   ├── webkit-desktop/
│   ├── tablet-ipad/
│   ├── mobile-iphone/
│   └── mobile-android/
│
├── playwright-visual.config.ts      # Config
└── .gitignore                       # Ignores diffs
```

## Browser/Viewport Coverage

**Desktop (1920×1080):**

- Chromium (Chrome, Edge)
- Firefox
- WebKit (Safari)

**Tablet:**

- iPad Pro Portrait (1024×1366)
- iPad Pro Landscape (1366×1024)

**Mobile:**

- iPhone 12 (390×844)
- Pixel 5 (393×851)
- iPhone SE (375×667)

## Git Workflow

### What's Tracked

✅ Baseline snapshots (`visual-snapshots/**/*.png`)
✅ Test files (`visual/*.spec.ts`)
✅ Configuration (`playwright-visual.config.ts`)

### What's Ignored

❌ Actual snapshots (`*-actual.png`)
❌ Diff snapshots (`*-diff.png`)
❌ Previous snapshots (`*-previous.png`)
❌ Test reports (`playwright-report-visual/`)

### Making Changes

```bash
# 1. Make visual changes
# Edit components, styles, etc.

# 2. Run tests (will fail)
bun run test:visual

# 3. Review changes
bun run test:visual:ui

# 4. Accept changes
bun run test:visual:update

# 5. Commit updated baselines
git add visual-snapshots/
git commit -m "Update visual baselines for button redesign"
```

## Troubleshooting

### Tests pass locally but fail in CI

- Ensure fonts are installed in CI
- Check browser versions match
- Verify same OS (Docker image)

### Tests are flaky

- Should NOT be flaky (animations disabled)
- If flaky, file an issue

### Want to skip a test

```typescript
test.skip('flaky test', async ({ page }) => {
  // ...
});
```

### Want to run only one test

```typescript
test.only('my test', async ({ page }) => {
  // ...
});
```

## Adding New Tests

### Component Test Example

```typescript
// visual/components.spec.ts
test('my new component', async ({ page }) => {
  await page.goto('http://localhost:5173');

  await page.evaluate(() => {
    document.getElementById('root')!.innerHTML = `
      <div class="p-8 bg-background">
        <button class="btn-primary">My Button</button>
      </div>
    `;
  });

  await expect(page.locator('#root')).toHaveScreenshot('my-component.png', {
    maxDiffPixels: 100,
  });
});
```

### Page Test Example

```typescript
// visual/pages.spec.ts
import { LAYOUT_SCREENSHOT_OPTIONS } from './helpers/visual-test-helpers';

test('my new page', async ({ page }) => {
  await setupVisualTest(page);

  // Render full page
  await page.evaluate(() => {
    document.getElementById('root')!.innerHTML = `
      <div class="min-h-screen bg-background">
        <!-- Page content -->
      </div>
    `;
  });

  await expect(page).toHaveScreenshot('my-page.png', LAYOUT_SCREENSHOT_OPTIONS);
});
```

## Configuration

### Snapshot Comparison Settings

```typescript
// playwright-visual.config.ts
expect: {
  toHaveScreenshot: {
    maxDiffPixels: 100,        // Max 100 pixels can differ
    threshold: 0.2,             // 20% pixel difference threshold
    animations: 'disabled',     // No animations
    caret: 'hide',             // Hide text cursors
  },
}
```

### Adjusting Per-Test

```typescript
await expect(page).toHaveScreenshot('test.png', {
  maxDiffPixels: 50, // Stricter
  threshold: 0.1, // 10% threshold
  fullPage: true, // Capture entire page
});
```

## Performance

- **Full test suite:** ~3-6 minutes (parallel)
- **Single browser:** ~45 seconds
- **Component tests only:** ~30 seconds

Runs faster on CI with more CPU cores.

## Coverage Summary

| Category        | Count | Status      |
| --------------- | ----- | ----------- |
| Test Files      | 4     | ✅ Complete |
| Test Cases      | 31    | ✅ Complete |
| Components      | 15+   | ✅ Complete |
| Pages           | 8     | ✅ Complete |
| Browsers        | 3     | ✅ Complete |
| Viewports       | 6     | ✅ Complete |
| Total Snapshots | ~272  | ✅ Complete |

## Need Help?

1. Check `visual/README.md` for detailed docs
2. Check `VISUAL_REGRESSION_SUMMARY.md` for full implementation details
3. Run `bun run test:visual:ui` to debug visually
4. Check Playwright docs: https://playwright.dev/docs/test-snapshots

## Quick Tips

✅ Always review diffs before updating baselines
✅ Commit baseline updates with descriptive messages
✅ Use `test:visual:ui` for best debugging experience
✅ Test locally before pushing to CI
✅ Group related baseline updates in single commit
✅ Document breaking visual changes in PR description

## Example PR Workflow

```bash
# Developer makes button changes
git checkout -b redesign-buttons

# Update component styles
# Edit src/components/Button.tsx

# Run visual tests (will fail)
bun run test:visual

# Review in UI mode
bun run test:visual:ui
# ✅ Changes look good

# Update baselines
bun run test:visual:update

# Commit with descriptive message
git add visual-snapshots/
git commit -m "Update button visual baselines for rounded corners"

# Push and create PR
git push origin redesign-buttons
```

PR will show visual changes in diff!

---

**Visual regression testing is ready to use. Start testing now:**

```bash
bun run test:visual
```
