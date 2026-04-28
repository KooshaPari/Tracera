# Viewport-Based Graph API Specification - Delivery Summary

**Date:** 2026-01-31
**Task:** Phase 4 Task 4.1 Part 1 - Design viewport-based data loading API
**Status:** ✅ Complete

## Deliverable

Created comprehensive API specification document:
- **Location:** `/docs/guides/viewport-graph-api-spec.md`
- **Format:** Markdown (22 sections, ~650 lines)
- **Version:** 1.0 (Draft)

## Specification Coverage

### 1. API Contract Definition ✅

**Endpoint:** `POST /api/v1/projects/{id}/graph/viewport`

**Request Schema:**
```typescript
interface ViewportRequest {
  viewport: ViewportBounds;  // Bounding box (minX, minY, maxX, maxY)
  zoom: number;              // Current zoom level
  bufferPx: number;          // Buffer pixels beyond viewport
  filters?: GraphFilters;    // Optional type/status/link filters
  perspective?: PerspectiveType;
}
```

**Response Schema:**
```typescript
interface ViewportResponse {
  nodes: GraphNode[];        // Visible nodes with positions
  edges: GraphEdge[];        // Edges connecting visible nodes
  metadata: ViewportMetadata; // hasMore flags + stats
}
```

### 2. Regionalization Strategy ✅

**Grid-Based Partitioning:**
- **Region Size:** 500px × 500px grid cells
- **Region ID Format:** `"r_{gridX}_{gridY}"` (e.g., "r_2_1", "r_-1_3")
- **Node Assignment:** Node → region containing its center point
- **Edge Assignment:** Edge → all regions it passes through

**Viewport Query Algorithm:**
1. Extend viewport by `bufferPx` on all sides
2. Calculate intersecting grid regions
3. Query nodes/edges from those regions
4. Apply filters and return results

**Rationale for 500px:**
- Average viewport (1200×800) → 6-12 regions
- With 300px buffer → adds 2-4 regions
- Typical query: 10-16 regions (optimal for batch fetching)
- Each region: ~50-200 nodes (good memory footprint)

### 3. Caching Requirements ✅

**Three-Tier Caching:**

#### Tier 1: Client-Side (React Query)
- **Key:** `viewport:${projectId}:${gridX}_${gridY}:${zoom}:${filterHash}`
- **TTL:** 5 minutes (stale-while-revalidate)
- **Invalidation:** On graph mutation, filter change, perspective change

#### Tier 2: Server-Side (Redis)
- **Key:** `region:{project_id}:{region_id}:{filter_hash}`
- **TTL:** 15 minutes
- **Pattern:** Cache-aside with granular invalidation
- **Invalidation:** Event-driven (node moved → invalidate old+new region)

#### Tier 3: Database (PostgreSQL)
- **Prepared Statements:** Pre-compiled region fetch queries
- **Indexes:**
  - `idx_graph_nodes_viewport` on (project_id, region_id, type)
  - `idx_graph_nodes_position` spatial index using GIST

**Cache Invalidation Strategy:**
- Node moved: Invalidate old + new region
- Node added/deleted: Invalidate containing region
- Edge added/deleted: Invalidate all intersecting regions
- Bulk update: Clear entire project cache

### 4. Performance Targets ✅

**Response Time Targets:**
| Scenario                     | Target  | Maximum |
|------------------------------|---------|---------|
| Cache hit (typical viewport) | <50ms   | 100ms   |
| Cache miss (6-12 regions)    | <150ms  | 300ms   |
| Large viewport (20+ regions) | <250ms  | 500ms   |
| Cold start (no cache)        | <500ms  | 1000ms  |

**Scalability Targets:**
| Graph Size   | Viewport Load | Memory per Viewport |
|--------------|---------------|---------------------|
| 1K nodes     | <50ms         | ~500 KB             |
| 10K nodes    | <150ms        | ~2 MB               |
| 50K nodes    | <300ms        | ~5 MB               |
| 100K+ nodes  | <500ms        | ~10 MB              |

### 5. Implementation Details ✅

**Backend (Python/FastAPI):**
- Route file: `src/tracertm/api/routers/graph_viewport.py`
- Service layer: `src/tracertm/services/graph_regions.py`
- Complete code examples provided for:
  - Viewport request handler
  - Region calculation utilities
  - Cache invalidation events

**Frontend (TypeScript/React):**
- API client: `frontend/apps/web/src/api/graph-viewport.ts`
- Hook: `frontend/apps/web/src/hooks/useGraphViewport.ts`
- React Query integration with proper cache configuration

**Database Schema:**
- Migration 045: Add `region_id` column to `graph_nodes`
- Migration 046: Create `edge_regions` join table
- Triggers for auto-region assignment on insert/update

## Key Features Documented

1. **Directional Paging Indicators** (`hasMore` flags)
   - North, South, East, West flags
   - Enables "load more" UI in each direction

2. **Filter Support**
   - Node types, link types, statuses
   - Perspective-based filtering
   - Filter hash in cache keys

3. **Error Handling**
   - Client-side retry logic
   - Server-side error responses (400, 404, 422, 500)
   - Detailed error messages with actionable context

4. **Migration Strategy**
   - 4-phase rollout plan
   - Feature flag: `ENABLE_VIEWPORT_LOADING`
   - A/B testing at 10% → 50% → 100%
   - Parallel implementation with legacy `/graph/full` endpoint

## Examples Provided

1. **Initial viewport load** - First page view
2. **Panning right** - Horizontal navigation with partial cache hits
3. **Zooming in** - Full cache hit scenario
4. **Filtered view** - Custom filter cache miss

Each example includes:
- Full request JSON
- Full response JSON
- Cache hit rate
- Region query count

## Technical Decisions

### Why POST instead of GET?
- Complex viewport parameters in request body
- Avoids URL length limits
- Better support for filter objects

### Why 500px regions?
- Balances query count (10-16 typical) with memory
- Optimal for typical viewport sizes (1200×800)
- Can be tuned per deployment (300px-1000px)

### Why three-tier caching?
- Client cache: Sub-50ms response for pan/zoom
- Server cache: Reduces database load by 80%+
- DB cache: Optimizes cold start performance

## Integration Points

**Existing Systems:**
- Extends current `graphApi` in `endpoints.ts`
- Compatible with existing `GraphData` types
- Works with current `EnhancedNodeData` and `EnhancedEdgeData`
- Integrates with React Query setup in `AppProviders.tsx`

**Database:**
- Builds on existing `graph_nodes` and `links` tables
- Adds non-breaking `region_id` columns
- Backward compatible with current queries

## Next Steps (Task 4.1 Part 2)

1. **Backend Implementation**
   - Create `/api/v1/projects/{id}/graph/viewport` endpoint
   - Implement region calculation service
   - Set up Redis caching layer
   - Add database migrations

2. **Frontend Integration**
   - Create `graphViewportApi` client
   - Implement `useGraphViewport` hook
   - Update graph components to use viewport API
   - Add progressive loading UI

3. **Testing**
   - Unit tests for region calculations
   - Integration tests for viewport queries
   - E2E tests for pan/zoom scenarios
   - Performance benchmarks

## Files Delivered

1. **Primary Deliverable:**
   - `/docs/guides/viewport-graph-api-spec.md` (650+ lines)

2. **This Summary:**
   - `/docs/reports/viewport-api-spec-delivery.md`

## Compliance with Project Standards

✅ Documentation in correct location (`docs/guides/`)
✅ Follows API versioning convention (`/api/v1/`)
✅ TypeScript type safety throughout
✅ Consistent with existing codebase patterns
✅ Performance targets aligned with requirements
✅ Comprehensive error handling specified
✅ Migration strategy included

---

**Specification Status:** Ready for Review & Implementation
**Estimated Implementation Time:** 3-4 days (backend + frontend + testing)
