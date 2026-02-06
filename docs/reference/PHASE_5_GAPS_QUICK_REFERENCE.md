# Phase 5 Gaps 5.6-5.8: Quick Reference Guide

**Status:** Architecture & Implementation Ready
**Document:** One-pager for rapid development
**Target:** Parallel agent execution

---

## Gap Summary Table

| Gap | File | Status | Type | Effort | Impact |
|-----|------|--------|------|--------|--------|
| **5.6** | `endpoints.test.ts` | `describe.skip` | Testing | 15 min | Contract validation |
| **5.7** | `gpuForceLayout.ts` | TODO lines 215, 226, 238, 249 | Performance | 20 min | 100x speedup (10k+ nodes) |
| **5.8** | `enhancedViewportCulling.ts` | TODO line 364 | Accuracy | 10 min | Edge culling 98% accuracy |

---

## Gap 5.6: API Endpoint Tests

### Quick Task List
1. Remove `describe.skip` at line 21 in `endpoints.test.ts`
2. Create fixtures in `__tests__/mocks/data.ts` (reuse existing mock data)
3. Implement 15+ tests:
   - Projects: GET list, GET/:id, POST, PUT/:id, DELETE/:id
   - Items: GET list, GET/:id, POST, PUT/:id, DELETE/:id
   - Links: GET list, GET/:id, POST, PUT/:id, DELETE/:id
   - Search, Graph, Equivalence, Queries endpoints
4. Add snapshot tests for all CRUD responses
5. Validate against OpenAPI spec

### Code Template
```typescript
describe('API Endpoints', () => {
  it('should list projects', async () => {
    const projects = await projectsApi.list();
    expect(projects).toMatchSnapshot();
  });

  it('should create project', async () => {
    const created = await projectsApi.create({
      name: 'Test',
    });
    expect(created).toHaveProperty('id');
  });
});
```

### Files
- Modify: `frontend/apps/web/src/__tests__/api/endpoints.test.ts`
- Modify: `frontend/apps/web/src/__tests__/mocks/handlers.ts` (add missing)
- Reuse: `frontend/apps/web/src/__tests__/mocks/data.ts`

### Success Criteria
- 15+ endpoint tests passing
- Snapshots match OpenAPI spec
- All CRUD operations tested

---

## Gap 5.7: GPU Compute Shaders

### Quick Task List

#### WebGPU Compute Shader (Lines 219-230)
1. Detect WebGPU capability: `navigator.gpu`
2. Create GPU device & buffers for nodes/edges
3. Compile WGSL compute shader (Fruchterman-Reingold)
4. Dispatch work in iterations
5. Read results back from GPU

#### WebGL GPGPU Fallback (Lines 242-253)
1. Create WebGL context
2. Compile fragment shader for force calculation
3. Use texture as position storage
4. Render to framebuffer, read back results
5. Fallback if WebGPU unavailable

### Key Shaders

**WebGPU (WGSL):**
```wgsl
@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) id: vec3<u32>) {
  // Repulsion: from all other nodes
  // Attraction: from connected edges
  // Update: position += velocity * damping
}
```

**WebGL (GLSL):**
```glsl
void main() {
  // Read position from texture
  // Calculate forces from other nodes
  // Write updated position
}
```

### Performance Targets
- WebGPU: 50-100x speedup (10k nodes: <100ms)
- WebGL: 20-50x speedup
- CPU fallback: ~1 iter/sec for 10k nodes

### Files
- Create: `frontend/apps/web/src/lib/gpuComputeShaders.ts` (400 lines)
  - `FRUCHTERMAN_REINGOLD_COMPUTE_SHADER` constant
  - `createComputeContext()` helper
  - `dispatchComputeWork()` function
- Create: `frontend/apps/web/src/lib/webglGpgpu.ts` (300 lines)
- Modify: `frontend/apps/web/src/lib/gpuForceLayout.ts` (lines 219-230, 242-253)
- Create: `frontend/apps/web/src/__tests__/lib/gpuComputeShaders.test.ts` (250 lines)

### Success Criteria
- WebGPU shader functional & tested
- WebGL fallback working
- CPU fallback confirmed
- Performance targets met (benchmarks in CI)
- No GPU memory leaks

---

## Gap 5.8: Spatial Indexing

### Quick Task List
1. Add midpoint fields to `RTreeItem` interface:
   ```typescript
   interface RTreeItemWithMidpoint extends RTreeItem {
     midpointX: number;
     midpointY: number;
   }
   ```
2. Update `calculateEdgeBounds()` to compute midpoints:
   ```typescript
   const midpointX = (sourcePos.x + targetPos.x) / 2;
   const midpointY = (sourcePos.y + targetPos.y) / 2;
   ```
3. Add distance calculation method:
   ```typescript
   getEdgeDistanceToViewportCenter(edgeId, viewport): number
   ```
4. Update culling functions to use distance thresholds
5. Add LOD distance-based culling levels

### Distance Calculation
```typescript
function getEdgeDistanceToViewportCenter(
  edge: RTreeItemWithMidpoint,
  viewport: ViewportBounds,
): number {
  const centerX = (viewport.minX + viewport.maxX) / 2;
  const centerY = (viewport.minY + viewport.maxY) / 2;
  const dx = edge.midpointX - centerX;
  const dy = edge.midpointY - centerY;
  return Math.sqrt(dx * dx + dy * dy);
}
```

### Performance
- Memory overhead: <5% (24→28 bytes per edge)
- Query time: Still O(log n) via R-tree
- Culling accuracy: 98%+ (vs ~85% baseline)

### Files
- Modify: `frontend/apps/web/src/lib/spatialIndex.ts` (add 50 lines)
- Modify: `frontend/apps/web/src/lib/enhancedViewportCulling.ts` (lines 361-378, ~80 lines)
- Create: `frontend/apps/web/src/__tests__/lib/spatialIndexMidpoint.test.ts` (200 lines)

### Success Criteria
- Midpoint calculations working
- LOD distance thresholds applied
- Memory overhead <5%
- Culling accuracy 98%+
- 95%+ test coverage

---

## Dependency Graph

```
Phase A (Prerequisites) ─────────────────┐
  └─ Validate OpenAPI setup             │
  └─ Detect WebGPU capability           │
  └─ Measure baseline performance       │
                                         │
    ┌─────────────────────────────────────┴──┐
    │                                         │
    ▼                                         ▼
Phase B (Gap 5.6)                    Phase C (Gap 5.7) ──────┐
  └─ Re-enable API tests              │ Create compute       │
  └─ Add endpoints tests              │ Create WebGL         │
  └─ Snapshot validation              │ Wire shaders        │
  └─ 15+ tests passing                │ Benchmark tests     │
                                      │
                                      └─────┬────────────────────┐
                                            │                    ▼
                                      Phase D (Gap 5.8)    Phase E (Integration)
                                        └─ Midpoints          └─ Full test suite
                                        └─ Distance calc      └─ Perf validation
                                        └─ LOD culling        └─ Completion report

Run B, C, D in parallel after A.
E depends on all (B5, C5, D4).
```

---

## Parallel Execution Plan

**Agent 1 - Frontend API (Gap 5.6)**
- Time: 15 min
- Focus: Test infrastructure & endpoint testing
- Deliverable: 15+ passing tests + snapshots

**Agent 2 - GPU Performance (Gap 5.7)**
- Time: 20 min (critical path)
- Focus: WebGPU + WebGL compute shader implementation
- Deliverable: Both backends functional + benchmarks

**Agent 3 - Spatial Index (Gap 5.8)**
- Time: 10 min
- Focus: Midpoint indexing + LOD enhancement
- Deliverable: 98%+ culling accuracy + tests

**Team Lead**
- Phase A (5 min): Setup & validation
- Phases B-D: Monitor agent progress
- Phase E (10 min): Integration & final validation

**Total Wall-Clock:** 45 minutes
**Parallelization Efficiency:** 3x speedup over sequential

---

## File Checklist

### Gap 5.6
- [ ] Modify: `frontend/apps/web/src/__tests__/api/endpoints.test.ts` (remove skip, add tests)
- [ ] Modify: `frontend/apps/web/src/__tests__/mocks/handlers.ts` (add missing endpoints)
- [ ] Reuse: `frontend/apps/web/src/__tests__/mocks/data.ts`

### Gap 5.7
- [ ] Create: `frontend/apps/web/src/lib/gpuComputeShaders.ts`
- [ ] Create: `frontend/apps/web/src/lib/webglGpgpu.ts`
- [ ] Modify: `frontend/apps/web/src/lib/gpuForceLayout.ts` (lines 219-230, 242-253)
- [ ] Create: `frontend/apps/web/src/__tests__/lib/gpuComputeShaders.test.ts`

### Gap 5.8
- [ ] Modify: `frontend/apps/web/src/lib/spatialIndex.ts` (~50 lines)
- [ ] Modify: `frontend/apps/web/src/lib/enhancedViewportCulling.ts` (lines 361-378)
- [ ] Create: `frontend/apps/web/src/__tests__/lib/spatialIndexMidpoint.test.ts`

---

## Testing & Validation

### Run Tests
```bash
# Gap 5.6: API endpoint tests
cd frontend/apps/web
bun test src/__tests__/api/endpoints.test.ts

# Gap 5.7: GPU compute shader tests
bun test src/__tests__/lib/gpuComputeShaders.test.ts

# Gap 5.8: Spatial index tests
bun test src/__tests__/lib/spatialIndexMidpoint.test.ts

# All tests
bun test src/__tests__/{api,lib}
```

### Performance Benchmarks
```bash
# GPU layout benchmark (10k+ nodes)
bun test src/__tests__/lib/gpuComputeShaders.test.ts --reporter=verbose

# Spatial index performance (culling time)
bun test src/__tests__/lib/spatialIndexMidpoint.test.ts --reporter=verbose
```

---

## Success Criteria Summary

**All 3 Gaps Closed:**
- [ ] Gap 5.6: 15+ endpoint tests passing, snapshots validated
- [ ] Gap 5.7: WebGPU + WebGL working, 10x+ speedup, benchmarks passing
- [ ] Gap 5.8: Midpoint indexing working, 98%+ culling accuracy, <5% memory overhead

**Phase 5 Complete:**
- [ ] 80+ new tests added
- [ ] Performance improvements documented
- [ ] Completion report generated
- [ ] CI/CD integration verified

---

## Key Resources

**Implementation Details:** `docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md`

**GPU Architecture:** `docs/architecture/gpu-force-layout.md`

**Spatial Indexing:** `docs/architecture/spatial-indexing.md`

**OpenAPI Spec:** `backend/docs/openapi.json`
