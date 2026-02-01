# Edge Rendering Quick Start

**Target:** Render 1M+ edge graphs with <100 visible edges

## Installation

The edge aggregation library is already integrated into the graph components. No installation needed.

## Basic Usage

### 1. Import the Library

```typescript
import {
  applyLazyEdgeRendering,
  createDefaultSamplingConfig,
  createDefaultFilterConfig,
} from '@/lib/edgeAggregation';
```

### 2. Apply to Your Graph

```typescript
function MyGraphComponent({ items, links }) {
  // Auto-tuned configuration based on edge count
  const config = createDefaultSamplingConfig(links.length);
  const filterConfig = createDefaultFilterConfig();

  const { visibleEdges, stats } = applyLazyEdgeRendering(
    links,
    items,
    config,
    filterConfig
  );

  console.log(`Reduced ${stats.totalEdges} → ${stats.sampledEdges} edges`);
  console.log(`Render ratio: ${stats.renderRatio.toFixed(2)}%`);

  return <ReactFlow edges={visibleEdges} nodes={nodes} />;
}
```

### 3. Add Edge Type Filter (Optional)

```typescript
import { EdgeTypeFilter, useEdgeTypeFilter } from '@/components/graph/EdgeTypeFilter';

function GraphWithFilter({ items, links }) {
  const availableTypes = useMemo(
    () => [...new Set(links.map(l => l.type))],
    [links]
  );

  const { enabledTypes, toggleType, enableAll, disableAll } =
    useEdgeTypeFilter(availableTypes);

  const filterConfig = {
    enabledTypes,
    showRelatedForSelection: true,
    maxRelatedEdges: 100,
  };

  const { visibleEdges } = applyLazyEdgeRendering(
    links,
    items,
    createDefaultSamplingConfig(links.length),
    filterConfig
  );

  return (
    <>
      <EdgeTypeFilter
        availableTypes={availableTypes}
        enabledTypes={enabledTypes}
        onToggleType={toggleType}
        onEnableAll={enableAll}
        onDisableAll={disableAll}
        compact
      />
      <ReactFlow edges={visibleEdges} />
    </>
  );
}
```

## Configuration Options

### Auto-Tuned Configs (Recommended)

```typescript
const config = createDefaultSamplingConfig(edgeCount);
// Automatically selects strategy based on edge count:
// - <1K edges: importance sampling, 500 visible
// - 1K-10K: hybrid sampling, 300 visible
// - 10K-100K: hybrid sampling, 150 visible
// - >100K: statistical sampling, 100 visible
```

### Custom Configuration

```typescript
const customConfig = {
  maxVisibleEdges: 50,                    // Target visible edge count
  samplingStrategy: 'hybrid',             // 'statistical' | 'importance' | 'hybrid'
  priorityTypes: ['implements', 'tests'], // Important edge types
  minEdgesForAggregation: 5,              // Min parallel edges to aggregate
  canvasFallbackDensity: 100,             // Edges per 10000px² for canvas
};
```

### Filter Configuration

```typescript
const filterConfig = {
  enabledTypes: new Set(['implements', 'tests']), // Show only these types
  showRelatedForSelection: true,                  // Show edges for selected nodes
  maxRelatedEdges: 100,                          // Max edges per selection
};
```

## Performance Benchmarks

### Run in Browser Console

```typescript
// Run full benchmark suite
window.edgeBenchmark.run();

// Custom benchmark
window.edgeBenchmark.runCustom(
  2000,      // nodes
  1000000,   // edges
  'random',  // distribution: 'random' | 'clustered' | 'parallel'
  { maxVisibleEdges: 50 }
);
```

### Expected Results

| Graph Size | Visible Edges | Render Time | Ratio |
|-----------|---------------|-------------|-------|
| 1K edges | 500 | <5ms | 50% |
| 10K edges | 300 | <10ms | 3% |
| 100K edges | 150 | <50ms | 0.15% |
| **1M edges** | **<100** | **<100ms** | **0.01%** |

## Strategies Explained

### 1. Edge Aggregation
- **What:** Merges parallel edges (same source→target)
- **When:** 2+ edges between same nodes
- **Visual:** Thicker line with count badge
- **Example:** 1000 A→B edges → 1 aggregated edge

### 2. Statistical Sampling
- **What:** Renders representative 5% sample
- **When:** Dense edge clusters
- **Visual:** Fewer edges, same density perception
- **Example:** 10K edges → 500 sampled edges

### 3. Importance Sampling
- **What:** Prioritizes critical edge types
- **When:** Semantic relationships matter
- **Visual:** Critical edges always visible
- **Example:** Show all `implements` and `tests` edges

### 4. Canvas Fallback
- **What:** Use canvas for ultra-dense areas
- **When:** >50 edges per 10000px²
- **Visual:** Background heatmap
- **Example:** 10K edges in cluster → canvas background

## Common Patterns

### Pattern 1: Large Static Graph

```typescript
// For graphs that don't change often
const config = createDefaultSamplingConfig(links.length);
const { visibleEdges } = applyLazyEdgeRendering(links, items, config);

// Cache the result
const cachedEdges = useMemo(() => visibleEdges, [links, items]);
```

### Pattern 2: Interactive Filter

```typescript
// User can toggle edge types
const { enabledTypes, toggleType } = useEdgeTypeFilter(allTypes);
const filterConfig = { enabledTypes, ... };

const { visibleEdges } = applyLazyEdgeRendering(
  links,
  items,
  config,
  filterConfig
);
```

### Pattern 3: Selection-Based

```typescript
// Show only edges related to selected nodes
const [selectedNodeIds, setSelectedNodeIds] = useState(new Set());

const { visibleEdges } = applyLazyEdgeRendering(
  links,
  items,
  config,
  filterConfig,
  selectedNodeIds  // Only show related edges
);
```

## Troubleshooting

### Issue: Too Many Edges Still Rendered

**Solution:** Reduce `maxVisibleEdges` in config

```typescript
const config = {
  ...createDefaultSamplingConfig(links.length),
  maxVisibleEdges: 50,  // More aggressive
};
```

### Issue: Missing Important Edges

**Solution:** Use importance sampling with priority types

```typescript
const config = {
  ...createDefaultSamplingConfig(links.length),
  samplingStrategy: 'importance',
  priorityTypes: ['implements', 'tests', 'blocks'],
};
```

### Issue: Flicker When Zooming/Panning

**Solution:** Already handled! Sampling is deterministic (hash-based)
- Same edges visible every frame
- No temporal flicker

### Issue: Low Visual Quality

**Solution:** Increase sample ratio or use hybrid strategy

```typescript
const config = {
  ...createDefaultSamplingConfig(links.length),
  samplingStrategy: 'hybrid',  // Better quality than pure statistical
};
```

## API Reference

### `applyLazyEdgeRendering()`

Main function that applies all reduction strategies.

```typescript
function applyLazyEdgeRendering(
  edges: EdgeBase[],
  nodes: Node[],
  config: EdgeSamplingConfig,
  filterConfig?: EdgeFilterConfig,
  selectedNodeIds?: Set<string>
): {
  visibleEdges: AggregatedEdge[];
  stats: {
    totalEdges: number;
    aggregatedEdges: number;
    sampledEdges: number;
    filteredEdges: number;
    canvasClusters: number;
    renderRatio: number;
  };
  canvasClusters: DenseClusterInfo[];
}
```

### `EdgeTypeFilter` Component

User control for edge type visibility.

```typescript
interface EdgeTypeFilterProps {
  availableTypes: LinkType[];
  enabledTypes: Set<LinkType>;
  onToggleType: (type: LinkType) => void;
  onEnableAll: () => void;
  onDisableAll: () => void;
  edgeStats?: Record<LinkType, number>;
  compact?: boolean;
}
```

## Next Steps

1. **Read Architecture Doc:** `/docs/architecture/edge-rendering-strategies.md`
2. **Run Benchmarks:** `window.edgeBenchmark.run()`
3. **Customize Config:** Tune for your specific use case
4. **Monitor Performance:** Check render time and memory usage

## Support

- **Tests:** `/frontend/apps/web/src/__tests__/lib/edgeAggregation.test.ts`
- **Implementation:** `/frontend/apps/web/src/lib/edgeAggregation.ts`
- **Benchmark:** `/frontend/apps/web/src/lib/edgeBenchmark.ts`
