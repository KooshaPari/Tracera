# Fumadocs Performance Testing Guide

Complete guide for running performance tests and validating the documentation site.

---

## Quick Start

```bash
# Install dependencies
bun install

# Run all tests
bun run test:all

# Or run individually
bun run test:performance  # Bundle size & build time
bun run lighthouse        # Lighthouse CI audit
bun run test:e2e         # E2E tests
```

---

## Performance Testing

### 1. Bundle Size Analysis

Analyze the production bundle to ensure it meets size targets.

```bash
# Run performance audit
bun run test:performance
```

**What it checks**:

- Total bundle size (target: <200KB gzipped)
- JavaScript bundle size
- CSS bundle size
- Image assets size
- Build time (target: <60s)
- Largest chunks and optimization opportunities

**Expected output**:

```
📈 Performance Metrics
==================================================

⏱️  Build Time: 45.23s
   ✅ Target: <60s

📦 Bundle Sizes:
   Total:  152.34 KB
   JS:     128.67 KB
   CSS:    18.45 KB
   Images: 5.22 KB

   Estimated gzipped: 45.70 KB
   ✅ Target: <200KB gzipped
```

### 2. Bundle Analyzer (Visual)

For detailed visual analysis of what's in your bundle:

```bash
# Analyze bundle composition
ANALYZE=true bun run build
```

This will:

1. Build the production bundle
2. Generate an interactive treemap
3. Open in your browser automatically

**Look for**:

- Duplicate dependencies
- Unexpectedly large packages
- Unused code that can be removed
- Opportunities for code splitting

---

## Lighthouse Testing

### Running Lighthouse CI

```bash
# Run Lighthouse audit
bun run lighthouse
```

**What it checks**:

- Performance score (target: >95)
- Accessibility score (target: >95)
- Best Practices score (target: >90)
- SEO score (target: >90)
- Core Web Vitals:
  - FCP: First Contentful Paint (<1.5s)
  - LCP: Largest Contentful Paint (<2.5s)
  - TTI: Time to Interactive (<2.5s)
  - TBT: Total Blocking Time (<200ms)
  - CLS: Cumulative Layout Shift (<0.1)

### Configuration

Edit `lighthouserc.json` to customize:

```json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3001/", "..."],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.95 }]
      }
    }
  }
}
```

### Interpreting Results

**Performance Score Breakdown**:

- 90-100: Excellent
- 50-89: Needs improvement
- 0-49: Poor

**If tests fail**:

1. Check which metric failed
2. Review Lighthouse report for specific recommendations
3. Apply optimizations
4. Re-run tests

---

## E2E Testing

### Running E2E Tests

```bash
# Run all E2E tests
bun run test:e2e

# Run in UI mode (interactive)
bun run test:e2e:ui

# Run in debug mode (step through)
bun run test:e2e:debug

# Run specific test file
bun run test:e2e e2e/docs.spec.ts

# Run specific test
bun run test:e2e -g "should open search dialog"
```

### Test Suites

**1. Navigation Tests**

- Homepage loads correctly
- Navigation to docs works
- Sidebar navigation works
- Breadcrumb navigation displays

**2. Search Functionality Tests**

- Search dialog opens with keyboard shortcut (Cmd/Ctrl+K)
- Search returns results quickly (<100ms)
- Search results are clickable and navigate correctly
- Search works with keyboard navigation

**3. OpenAPI Documentation Tests**

- API reference page loads
- API endpoints display correctly
- Operations can be expanded/collapsed
- Request/response schemas render

**4. Dark Mode Tests**

- Theme toggle works
- Theme persists across page reloads
- All pages render correctly in both themes

**5. Performance Tests**

- Page load time <3s
- No layout shifts (CLS <0.1)
- Time to Interactive <2.5s

**6. Accessibility Tests**

- No automatic a11y violations
- Keyboard navigation works
- Proper heading hierarchy
- Skip to content link exists

**7. Mobile Responsiveness Tests**

- Mobile layout renders correctly
- Mobile menu works
- Touch targets are adequate

### Test Configuration

Edit `playwright.config.ts` to customize:

```typescript
export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:3001',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

### Viewing Test Reports

After running tests:

```bash
# Open HTML report
bunx playwright show-report

# Or check the playwright-report/ directory
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: bun install

      - name: Run performance tests
        run: bun run test:performance

      - name: Run Lighthouse CI
        run: bun run lighthouse
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

      - name: Install Playwright browsers
        run: bunx playwright install --with-deps

      - name: Run E2E tests
        run: bun run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            playwright-report/
            .lighthouseci/
```

---

## Troubleshooting

### Common Issues

**1. Lighthouse fails to start server**

```bash
# Solution: Make sure port 3001 is free
lsof -ti:3001 | xargs kill -9

# Then retry
bun run lighthouse
```

**2. E2E tests timeout**

```bash
# Solution: Increase timeout in playwright.config.ts
timeout: 60000, // 60 seconds
```

**3. Bundle size exceeds target**

```bash
# Solution: Analyze bundle
ANALYZE=true bun run build

# Look for:
# - Duplicate packages
# - Large dependencies that can be lazy-loaded
# - Unused code that can be removed
```

**4. Performance score too low**

Check Lighthouse report for specific issues:

- Render-blocking resources
- Unused JavaScript
- Unoptimized images
- Long tasks blocking main thread

**5. Search tests failing**

```bash
# Solution: Check if search is properly configured
# Verify that Fumadocs search is set up in source.config.ts
```

---

## Performance Optimization Checklist

### Before Production

- [ ] Run `bun run test:performance` - all checks pass
- [ ] Run `bun run lighthouse` - all scores >90
- [ ] Run `bun run test:e2e` - all tests pass
- [ ] Check bundle analyzer for optimization opportunities
- [ ] Test on real devices (mobile + desktop)
- [ ] Test on slow network (3G)
- [ ] Verify search works and is fast
- [ ] Verify dark mode works correctly
- [ ] Check all documentation pages load quickly
- [ ] Verify API reference renders correctly

### Performance Targets

| Metric      | Target         | How to Check               |
| ----------- | -------------- | -------------------------- |
| Bundle Size | <200KB gzipped | `bun run test:performance` |
| FCP         | <1.5s          | `bun run lighthouse`       |
| LCP         | <2.5s          | `bun run lighthouse`       |
| TTI         | <2.5s          | `bun run lighthouse`       |
| TBT         | <200ms         | `bun run lighthouse`       |
| CLS         | <0.1           | `bun run lighthouse`       |
| Search      | <100ms         | `bun run test:e2e`         |
| Build Time  | <60s           | `bun run test:performance` |
| Lighthouse  | >95            | `bun run lighthouse`       |

---

## Additional Resources

- [Lighthouse Documentation](https://developer.chrome.com/docs/lighthouse)
- [Playwright Documentation](https://playwright.dev)
- [Next.js Performance](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Fumadocs Documentation](https://fumadocs.vercel.app)
- [Web Vitals](https://web.dev/vitals/)

---

## Support

If you encounter issues:

1. Check this guide for troubleshooting steps
2. Review test output for specific errors
3. Check Lighthouse report for recommendations
4. Review Playwright trace for E2E failures
5. Open an issue with:
   - Test output
   - Error messages
   - Environment details (OS, Node version, etc.)
