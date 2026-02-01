# Quick Start: Graph Performance Testing

## Run Tests

```bash
# All performance tests
bun playwright test e2e/graph-performance.spec.ts

# Specific suite
bun playwright test e2e/graph-performance.spec.ts -g "500 Node Load"

# With UI mode
bun playwright test e2e/graph-performance.spec.ts --ui

# Generate report
bun playwright test e2e/graph-performance.spec.ts --reporter=html
```

## Performance Targets

| Metric | Target | Test |
|--------|--------|------|
| **FPS (Panning)** | 60 FPS | ≥50 FPS |
| **FPS (Zoom)** | 60 FPS | ≥50 FPS |
| **Node Selection** | <30ms | <50ms |
| **Load Time (500 nodes)** | <3s | <5s |
| **Memory Increase** | <10MB | <20MB |
| **Jank Frames** | <1% | <5% |

## Test Suites

### 1. Basic Performance (500 nodes)
```bash
bun playwright test -g "500 Node Load"
```
- Load time
- Panning FPS
- Continuous interaction

### 2. Zoom Performance
```bash
bun playwright test -g "Zoom Operations"
```
- Smooth transitions
- Rapid zoom
- Control responsiveness

### 3. Interaction Speed
```bash
bun playwright test -g "Node Selection"
```
- Selection response
- Rapid selection
- Multi-selection

### 4. Large Graphs (1000+ nodes)
```bash
bun playwright test -g "Large Graph"
```
- Progressive loading
- Viewport culling
- Memory limits

### 5. Memory Management
```bash
bun playwright test -g "Memory Management"
```
- Leak detection
- Cleanup verification

## Quick Checks

### Is the graph fast enough?
```bash
# Run FPS tests only
bun playwright test -g "FPS|maintain performance"
```

### Is selection responsive?
```bash
# Run interaction tests
bun playwright test -g "Node Selection|Responsiveness"
```

### Does it handle large graphs?
```bash
# Run large graph suite
bun playwright test -g "Large Graph"
```

### Are there memory leaks?
```bash
# Run memory tests (requires --expose-gc)
bun playwright test -g "Memory Management"
```

## Debugging Failed Tests

### 1. Check Test Output
```bash
# Verbose output
bun playwright test e2e/graph-performance.spec.ts --reporter=list

# With traces
bun playwright test e2e/graph-performance.spec.ts --trace on
```

### 2. View Performance Metrics
Failed tests show:
- Expected vs Actual FPS
- Frame timings
- Memory usage
- Network requests

### 3. Profile in Chrome
```bash
# Run with DevTools
bun playwright test --headed --debug
```

## Common Issues

### Low FPS
- **Cause**: Too many rendered nodes
- **Fix**: Check viewport culling
- **Test**: `should use viewport culling`

### Slow Selection
- **Cause**: Inefficient event handlers
- **Fix**: Debounce/throttle handlers
- **Test**: `should select nodes with <50ms`

### Memory Leaks
- **Cause**: Event listeners not cleaned up
- **Fix**: Use cleanup in useEffect
- **Test**: `should not leak memory`

### Slow Load
- **Cause**: Loading all data upfront
- **Fix**: Progressive/lazy loading
- **Test**: `should progressively load`

## CI Integration

### GitHub Actions
```yaml
- name: Performance Tests
  run: |
    bun playwright test e2e/graph-performance.spec.ts \
      --reporter=json > performance.json

- name: Check Thresholds
  run: |
    if [ $(jq '.stats.failures' performance.json) -gt 0 ]; then
      echo "Performance tests failed!"
      exit 1
    fi
```

### Performance Budgets
Set in `playwright.config.ts`:
```typescript
expect: {
  timeout: 5000, // Max test timeout
  toPass: { timeout: 30000 } // Max retry time
}
```

## Best Practices

1. **Run on Clean State**
   - Clear cache before tests
   - Reset browser state
   - Force garbage collection

2. **Consistent Environment**
   - Same viewport size
   - Same system load
   - Same network conditions

3. **Multiple Runs**
   - Run 3+ times
   - Take median/average
   - Ignore outliers

4. **Compare Baselines**
   - Track metrics over time
   - Compare to previous runs
   - Set regression thresholds

## Next Steps

1. Run all tests: `bun playwright test e2e/graph-performance.spec.ts`
2. Fix any failures
3. Set up CI automation
4. Monitor trends over time

## Need Help?

- View full documentation: `GRAPH_PERFORMANCE_TESTS.md`
- Check test file: `e2e/graph-performance.spec.ts`
- Review Playwright docs: https://playwright.dev/docs/test-performance
