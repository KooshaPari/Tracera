# Phase 5: Wave 3 Readiness Brief

**Status:** 🟢 READY TO DISPATCH (Pending Gap 5.4 completion)
**Date Prepared:** 2026-02-06 02:30 UTC
**Dispatch Trigger:** Gap 5.4 signals completion (~T+20 min = 02:35 UTC)
**Owner:** api-performance-implementer (Task #19)
**Parallel Branches:** Tasks #20, #21, #22 (independent execution)

---

## DISPATCH AUTHORIZATION

**Upon Receipt of This Brief + Gap 5.4 Completion Signal:**

✅ You are authorized to immediately begin Wave 3 implementation
✅ All three gaps (5.6, 5.7, 5.8) can execute in parallel
✅ Execute in order: Gap 5.6 → Gap 5.7 → Gap 5.8 (sequential preferred for focus)
✅ Or execute all 3 in parallel (if you prefer context-switching)

**Critical Path:** Gap 5.7 (GPU shaders) is longest - 40 min
**Estimated Wall-Clock:** 40-50 minutes for all 3 gaps (5.6: 30 min, 5.7: 40 min, 5.8: 20 min)
**Expected Completion:** T+60-90 min from Wave 2 start (03:15-03:45 UTC)

---

## WAVE 3 OVERVIEW

### Gap 5.6: Re-enable API Endpoint Tests (15+ tests)
**Task:** #20
**Duration:** ~30 minutes
**Scope:**
- Re-enable 15+ existing API endpoint tests
- Implement OpenAPI contract validation
- Add response snapshot validation
- Verify 100% endpoint coverage

**Key Files to Modify:**
- Frontend tests: `/frontend/apps/web/src/__tests__/api/endpoints.test.ts`
- Backend validation: API contracts in OpenAPI spec
- Response snapshots: Add to test fixtures

**Success Criteria:**
- ✅ 15+ tests re-enabled and passing
- ✅ 100% endpoint coverage verified
- ✅ OpenAPI contract validation working
- ✅ Response snapshots validated

**Architecture Details:** See PHASE_5_COMPLETE_EXECUTION_PLAN.md, Section: "Gap 5.6 Implementation"

---

### Gap 5.7: GPU Compute Shaders Implementation (10+ tests)
**Task:** #21 (CRITICAL PATH - 40 minutes)
**Duration:** ~40 minutes
**Scope:**
- Implement WebGPU compute shaders (WGSL language)
- Add WebGL GPGPU fallback (fragment shaders)
- Achieve 50-100x speedup for force-directed layout
- Benchmark: 10k nodes in <100ms (vs ~30s CPU)
- Test with 10k+ node graph

**Key Files to Create/Modify:**
- `/frontend/apps/web/src/lib/gpu-compute/webgpu-shaders.ts`
  - Compute shader implementation
  - Buffer management
  - Pipeline setup
- `/frontend/apps/web/src/lib/gpu-compute/webgl-fallback.ts`
  - Fragment shader implementation
  - Texture-based rendering
- `/frontend/apps/web/src/lib/gpu-compute/layout-worker.ts`
  - Integration with layout worker
  - Device capability detection
  - Graceful fallback

**Code Template - WebGPU Compute Shader:**
```typescript
// Force-directed layout compute shader (WGSL)
const computeShaderCode = `
@group(0) @binding(0) var<storage, read_write> positions: array<vec2<f32>>;
@group(0) @binding(1) var<storage, read> velocities: array<vec2<f32>>;
@group(0) @binding(2) var<storage, read> forces: array<vec2<f32>>;

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let idx = global_id.x;
  if (idx >= arrayLength(&positions)) { return; }

  // Read node data
  var pos = positions[idx];
  var vel = velocities[idx];
  let force = forces[idx];

  // Apply force-directed physics
  vel += force * deltaTime * damping;
  pos += vel * deltaTime;

  // Write back
  positions[idx] = pos;
}
`;
```

**Code Template - WebGL Fallback:**
```typescript
// Fragment shader for GPGPU simulation
const fragmentShader = `#version 300 es
precision highp float;

uniform sampler2D positionTexture;
uniform sampler2D velocityTexture;
uniform sampler2D forceTexture;
uniform vec2 gridSize;
uniform float deltaTime;
uniform float damping;

out vec4 outColor;

void main() {
  vec2 uv = gl_FragCoord.xy / gridSize;

  // Sample textures for current node
  vec2 pos = texture(positionTexture, uv).xy;
  vec2 vel = texture(velocityTexture, uv).xy;
  vec2 force = texture(forceTexture, uv).xy;

  // Apply physics
  vel += force * deltaTime * damping;
  pos += vel * deltaTime;

  outColor = vec4(pos, vel);
}
`;
```

**Testing Strategy:**
- Benchmark test: 10k nodes, measure layout time
- Performance target: <100ms (vs 30s CPU)
- Validate 50-100x speedup
- Test device fallback (non-WebGPU browsers)

**Success Criteria:**
- ✅ 10+ tests passing
- ✅ WebGPU compute shader functional
- ✅ WebGL fallback tested
- ✅ 50-100x speedup verified
- ✅ Benchmark: 10k nodes in <100ms

**Architecture Details:** See PHASE_5_COMPLETE_EXECUTION_PLAN.md, Section: "Gap 5.7 GPU Shaders"

---

### Gap 5.8: Spatial Indexing Optimization (8+ tests)
**Task:** #22
**Duration:** ~20 minutes
**Scope:**
- Implement edge midpoint distance calculation
- Add Cohen-Sutherland line clipping algorithm
- Optimize viewport culling (98% accuracy target)
- Benchmark: 5k edges in <50ms
- Memory overhead: <5%

**Key Files to Create/Modify:**
- `/frontend/apps/web/src/lib/spatial-indexing/edge-midpoints.ts`
  - Edge midpoint calculation
  - Distance-to-viewport computation
- `/frontend/apps/web/src/lib/spatial-indexing/viewport-culling.ts`
  - Cohen-Sutherland clipping algorithm
  - Culling accuracy measurement
- `/frontend/apps/web/src/lib/spatial-indexing/spatial-tree.ts`
  - Update existing R-tree implementation
  - Add edge midpoint storage

**Code Template - Edge Midpoint Calculation:**
```typescript
// Calculate edge midpoint and distance to viewport
function calculateEdgeMidpoint(edge: Edge, viewport: Viewport): MidpointData {
  const start = edge.source.position;
  const end = edge.target.position;

  // Midpoint calculation
  const midpoint = {
    x: (start.x + end.x) / 2,
    y: (start.y + end.y) / 2
  };

  // Distance to viewport bounds
  const distToViewport = Math.min(
    Math.hypot(midpoint.x - viewport.centerX, midpoint.y - viewport.centerY),
    // Also check if edge crosses viewport
    0
  );

  return { midpoint, distToViewport };
}

// Cohen-Sutherland line clipping
function cohenSutherlandClip(edge: Edge, viewport: Viewport): boolean {
  let x0 = edge.source.x, y0 = edge.source.y;
  let x1 = edge.target.x, y1 = edge.target.y;

  const inside = (x: number, y: number) =>
    x >= viewport.left && x <= viewport.right &&
    y >= viewport.top && y <= viewport.bottom;

  // Clip line to viewport bounds
  // ... implementation ...

  return visibleLength > CULL_THRESHOLD;
}
```

**Testing Strategy:**
- Midpoint calculation accuracy test
- Culling accuracy measurement (target 98%)
- Benchmark: 5k edges in <50ms
- Memory overhead measurement (<5% target)
- Verify integration with existing graph rendering

**Success Criteria:**
- ✅ 8+ tests passing
- ✅ Edge midpoint indexing working
- ✅ 98% culling accuracy achieved
- ✅ <5% memory overhead
- ✅ Benchmark: 5k edges in <50ms

**Architecture Details:** See PHASE_5_COMPLETE_EXECUTION_PLAN.md, Section: "Gap 5.8 Spatial Indexing"

---

## EXECUTION SEQUENCE

### Recommended Approach: Sequential Focus (40-50 min total)

**Phase 1: Gap 5.6 (30 min)**
1. List all existing API endpoint tests
2. Identify which are currently disabled/skipped
3. Re-enable tests
4. Implement OpenAPI contract validation
5. Add response snapshot tests
6. Run tests: `cd frontend && bun run test -- src/__tests__/api/endpoints.test.ts --run`
7. Verify 15+ tests passing

**Phase 2: Gap 5.7 (40 min - START IMMEDIATELY, can overlap Phase 1)**
1. Study existing layout algorithm
2. Implement WebGPU compute shader code
3. Add WebGL GPGPU fallback
4. Create GPU computation wrapper
5. Integrate with layout worker
6. Create benchmark test: 10k nodes
7. Run test: measure <100ms target
8. Verify 50-100x speedup

**Phase 3: Gap 5.8 (20 min - can start while Phase 2 GPU tests run)**
1. Create edge midpoint calculation function
2. Implement Cohen-Sutherland clipping
3. Add to spatial indexing system
4. Create culling tests (8+ tests)
5. Benchmark: 5k edges in <50ms
6. Verify 98% culling accuracy

**Parallel Alternative:** All 3 gaps can execute in parallel (if you prefer task switching)

---

## CRITICAL SUCCESS FACTORS

### Gap 5.6 (API Tests)
- ✅ All tests must pass
- ✅ Coverage ≥85% maintained
- ✅ No snapshot mismatches

### Gap 5.7 (GPU Shaders) - **MOST CRITICAL**
- ✅ **50-100x speedup verified** (non-negotiable)
- ✅ Benchmark: 10k nodes in <100ms (target = MUST)
- ✅ WebGL fallback tested on non-WebGPU browsers
- ✅ All 10+ tests passing

### Gap 5.8 (Spatial Indexing)
- ✅ 98% culling accuracy measured
- ✅ <5% memory overhead confirmed
- ✅ <50ms benchmark for 5k edges
- ✅ All 8+ tests passing

---

## VALIDATION CHECKLIST

### Before Starting Gap 5.6:
- [ ] Task #20 ready to claim
- [ ] Existing endpoint tests located
- [ ] OpenAPI spec accessible
- [ ] Test fixtures ready

### Before Starting Gap 5.7:
- [ ] Task #21 ready to claim
- [ ] Layout algorithm code reviewed
- [ ] WebGPU device capability checked
- [ ] WGSL shader syntax studied
- [ ] 10k node benchmark data ready

### Before Starting Gap 5.8:
- [ ] Task #22 ready to claim
- [ ] R-tree implementation understood
- [ ] Cohen-Sutherland algorithm reviewed
- [ ] 5k edge test data ready

### Before Committing:
- [ ] Gap 5.6: 15+ tests passing
- [ ] Gap 5.7: 10+ tests + GPU speedup verified
- [ ] Gap 5.8: 8+ tests + spatial metrics verified
- [ ] Coverage: ≥85% maintained
- [ ] All 33+ tests passing

---

## SUPPORT RESOURCES

**Full Architecture:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/reports/PHASE_5_COMPLETE_EXECUTION_PLAN.md`
- Sections: Gap 5.6, 5.7, 5.8 (comprehensive)
- Code sketches and pseudocode
- Testing strategies

**Implementation Guide:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md`
- Problem analysis
- Acceptance criteria
- Risk mitigation

**Quick Reference:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/guides/quick-start/PHASE_5_GAPS_QUICK_REFERENCE.md`
- Per-gap task checklists
- Testing commands
- Success criteria

---

## DEPLOYMENT TRIGGER SIGNAL

**Team Lead will send this message when Gap 5.4 completes:**

```
✅ Gap 5.4 COMPLETE (Checkpoint 1 Phase 2 ready)
🚀 WAVE 3 AUTHORIZED: Begin Gap 5.6 immediately
⏰ Critical Path: Gap 5.7 (40 min) must complete by T+60 for schedule
📊 Expected completion: T+60-90 min from Wave 2 start (03:15-03:45 UTC)
```

**Upon receipt, proceed immediately with Gap 5.6.**

---

## TIMELINE TARGETS

| Task | Duration | Start | End | Critical Path? |
|------|----------|-------|-----|-----------------|
| **Gap 5.6** | 30 min | T+20 (02:35) | T+50 (03:05) | No |
| **Gap 5.7** | 40 min | T+20 (02:35) | T+60 (03:15) | **YES - Longest** |
| **Gap 5.8** | 20 min | T+20 (02:35) | T+40 (02:55) | No |
| **Wave 3 Complete** | - | - | **T+60 (03:15)** | - |

**Wall-clock Optimization:**
- Sequential: 30+40+20 = 90 minutes
- Parallel: max(30,40,20) = 40 minutes
- Recommended: Start all 3, focus on Gap 5.7 for critical path

---

## TEAM LEAD HANDOFF

**Status as of 02:30 UTC:**
- ✅ Wave 1 complete (18 tests passing)
- ✅ Wave 2 Phase 1 in progress (expected Checkpoint 1 ready ~02:30)
- ✅ Wave 3 fully briefed and ready
- ✅ Gap 5.4 (critical path) estimated to signal completion T+20 (02:35 UTC)

**Your authorization:**
You are fully ready to execute. Upon receipt of Gap 5.4 completion signal (~02:35 UTC), begin Wave 3 immediately with Gap 5.6.

---

## SUCCESS CELEBRATION

**When all 33+ tests passing:**
```
✅ Wave 3 COMPLETE (Gaps 5.6-5.8)
✅ GPU 50-100x speedup verified
✅ Spatial culling 98% accuracy achieved
✅ 33+/33 tests passing
✅ Coverage ≥85% maintained
✅ Phase 5 READY FOR FINAL VALIDATION
```

---

**Prepared by:** api-performance-architect (Task #1)
**Date:** 2026-02-06 02:30 UTC
**Status:** READY FOR IMMEDIATE DISPATCH
**Next Trigger:** Gap 5.4 completion signal (estimated T+20 min)
