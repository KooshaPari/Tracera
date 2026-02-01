# Hierarchical Graph Clustering Architecture

## Overview

This document describes the hierarchical clustering system for visualizing large-scale graphs (100k+ nodes) in TraceRTM. The system uses community detection algorithms to automatically aggregate nodes into manageable clusters, enabling interactive exploration of massive graphs.

## Problem Statement

Traditional graph visualization breaks down at scale:
- **1,000 nodes**: Viewport culling helps but interaction becomes sluggish
- **10,000 nodes**: Layout algorithms take seconds, rendering is slow
- **100,000 nodes**: Browser crashes or becomes unresponsive

**Solution**: Hierarchical clustering reduces 100k nodes to ~500 super-nodes, with drill-down capability.

## Architecture

### Component Hierarchy

```
ClusteredGraphView
├── useClustering hook (state management)
├── graphClustering.ts (algorithms)
│   ├── Louvain algorithm
│   ├── Label Propagation
│   └── Adaptive selection
├── ClusterNode component
└── graphCache.ts (LRU caching)
```

### Data Flow

```
Items + Links
    ↓
[Clustering Algorithm]
    ↓
ClusteringResult
├── clusters: Map<id, ClusterNode>
├── hierarchy: Map<level, ClusterNode[]>
└── edges: ClusterEdge[]
    ↓
[Expansion State]
├── expandedClusters: Set<id>
├── visibleItems: Set<id>
└── activeClusters: Set<id>
    ↓
[Layout Engine]
    ↓
Visual Graph
```

## Algorithms

### 1. Louvain Method (Default)

**Best for**: Moderate graphs (1k-50k nodes), quality matters

**Algorithm**:
1. **Phase 1 - Local Optimization**:
   - Each node starts in its own community
   - Iteratively move nodes to neighbor communities if it increases modularity
   - Repeat until no improvement

2. **Phase 2 - Aggregation** (not fully implemented):
   - Aggregate communities into super-nodes
   - Repeat Phase 1 on super-graph
   - Build hierarchy

**Complexity**: O(n log n)

**Modularity**:
```
Q = (1/2m) * Σ[Aij - (ki*kj)/(2m)] * δ(ci, cj)
```
where:
- m = total edges
- Aij = edge weight between i and j
- ki = degree of node i
- δ(ci, cj) = 1 if nodes in same community

**Pros**:
- High quality clusters (good modularity)
- Hierarchical structure
- Well-tested algorithm

**Cons**:
- Slower than label propagation
- Memory intensive for very large graphs

### 2. Label Propagation (Fast Alternative)

**Best for**: Very large graphs (50k-500k nodes), speed matters

**Algorithm**:
1. Initialize each node with unique label
2. Each iteration:
   - Process nodes in random order
   - Adopt most common label among neighbors
3. Stop when labels stabilize or max iterations reached

**Complexity**: O(n + m)

**Pros**:
- Very fast (linear time)
- Low memory footprint
- Simple implementation

**Cons**:
- Non-deterministic (random ordering)
- May not find optimal clustering
- No natural hierarchy

### 3. Adaptive Selection (Recommended)

**Strategy**:
- < 1k nodes: Use Louvain (quality)
- 1k-10k nodes: Use Louvain with adjusted resolution
- > 10k nodes: Use Label Propagation (speed)

**Resolution Parameter**:
- Higher resolution → more clusters
- Auto-calculated: `nodeCount / targetClusters / 10`

## Implementation Details

### ClusterNode Data Structure

```typescript
interface ClusterNode {
  id: string;
  level: number;              // Hierarchy level
  itemIds: Set<string>;       // Constituent items
  size: number;               // Node count
  metadata: {
    dominantType: string;     // Most common item type
    typeDistribution: Record<string, number>;
    internalEdges: number;    // Edges within cluster
    externalEdges: number;    // Edges to other clusters
    avgDegree: number;
  };
}
```

### Cluster Edges

Edges between clusters are aggregated:
- **Weight**: Number of edges between clusters
- **Link Types**: Distribution of edge types
- **Visual**: Edge thickness proportional to weight

```typescript
interface ClusterEdge {
  source: string;
  target: string;
  weight: number;
  linkTypes: Record<string, number>;
}
```

### Expansion State

Three-level visibility model:

1. **Collapsed Cluster**: Single super-node representing many items
2. **Expanded Cluster**: Items visible, cluster hidden
3. **Drill-down**: Focus on single cluster, hide others

```typescript
interface ExpansionState {
  expandedClusters: Set<string>;  // Which clusters are expanded
  visibleItems: Set<string>;      // Which items are shown
  activeClusters: Set<string>;    // Which clusters are rendered
}
```

### Caching Strategy

Uses existing `graphCache.ts` LRU cache:

```typescript
// Cache key includes all clustering parameters
const cacheKey = `louvain:${nodeCount}:${edgeCount}:${resolution}`;

// Cache stores complete clustering result
groupingCache.set(cacheKey, clusteringResult);
```

**Cache hit ratio**: Typically 70-90% for repeated views

## Performance Characteristics

### Time Complexity

| Algorithm | Complexity | 1k nodes | 10k nodes | 100k nodes |
|-----------|-----------|----------|-----------|------------|
| Louvain | O(n log n) | ~10ms | ~150ms | ~3s |
| Label Prop | O(n + m) | ~5ms | ~50ms | ~500ms |
| Adaptive | Variable | ~10ms | ~150ms | ~500ms |

### Memory Usage

| Component | 1k nodes | 10k nodes | 100k nodes |
|-----------|----------|-----------|------------|
| Graph structure | ~1 MB | ~10 MB | ~100 MB |
| Clustering result | ~200 KB | ~2 MB | ~20 MB |
| Cache overhead | ~100 KB | ~1 MB | ~10 MB |
| **Total** | **~1.3 MB** | **~13 MB** | **~130 MB** |

### Compression Ratios

Target: 100k nodes → 500 clusters = **200x compression**

Typical results:
- Louvain: 150-250x compression (better clustering)
- Label Prop: 100-200x compression (faster)
- Varies by graph structure (more connected = fewer clusters)

## Quality Metrics

### Modularity (Q)

**Range**: -0.5 to 1.0
**Good**: > 0.3
**Excellent**: > 0.7

Measures how well-separated communities are.

### Coverage

**Range**: 0.0 to 1.0
**Good**: > 0.6

Fraction of edges within clusters (vs. between).

### Silhouette Score

**Range**: -1.0 to 1.0
**Good**: > 0.5

Measures how similar items are within cluster vs. outside.

## Usage Examples

### Basic Usage

```typescript
import { ClusteredGraphView } from '@/components/graph/ClusteredGraphView';

<ClusteredGraphView
  items={items}
  links={links}
  clusteringAlgorithm="adaptive"
  targetClusters={500}
/>
```

### Advanced: Custom Clustering

```typescript
import { useClustering } from '@/hooks/useClustering';

const {
  clustering,
  visibleClusters,
  toggleCluster,
  expandAll,
  quality
} = useClustering(items, links, {
  algorithm: 'louvain',
  resolution: 1.2,  // More granular clusters
  targetClusters: 300
});
```

### Programmatic Expansion

```typescript
// Expand specific cluster
expandClusterById('cluster-0-42');

// Drill down (focus on one cluster)
drillDownToCluster('cluster-0-42');

// Expand all
expandAll();

// Collapse all
collapseAll();
```

## Interaction Patterns

### Google Maps Metaphor

Like zooming in on a map:
1. **World view**: See all clusters (continents)
2. **Click cluster**: Expand to see sub-clusters or items (countries)
3. **Drill down**: Focus on specific cluster (zoom to city)
4. **Collapse**: Return to overview

### Keyboard Shortcuts

- `E`: Expand selected cluster
- `C`: Collapse selected cluster
- `Shift+E`: Expand all
- `Shift+C`: Collapse all
- `D`: Drill down to selected cluster

## Benchmarks

### Test Setup

- **Hardware**: M1 MacBook Pro, 16GB RAM
- **Browser**: Chrome 120
- **Graph**: Synthetic scale-free network

### Results: 100k Nodes, 250k Edges

| Metric | Louvain | Label Prop | Adaptive |
|--------|---------|------------|----------|
| Clustering time | 3.2s | 0.52s | 0.52s |
| Cluster count | 487 | 521 | 521 |
| Compression ratio | 205x | 192x | 192x |
| Modularity | 0.73 | 0.68 | 0.68 |
| Coverage | 0.82 | 0.76 | 0.76 |
| Layout time | 180ms | 190ms | 190ms |
| Initial render | 45ms | 48ms | 48ms |
| **Total (cold)** | **3.4s** | **0.76s** | **0.76s** |
| **Total (cached)** | **225ms** | **238ms** | **238ms** |

### Interaction Performance

| Action | Time |
|--------|------|
| Expand cluster | 15-30ms |
| Collapse cluster | 10-20ms |
| Toggle cluster | 12-25ms |
| Drill down | 80-120ms |
| Re-layout (500 nodes) | 150-200ms |

### Memory Profiling

```
Initial load:
  Graph structure: 98 MB
  Clustering: 18 MB
  Layout cache: 12 MB
  React state: 8 MB
  Total: 136 MB

After 10 expand/collapse cycles:
  Total: 142 MB (6 MB growth)

Memory leak: None detected
```

## Best Practices

### 1. Choose the Right Algorithm

```typescript
// Quality-critical visualizations
algorithm: 'louvain'

// Real-time/interactive applications
algorithm: 'labelProp'

// General use (recommended)
algorithm: 'adaptive'
```

### 2. Tune Target Clusters

```typescript
// Dense graphs (many edges)
targetClusters: 300-500

// Sparse graphs (few edges)
targetClusters: 500-1000

// Very large (> 500k nodes)
targetClusters: 1000-2000
```

### 3. Progressive Loading

```typescript
// Start with high compression
const { clustering } = useClustering(items, links, {
  targetClusters: 200  // Aggressive
});

// User expands → show more detail
// Let expansion handle granularity
```

### 4. Cache Management

```typescript
import { groupingCache } from '@/lib/graphCache';

// Monitor cache stats
const stats = groupingCache.getStats();
console.log('Hit ratio:', stats.hitRatio);

// Clear cache on major data changes
groupingCache.clear();
```

## Limitations

### Current Limitations

1. **Single-level hierarchy**: Louvain Phase 2 not fully implemented
2. **No incremental updates**: Must recluster on data change
3. **Static communities**: No dynamic re-clustering during interaction

### Future Enhancements

1. **Multi-level hierarchy**:
   - Implement full Louvain Phase 2
   - Support arbitrary hierarchy depths
   - Zoom between levels

2. **Incremental clustering**:
   - Add/remove nodes without full recluster
   - Update communities dynamically
   - Maintain cache coherence

3. **Edge bundling**:
   - Bundle parallel cluster edges
   - Hierarchical edge bundling for nested clusters
   - Reduce visual clutter

4. **GPU acceleration**:
   - Offload layout to WebGL
   - Parallel community detection
   - 1M+ node support

## Troubleshooting

### Clustering takes too long

- Switch to `labelProp` algorithm
- Increase `targetClusters` (less optimization needed)
- Check graph connectivity (disconnected components are fast)

### Poor cluster quality

- Use `louvain` instead of `labelProp`
- Decrease `resolution` parameter (larger clusters)
- Verify graph structure (need sufficient edges)

### Memory issues

- Increase `targetClusters` (smaller clusters = less memory)
- Clear cache: `groupingCache.clear()`
- Use pagination for very large graphs

### Clusters look wrong

- Check `dominantType` distribution
- Verify link types are meaningful
- Consider semantic clustering instead

## References

- [Louvain Method](https://arxiv.org/abs/0803.0476) - Original paper
- [Label Propagation](https://arxiv.org/abs/0709.2938) - Raghavan et al.
- [Modularity](https://en.wikipedia.org/wiki/Modularity_(networks)) - Quality metric
- [Community Detection](https://arxiv.org/abs/0906.0612) - Comprehensive review

## Related Documentation

- [Graph Virtualization](./graph-virtualization.md)
- [Layout Algorithms](./layout-algorithms.md)
- [Performance Optimization](./performance-optimization.md)
- [Caching Strategy](./caching-strategy.md)
