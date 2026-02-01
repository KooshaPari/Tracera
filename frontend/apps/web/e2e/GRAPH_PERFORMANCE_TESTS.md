# Graph Performance E2E Tests

## Overview

Comprehensive Playwright E2E performance tests for graph visualization, measuring real-world performance metrics including frame rates, interaction responsiveness, memory usage, and network efficiency.

## Test File

- **Location**: `/frontend/apps/web/e2e/graph-performance.spec.ts`
- **Framework**: Playwright Test
- **Total Test Suites**: 10
- **Total Tests**: 37

## Performance Targets

### Frame Rate
- **Target**: 60 FPS (16.6ms per frame)
- **Minimum Acceptable**: 50 FPS during interactions
- **Jank Tolerance**: <5% frames over 50ms

### Interaction Response
- **Node Selection**: <50ms
- **Maximum Response**: <100ms
- **Keyboard Shortcuts**: <100ms

### Memory Usage
- **Memory Increase**: <20MB during normal operations
- **Large Graph**: <50MB total
- **Heap Usage**: <80% of limit

### Network Efficiency
- **Initial Load**: <10 API requests
- **Progressive Loading**: <20 total requests
- **Cached Reload**: <5 requests

## Test Suites

### 1. Graph Performance - 500 Node Load
Tests basic graph loading and panning performance with medium-sized graphs.

**Tests:**
- ✓ Load 500 node graph within 5 seconds
- ✓ Maintain 60 FPS during panning
- ✓ Sustain performance during continuous panning (3+ seconds)

**Assertions:**
- Load time < 5000ms
- FPS > 50
- Average frame time < 20ms
- Jank percentage < 5%

### 2. Graph Performance - Zoom Operations
Tests zoom functionality smoothness and responsiveness.

**Tests:**
- ✓ Smooth zoom transitions
- ✓ Handle rapid zoom changes
- ✓ Zoom controls respond quickly

**Assertions:**
- Zoom FPS > 50
- Zoom control response < 100ms
- No freezing during rapid zoom

### 3. Graph Performance - Node Selection
Tests node selection responsiveness and multi-selection performance.

**Tests:**
- ✓ Select nodes with <50ms response time
- ✓ Handle rapid node selection without lag
- ✓ Maintain performance with multiple selections

**Assertions:**
- Average response time < 50ms
- Maximum response time < 100ms
- Multi-select maintains 45+ FPS

### 4. Graph Performance - Edge Rendering
Tests edge rendering stability during interactions.

**Tests:**
- ✓ Render edges without flicker during pan
- ✓ Maintain edge visibility during zoom
- ✓ Handle edge hover interactions smoothly

**Assertions:**
- No excessive edge flicker
- Edges remain visible at all zoom levels
- Hover interactions maintain 50+ FPS

### 5. Graph Performance - LOD Transitions
Tests Level of Detail transitions for smooth performance at different zoom levels.

**Tests:**
- ✓ Smoothly transition LOD during zoom
- ✓ Switch node detail levels appropriately
- ✓ Maintain readable text during LOD transitions

**Assertions:**
- LOD transition FPS > 40
- Jank percentage < 15%
- Labels remain visible at all levels

### 6. Graph Performance - Large Graph (1000+ Nodes)
Tests performance with very large graphs using progressive loading and virtualization.

**Tests:**
- ✓ Progressively load large graph
- ✓ Use viewport culling for off-screen nodes
- ✓ Maintain performance with large graph panning
- ✓ Handle large graph zoom efficiently
- ✓ Not exceed memory limits with large graph

**Assertions:**
- Initial render < 3000ms
- Viewport culling active
- Large graph panning FPS > 30
- Memory increase < 50MB
- Heap usage < 80%

### 7. Graph Performance - Memory Management
Tests memory efficiency and leak prevention.

**Tests:**
- ✓ Not leak memory during repeated interactions
- ✓ Clean up nodes when navigating away

**Assertions:**
- Repeated operations memory increase < 20MB
- Navigation cleanup releases memory

### 8. Graph Performance - Network Requests
Tests API efficiency and caching strategies.

**Tests:**
- ✓ Efficiently load graph data
- ✓ Implement progressive loading for viewport
- ✓ Cache graph data appropriately

**Assertions:**
- Initial load < 10 requests
- Progressive loading < 20 requests
- Cached reload < 5 requests

### 9. Graph Performance - Interaction Responsiveness
Tests keyboard shortcuts and UI control responsiveness.

**Tests:**
- ✓ Respond to keyboard shortcuts quickly
- ✓ Handle context menu interactions efficiently
- ✓ Update layout controls without lag

**Assertions:**
- Keyboard shortcuts < 100ms
- Context menu < 100ms
- Control updates < 100ms

### 10. Graph Performance - Rendering Optimization
Tests low-level rendering optimizations.

**Tests:**
- ✓ Use requestAnimationFrame for smooth updates
- ✓ Batch DOM updates efficiently
- ✓ Minimize layout thrashing

**Assertions:**
- RAF calls > 0 during updates
- Batched updates < 500ms
- Layout operations < 50ms

## Test Utilities

### Performance Measurement Functions

#### `measureFrameRate(page, duration)`
Measures FPS and frame timing during animations.

**Returns:**
```typescript
{
  fps: number;              // Frames per second
  avgFrameTime: number;     // Average ms per frame
  maxFrameTime: number;     // Worst frame time
  jankFrames: number;       // Frames over 50ms
  jankPercentage: number;   // % of janky frames
}
```

#### `getMemoryUsage(page)`
Captures current memory metrics.

**Returns:**
```typescript
{
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}
```

#### `measureInteractionTime(page, action)`
Measures response time for user interactions.

**Returns:** Response time in milliseconds

#### `waitForGraphReady(page)`
Waits for graph to be fully initialized and rendered.

#### `getNodeCount(page)` / `getEdgeCount(page)`
Gets current rendered node/edge count.

#### `forceGC(page)`
Triggers garbage collection for memory tests.

## Running the Tests

### Run All Graph Performance Tests
```bash
# Full test suite
bun playwright test e2e/graph-performance.spec.ts

# With UI
bun playwright test e2e/graph-performance.spec.ts --ui

# Specific suite
bun playwright test e2e/graph-performance.spec.ts -g "500 Node Load"
```

### Run with Performance Profiling
```bash
# Enable performance traces
bun playwright test e2e/graph-performance.spec.ts --trace on

# View trace
bun playwright show-report
```

### Run with Memory Profiling
Chrome must be launched with `--js-flags="--expose-gc"` for memory tests:

```bash
# Set in playwright.config.ts
use: {
  launchOptions: {
    args: ['--js-flags=--expose-gc']
  }
}
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Graph Performance Tests
  run: |
    bun playwright test e2e/graph-performance.spec.ts --reporter=json > performance-results.json

- name: Check Performance Thresholds
  run: |
    # Parse results and fail if thresholds exceeded
    node scripts/check-performance-thresholds.js
```

### Performance Budgets
Can be enforced in CI:
- FPS: Must be ≥50 for all pan/zoom operations
- Response Time: Must be ≤50ms for node selection
- Memory: Must not increase >50MB for large graphs
- Load Time: Must be ≤5s for 500 nodes

## Debugging Failed Tests

### Check Frame Rate Issues
1. Review frame timings in test output
2. Check for excessive jank frames
3. Profile with Chrome DevTools Performance tab
4. Look for long tasks in main thread

### Check Memory Leaks
1. Enable `--expose-gc` flag
2. Compare memory before/after operations
3. Use Chrome DevTools Memory profiler
4. Check for retained detached DOM nodes

### Check Network Issues
1. Review request waterfall
2. Check for duplicate requests
3. Verify caching headers
4. Monitor payload sizes

## Performance Monitoring Dashboard

Consider integrating with monitoring tools:
- **Lighthouse CI**: Continuous performance monitoring
- **Speedcurve**: Real user monitoring
- **Chrome UX Report**: Field data
- **Custom Dashboard**: Track metrics over time

## Test Scenarios by Graph Size

### Small Graph (<100 nodes)
- Instant load (<1s)
- Perfect 60 FPS
- All interactions <30ms

### Medium Graph (100-500 nodes)
- Fast load (<3s)
- Smooth 50-60 FPS
- Interactions <50ms

### Large Graph (500-1000 nodes)
- Progressive load (<5s)
- Acceptable 40-50 FPS
- Interactions <100ms

### Very Large Graph (1000+ nodes)
- Virtualized load (<3s initial)
- Viewport-dependent rendering
- 30+ FPS acceptable
- Progressive/lazy loading

## Known Limitations

### Browser-Specific
- Memory API requires Chrome with flags
- FPS measurement varies by browser
- Some features may not work in headless mode

### Environment-Specific
- CI performance may differ from local
- Network speed affects progressive loading
- System load impacts frame rates

### Test-Specific
- RAF call counting is approximate
- Flicker detection is simplified
- Memory measurements have variance

## Future Enhancements

### Additional Test Coverage
- [ ] Mobile viewport performance
- [ ] Touch gesture performance
- [ ] WebGL rendering tests (if applicable)
- [ ] Multi-monitor scenarios
- [ ] High DPI display tests

### Enhanced Metrics
- [ ] First Contentful Paint (FCP)
- [ ] Time to Interactive (TTI)
- [ ] Custom metrics (graph-specific)
- [ ] User-centric metrics

### Automation
- [ ] Automated performance regression detection
- [ ] Slack/email notifications on threshold violations
- [ ] Performance trend reports
- [ ] Comparative analysis (PR vs main)

## Resources

- [Playwright Performance Testing](https://playwright.dev/docs/test-performance)
- [Web Vitals](https://web.dev/vitals/)
- [ReactFlow Performance](https://reactflow.dev/learn/advanced-use/performance)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)

## Contributing

When adding new performance tests:
1. Define clear performance targets
2. Use helper functions for consistency
3. Document expected behavior
4. Set appropriate timeouts
5. Handle browser differences
6. Clean up resources (memory, listeners)

## License

Part of TraceRTM project - see main LICENSE file.
