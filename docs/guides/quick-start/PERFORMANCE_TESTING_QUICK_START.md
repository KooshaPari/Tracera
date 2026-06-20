# Performance Testing Quick Start

## TL;DR

```bash
cd frontend

# Run all performance tests
bun scripts/run-all-performance-tests.ts

# View results
cat PERFORMANCE_TEST_REPORT.md
```

## Individual Test Commands

```bash
# 1. Validate optimizations are in place
bun scripts/validate-optimizations.ts

# 2. Test build performance (all apps)
bun scripts/test-build-performance.ts

# 3. Test runtime performance
bun scripts/test-runtime-performance.ts

# 4. Run unit tests
bun test

# 5. Run E2E tests
cd apps/web
bun run test:e2e

# 6. Run only performance E2E tests
bun run test:e2e performance.spec.ts
```

## Quick Health Check

```bash
# Fast validation (30 seconds)
bun scripts/validate-optimizations.ts
```

## What Gets Tested

### Build Performance

- ✅ Build times for web, docs, storybook
- ✅ Bundle sizes and chunk counts
- ✅ Build success rate
- ✅ Targets: Web < 15s, Full < 45s

### Runtime Performance

- ✅ Dev server startup (< 3s)
- ✅ node_modules size (< 400MB)
- ✅ HMR configuration
- ✅ Build optimizations

### Code Quality

- ✅ Virtual scrolling implemented
- ✅ Memoization in place
- ✅ Lazy loading active
- ✅ SWC compiler enabled

### End-to-End Performance

- ✅ Core Web Vitals (FCP, LCP, TTI)
- ✅ Page load times
- ✅ Frame rate (60fps)
- ✅ Memory leak detection
- ✅ Bundle size optimization

## Performance Targets

| Metric       | Target  | Critical        |
| ------------ | ------- | --------------- |
| Dev startup  | < 3s    | ✅ Yes          |
| Web build    | < 15s   | ✅ Yes          |
| Full build   | < 45s   | ✅ Yes          |
| HMR          | < 100ms | ✅ Yes          |
| node_modules | < 400MB | ⚠️ Nice-to-have |
| FCP          | < 1.8s  | ✅ Yes          |
| LCP          | < 2.5s  | ✅ Yes          |
| TTI          | < 3.8s  | ✅ Yes          |

## Generated Reports

After running tests, you'll find:

```
frontend/
├── build-performance-results.json       # Build metrics
├── runtime-performance-results.json     # Runtime metrics
├── optimization-validation-results.json # Validation checks
├── performance-test-summary.json        # Overall summary
└── PERFORMANCE_TEST_REPORT.md          # Markdown report
```

## CI/CD Integration

Add to `.github/workflows/frontend.yml`:

```yaml
- name: Performance Tests
  run: |
    cd frontend
    bun scripts/run-all-performance-tests.ts
```

## Troubleshooting

### Build too slow?

```bash
# Clear cache and rebuild
bun run clean
bun install
bun run build
```

### Dev server slow?

```bash
# Clear Vite cache
rm -rf apps/web/node_modules/.vite
```

### Tests failing?

```bash
# Check generated reports
cat performance-test-summary.json
cat PERFORMANCE_TEST_REPORT.md
```

## Next Steps

1. Run tests: `bun scripts/run-all-performance-tests.ts`
2. Review report: `PERFORMANCE_TEST_REPORT.md`
3. Fix any critical failures
4. Commit changes
5. Set up CI/CD automation

## Support

For detailed documentation, see:

- `FRONTEND_OPTIMIZATION_GUIDE.md` - Full guide
- `apps/web/e2e/performance.spec.ts` - E2E test details
- Individual script files for implementation details
