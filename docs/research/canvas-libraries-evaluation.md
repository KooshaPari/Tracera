# Canvas-Based Rendering Libraries Evaluation for 100k+ Node Graph Visualization

**Date:** 2026-02-01
**Scope:** Evaluate canvas rendering solutions for massive-scale graph visualization (100k+ nodes)
**Objective:** Recommend optimal rendering strategy for high-performance graph visualization

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Performance Comparison Matrix](#performance-comparison-matrix)
3. [Library Deep Dives](#library-deep-dives)
4. [Hybrid Strategies](#hybrid-strategies)
5. [Custom Implementation Guide](#custom-implementation-guide)
6. [Code Examples](#code-examples)
7. [Final Recommendation](#final-recommendation)

---

## Executive Summary

For rendering 100k+ node graphs, **PixiJS v8 with ParticleContainer is the clear winner** for pure rendering performance, achieving 1,000,000 particles at 60fps. However, the optimal solution depends on interactivity requirements:

- **Pure Performance (minimal interaction):** PixiJS v8 + ParticleContainer + WebGL
- **Rich Interactivity:** Hybrid approach (PixiJS background + selective Canvas foreground)
- **Moderate Scale (<50k nodes):** Konva.js with FastLayers
- **Custom Control:** Raw Canvas API + OffscreenCanvas + WebWorkers

**Key Insight:** No single library handles all requirements at 100k+ scale. Hybrid architectures combining WebGL for bulk rendering with Canvas for interactive elements provide the best balance.

---

## Performance Comparison Matrix

| Library | Rendering Mode | Max Nodes (60fps) | Memory Usage | Interaction Cost | React Integration | TypeScript Support | Learning Curve |
|---------|---------------|-------------------|--------------|------------------|-------------------|-------------------|----------------|
| **PixiJS v8** | WebGL | 1,000,000+ (particles) | High | Medium | react-pixi (6 FPS with text) | Excellent | Medium |
| **Konva.js** | Canvas 2D | 10,000 (interactive) | Medium | High | react-konva (9 FPS) | Good | Low |
| **Fabric.js** | Canvas 2D | ~10,000 (slow at 17k×7k canvas) | High | Very High | Limited | Good | Medium |
| **Raw Canvas** | Canvas 2D | 50,000+ (optimized) | Low-Medium | Custom | Custom | N/A | High |
| **OffscreenCanvas** | Canvas 2D (Worker) | 100,000+ (batch rendered) | Medium | None (background) | Custom | Excellent | High |
| **Hybrid (PixiJS + Canvas)** | WebGL + Canvas 2D | 100,000+ | Medium-High | Low-Medium | Custom | Good | Very High |

### Performance Characteristics

**PixiJS v8:**
- [ParticleContainer can handle 1,000,000 particles at 60fps](https://pixijs.com/blog/particlecontainer-v8) on modern hardware
- [Optimized rendering loop updates only changed elements](https://pixijs.com/8.x/guides/concepts/performance-tips)
- WebGPU backend available for improved batch handling
- [react-pixi-fiber: 48 FPS without text, 6 FPS with text at 1000 items](https://github.com/ryohey/react-canvas-perf)

**Konva.js:**
- [Stress test handles 10,000 shapes](https://konvajs.org/docs/sandbox/Resizing_Stress_Test.html) with optimization
- [FastLayers render 2x faster than normal layers](https://konvajs.org/docs/performance/Layer_Management.html) but lack interactivity
- [react-konva: 9 FPS with text, 26 FPS without text at 1000 items](https://github.com/ryohey/react-canvas-perf)
- [Shape caching dramatically improves performance for complex shapes](https://konvajs.org/docs/performance/Shape_Caching.html)

**Fabric.js:**
- [Performance issues with large canvases (17126×7677) and 10k objects](https://github.com/fabricjs/fabric.js/issues/1855)
- [StaticCanvas improves performance when interactivity not needed](https://github.com/fabricjs/fabric.js/wiki/Optimizing-performance)
- Object caching helps but viewport zooming invalidates cache

**Raw Canvas + OffscreenCanvas:**
- [OffscreenCanvas decouples rendering from DOM for speed improvements](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas)
- [Batched rendering with drawImage reduces complexity from O(n) path operations to O(n) image blits](https://blog.ag-grid.com/optimising-html5-canvas-rendering-best-practices-and-techniques/)
- [WebWorker rendering enables true parallelism](https://web.dev/articles/offscreen-canvas)

---

## Library Deep Dives

### 1. Konva.js

**Best For:** Interactive applications with moderate node counts (<50k)

#### Performance Optimization

**Layer Management:**
```typescript
// CRITICAL: Use 3-5 layers maximum
const backgroundLayer = new Konva.Layer();
const edgesLayer = new Konva.Layer();
const nodesLayer = new Konva.Layer();
const interactionLayer = new Konva.Layer();
```

[Layer management is the most important performance consideration](https://konvajs.org/docs/performance/Layer_Management.html)

**FastLayer for Static Content:**
```typescript
// 2x faster rendering, no mouse interaction
const staticEdgesLayer = new Konva.FastLayer();
```

**Shape Caching:**
```typescript
// Cache complex nodes as bitmaps
complexNode.cache();
complexNode.drawHitFromCache(); // Use cached version for hit detection
```

[Shape caching creates internal images to avoid recomposing from drawing instructions](https://konvajs.org/docs/performance/Shape_Caching.html)

**Disable Event Listening:**
```typescript
// For layers with thousands of shapes
staticLayer.listening(false);
```

[Each event listener adds overhead when checking which to trigger](https://konvajs.org/docs/performance/All_Performance_Tips.html)

#### React Integration (react-konva)

[React-konva provides declarative canvas API](https://konvajs.org/docs/react/index.html) with TypeScript support:

```typescript
import { Stage, Layer, Circle, Line } from 'react-konva';
import { KonvaEventObject } from 'konva/lib/Node';

interface Node {
  id: string;
  x: number;
  y: number;
  color: string;
}

const GraphView: React.FC<{ nodes: Node[] }> = ({ nodes }) => {
  const handleNodeClick = (e: KonvaEventObject<MouseEvent>) => {
    console.log('Clicked:', e.target.id());
  };

  return (
    <Stage width={window.innerWidth} height={window.innerHeight}>
      <Layer listening={false}> {/* Static edges layer */}
        {/* Render edges here */}
      </Layer>
      <Layer> {/* Interactive nodes layer */}
        {nodes.slice(0, 5000).map(node => ( // Limit rendered nodes
          <Circle
            key={node.id}
            id={node.id}
            x={node.x}
            y={node.y}
            radius={5}
            fill={node.color}
            onClick={handleNodeClick}
          />
        ))}
      </Layer>
    </Stage>
  );
};
```

**Event Delegation:**
[Use layer-level events for efficiency](https://konvajs.org/docs/events/Event_Delegation.html):

```typescript
<Layer onClick={(e) => {
  const shape = e.target;
  console.log('Clicked shape:', shape.getClassName());
}}>
  {/* Child shapes inherit events */}
</Layer>
```

#### Limitations at 100k+ Nodes

- Canvas 2D rendering becomes CPU-bound
- Event handling overhead with thousands of shapes
- Memory usage grows with node complexity
- [Performance degrades significantly beyond 10k nodes](https://konvajs.org/docs/sandbox/Resizing_Stress_Test.html)

**Verdict:** Excellent for <10k nodes with rich interactivity. Not suitable for 100k+ without culling.

---

### 2. PixiJS v8

**Best For:** Maximum rendering performance with 100k+ sprites/particles

#### ParticleContainer - The Game Changer

[PixiJS v8's ParticleContainer achieves jaw-dropping performance, rendering 100K+ particles without breaking a sweat](https://pixijs.com/blog/particlecontainer-v8):

```typescript
import { Application, ParticleContainer, Texture, Sprite } from 'pixi.js';

const app = new Application();
await app.init({
  width: window.innerWidth,
  height: window.innerHeight,
  antialias: true
});

// ParticleContainer optimized for 100k+ sprites
const particles = new ParticleContainer(100000, {
  position: true,    // Allow position updates
  rotation: true,    // Allow rotation updates
  uvs: false,        // Static texture coordinates
  tint: true,        // Allow color tint
  alpha: false       // Static alpha
});

// Only enable dynamic properties you need
// Each dynamic property adds computational cost

const nodeTexture = Texture.from('node-circle.png');

for (let i = 0; i < 100000; i++) {
  const sprite = new Sprite(nodeTexture);
  sprite.x = Math.random() * app.screen.width;
  sprite.y = Math.random() * app.screen.height;
  particles.addChild(sprite);
}

app.stage.addChild(particles);
```

**Performance Characteristics:**
- [1,000,000 particles at 60fps on M3 MacBook Pro](https://pixijs.com/blog/particlecontainer-v8)
- [Particles are lightweight, lacking children, events, or filters](https://pixijs.com/8.x/guides/components/scene-objects/particle-container)
- [Dynamic properties are recalculated and uploaded to GPU each frame](https://pixijs.com/8.x/guides/components/scene-objects/particle-container)

#### Batch Rendering Optimization

[PixiJS automatically batches draw calls to reduce GPU overhead](https://pixijs.com/8.x/guides/concepts/performance-tips):

```typescript
// GOOD: Grouped by type for batching
sprites.forEach(sprite => stage.addChild(sprite));
graphics.forEach(graphic => stage.addChild(graphic));

// BAD: Alternating types breaks batches
items.forEach(item => {
  if (item.type === 'sprite') stage.addChild(sprite);
  else stage.addChild(graphic);
});
```

**Batch Limits:**
- [Up to 16 different textures per batch (hardware dependent)](https://pixijs.com/8.x/guides/concepts/performance-tips)
- Filters, masks, and blend modes break batches

#### WebGPU Backend

[PixiJS v8 includes WebGPU support for modern browsers](https://pixijs.com/blog/pixi-v8-launches):

```typescript
import { Application } from 'pixi.js';

const app = new Application();
await app.init({
  preference: 'webgpu', // Prefer WebGPU
  width: 1920,
  height: 1080
});

console.log(app.renderer.type); // 'webgpu' if supported
```

**WebGPU Benefits:**
- [Better performance for scenes with batch breaks (filters, masks, blend modes)](https://pixijs.com/blog/pixi-v8-beta)
- More modern rendering approach
- [Does not automatically guarantee better performance - often CPU-bound](https://pixijs.com/blog/pixi-v8-beta)

#### React Integration (react-pixi)

[React-pixi provides React fiber renderer for PixiJS](https://github.com/pixijs/pixi-react):

```typescript
import { Stage, Container, Sprite } from '@pixi/react';
import { useMemo } from 'react';

interface NodeData {
  id: string;
  x: number;
  y: number;
}

const GraphRenderer: React.FC<{ nodes: NodeData[] }> = ({ nodes }) => {
  // Memoize to prevent recreation
  const nodeSprites = useMemo(() =>
    nodes.map(node => (
      <Sprite
        key={node.id}
        image="/node-texture.png"
        x={node.x}
        y={node.y}
        anchor={0.5}
      />
    )),
    [nodes]
  );

  return (
    <Stage width={1920} height={1080} options={{ antialias: true }}>
      <Container>
        {nodeSprites}
      </Container>
    </Stage>
  );
};
```

**Performance Caveat:**
[Benchmark shows react-pixi at 6 FPS with text, 48 FPS without at 1000 items](https://github.com/ryohey/react-canvas-perf) - React reconciliation overhead is significant.

**Recommendation:** Use imperative PixiJS API for 100k+ nodes, not React wrapper.

#### Limitations

- [ParticleContainer sprites lack events, children, and filters](https://pixijs.com/8.x/guides/components/scene-objects/particle-container)
- Interaction requires custom hit detection
- Memory usage grows with texture count
- React integration adds overhead

**Verdict:** Unmatched rendering performance for 100k+ nodes. Requires custom interaction layer.

---

### 3. Fabric.js

**Best For:** Rich object manipulation, SVG integration (not recommended for 100k+ nodes)

#### Performance Characteristics

[Fabric.js shows performance issues at scale](https://github.com/fabricjs/fabric.js/issues/1855):
- ~10k objects with large canvas (17126×7677) causes slow browser response
- Object-heavy model increases memory usage
- Selection and manipulation overhead at scale

#### Optimization Techniques

**Static Canvas:**
[Use StaticCanvas when interactivity not needed](https://github.com/fabricjs/fabric.js/wiki/Optimizing-performance):

```typescript
import { StaticCanvas } from 'fabric';

const canvas = new StaticCanvas('canvas');
// No selection, events, or transformations
// Significantly faster rendering
```

**Disable Render on Add/Remove:**
```typescript
canvas.renderOnAddRemove = false;

// Batch add objects
objects.forEach(obj => canvas.add(obj));

// Manual render after batch
canvas.requestRenderAll();
```

**Object Caching:**
[Cache complex objects as bitmaps](https://fabricjs.com/docs/fabric-object-caching/):

```typescript
const complexObject = new fabric.Group([/* many shapes */]);
complexObject.set({ objectCaching: true });
```

**Caching Pitfalls:**
- [Viewport zooming invalidates all caches (forces redraw)](https://fabricjs.com/docs/fabric-object-caching/)
- Memory overhead for cached bitmaps

#### Limitations at 100k+ Nodes

- Not designed for extreme scale
- Heavy object model (each shape is full object with properties)
- Poor performance with large canvases
- Memory-intensive

**Verdict:** Not recommended for 100k+ nodes. Better suited for editors with rich object manipulation.

---

### 4. Raw Canvas API

**Best For:** Maximum control and performance ceiling

#### Performance Ceiling

[Raw Canvas API provides best possible performance](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas) when optimized correctly:

```typescript
const canvas = document.getElementById('graph-canvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d', {
  alpha: false,           // Opaque canvas (faster compositing)
  desynchronized: true,   // Reduced latency
  willReadFrequently: false // Optimize for write operations
});

// Pre-render nodes to offscreen canvas
const nodeCanvas = document.createElement('canvas');
const nodeCtx = nodeCanvas.getContext('2d')!;
nodeCanvas.width = 10;
nodeCanvas.height = 10;

// Draw node template once
nodeCtx.fillStyle = '#3498db';
nodeCtx.beginPath();
nodeCtx.arc(5, 5, 5, 0, Math.PI * 2);
nodeCtx.fill();

// Batch render using drawImage (O(1) per node)
interface Node {
  x: number;
  y: number;
  color: string;
}

function renderNodes(nodes: Node[]) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Render all nodes with single draw call pattern
  for (const node of nodes) {
    ctx.drawImage(nodeCanvas, node.x - 5, node.y - 5);
  }
}
```

[Batched rendering with drawImage reduces complexity](https://blog.ag-grid.com/optimising-html5-canvas-rendering-best-practices-and-techniques/) from O(n) path operations to O(n) simple blits.

#### OffscreenCanvas + Web Workers

[OffscreenCanvas decouples rendering from DOM for true parallelism](https://web.dev/articles/offscreen-canvas):

**Main Thread:**
```typescript
const offscreen = canvas.transferControlToOffscreen();
const worker = new Worker('graph-renderer.worker.js');

worker.postMessage(
  {
    canvas: offscreen,
    nodes: nodeData
  },
  [offscreen] // Transfer ownership
);
```

**Worker (graph-renderer.worker.ts):**
```typescript
let ctx: OffscreenCanvasRenderingContext2D;

self.onmessage = (e) => {
  const { canvas, nodes } = e.data;

  if (canvas) {
    ctx = canvas.getContext('2d')!;
  }

  if (nodes && ctx) {
    renderGraph(nodes);
  }
};

function renderGraph(nodes: Array<{ x: number; y: number }>) {
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

  // Batch rendering
  ctx.fillStyle = '#3498db';
  nodes.forEach(node => {
    ctx.beginPath();
    ctx.arc(node.x, node.y, 5, 0, Math.PI * 2);
    ctx.fill();
  });
}
```

**Performance Benefits:**
- [Rendering fully detached from DOM - no synchronization overhead](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas)
- [True parallelism on multi-core systems](https://web.dev/articles/offscreen-canvas)
- Main thread remains responsive during heavy rendering

#### ImageBitmap Optimization

[ImageBitmap provides efficient image transfer between canvases](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas):

```typescript
// In worker
const offscreen = new OffscreenCanvas(100, 100);
const ctx = offscreen.getContext('2d')!;

// Render node template
ctx.fillStyle = '#3498db';
ctx.beginPath();
ctx.arc(50, 50, 50, 0, Math.PI * 2);
ctx.fill();

// Transfer to main thread without copy
const bitmap = await offscreen.transferToImageBitmap();
self.postMessage({ bitmap }, [bitmap]);
```

**Note:** [Firefox had performance issues with transferToImageBitmap that were addressed in 2024](https://bugzilla.mozilla.org/show_bug.cgi?id=1788206).

#### Spatial Indexing for Culling

Combine Canvas with spatial data structures for efficient viewport culling:

```typescript
class QuadTree<T extends { x: number; y: number }> {
  private boundary: Rectangle;
  private capacity: number;
  private points: T[] = [];
  private divided: boolean = false;
  private northwest?: QuadTree<T>;
  private northeast?: QuadTree<T>;
  private southwest?: QuadTree<T>;
  private southeast?: QuadTree<T>;

  constructor(boundary: Rectangle, capacity: number = 4) {
    this.boundary = boundary;
    this.capacity = capacity;
  }

  insert(point: T): boolean {
    if (!this.boundary.contains(point)) return false;

    if (this.points.length < this.capacity) {
      this.points.push(point);
      return true;
    }

    if (!this.divided) this.subdivide();

    return (
      this.northwest!.insert(point) ||
      this.northeast!.insert(point) ||
      this.southwest!.insert(point) ||
      this.southeast!.insert(point)
    );
  }

  query(range: Rectangle, found: T[] = []): T[] {
    if (!this.boundary.intersects(range)) return found;

    for (const p of this.points) {
      if (range.contains(p)) found.push(p);
    }

    if (this.divided) {
      this.northwest!.query(range, found);
      this.northeast!.query(range, found);
      this.southwest!.query(range, found);
      this.southeast!.query(range, found);
    }

    return found;
  }

  private subdivide() {
    const { x, y, w, h } = this.boundary;
    const halfW = w / 2;
    const halfH = h / 2;

    this.northwest = new QuadTree(new Rectangle(x, y, halfW, halfH), this.capacity);
    this.northeast = new QuadTree(new Rectangle(x + halfW, y, halfW, halfH), this.capacity);
    this.southwest = new QuadTree(new Rectangle(x, y + halfH, halfW, halfH), this.capacity);
    this.southeast = new QuadTree(new Rectangle(x + halfW, y + halfH, halfW, halfH), this.capacity);

    this.divided = true;
  }
}

class Rectangle {
  constructor(
    public x: number,
    public y: number,
    public w: number,
    public h: number
  ) {}

  contains(point: { x: number; y: number }): boolean {
    return (
      point.x >= this.x &&
      point.x <= this.x + this.w &&
      point.y >= this.y &&
      point.y <= this.y + this.h
    );
  }

  intersects(range: Rectangle): boolean {
    return !(
      range.x > this.x + this.w ||
      range.x + range.w < this.x ||
      range.y > this.y + this.h ||
      range.y + range.h < this.y
    );
  }
}

// Usage with Canvas rendering
const quadTree = new QuadTree<Node>(
  new Rectangle(0, 0, canvas.width, canvas.height)
);

// Insert all nodes
nodes.forEach(node => quadTree.insert(node));

// Render only visible nodes
function render(viewport: Rectangle) {
  const visibleNodes = quadTree.query(viewport);

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  visibleNodes.forEach(node => {
    ctx.fillRect(node.x, node.y, 5, 5);
  });
}
```

[Quadtree spatial indexing efficiently determines visible objects within camera frustum](https://www.mdpi.com/2075-5309/15/16/2916).

#### Memory Management

[ECMAScript 2021's FinalizationRegistry enables automatic resource cleanup](https://app.studyraid.com/en/read/12533/405940/memory-management-strategies):

```typescript
const registry = new FinalizationRegistry<() => void>((cleanup) => {
  cleanup();
});

class CanvasPool {
  private pool: HTMLCanvasElement[] = [];
  private maxSize = 10;

  acquire(width: number, height: number): HTMLCanvasElement {
    const canvas = this.pool.pop() || document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    return canvas;
  }

  release(canvas: HTMLCanvasElement): void {
    if (this.pool.length < this.maxSize) {
      const ctx = canvas.getContext('2d')!;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      this.pool.push(canvas);
    }
  }
}

// Reuse canvases instead of creating new ones
const pool = new CanvasPool();
```

[Reusing canvas instances by avoiding frequent createCanvas() calls significantly improves performance](https://app.studyraid.com/en/read/12533/405940/memory-management-strategies).

**Verdict:** Highest performance ceiling with complete control. Requires significant implementation effort.

---

## Hybrid Strategies

[Hybrid solutions often work best, combining technologies for optimal performance](https://medium.com/@beyons/building-a-high-performance-ui-framework-with-html5-canvas-and-webgl-f7628af8a3c2).

### Strategy 1: WebGL Background + Canvas Foreground

**Concept:** Render bulk graph with WebGL, overlay interactive elements with Canvas.

```typescript
import { Application, Graphics } from 'pixi.js';

// WebGL layer (PixiJS) for 100k nodes
const pixiApp = new Application();
await pixiApp.init({
  backgroundAlpha: 1,
  antialias: true
});
document.getElementById('graph-container')!.appendChild(pixiApp.canvas);

// Canvas layer for interaction highlights
const interactionCanvas = document.createElement('canvas');
interactionCanvas.style.position = 'absolute';
interactionCanvas.style.top = '0';
interactionCanvas.style.left = '0';
interactionCanvas.style.pointerEvents = 'none'; // Click through to PixiJS
document.getElementById('graph-container')!.appendChild(interactionCanvas);

const interactionCtx = interactionCanvas.getContext('2d')!;

// Render 100k nodes in PixiJS
function renderBulkNodes(nodes: NodeData[]) {
  const graphics = new Graphics();

  for (const node of nodes) {
    graphics.circle(node.x, node.y, 3);
    graphics.fill({ color: 0x3498db });
  }

  pixiApp.stage.addChild(graphics);
}

// Highlight selected nodes in Canvas
function highlightNode(node: NodeData) {
  interactionCtx.clearRect(0, 0, interactionCanvas.width, interactionCanvas.height);

  interactionCtx.strokeStyle = '#e74c3c';
  interactionCtx.lineWidth = 2;
  interactionCtx.beginPath();
  interactionCtx.arc(node.x, node.y, 8, 0, Math.PI * 2);
  interactionCtx.stroke();
}
```

**Benefits:**
- WebGL handles massive static rendering
- Canvas provides rich interaction without WebGL complexity
- Layers can be updated independently

**Drawbacks:**
- Increased memory (two rendering contexts)
- Synchronization complexity
- Hit detection must query both layers

### Strategy 2: Multi-Layer Static + Dynamic Split

**Concept:** Separate static (edges) and dynamic (nodes) into different layers/canvases.

```typescript
// Static layer (edges) - rarely updated
const edgesCanvas = document.createElement('canvas');
const edgesCtx = edgesCanvas.getContext('2d', {
  alpha: false,
  willReadFrequently: false
})!;

// Dynamic layer (nodes) - frequently updated
const nodesCanvas = document.createElement('canvas');
const nodesCtx = nodesCanvas.getContext('2d', {
  alpha: true,  // Transparent to show edges below
  willReadFrequently: false
})!;

// Render edges once (or rarely)
function renderEdges(edges: EdgeData[]) {
  edgesCtx.clearRect(0, 0, edgesCanvas.width, edgesCanvas.height);
  edgesCtx.strokeStyle = '#95a5a6';
  edgesCtx.lineWidth = 1;

  for (const edge of edges) {
    edgesCtx.beginPath();
    edgesCtx.moveTo(edge.x1, edge.y1);
    edgesCtx.lineTo(edge.x2, edge.y2);
    edgesCtx.stroke();
  }
}

// Render nodes frequently (animation, interaction)
function renderNodes(nodes: NodeData[]) {
  nodesCtx.clearRect(0, 0, nodesCanvas.width, nodesCanvas.height);

  for (const node of nodes) {
    nodesCtx.fillStyle = node.color;
    nodesCtx.fillRect(node.x - 2, node.y - 2, 4, 4);
  }
}

// Stack canvases
edgesCanvas.style.position = 'absolute';
nodesCanvas.style.position = 'absolute';
container.appendChild(edgesCanvas);
container.appendChild(nodesCanvas);
```

**Benefits:**
- Avoid re-rendering static content
- Reduced draw calls per frame
- Better cache utilization

**Drawbacks:**
- Complexity in layer management
- Memory overhead from multiple canvases

### Strategy 3: LOD (Level of Detail) Rendering

**Concept:** Render different detail levels based on zoom/viewport.

```typescript
interface RenderStrategy {
  minZoom: number;
  maxZoom: number;
  render: (nodes: NodeData[], ctx: CanvasRenderingContext2D) => void;
}

const strategies: RenderStrategy[] = [
  {
    minZoom: 0,
    maxZoom: 0.5,
    render: (nodes, ctx) => {
      // Far zoom: render as pixels
      ctx.fillStyle = '#3498db';
      nodes.forEach(node => ctx.fillRect(node.x, node.y, 1, 1));
    }
  },
  {
    minZoom: 0.5,
    maxZoom: 1.5,
    render: (nodes, ctx) => {
      // Medium zoom: small circles
      nodes.forEach(node => {
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, 3, 0, Math.PI * 2);
        ctx.fill();
      });
    }
  },
  {
    minZoom: 1.5,
    maxZoom: Infinity,
    render: (nodes, ctx) => {
      // Close zoom: circles + labels
      nodes.forEach(node => {
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#000';
        ctx.font = '10px Arial';
        ctx.fillText(node.label, node.x + 10, node.y);
      });
    }
  }
];

function renderWithLOD(nodes: NodeData[], zoom: number, ctx: CanvasRenderingContext2D) {
  const strategy = strategies.find(s => zoom >= s.minZoom && zoom < s.maxZoom);
  if (strategy) {
    strategy.render(nodes, ctx);
  }
}
```

**Benefits:**
- Optimal detail for zoom level
- Reduced rendering cost when zoomed out
- Better performance at all scales

**Drawbacks:**
- Implementation complexity
- Potential visual "popping" during transitions
- Requires careful tuning of thresholds

### Strategy 4: WebWorker Layout + Main Thread Rendering

**Concept:** Offload force-directed layout to worker, render results on main thread.

[Force-directed graphs use WebWorkers to offload physics simulations](https://observablehq.com/@zakjan/force-directed-graph-pixi):

**Main Thread:**
```typescript
// graph-manager.ts
const layoutWorker = new Worker(new URL('./layout.worker.ts', import.meta.url));

layoutWorker.onmessage = (e) => {
  const { nodes, edges } = e.data;
  renderGraph(nodes, edges);
};

// Send initial data
layoutWorker.postMessage({
  nodes: initialNodes,
  edges: initialEdges,
  config: { iterations: 100 }
});

function renderGraph(nodes: NodeData[], edges: EdgeData[]) {
  // Render using PixiJS or Canvas
  pixiApp.stage.removeChildren();

  const graphics = new Graphics();

  // Edges
  graphics.stroke({ color: 0x95a5a6, width: 1 });
  edges.forEach(edge => {
    graphics.moveTo(edge.source.x, edge.source.y);
    graphics.lineTo(edge.target.x, edge.target.y);
  });

  // Nodes
  nodes.forEach(node => {
    graphics.circle(node.x, node.y, 5);
    graphics.fill({ color: 0x3498db });
  });

  pixiApp.stage.addChild(graphics);
}
```

**Worker (layout.worker.ts):**
```typescript
// d3-force simulation in worker
import { forceSimulation, forceLink, forceManyBody, forceCenter } from 'd3-force';

self.onmessage = (e) => {
  const { nodes, edges, config } = e.data;

  const simulation = forceSimulation(nodes)
    .force('link', forceLink(edges).id((d: any) => d.id))
    .force('charge', forceManyBody().strength(-30))
    .force('center', forceCenter(960, 540));

  // Run simulation for N iterations
  for (let i = 0; i < config.iterations; i++) {
    simulation.tick();

    // Send progress updates
    if (i % 10 === 0) {
      self.postMessage({
        nodes: simulation.nodes(),
        edges,
        progress: (i / config.iterations) * 100
      });
    }
  }

  // Final state
  self.postMessage({
    nodes: simulation.nodes(),
    edges,
    complete: true
  });
};
```

[WebWorkers don't have DOM access, so expensive operations must be DOM-independent](https://observablehq.com/@zakjan/force-directed-graph-pixi).

**Benefits:**
- Main thread stays responsive during layout
- [True parallelism on multi-core CPUs](https://observablehq.com/@zakjan/force-directed-graph-pixi)
- Clean separation of concerns

**Drawbacks:**
- No DOM access in worker
- Serialization overhead for large datasets
- Can't use DOM-based libraries in worker

---

## Custom Implementation Guide

### Building a 100k Node Renderer from Scratch

**Architecture:**
1. **Spatial Indexing Layer:** QuadTree/R-tree for culling
2. **Rendering Layer:** OffscreenCanvas + Workers for parallel rendering
3. **Interaction Layer:** Lightweight hit detection
4. **Data Layer:** Efficient graph structure

**Step 1: Graph Data Structure**

```typescript
// Optimized graph structure
class GraphData {
  nodes: Float32Array; // [x, y, x, y, ...] packed positions
  edges: Uint32Array;  // [source_idx, target_idx, ...] indices into nodes
  colors: Uint32Array; // Packed RGBA colors

  constructor(nodeCount: number, edgeCount: number) {
    this.nodes = new Float32Array(nodeCount * 2);
    this.edges = new Uint32Array(edgeCount * 2);
    this.colors = new Uint32Array(nodeCount);
  }

  getNodePosition(index: number): { x: number; y: number } {
    return {
      x: this.nodes[index * 2],
      y: this.nodes[index * 2 + 1]
    };
  }

  setNodePosition(index: number, x: number, y: number): void {
    this.nodes[index * 2] = x;
    this.nodes[index * 2 + 1] = y;
  }
}
```

**Benefits:**
- Typed arrays for cache-friendly memory layout
- Transferable to Web Workers without copy
- Minimal memory overhead

**Step 2: Viewport Culling with QuadTree**

```typescript
// Build spatial index
class SpatialIndex {
  private tree: QuadTree<number>; // Store node indices

  constructor(private graph: GraphData, bounds: Rectangle) {
    this.tree = new QuadTree(bounds);
    this.rebuild();
  }

  rebuild(): void {
    this.tree.clear();

    const nodeCount = this.graph.nodes.length / 2;
    for (let i = 0; i < nodeCount; i++) {
      const pos = this.graph.getNodePosition(i);
      this.tree.insert({ ...pos, index: i });
    }
  }

  queryVisible(viewport: Rectangle): number[] {
    const results = this.tree.query(viewport);
    return results.map(r => r.index);
  }
}
```

**Step 3: Worker-Based Rendering**

```typescript
// Main thread - graph-renderer.ts
class GraphRenderer {
  private worker: Worker;
  private canvas: HTMLCanvasElement;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.worker = new Worker(new URL('./render.worker.ts', import.meta.url));

    const offscreen = canvas.transferControlToOffscreen();
    this.worker.postMessage({ canvas: offscreen }, [offscreen]);
  }

  render(visibleNodeIndices: number[], graph: GraphData, viewport: Rectangle): void {
    this.worker.postMessage({
      indices: visibleNodeIndices,
      nodes: graph.nodes,
      colors: graph.colors,
      viewport
    }, [
      graph.nodes.buffer,
      graph.colors.buffer
    ]);
  }
}

// Worker - render.worker.ts
let ctx: OffscreenCanvasRenderingContext2D;

self.onmessage = (e) => {
  if (e.data.canvas) {
    ctx = e.data.canvas.getContext('2d')!;
  }

  if (e.data.indices) {
    const { indices, nodes, colors, viewport } = e.data;
    renderNodes(indices, nodes, colors, viewport);
  }
};

function renderNodes(
  indices: number[],
  nodes: Float32Array,
  colors: Uint32Array,
  viewport: Rectangle
) {
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

  // Batch rendering
  for (const idx of indices) {
    const x = nodes[idx * 2] - viewport.x;
    const y = nodes[idx * 2 + 1] - viewport.y;
    const color = colors[idx];

    ctx.fillStyle = `rgba(${(color >> 24) & 0xff}, ${(color >> 16) & 0xff}, ${(color >> 8) & 0xff}, ${color & 0xff})`;
    ctx.fillRect(x - 2, y - 2, 4, 4);
  }
}
```

**Step 4: Efficient Hit Detection**

```typescript
class HitDetector {
  constructor(
    private graph: GraphData,
    private spatialIndex: SpatialIndex
  ) {}

  findNodeAtPoint(x: number, y: number, radius = 5): number | null {
    // Query small area around click
    const candidates = this.spatialIndex.queryVisible(
      new Rectangle(x - radius, y - radius, radius * 2, radius * 2)
    );

    // Check each candidate
    for (const idx of candidates) {
      const pos = this.graph.getNodePosition(idx);
      const dist = Math.hypot(pos.x - x, pos.y - y);

      if (dist <= radius) {
        return idx;
      }
    }

    return null;
  }
}
```

**Step 5: Integration Example**

```typescript
// Complete integration
class GraphVisualization {
  private graph: GraphData;
  private spatialIndex: SpatialIndex;
  private renderer: GraphRenderer;
  private hitDetector: HitDetector;
  private viewport: Rectangle;

  constructor(canvas: HTMLCanvasElement) {
    // Initialize with 100k nodes
    this.graph = new GraphData(100000, 300000);

    // Random positions
    for (let i = 0; i < 100000; i++) {
      this.graph.setNodePosition(
        i,
        Math.random() * 10000,
        Math.random() * 10000
      );
    }

    this.spatialIndex = new SpatialIndex(
      this.graph,
      new Rectangle(0, 0, 10000, 10000)
    );

    this.renderer = new GraphRenderer(canvas);
    this.hitDetector = new HitDetector(this.graph, this.spatialIndex);

    this.viewport = new Rectangle(0, 0, canvas.width, canvas.height);

    // Setup interaction
    canvas.addEventListener('click', this.handleClick.bind(this));

    // Initial render
    this.render();
  }

  render(): void {
    const visibleIndices = this.spatialIndex.queryVisible(this.viewport);
    console.log(`Rendering ${visibleIndices.length} / 100000 nodes`);

    this.renderer.render(visibleIndices, this.graph, this.viewport);
  }

  handleClick(e: MouseEvent): void {
    const rect = (e.target as HTMLCanvasElement).getBoundingClientRect();
    const x = e.clientX - rect.left + this.viewport.x;
    const y = e.clientY - rect.top + this.viewport.y;

    const nodeIdx = this.hitDetector.findNodeAtPoint(x, y);
    if (nodeIdx !== null) {
      console.log('Clicked node:', nodeIdx);
    }
  }

  pan(dx: number, dy: number): void {
    this.viewport.x += dx;
    this.viewport.y += dy;
    this.render();
  }

  zoom(factor: number, centerX: number, centerY: number): void {
    // Implement zoom logic
    this.viewport.w *= factor;
    this.viewport.h *= factor;
    this.render();
  }
}

// Usage
const canvas = document.getElementById('graph') as HTMLCanvasElement;
const viz = new GraphVisualization(canvas);
```

---

## Code Examples

### Example 1: PixiJS ParticleContainer with Spatial Culling

```typescript
import { Application, ParticleContainer, Sprite, Texture } from 'pixi.js';

interface Node {
  id: string;
  x: number;
  y: number;
  sprite?: Sprite;
}

class PixiGraphRenderer {
  private app: Application;
  private particles: ParticleContainer;
  private nodeTexture: Texture;
  private nodes: Node[] = [];

  async init(container: HTMLElement) {
    this.app = new Application();
    await this.app.init({
      width: container.clientWidth,
      height: container.clientHeight,
      antialias: true,
      autoDensity: true,
      resolution: window.devicePixelRatio || 1
    });

    container.appendChild(this.app.canvas);

    // Create node texture
    this.nodeTexture = await Texture.fromURL('/assets/node.png');

    // ParticleContainer for 100k nodes
    this.particles = new ParticleContainer(100000, {
      position: true,
      tint: true
    });

    this.app.stage.addChild(this.particles);
  }

  addNodes(nodes: Node[]) {
    this.nodes = nodes;

    nodes.forEach(node => {
      const sprite = new Sprite(this.nodeTexture);
      sprite.x = node.x;
      sprite.y = node.y;
      sprite.tint = 0x3498db;
      sprite.anchor.set(0.5);

      node.sprite = sprite;
      this.particles.addChild(sprite);
    });
  }

  updateVisibleNodes(viewport: { x: number; y: number; width: number; height: number }) {
    // Simple viewport culling
    this.nodes.forEach(node => {
      const isVisible = (
        node.x >= viewport.x &&
        node.x <= viewport.x + viewport.width &&
        node.y >= viewport.y &&
        node.y <= viewport.y + viewport.height
      );

      if (node.sprite) {
        node.sprite.visible = isVisible;
      }
    });
  }

  destroy() {
    this.app.destroy(true);
  }
}

// Usage
const renderer = new PixiGraphRenderer();
await renderer.init(document.getElementById('graph-container')!);

// Add 100k nodes
const nodes = Array.from({ length: 100000 }, (_, i) => ({
  id: `node-${i}`,
  x: Math.random() * 10000,
  y: Math.random() * 10000
}));

renderer.addNodes(nodes);
```

### Example 2: Konva with Layer Optimization

```typescript
import Konva from 'konva';
import { KonvaEventObject } from 'konva/lib/Node';

class KonvaGraphRenderer {
  private stage: Konva.Stage;
  private edgesLayer: Konva.FastLayer;
  private nodesLayer: Konva.Layer;
  private interactionLayer: Konva.Layer;

  constructor(container: HTMLDivElement) {
    this.stage = new Konva.Stage({
      container,
      width: container.clientWidth,
      height: container.clientHeight
    });

    // Static edges (no interaction)
    this.edgesLayer = new Konva.FastLayer();

    // Interactive nodes
    this.nodesLayer = new Konva.Layer();

    // Highlights (above everything)
    this.interactionLayer = new Konva.Layer();

    this.stage.add(this.edgesLayer);
    this.stage.add(this.nodesLayer);
    this.stage.add(this.interactionLayer);
  }

  addEdges(edges: Array<{ x1: number; y1: number; x2: number; y2: number }>) {
    // Batch edges into single shape for performance
    const line = new Konva.Line({
      points: edges.flatMap(e => [e.x1, e.y1, e.x2, e.y2]),
      stroke: '#95a5a6',
      strokeWidth: 1
    });

    this.edgesLayer.add(line);
    this.edgesLayer.batchDraw();
  }

  addNodes(nodes: Array<{ id: string; x: number; y: number }>) {
    // Limit to 5000 for performance
    const visibleNodes = nodes.slice(0, 5000);

    visibleNodes.forEach(node => {
      const circle = new Konva.Circle({
        id: node.id,
        x: node.x,
        y: node.y,
        radius: 5,
        fill: '#3498db',
        shadowBlur: 0
      });

      // Cache for performance
      circle.cache();

      circle.on('click', this.handleNodeClick.bind(this));
      circle.on('mouseenter', this.handleNodeHover.bind(this));
      circle.on('mouseleave', this.handleNodeLeave.bind(this));

      this.nodesLayer.add(circle);
    });

    this.nodesLayer.batchDraw();
  }

  private handleNodeClick(e: KonvaEventObject<MouseEvent>) {
    const nodeId = e.target.id();
    console.log('Clicked node:', nodeId);

    // Highlight in interaction layer
    this.interactionLayer.destroyChildren();

    const highlight = new Konva.Circle({
      x: e.target.x(),
      y: e.target.y(),
      radius: 10,
      stroke: '#e74c3c',
      strokeWidth: 2
    });

    this.interactionLayer.add(highlight);
    this.interactionLayer.batchDraw();
  }

  private handleNodeHover(e: KonvaEventObject<MouseEvent>) {
    document.body.style.cursor = 'pointer';
    e.target.to({ scaleX: 1.5, scaleY: 1.5, duration: 0.1 });
  }

  private handleNodeLeave(e: KonvaEventObject<MouseEvent>) {
    document.body.style.cursor = 'default';
    e.target.to({ scaleX: 1, scaleY: 1, duration: 0.1 });
  }

  destroy() {
    this.stage.destroy();
  }
}

// Usage
const container = document.getElementById('graph-container') as HTMLDivElement;
const renderer = new KonvaGraphRenderer(container);

// Add edges
renderer.addEdges([
  { x1: 100, y1: 100, x2: 200, y2: 200 },
  // ... more edges
]);

// Add nodes
renderer.addNodes([
  { id: 'node-1', x: 100, y: 100 },
  // ... more nodes (limit to 5000)
]);
```

### Example 3: Hybrid PixiJS + Canvas Interaction

```typescript
import { Application, Graphics } from 'pixi.js';

class HybridGraphRenderer {
  private pixiApp: Application;
  private interactionCanvas: HTMLCanvasElement;
  private interactionCtx: CanvasRenderingContext2D;
  private nodes: Array<{ id: string; x: number; y: number }> = [];

  async init(container: HTMLElement) {
    // WebGL layer (PixiJS)
    this.pixiApp = new Application();
    await this.pixiApp.init({
      width: container.clientWidth,
      height: container.clientHeight,
      backgroundAlpha: 1,
      antialias: true
    });

    container.appendChild(this.pixiApp.canvas);

    // Canvas interaction layer
    this.interactionCanvas = document.createElement('canvas');
    this.interactionCanvas.width = container.clientWidth;
    this.interactionCanvas.height = container.clientHeight;
    this.interactionCanvas.style.position = 'absolute';
    this.interactionCanvas.style.top = '0';
    this.interactionCanvas.style.left = '0';
    this.interactionCanvas.style.pointerEvents = 'auto';

    container.appendChild(this.interactionCanvas);

    this.interactionCtx = this.interactionCanvas.getContext('2d')!;

    // Setup interaction
    this.interactionCanvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    this.interactionCanvas.addEventListener('click', this.handleClick.bind(this));
  }

  renderNodes(nodes: Array<{ id: string; x: number; y: number }>) {
    this.nodes = nodes;

    // Render all nodes in PixiJS (WebGL)
    const graphics = new Graphics();

    nodes.forEach(node => {
      graphics.circle(node.x, node.y, 3);
      graphics.fill({ color: 0x3498db });
    });

    this.pixiApp.stage.addChild(graphics);
  }

  private findNodeAtPoint(x: number, y: number, radius = 10): typeof this.nodes[0] | null {
    // Simple distance check (use QuadTree for 100k+ nodes)
    for (const node of this.nodes) {
      const dist = Math.hypot(node.x - x, node.y - y);
      if (dist <= radius) {
        return node;
      }
    }
    return null;
  }

  private handleMouseMove(e: MouseEvent) {
    const rect = this.interactionCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const node = this.findNodeAtPoint(x, y);

    // Clear interaction layer
    this.interactionCtx.clearRect(0, 0, this.interactionCanvas.width, this.interactionCanvas.height);

    if (node) {
      // Draw hover highlight
      this.interactionCtx.strokeStyle = '#e74c3c';
      this.interactionCtx.lineWidth = 2;
      this.interactionCtx.beginPath();
      this.interactionCtx.arc(node.x, node.y, 8, 0, Math.PI * 2);
      this.interactionCtx.stroke();

      // Tooltip
      this.interactionCtx.fillStyle = 'rgba(0, 0, 0, 0.8)';
      this.interactionCtx.fillRect(node.x + 10, node.y - 20, 60, 20);
      this.interactionCtx.fillStyle = '#fff';
      this.interactionCtx.font = '12px Arial';
      this.interactionCtx.fillText(node.id, node.x + 15, node.y - 6);

      this.interactionCanvas.style.cursor = 'pointer';
    } else {
      this.interactionCanvas.style.cursor = 'default';
    }
  }

  private handleClick(e: MouseEvent) {
    const rect = this.interactionCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const node = this.findNodeAtPoint(x, y);
    if (node) {
      console.log('Clicked node:', node.id);

      // Permanent highlight
      this.interactionCtx.strokeStyle = '#2ecc71';
      this.interactionCtx.lineWidth = 3;
      this.interactionCtx.setLineDash([5, 5]);
      this.interactionCtx.beginPath();
      this.interactionCtx.arc(node.x, node.y, 12, 0, Math.PI * 2);
      this.interactionCtx.stroke();
      this.interactionCtx.setLineDash([]);
    }
  }

  destroy() {
    this.pixiApp.destroy(true);
    this.interactionCanvas.remove();
  }
}

// Usage
const renderer = new HybridGraphRenderer();
await renderer.init(document.getElementById('graph-container')!);

// Render 100k nodes
const nodes = Array.from({ length: 100000 }, (_, i) => ({
  id: `node-${i}`,
  x: Math.random() * 1920,
  y: Math.random() * 1080
}));

renderer.renderNodes(nodes);
```

### Example 4: Force-Directed Layout in WebWorker

```typescript
// force-layout.worker.ts
import { forceSimulation, forceLink, forceManyBody, forceCenter, SimulationNodeDatum } from 'd3-force';

interface GraphData {
  nodes: Array<{ id: string; x?: number; y?: number }>;
  edges: Array<{ source: string; target: string }>;
}

self.onmessage = (e: MessageEvent) => {
  const { nodes, edges, config } = e.data as {
    nodes: GraphData['nodes'];
    edges: GraphData['edges'];
    config: { width: number; height: number; iterations: number };
  };

  // Create simulation
  const simulation = forceSimulation(nodes as SimulationNodeDatum[])
    .force('link', forceLink(edges).id((d: any) => d.id).distance(30))
    .force('charge', forceManyBody().strength(-50))
    .force('center', forceCenter(config.width / 2, config.height / 2))
    .stop(); // Manual ticking

  // Run iterations
  for (let i = 0; i < config.iterations; i++) {
    simulation.tick();

    // Send progress updates every 10%
    if (i % Math.floor(config.iterations / 10) === 0) {
      self.postMessage({
        type: 'progress',
        progress: (i / config.iterations) * 100,
        nodes: simulation.nodes()
      });
    }
  }

  // Send final result
  self.postMessage({
    type: 'complete',
    nodes: simulation.nodes()
  });
};

// Main thread - graph-layout-manager.ts
class GraphLayoutManager {
  private worker: Worker;
  private onProgress?: (progress: number, nodes: any[]) => void;
  private onComplete?: (nodes: any[]) => void;

  constructor() {
    this.worker = new Worker(new URL('./force-layout.worker.ts', import.meta.url));

    this.worker.onmessage = (e) => {
      if (e.data.type === 'progress' && this.onProgress) {
        this.onProgress(e.data.progress, e.data.nodes);
      } else if (e.data.type === 'complete' && this.onComplete) {
        this.onComplete(e.data.nodes);
      }
    };
  }

  computeLayout(
    nodes: Array<{ id: string }>,
    edges: Array<{ source: string; target: string }>,
    config: { width: number; height: number; iterations: number }
  ): Promise<Array<{ id: string; x: number; y: number }>> {
    return new Promise((resolve) => {
      this.onComplete = resolve;

      this.worker.postMessage({ nodes, edges, config });
    });
  }

  onProgressUpdate(callback: (progress: number, nodes: any[]) => void) {
    this.onProgress = callback;
  }

  terminate() {
    this.worker.terminate();
  }
}

// Usage
const layoutManager = new GraphLayoutManager();

layoutManager.onProgressUpdate((progress, nodes) => {
  console.log(`Layout ${progress.toFixed(0)}% complete`);
  // Optionally render intermediate states
});

const finalNodes = await layoutManager.computeLayout(
  nodes,
  edges,
  { width: 1920, height: 1080, iterations: 300 }
);

// Render final layout
renderer.renderNodes(finalNodes);
```

---

## Final Recommendation

### For 100k+ Node Graph Visualization

**Primary Recommendation: Hybrid PixiJS + Custom Canvas Interaction**

```
Architecture:
┌─────────────────────────────────────────┐
│  Interaction Layer (Canvas 2D)          │  ← Hover, tooltips, selection
│  - Transparent overlay                  │
│  - Spatial index for hit detection      │
│  - Custom drawing for highlights        │
├─────────────────────────────────────────┤
│  Rendering Layer (PixiJS WebGL)         │  ← 100k+ nodes bulk rendering
│  - ParticleContainer for nodes          │
│  - Graphics for edges                   │
│  - Viewport culling                     │
├─────────────────────────────────────────┤
│  Layout Layer (WebWorker)               │  ← Compute positions
│  - d3-force simulation                  │
│  - Incremental updates                  │
│  - Transferable ArrayBuffers            │
└─────────────────────────────────────────┘
```

### Implementation Strategy

**Phase 1: Foundation (Week 1)**
1. Setup PixiJS with ParticleContainer
2. Implement basic node rendering (10k nodes)
3. Add simple pan/zoom
4. Verify 60fps performance

**Phase 2: Scaling (Week 2)**
5. Integrate QuadTree spatial indexing
6. Implement viewport culling
7. Scale to 100k nodes
8. Optimize memory usage

**Phase 3: Interaction (Week 3)**
9. Add Canvas interaction layer
10. Implement hit detection via spatial index
11. Add hover effects and tooltips
12. Implement selection

**Phase 4: Layout (Week 4)**
13. Setup WebWorker for force-directed layout
14. Integrate d3-force
15. Add incremental rendering during layout
16. Polish animations

### Technology Stack

```typescript
{
  "rendering": "PixiJS v8 (WebGL)",
  "interaction": "Raw Canvas 2D API",
  "layout": "d3-force in WebWorker",
  "spatial": "Custom QuadTree",
  "framework": "React (minimal integration)",
  "typescript": "5.0+"
}
```

### Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Render 100k nodes | 60 FPS | PixiJS ParticleContainer + viewport culling |
| Pan/zoom | 60 FPS | Transform at GPU level (PixiJS stage) |
| Hit detection | <16ms | QuadTree spatial index |
| Layout computation | Background | WebWorker (non-blocking) |
| Memory usage | <500MB | Typed arrays, texture atlases |
| Initial load | <3s | Progressive rendering, lazy loading |

### Alternative Scenarios

**Scenario 1: Rich Node Interaction Required**
- Use **Konva.js** with aggressive culling
- Limit to 10k visible nodes
- FastLayer for edges
- Cache complex nodes

**Scenario 2: Maximum Control & Custom Algorithms**
- Use **Raw Canvas API** with OffscreenCanvas
- Implement custom rendering pipeline
- WebWorker-based parallel rendering
- Complete control over every pixel

**Scenario 3: Existing React-Heavy Codebase**
- Use **react-konva** for <5k nodes
- Implement virtualization (only render visible)
- Memoize components aggressively
- Consider gradual migration to imperative API

### Avoid

- ❌ **Fabric.js** for 100k+ nodes (too slow)
- ❌ **Pure react-pixi** (reconciliation overhead)
- ❌ **DOM-based solutions** (React Flow, Cytoscape.js with DOM)
- ❌ **SVG rendering** at this scale

---

## References

### PixiJS
- [PixiJS v8 ParticleContainer Performance](https://pixijs.com/blog/particlecontainer-v8)
- [PixiJS Performance Tips](https://pixijs.com/8.x/guides/concepts/performance-tips)
- [PixiJS v8 Launch](https://pixijs.com/blog/pixi-v8-launches)
- [PixiJS WebGL vs Canvas Comparison](https://aircada.com/blog/pixijs-vs-konva)

### Konva.js
- [Konva Performance Tips](https://konvajs.org/docs/performance/All_Performance_Tips.html)
- [Konva Layer Management](https://konvajs.org/docs/performance/Layer_Management.html)
- [Konva Shape Caching](https://konvajs.org/docs/performance/Shape_Caching.html)
- [Konva Event Delegation](https://konvajs.org/docs/events/Event_Delegation.html)
- [React-Konva Documentation](https://konvajs.org/docs/react/index.html)

### Fabric.js
- [Fabric.js Performance Optimization](https://github.com/fabricjs/fabric.js/wiki/Optimizing-performance)
- [Fabric.js Object Caching](https://fabricjs.com/docs/fabric-object-caching/)
- [Fabric.js Performance Issues](https://github.com/fabricjs/fabric.js/issues/1855)

### Canvas API & OffscreenCanvas
- [OffscreenCanvas MDN](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas)
- [Optimizing Canvas Performance](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas)
- [OffscreenCanvas with Web Workers](https://web.dev/articles/offscreen-canvas)
- [Canvas Optimization Techniques](https://blog.ag-grid.com/optimising-html5-canvas-rendering-best-practices-and-techniques/)

### Performance Comparisons
- [React Canvas Performance Benchmarks](https://github.com/ryohey/react-canvas-perf)
- [PixiJS vs Konva Comparison](https://aircada.com/blog/pixijs-vs-konva)
- [Canvas Engines Benchmark](https://benchmarks.slaylines.io/)

### Large-Scale Graph Rendering
- [Rendering One Million Datapoints](https://blog.scottlogic.com/2020/05/01/rendering-one-million-points-with-d3.html)
- [How to Visualize a Graph with a Million Nodes](https://nightingaledvs.com/how-to-visualize-a-graph-with-a-million-nodes/)
- [Force-Directed Graph with PixiJS](https://observablehq.com/@zakjan/force-directed-graph-pixi)
- [WebGL-Based Visualization Framework](https://www.mdpi.com/2075-5309/15/16/2916)

### Spatial Indexing
- [Quadtree Data Structure](https://www.deepblock.net/blog/quadtree)
- [Quadtrees on the GPU](https://www.researchgate.net/publication/331761994_Quadtrees_on_the_GPU)

### Memory Management
- [Canvas Memory Management](https://app.studyraid.com/en/read/12533/405940/memory-management-strategies)
- [JavaScript Memory Optimization](https://dev.to/shafayeat/javascript-memory-management-and-optimization-techniques-for-large-scale-applications-5e4a)

### Hybrid Rendering
- [Building High-Performance UI with Canvas and WebGL](https://medium.com/@beyons/building-a-high-performance-ui-framework-with-html5-canvas-and-webgl-f7628af8a3c2)
- [SVG vs Canvas vs WebGL in 2025](https://www.svggenie.com/blog/svg-vs-canvas-vs-webgl-performance-2025)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-01
**Next Review:** 2026-04-01
