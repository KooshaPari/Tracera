# Manual Testing Guide - 10k Node Baseline Verification

This guide provides step-by-step instructions for manually verifying the 10k node performance baseline in the browser.

## Prerequisites

1. **Generated Test Data**

   ```bash
   cd frontend/apps/web
   bun run generate:test-graph 10000 15000
   ```

2. **Development Server Running**

   ```bash
   bun run dev
   ```

3. **Browser DevTools Ready**
   - Chrome/Edge DevTools (Recommended)
   - Firefox DevTools (Alternative)

## Test Setup

### Loading Test Data

1. Navigate to the graph view in the application
2. Open DevTools Console
3. Load test data:
   ```javascript
   // Load test graph data
   const response = await fetch('/test-data/test-graph-10000.json');
   const testGraph = await response.json();
   console.log('Loaded test graph:', testGraph.metadata);
   ```

### Performance Panel Setup

1. Open DevTools → **Performance** tab
2. Enable **Screenshots** option
3. Set **CPU throttling** to "No throttling" for baseline
4. Set **Network** to "No throttling"

---

## Test 1: FPS Measurement @ 10k Nodes

**Objective:** Measure frame rate during graph interaction

### Steps

1. Load 10k node test graph
2. Open Performance panel
3. Click **Record** (●)
4. Perform the following actions for 10 seconds:
   - Pan the graph (drag viewport)
   - Zoom in/out (mouse wheel)
   - Move cursor across nodes
5. Stop recording

### Measurements

1. Look at **Frames** section
2. Hover over frame bars to see FPS
3. Calculate average FPS from multiple frames
4. Check **Main thread** for layout/paint operations

### Expected Results

- ✓ **Average FPS:** ≥60 FPS
- ✓ **Frame time:** ≤16.67ms (1000ms/60fps)
- ✓ **No red bars** (dropped frames)

### Screenshot Locations

- Take screenshot of Performance timeline
- Save as: `screenshots/test1-fps-measurement.png`

---

## Test 2: R-tree Query Performance

**Objective:** Measure viewport culling query time

### Steps

1. Open Console
2. Enable verbose logging:
   ```javascript
   // Enable performance logging
   localStorage.setItem('debug:graph:performance', 'true');
   ```
3. Reload page with test graph
4. Pan viewport 10 times
5. Check console logs for query times

### Measurements

Look for console output like:

```
[Graph] Viewport query: 3.2ms (visible: 247/10000 nodes)
```

### Expected Results

- ✓ **Query time:** <5ms
- ✓ **Visible nodes:** ~200-500 (depending on zoom)
- ✓ **Culled nodes:** >9000

### Console Output

Copy console logs to: `screenshots/test2-query-times.txt`

---

## Test 3: Memory Usage

**Objective:** Verify memory consumption stays below 600MB

### Steps

1. Open DevTools → **Memory** tab
2. Click **Take heap snapshot** (before loading graph)
3. Load 10k test graph
4. Wait 5 seconds for stabilization
5. Click **Take heap snapshot** (after loading graph)
6. Compare snapshots

### Measurements

1. Check **Shallow Size** and **Retained Size**
2. Look for memory leaks (expanding size over time)
3. Note total heap size

### Expected Results

- ✓ **Heap size:** <600MB
- ✓ **No memory leaks** (stable size)
- ✓ **Reasonable growth** (≈200-400MB for graph data)

### Screenshot

Save heap snapshot comparison: `screenshots/test3-memory-usage.png`

---

## Test 4: Node LOD Transitions

**Objective:** Verify smooth LOD transitions across zoom levels

### Steps

1. Load 10k test graph
2. Start at zoom level 0.3 (very zoomed out)
3. Gradually zoom in to 2.0
4. Observe node rendering changes

### Visual Checkpoints

| Zoom Level | Expected Node Rendering     | Visual Check           |
| ---------- | --------------------------- | ---------------------- |
| 0.3        | SimplePill (minimal detail) | Small colored circles  |
| 0.5        | MediumPill (label only)     | Circles with labels    |
| 0.8        | RichNodePill (full detail)  | Full node cards        |
| 1.0        | RichNodePill                | Full detail maintained |
| 1.5+       | RichNodePill                | Maximum detail         |

### Expected Results

- ✓ **Smooth transitions** (no visual jumps)
- ✓ **Progressive enhancement** (details appear gradually)
- ✓ **No flickering** during zoom

### Screenshots

Take screenshots at each zoom level: `screenshots/test4-lod-zoom-{level}.png`

---

## Test 5: Selected Node Full Detail

**Objective:** Verify selected nodes always show full detail

### Steps

1. Zoom out to 0.3 (very far)
2. Nodes should appear as SimplePill
3. Click on a node
4. Observe selected node rendering

### Expected Results

- ✓ **Selected node:** Shows RichNodePill even at zoom 0.3
- ✓ **Other nodes:** Remain SimplePill
- ✓ **Transition:** Smooth from simple → detailed

### Screenshot

Save: `screenshots/test5-selected-detail.png`

---

## Test 6: Edge LOD Transitions

**Objective:** Verify edges simplify based on viewport distance

### Steps

1. Load graph with 15k edges:
   ```javascript
   const response = await fetch('/test-data/test-graph-10000.json');
   const testGraph = await response.json();
   // Graph has 15k edges
   ```
2. Pan to center of graph
3. Observe edge rendering at different distances

### Visual Checkpoints

| Distance from Center | Expected Edge Rendering   |
| -------------------- | ------------------------- |
| <500px               | Bezier curves with labels |
| 500-1500px           | Simple straight lines     |
| >1500px              | Hidden (opacity 0)        |

### Expected Results

- ✓ **Center edges:** Full detail (curves + labels)
- ✓ **Mid-distance edges:** Simplified (straight lines)
- ✓ **Far edges:** Hidden
- ✓ **Performance:** No lag when panning

### Screenshot

Save: `screenshots/test6-edge-lod.png`

---

## Test 7: Maximum Node Count Stress Test

**Objective:** Find performance breaking point

### Steps

1. Test graphs of increasing size:

   ```bash
   bun run generate:test-graph 5000 7500
   bun run generate:test-graph 10000 15000
   bun run generate:test-graph 15000 22500
   bun run generate:test-graph 20000 30000
   ```

2. Load each graph and measure FPS
3. Record results

### Expected Results

| Node Count | Expected FPS | Usability   |
| ---------- | ------------ | ----------- |
| 5,000      | ≥60 FPS      | ✓ Excellent |
| 10,000     | ≥60 FPS      | ✓ Good      |
| 15,000     | ≥30 FPS      | ✓ Usable    |
| 20,000     | <30 FPS      | ✗ Degraded  |

### Data Collection

Create table: `screenshots/test7-stress-test-results.csv`

---

## Test 8: Pan Performance

**Objective:** Verify smooth panning without frame drops

### Steps

1. Load 10k test graph
2. Open Performance panel
3. Record while performing:
   - Rapid horizontal panning (30 seconds)
   - Rapid vertical panning (30 seconds)
   - Diagonal panning (30 seconds)

### Measurements

1. Check for **dropped frames** (red bars)
2. Measure **pan latency** (input → visual update)
3. Monitor **Main thread** activity

### Expected Results

- ✓ **FPS:** ≥50 FPS during panning
- ✓ **No frame drops** (<5% dropped frames acceptable)
- ✓ **Smooth motion** (no stuttering)

### Screenshot

Save: `screenshots/test8-pan-performance.png`

---

## Test 9: Zoom Performance

**Objective:** Verify smooth zoom transitions

### Steps

1. Load 10k test graph
2. Record performance
3. Rapidly zoom in/out using mouse wheel:
   - 20 zoom-in operations
   - 20 zoom-out operations
   - Mix of both

### Measurements

1. Check **LOD transition time**
2. Monitor **frame rate during zoom**
3. Look for **layout thrashing**

### Expected Results

- ✓ **Zoom response:** <50ms per zoom level change
- ✓ **LOD transitions:** Smooth (no flashing)
- ✓ **FPS maintained:** ≥50 FPS

### Screenshot

Save: `screenshots/test9-zoom-performance.png`

---

## Reporting Results

### Create Results Document

Use this template:

```markdown
# Manual Verification Results - [Date]

**Tester:** [Your Name]
**Browser:** [Chrome/Firefox] [Version]
**OS:** [macOS/Windows/Linux]
**Hardware:** [CPU/GPU]

## Test Results

| Test            | Target     | Actual   | Pass/Fail | Notes |
| --------------- | ---------- | -------- | --------- | ----- |
| FPS @ 10k       | ≥60 FPS    | XX FPS   | ✓/✗       |       |
| R-tree query    | <5ms       | XX ms    | ✓/✗       |       |
| Memory usage    | <600MB     | XX MB    | ✓/✗       |       |
| Node LOD        | Smooth     | [Result] | ✓/✗       |       |
| Selected detail | Full       | [Result] | ✓/✗       |       |
| Edge LOD        | Smooth     | [Result] | ✓/✗       |       |
| Max nodes       | 10k usable | [Result] | ✓/✗       |       |
| Pan perf        | No drops   | [Result] | ✓/✗       |       |
| Zoom perf       | Smooth     | [Result] | ✓/✗       |       |

## Issues Found

[List any issues or unexpected behaviors]

## Recommendations

[Suggested improvements]

## Screenshots

[Attach all screenshots]
```

### Submit Results

1. Save results to: `manual-testing-results/YYYY-MM-DD-results.md`
2. Add screenshots to: `manual-testing-results/screenshots/`
3. Create summary in PERFORMANCE_VERIFICATION_RESULTS.md

---

## Automated Verification

For quick verification, run:

```bash
# Generate test data
bun run generate:test-graph 10000 15000

# Run automated verification
bun run verify:10k-baseline
```

This will generate: `PERFORMANCE_VERIFICATION_RESULTS.md`

---

## Troubleshooting

### Issue: Low FPS

**Possible Causes:**

- Browser throttling enabled
- Other heavy processes running
- GPU acceleration disabled

**Solutions:**

1. Disable CPU throttling in DevTools
2. Close other applications
3. Enable hardware acceleration in browser settings

### Issue: High Memory Usage

**Possible Causes:**

- Memory leak in graph rendering
- Too many retained objects
- Large node data structures

**Solutions:**

1. Check for leaked event listeners
2. Use heap snapshots to find retained objects
3. Optimize node data structure

### Issue: Jerky Animations

**Possible Causes:**

- Layout thrashing
- Too many style recalculations
- Synchronous rendering

**Solutions:**

1. Use `requestAnimationFrame` for animations
2. Batch DOM updates
3. Use CSS transforms instead of layout properties

---

## Next Steps

1. ✓ Complete all 9 manual tests
2. ✓ Document results with screenshots
3. ✓ Compare with automated verification results
4. ✓ Update IMPLEMENTATION_COMPLETE.md
5. ✓ Mark Task 17 as complete

---

_For questions or issues, refer to the main project documentation._
