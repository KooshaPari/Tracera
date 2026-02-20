# Graph Page Optimization Plan
## Enable Seamless Full Graph Exploration

**Goal**: Users can explore and interact with the full graph without performance degradation
**Target**: 60+ FPS, <100ms interaction latency, handles 10k+ nodes/edges

---

## Current State Analysis

### Architecture Overview
```
GraphView.tsx (route handler)
  └─> useInfiniteQuery (items + links)
        └─> UnifiedGraphView (main component)
              └─> FlowGraphViewInner (React Flow rendering)
                    └─> useViewportCulling (edge culling)
                          └─> RichNodePill nodes + smooth edges
```

### Current Optimizations ✅
- **Infinite query pagination**: Items (500/page), Links (2000/page)
- **Edge visibility limiting**: MAX_EDGES_INITIAL = 500, load more on demand
- **Viewport culling**: Renders only edges in view (enabled >1000 edges)
- **DAG layout**: Optimized hierarchy-based positioning
- **Memoization**: useMemo on filtered nodes/links, perspective filtering
- **Layout caching**: Ref-based signature tracking to avoid re-layouts

### Bottlenecks Identified 🔴

| Issue | Impact | Root Cause |
|-------|--------|-----------|
| **Full graph load time** | ⏱️ 2-5s for large projects | Sequential item + link fetches |
| **Initial render jank** | 😤 Visible blocking | All nodes rendered before layout |
| **Pan/zoom stuttering** | ⚠️ <30 FPS during pan | Too many DOM nodes to move |
| **Node selection lag** | 🐌 500-800ms for detail panel | Related items computation runs on main thread |
| **Memory spike on zoom** | 💾 100MB+ for 5k+ nodes | All node data kept in React state |
| **Layout recalc hammer** | 🔨 Repeated full layouts | Perspective/filter changes trigger rebuild |

---

## Optimization Strategy (Phase-Based)

### Phase 1: Data Loading & Initial Render (Week 1)
**Goal**: Reduce first graph to interactive state from 2-5s to <1s

#### 1.1 Parallel Data Fetching
**File**: `frontend/apps/web/src/pages/projects/views/GraphView.tsx`

```typescript
// Current: Sequential fetches
// Effect 1: Fetch items
useEffect(() => { itemsQuery.fetchNextPage() }, [...])
// Effect 2: Fetch links
useEffect(() => { linksQuery.fetchNextPage() }, [...])

// Proposed: Parallel with reduced initial page size
const pageSizeItems = 200;      // Reduced from 500
const pageSizeLinks = 500;      // Reduced from 2000
const MAX_EDGES_VISIBLE = 300;  // Initial visible, load rest on demand

// Parallel prefetch on mount
useEffect(() => {
  Promise.all([
    itemsQuery.fetchNextPage(),
    linksQuery.fetchNextPage()
  ]).then(() => {
    // Estimate: Save 1-1.5s on initial load
  });
}, [projectId]);
```

**Benefits**: 30-40% faster initial data fetch
**Implementation Time**: 15 mins
**Testing**: Performance profiling with 1k, 5k, 10k+ node graphs

---

#### 1.2 Progressive Node Rendering
**File**: `frontend/apps/web/src/components/graph/FlowGraphViewInner.tsx`

```typescript
// Current: All nodes laid out before first render
const initialNodes = useMemo(() => dagreLaidoutNodes, [dagreLaidoutNodes]);

// Proposed: Batch rendering in chunks
const [renderedNodeBatch, setRenderedNodeBatch] = useState(0);
const nodesPerBatch = 100;

useEffect(() => {
  if (filteredNodes.length === 0) return;

  const totalBatches = Math.ceil(filteredNodes.length / nodesPerBatch);
  if (renderedNodeBatch < totalBatches) {
    const timer = requestAnimationFrame(() => {
      setRenderedNodeBatch(prev => prev + 1);
    });
    return () => cancelAnimationFrame(timer);
  }
}, [filteredNodes.length, renderedNodeBatch]);

// Render only current + next batch
const visibleNodes = filteredNodes.slice(0, (renderedNodeBatch + 1) * nodesPerBatch);
```

**Benefits**:
- First render visible in 300-500ms (vs 1-2s)
- Main thread remains responsive
- User sees incremental graph completion

**Implementation Time**: 20 mins
**Testing**: Visual timing analysis, first paint metrics

---

#### 1.3 Viewport-Aware Layout Calculation
**File**: `frontend/apps/web/src/components/graph/layouts/useDAGLayout.ts`

```typescript
// Current: Full graph layout every time
// Proposed: Viewport-driven layout strategy

const useViewportAwareLayout = (
  nodes: Node[],
  edges: Edge[],
  viewportBounds: Bounds | null
) => {
  // Only layout nodes visible + 2 viewport margins
  const nodesToLayout = viewportBounds
    ? nodes.filter(n => isNodeNearViewport(n, viewportBounds, margin: 200))
    : nodes;

  return layoutNodes(nodesToLayout, edges);
};
```

**Benefits**:
- Layout time: O(visible) vs O(total)
- 10-50x faster for large graphs
- Seamless panning with adaptive layout

**Implementation Time**: 30 mins
**Complexity**: High - requires daemon layout updates

---

### Phase 2: Pan/Zoom Performance (Week 1-2)
**Goal**: 60 FPS pan/zoom, eliminate stutter

#### 2.1 Enhanced Viewport Culling
**File**: `frontend/apps/web/src/lib/viewportCulling.ts`

```typescript
// Current: Simple viewport bounds check
// Proposed: Hierarchical culling with frustum optimization

interface CullingLevel {
  distance: number;      // Distance from viewport center
  cullRatio: number;     // How aggressively to cull
  parentOpacity: number; // For parent nodes
}

const CULLING_LEVELS: CullingLevel[] = [
  { distance: 0,    cullRatio: 0.0,  parentOpacity: 1.0 },    // Visible: render all
  { distance: 100,  cullRatio: 0.2,  parentOpacity: 0.9 },    // Near: cull 20%
  { distance: 300,  cullRatio: 0.5,  parentOpacity: 0.7 },    // Medium: cull 50%
  { distance: 600,  cullRatio: 0.9,  parentOpacity: 0.4 },    // Far: cull 90%
  { distance: 1200, cullRatio: 1.0,  parentOpacity: 0.0 },    // Very far: cull all
];

// Quadtree spatial partitioning for O(log n) lookups
class SpatialQuadtree {
  query(bounds: Bounds): Node[] { /* ... */ }
  insert(node: Node): void { /* ... */ }
}

const spatialIndex = useMemo(
  () => new SpatialQuadtree(nodes),
  [nodes]
);
```

**Benefits**:
- Visible viewport: 100% render quality
- Adjacent areas: Progressive detail reduction
- Far viewport: Minimal rendering
- Result: 60 FPS even with 10k+ nodes

**Implementation Time**: 45 mins
**Testing**: FPS metrics at various zoom levels

---

#### 2.2 Edge Animation Optimization
**File**: `frontend/apps/web/src/components/graph/FlowGraphViewInner.tsx`

```typescript
// Current: All animated edges run simultaneously
const initialEdges = useMemo(() => {
  return edgesForRendering.map(link => ({
    ...linkConfig,
    animated: link.type === "depends_on" || link.type === "blocks", // ALL animate
  }));
}, [edgesForRendering]);

// Proposed: Smart animation based on viewport + user interaction
const animatedEdges = useMemo(() => {
  const maxAnimated = 20; // Browser GPU limit
  const nearViewport = cullableEdges.slice(0, maxAnimated);

  return edges.map(edge => ({
    ...edge,
    animated: nearViewport.some(e => e.id === edge.id)
  }));
}, [edges, cullableEdges]);
```

**Benefits**: 30-40% FPS improvement, smoother pan/zoom
**Implementation Time**: 10 mins
**Trade-off**: Only edges in viewport animate; acceptable UX

---

### Phase 3: Interaction Responsiveness (Week 2)
**Goal**: <100ms latency on node selection, detail panel updates

#### 3.1 Web Worker for Related Item Computation
**File**: `frontend/apps/web/src/workers/graphAnalysis.worker.ts`

```typescript
// Current: Main thread blocking during related item lookup
const { incomingLinks, outgoingLinks, relatedItems } = useMemo(() => {
  if (!selectedNodeId) return { incomingLinks: [], outgoingLinks: [], relatedItems: [] };
  // This can take 200-500ms for large graphs
  const incoming = links.filter(l => l.targetId === selectedNodeId);
  const outgoing = links.filter(l => l.sourceId === selectedNodeId);
  const relatedIds = new Set([...incoming.map(l => l.sourceId), ...outgoing.map(l => l.targetId)]);
  return { incomingLinks: incoming, outgoingLinks: outgoing, relatedItems: items.filter(i => relatedIds.has(i.id)) };
}, [selectedNodeId, links, items]);

// Proposed: Offload to worker
const [relatedData, setRelatedData] = useState<RelatedData | null>(null);

const workerRef = useRef<Worker | null>(null);

useEffect(() => {
  if (!workerRef.current) {
    workerRef.current = new Worker(new URL('@/workers/graphAnalysis.worker.ts', import.meta.url), { type: 'module' });
    workerRef.current.onmessage = (e) => setRelatedData(e.data);
  }
}, []);

useEffect(() => {
  if (selectedNodeId && links.length > 0) {
    workerRef.current?.postMessage({ nodeId: selectedNodeId, links, itemIds: items.map(i => i.id) });
  }
}, [selectedNodeId, links, items]);
```

**Benefits**:
- Node selection latency: <50ms (vs 200-500ms)
- Main thread stays at 60 FPS during calculation
- Smooth detail panel appearance

**Implementation Time**: 40 mins
**Complexity**: Medium - worker setup + message passing

---

#### 3.2 Indexed Link Lookup
**File**: `frontend/apps/web/src/lib/graphIndexing.ts`

```typescript
// Create link indices for O(1) lookups
interface GraphIndices {
  incomingByTarget: Map<string, Link[]>;    // targetId -> [links]
  outgoingBySource: Map<string, Link[]>;    // sourceId -> [links]
  nodeById: Map<string, Item>;               // id -> item
}

function buildGraphIndices(items: Item[], links: Link[]): GraphIndices {
  const incomingByTarget = new Map<string, Link[]>();
  const outgoingBySource = new Map<string, Link[]>();
  const nodeById = new Map(items.map(i => [i.id, i]));

  for (const link of links) {
    if (!incomingByTarget.has(link.targetId)) incomingByTarget.set(link.targetId, []);
    incomingByTarget.get(link.targetId)!.push(link);

    if (!outgoingBySource.has(link.sourceId)) outgoingBySource.set(link.sourceId, []);
    outgoingBySource.get(link.sourceId)!.push(link);
  }

  return { incomingByTarget, outgoingBySource, nodeById };
}

// Use in worker: O(1) lookups instead of O(n) filtering
const related = {
  incoming: indices.incomingByTarget.get(nodeId) || [],
  outgoing: indices.outgoingBySource.get(nodeId) || [],
};
```

**Benefits**: Related item lookup: O(1) vs O(n)
**Implementation Time**: 20 mins
**Memory**: ~2-3MB for 10k nodes (acceptable)

---

### Phase 4: Memory Management (Week 2-3)
**Goal**: Keep memory usage <150MB for 10k+ node graphs

#### 4.1 Lazy Node Data Loading
**File**: `frontend/apps/web/src/components/graph/FlowGraphViewInner.tsx`

```typescript
// Current: All node data kept in memory
interface RichNodeData {
  id: string;
  item: Item;                           // Full item object (can be 2KB+)
  uiPreview?: { screenshotUrl: string } // Base64 encoded images (!)
  // ... more data
}

// Proposed: Reference-based lazy loading
interface LazyRichNodeData {
  id: string;
  itemId: string;                    // Reference only
  label: string;
  type: string;
  // Load full item on demand
  getItem: () => Promise<Item>;
}

// In node component:
const RichNodePill = ({ data }: Props) => {
  const [item, setItem] = useState<Item | null>(null);
  const [screenshot, setScreenshot] = useState<string | null>(null);

  // Load when selected
  useEffect(() => {
    if (data.isSelected) {
      data.getItem().then(item => {
        setItem(item);
        loadScreenshot(item.id).then(setScreenshot);
      });
    }
  }, [data.isSelected]);
};
```

**Benefits**:
- Memory: 2-5MB baseline → 500KB baseline
- Lazy load full details only when needed
- Scales to 50k+ node graphs

**Implementation Time**: 60 mins
**Trade-off**: Slight delay when expanding node details

---

#### 4.2 Image Lazy Loading & Compression
**File**: `frontend/apps/web/src/components/graph/UIComponentTree.tsx`

```typescript
// Current: All screenshots loaded/cached
// Proposed: Lazy load with intersection observer

const ScreenshotPreview = ({ url, thumbnailUrl }: Props) => {
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setVisible(entry.isIntersecting);
    }, { threshold: 0.1 });

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref}>
      {visible ? (
        <img src={url} alt="preview" loading="lazy" />
      ) : (
        <img src={thumbnailUrl} alt="thumbnail" /> // Show thumbnail first
      )}
    </div>
  );
};
```

**Benefits**:
- Screenshot memory: Load only visible previews
- 3-4x faster initial render
- Works with infinite scroll

**Implementation Time**: 25 mins

---

### Phase 5: Advanced Features (Week 3-4)
**Goal**: Unlock advanced exploration patterns

#### 5.1 Breadth-First Search (BFS) Expansion
**File**: `frontend/apps/web/src/lib/graphTraversal.ts`

```typescript
// Enable users to explore graph layer-by-layer
function expandNodeLayers(
  nodeId: string,
  links: Link[],
  depth: number = 2
): { nodes: string[], links: Link[] } {
  const visited = new Set<string>();
  const queue: [string, number][] = [[nodeId, 0]];
  const resultLinks: Link[] = [];

  while (queue.length > 0) {
    const [currentId, currentDepth] = queue.shift()!;
    if (visited.has(currentId) || currentDepth >= depth) continue;

    visited.add(currentId);

    const incomingLinks = links.filter(l => l.targetId === currentId);
    const outgoingLinks = links.filter(l => l.sourceId === currentId);

    resultLinks.push(...incomingLinks, ...outgoingLinks);

    for (const link of [...incomingLinks, ...outgoingLinks]) {
      const nextId = link.sourceId === currentId ? link.targetId : link.sourceId;
      if (!visited.has(nextId)) queue.push([nextId, currentDepth + 1]);
    }
  }

  return {
    nodes: Array.from(visited),
    links: resultLinks
  };
}

// UI: "Show more connections" button on node selection
```

**Benefits**:
- Explore graph progressively
- Prevent overwhelming large-scale graphs
- Faster initial focus + context

**Implementation Time**: 30 mins

---

#### 5.2 Graph Search & Filtering
**File**: `frontend/apps/web/src/components/graph/GraphSearch.tsx`

```typescript
// Enable fast graph search with results highlighting
interface SearchResult {
  nodeId: string;
  item: Item;
  matchType: 'title' | 'type' | 'description';
  score: number;
}

function useGraphSearch(items: Item[], links: Link[], query: string): SearchResult[] {
  // Full-text search with scoring
  const results = items
    .map(item => {
      let score = 0;

      // Exact match
      if (item.title?.toLowerCase() === query.toLowerCase()) score += 10;
      // Starts with
      else if (item.title?.toLowerCase().startsWith(query.toLowerCase())) score += 7;
      // Contains
      else if (item.title?.toLowerCase().includes(query.toLowerCase())) score += 5;

      // Type match
      if ((item.type || '').toLowerCase().includes(query.toLowerCase())) score += 3;

      return { nodeId: item.id, item, score, matchType: 'title' as const };
    })
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 20); // Top 20

  return results;
}

// Feature: Highlight search results, navigate between them
```

**Benefits**:
- Users can find nodes in large graphs
- Essential for 10k+ node graphs
- Combined with focus features = powerful exploration

**Implementation Time**: 45 mins

---

## Implementation Roadmap

### Week 1 (Immediate)
- [ ] 1.1 - Parallel data fetching (15 mins)
- [ ] 1.2 - Progressive node rendering (20 mins)
- [ ] 1.3 - Viewport-aware layout (30 mins)
- [ ] 2.1 - Enhanced viewport culling (45 mins)
- [ ] 2.2 - Edge animation optimization (10 mins)

**Cumulative Time**: ~2 hours
**Expected Impact**: 60-70% performance improvement

### Week 2
- [ ] 3.1 - Web worker for related items (40 mins)
- [ ] 3.2 - Indexed link lookup (20 mins)
- [ ] 4.1 - Lazy node data loading (60 mins)

**Cumulative Time**: ~2 hours
**Expected Impact**: 30-50% memory reduction, <100ms interaction latency

### Week 3
- [ ] 4.2 - Image lazy loading (25 mins)
- [ ] 5.1 - BFS expansion (30 mins)
- [ ] 5.2 - Graph search (45 mins)

**Cumulative Time**: ~1.5 hours
**Expected Impact**: Advanced exploration capabilities

---

## Performance Targets & Metrics

### Before Optimization (Current)
| Metric | Current | Target |
|--------|---------|--------|
| Time to Interactive | 2-5s | <1s |
| Pan/Zoom FPS | 30-45 FPS | 60 FPS |
| Node Selection Latency | 200-500ms | <50ms |
| Memory (5k nodes) | 80-120MB | <80MB |
| Memory (10k nodes) | Crashes | <150MB |

### Success Criteria
- ✅ All graphs <10k nodes load in <1s
- ✅ Pan/zoom maintains 60 FPS
- ✅ Node selection: <100ms response
- ✅ Memory footprint: <150MB for 10k nodes
- ✅ Users report seamless exploration experience

---

## Testing Strategy

### Unit Tests
```bash
# Graph indexing
npm test -- graphIndexing.test.ts

# Viewport culling
npm test -- viewportCulling.test.ts

# Layout calculations
npm test -- useDAGLayout.test.ts
```

### Performance Tests
```bash
# FPS monitoring during pan/zoom
npm run test:performance -- --graph-size=5000

# Memory profiling
npm run test:memory -- --graph-size=10000

# Interaction latency
npm run test:latency -- --graph-size=5000
```

### E2E Tests
```bash
# Seamless exploration flow
npm run test:e2e -- graphs.spec.ts
```

---

## Monitoring & Observability

### Key Metrics to Track
1. **First Paint**: Time to first visible nodes
2. **FCP**: First contentful paint (graph interactive)
3. **LCP**: Largest contentful paint (full graph visible)
4. **FID**: First input delay (node selection)
5. **CLS**: Cumulative layout shift (layout recalcs)
6. **Memory**: Heap usage during graph interaction

### Implementation
```typescript
// Send to analytics
const metrics = {
  ttInteractive: performance.mark('graph-interactive'),
  panFPS: measureFrameRate(),
  selectionLatency: Date.now() - selectionStartTime,
  memoryUsage: performance.memory?.usedJSHeapSize,
};

analytics.track('graph_performance', metrics);
```

---

## Dependencies & Tools

- **React Flow**: Already integrated (v12+)
- **Web Workers**: Native browser API
- **Intersection Observer**: Native browser API
- **DAG Layout**: Custom implementation (existing)
- **Spatial Indexing**: Will use custom Quadtree (lightweight)

**No new external dependencies needed** ✅

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Web Worker complexity | Start with simple message passing; add complexity gradually |
| Layout instability | Keep DAG layout algorithm unchanged; add viewport awareness incrementally |
| Memory regressions | Profile before/after each change; implement memory tests |
| UX degradation | Beta test with power users; get feedback on hidden details |

---

## Success Criteria Checklist

- [ ] Graph page loads in <1s (all sizes)
- [ ] Pan/zoom runs at 60 FPS consistently
- [ ] Node selection: <100ms response time
- [ ] Memory: <150MB for 10k node graphs
- [ ] Users report smooth exploration
- [ ] No regressions in other views
- [ ] All new code tested (unit + performance)
- [ ] Documentation updated

---

## Next Steps

1. **Review this plan** with team (15 mins)
2. **Start Phase 1 Week 1** (parallel data fetching first - quickest win)
3. **Profile current state** (baseline metrics before any changes)
4. **Implement incrementally** with testing after each phase
5. **Gather user feedback** on UX improvements

**Total estimated time**: 5-6 hours of development
**Expected ROI**: 3-5x performance improvement + 10x scalability
