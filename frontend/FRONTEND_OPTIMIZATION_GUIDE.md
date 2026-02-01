# Frontend Optimization Testing & Validation Guide

This guide documents the comprehensive performance testing and validation infrastructure for TracerTM's frontend.

## Overview

The frontend has been optimized for maximum performance with the following targets:
- Dev server startup: < 3s
- Web app build: < 15s
- Full monorepo build: < 45s
- HMR (Hot Module Replacement): < 100ms
- node_modules size: < 400MB
- All tests passing

## Test Suites

### 1. Build Performance Tests

**Location:** `/frontend/scripts/test-build-performance.ts`

Tests all apps build successfully and measures performance:
- Build times for each app (web, docs, storybook)
- Bundle sizes and chunk counts
- Build success rate
- Overall build time

**Run:**
```bash
cd frontend
bun scripts/test-build-performance.ts
```

**Output:** `build-performance-results.json`

### 2. Runtime Performance Tests

**Location:** `/frontend/scripts/test-runtime-performance.ts`

Tests runtime performance metrics:
- Dev server startup time
- node_modules size
- HMR configuration
- Build optimizations

**Run:**
```bash
cd frontend
bun scripts/test-runtime-performance.ts
```

**Output:** `runtime-performance-results.json`

### 3. Optimization Validation

**Location:** `/frontend/scripts/validate-optimizations.ts`

Validates that all optimizations are in place:
- Package optimizations (workspaces, bun, lock file)
- Build optimizations (turbo, vite, SWC)
- Code optimizations (lazy loading, virtual scrolling, memoization)
- Test setup (vitest, playwright)
- Development experience (TypeScript, linting, scripts)

**Run:**
```bash
cd frontend
bun scripts/validate-optimizations.ts
```

**Output:** `optimization-validation-results.json`

### 4. E2E Performance Tests

**Location:** `/frontend/apps/web/e2e/performance.spec.ts`

Comprehensive E2E tests for runtime performance:
- Core Web Vitals (FCP, LCP, TTI)
- Page load times
- Bundle size optimization
- Virtual scrolling efficiency
- Frame rate (60fps target)
- Memory leak detection
- Image optimization
- CSS efficiency
- Performance regression tests

**Run:**
```bash
cd frontend/apps/web
bun run test:e2e performance.spec.ts
```

### 5. Master Test Runner

**Location:** `/frontend/scripts/run-all-performance-tests.ts`

Runs all test suites in sequence and generates a comprehensive report:

**Run:**
```bash
cd frontend
bun scripts/run-all-performance-tests.ts
```

**Output:**
- `performance-test-summary.json` - Complete results
- `PERFORMANCE_TEST_REPORT.md` - Markdown report

## Quick Start

### Run All Performance Tests

```bash
cd frontend
bun scripts/run-all-performance-tests.ts
```

This will:
1. Validate all optimizations are in place
2. Test build performance
3. Test runtime performance
4. Run unit tests
5. Run E2E tests (including performance tests)
6. Generate comprehensive report

### Run Individual Test Suites

```bash
# Validate optimizations
bun scripts/validate-optimizations.ts

# Test build performance
bun scripts/test-build-performance.ts

# Test runtime performance
bun scripts/test-runtime-performance.ts

# Run unit tests
bun test

# Run E2E tests
cd apps/web
bun run test:e2e

# Run only performance E2E tests
bun run test:e2e performance.spec.ts
```

## Performance Metrics

### Build Performance

| Metric | Target | Current |
|--------|--------|---------|
| Web app build | < 15s | ✅ Optimized |
| Full monorepo build | < 45s | ✅ Optimized |
| Dev server startup | < 3s | ✅ Optimized |

### Runtime Performance

| Metric | Target | Status |
|--------|--------|--------|
| First Contentful Paint (FCP) | < 1.8s | ✅ Tested |
| Largest Contentful Paint (LCP) | < 2.5s | ✅ Tested |
| Time to Interactive (TTI) | < 3.8s | ✅ Tested |
| Frame Rate | > 55fps | ✅ Tested |
| Memory Leaks | < 50% increase | ✅ Tested |

### Bundle Optimization

| Metric | Target | Status |
|--------|--------|--------|
| Initial bundle | < 500KB | ✅ Tested |
| node_modules | < 400MB | ✅ Tested |
| CSS rules | < 5000 | ✅ Tested |
| Image sizes | < 200KB each | ✅ Tested |

## Optimization Features

### Package Management
- ✅ Bun package manager for faster installs
- ✅ Workspaces for monorepo structure
- ✅ Pruned dependencies
- ✅ Lock file for consistency

### Build Optimizations
- ✅ Turbo for parallel builds and caching
- ✅ Vite with SWC for fast compilation
- ✅ Dependency pre-bundling
- ✅ Tree shaking and minification

### Code Optimizations
- ✅ Lazy loading for route components
- ✅ Virtual scrolling for large lists
- ✅ Memoization for expensive computations
- ✅ Code splitting for smaller bundles

### Test Infrastructure
- ✅ Vitest for unit tests
- ✅ Playwright for E2E tests
- ✅ Performance benchmarking
- ✅ Regression detection

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/frontend-tests.yml
name: Frontend Tests

on: [push, pull_request]

jobs:
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: oven-sh/setup-bun@v1
      - name: Install dependencies
        run: cd frontend && bun install
      - name: Run performance tests
        run: cd frontend && bun scripts/run-all-performance-tests.ts
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: |
            frontend/performance-test-summary.json
            frontend/PERFORMANCE_TEST_REPORT.md
```

## Troubleshooting

### Build Performance Issues

If builds are slow:
1. Check Turbo cache is enabled
2. Verify SWC is being used (not babel)
3. Clear `dist/` and `.turbo/` directories
4. Run `bun install` to ensure dependencies are fresh

### Runtime Performance Issues

If dev server is slow:
1. Check node_modules size
2. Verify HMR configuration
3. Check for circular dependencies
4. Clear Vite cache: `rm -rf apps/web/node_modules/.vite`

### Test Failures

If tests fail:
1. Review the generated JSON reports
2. Check for recent code changes
3. Ensure all dependencies are installed
4. Verify test environment matches production

## Maintenance

### Regular Checks

Run performance tests:
- Before major releases
- After dependency updates
- When adding new features
- Weekly in CI/CD

### Benchmark Updates

Update baselines when:
- Hardware changes
- Major dependency updates
- Intentional performance improvements

### Documentation Updates

Keep this guide updated when:
- Adding new test suites
- Changing performance targets
- Updating optimization strategies

## Results Interpretation

### JSON Reports

All test scripts generate JSON reports with detailed metrics:
- `build-performance-results.json` - Build times and sizes
- `runtime-performance-results.json` - Runtime metrics
- `optimization-validation-results.json` - Validation checks
- `performance-test-summary.json` - Overall summary

### Markdown Report

`PERFORMANCE_TEST_REPORT.md` provides:
- Executive summary
- Detailed results for each suite
- Success criteria validation
- Next steps and recommendations

## Best Practices

1. **Run tests locally** before pushing
2. **Review reports** after each test run
3. **Fix critical failures** immediately
4. **Monitor trends** over time
5. **Update baselines** when appropriate
6. **Document changes** that affect performance

## Support

For issues or questions:
- Check the troubleshooting section above
- Review test output and JSON reports
- Consult the main project documentation
- Open an issue with test results attached

## Quick Reference

```bash
# Full test suite
bun scripts/run-all-performance-tests.ts

# Individual tests
bun scripts/validate-optimizations.ts
bun scripts/test-build-performance.ts
bun scripts/test-runtime-performance.ts
bun test
bun --cwd apps/web run test:e2e

# Clean and rebuild
bun run clean
bun install
bun run build

# Check results
cat performance-test-summary.json
cat PERFORMANCE_TEST_REPORT.md
```
