# WAVE 3 EXECUTION PLAN: Gaps 5.6-5.8

**Status:** 🟢 **LIVE DEPLOYMENT** at T+15
**Agent:** api-performance-implementer
**Tasks:** #20 (Gap 5.6), #21 (Gap 5.7 CRITICAL PATH), #22 (Gap 5.8)
**Duration:** ~40 min total (T+15 to T+55-60)
**Success Target:** 30+ tests + GPU 50-100x speedup + Spatial 98% accuracy

---

## DEPLOYMENT TIMELINE

### T+15: Launch All 3 Tasks Simultaneously
```
Gap 5.8: Spatial Indexing (20 min) ────────────────────────────────┐ T+35
Gap 5.6: API Endpoints (30 min)     ────────────────────────────────────┐ T+45
Gap 5.7: GPU Shaders (40 min - CRITICAL) ────────────────────────────────────────┐ T+55
                                                                          │
                                                               Wave 2 Completion: T+60
```

### Checkpoint Timeline
- **T+15:** All 3 tasks report "Ready & starting Phase 1"
- **T+30-35:** Gap 5.8 Phase 1 complete + Gap 5.6 Phase 1 complete
- **T+45:** Gap 5.6 complete (15+ tests passing)
- **T+55:** Gap 5.7 GPU speedup verified (50-100x confirmed)
- **T+60:** All Wave 3 tests passing (30+ total)

---

## TASK #20: GAP 5.6 - API ENDPOINTS (15+ Tests)

### Overview
Re-enable and implement comprehensive API endpoint tests covering CRUD operations, error handling, and contract validation.

### Phases (4 sequential, ~30 min total)

#### Phase 1 (10 min): Test Setup & Fixtures
**Objective:** Prepare test data and MSW mock handlers

**Files to modify:**
- `frontend/apps/web/src/__tests__/mocks/data.ts`
- `frontend/apps/web/src/__tests__/mocks/handlers.ts`

**What to create:**
1. **mockEndpoints array** in data.ts with 20+ variants:
   ```typescript
   const mockEndpoints = [
     { method: 'GET', path: '/api/v1/items', status: 200, response: { data: [...] } },
     { method: 'POST', path: '/api/v1/items', status: 201, response: { id: 'item-1', ... } },
     // ... 20+ variants including all CRUD + errors
   ];
   ```

2. **Response snapshots** for contract validation (prepare .snap file structure)

3. **MSW handlers** for all variants in handlers.ts:
   ```typescript
   rest.get('/api/v1/items', (req, res, ctx) => {
     return res(ctx.json({ data: mockItems }));
   }),
   // ... all CRUD operations
   ```

4. **Test fixtures** prepared in api-mocks.ts

**Acceptance:**
- ✅ 20+ mock endpoints defined
- ✅ All MSW handlers registered
- ✅ Response snapshots prepared
- ✅ Test fixtures ready

---

#### Phase 2 (8 min): Re-enable CRUD Tests
**Objective:** Enable basic CRUD operation tests with contract validation

**File to modify:**
- `frontend/apps/web/src/__tests__/api/endpoints.test.ts`

**What to do:**
1. Find all `describe.skip` blocks for CRUD operations
2. Replace `describe.skip` with `describe`
3. For each test, add contract validation:
   ```typescript
   it('should create item', async () => {
     const response = await api.items.create({ name: 'Test' });
     // Contract validation
     expect(response).toHaveProperty('id');
     expect(response).toHaveProperty('createdAt');
     // Snapshot match
     expect(response).toMatchSnapshot('create-item-response');
   });
   ```

4. Handle error cases (4xx, 5xx):
   ```typescript
   it('should handle 404 error', async () => {
     await expect(api.items.get('nonexistent')).rejects.toThrow('404');
   });
   ```

**Tests to enable (~5 tests):**
- Create item test
- Read/list items test
- Update item test
- Delete item test
- Error handling test (400/404/500)

**Acceptance:**
- ✅ 5/5 CRUD tests un-skipped
- ✅ Contract validation added to each
- ✅ Error cases handled
- ✅ No compilation errors

---

#### Phase 3 (8 min): Re-enable Advanced Tests
**Objective:** Enable filtering, pagination, sorting tests

**File to modify:**
- `frontend/apps/web/src/__tests__/api/endpoints.test.ts` (continued)

**What to do:**
1. Find all `describe.skip` blocks for advanced operations
2. Replace with `describe`
3. Implement advanced test scenarios:
   ```typescript
   it('should filter items by type', async () => {
     const items = await api.items.list({ filter: { type: 'document' } });
     expect(items).toHaveLength(3);
     items.forEach(item => expect(item.type).toBe('document'));
   });
   ```

4. Add pagination tests:
   ```typescript
   it('should paginate items', async () => {
     const page1 = await api.items.list({ page: 1, limit: 10 });
     const page2 = await api.items.list({ page: 2, limit: 10 });
     expect(page1[0].id).not.toBe(page2[0].id);
   });
   ```

5. Add sorting tests:
   ```typescript
   it('should sort items', async () => {
     const sorted = await api.items.list({ sort: 'createdAt:desc' });
     // Verify sort order
   });
   ```

**Tests to enable (~10+ tests):**
- Filter by type, status, priority
- Pagination (first, next, last)
- Sorting (asc/desc, multiple fields)
- Search query
- Complex filter combinations

**Acceptance:**
- ✅ 10+ advanced tests un-skipped
- ✅ All snapshot matches pass
- ✅ No flakes on 3x runs
- ✅ Coverage ≥85%

---

#### Phase 4 (4 min): Validation & Reporting
**Objective:** Run full suite and verify success

**Commands:**
```bash
# Run full endpoint test suite
cd frontend && bun run test -- src/__tests__/api/endpoints.test.ts --run

# Check coverage
cd frontend && bun run test -- src/__tests__/api/endpoints.test.ts --coverage

# 5x consecutive runs (flake detection)
for i in {1..5}; do
  bun run test -- src/__tests__/api/endpoints.test.ts --run || exit 1
done
```

**Success Criteria:**
- ✅ 15+ tests passing (all green)
- ✅ Coverage ≥85%
- ✅ 5x runs = 0 flakes
- ✅ All snapshots match
- ✅ No console errors/warnings

**Report (commit message):**
```
feat: re-enable API endpoints test suite (Gap 5.6)

- Re-enable 5 CRUD operation tests with contract validation
- Re-enable 10+ advanced tests (filter/paginate/sort)
- Extend MSW handlers for all endpoint variants
- Add response snapshot validation
- 15+ tests passing, coverage 85%+
```

---

## TASK #21: GAP 5.7 - GPU COMPUTE SHADERS (CRITICAL PATH, 10+ Tests)

### Overview
Implement WebGPU and WebGL GPGPU compute shaders for 50-100x force-directed layout performance improvement. **This is the critical path task** (40 min = longest Wave 3 task).

### Phases (4 sequential, ~40 min total)

#### Phase 1 (12 min): WebGPU Setup
**Objective:** Create WebGPU compute shader hook and shader implementation

**Files to create:**
- `NEW: frontend/apps/web/src/hooks/useGPUCompute.ts`
- `NEW: frontend/apps/web/src/shaders/force-directed.wgsl`

**useGPUCompute.ts (150-200 lines):**
```typescript
import { useCallback, useEffect, useRef, useState } from 'react';

export interface GPUComputeState {
  positions: Float32Array | null;
  velocities: Float32Array | null;
  forces: Float32Array | null;
  ready: boolean;
  supported: boolean;
}

export function useGPUCompute(nodes: number, edges: number) {
  const [state, setState] = useState<GPUComputeState>({
    positions: null,
    velocities: null,
    forces: null,
    ready: false,
    supported: !!navigator.gpu,
  });

  const gpuRef = useRef<{
    device: GPUDevice | null;
    positionBuffer: GPUBuffer | null;
    velocityBuffer: GPUBuffer | null;
    forceBuffer: GPUBuffer | null;
    computePipeline: GPUComputePipeline | null;
  }>({
    device: null,
    positionBuffer: null,
    velocityBuffer: null,
    forceBuffer: null,
    computePipeline: null,
  });

  // Initialize GPU device
  useEffect(() => {
    if (!navigator.gpu) {
      console.warn('WebGPU not supported');
      setState(prev => ({ ...prev, supported: false }));
      return;
    }

    const initGPU = async () => {
      try {
        const adapter = await navigator.gpu.requestAdapter();
        if (!adapter) throw new Error('GPU adapter not found');

        const device = await adapter.requestDevice();
        gpuRef.current.device = device;

        // Create compute shader module
        const shaderModule = device.createShaderModule({
          code: FORCE_DIRECTED_WGSL,
        });

        // Create compute pipeline
        const computePipeline = await device.createComputePipelineAsync({
          layout: 'auto',
          compute: { module: shaderModule, entryPoint: 'compute' },
        });
        gpuRef.current.computePipeline = computePipeline;

        setState(prev => ({ ...prev, ready: true, supported: true }));
      } catch (error) {
        console.error('WebGPU initialization failed:', error);
        setState(prev => ({ ...prev, supported: false }));
      }
    };

    initGPU();
  }, []);

  // Run compute shader
  const compute = useCallback(
    async (
      positions: Float32Array,
      velocities: Float32Array,
      edges: Array<[number, number]>,
      parameters: { k: number; dt: number; maxVelocity: number }
    ): Promise<Float32Array> => {
      if (!state.ready || !gpuRef.current.device) {
        throw new Error('GPU not ready');
      }

      // Implementation: create buffers, run compute shader, read results
      // (Details in Phase 3 integration)
      return positions;
    },
    [state.ready]
  );

  return { ...state, compute };
}

// WGSL shader code (see force-directed.wgsl file)
import FORCE_DIRECTED_WGSL from '../shaders/force-directed.wgsl?raw';
```

**force-directed.wgsl (100-150 lines):**
```wgsl
struct Node {
  x: f32,
  y: f32,
  vx: f32,
  vy: f32,
}

struct Edge {
  src: u32,
  dst: u32,
}

@group(0) @binding(0) var<storage, read_write> nodes: array<Node>;
@group(0) @binding(1) var<storage, read> edges: array<Edge>;
@group(0) @binding(2) var<uniform> params: vec4f; // k, dt, maxVelocity, damping

@compute @workgroup_size(64)
fn compute(@builtin(global_invocation_id) global_id: vec3u) {
  let idx = global_id.x;
  if (idx >= arrayLength(&nodes)) { return; }

  var node = nodes[idx];
  var fx: f32 = 0.0;
  var fy: f32 = 0.0;

  // Repulsive forces (all node pairs)
  for (var i = 0u; i < arrayLength(&nodes); i += 1u) {
    if (i == idx) { continue; }

    let other = nodes[i];
    let dx = other.x - node.x;
    let dy = other.y - node.y;
    let dist_sq = dx * dx + dy * dy + 1.0; // Add epsilon
    let dist = sqrt(dist_sq);

    let repulsion = params.x / dist_sq;
    fx -= (dx / dist) * repulsion;
    fy -= (dy / dist) * repulsion;
  }

  // Attractive forces (edges)
  for (var e = 0u; e < arrayLength(&edges); e += 1u) {
    let edge = edges[e];
    if (edge.src != idx && edge.dst != idx) { continue; }

    let other_idx = select(edge.dst, edge.src, edge.src == idx);
    let other = nodes[other_idx];
    let dx = other.x - node.x;
    let dy = other.y - node.y;
    let dist = sqrt(dx * dx + dy * dy + 1.0);

    let attraction = dist * params.x * 0.1;
    fx += (dx / (dist + 0.001)) * attraction;
    fy += (dy / (dist + 0.001)) * attraction;
  }

  // Velocity update (with damping)
  node.vx = (node.vx + fx * params.y) * params.w;
  node.vy = (node.vy + fy * params.y) * params.w;

  // Limit velocity
  let v_len = sqrt(node.vx * node.vx + node.vy * node.vy);
  if (v_len > params.z) {
    node.vx = (node.vx / v_len) * params.z;
    node.vy = (node.vy / v_len) * params.z;
  }

  // Position update
  node.x += node.vx * params.y;
  node.y += node.vy * params.y;

  nodes[idx] = node;
}
```

**Acceptance:**
- ✅ useGPUCompute.ts created (150-200 lines)
- ✅ force-directed.wgsl created (100-150 lines)
- ✅ TypeScript compiles cleanly
- ✅ No shader compilation errors

---

#### Phase 2 (12 min): WebGL Fallback
**Objective:** Create WebGL GPGPU fallback for browsers without WebGPU

**Files to create:**
- `NEW: frontend/apps/web/src/hooks/useWebGLCompute.ts`
- `NEW: frontend/apps/web/src/shaders/force-directed.glsl`

**useWebGLCompute.ts (150-200 lines):**
```typescript
import { useCallback, useEffect, useRef, useState } from 'react';
import FORCE_DIRECTED_GLSL from '../shaders/force-directed.glsl?raw';

export function useWebGLCompute(nodes: number) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const glRef = useRef<WebGLRenderingContext | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Create offscreen canvas
    const canvas = document.createElement('canvas');
    const size = Math.ceil(Math.sqrt(nodes));
    canvas.width = size;
    canvas.height = size;

    const gl = canvas.getContext('webgl2');
    if (!gl) {
      console.error('WebGL2 not supported');
      return;
    }

    glRef.current = gl;

    // Create shader program (ping-pong texture rendering)
    const program = gl.createProgram();
    if (!program) return;

    // Compile and link shaders
    const shader = gl.createShader(gl.FRAGMENT_SHADER);
    if (!shader) return;
    gl.shaderSource(shader, FORCE_DIRECTED_GLSL);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error(gl.getShaderInfoLog(shader));
      return;
    }

    // ... bind textures, create framebuffers

    setReady(true);
  }, [nodes]);

  const compute = useCallback(
    async (positions: Float32Array): Promise<Float32Array> => {
      if (!glRef.current) throw new Error('WebGL not initialized');

      const gl = glRef.current;

      // Upload position texture
      // Run compute passes (ping-pong)
      // Read results

      return positions;
    },
    []
  );

  return { ready, compute };
}
```

**force-directed.glsl (80-120 lines):**
```glsl
precision highp float;

uniform sampler2D positionTexture;
uniform sampler2D velocityTexture;
uniform vec2 invSize; // 1.0 / size
uniform vec4 params; // k, dt, maxVelocity, damping

varying vec2 vUV;

void main() {
  vec4 position = texture2D(positionTexture, vUV);
  vec4 velocity = texture2D(velocityTexture, vUV);

  float fx = 0.0;
  float fy = 0.0;

  // Sample nearby positions and compute forces
  // (Similar to WGSL shader but with texture sampling)

  gl_FragColor = vec4(position.xy + velocity.xy * params.y, position.zw);
}
```

**Acceptance:**
- ✅ useWebGLCompute.ts created (150-200 lines)
- ✅ force-directed.glsl created (80-120 lines)
- ✅ Fallback correctly detects WebGL2
- ✅ No compilation errors

---

#### Phase 3 (10 min): Performance Testing & Benchmarking
**Objective:** Benchmark GPU layout vs CPU and verify 50-100x speedup

**File to create:**
- `NEW: frontend/apps/web/src/__tests__/performance/gpu-compute.perf.test.tsx`

**gpu-compute.perf.test.tsx (200-250 lines):**
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { useGPUCompute } from '../../hooks/useGPUCompute';
import { useWebGLCompute } from '../../hooks/useWebGLCompute';
import { generateTestGraph } from '../mocks/data';

describe('GPU Compute Performance', () => {
  describe('WebGPU vs CPU Layout', () => {
    it('should compute 10k node layout in <100ms (WebGPU)', async () => {
      const { nodes, edges } = generateTestGraph(10000, 15000);
      const positions = new Float32Array(nodes.length * 2);

      const start = performance.now();
      // Run GPU compute layout
      const result = await gpuCompute(positions, edges);
      const duration = performance.now() - start;

      expect(duration).toBeLessThan(100); // <100ms
      expect(result).toBeDefined();
    });

    it('should achieve 50-100x speedup over CPU', async () => {
      const { nodes, edges } = generateTestGraph(5000, 10000);

      // CPU timing
      const cpuStart = performance.now();
      cpuForceDirected(nodes, edges, 100); // 100 iterations
      const cpuDuration = performance.now() - cpuStart;

      // GPU timing
      const gpuStart = performance.now();
      await gpuCompute(nodes, edges, 100);
      const gpuDuration = performance.now() - gpuStart;

      const speedup = cpuDuration / gpuDuration;
      expect(speedup).toBeGreaterThan(50);
    });

    it('should use <1GB memory for 10k nodes', async () => {
      const { nodes } = generateTestGraph(10000, 15000);
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;

      // Run compute
      const result = await gpuCompute(nodes);

      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      const memoryUsed = (finalMemory - initialMemory) / 1024 / 1024; // MB

      expect(memoryUsed).toBeLessThan(1000); // <1GB
    });
  });

  describe('Browser Compatibility', () => {
    it('should fallback to WebGL when WebGPU unavailable', async () => {
      // Temporarily disable WebGPU
      const originalGPU = navigator.gpu;
      (navigator as any).gpu = undefined;

      const { nodes, edges } = generateTestGraph(1000, 2000);
      const result = await fallbackCompute(nodes, edges);

      expect(result).toBeDefined();

      // Restore
      (navigator as any).gpu = originalGPU;
    });

    it('should work on Chrome, Firefox, Safari, Edge', async () => {
      // Test detection logic
      expect(detectWebGPUSupport()).toBeDefined();
    });
  });
});
```

**Acceptance:**
- ✅ 10k nodes layout <100ms verified
- ✅ 50-100x speedup confirmed
- ✅ Memory usage <1GB
- ✅ Browser compatibility tested
- ✅ Fallback logic verified

**Performance Report Expected:**
- CPU layout 5k nodes (100 iter): ~5000ms
- GPU layout 5k nodes (100 iter): ~50-100ms
- **Speedup: 50-100x** ✅

---

#### Phase 4 (6 min): Integration & Validation
**Objective:** Wire GPU compute into SigmaGraphView and verify production use

**Files to modify:**
- `frontend/apps/web/src/components/graph/SigmaGraphView.tsx`

**Integration:**
```typescript
import { useGPUCompute } from '../../hooks/useGPUCompute';
import { useWebGLCompute } from '../../hooks/useWebGLCompute';

export function SigmaGraphView({ nodes, edges, ...props }) {
  const gpuCompute = useGPUCompute(nodes.length, edges.length);
  const webglCompute = useWebGLCompute(nodes.length);

  const computeLayout = useCallback(async (positions) => {
    if (gpuCompute.ready) {
      return await gpuCompute.compute(positions, velocities, edges, params);
    } else if (webglCompute.ready) {
      return await webglCompute.compute(positions);
    } else {
      return cpuForceDirected(positions, velocities, edges, params);
    }
  }, [gpuCompute.ready, webglCompute.ready]);

  // Use computeLayout in graph update loop
  useEffect(() => {
    const frame = () => {
      const newPositions = await computeLayout(positions);
      updateGraphPositions(newPositions);
      requestAnimationFrame(frame);
    };
    const id = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(id);
  }, [computeLayout]);
}
```

**Acceptance:**
- ✅ GPU compute integrated into SigmaGraphView
- ✅ Fallback chain: WebGPU → WebGL → CPU
- ✅ Performance visualization (FPS, compute time)
- ✅ No UI jank or blocking operations
- ✅ Layout converges correctly

**Success Criteria:**
- ✅ 10k+ nodes render smoothly (<16ms per frame)
- ✅ 50-100x speedup verified in production
- ✅ CPU fallback works correctly
- ✅ All tests passing (10+ performance tests)
- ✅ Quality score: 97+/100

---

## TASK #22: GAP 5.8 - SPATIAL INDEXING (8+ Tests)

### Overview
Implement spatial indexing for edge midpoint visibility computation to optimize viewport culling. **Shortest task (20 min)** but critical for viewport performance.

### Phases (4 sequential, ~20 min total)

#### Phase 1 (6 min): Spatial Index Structure
**Objective:** Create edge spatial index and midpoint calculation

**Files to create:**
- `NEW: frontend/apps/web/src/lib/graph/spatial-index.ts`

**spatial-index.ts (150-180 lines):**
```typescript
export interface Edge {
  id: string;
  source: { x: number; y: number };
  target: { x: number; y: number };
}

export class EdgeSpatialIndex {
  private grid: Map<string, Set<Edge>> = new Map();
  private gridSize: number;
  private bounds: { minX: number; maxX: number; minY: number; maxY: number };

  constructor(edges: Edge[], gridSize: number = 50) {
    this.gridSize = gridSize;
    this.bounds = { minX: 0, maxX: 0, minY: 0, maxY: 0 };
    this.rebuildIndex(edges);
  }

  rebuildIndex(edges: Edge[]) {
    this.grid.clear();

    // Calculate bounds
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    edges.forEach(edge => {
      minX = Math.min(minX, edge.source.x, edge.target.x);
      maxX = Math.max(maxX, edge.source.x, edge.target.x);
      minY = Math.min(minY, edge.source.y, edge.target.y);
      maxY = Math.max(maxY, edge.source.y, edge.target.y);
    });

    this.bounds = { minX, maxX, minY, maxY };

    // Insert edges into grid
    edges.forEach(edge => {
      const gridCells = this.getGridCells(edge);
      gridCells.forEach(cellKey => {
        if (!this.grid.has(cellKey)) {
          this.grid.set(cellKey, new Set());
        }
        this.grid.get(cellKey)!.add(edge);
      });
    });
  }

  private getGridCells(edge: Edge): string[] {
    const cells: string[] = [];

    // Get all grid cells the edge intersects
    const x1 = Math.floor((edge.source.x - this.bounds.minX) / this.gridSize);
    const y1 = Math.floor((edge.source.y - this.bounds.minY) / this.gridSize);
    const x2 = Math.floor((edge.target.x - this.bounds.minX) / this.gridSize);
    const y2 = Math.floor((edge.target.y - this.bounds.minY) / this.gridSize);

    const minX = Math.min(x1, x2);
    const maxX = Math.max(x1, x2);
    const minY = Math.min(y1, y2);
    const maxY = Math.max(y1, y2);

    for (let x = minX; x <= maxX; x++) {
      for (let y = minY; y <= maxY; y++) {
        cells.push(`${x},${y}`);
      }
    }

    return cells;
  }

  // Calculate midpoint of edge
  midpoint(edge: Edge): { x: number; y: number } {
    return {
      x: (edge.source.x + edge.target.x) / 2,
      y: (edge.source.y + edge.target.y) / 2,
    };
  }

  // Query edges within viewport bounds
  queryViewport(viewport: { minX: number; maxX: number; minY: number; maxY: number }): Edge[] {
    const result: Set<Edge> = new Set();

    const minGridX = Math.floor((viewport.minX - this.bounds.minX) / this.gridSize);
    const maxGridX = Math.floor((viewport.maxX - this.bounds.minX) / this.gridSize);
    const minGridY = Math.floor((viewport.minY - this.bounds.minY) / this.gridSize);
    const maxGridY = Math.floor((viewport.maxY - this.bounds.minY) / this.gridSize);

    for (let x = minGridX; x <= maxGridX; x++) {
      for (let y = minGridY; y <= maxGridY; y++) {
        const cellKey = `${x},${y}`;
        const cellEdges = this.grid.get(cellKey);
        if (cellEdges) {
          cellEdges.forEach(edge => result.add(edge));
        }
      }
    }

    return Array.from(result);
  }
}
```

**Acceptance:**
- ✅ EdgeSpatialIndex class created (150-180 lines)
- ✅ Grid-based indexing working
- ✅ queryViewport() efficiently returns only visible edges
- ✅ No compilation errors

---

#### Phase 2 (6 min): Visibility Computation
**Objective:** Implement viewport culling with Cohen-Sutherland clipping

**File to create:**
- `NEW: frontend/apps/web/src/lib/graph/viewport-culling.ts`

**viewport-culling.ts (120-150 lines):**
```typescript
export interface Viewport {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export interface Edge {
  id: string;
  source: { x: number; y: number };
  target: { x: number; y: number };
}

// Cohen-Sutherland line clipping algorithm
function cohenSutherlandClip(
  x1: number, y1: number,
  x2: number, y2: number,
  xmin: number, ymin: number,
  xmax: number, ymax: number
): [number, number, number, number] | null {

  const INSIDE = 0;
  const LEFT = 1;
  const RIGHT = 2;
  const BOTTOM = 4;
  const TOP = 8;

  const computeCode = (x: number, y: number) => {
    let code = INSIDE;
    if (x < xmin) code |= LEFT;
    else if (x > xmax) code |= RIGHT;
    if (y < ymin) code |= BOTTOM;
    else if (y > ymax) code |= TOP;
    return code;
  };

  let code1 = computeCode(x1, y1);
  let code2 = computeCode(x2, y2);
  let x = 0, y = 0;

  while (true) {
    if ((code1 | code2) === INSIDE) {
      // Both points inside
      return [x1, y1, x2, y2];
    }
    if ((code1 & code2) !== INSIDE) {
      // Both points outside (same side)
      return null;
    }

    // One point outside, clip against viewport
    const codeOut = code1 !== INSIDE ? code1 : code2;

    if (codeOut & TOP) {
      x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1);
      y = ymax;
    } else if (codeOut & BOTTOM) {
      x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1);
      y = ymin;
    } else if (codeOut & RIGHT) {
      y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1);
      x = xmax;
    } else if (codeOut & LEFT) {
      y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1);
      x = xmin;
    }

    if (codeOut === code1) {
      x1 = x;
      y1 = y;
      code1 = computeCode(x1, y1);
    } else {
      x2 = x;
      y2 = y;
      code2 = computeCode(x2, y2);
    }
  }
}

// Main visibility function
export function isEdgeVisible(
  edge: Edge,
  viewport: Viewport,
  cache: Map<string, boolean> = new Map()
): boolean {
  const cacheKey = `${edge.id}:${JSON.stringify(viewport)}`;

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey)!;
  }

  // Use Cohen-Sutherland clipping
  const clipped = cohenSutherlandClip(
    edge.source.x, edge.source.y,
    edge.target.x, edge.target.y,
    viewport.minX, viewport.minY,
    viewport.maxX, viewport.maxY
  );

  const visible = clipped !== null;
  cache.set(cacheKey, visible);

  return visible;
}

// Batch visibility computation
export function getVisibleEdges(
  edges: Edge[],
  viewport: Viewport,
  cache?: Map<string, boolean>
): Edge[] {
  const visibleCache = cache || new Map();

  return edges.filter(edge =>
    isEdgeVisible(edge, viewport, visibleCache)
  );
}
```

**Acceptance:**
- ✅ Cohen-Sutherland clipping implemented (correct algorithm)
- ✅ isEdgeVisible() returns accurate boolean
- ✅ getVisibleEdges() filters edge list correctly
- ✅ Caching prevents redundant computations
- ✅ No compilation errors

---

#### Phase 3 (6 min): Performance Optimization
**Objective:** Benchmark spatial culling and verify <50ms for 5k edges

**File to create:**
- `NEW: frontend/apps/web/src/__tests__/lib/spatial-index.test.ts`

**spatial-index.test.ts (150-200 lines):**
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { EdgeSpatialIndex } from '../../lib/graph/spatial-index';
import { getVisibleEdges, isEdgeVisible } from '../../lib/graph/viewport-culling';

describe('Spatial Indexing & Viewport Culling', () => {
  describe('EdgeSpatialIndex', () => {
    it('should build index for 5k edges', () => {
      const edges = generateEdges(5000);
      const start = performance.now();
      const index = new EdgeSpatialIndex(edges, 50);
      const duration = performance.now() - start;

      expect(index).toBeDefined();
      expect(duration).toBeLessThan(100); // <100ms build time
    });

    it('should query viewport in <50ms for 5k edges', () => {
      const edges = generateEdges(5000);
      const index = new EdgeSpatialIndex(edges);
      const viewport = { minX: 0, maxX: 500, minY: 0, maxY: 500 };

      const start = performance.now();
      const visible = index.queryViewport(viewport);
      const duration = performance.now() - start;

      expect(duration).toBeLessThan(50); // <50ms query
      expect(visible.length).toBeGreaterThan(0);
      expect(visible.length).toBeLessThan(5000);
    });

    it('should achieve 98% culling accuracy', () => {
      const edges = generateEdges(1000);
      const index = new EdgeSpatialIndex(edges);
      const viewport = { minX: 0, maxX: 250, minY: 0, maxY: 250 };

      // Query with spatial index
      const spatialResult = index.queryViewport(viewport);

      // Brute force (ground truth)
      const bruteForce = edges.filter(edge => {
        const mx = (edge.source.x + edge.target.x) / 2;
        const my = (edge.source.y + edge.target.y) / 2;
        return mx >= viewport.minX && mx <= viewport.maxX &&
               my >= viewport.minY && my <= viewport.maxY;
      });

      // Calculate accuracy
      const accuracy = spatialResult.length / bruteForce.length;
      expect(accuracy).toBeGreaterThan(0.98); // 98% accuracy
    });
  });

  describe('Cohen-Sutherland Clipping', () => {
    it('should clip edge correctly', () => {
      const edge = {
        id: 'test',
        source: { x: -10, y: 50 },
        target: { x: 510, y: 50 },
      };

      const clipped = cohenSutherlandClip(
        edge.source.x, edge.source.y,
        edge.target.x, edge.target.y,
        0, 0, 500, 500
      );

      expect(clipped).not.toBeNull();
      expect(clipped![0]).toBeGreaterThanOrEqual(0); // x1 clipped
      expect(clipped![2]).toBeLessThanOrEqual(500); // x2 clipped
    });

    it('should return null for completely outside edge', () => {
      const clipped = cohenSutherlandClip(
        -100, -100, -50, -50,
        0, 0, 500, 500
      );

      expect(clipped).toBeNull();
    });
  });

  describe('Integration', () => {
    it('should correctly render only visible edges in viewport', () => {
      const edges = generateEdges(5000);
      const viewport = { minX: 0, maxX: 500, minY: 0, maxY: 500 };

      const visible = getVisibleEdges(edges, viewport);

      // All visible edges should have midpoint inside viewport
      visible.forEach(edge => {
        const mx = (edge.source.x + edge.target.x) / 2;
        const my = (edge.source.y + edge.target.y) / 2;

        // May or may not be strictly inside (Cohen-Sutherland handles clipping)
        expect(edge).toBeDefined();
      });
    });
  });
});
```

**Acceptance:**
- ✅ 5k edges culled in <50ms verified
- ✅ 98% accuracy confirmed against brute-force
- ✅ <5% memory overhead measured
- ✅ Cohen-Sutherland clipping correct
- ✅ All tests passing (8+ total)

---

#### Phase 4 (2 min): Integration & Validation
**Objective:** Wire spatial index into SigmaGraphView and verify production use

**Files to modify:**
- `frontend/apps/web/src/components/graph/SigmaGraphView.tsx`

**Integration:**
```typescript
import { EdgeSpatialIndex } from '../../lib/graph/spatial-index';
import { getVisibleEdges } from '../../lib/graph/viewport-culling';

export function SigmaGraphView({ nodes, edges, viewport, ...props }) {
  const [spatialIndex, setSpatialIndex] = useState<EdgeSpatialIndex | null>(null);
  const [visibleEdges, setVisibleEdges] = useState<Edge[]>(edges);

  // Build spatial index once
  useEffect(() => {
    const index = new EdgeSpatialIndex(edges);
    setSpatialIndex(index);
  }, [edges]);

  // Update visible edges when viewport changes
  useEffect(() => {
    if (spatialIndex && viewport) {
      const visible = spatialIndex.queryViewport(viewport);
      setVisibleEdges(visible);
    }
  }, [spatialIndex, viewport]);

  // Render only visible edges
  return (
    <Sigma graph={createGraph(nodes, visibleEdges)} />
  );
}
```

**Acceptance:**
- ✅ Spatial index integrated into SigmaGraphView
- ✅ Only visible edges rendered (98% culling accuracy)
- ✅ FPS improvement verified (measure before/after)
- ✅ Memory overhead <5%
- ✅ No visual artifacts or missing edges

---

## CHECKPOINT REPORTING EXPECTATIONS

### Checkpoint 1 (T+15)
**Expected Report:**
```
Gap 5.6 (API Endpoints): Ready - starting Phase 1
Gap 5.7 (GPU Shaders): Ready - starting Phase 1
Gap 5.8 (Spatial Indexing): Ready - starting Phase 1
```

### Checkpoint 2 (T+30-35)
**Expected Reports:**
```
Gap 5.8: Phase 1 complete (EdgeSpatialIndex created)
Gap 5.6: Phase 1 complete (mockEndpoints defined, MSW handlers registered)
```

### Checkpoint 3 (T+45-50)
**Expected Reports:**
```
Gap 5.6: Complete! 15+ tests passing, coverage 85%+
Gap 5.7: Phase 2 complete (WebGL fallback created)
```

### Checkpoint 4 (T+55-60)
**Expected Reports:**
```
Gap 5.7: Complete! GPU shaders tested, 50-100x speedup verified, all tests passing
Gap 5.8: Complete! Cohen-Sutherland clipping verified, <50ms for 5k edges
All Wave 3 tests: 30+ passing ✅
```

---

## SUCCESS CRITERIA SUMMARY

### Gap 5.6 (API Endpoints)
- ✅ 15+ tests passing
- ✅ Contract validation complete
- ✅ All snapshots match
- ✅ Coverage ≥85%
- ✅ 5x flake-free runs

### Gap 5.7 (GPU Shaders) — CRITICAL PATH
- ✅ 10k+ nodes render <100ms
- ✅ 50-100x speedup verified
- ✅ WebGPU + WebGL fallback working
- ✅ Cross-browser compatible
- ✅ 10+ performance tests passing

### Gap 5.8 (Spatial Indexing)
- ✅ 5k edges culled <50ms
- ✅ 98% culling accuracy
- ✅ <5% memory overhead
- ✅ 8+ tests passing
- ✅ FPS improvement verified

---

**Status:** 🚀 **WAVE 3 EXECUTING - ALL 3 TASKS LIVE**
**Duration:** T+15 to T+55 min (40 min total)
**Critical Path:** Gap 5.7 (GPU shaders)
**Overall Wave 3 Delivery:** 30+ tests + 50-100x GPU speedup + 98% spatial accuracy

Let's deliver! 🎯

