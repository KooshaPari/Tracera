# 10k Node Graph Performance Baseline Report

## Executive Summary

This document establishes the performance baseline for rendering and interacting with 10,000 node graphs in the TraceRTM graph visualization system. These benchmarks measure the current implementation and define targets for Phases 5-8 optimization work.

## Test Overview

### Graph Configuration
- **Nodes**: 10,000
- **Edges**: ~50,000 (average 5 edges per node)
- **Node Types**: requirement, epic, user_story, task, bug, test_case, code, ui_component
- **Viewport**: 1920x1080

### Test Scenarios

1. **Initial Load** - Measure time to render 10k nodes and compute layout
2. **Continuous Pan** - FPS during extended panning operations
3. **Zoom Operations** - FPS during zoom from 0.1x to 2x
4. **Node Selection** - Response time for selecting individual nodes
5. **LOD Transitions** - Performance of level-of-detail changes during zoom

## Performance Targets

### Phase 5-8 Targets (10k nodes)
| Metric | Current Baseline | Phase 5-8 Target | Status |
|--------|------------------|------------------|--------|
| Initial Render | TBD | < 3s | 🔴 TBD |
| Pan FPS | TBD | > 30 fps | 🔴 TBD |
| Zoom FPS | TBD | > 30 fps | 🔴 TBD |
| Memory Usage | TBD | < 500 MB | 🔴 TBD |
| Node Selection | TBD | < 100 ms | 🔴 TBD |
| LOD Transition | TBD | < 100 ms | 🔴 TBD |

### 100k Node Stretch Goals
| Metric | Target |
|--------|--------|
| Initial Render | < 5s |
| Pan FPS | > 30 fps |
| Zoom FPS | > 30 fps |
| Memory Usage | < 800 MB |
| Node Selection | < 50 ms |

## Benchmark Metrics

### 1. Initial Render Performance

**What it measures:**
- Time from data load to first interactive frame
- Layout computation time
- First contentful paint
- Initial memory allocation

**Current optimizations in place:**
- DAG layout algorithm
- Viewport culling with 300px padding
- Level-of-detail rendering (3 levels)
- Progressive node loading

**Expected results:**
- Layout computation: < 2s
- First paint: < 500ms
- Total render time: < 3s
- Visible nodes: 200-500 (depending on viewport)

### 2. Continuous Pan Performance

**What it measures:**
- Frame rate during extended panning (3s duration)
- Frame time consistency
- Jank percentage (frames > 50ms)
- Viewport culling effectiveness

**Current optimizations:**
- `requestAnimationFrame` batching
- Edge culling based on visible nodes
- Memoized node components
- Throttled viewport updates

**Expected results:**
- FPS: > 30 fps average
- Jank: < 10% frames
- Average frame time: < 33ms
- Culling ratio: > 80%

### 3. Zoom Performance

**What it measures:**
- FPS during zoom operations (0.1x to 2x range)
- LOD transition smoothness
- Memory pressure during zoom

**Current optimizations:**
- 3-level LOD system (high/medium/low)
- Simplified node components at low zoom
- Edge animation disabled during zoom
- Zoom thresholds: high >= 0.8x, medium >= 0.5x

**Expected results:**
- FPS: > 30 fps during zoom
- LOD transitions: < 100ms
- No memory spikes during zoom

### 4. Node Selection Performance

**What it measures:**
- Time from click to visual feedback
- Detail panel render time
- Event handling efficiency

**Current optimizations:**
- Memoized node data
- Lazy detail panel loading
- Debounced related items calculation

**Expected results:**
- Average selection time: < 100ms
- Max selection time: < 200ms
- Consistent across 20 selections

### 5. LOD Transition Performance

**What it measures:**
- Time to switch between LOD levels
- Component re-render efficiency
- Visual smoothness of transitions

**Current optimizations:**
- Component type switching (richPill → mediumPill → simplifiedPill)
- Memoized node components
- Stable node IDs

**Expected results:**
- Transition time: < 100ms
- No visual flicker
- Smooth zoom experience

## Memory Analysis

### Heap Allocation Tracking

**What we measure:**
- Initial heap size after load
- Peak heap during interaction
- Final heap after operations
- Heap usage percentage

**Memory breakdown:**
- Node data structures: ~200-300 MB
- React virtual DOM: ~50-100 MB
- ReactFlow internals: ~100-150 MB
- Edge data: ~50-100 MB

**Expected results:**
- Initial: < 400 MB
- Peak: < 500 MB
- No memory leaks during interaction
- Heap usage: < 60% of limit

## Culling Analysis

### Viewport Culling Metrics

**What we track:**
- Visible nodes in viewport
- Culled (off-screen) nodes
- Culling ratio
- Edge culling effectiveness

**Current configuration:**
- Viewport padding: 300px
- Culling threshold: Always enabled
- Edge culling: Render only visible node edges

**Expected results:**
- Visible nodes: 200-500 (2-5% of total)
- Culled nodes: 9,500-9,800 (95-98%)
- Culling ratio: > 95%
- Rendered edges: 500-2,500 (1-5% of total)

## Running the Benchmarks

### Prerequisites

```bash
# Install dependencies
bun install

# Build the application
bun run build
```

### Execute Benchmarks

```bash
# Run the 10k node baseline benchmark
bun run test:e2e --grep "10k Node Baseline Performance"

# Or run all performance tests
bun run test:performance
```

### Generate HTML Report

```bash
# Generate visual report with charts
bun run scripts/generate-performance-report.ts
```

The report will be generated in:
```
frontend/apps/web/performance-results/10k-baseline-{timestamp}.html
```

## Interpreting Results

### Performance Grades

- **A (90-100)**: Production ready, excellent performance
- **B (70-89)**: Good performance, minor optimizations needed
- **C (50-69)**: Acceptable, optimization work required
- **D (30-49)**: Below target, significant optimization needed
- **F (0-29)**: Not viable, major architectural changes needed

### Key Indicators

✅ **Pass**: Meets or exceeds target
⚠️ **Warn**: Close to target, watch for regression
❌ **Fail**: Below target, optimization required

### Blockers vs Recommendations

**Blockers** - Critical issues that prevent production deployment:
- Initial render > 10s
- FPS < 15 during pan/zoom
- Memory usage > 1 GB
- Consistent crashes or freezes

**Recommendations** - Optimization opportunities:
- Improve viewport culling
- Optimize edge rendering
- Reduce memory footprint
- Enhance LOD transitions

## Optimization Roadmap (Phases 5-8)

### Phase 5: Core Optimizations
- **Target**: Baseline functionality at 10k scale
- WebGL renderer for nodes (massive performance gain)
- Spatial indexing (R-tree/Quad-tree) for culling
- Worker-based layout computation
- **Expected improvement**: 2-3x FPS increase

### Phase 6: Advanced Culling
- **Target**: 60 FPS at 10k nodes
- Frustum culling with spatial hash
- Dynamic LOD based on node importance
- Edge bundling for dense connections
- **Expected improvement**: 40% fewer rendered elements

### Phase 7: Memory Optimization
- **Target**: < 300 MB heap usage
- Virtual scrolling for node data
- Lazy edge materialization
- Texture atlasing for node graphics
- **Expected improvement**: 50% memory reduction

### Phase 8: 100k Node Support
- **Target**: Usable performance at 100k scale
- Hierarchical clustering
- Progressive data streaming
- GPU-accelerated edge rendering
- **Expected improvement**: 10x scalability

## Comparison with Industry Standards

| Product | Max Nodes | Pan FPS | Memory (10k) | Notes |
|---------|-----------|---------|--------------|-------|
| Gephi | 100k+ | 30-60 | 400 MB | Desktop app, native rendering |
| Cytoscape.js | 10k | 20-30 | 300 MB | Canvas-based, limited interactivity |
| vis.js | 5k | 15-25 | 400 MB | DOM-based, performance issues at scale |
| **TraceRTM (Current)** | **TBD** | **TBD** | **TBD** | React + ReactFlow, virtualization |
| **TraceRTM (Target)** | **10k** | **30+** | **< 500 MB** | Phase 5-8 optimizations |
| **TraceRTM (Stretch)** | **100k** | **30+** | **< 800 MB** | Full optimization suite |

## Technical Details

### Test Implementation

The benchmark is implemented as a Playwright E2E test that:

1. Generates synthetic graph data (10k nodes, 50k edges)
2. Injects data into the graph component
3. Measures performance during various operations
4. Collects memory and FPS metrics
5. Generates JSON results and HTML reports

### Data Generation

Nodes are distributed across 8 types:
- 1,250 requirements
- 1,250 epics
- 1,250 user stories
- 1,250 tasks
- 1,250 bugs
- 1,250 test cases
- 1,250 code entities
- 1,250 UI components

Edges are randomly distributed across 5 types:
- traces_to (10,000)
- depends_on (10,000)
- blocks (10,000)
- implements (10,000)
- tests (10,000)

### Measurement Methodology

**Frame Rate**:
```typescript
// Measure FPS over duration
const frameTimings: number[] = [];
let lastFrameTime = performance.now();

const measureFrames = () => {
  const now = performance.now();
  frameTimings.push(now - lastFrameTime);
  lastFrameTime = now;

  if (now - startTime < duration) {
    requestAnimationFrame(measureFrames);
  } else {
    calculateMetrics(frameTimings);
  }
};
```

**Memory**:
```typescript
// Chrome performance.memory API
const memory = (performance as any).memory;
const heapUsed = memory.usedJSHeapSize / 1048576; // MB
```

**Interaction Time**:
```typescript
const startTime = performance.now();
await action();
await waitForNextFrame();
const endTime = performance.now();
```

## Continuous Monitoring

### CI/CD Integration

The benchmark can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/performance.yml
- name: Run Performance Benchmarks
  run: bun run test:e2e --grep "10k Node Baseline"

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: performance-results
    path: frontend/apps/web/performance-results/
```

### Performance Regression Detection

Track metrics over time to detect regressions:

```typescript
// Compare current run against baseline
if (currentRenderTime > baselineRenderTime * 1.2) {
  console.warn("⚠️ 20% performance regression detected!");
}
```

## Troubleshooting

### Common Issues

**Low FPS during pan**:
- Check viewport culling is enabled
- Verify edge count in viewport
- Monitor for excessive re-renders

**High memory usage**:
- Check for memory leaks (repeated operations)
- Verify nodes are properly cleaned up
- Monitor edge data structures

**Slow initial render**:
- Check layout computation time
- Verify progressive loading
- Monitor for blocking operations

### Debug Tools

Enable debug mode in the graph component:
```typescript
<VirtualizedGraphView
  enableVirtualization={true}
  showControls={true}
  // Shows performance metrics in UI
/>
```

## Appendix

### Related Documentation
- [Graph Virtualization Implementation](../guides/graph-virtualization.md)
- [LOD System Architecture](../reference/lod-system.md)
- [Performance Optimization Guide](../guides/performance-optimization.md)

### Benchmark Results Archive
- Results are stored in: `frontend/apps/web/performance-results/`
- JSON format for programmatic analysis
- HTML format for human review
- Timestamped for historical comparison

### Future Work
- [ ] WebGL renderer integration
- [ ] Spatial indexing implementation
- [ ] Worker-based layout computation
- [ ] Edge bundling algorithm
- [ ] Hierarchical clustering for 100k nodes
- [ ] GPU-accelerated rendering pipeline

---

**Last Updated**: 2026-01-31
**Version**: 1.0.0
**Maintainer**: Performance Engineering Team
