# Fumadocs Phase 8: Performance Testing - Quick Reference

## Overview

Phase 8 implements comprehensive performance testing and validation for the Fumadocs documentation site.

---

## Test Execution

### Quick Start

```bash
# Navigate to docs directory
cd frontend/apps/docs

# Install dependencies (if not already done)
bun install

# Run all tests
bun run test:all
```

### Individual Test Suites

```bash
# Performance audit (bundle size + build time)
bun run test:performance

# Lighthouse CI (Core Web Vitals)
bun run lighthouse

# E2E tests (functionality + performance)
bun run test:e2e

# Bundle analysis (visual treemap)
bun run audit:bundle
```

---

## Success Criteria

| Metric                 | Target | Test Command               |
| ---------------------- | ------ | -------------------------- |
| Bundle Size (gzipped)  | <200KB | `bun run test:performance` |
| First Contentful Paint | <1.5s  | `bun run lighthouse`       |
| Time to Interactive    | <2.5s  | `bun run lighthouse`       |
| Search Response        | <100ms | `bun run test:e2e`         |
| Lighthouse Score       | >95    | `bun run lighthouse`       |
| Build Time             | <60s   | `bun run test:performance` |

---

## Key Files

### Test Configuration

| File                           | Purpose                     |
| ------------------------------ | --------------------------- |
| `lighthouserc.json`            | Lighthouse CI configuration |
| `playwright.config.ts`         | E2E test configuration      |
| `e2e/docs.spec.ts`             | E2E test suite              |
| `scripts/performance-audit.ts` | Performance audit script    |

### Documentation

| File                         | Purpose                     |
| ---------------------------- | --------------------------- |
| `TESTING_GUIDE.md`           | Complete testing guide      |
| `PERFORMANCE_REPORT.md`      | Performance report template |
| `PHASE_8_QUICK_REFERENCE.md` | This file                   |

---

## Common Commands

```bash
# Run E2E tests in UI mode (interactive debugging)
bun run test:e2e:ui

# Run E2E tests in debug mode (step through)
bun run test:e2e:debug

# Run specific E2E test
bun run test:e2e -g "should open search dialog"

# Install Playwright browsers
bunx playwright install

# View test reports
bunx playwright show-report
```

---

## Test Suites Overview

### 1. Performance Audit (`test:performance`)

**What it tests**:

- Build time
- Bundle sizes (JS, CSS, images)
- Chunk analysis

**Output**:

```
📈 Performance Metrics
⏱️  Build Time: 45.23s ✅
📦 Bundle Sizes:
   Total:  152.34 KB
   Estimated gzipped: 45.70 KB ✅
```

### 2. Lighthouse CI (`lighthouse`)

**What it tests**:

- Performance score
- Accessibility score
- Best Practices score
- SEO score
- Core Web Vitals (FCP, LCP, TTI, TBT, CLS)

**Output**:

- `.lighthouseci/` directory with reports
- Console summary of scores

### 3. E2E Tests (`test:e2e`)

**Test Categories**:

- ✅ Navigation (homepage, docs, sidebar)
- ✅ Search functionality (keyboard shortcuts, results)
- ✅ OpenAPI documentation (rendering, expansion)
- ✅ Dark mode (toggle, persistence)
- ✅ Performance (load time, CLS, TTI)
- ✅ Accessibility (keyboard nav, a11y violations)
- ✅ Mobile responsiveness (layout, menu)

**Output**:

- `playwright-report/` directory with HTML report
- `playwright-results.json` with test results

---

## Troubleshooting

### Issue: Lighthouse fails to start server

```bash
# Kill any process on port 3001
lsof -ti:3001 | xargs kill -9

# Retry
bun run lighthouse
```

### Issue: E2E tests timeout

Edit `playwright.config.ts`:

```typescript
timeout: 60000, // Increase to 60 seconds
```

### Issue: Bundle size too large

```bash
# Analyze bundle visually
bun run audit:bundle

# Look for:
# - Duplicate packages
# - Large dependencies to lazy-load
# - Unused code to remove
```

### Issue: Search tests fail

Check `source.config.ts` for proper search configuration.

---

## Performance Optimization Tips

### Reduce Bundle Size

1. **Lazy load components**:

   ```typescript
   const HeavyComponent = lazy(() => import('./HeavyComponent'));
   ```

2. **Use dynamic imports**:

   ```typescript
   const module = await import('./module');
   ```

3. **Tree shake unused code**:
   - Check bundle analyzer for unused exports
   - Remove unused dependencies

### Improve Core Web Vitals

1. **Reduce FCP**:
   - Minimize render-blocking resources
   - Inline critical CSS
   - Preload important fonts

2. **Reduce LCP**:
   - Optimize images (WebP, lazy loading)
   - Reduce server response time
   - Eliminate render-blocking resources

3. **Reduce TBT**:
   - Split long tasks
   - Defer non-critical JavaScript
   - Use web workers for heavy computation

4. **Reduce CLS**:
   - Set explicit dimensions for images
   - Reserve space for dynamic content
   - Avoid inserting content above existing content

---

## CI/CD Integration

Tests run automatically on:

- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Workflow**: `.github/workflows/docs-performance.yml`

**Artifacts**:

- Playwright report
- Lighthouse results
- Bundle analysis

---

## Next Steps After Phase 8

Once all tests pass:

1. ✅ Generate final performance report
2. ✅ Capture screenshots for documentation
3. ✅ Update `PERFORMANCE_REPORT.md` with actual metrics
4. ✅ Create production deployment plan
5. ✅ Set up performance monitoring
6. ✅ Deploy to production

---

## Resources

- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Complete testing guide
- [PERFORMANCE_REPORT.md](./PERFORMANCE_REPORT.md) - Report template
- [Lighthouse Docs](https://developer.chrome.com/docs/lighthouse)
- [Playwright Docs](https://playwright.dev)
- [Web Vitals](https://web.dev/vitals/)

---

**Phase 8 Status**: ✅ IMPLEMENTATION COMPLETE
**Next Phase**: Production Deployment
