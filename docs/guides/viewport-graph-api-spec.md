# Viewport-Based Graph Data Loading API Specification

**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-01-31

## Table of Contents

1. [Overview](#overview)
2. [API Contract](#api-contract)
3. [Regionalization Strategy](#regionalization-strategy)
4. [Caching Requirements](#caching-requirements)
5. [Performance Targets](#performance-targets)
6. [Implementation Notes](#implementation-notes)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

---

## Overview

The Viewport-Based Graph Data Loading API provides an efficient mechanism for loading only the graph nodes and edges visible within the current viewport, plus a configurable buffer zone. This approach enables:

- **Scalable rendering** of graphs with 10,000+ nodes
- **Reduced initial load time** by deferring off-screen content
- **Progressive disclosure** as users pan and zoom
- **Memory efficiency** by releasing off-viewport data

### Design Goals

1. **Sub-100ms response time** for typical viewport queries
2. **Predictable query patterns** for effective caching
3. **Minimal over-fetching** while avoiding visible gaps during pan/zoom
4. **Stateless API** - all context in request parameters

---

## API Contract

### Endpoint

```
POST /api/v1/projects/{id}/graph/viewport
```

**Method:** POST (not GET, to support complex viewport parameters in request body)

**Path Parameters:**

| Parameter | Type   | Required | Description                  |
|-----------|--------|----------|------------------------------|
| `id`      | UUID   | Yes      | Project ID                   |

### Request Body

```typescript
interface ViewportRequest {
  viewport: ViewportBounds;
  zoom: number;
  bufferPx: number;
  filters?: GraphFilters;
  perspective?: PerspectiveType;
}

interface ViewportBounds {
  minX: number;    // Left edge of viewport (canvas coordinates)
  minY: number;    // Top edge of viewport (canvas coordinates)
  maxX: number;    // Right edge of viewport (canvas coordinates)
  maxY: number;    // Bottom edge of viewport (canvas coordinates)
}

interface GraphFilters {
  nodeTypes?: string[];        // Filter by item types
  linkTypes?: LinkType[];      // Filter by link types
  statuses?: ItemStatus[];     // Filter by status
  perspectives?: PerspectiveType[];
}
```

**Field Descriptions:**

- **viewport**: Bounding box defining the visible area in canvas coordinate space
- **zoom**: Current zoom level (1.0 = 100%, 0.5 = 50%, 2.0 = 200%)
- **bufferPx**: Additional pixels to load beyond viewport edges (recommended: 200-500px)
- **filters**: Optional filters to apply to returned data
- **perspective**: Optional perspective view (e.g., "technical", "business", "ui")

### Response Body

```typescript
interface ViewportResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: ViewportMetadata;
}

interface GraphNode {
  id: string;
  type: string;
  title: string;
  status: ItemStatus;
  position: Position;
  data: EnhancedNodeData;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: LinkType;
  label: string;
  data?: Record<string, unknown>;
}

interface Position {
  x: number;
  y: number;
}

interface ViewportMetadata {
  hasMore: DirectionalFlags;
  regionStats: RegionStats;
  cacheKey: string;
  timestamp: string;
}

interface DirectionalFlags {
  north: boolean;   // More content above viewport
  south: boolean;   // More content below viewport
  east: boolean;    // More content to the right
  west: boolean;    // More content to the left
}

interface RegionStats {
  totalNodes: number;
  totalEdges: number;
  regionsQueried: number;
  cacheHitRate: number;
}
```

### HTTP Status Codes

| Code | Meaning                                      |
|------|----------------------------------------------|
| 200  | Success - viewport data returned             |
| 400  | Bad Request - invalid viewport parameters    |
| 404  | Not Found - project does not exist           |
| 422  | Unprocessable Entity - invalid filter combo  |
| 500  | Internal Server Error                        |

---

## Regionalization Strategy

### Grid-Based Partitioning

The graph canvas is divided into a **500px × 500px grid** of regions. Each region is identified by its grid coordinates.

```
Region ID = "r_{gridX}_{gridY}"

gridX = floor(canvasX / 500)
gridY = floor(canvasY / 500)
```

**Example:**

```
Canvas position (1250, 750) → Region ID "r_2_1"
Canvas position (-500, 1500) → Region ID "r_-1_3"
```

### Region Assignment

1. **Node Assignment**: A node belongs to the region containing its center point
2. **Edge Assignment**: An edge belongs to all regions it passes through (calculated via line-box intersection)

### Viewport Query Strategy

Given a viewport request:

1. Calculate the extended bounding box: `viewport ± bufferPx`
2. Determine all regions intersecting the extended box
3. Query nodes/edges from those regions
4. Apply additional filters (type, status, etc.)
5. Return results with metadata

**Pseudocode:**

```python
def get_viewport_data(viewport, buffer_px):
    # Extend viewport by buffer
    extended = {
        'minX': viewport.minX - buffer_px,
        'minY': viewport.minY - buffer_px,
        'maxX': viewport.maxX + buffer_px,
        'maxY': viewport.maxY + buffer_px
    }

    # Calculate region bounds
    min_grid_x = floor(extended.minX / REGION_SIZE)
    max_grid_x = floor(extended.maxX / REGION_SIZE)
    min_grid_y = floor(extended.minY / REGION_SIZE)
    max_grid_y = floor(extended.maxY / REGION_SIZE)

    # Query all intersecting regions
    regions = []
    for gx in range(min_grid_x, max_grid_x + 1):
        for gy in range(min_grid_y, max_grid_y + 1):
            regions.append(f"r_{gx}_{gy}")

    # Fetch data from regions (with caching)
    nodes = fetch_nodes_from_regions(regions)
    edges = fetch_edges_from_regions(regions)

    return {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'hasMore': calculate_has_more(extended, all_nodes),
            'regionStats': {
                'regionsQueried': len(regions),
                'totalNodes': len(nodes),
                'totalEdges': len(edges)
            }
        }
    }
```

### Region Size Rationale

**Why 500px?**

1. **Average viewport**: ~1200px × 800px → 6-12 regions per viewport
2. **Buffer zone**: 300px buffer → typically adds 2-4 regions
3. **Database efficiency**: 10-16 region queries is optimal for batch fetching
4. **Memory footprint**: Each region averages 50-200 nodes

**Tuning Parameters:**

- Large graphs (>10K nodes): Consider 750px or 1000px regions
- Dense graphs: Smaller regions (300px-400px) for finer granularity
- Sparse graphs: Larger regions (1000px) to reduce query overhead

---

## Caching Requirements

### Three-Tier Caching Strategy

#### 1. Client-Side Cache (React Query / SWR)

**Cache Key Format:**
```typescript
const cacheKey = `viewport:${projectId}:${gridX}_${gridY}:${zoom}:${hash(filters)}`
```

**TTL:** 5 minutes (stale-while-revalidate)

**Invalidation Triggers:**
- Graph data mutation (add/remove/move node)
- Filter change
- Perspective change

**Implementation:**

```typescript
// Using React Query
const { data, isLoading } = useQuery({
  queryKey: ['viewport', projectId, viewport, zoom, filters],
  queryFn: () => fetchViewportData(projectId, viewport, zoom, filters),
  staleTime: 5 * 60 * 1000,  // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
  refetchOnWindowFocus: false,
})
```

#### 2. Server-Side Region Cache (Redis)

**Cache Structure:**

```
Key: "region:{project_id}:{region_id}:{filter_hash}"
Value: JSON-serialized { nodes: [], edges: [] }
TTL: 15 minutes
```

**Cache Warming:**

```python
# On graph update, invalidate affected regions
def invalidate_regions(node_id, old_position, new_position):
    old_region = calculate_region(old_position)
    new_region = calculate_region(new_position)

    cache.delete(f"region:{project_id}:{old_region}")
    if old_region != new_region:
        cache.delete(f"region:{project_id}:{new_region}")
```

**Cache-Aside Pattern:**

```python
async def get_region_data(project_id, region_id, filters):
    cache_key = f"region:{project_id}:{region_id}:{hash(filters)}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - query database
    data = await db.query(
        """
        SELECT * FROM graph_nodes
        WHERE project_id = :project_id
          AND region_id = :region_id
        """
    )

    # Store in cache
    await cache.setex(cache_key, 900, json.dumps(data))
    return data
```

#### 3. Database Query Cache (PostgreSQL)

**Prepared Statements:**

```sql
-- Pre-compiled query for region fetch
PREPARE get_region_nodes AS
SELECT
    n.id, n.type, n.title, n.status,
    n.position_x, n.position_y,
    n.data
FROM graph_nodes n
WHERE n.project_id = $1
  AND n.region_id = ANY($2)
  AND ($3::text[] IS NULL OR n.type = ANY($3))
ORDER BY n.position_x, n.position_y;
```

**Database Indexes:**

```sql
-- Composite index for viewport queries
CREATE INDEX idx_graph_nodes_viewport
ON graph_nodes(project_id, region_id, type)
INCLUDE (position_x, position_y);

-- Spatial index for precise bounds checking
CREATE INDEX idx_graph_nodes_position
ON graph_nodes USING GIST (
    project_id,
    box(point(position_x, position_y), point(position_x, position_y))
);
```

### Cache Invalidation Strategy

**Granular Invalidation:**

1. **Node moved**: Invalidate old + new region
2. **Node added/deleted**: Invalidate containing region
3. **Edge added/deleted**: Invalidate all intersecting regions
4. **Bulk update**: Invalidate all regions (clear project cache)

**Event-Driven Invalidation:**

```python
# Using event bus for cache invalidation
@event_handler("graph.node.moved")
async def on_node_moved(event):
    project_id = event.project_id
    old_region = calculate_region(event.old_position)
    new_region = calculate_region(event.new_position)

    await cache.delete_pattern(f"region:{project_id}:{old_region}:*")
    if old_region != new_region:
        await cache.delete_pattern(f"region:{project_id}:{new_region}:*")
```

---

## Performance Targets

### Response Time Targets

| Scenario                        | Target     | Maximum    |
|---------------------------------|------------|------------|
| Cache hit (typical viewport)    | < 50ms     | 100ms      |
| Cache miss (6-12 regions)       | < 150ms    | 300ms      |
| Large viewport (20+ regions)    | < 250ms    | 500ms      |
| Cold start (no cache)           | < 500ms    | 1000ms     |

### Scalability Targets

| Graph Size          | Viewport Load Time | Memory per Viewport |
|---------------------|-------------------|---------------------|
| 1,000 nodes         | < 50ms            | ~500 KB             |
| 10,000 nodes        | < 150ms           | ~2 MB               |
| 50,000 nodes        | < 300ms           | ~5 MB               |
| 100,000+ nodes      | < 500ms           | ~10 MB              |

### Database Query Performance

**Query Budget per Viewport Request:**

- **Ideal:** 1-2 queries (full cache hit on regions)
- **Typical:** 3-5 queries (partial cache hit)
- **Worst case:** 10-15 queries (cache miss on all regions)

**Optimization Techniques:**

1. **Batch fetching**: Single query for multiple regions
2. **Connection pooling**: Reuse database connections
3. **Parallel queries**: Fetch nodes and edges concurrently
4. **Query result streaming**: Stream large result sets

---

## Implementation Notes

### Backend (Python/FastAPI)

**File:** `src/tracertm/api/routers/graph_viewport.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/projects/{project_id}/graph", tags=["graph"])

class ViewportBounds(BaseModel):
    minX: float
    minY: float
    maxX: float
    maxY: float

class ViewportRequest(BaseModel):
    viewport: ViewportBounds
    zoom: float
    bufferPx: int = 300
    filters: Optional[dict] = None
    perspective: Optional[str] = None

@router.post("/viewport")
async def get_viewport_data(
    project_id: str,
    request: ViewportRequest,
    db: Session = Depends(get_db)
) -> ViewportResponse:
    """
    Fetch graph nodes and edges within the specified viewport.

    Uses region-based caching for optimal performance.
    """
    # Calculate affected regions
    regions = calculate_viewport_regions(
        request.viewport,
        request.bufferPx
    )

    # Fetch data with caching
    nodes = await fetch_nodes_from_regions(
        db, project_id, regions, request.filters
    )
    edges = await fetch_edges_for_nodes(
        db, project_id, [n.id for n in nodes]
    )

    # Calculate metadata
    has_more = calculate_directional_flags(
        request.viewport, nodes
    )

    return ViewportResponse(
        nodes=nodes,
        edges=edges,
        metadata=ViewportMetadata(
            hasMore=has_more,
            regionStats={
                "totalNodes": len(nodes),
                "totalEdges": len(edges),
                "regionsQueried": len(regions)
            }
        )
    )
```

### Frontend (TypeScript/React)

**File:** `frontend/apps/web/src/api/graph-viewport.ts`

```typescript
import { apiClient, handleApiResponse } from './client';
import type { ViewportRequest, ViewportResponse } from './types';

export const graphViewportApi = {
  fetch: async (
    projectId: string,
    request: ViewportRequest
  ): Promise<ViewportResponse> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/projects/{id}/graph/viewport', {
        params: { path: { id: projectId } },
        body: request,
      })
    );
  },
};
```

**Hook Integration:**

```typescript
// frontend/apps/web/src/hooks/useGraphViewport.ts
import { useQuery } from '@tanstack/react-query';
import { graphViewportApi } from '@/api/graph-viewport';

export function useGraphViewport(
  projectId: string,
  viewport: ViewportBounds,
  zoom: number,
  options?: UseQueryOptions
) {
  return useQuery({
    queryKey: ['graph-viewport', projectId, viewport, zoom],
    queryFn: () => graphViewportApi.fetch(projectId, {
      viewport,
      zoom,
      bufferPx: 300,
    }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
}
```

### Region Calculation Utilities

```python
# src/tracertm/services/graph_regions.py

REGION_SIZE = 500  # pixels

def calculate_region_id(x: float, y: float) -> str:
    """Calculate region ID from canvas coordinates."""
    grid_x = int(x // REGION_SIZE)
    grid_y = int(y // REGION_SIZE)
    return f"r_{grid_x}_{grid_y}"

def calculate_viewport_regions(
    viewport: ViewportBounds,
    buffer_px: int
) -> List[str]:
    """Calculate all regions intersecting the viewport + buffer."""
    extended = {
        'minX': viewport.minX - buffer_px,
        'minY': viewport.minY - buffer_px,
        'maxX': viewport.maxX + buffer_px,
        'maxY': viewport.maxY + buffer_px,
    }

    min_grid_x = int(extended['minX'] // REGION_SIZE)
    max_grid_x = int(extended['maxX'] // REGION_SIZE)
    min_grid_y = int(extended['minY'] // REGION_SIZE)
    max_grid_y = int(extended['maxY'] // REGION_SIZE)

    regions = []
    for gx in range(min_grid_x, max_grid_x + 1):
        for gy in range(min_grid_y, max_grid_y + 1):
            regions.append(f"r_{gx}_{gy}")

    return regions

def assign_node_to_region(position: Position) -> str:
    """Assign a node to its containing region."""
    return calculate_region_id(position.x, position.y)

def assign_edge_to_regions(
    source_pos: Position,
    target_pos: Position
) -> List[str]:
    """Assign an edge to all regions it intersects."""
    regions = set()

    # Start and end regions
    regions.add(calculate_region_id(source_pos.x, source_pos.y))
    regions.add(calculate_region_id(target_pos.x, target_pos.y))

    # Use Bresenham-like algorithm for intermediate regions
    dx = target_pos.x - source_pos.x
    dy = target_pos.y - source_pos.y
    steps = max(abs(dx), abs(dy)) // REGION_SIZE + 1

    for i in range(int(steps) + 1):
        t = i / steps if steps > 0 else 0
        x = source_pos.x + t * dx
        y = source_pos.y + t * dy
        regions.add(calculate_region_id(x, y))

    return list(regions)
```

---

## Error Handling

### Client-Side Error Handling

```typescript
const { data, error, isLoading } = useGraphViewport(projectId, viewport, zoom, {
  onError: (error) => {
    if (error.status === 404) {
      toast.error('Project not found');
    } else if (error.status === 422) {
      toast.error('Invalid filter combination');
    } else {
      toast.error('Failed to load graph data');
    }
  },
  retry: 3,
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
});
```

### Server-Side Error Responses

**400 Bad Request:**

```json
{
  "code": "INVALID_VIEWPORT",
  "message": "Viewport bounds are invalid",
  "details": {
    "field": "viewport.maxX",
    "reason": "maxX must be greater than minX"
  }
}
```

**422 Unprocessable Entity:**

```json
{
  "code": "INVALID_FILTER_COMBINATION",
  "message": "Cannot combine perspective and manual type filters",
  "details": {
    "conflictingFields": ["perspective", "filters.nodeTypes"]
  }
}
```

**500 Internal Server Error:**

```json
{
  "code": "REGION_QUERY_FAILED",
  "message": "Failed to query graph regions",
  "details": {
    "regions": ["r_2_3", "r_2_4"],
    "error": "Database connection timeout"
  }
}
```

---

## Examples

### Example 1: Initial Viewport Load

**Request:**

```json
POST /api/v1/projects/550e8400-e29b-41d4-a716-446655440000/graph/viewport

{
  "viewport": {
    "minX": 0,
    "minY": 0,
    "maxX": 1200,
    "maxY": 800
  },
  "zoom": 1.0,
  "bufferPx": 300
}
```

**Response:**

```json
{
  "nodes": [
    {
      "id": "node-1",
      "type": "requirement",
      "title": "User Authentication",
      "status": "in_progress",
      "position": { "x": 400, "y": 300 },
      "data": {
        "id": "node-1",
        "item": { /* full item data */ },
        "connections": {
          "incoming": 2,
          "outgoing": 5,
          "total": 7,
          "byType": { "implements": 3, "tests": 2, "depends_on": 2 }
        },
        "depth": 1,
        "hasChildren": true
      }
    }
    // ... more nodes
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2",
      "type": "implements",
      "label": "Implemented by"
    }
    // ... more edges
  ],
  "metadata": {
    "hasMore": {
      "north": false,
      "south": true,
      "east": true,
      "west": false
    },
    "regionStats": {
      "totalNodes": 47,
      "totalEdges": 83,
      "regionsQueried": 8,
      "cacheHitRate": 0.0
    },
    "cacheKey": "viewport:550e8400:1_1:1.0:default",
    "timestamp": "2026-01-31T12:34:56Z"
  }
}
```

### Example 2: Panning Right

**Request:**

```json
POST /api/v1/projects/550e8400-e29b-41d4-a716-446655440000/graph/viewport

{
  "viewport": {
    "minX": 1000,
    "minY": 0,
    "maxX": 2200,
    "maxY": 800
  },
  "zoom": 1.0,
  "bufferPx": 300
}
```

**Response:**

```json
{
  "nodes": [ /* 32 new nodes */ ],
  "edges": [ /* 54 new edges */ ],
  "metadata": {
    "hasMore": {
      "north": false,
      "south": true,
      "east": true,
      "west": true
    },
    "regionStats": {
      "totalNodes": 32,
      "totalEdges": 54,
      "regionsQueried": 8,
      "cacheHitRate": 0.625  // 5 of 8 regions were cached
    },
    "cacheKey": "viewport:550e8400:3_1:1.0:default",
    "timestamp": "2026-01-31T12:35:12Z"
  }
}
```

### Example 3: Zooming In

**Request:**

```json
POST /api/v1/projects/550e8400-e29b-41d4-a716-446655440000/graph/viewport

{
  "viewport": {
    "minX": 400,
    "minY": 200,
    "maxX": 800,
    "maxY": 500
  },
  "zoom": 2.0,
  "bufferPx": 200
}
```

**Response:**

```json
{
  "nodes": [ /* 12 nodes in zoomed view */ ],
  "edges": [ /* 18 edges */ ],
  "metadata": {
    "hasMore": {
      "north": true,
      "south": true,
      "east": true,
      "west": true
    },
    "regionStats": {
      "totalNodes": 12,
      "totalEdges": 18,
      "regionsQueried": 4,
      "cacheHitRate": 1.0  // All cached from previous queries
    },
    "cacheKey": "viewport:550e8400:1_0:2.0:default",
    "timestamp": "2026-01-31T12:36:05Z"
  }
}
```

### Example 4: Filtered View

**Request:**

```json
POST /api/v1/projects/550e8400-e29b-41d4-a716-446655440000/graph/viewport

{
  "viewport": {
    "minX": 0,
    "minY": 0,
    "maxX": 1200,
    "maxY": 800
  },
  "zoom": 1.0,
  "bufferPx": 300,
  "filters": {
    "nodeTypes": ["requirement", "test_case"],
    "linkTypes": ["implements", "tests"],
    "statuses": ["in_progress", "done"]
  }
}
```

**Response:**

```json
{
  "nodes": [ /* 23 filtered nodes */ ],
  "edges": [ /* 31 filtered edges */ ],
  "metadata": {
    "hasMore": {
      "north": false,
      "south": true,
      "east": false,
      "west": false
    },
    "regionStats": {
      "totalNodes": 23,
      "totalEdges": 31,
      "regionsQueried": 8,
      "cacheHitRate": 0.0  // New filter = no cache hits
    },
    "cacheKey": "viewport:550e8400:1_1:1.0:filtered_abc123",
    "timestamp": "2026-01-31T12:37:22Z"
  }
}
```

---

## Migration Path

### Phase 1: Parallel Implementation (Week 1)

1. Implement new viewport endpoint alongside existing `GET /graph/full`
2. Add feature flag: `ENABLE_VIEWPORT_LOADING`
3. Deploy backend changes
4. Monitor performance metrics

### Phase 2: Client Integration (Week 2)

1. Update frontend graph components to use viewport API when flag enabled
2. Implement progressive loading UI (loading spinners for uncached regions)
3. A/B test with 10% of users

### Phase 3: Gradual Rollout (Week 3-4)

1. Increase rollout to 50% of users
2. Monitor error rates and performance
3. Tune cache TTLs and buffer sizes based on real usage

### Phase 4: Full Migration (Week 5)

1. Enable for 100% of users
2. Deprecate `GET /graph/full` endpoint
3. Remove legacy code

---

## Related Documents

- [Graph Virtualization Implementation Guide](./graph-virtualization-guide.md)
- [Caching Strategy Overview](./caching-strategy.md)
- [Performance Optimization Checklist](./performance-checklist.md)
- [API Versioning Policy](./api-versioning.md)

---

## Changelog

| Version | Date       | Author       | Changes                                  |
|---------|------------|--------------|------------------------------------------|
| 1.0     | 2026-01-31 | Claude Code  | Initial specification                    |

---

## Appendix: Database Schema Changes

### Required Migrations

**Migration:** Add region_id column to graph_nodes table

```sql
-- Migration: 045_add_graph_node_regions.sql

ALTER TABLE graph_nodes
ADD COLUMN region_id VARCHAR(20);

CREATE INDEX idx_graph_nodes_region
ON graph_nodes(project_id, region_id);

-- Backfill existing nodes with region assignments
UPDATE graph_nodes
SET region_id = 'r_' ||
    FLOOR(position_x / 500)::text || '_' ||
    FLOOR(position_y / 500)::text
WHERE region_id IS NULL;

ALTER TABLE graph_nodes
ALTER COLUMN region_id SET NOT NULL;
```

**Migration:** Add region associations for edges

```sql
-- Migration: 046_add_edge_regions.sql

CREATE TABLE edge_regions (
    edge_id UUID NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    region_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (edge_id, region_id)
);

CREATE INDEX idx_edge_regions_region
ON edge_regions(region_id);

-- Backfill existing edges
INSERT INTO edge_regions (edge_id, region_id)
SELECT DISTINCT
    l.id,
    'r_' ||
    FLOOR(LEAST(
        gn_source.position_x,
        gn_target.position_x
    ) / 500)::text || '_' ||
    FLOOR(LEAST(
        gn_source.position_y,
        gn_target.position_y
    ) / 500)::text
FROM links l
JOIN graph_nodes gn_source ON l.source_id = gn_source.item_id
JOIN graph_nodes gn_target ON l.target_id = gn_target.item_id;
```

### Database Triggers

**Trigger:** Auto-assign regions on node insert/update

```sql
CREATE OR REPLACE FUNCTION update_node_region()
RETURNS TRIGGER AS $$
BEGIN
    NEW.region_id := 'r_' ||
        FLOOR(NEW.position_x / 500)::text || '_' ||
        FLOOR(NEW.position_y / 500)::text;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_node_region
BEFORE INSERT OR UPDATE OF position_x, position_y
ON graph_nodes
FOR EACH ROW
EXECUTE FUNCTION update_node_region();
```

---

**End of Specification**
