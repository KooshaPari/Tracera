# Quick Start: Performance Benchmarking

This guide shows you how to run the 10k node performance baseline benchmarks and interpret the results.

## Prerequisites

1. **Install dependencies**:
   ```bash
   cd frontend/apps/web
   bun install
   ```

2. **Install Playwright browsers** (if not already installed):
   ```bash
   bun playwright install chromium
   ```

3. **Build the application**:
   ```bash
   bun run build
   ```

## Running the Benchmarks

### Quick Run (All Performance Tests)

Run all performance tests including the 10k baseline:

```bash
bun run test:performance
```

### 10k Baseline Only

Run only the comprehensive 10k node baseline benchmark:

```bash
bun run test:performance:10k
```

### Full Benchmark + Report

Run the benchmark and automatically generate the HTML report:

```bash
bun run perf:baseline
```

This will:
1. Execute all 5 benchmark scenarios
2. Capture performance metrics
3. Save results to `performance-results/10k-baseline-{timestamp}.json`
4. Generate HTML report to `performance-results/10k-baseline-{timestamp}.html`

## Viewing Results

### Terminal Output

After running the benchmark, you'll see a summary in the terminal:

```
================================================================================
📊 10K NODE BASELINE BENCHMARK RESULTS
================================================================================
Overall Score: 65/100 (Grade: C)
Production Ready: ❌ NO

Scenario Results:
  Load Time: 2847ms (target: <3000ms)
  Pan FPS: 28.3 (target: >30fps)
  Zoom FPS: 31.2 (target: >30fps)
  Selection: 87.5ms (target: <100ms)
  LOD Transition: 92.3ms (target: <100ms)
  Memory: 412.5MB (target: <500MB)

⚠️  Blockers:
    - Pan FPS below 30fps

💡 Recommendations:
    - Optimize viewport culling and edge rendering
    - Increase viewport culling aggressiveness

📄 Results saved to: performance-results/10k-baseline-1738368000000.json
================================================================================
```

### HTML Report

Open the generated HTML report in your browser:

```bash
# macOS
open frontend/apps/web/performance-results/10k-baseline-{timestamp}.html

# Linux
xdg-open frontend/apps/web/performance-results/10k-baseline-{timestamp}.html

# Windows
start frontend/apps/web/performance-results/10k-baseline-{timestamp}.html
```

The HTML report includes:
- **Performance Grade** (A-F)
- **Interactive Charts** showing metrics vs targets
- **Comparison Table** with current vs target vs 100k goal
- **Blockers** preventing production deployment
- **Recommendations** for optimization
- **Test Environment** details

### JSON Results

For programmatic analysis, use the JSON output:

```bash
cat frontend/apps/web/performance-results/10k-baseline-{timestamp}.json | jq '.summary'
```

## Understanding the Results

### Performance Grades

- **A (90-100)**: ✅ Production ready, excellent performance
- **B (70-89)**: ✅ Good, minor optimizations recommended
- **C (50-69)**: ⚠️ Acceptable, optimization work required
- **D (30-49)**: ❌ Below target, significant work needed
- **F (0-29)**: ❌ Not viable, architectural changes required

### Key Metrics Explained

#### Initial Render Time
- **What**: Time from loading data to first interactive frame
- **Target**: < 3000ms
- **Includes**: Layout computation + first paint
- **Why it matters**: First impression of application responsiveness

#### Pan FPS (Frames Per Second)
- **What**: Frame rate during continuous panning
- **Target**: > 30 fps (smooth) / > 60 fps (ideal)
- **Why it matters**: Core navigation experience

#### Zoom FPS
- **What**: Frame rate during zoom operations
- **Target**: > 30 fps
- **Why it matters**: Essential for exploring large graphs

#### Node Selection Time
- **What**: Response time when clicking a node
- **Target**: < 100ms (feels instant to users)
- **Why it matters**: Interaction responsiveness

#### Memory Usage
- **What**: JavaScript heap size during operation
- **Target**: < 500MB (10k) / < 800MB (100k)
- **Why it matters**: Browser stability and user experience

#### LOD Transition Time
- **What**: Time to switch between detail levels during zoom
- **Target**: < 100ms
- **Why it matters**: Smooth visual experience

### Blockers vs Recommendations

**Blockers** (❌ Must fix before production):
- Initial render > 10 seconds
- FPS < 15 during pan/zoom
- Memory usage > 1 GB
- Frequent crashes

**Recommendations** (💡 Should improve):
- Pan FPS < 30
- Selection time > 100ms
- Memory usage > 500MB
- Culling ratio < 80%

## Troubleshooting

### Benchmark Fails to Run

**Error**: "No benchmark results found"

```bash
# Ensure you ran the benchmark first
bun run test:performance:10k

# Then generate the report
bun run perf:report
```

**Error**: "Timeout waiting for .react-flow"

```bash
# The graph component may not be loading
# Check if the application builds correctly
bun run build

# Try running with headed browser to debug
bun playwright test src/__tests__/performance/10k-baseline.bench.ts --headed
```

### Poor Performance Results

**All metrics are red (F grade)**:

1. Check if the application is in production mode:
   ```bash
   bun run build
   bun run preview
   ```

2. Ensure no background processes are consuming CPU

3. Close other browser tabs and applications

4. Try running on a more powerful machine

**Inconsistent results between runs**:

1. Run multiple times and average the results
2. Close all other applications
3. Disable browser extensions
4. Use incognito/private mode

### Memory Issues

**Error**: "Out of memory" during benchmark

1. Reduce the test duration in the benchmark file
2. Run on a machine with more RAM
3. Close other applications

## Next Steps

### Comparing Results

To track performance over time:

1. Run benchmarks after each optimization
2. Compare JSON results programmatically:

```typescript
import baseline1 from './10k-baseline-1.json';
import baseline2 from './10k-baseline-2.json';

const improvement = {
  renderTime: baseline1.scenarios.load10kGraph.initialRenderTime -
              baseline2.scenarios.load10kGraph.initialRenderTime,
  panFPS: baseline2.scenarios.continuousPan.continuousPanFPS -
          baseline1.scenarios.continuousPan.continuousPanFPS,
};

console.log(`Render time: ${improvement.renderTime}ms faster`);
console.log(`Pan FPS: ${improvement.panFPS.toFixed(1)} fps better`);
```

### CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
# .github/workflows/performance.yml
name: Performance Benchmarks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: bun install

      - name: Run benchmarks
        run: bun run perf:baseline

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: frontend/apps/web/performance-results/
```

### Custom Benchmarks

To create custom benchmarks for specific scenarios:

1. Copy the baseline benchmark as a template
2. Modify the test scenarios
3. Adjust performance targets
4. Run and compare results

Example:

```typescript
// Custom 5k node benchmark
test("Custom scenario: 5k nodes with filters", async ({ page }) => {
  // Generate 5k nodes
  await generate5kGraphData(page);

  // Apply filters
  await page.click('[data-testid="filter-requirements"]');

  // Measure performance
  const metrics = await measureFrameRate(page, 2000);

  expect(metrics.fps).toBeGreaterThan(45); // Higher target for fewer nodes
});
```

## Resources

- [Full Performance Report Documentation](../../reports/10k-node-baseline-performance.md)
- [Graph Virtualization Guide](../graph-virtualization.md)
- [Performance Optimization Roadmap](../performance-optimization.md)
- [Playwright Documentation](https://playwright.dev/)

## Support

If you encounter issues running the benchmarks:

1. Check the [troubleshooting section](#troubleshooting) above
2. Review the [benchmark source code](../../../frontend/apps/web/src/__tests__/performance/10k-baseline.bench.ts)
3. Open an issue on GitHub with:
   - Error message
   - Terminal output
   - System information (OS, RAM, CPU)
   - Node version (`node --version`)

---

**Last Updated**: 2026-01-31
**Benchmark Version**: 1.0.0
