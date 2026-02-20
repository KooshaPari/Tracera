# Graph Clustering Quick Start

## Overview

Graph clustering reduces 100k+ nodes into manageable super-nodes for interactive exploration. Think Google Maps: world → country → city → street.

## Basic Usage

### 1. Simple Clustered View

```typescript
import { ClusteredGraphView } from '@/components/graph';

<ClusteredGraphView
  items={items}           // Your graph nodes
  links={links}           // Your graph edges
  targetClusters={500}    // Compress to ~500 clusters
/>
```

### 2. Custom Algorithm

```typescript
<ClusteredGraphView
  items={items}
  links={links}
  clusteringAlgorithm="louvain"  // or "labelProp", "adaptive"
  targetClusters={300}
/>
```

### 3. Programmatic Control

```typescript
import { useClustering } from '@/hooks';

function MyGraph() {
  const {
    clustering,
    visibleClusters,
    visibleItems,
    toggleCluster,
    expandAll,
    collapseAll,
    quality
  } = useClustering(items, links, {
    algorithm: 'adaptive',
    targetClusters: 500
  });

  return (
    <div>
      <button onClick={expandAll}>Expand All</button>
      <button onClick={collapseAll}>Collapse All</button>
      <div>Modularity: {quality?.modularity.toFixed(3)}</div>
      {/* Render clustered graph */}
    </div>
  );
}
```

## Algorithm Selection

### Louvain (Best Quality)
- **Use when**: Quality > Speed, graphs < 50k nodes
- **Complexity**: O(n log n)
- **Best modularity** (0.7+)

```typescript
algorithm: 'louvain'
resolution: 1.0  // Lower = larger clusters
```

### Label Propagation (Fastest)
- **Use when**: Speed > Quality, graphs > 50k nodes
- **Complexity**: O(n + m)
- **Fast** but lower quality (0.6+ modularity)

```typescript
algorithm: 'labelProp'
```

### Adaptive (Recommended)
- **Use when**: Unsure, general purpose
- **Auto-selects**: Louvain for small, Label Prop for large
- **Best default**

```typescript
algorithm: 'adaptive'
targetClusters: 500  // Desired cluster count
```

## Common Patterns

### 1. Progressive Exploration

Start collapsed, let users drill down:

```typescript
const {
  visibleClusters,
  toggleCluster,
  drillDownToCluster
} = useClustering(items, links);

// User clicks cluster
<ClusterNode
  data={{
    cluster,
    onToggle: toggleCluster,
    onDrillDown: drillDownToCluster
  }}
/>
```

### 2. Focus on Area

Show only one cluster's contents:

```typescript
const { drillDownToCluster } = useClustering(items, links);

// Focus on specific cluster
drillDownToCluster('cluster-0-42');
```

### 3. Quality Monitoring

Track clustering quality in real-time:

```typescript
const { quality, compressionRatio } = useClustering(items, links);

console.log('Modularity:', quality.modularity);
console.log('Compression:', compressionRatio, 'x');
```

## Performance Tips

### 1. Target Cluster Count

```typescript
// Dense graphs (many edges)
targetClusters: 300-500

// Sparse graphs (few edges)
targetClusters: 500-1000

// Very large (> 500k nodes)
targetClusters: 1000-2000
```

### 2. Algorithm Selection

```typescript
// < 1k nodes: Use Louvain (quality)
if (nodeCount < 1000) algorithm = 'louvain';

// 1k-10k nodes: Use Louvain (balanced)
else if (nodeCount < 10000) algorithm = 'louvain';

// > 10k nodes: Use Label Prop (speed)
else algorithm = 'labelProp';

// Or just use 'adaptive' (does this automatically)
```

### 3. Caching

Results are automatically cached:

```typescript
import { groupingCache } from '@/lib/graphCache';

// Check cache stats
const stats = groupingCache.getStats();
console.log('Hit ratio:', stats.hitRatio);

// Clear cache on data change
groupingCache.clear();
```

## Component Props

### ClusteredGraphView

```typescript
interface ClusteredGraphViewProps {
  items: Item[];                           // Graph nodes
  links: Link[];                           // Graph edges
  onNavigateToItem?: (id: string) => void; // Item click handler
  showControls?: boolean;                  // Show toolbar
  autoFit?: boolean;                       // Auto-fit viewport
  clusteringAlgorithm?: 'louvain' | 'labelProp' | 'adaptive';
  targetClusters?: number;                 // Desired cluster count
}
```

### ClusterNode

```typescript
interface ClusterNodeData {
  cluster: ClusterNode;       // Cluster metadata
  items: Item[];              // Items in cluster
  links: Link[];              // Edges in cluster
  isExpanded: boolean;        // Expansion state
  level: number;              // Hierarchy level
  onToggle: (id: string) => void;       // Toggle handler
  onDrillDown?: (id: string) => void;   // Drill-down handler
  onItemSelect?: (id: string) => void;  // Item click handler
}
```

## Metrics

### Compression Ratio

How much the graph is reduced:

```typescript
const { compressionRatio } = useClustering(items, links);

// 100k nodes → 500 clusters = 200x compression
console.log(`${compressionRatio}x compression`);
```

### Modularity (Q)

Quality of clustering (0-1, higher = better):

```typescript
const { quality } = useClustering(items, links);

console.log('Q =', quality.modularity);

// Good: > 0.3
// Excellent: > 0.7
```

### Coverage

Fraction of edges within clusters:

```typescript
const { quality } = useClustering(items, links);

console.log('Coverage:', quality.coverage);

// Good: > 0.6
```

## Troubleshooting

### Clustering is slow

```typescript
// Switch to faster algorithm
algorithm: 'labelProp'

// Or increase target clusters
targetClusters: 1000  // Less optimization needed
```

### Poor cluster quality

```typescript
// Use higher quality algorithm
algorithm: 'louvain'

// Or adjust resolution
resolution: 0.8  // Larger clusters
```

### Clusters look wrong

```typescript
// Check your graph structure
console.log('Nodes:', items.length);
console.log('Edges:', links.length);
console.log('Avg degree:', links.length * 2 / items.length);

// Sparse graphs (avg degree < 2) cluster poorly
// Solution: Use semantic grouping instead
```

## Examples

### Example 1: Basic Clustering

```typescript
import { ClusteredGraphView } from '@/components/graph';

export function MyGraphView({ items, links }) {
  return (
    <ClusteredGraphView
      items={items}
      links={links}
      targetClusters={500}
      onNavigateToItem={(id) => console.log('Navigate:', id)}
    />
  );
}
```

### Example 2: Advanced Control

```typescript
import { useClustering } from '@/hooks';
import { ClusterNode } from '@/components/graph';

export function AdvancedGraphView({ items, links }) {
  const {
    clustering,
    visibleClusters,
    toggleCluster,
    quality,
    isProcessing
  } = useClustering(items, links, {
    algorithm: 'louvain',
    resolution: 1.2,
    targetClusters: 300
  });

  if (isProcessing) return <div>Clustering...</div>;

  return (
    <div>
      <div>
        Modularity: {quality?.modularity.toFixed(3)}
        ({clustering?.totalClusters} clusters)
      </div>
      {visibleClusters.map(cluster => (
        <ClusterNode
          key={cluster.id}
          data={{
            cluster,
            items: items.filter(i => cluster.itemIds.has(i.id)),
            links,
            isExpanded: false,
            level: cluster.level,
            onToggle: toggleCluster
          }}
        />
      ))}
    </div>
  );
}
```

### Example 3: Performance Monitoring

```typescript
import { useClustering } from '@/hooks';
import { groupingCache } from '@/lib/graphCache';

export function MonitoredGraphView({ items, links }) {
  const { clustering, quality } = useClustering(items, links);
  const cacheStats = groupingCache.getStats();

  return (
    <div>
      <div>Nodes: {items.length}</div>
      <div>Clusters: {clustering?.totalClusters}</div>
      <div>Compression: {clustering?.compressionRatio.toFixed(1)}x</div>
      <div>Modularity: {quality?.modularity.toFixed(3)}</div>
      <div>Cache Hit Ratio: {(cacheStats.hitRatio * 100).toFixed(1)}%</div>
      {/* Graph visualization */}
    </div>
  );
}
```

## Benchmarks

### Small Graph (1k nodes)
- Louvain: ~10ms
- Label Prop: ~5ms
- Clusters: ~50-100
- Compression: ~10-20x

### Medium Graph (10k nodes)
- Louvain: ~150ms
- Label Prop: ~50ms
- Clusters: ~100-200
- Compression: ~50-100x

### Large Graph (100k nodes)
- Louvain: ~3s
- Label Prop: ~500ms
- Clusters: ~500-1000
- Compression: ~100-200x

## Next Steps

- [Full Architecture Documentation](../../architecture/hierarchical-clustering.md)
- [Benchmark Tests](../../../frontend/apps/web/src/__tests__/lib/graphClustering.bench.ts)
- [Algorithm Details](../../architecture/hierarchical-clustering.md#algorithms)
- [Performance Tuning](../../architecture/hierarchical-clustering.md#best-practices)
