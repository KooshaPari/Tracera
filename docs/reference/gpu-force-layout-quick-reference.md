# GPU Force-Directed Layout - Quick Reference

## Quick Start

```typescript
import { useGPUForceLayout } from '@/components/graph/layouts';

function MyGraph() {
  const { nodes, isComputing } = useGPUForceLayout(inputNodes, inputEdges);
  return <Graph nodes={nodes} edges={edges} />;
}
```

## API Reference

### useGPUForceLayout Hook

```typescript
const {
  nodes,           // Node[] - Layouted nodes
  isComputing,     // boolean - Is calculation running
  progress,        // number - Progress 0-1
  duration,        // number | null - Last calculation time (ms)
  error,           // string | null - Error message
  calculateLayout  // Function - Manual layout calculation
} = useGPUForceLayout(nodes, edges, options);
```

#### Options

```typescript
{
  enabled?: boolean;              // Default: true
  animateTransitions?: boolean;   // Default: true
  animationDuration?: number;     // Default: 800ms
  config?: {
    iterations?: number;          // Default: 300
    repulsionStrength?: number;   // Default: 5000
    attractionStrength?: number;  // Default: 0.1
    damping?: number;             // Default: 0.9
    theta?: number;               // Default: 0.5 (0=exact, 1=fast)
    minDistance?: number;         // Default: 10
    maxDistance?: number;         // Default: 1000
    centeringStrength?: number;   // Default: 0.01
  }
}
```

### GPUForceLayout Class

```typescript
import { getGPUForceLayout } from '@/components/graph/layouts';

const layout = getGPUForceLayout();
const result = await layout.simulate(nodes, edges, config);
```

### Direct Integration

```typescript
import { useDAGLayout } from '@/components/graph/layouts';

const { nodes } = useDAGLayout(
  inputNodes,
  inputEdges,
  'organic-network',  // Uses GPU force layout
  { nodeWidth: 200, nodeHeight: 80 }
);
```

## Configuration Presets

### Fast (Large Graphs >10k nodes)

```typescript
{
  iterations: 100,
  theta: 0.7,
  repulsionStrength: 3000,
  damping: 0.95
}
```

### Quality (Small Graphs <1k nodes)

```typescript
{
  iterations: 300,
  theta: 0.3,
  repulsionStrength: 5000,
  damping: 0.9
}
```

### Dense Graphs

```typescript
{
  iterations: 200,
  repulsionStrength: 8000,
  attractionStrength: 0.05,
  theta: 0.5
}
```

### Sparse Graphs

```typescript
{
  iterations: 150,
  repulsionStrength: 2000,
  attractionStrength: 0.2,
  centeringStrength: 0.02
}
```

## Performance Targets

| Nodes    | Target Time | Achieved |
|----------|-------------|----------|
| 100      | <100ms      | ✅       |
| 1,000    | <500ms      | ✅       |
| 5,000    | <2s         | ✅       |
| 10,000   | <3s         | ✅       |
| 50,000   | <5s         | ✅       |

## Barnes-Hut Theta Parameter

- **theta = 0:** Exact calculation (slowest, most accurate)
- **theta = 0.3:** High quality (recommended for <1k nodes)
- **theta = 0.5:** Balanced (default, good for most cases)
- **theta = 0.7:** Fast approximation (recommended for >10k nodes)
- **theta = 1.0:** Maximum speed (lowest quality)

## Worker Threshold

- **<1000 nodes:** Main thread
- **≥1000 nodes:** Web Worker (automatic)

## Common Patterns

### Progress Indicator

```typescript
const { progress, isComputing } = useGPUForceLayout(nodes, edges);

{isComputing && (
  <div>Computing: {Math.round(progress * 100)}%</div>
)}
```

### Performance Timing

```typescript
const { duration } = useGPUForceLayout(nodes, edges);

{duration && (
  <div>Layout calculated in {duration.toFixed(0)}ms</div>
)}
```

### Error Handling

```typescript
const { error, nodes } = useGPUForceLayout(inputNodes, edges);

if (error) {
  console.error('Layout failed:', error);
  // Falls back to original nodes
}
```

### Manual Calculation

```typescript
const { calculateLayout } = useGPUForceLayout([], [], { enabled: false });

const handleLayout = async () => {
  const result = await calculateLayout(nodes, edges);
  // Use result...
};
```

## Troubleshooting

### Slow Performance

1. Increase `theta` (0.5 → 0.7)
2. Reduce `iterations` (300 → 150)
3. Lower `repulsionStrength` for dense graphs

### Overlapping Nodes

1. Increase `repulsionStrength` (5000 → 8000)
2. Increase `iterations` (300 → 500)
3. Decrease `theta` for better accuracy

### Scattered Layout

1. Increase `centeringStrength` (0.01 → 0.05)
2. Increase `attractionStrength` (0.1 → 0.2)
3. Decrease `repulsionStrength`

### No Animation

```typescript
// Enable transitions
useGPUForceLayout(nodes, edges, {
  animateTransitions: true,
  animationDuration: 800
});
```

## Files

```
frontend/apps/web/src/components/graph/layouts/
├── gpuForceLayout.ts           # Core engine
├── gpuForceLayout.worker.ts    # Web Worker
├── useGPUForceLayout.ts        # React hook
├── useDAGLayout.ts             # Integration
└── __tests__/                  # Tests
    ├── gpuForceLayout.test.ts
    ├── gpuForceLayout.bench.test.ts
    └── useGPUForceLayout.test.tsx
```

## Examples

### Example 1: Simple Force Layout

```typescript
import { useGPUForceLayout } from '@/components/graph/layouts';

function SimpleGraph({ nodes, edges }) {
  const { nodes: layoutedNodes } = useGPUForceLayout(nodes, edges);
  return <ReactFlow nodes={layoutedNodes} edges={edges} />;
}
```

### Example 2: Custom Configuration

```typescript
function CustomGraph({ nodes, edges }) {
  const { nodes: layoutedNodes, isComputing } = useGPUForceLayout(
    nodes,
    edges,
    {
      config: {
        iterations: 200,
        repulsionStrength: 8000,
        theta: 0.6
      },
      animateTransitions: true
    }
  );

  return (
    <>
      {isComputing && <Spinner />}
      <ReactFlow nodes={layoutedNodes} edges={edges} />
    </>
  );
}
```

### Example 3: Large Graph Optimization

```typescript
function LargeGraph({ nodes, edges }) {
  const config = useMemo(() => {
    if (nodes.length > 10000) {
      return {
        iterations: 100,
        theta: 0.7,
        repulsionStrength: 3000
      };
    }
    return {
      iterations: 300,
      theta: 0.5
    };
  }, [nodes.length]);

  const { nodes: layoutedNodes, duration } = useGPUForceLayout(
    nodes,
    edges,
    { config }
  );

  return (
    <>
      <div>Layout time: {duration?.toFixed(0)}ms</div>
      <ReactFlow nodes={layoutedNodes} edges={edges} />
    </>
  );
}
```

## Testing

```bash
# Run unit tests
bun test src/components/graph/layouts/__tests__/gpuForceLayout.test.ts

# Run benchmarks
bun test src/components/graph/layouts/__tests__/gpuForceLayout.bench.test.ts

# Run hook tests
bun test src/components/graph/layouts/__tests__/useGPUForceLayout.test.tsx
```

## See Also

- [Full Completion Report](../reports/task-104-gpu-force-layout-completion.md)
- [Layout System Documentation](../guides/graph-layouts.md)
- XYFlow Documentation: https://reactflow.dev/
