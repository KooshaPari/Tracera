# D3-Force Graph Evaluation for 100k+ Nodes

**Research Date:** 2026-02-01
**Purpose:** Evaluate D3.js force-directed graphs for large-scale visualization (100k+ nodes)

---

## Executive Summary

**Verdict: NOT RECOMMENDED for 100k+ nodes without significant optimization**

D3-force can theoretically handle large graphs due to its O(n log n) Barnes-Hut optimization, but **rendering becomes the primary bottleneck**. For 100k+ nodes:

- **SVG rendering:** Impractical beyond ~1,000-2,000 nodes
- **Canvas rendering:** Viable up to ~10,000 nodes with optimization
- **WebGL rendering (PixiJS):** Required for 100k+ nodes
- **Web Worker computation:** Essential for UI responsiveness

**Recommended Approach:**
1. D3-force for layout computation (in Web Worker)
2. PixiJS for WebGL rendering
3. Viewport culling for visible nodes only
4. Graph clustering/aggregation for user experience

---

## 1. D3-Force Performance Benchmarks

### 1.1 Simulation Performance

**Algorithmic Complexity:**
- D3-force uses [Barnes-Hut approximation](https://jheer.github.io/barnes-hut/) with **O(n log n)** complexity per tick
- Quadtree-based spatial subdivision for efficient force calculation
- Default: ~300 iterations for convergence

**Known Performance Thresholds:**

| Node Count | SVG Rendering | Canvas Rendering | Notes |
|------------|---------------|------------------|-------|
| < 1,000 | Good | Excellent | SVG is acceptable |
| 1,000 - 2,000 | Choppy | Good | [SVG starts lagging](https://groups.google.com/g/d3-js/c/ZJ6pznVU5LQ/m/wLYuIGPUnvsJ) |
| 2,000 - 10,000 | Poor | Acceptable | [Canvas ~4x faster](https://medium.com/@xoor/implementing-charts-that-scale-with-d3-and-canvas-3e14bbe70f37) |
| 10,000+ | Unusable | Requires optimization | [WebGL needed](https://blog.scottlogic.com/2020/05/01/rendering-one-million-points-with-d3.html) |
| 100,000+ | N/A | N/A | Hybrid approach required |

**Benchmark: Canvas vs SVG (10,000 nodes)**
- D3/Canvas: **173 ms** per render
- D3/SVG: **682 ms** per render
- Performance gain: **~4x faster** with Canvas

Source: [Implementing Charts that Scale with D3 and Canvas](https://medium.com/@xoor/implementing-charts-that-scale-with-d3-and-canvas-3e14bbe70f37)

### 1.2 Alpha Decay Strategies

The simulation uses an "alpha" value (0.0 to 1.0) that controls cooling/convergence.

**Default Configuration:**
```javascript
simulation
  .alphaMin(0.001)        // Stop when alpha < 0.001
  .alphaDecay(0.0228)     // Decay rate: 1 - pow(0.001, 1/300)
  .alphaTarget(0)         // Cool to zero
```

**Convergence Time:**
- Default: **~300 iterations** = `⌈log(alphaMin) / log(1 - alphaDecay)⌉`
- Formula: `iterations = Math.ceil(Math.log(0.001) / Math.log(1 - 0.0228))`

**Optimization Strategies:**

| Strategy | Use Case | Trade-off |
|----------|----------|-----------|
| Higher decay (e.g., 0.05) | Quick preview | Risk local minimum, less stable |
| Lower decay (e.g., 0.01) | High-quality layout | Slower convergence, better layout |
| Dynamic decay | Large graphs | Fast initial, slow refinement |
| alphaTarget > 0 | Interactive updates | Continuous warming for smooth transitions |

**Best Practice for 100k+ Nodes:**
```javascript
// Fast initial layout
simulation.alphaDecay(0.05).on('end', () => {
  // Refine with slower decay
  simulation.alphaDecay(0.01).alphaTarget(0.001).restart();
});
```

Source: [D3 Force Simulations Documentation](https://d3js.org/d3-force/simulation)

### 1.3 Convergence Time Measurements

**Expected Tick Times (estimated):**

| Node Count | Ticks/sec | 300 iterations |
|------------|-----------|----------------|
| 1,000 | ~60 | ~5 seconds |
| 10,000 | ~15 | ~20 seconds |
| 50,000 | ~3-5 | ~60-100 seconds |
| 100,000 | ~1-2 | ~150-300 seconds |

*Note: Times vary based on hardware, edge density, and force configuration*

**Critical Insight:** For large graphs, [static layouts should be computed in a web worker](https://d3js.org/d3-force/simulation) to avoid freezing the UI.

---

## 2. Quadtree Optimization (Barnes-Hut)

### 2.1 How Barnes-Hut Works

The [Barnes-Hut algorithm](https://jheer.github.io/barnes-hut/) reduces n-body simulation from **O(n²)** to **O(n log n)**.

**Three-Step Process:**

1. **Quadtree Construction:** Recursively subdivide 2D space into four quadrants
   ```
   ┌─────────┬─────────┐
   │ NW      │ NE      │
   │    •    │  •  •   │
   ├─────────┼─────────┤
   │ SW      │ SE      │
   │  •      │    •    │
   └─────────┴─────────┘
   ```

2. **Center of Mass Calculation:** Each cell stores aggregate position/strength of child nodes

3. **Force Approximation:** For distant clusters, treat entire cell as single node

### 2.2 Theta Parameter (θ)

The **theta** parameter controls approximation accuracy:

```javascript
simulation.force('charge', d3.forceManyBody().theta(0.9));
```

**Theta Trade-offs:**

| Theta | Accuracy | Performance | Use Case |
|-------|----------|-------------|----------|
| 0.0 | Exact (no approximation) | O(n²) - very slow | N/A - defeats purpose |
| 0.5 | High accuracy | Slower | High-quality static layouts |
| **0.9** (default) | Good balance | Fast | Most use cases |
| 1.2 | Lower accuracy | Faster | Quick previews, large graphs |

**Formula:** If `w / l < theta`, approximate the entire cell as a single node
- `w` = cell width
- `l` = distance from node to cell center

Source: [D3 Many-Body Force Documentation](https://d3js.org/d3-force/many-body)

### 2.3 d3-force-reuse Optimization

The [d3-force-reuse library](https://github.com/twosixlabs/d3-force-reuse) provides significant performance gains by **reusing quadtrees**.

**Key Insight:** Quadtree construction is O(n log n), but node positions change slowly during simulation.

**Implementation:**
```javascript
import { forceSimulation } from 'd3-force';
import { forceManyBodyReuse } from 'd3-force-reuse';

const simulation = forceSimulation(nodes)
  .force('charge', forceManyBodyReuse()
    .theta(0.9)
    .schedule({ uniform: 13 })  // Recompute every 13 ticks
  );
```

**Performance Gains:**
- **10% to 90% faster** depending on graph characteristics
- Optimal schedule: **every 13-14 iterations** (uniform schedule)
- Works by amortizing quadtree construction cost

**Research:** ["It Pays to Be Lazy: Reusing Force Approximations"](https://twosixtech.com/blog/faster-force-directed-graph-layouts-by-reusing-force-approximations/) by Robert Gove

---

## 3. Force Primitives

### 3.1 Built-in Forces

**forceCenter:**
```javascript
simulation.force('center', d3.forceCenter(width / 2, height / 2));
```
- Complexity: **O(n)** - very fast
- Prevents graph drift
- Use: Always include for stability

**forceCollide:**
```javascript
simulation.force('collide', d3.forceCollide(radius).iterations(2));
```
- Complexity: **O(n log n)** with quadtree
- Prevents node overlap
- Iterations: 1-3 (more = better separation, slower)

**forceLink:**
```javascript
simulation.force('link', d3.forceLink(links).id(d => d.id).distance(100));
```
- Complexity: **O(e)** where e = edge count
- Creates spring-like connections
- Critical for connected graphs

**forceManyBody:**
```javascript
simulation.force('charge', d3.forceManyBody().strength(-30).distanceMax(500));
```
- Complexity: **O(n log n)** with Barnes-Hut
- Creates repulsion (negative strength) or attraction (positive)
- **distanceMax:** Limits interaction range → huge performance gain for large graphs

**Performance Best Practice for 100k+ Nodes:**
```javascript
simulation
  .force('charge', d3.forceManyBody()
    .strength(-30)
    .distanceMax(200)  // CRITICAL: Limit interaction distance
    .theta(0.9)
  )
  .force('link', d3.forceLink(links).distance(50))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .velocityDecay(0.4);  // Damping: higher = faster settling
```

### 3.2 Custom Forces

**Pattern:**
```javascript
function customForce(alpha) {
  return function(alpha) {
    nodes.forEach(node => {
      // Apply custom force to node.vx, node.vy
      node.vx += someCalculation(node) * alpha;
      node.vy += someCalculation(node) * alpha;
    });
  };
}

simulation.force('custom', customForce);
```

**Performance Impact:**
- Custom forces run **every tick**
- Keep calculations **O(1) per node** for O(n) overall
- Avoid nested loops (leads to O(n²))

**Example: Boundary Force (O(n))**
```javascript
function boundaryForce(x0, y0, x1, y1) {
  const strength = 0.1;
  return function(alpha) {
    nodes.forEach(node => {
      if (node.x < x0) node.vx += (x0 - node.x) * strength * alpha;
      if (node.x > x1) node.vx += (x1 - node.x) * strength * alpha;
      if (node.y < y0) node.vy += (y0 - node.y) * strength * alpha;
      if (node.y > y1) node.vy += (y1 - node.y) * strength * alpha;
    });
  };
}
```

---

## 4. React Integration Patterns

### 4.1 DOM Ownership Approaches

**Three Strategies:**

1. **React for DOM, D3 for Math** (Recommended for small graphs)
   - React renders SVG elements
   - D3 calculates positions
   - React owns lifecycle

2. **Hybrid: React Structure, D3 Details** (Balanced)
   - React renders container/structure
   - D3 manipulates internal elements
   - Clear boundary via refs

3. **D3 Full Control** (Best for performance)
   - React renders empty container
   - D3 owns all internals (Canvas/WebGL)
   - React only provides container ref

Source: [Working with React and D3 together](https://gist.github.com/alexcjohnson/a4b714eee8afd2123ee00cb5b3278a5f)

### 4.2 useRef + useEffect Pattern

**Standard Approach:**
```typescript
import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

function ForceGraph({ nodes, links }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(width / 2, height / 2));

    // D3 renders inside ref
    const node = svg.selectAll('.node')
      .data(nodes)
      .join('circle')
      .attr('class', 'node');

    simulation.on('tick', () => {
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });

    return () => simulation.stop(); // Cleanup
  }, [nodes, links]);

  return <svg ref={svgRef} width={800} height={600} />;
}
```

Source: [Simple D3 with React Hooks](https://medium.com/@jeffbutsch/using-d3-in-react-with-hooks-4a6c61f1d102)

### 4.3 Custom useD3 Hook

**Reusable Hook Pattern:**
```typescript
import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

function useD3(renderFn, dependencies) {
  const ref = useRef();

  useEffect(() => {
    renderFn(d3.select(ref.current));
    return () => {}; // Cleanup if needed
  }, dependencies);

  return ref;
}

// Usage
function Graph({ data }) {
  const ref = useD3(
    (svg) => {
      // D3 code here
      svg.selectAll('circle')
        .data(data)
        .join('circle')
        .attr('r', 5);
    },
    [data] // Re-run when data changes
  );

  return <svg ref={ref} />;
}
```

Source: [React Hooks and D3](https://observablehq.com/@herrstucki/react-hooks-and-d3)

### 4.4 Canvas Integration Pattern

**For Large Graphs (10k+ nodes):**
```typescript
import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

function CanvasGraph({ nodes, links }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(width / 2, height / 2));

    simulation.on('tick', () => {
      context.clearRect(0, 0, width, height);

      // Draw links
      context.strokeStyle = '#999';
      links.forEach(link => {
        context.beginPath();
        context.moveTo(link.source.x, link.source.y);
        context.lineTo(link.target.x, link.target.y);
        context.stroke();
      });

      // Draw nodes
      context.fillStyle = '#69b3a2';
      nodes.forEach(node => {
        context.beginPath();
        context.arc(node.x, node.y, 5, 0, 2 * Math.PI);
        context.fill();
      });
    });

    return () => simulation.stop();
  }, [nodes, links]);

  return <canvas ref={canvasRef} width={800} height={600} />;
}
```

---

## 5. react-d3-graph Library Analysis

### 5.1 Status and Maintenance

**Library:** [react-d3-graph](https://github.com/danielcaldas/react-d3-graph)

**Current Status (2026):**
- Latest version: **2.6.0** (last published **5 years ago**)
- **NOT ACTIVELY MAINTAINED** ❌
- Last significant update: ~2021

**Verdict:** **NOT RECOMMENDED** for new projects

### 5.2 Feature Completeness

**Strengths (when last maintained):**
- Interactive and configurable out-of-box
- React-friendly API
- Force-directed layout built-in
- Good for small-to-medium graphs (< 1000 nodes)

**Limitations:**
- Performance issues at scale
- No WebGL rendering option
- Limited customization for advanced use cases

### 5.3 Modern Alternatives (2026)

**Better Options:**

1. **[Recharts](https://recharts.org/)** (24.8k+ stars)
   - Actively maintained
   - Excellent documentation
   - Limited force-directed support (not specialized for graphs)

2. **[visx](https://airbnb.io/visx/)** (19k+ stars)
   - Low-level D3 + React primitives
   - High flexibility
   - Steep learning curve
   - Good for custom force graphs

3. **[Nivo](https://nivo.rocks/)** (13k+ stars)
   - Multiple rendering methods
   - Good performance
   - Limited graph network support

4. **[react-force-graph](https://github.com/vasturiano/react-force-graph)** (Recommended for graphs)
   - Based on d3-force
   - WebGL rendering option
   - Better maintained
   - **Supports ngraph.forcelayout** as alternative engine

**Recommendation for 100k+ Nodes:**
- Build custom solution: D3-force (computation) + PixiJS (rendering)
- Use react-force-graph if WebGL rendering sufficient

Sources:
- [Best React chart libraries (2025 update)](https://blog.logrocket.com/best-react-chart-libraries-2025/)
- [15 Best React JS Chart Libraries in 2026](https://technostacks.com/blog/react-chart-libraries/)

---

## 6. Optimization Techniques

### 6.1 Web Worker Simulation

**Why:** Offload CPU-intensive force calculations to prevent UI freezing.

**Implementation Pattern:**

**Main Thread (React Component):**
```typescript
import { useRef, useEffect, useState } from 'react';

function ForceGraph({ nodes, links }) {
  const [positions, setPositions] = useState(nodes);
  const workerRef = useRef<Worker>();

  useEffect(() => {
    // Create worker
    workerRef.current = new Worker(
      new URL('./force-worker.ts', import.meta.url)
    );

    // Send initial data
    workerRef.current.postMessage({ nodes, links, type: 'init' });

    // Listen for position updates
    workerRef.current.onmessage = (e) => {
      if (e.data.type === 'tick') {
        setPositions(e.data.nodes); // Update UI
      }
    };

    return () => workerRef.current?.terminate();
  }, [nodes, links]);

  return (
    <canvas>
      {/* Render positions */}
    </canvas>
  );
}
```

**Web Worker (force-worker.ts):**
```typescript
import * as d3 from 'd3-force';

let simulation: d3.Simulation<any, any>;

self.onmessage = (e) => {
  if (e.data.type === 'init') {
    const { nodes, links } = e.data;

    simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(400, 300));

    simulation.on('tick', () => {
      // Send positions to main thread
      self.postMessage({ type: 'tick', nodes });
    });

    simulation.on('end', () => {
      self.postMessage({ type: 'end' });
    });
  }
};
```

**Performance Gain:**
- **UI remains responsive** during computation
- Can run simulation at full speed without frame drops
- **Critical for graphs > 5,000 nodes**

Sources:
- [Force-directed web worker](https://observablehq.com/@d3/force-directed-web-worker)
- [Force Simulation with Web Worker](https://gist.github.com/ch-bu/33226a03aef07c290a9cfb50abd8cfb9)

### 6.2 Reduced/Adaptive Tick Rate

**Strategy:** Don't update rendering every tick—throttle visual updates.

**Implementation:**
```typescript
let tickCounter = 0;
const RENDER_EVERY_N_TICKS = 5; // Render every 5th tick

simulation.on('tick', () => {
  tickCounter++;

  if (tickCounter % RENDER_EVERY_N_TICKS === 0) {
    render(); // Update canvas/DOM
  }
});
```

**Adaptive Throttling:**
```typescript
function getThrottleRate(alpha) {
  if (alpha > 0.5) return 10; // Early: low quality, high speed
  if (alpha > 0.1) return 5;  // Mid: balanced
  return 1;                   // Late: high quality, every tick
}

simulation.on('tick', () => {
  const throttle = getThrottleRate(simulation.alpha());
  if (tickCounter++ % throttle === 0) {
    render();
  }
});
```

**Trade-offs:**
- Visual smoothness vs. performance
- Early simulation: choppy but fast
- Late simulation: smooth final arrangement

### 6.3 Viewport-Based Force Optimization

**Concept:** Apply forces only to visible nodes or use simplified forces for distant nodes.

**Implementation:**
```typescript
// Custom force that considers viewport
function viewportAwareForce(visibleBounds) {
  return function(alpha) {
    nodes.forEach(node => {
      const isVisible = (
        node.x >= visibleBounds.x0 &&
        node.x <= visibleBounds.x1 &&
        node.y >= visibleBounds.y0 &&
        node.y <= visibleBounds.y1
      );

      if (isVisible) {
        // Apply full precision forces
        // ... normal force calculations
      } else {
        // Simplified forces or skip
        // Just prevent infinite drift
        node.vx *= 0.95;
        node.vy *= 0.95;
      }
    });
  };
}
```

**Viewport Culling:**
- Only render nodes within camera view
- Use [pixi-cull](https://github.com/davidfig/pixi-cull) with PixiJS

Source: [Scale up your D3 graph visualisation, part 2](https://medium.com/neo4j/scale-up-your-d3-graph-visualisation-part-2-2726a57301ec)

### 6.4 Clustering Distant Nodes

**Approach:** Group distant nodes into meta-nodes.

**Benefits:**
- Reduce effective node count
- O(n log n) becomes O(m log m) where m << n
- Better UX (aggregated view)

**Not implemented in D3 by default—requires custom logic or third-party libraries.**

---

## 7. Canvas Rendering Deep Dive

### 7.1 Canvas vs SVG Performance

**SVG Characteristics:**
- **Retained mode:** Browser maintains DOM tree of shapes
- Easy event handling (each element = DOM node)
- Poor performance: **~1,000 node limit**

**Canvas Characteristics:**
- **Immediate mode:** Pixel buffer, no DOM elements
- Excellent performance: **10,000+ nodes feasible**
- Harder event handling (no individual elements)

**Benchmark (10,000 rows):**
| Method | Render Time |
|--------|-------------|
| D3 + SVG | 682 ms |
| D3 + Canvas | 173 ms |
| **Speedup** | **~4x faster** |

Sources:
- [Implementing Charts that Scale with D3 and Canvas](https://medium.com/@xoor/implementing-charts-that-scale-with-d3-and-canvas-3e14bbe70f37)
- [How many SVGs before performance issues?](https://groups.google.com/g/d3-js/c/ZJ6pznVU5LQ/m/wLYuIGPUnvsJ)

### 7.2 Event Handling with Canvas

**Challenge:** Canvas is a single pixel buffer—can't attach listeners to individual nodes.

**Solution: Virtual Canvas Technique**

```typescript
class CanvasGraph {
  canvas: HTMLCanvasElement;
  virtualCanvas: HTMLCanvasElement; // Hidden canvas
  colorToNode: Map<string, Node>;   // Color → Node mapping

  constructor(canvas) {
    this.canvas = canvas;
    this.virtualCanvas = document.createElement('canvas');
    this.virtualCanvas.width = canvas.width;
    this.virtualCanvas.height = canvas.height;
    this.colorToNode = new Map();
  }

  render() {
    const ctx = this.canvas.getContext('2d');
    const vCtx = this.virtualCanvas.getContext('2d');

    nodes.forEach((node, i) => {
      // Render visible node normally
      ctx.fillStyle = node.color;
      ctx.beginPath();
      ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
      ctx.fill();

      // Render unique color on virtual canvas
      const uniqueColor = `rgb(${i % 256}, ${Math.floor(i / 256) % 256}, ${Math.floor(i / 65536)})`;
      this.colorToNode.set(uniqueColor, node);
      vCtx.fillStyle = uniqueColor;
      vCtx.beginPath();
      vCtx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
      vCtx.fill();
    });
  }

  handleClick(event) {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Sample virtual canvas
    const vCtx = this.virtualCanvas.getContext('2d');
    const pixel = vCtx.getImageData(x, y, 1, 1).data;
    const color = `rgb(${pixel[0]}, ${pixel[1]}, ${pixel[2]})`;

    const node = this.colorToNode.get(color);
    if (node) {
      console.log('Clicked node:', node);
    }
  }
}
```

Source: [Rendering One Million Datapoints with D3 and WebGL](https://blog.scottlogic.com/2020/05/01/rendering-one-million-points-with-d3.html)

### 7.3 requestAnimationFrame Optimization

**Standard Pattern:**
```typescript
function render() {
  context.clearRect(0, 0, width, height);

  // Draw graph
  drawLinks();
  drawNodes();
}

simulation.on('tick', render); // BAD: Renders every tick
```

**Optimized Pattern:**
```typescript
let frameRequested = false;
let needsRender = false;

function scheduleRender() {
  needsRender = true;
  if (!frameRequested) {
    frameRequested = true;
    requestAnimationFrame(() => {
      if (needsRender) {
        render();
        needsRender = false;
      }
      frameRequested = false;
    });
  }
}

simulation.on('tick', scheduleRender);
```

**Benefits:**
- Syncs with browser refresh (60 FPS)
- Avoids wasted renders
- Smoother animation

### 7.4 Dirty Flag Pattern

**Concept:** Only re-render when data actually changes.

```typescript
let isDirty = false;

simulation.on('tick', () => {
  isDirty = true;
});

function renderLoop() {
  if (isDirty) {
    render();
    isDirty = false;
  }
  requestAnimationFrame(renderLoop);
}

renderLoop();
```

---

## 8. WebGL Hybrid Approaches

### 8.1 Why WebGL for 100k+ Nodes

**Canvas Limitations:**
- CPU-bound rendering
- Practical limit: ~10,000 interactive nodes
- No GPU acceleration

**WebGL Advantages:**
- **GPU-accelerated** rendering
- Can handle **millions of points**
- Batch rendering via shaders

**Trade-off:** Increased complexity

### 8.2 D3-Force + PixiJS Pattern

**Architecture:**
```
D3-Force (layout calculation) → PixiJS (WebGL rendering)
         ↓                              ↓
   Compute positions              GPU batch render
```

**Implementation Example:**

```typescript
import * as d3 from 'd3-force';
import * as PIXI from 'pixi.js';

// Setup PixiJS renderer
const app = new PIXI.Application({
  width: 800,
  height: 600,
  backgroundColor: 0x1a1a1a,
  antialias: true,
});

// Create sprite pool (reuse sprites)
const nodeSprites = nodes.map(node => {
  const sprite = new PIXI.Graphics();
  sprite.beginFill(0x69b3a2);
  sprite.drawCircle(0, 0, 5);
  sprite.endFill();
  app.stage.addChild(sprite);
  return sprite;
});

// D3 force simulation
const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links))
  .force('charge', d3.forceManyBody())
  .force('center', d3.forceCenter(400, 300));

// Update sprite positions each tick
simulation.on('tick', () => {
  nodes.forEach((node, i) => {
    nodeSprites[i].position.set(node.x, node.y);
  });
});
```

**Key Optimization: Use Sprites**
- PixiJS batches sprites into single WebGL draw call
- Much faster than individual Graphics objects

Source: [Scale Up D3 Graph Visualization with PIXI.js](https://graphaware.com/blog/scale-up-your-d3-graph-visualisation-webgl-canvas-with-pixi-js/)

### 8.3 D3 + PixiJS Advanced Patterns

**Particle Container (Maximum Performance):**
```typescript
import { ParticleContainer, Sprite, Texture } from 'pixi.js';

// Pre-create texture
const texture = PIXI.Texture.from('/node-sprite.png');

// Particle container for batch rendering
const particleContainer = new PIXI.ParticleContainer(100000, {
  position: true,
  rotation: false,
  uvs: false,
  tint: false,
});

const sprites = nodes.map(node => {
  const sprite = new PIXI.Sprite(texture);
  sprite.anchor.set(0.5);
  particleContainer.addChild(sprite);
  return sprite;
});

app.stage.addChild(particleContainer);

// Update positions from D3 simulation
simulation.on('tick', () => {
  nodes.forEach((node, i) => {
    sprites[i].position.set(node.x, node.y);
  });
});
```

**Performance:**
- ParticleContainer: **100,000+ sprites** at 60 FPS
- Regular Container: **~10,000 sprites** at 60 FPS

**Limitation:** ParticleContainer has limited interactivity

### 8.4 Web Worker + PixiJS Architecture

**Optimal Setup for 100k+ Nodes:**

```
┌─────────────────┐         ┌─────────────────┐
│   Web Worker    │         │   Main Thread   │
│                 │         │                 │
│  D3 Simulation  │ ─────> │  PixiJS Render  │
│  (positions)    │  JSON   │  (sprites)      │
└─────────────────┘         └─────────────────┘
     CPU bound                  GPU accelerated
```

**Benefits:**
- Simulation doesn't block UI
- Rendering uses GPU
- Can run simulation at different rate than rendering (e.g., 10 ticks/frame)

**Code Structure:**

**worker.ts:**
```typescript
import * as d3 from 'd3-force';

let simulation;

self.onmessage = (e) => {
  if (e.data.type === 'init') {
    simulation = d3.forceSimulation(e.data.nodes)
      .force('link', d3.forceLink(e.data.links))
      .force('charge', d3.forceManyBody().distanceMax(200))
      .force('center', d3.forceCenter(400, 300));

    simulation.on('tick', () => {
      // Send positions every N ticks
      if (simulation.alpha() % 0.01 < 0.005) {
        self.postMessage({
          type: 'positions',
          nodes: e.data.nodes.map(n => ({ x: n.x, y: n.y })),
        });
      }
    });
  }
};
```

**main.tsx:**
```typescript
const worker = new Worker(new URL('./worker.ts', import.meta.url));

worker.postMessage({ type: 'init', nodes, links });

worker.onmessage = (e) => {
  if (e.data.type === 'positions') {
    // Update PixiJS sprites
    e.data.nodes.forEach((pos, i) => {
      sprites[i].position.set(pos.x, pos.y);
    });
  }
};
```

Sources:
- [Creating a Force Graph using React, D3 and PixiJS](https://dev.to/gilfink/creating-a-force-graph-using-react-d3-and-pixijs-182n)
- [d3-webworker-pixijs experiment](https://github.com/markuslerner/d3-webworker-pixijs)

---

## 9. 100k+ Node Strategy

### 9.1 Known Performance Ceiling

**Realistic Limits (Web Browser):**

| Approach | Node Limit | Notes |
|----------|------------|-------|
| SVG (D3 only) | ~1,000 | DOM bottleneck |
| Canvas (D3 + manual render) | ~10,000 | CPU rendering limit |
| **WebGL (D3 + PixiJS)** | **~100,000** | GPU accelerated |
| WebGL (optimized clustering) | 500,000+ | With aggressive optimization |

**Memory Constraints:**
- 100k nodes × 10 properties × 8 bytes ≈ **8 MB** (manageable)
- Edges: 500k edges × 2 pointers × 8 bytes ≈ **8 MB**
- Total: **~20-50 MB** for data structures (acceptable)

**Bottlenecks:**
1. **Force calculation:** O(n log n) per tick → Web Worker required
2. **Rendering:** GPU required (PixiJS/WebGL)
3. **Interactivity:** Virtual canvas technique or spatial indexing

### 9.2 Hybrid Rendering Strategy

**Approach: Level-of-Detail (LOD)**

```typescript
const LOD_LEVELS = {
  FULL_DETAIL: { zoom: 2.0, nodeSize: 8, showLabels: true },
  MEDIUM: { zoom: 1.0, nodeSize: 5, showLabels: false },
  LOW: { zoom: 0.5, nodeSize: 3, clusters: true },
};

function render(zoomLevel) {
  const lod = getLOD(zoomLevel);

  if (lod.clusters) {
    // Render aggregated clusters
    renderClusters(metaNodes);
  } else {
    // Render individual nodes
    renderNodes(nodes, lod.nodeSize, lod.showLabels);
  }
}
```

**Graph Clustering Example:**
```typescript
import { hierarchy, cluster } from 'd3-hierarchy';

function clusterGraph(nodes, links, threshold) {
  // Use community detection (e.g., Louvain algorithm)
  const communities = detectCommunities(nodes, links);

  // Create meta-nodes
  const metaNodes = communities.map(community => ({
    id: `cluster-${community.id}`,
    size: community.nodes.length,
    nodes: community.nodes,
    x: d3.mean(community.nodes, d => d.x),
    y: d3.mean(community.nodes, d => d.y),
  }));

  return metaNodes;
}
```

**Drill-Down Interaction:**
- Zoomed out: Show meta-nodes (clusters)
- Zoomed in: Expand cluster, show individual nodes
- Dynamically adjust visible node count

Source: [D3-Force Directed Graph Layout Optimization in NebulaGraph Studio](https://www.nebula-graph.io/posts/d3-force-layout-optimization)

### 9.3 Viewport Culling for 100k Nodes

**Technique:** Only render nodes within camera viewport.

**Implementation with PixiJS:**
```typescript
import Cull from 'pixi-cull';

const cull = new Cull.Simple();
cull.addList(nodeSprites); // All sprites
cull.cull(app.renderer.screen); // Cull to viewport

// On pan/zoom
function onViewportChange() {
  cull.cull(app.renderer.screen);
  // Only culled (visible) sprites are rendered
}
```

**Performance Gain:**
- 100k nodes, viewport shows 5%: **Render only 5,000 nodes**
- Massive FPS improvement

**Caveat:** Force simulation still processes all nodes (unless using viewport-aware forces)

Source: [Scale up your D3 graph visualisation, part 2](https://medium.com/neo4j/scale-up-your-d3-graph-visualisation-part-2-2726a57301ec)

### 9.4 Progressive/Lazy Loading

**Strategy:** Load and simulate nodes in chunks.

**Implementation:**
```typescript
async function loadGraphInChunks(graphData, chunkSize = 10000) {
  const chunks = chunkArray(graphData.nodes, chunkSize);

  for (let i = 0; i < chunks.length; i++) {
    // Add chunk to simulation
    simulation.nodes([...simulation.nodes(), ...chunks[i]]);

    // Warm restart simulation
    simulation.alpha(0.3).restart();

    // Wait for stabilization
    await new Promise(resolve => {
      const check = () => {
        if (simulation.alpha() < 0.05) {
          resolve();
        } else {
          requestAnimationFrame(check);
        }
      };
      check();
    });
  }
}
```

**User Experience:**
- Show initial graph quickly (first 10k nodes)
- Progressively add more nodes
- Maintain interactivity throughout

---

## 10. ngraph.forcelayout vs d3-force

### 10.1 Feature Comparison

| Feature | d3-force | ngraph.forcelayout |
|---------|----------|-------------------|
| **Algorithm** | Barnes-Hut | Custom physics engine |
| **Dimensions** | 2D, 3D (d3-force-3d) | 1D, 2D, 3D, N-D |
| **Complexity** | O(n log n) | O(n log n) |
| **Customization** | High (many force types) | Medium |
| **React Integration** | Manual | Manual |
| **WebGL Support** | Via PixiJS | Via custom render |
| **Ecosystem** | Large (D3 ecosystem) | Smaller (ngraph family) |
| **Documentation** | Excellent | Good |
| **Maintenance** | Active (D3 team) | Active (anvaka) |

Sources:
- [ngraph.forcelayout](https://github.com/anvaka/ngraph.forcelayout)
- [d3-force documentation](https://d3js.org/d3-force)

### 10.2 Performance Characteristics

**ngraph.forcelayout Optimizations:**
- Ad-hoc code generation for vector algebra
- Dimension-specific optimizations
- Optimized for performance-first

**d3-force Optimizations:**
- Well-established Barnes-Hut implementation
- Rich ecosystem (d3-force-reuse, etc.)
- More battle-tested at scale

**Community Feedback:**
- "D3 force layout is just for example purposes... not going to perform [for large graphs]"
- "For hobbyists exploring network visualization, ngraph or react-force-graph would be good options"

**Benchmark Gap:** No public head-to-head benchmarks available (as of 2026)

### 10.3 Recommendation

**Use d3-force if:**
- You need rich ecosystem (D3 integration)
- Extensive customization (custom forces)
- React integration (many examples)
- Hybrid rendering (PixiJS patterns well-documented)

**Use ngraph.forcelayout if:**
- Purely performance-focused
- Higher-dimensional layouts (>3D)
- Prefer lightweight library
- Part of ngraph ecosystem (ngraph.graph, etc.)

**For 100k+ Nodes:**
- **Either can work** with proper optimization (Web Worker + WebGL)
- **d3-force + PixiJS** has more tutorials/examples
- Consider [react-force-graph](https://github.com/vasturiano/react-force-graph) which **supports both engines**

Source: [A Comparison of Javascript Graph / Network Visualisation Libraries](https://www.cylynx.io/blog/a-comparison-of-javascript-graph-network-visualisation-libraries/)

---

## 11. Implementation Recommendations

### 11.1 Architecture for 100k+ Nodes

**Recommended Stack:**
```
┌────────────────────────────────────────┐
│         React Component Layer          │
│  - State management                    │
│  - User interactions                   │
│  - Controls (zoom, pan, filters)       │
└────────────────┬───────────────────────┘
                 │
┌────────────────▼───────────────────────┐
│       PixiJS Rendering Layer           │
│  - WebGL acceleration                  │
│  - Sprite batching                     │
│  - Viewport culling (pixi-cull)        │
│  - Virtual canvas for events           │
└────────────────┬───────────────────────┘
                 │
┌────────────────▼───────────────────────┐
│      Web Worker: D3 Simulation         │
│  - Force calculation                   │
│  - Position updates                    │
│  - Send positions → Main thread        │
└────────────────────────────────────────┘
```

### 11.2 Optimization Checklist

**For 100k+ Node Performance:**

- [ ] **Use WebGL rendering** (PixiJS ParticleContainer)
- [ ] **Offload simulation to Web Worker**
- [ ] **Limit force interaction distance** (`distanceMax`)
- [ ] **Reuse quadtrees** (d3-force-reuse)
- [ ] **Implement viewport culling** (pixi-cull)
- [ ] **Use adaptive tick rates** (fewer renders during early simulation)
- [ ] **Cluster distant nodes** (meta-nodes at low zoom)
- [ ] **Virtual canvas for events** (hit detection)
- [ ] **Progressive loading** (if applicable)
- [ ] **Level-of-detail rendering** (zoom-based quality)

### 11.3 Code Template

**Complete Example:**

```typescript
// React component
import { useEffect, useRef } from 'react';
import * as PIXI from 'pixi.js';
import Cull from 'pixi-cull';

function LargeForceGraph({ nodes, links }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application>();
  const workerRef = useRef<Worker>();

  useEffect(() => {
    if (!containerRef.current) return;

    // Setup PixiJS
    const app = new PIXI.Application({
      width: 1200,
      height: 800,
      backgroundColor: 0x1a1a1a,
      resolution: window.devicePixelRatio,
    });
    containerRef.current.appendChild(app.view);
    appRef.current = app;

    // Create particle container for nodes
    const particleContainer = new PIXI.ParticleContainer(nodes.length, {
      position: true,
      scale: true,
      tint: true,
    });
    app.stage.addChild(particleContainer);

    // Create sprites
    const texture = PIXI.Texture.from('/node.png');
    const sprites = nodes.map(() => {
      const sprite = new PIXI.Sprite(texture);
      sprite.anchor.set(0.5);
      particleContainer.addChild(sprite);
      return sprite;
    });

    // Setup viewport culling
    const cull = new Cull.Simple();
    cull.addList(sprites);

    // Create Web Worker for simulation
    const worker = new Worker(
      new URL('./force-worker.ts', import.meta.url)
    );
    workerRef.current = worker;

    worker.postMessage({
      type: 'init',
      nodes: nodes.map((n, i) => ({ ...n, index: i })),
      links,
      width: 1200,
      height: 800,
    });

    // Listen for position updates
    worker.onmessage = (e) => {
      if (e.data.type === 'tick') {
        e.data.positions.forEach((pos, i) => {
          sprites[i].position.set(pos.x, pos.y);
        });
        cull.cull(app.renderer.screen);
      }
    };

    // Cleanup
    return () => {
      worker.terminate();
      app.destroy(true);
    };
  }, [nodes, links]);

  return <div ref={containerRef} />;
}

export default LargeForceGraph;
```

**Web Worker (force-worker.ts):**
```typescript
import * as d3 from 'd3-force';
import { forceManyBodyReuse } from 'd3-force-reuse';

let simulation;
let tickCount = 0;

self.onmessage = (e) => {
  if (e.data.type === 'init') {
    const { nodes, links, width, height } = e.data;

    simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(50))
      .force('charge', forceManyBodyReuse()
        .strength(-30)
        .distanceMax(200)
        .theta(0.9)
      )
      .force('center', d3.forceCenter(width / 2, height / 2))
      .velocityDecay(0.4)
      .alphaDecay(0.02);

    simulation.on('tick', () => {
      tickCount++;

      // Send positions every 3 ticks (throttle)
      if (tickCount % 3 === 0) {
        self.postMessage({
          type: 'tick',
          positions: nodes.map(n => ({ x: n.x, y: n.y })),
          alpha: simulation.alpha(),
        });
      }
    });
  }
};
```

### 11.4 When NOT to Use D3-Force for 100k+ Nodes

**Consider Alternatives If:**

1. **Graph is highly dynamic** (frequent add/remove)
   - Alternative: Static layout (Graphviz, etc.)

2. **Graph is hierarchical**
   - Alternative: Tree layouts (d3-hierarchy)

3. **Precise positioning required**
   - Alternative: Manual layout or grid-based

4. **Mobile/low-power devices**
   - Alternative: Server-side layout, send static positions

5. **Need instant results**
   - Alternative: Pre-computed layouts

6. **Graph has >500k nodes**
   - Alternative: Database-level graph processing (Neo4j, etc.) + aggregated view

---

## 12. Summary and Decision Matrix

### 12.1 Viability Assessment: 100k+ Nodes

| Requirement | Feasible? | Implementation |
|-------------|-----------|----------------|
| Render 100k nodes | ✅ Yes | PixiJS ParticleContainer (WebGL) |
| Interactive simulation | ⚠️ Limited | Web Worker + chunked updates |
| Smooth 60 FPS | ⚠️ Conditional | Viewport culling + LOD required |
| Event handling | ✅ Yes | Virtual canvas or spatial index |
| React integration | ✅ Yes | Custom hooks + refs |
| Real-time updates | ❌ No | Too expensive; use static layout |

**Overall Verdict:** **Feasible with significant engineering effort**

### 12.2 Effort vs. Capability Matrix

```
High Capability
    │
    │                        ┌────────────────┐
    │                        │ D3 + PixiJS    │
    │                        │ + Web Worker   │
    │                        │ + Culling      │
    │                        └────────────────┘
    │
    │             ┌────────────────┐
    │             │ D3 + Canvas    │
    │             │ + Events       │
    │             └────────────────┘
    │
    │  ┌────────────────┐
    │  │ D3 + SVG       │
    │  │ (Basic)        │
    │  └────────────────┘
    │
Low Capability
    └──────────────────────────────────> High Effort
        Low Effort
```

### 12.3 Recommended Path Forward

**For 100k+ Nodes in Production:**

1. **Evaluate if force-directed is necessary**
   - Consider hierarchical, static, or pre-computed layouts first

2. **If force-directed required:**
   - Start with [react-force-graph](https://github.com/vasturiano/react-force-graph) (supports WebGL)
   - Benchmark with your data

3. **If custom solution needed:**
   - Follow architecture in Section 11.1
   - Implement incrementally:
     1. Canvas proof-of-concept
     2. Add PixiJS rendering
     3. Move simulation to Web Worker
     4. Add viewport culling
     5. Implement clustering/LOD

4. **Performance testing at each stage**
   - Measure FPS, memory, simulation convergence time
   - Test on target devices (especially mobile)

### 12.4 Quick Reference: Key Takeaways

**D3-Force Strengths:**
- Excellent algorithm (O(n log n))
- Rich ecosystem and documentation
- Highly customizable
- Works well up to ~10k nodes (Canvas)

**D3-Force Weaknesses:**
- Rendering is bottleneck, not algorithm
- Requires WebGL for 100k+ nodes
- Complex React integration at scale
- Real-time updates expensive

**Critical Optimizations:**
1. **Web Worker** for simulation
2. **PixiJS** for rendering
3. **Viewport culling**
4. **distanceMax** to limit force range
5. **Clustering** for UX

**Best Alternative Libraries:**
- [react-force-graph](https://github.com/vasturiano/react-force-graph) (WebGL built-in)
- [ngraph.forcelayout](https://github.com/anvaka/ngraph.forcelayout) (performance-focused)
- [Sigma.js](https://www.sigmajs.org/) (graph visualization, not force-directed)

---

## References

### Performance & Benchmarks
- [Large Quantity Force Layout Performance - D3 Issue #1936](https://github.com/d3/d3/issues/1936)
- [Implementing Charts that Scale with D3 and Canvas](https://medium.com/@xoor/implementing-charts-that-scale-with-d3-and-canvas-3e14bbe70f37)
- [Optimizing D3 Chart Performance for Large Data Sets](https://reintech.io/blog/optimizing-d3-chart-performance-large-data)
- [How many SVGs before performance issues?](https://groups.google.com/g/d3-js/c/ZJ6pznVU5LQ/m/wLYuIGPUnvsJ)

### Barnes-Hut & Quadtree
- [The Barnes-Hut Approximation](https://jheer.github.io/barnes-hut/)
- [Faster force-directed graph layouts by reusing force approximations](https://twosixtech.com/blog/faster-force-directed-graph-layouts-by-reusing-force-approximations/)
- [d3-force-reuse library](https://github.com/twosixlabs/d3-force-reuse)
- [D3 Many-Body Force Documentation](https://d3js.org/d3-force/many-body)

### React Integration
- [Simple D3 with React Hooks](https://medium.com/@jeffbutsch/using-d3-in-react-with-hooks-4a6c61f1d102)
- [React Hooks and D3](https://observablehq.com/@herrstucki/react-hooks-and-d3)
- [Working with React and D3 together](https://gist.github.com/alexcjohnson/a4b714eee8afd2123ee00cb5b3278a5f)
- [D3, React, and using 'refs'](https://medium.com/@mautayro/d3-react-and-using-refs-e25b9a817a43)

### Canvas Rendering
- [Learnings from a d3.js addict on starting with canvas](https://www.visualcinnamon.com/2015/11/learnings-from-a-d3-js-addict-on-starting-with-canvas/)
- [Rendering One Million Datapoints with D3 and WebGL](https://blog.scottlogic.com/2020/05/01/rendering-one-million-points-with-d3.html)
- [D3 Round Two: How to Blend HTML5 Canvas with SVG](https://www.mongodb.com/blog/post/d3-round-two-how-blend-html5-canvas-svg-speed-up-rendering)

### Web Workers
- [Force-directed web worker - D3 Observable](https://observablehq.com/@d3/force-directed-web-worker)
- [Force Simulation with Web Worker](https://gist.github.com/ch-bu/33226a03aef07c290a9cfb50abd8cfb9)
- [D3 Force Simulations Documentation](https://d3js.org/d3-force/simulation)

### WebGL & PixiJS
- [Scale Up D3 Graph Visualization with PIXI.js](https://graphaware.com/blog/scale-up-your-d3-graph-visualisation-webgl-canvas-with-pixi-js/)
- [Creating a Force Graph using React, D3 and PixiJS](https://dev.to/gilfink/creating-a-force-graph-using-react-d3-and-pixijs-182n)
- [Scale up your D3 graph visualisation, part 2](https://medium.com/neo4j/scale-up-your-d3-graph-visualisation-part-2-2726a57301ec)
- [d3-webworker-pixijs experiment](https://github.com/markuslerner/d3-webworker-pixijs)

### Libraries & Comparisons
- [react-d3-graph](https://github.com/danielcaldas/react-d3-graph)
- [Best React chart libraries (2025 update)](https://blog.logrocket.com/best-react-chart-libraries-2025/)
- [ngraph.forcelayout](https://github.com/anvaka/ngraph.forcelayout)
- [A Comparison of Javascript Graph / Network Visualisation Libraries](https://www.cylynx.io/blog/a-comparison-of-javascript-graph-network-visualisation-libraries/)

### Optimization Techniques
- [D3-Force Directed Graph Layout Optimization in NebulaGraph Studio](https://www.nebula-graph.io/posts/d3-force-layout-optimization)
- [The Best Libraries and Methods to Render Large Force-Directed Graphs on the Web](https://weber-stephen.medium.com/the-best-libraries-and-methods-to-render-large-network-graphs-on-the-web-d122ece2f4dc)

---

**Document Status:** Complete
**Last Updated:** 2026-02-01
**Next Review:** When implementing 100k+ node visualization
