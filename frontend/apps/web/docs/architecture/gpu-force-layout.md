# GPU-Accelerated Force-Directed Graph Layout

## Executive Summary

This document provides comprehensive research and implementation guidance for GPU-accelerated force-directed graph layout capable of handling 100,000+ nodes in real-time. Current CPU-based D3-force solutions take 30+ seconds for large graphs; GPU acceleration can reduce this to under 5 seconds.

**Target Performance:**
- **Current (CPU):** 30+ seconds for 100k nodes
- **Target (GPU):** <5 seconds for 100k nodes
- **Expected Speedup:** 100x for force calculations

---

## Problem Statement

### Current Limitations

**D3-Force (CPU-Based)**
- Single-threaded JavaScript execution
- O(n²) complexity for naive force calculations
- Barnes-Hut optimization: O(n log n) but still CPU-bound
- Performance degrades rapidly beyond 10k nodes
- 30+ seconds for 100k nodes unacceptable for real-time interaction

**Bottlenecks:**
1. N-body repulsion calculations (all pairs)
2. Iterative simulation (50-100 iterations)
3. Sequential processing on single CPU core

---

## GPU Computing Solution

### Why GPU Acceleration Works

**Parallel Architecture:**
- Modern GPUs: 1000+ cores vs CPU's 4-16 cores
- SIMD execution: Same instruction on many data points
- Perfect for embarrassingly parallel problems (force calculations)

**Force-Directed Layout as GPU Problem:**
- Each node's force can be calculated independently
- Barnes-Hut quadtree traversal parallelizable
- Iteration convergence naturally parallel

**Expected Performance:**
- 100x speedup for force calculations
- 60 FPS for 10k nodes (real-time)
- <5 seconds for 100k nodes layout

---

## Technology Options

### 1. WebGPU (Recommended)

**Overview:**
- Modern GPU API for the web (successor to WebGL)
- Direct access to compute shaders
- Storage buffers for large data
- Cross-browser support as of 2026

**Browser Support (2026):**
- **Chrome/Edge:** Full support since v113 (Windows via DirectX 12, macOS, ChromeOS, Android 12+)
- **Safari:** Enabled by default in iOS 26, macOS Tahoe 26, visionOS 26
- **Firefox:** Windows support in v141, macOS ARM64 in v145, Linux/Android in 2026
- **Coverage:** ~70% global browser coverage and growing

**Advantages:**
- True compute shaders (vs WebGL fragment shader hacks)
- Better performance than WebGL
- Modern API design
- First-class GPGPU support

**Limitations:**
- Requires fallback for older browsers
- Still stabilizing (but production-ready in 2026)

**Sources:**
- [WebGPU Now Supported in Major Browsers](https://web.dev/blog/webgpu-supported-major-browsers)
- [WebGPU Browser Compatibility](https://caniuse.com/webgpu)
- [WebGPU 2026: 70% Browser Support](https://byteiota.com/webgpu-2026-70-browser-support-15x-performance-gains/)

### 2. WebGL 2.0 + GPGPU

**Overview:**
- Wider browser support (90%+)
- Compute via fragment shaders
- GPGPU techniques with texture encoding

**GPGPU Approach:**
- Encode data as RGBA pixels in textures
- Fragment shader processes each pixel
- Read back texture data for results

**Advantages:**
- Broad compatibility
- Proven technique
- Fallback option

**Limitations:**
- No true compute shaders
- More complex data encoding
- Lower performance than WebGPU
- Limited storage buffer size

**Sources:**
- [WebGL2 GPGPU Tutorial](https://webgl2fundamentals.org/webgl/lessons/webgl-gpgpu.html)
- [WebGL N-body Simulations](https://www.ibiblio.org/e-notes/webgl/gpu/n-toy.html)

### 3. Hybrid CPU/GPU

**Approach:**
- GPU for physics simulation (force calculations)
- CPU for final positioning and constraints
- Best of both worlds

**Use Cases:**
- When constraints require sequential processing
- When WebGPU unavailable (fallback)
- When graph has semantic constraints

---

## Research: Leading Implementations

### GraphWaGu (State-of-the-Art)

**Overview:**
First WebGPU-based graph visualization system from research at University of Utah.

**Capabilities:**
- 100,000 nodes + 2,000,000 edges
- Interactive frame rates (100ms iteration for 20k nodes/400k edges)
- Modified Fruchterman-Reingold algorithm
- Barnes-Hut approximation in compute shaders

**Technical Details:**

**Quadtree for Barnes-Hut:**
- Quadtree generation and traversal in compute shaders
- No recursion or pointers (GPU limitation)
- Pseudo-stack buffer: size ≈ |V|log₄|V|
- Parallel tree traversal for each node

**Algorithms:**
1. **Fruchterman-Reingold:** Basic force-directed
2. **Barnes-Hut:** O(n log n) approximation

**Performance:**
- Best scalability vs state-of-the-art web libraries
- Maintains interactivity up to 100k nodes
- WebGPU provides 10x+ speedup over WebGL

**Code:**
- Open source: [GitHub - GraphWaGu](https://github.com/harp-lab/GraphWaGu)
- Research paper: [GraphWaGu Paper (PDF)](https://stevepetruzza.io/pubs/graphwagu-2022.pdf)

**Sources:**
- [GraphWaGu Research Paper](https://stevepetruzza.io/pubs/graphwagu-2022.pdf)
- [GraphWaGu GitHub](https://github.com/harp-lab/GraphWaGu)
- [GraphWaGu Project Page](https://www.willusher.io/publications/graphwagu/)

### @antv/layout-gpu

**Overview:**
Production-ready GPU-accelerated layout library from Ant Financial.

**Features:**
- WebGL/WebGPU support
- Fruchterman-Reingold algorithm
- Best performance in benchmarks
- Simple async API

**Usage:**
```typescript
import { FruchtermanGPU } from '@antv/layout-gpu';

const layout = new FruchtermanGPU({
  gravity: 10,
  speed: 5,
  maxIteration: 1000,
});

const result = await layout.execute(graph);
```

**Benchmarks:**
- Outperforms graphology, d3-force
- Handles 10k+ nodes efficiently
- WebGPU faster than WebGL

**Sources:**
- [@antv/layout-gpu on npm](https://www.npmjs.com/package/@antv/layout-gpu)
- [AntV Layout Benchmarks](https://antv.vision/layout/index.html)
- [AntV Layout GitHub](https://github.com/antvis/layout)

### Sigma.js + ParaGraphL

**Sigma.js:**
- WebGL rendering (not compute)
- Handles 100k edges easily
- Force layout struggles beyond 50k edges
- GPU usage issues with forceatlas2 plugin

**ParaGraphL:**
- WebGL-powered parallel layout framework
- Sigma.js plugin
- Significant speedup for Fruchterman-Reingold
- Proof of concept for WebGL acceleration

**Performance:**
- Rendering: Excellent (WebGL)
- Layout: Limited by WebGL constraints

**Sources:**
- [Sigma.js Official](https://www.sigmajs.org/)
- [ParaGraphL Demo](https://nblintao.github.io/ParaGraphL/)
- [Sigma.js Performance Discussion](https://github.com/jacomyal/sigma.js/issues/239)

---

## Barnes-Hut Algorithm on GPU

### Overview

Barnes-Hut reduces force calculation from O(n²) to O(n log n) by approximating distant node clusters as single mass points.

### Algorithm Steps

1. **Build Quadtree:** Divide 2D space recursively into quadrants
2. **Calculate Centers of Mass:** For each quadrant
3. **Traverse Tree:** For each node, approximate distant clusters
4. **Apply Forces:** Based on approximation

### GPU Implementation Challenges

**No Recursion:**
- GPUs don't support recursion
- Solution: Iterative traversal with pseudo-stack

**No Pointers:**
- Solution: Index-based tree in buffer
- Flatten tree to array

**Pseudo-Stack Approach:**
```
Stack buffer size: |V|log₄|V|
Iteratively push/pop quadrants
Traverse without recursion
```

### WebGPU Quadtree Implementation

**Key Resources:**
- [WebGPU Quadtree Sample](https://github.com/cedricpinson/webgpu-quadtree-compute-shader)
- [Quadtrees on GPU Paper](https://www.researchgate.net/publication/331761994_Quadtrees_on_the_GPU)
- [Barnes-Hut Visualization](https://jheer.github.io/barnes-hut/)

**Implementation Patterns:**

```typescript
// Compute shader pseudo-code
@compute @workgroup_size(64)
fn buildQuadtree(
  @builtin(global_invocation_id) id: vec3<u32>
) {
  // Build quadtree in parallel
  // Each workgroup handles subset of nodes
}

@compute @workgroup_size(64)
fn calculateForces(
  @builtin(global_invocation_id) id: vec3<u32>
) {
  let nodeId = id.x;
  var force = vec2<f32>(0.0);

  // Traverse quadtree with pseudo-stack
  // Approximate distant clusters
  // Accumulate forces

  outputForces[nodeId] = force;
}
```

**Sources:**
- [WebGPU Quadtree Compute Shader](https://github.com/cedricpinson/webgpu-quadtree-compute-shader)
- [Barnes-Hut CUDA Implementation](https://iss.oden.utexas.edu/Publications/Papers/burtscher11.pdf)
- [WebGPU Compute Shader Basics](https://webgpufundamentals.org/webgpu/lessons/webgpu-compute-shaders.html)

---

## Recommended Implementation Strategy

### Phase 1: WebGPU Fruchterman-Reingold (Simple)

**Why Start Here:**
- Simpler than Barnes-Hut
- Validates GPU pipeline
- Good for <10k nodes
- Foundation for optimization

**Algorithm:**
```
For each iteration:
  1. Repulsive forces (all pairs)
  2. Attractive forces (edges only)
  3. Update positions
  4. Apply damping
```

**Expected Performance:**
- 10k nodes: <1 second
- Real-time interaction at 60 FPS

### Phase 2: Barnes-Hut Optimization

**When:**
- After Phase 1 validated
- For 10k-100k nodes

**Adds:**
- Quadtree construction
- Tree traversal
- Approximation logic

**Expected Performance:**
- 100k nodes: <5 seconds
- O(n log n) vs O(n²)

### Phase 3: Hybrid Fallback

**Graceful Degradation:**
```
IF WebGPU available
  Use GPU acceleration
ELSE IF WebGL 2.0 available
  Use WebGL GPGPU
ELSE
  Use CPU D3-force (current behavior)
```

**Progressive Enhancement:**
- Always works (CPU fallback)
- Better on modern browsers (GPU)

---

## Implementation Architecture

### File Structure

```
src/lib/
├── gpuForceLayout.ts          # Main API
├── gpuForceLayoutWorker.ts    # Web Worker wrapper
└── gpu/
    ├── webgpu/
    │   ├── fruchterman.ts     # Fruchterman-Reingold
    │   ├── barnesHut.ts       # Barnes-Hut optimization
    │   └── shaders/
    │       ├── repulsion.wgsl
    │       ├── attraction.wgsl
    │       └── update.wgsl
    ├── webgl/
    │   ├── gpgpu.ts           # WebGL fallback
    │   └── shaders/
    └── cpu/
        └── fallback.ts        # D3-force fallback
```

### API Design

```typescript
import { GPUForceLayout } from '@/lib/gpuForceLayout';

// Initialize
const layout = new GPUForceLayout({
  nodes: graphNodes,
  edges: graphEdges,
  algorithm: 'fruchterman', // or 'barnes-hut'
  iterations: 100,
  gpu: true, // auto-detect and fallback
});

// Run layout
const positions = await layout.compute();

// Progressive rendering (stream positions)
layout.onProgress((partialPositions, progress) => {
  updateGraph(partialPositions);
});
```

### Integration with useDAGLayout

```typescript
// Add to LAYOUT_CONFIGS
{
  id: "gpu-force",
  label: "GPU Force (Large Graphs)",
  description: "GPU-accelerated for 10k+ nodes",
  icon: "Zap",
  algorithm: "gpu-force",
  bestFor: [
    "Large graphs (10k+ nodes)",
    "Real-time interaction",
    "Fast exploration"
  ],
}
```

---

## Performance Benchmarks (Target)

| Nodes | CPU (D3) | WebGL | WebGPU | Speedup |
|-------|----------|-------|--------|---------|
| 1k    | 0.5s     | 0.2s  | 0.1s   | 5x      |
| 5k    | 5s       | 1s    | 0.5s   | 10x     |
| 10k   | 20s      | 3s    | 1s     | 20x     |
| 50k   | 180s     | 20s   | 3s     | 60x     |
| 100k  | 600s     | 50s   | 5s     | 120x    |

**Assumptions:**
- Modern GPU (2020+)
- 100 iterations
- Barnes-Hut for GPU/WebGL
- Naive for CPU

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Create `gpuForceLayout.ts` with API
- [ ] Implement WebGPU device detection
- [ ] Basic Fruchterman-Reingold compute shader
- [ ] Position buffer management
- [ ] Integration test with 1k nodes

### Phase 2: Optimization
- [ ] Barnes-Hut quadtree construction
- [ ] Quadtree traversal shader
- [ ] Pseudo-stack implementation
- [ ] Test with 10k-100k nodes
- [ ] Performance benchmarking

### Phase 3: Production
- [ ] WebGL GPGPU fallback
- [ ] CPU D3-force fallback
- [ ] Progressive rendering (streaming)
- [ ] Web Worker isolation
- [ ] Error handling and recovery

### Phase 4: Integration
- [ ] Add to `useDAGLayout` hook
- [ ] Add to `LayoutSelector` component
- [ ] Update `FlowGraphViewInner`
- [ ] Documentation and examples
- [ ] Performance monitoring

---

## Next Steps

1. **Research Validation:**
   - Review GraphWaGu source code
   - Test @antv/layout-gpu with current graph
   - Benchmark current CPU performance

2. **Prototype:**
   - Implement basic WebGPU Fruchterman-Reingold
   - Test with 1k, 10k, 100k node datasets
   - Measure actual speedup

3. **Production:**
   - Add Barnes-Hut optimization
   - Implement fallback chain
   - Integrate with existing layouts
   - Document and deploy

---

## Key Insights

### What Makes GPU Acceleration Work

1. **Parallelism:** Force calculations are independent
2. **SIMD:** Same force formula for all node pairs
3. **Iteration:** 50-100 iterations benefit from GPU speed
4. **Data Locality:** Node positions fit in GPU memory

### When NOT to Use GPU

- **Small graphs (<1k nodes):** Overhead not worth it
- **Complex constraints:** CPU better for sequential logic
- **Offline processing:** CPU adequate, no need for complexity
- **Browser compatibility critical:** Fallback overhead

### Critical Success Factors

1. **Workgroup Size:** 64 recommended for WebGPU
2. **Memory Management:** Reuse buffers, avoid copies
3. **Iteration Count:** Balance quality vs speed
4. **Progressive Rendering:** Show intermediate results

---

## References

### Research Papers
- [GraphWaGu: GPU Powered Large Scale Graph Layout (2022)](https://stevepetruzza.io/pubs/graphwagu-2022.pdf)
- [Exploiting GPUs for Fast Force-Directed Visualization](https://liacs.leidenuniv.nl/~takesfw/pdf/exploiting-gpus-fast.pdf)
- [Quadtrees on the GPU](https://www.researchgate.net/publication/331761994_Quadtrees_on_the_GPU)

### Libraries & Tools
- [GraphWaGu GitHub Repository](https://github.com/harp-lab/GraphWaGu)
- [@antv/layout-gpu Package](https://www.npmjs.com/package/@antv/layout-gpu)
- [ParaGraphL Demo](https://nblintao.github.io/ParaGraphL/)
- [Sigma.js](https://www.sigmajs.org/)

### WebGPU Resources
- [WebGPU Fundamentals](https://webgpufundamentals.org/webgpu/lessons/webgpu-compute-shaders.html)
- [WebGPU Quadtree Sample](https://github.com/cedricpinson/webgpu-quadtree-compute-shader)
- [WebGPU Browser Support](https://caniuse.com/webgpu)

### WebGL GPGPU
- [WebGL2 GPGPU Tutorial](https://webgl2fundamentals.org/webgl/lessons/webgl-gpgpu.html)
- [WebGL N-body Simulation](https://www.ibiblio.org/e-notes/webgl/gpu/n-toy.html)

### Algorithm Theory
- [Barnes-Hut Approximation Visualization](https://jheer.github.io/barnes-hut/)
- [Barnes-Hut Simulation Wikipedia](https://en.wikipedia.org/wiki/Barnes%E2%80%93Hut_simulation)

---

## Conclusion

GPU acceleration for force-directed layout is **production-ready in 2026** with WebGPU achieving critical mass (70% browser support). The expected **100x speedup** makes real-time interaction with 100k+ node graphs feasible.

**Recommended Approach:**
1. Start with **WebGPU Fruchterman-Reingold** (simple, proven)
2. Add **Barnes-Hut optimization** for 10k+ nodes
3. Implement **graceful fallback** (WebGL → CPU)
4. Integrate with existing layout system

**Expected Outcome:**
- **100k nodes:** <5 seconds (from 30+ seconds)
- **10k nodes:** Real-time 60 FPS interaction
- **Progressive enhancement:** Works everywhere, better on modern browsers

This research provides a clear path to production-grade GPU-accelerated graph layout for TraceRTM.
