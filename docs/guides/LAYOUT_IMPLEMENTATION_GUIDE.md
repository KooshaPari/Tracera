# Graph Layout Implementation Guide for React Flow

Quick reference for implementing layout algorithms in traceability tools.

## Quick Start Decision Tree

```
Do you have a DAG (requirements → tests → releases)?
├─ YES
│  └─ < 500 nodes? → Use Dagre (simple, fast)
│  └─ > 500 nodes or complex deps? → Use ELK (powerful, configurable)
│
└─ NO (exploratory data)
   └─ Use D3-Force (organic, natural arrangement)
```

---

## 1. Installation & Setup

### All Libraries
```bash
npm install @dagrejs/dagre elkjs d3-force @xyflow/react
```

### Import Statements
```typescript
import dagre from '@dagrejs/dagre';
import ELK from 'elkjs/lib/elk.bundled.js';
import { forceSimulation, forceLink, forceManyBody, forceCenter } from 'd3-force';
import { useNodes, useEdges, useReactFlow } from '@xyflow/react';
```

---

## 2. Complete Working Examples

### Example 1: Dagre Layout (Simplest)

**File: `hooks/useDagreLayout.ts`**
```typescript
import { useCallback } from 'react';
import dagre from '@dagrejs/dagre';
import { Node, Edge } from '@xyflow/react';

type Direction = 'TB' | 'BT' | 'LR' | 'RL';

export const useDagreLayout = () => {
  const layoutNodes = useCallback(
    (nodes: Node[], edges: Edge[], direction: Direction = 'TB'): Node[] => {
      if (!nodes.length) return nodes;

      const g = new dagre.graphlib.Graph({ compound: true });
      g.setGraph({
        rankdir: direction,
        nodesep: 80,
        ranksep: 100,
        marginx: 0,
        marginy: 0
      });
      g.setDefaultEdgeLabel(() => ({}));

      nodes.forEach(node => {
        g.setNode(node.id, {
          width: node.measured?.width || 150,
          height: node.measured?.height || 50
        });
      });

      edges.forEach(edge => {
        g.setEdge(edge.source, edge.target);
      });

      dagre.layout(g);

      return nodes.map(node => {
        const dagNode = g.node(node.id);
        return {
          ...node,
          position: {
            x: dagNode.x - (node.measured?.width || 150) / 2,
            y: dagNode.y - (node.measured?.height || 50) / 2
          }
        };
      });
    },
    []
  );

  return { layoutNodes };
};
```

**Usage Component:**
```typescript
import { useNodes, useEdges, useReactFlow } from '@xyflow/react';
import { useDagreLayout } from '@/hooks/useDagreLayout';

function DagreLayoutComponent() {
  const nodes = useNodes();
  const edges = useEdges();
  const { getNodes, setNodes } = useReactFlow();
  const { layoutNodes } = useDagreLayout();

  const handleLayoutFlow = () => {
    const layouted = layoutNodes(getNodes(), edges, 'TB');
    setNodes(layouted);
  };

  const handleLayoutHorizontal = () => {
    const layouted = layoutNodes(getNodes(), edges, 'LR');
    setNodes(layouted);
  };

  return (
    <div className="layout-controls">
      <button onClick={handleLayoutFlow}>Flow Chart</button>
      <button onClick={handleLayoutHorizontal}>Horizontal</button>
    </div>
  );
}

export default DagreLayoutComponent;
```

---

### Example 2: ELK Layout (Most Powerful)

**File: `hooks/useELKLayout.ts`**
```typescript
import { useCallback } from 'react';
import ELK from 'elkjs/lib/elk.bundled.js';
import { Node, Edge } from '@xyflow/react';

const elk = new ELK();

interface ELKConfig {
  [key: string]: any;
}

const DEFAULT_ELK_CONFIG: ELKConfig = {
  'elk.algorithm': 'layered',
  'elk.direction': 'DOWN',
  'elk.layered.spacing.nodeNodeBetweenLayers': 100,
  'elk.spacing.nodeNode': 80,
  'elk.edgeRouting': 'ORTHOGONAL',
  'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP'
};

export const useELKLayout = () => {
  const layoutNodes = useCallback(
    async (
      nodes: Node[],
      edges: Edge[],
      config: Partial<ELKConfig> = {}
    ): Promise<Node[]> => {
      if (!nodes.length) return nodes;

      const elkConfig = { ...DEFAULT_ELK_CONFIG, ...config };

      const graph = {
        id: 'root',
        layoutOptions: elkConfig,
        children: nodes.map(node => ({
          id: node.id,
          width: node.measured?.width || 150,
          height: node.measured?.height || 50
        })),
        edges: edges.map(edge => ({
          id: `${edge.source}-${edge.target}`,
          sources: [edge.source],
          targets: [edge.target]
        }))
      };

      try {
        const layoutedGraph = await elk.layout(graph);

        return nodes.map(node => {
          const elkNode = layoutedGraph.children?.find(
            (child: any) => child.id === node.id
          );
          if (!elkNode) return node;

          return {
            ...node,
            position: {
              x: (elkNode.x || 0) - (node.measured?.width || 150) / 2,
              y: (elkNode.y || 0) - (node.measured?.height || 50) / 2
            }
          };
        });
      } catch (error) {
        console.error('ELK layout error:', error);
        return nodes;
      }
    },
    []
  );

  return { layoutNodes };
};
```

**Usage Component:**
```typescript
import { useState } from 'react';
import { useNodes, useEdges, useReactFlow } from '@xyflow/react';
import { useELKLayout } from '@/hooks/useELKLayout';

function ELKLayoutComponent() {
  const nodes = useNodes();
  const edges = useEdges();
  const { getNodes, setNodes } = useReactFlow();
  const { layoutNodes } = useELKLayout();
  const [isLoading, setIsLoading] = useState(false);

  const handleLayout = async (direction: string) => {
    setIsLoading(true);
    try {
      const layouted = await layoutNodes(getNodes(), edges, {
        'elk.direction': direction
      });
      setNodes(layouted);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="layout-controls">
      <button onClick={() => handleLayout('DOWN')} disabled={isLoading}>
        Vertical
      </button>
      <button onClick={() => handleLayout('RIGHT')} disabled={isLoading}>
        Horizontal
      </button>
    </div>
  );
}

export default ELKLayoutComponent;
```

---

### Example 3: Force-Directed Layout (Organic)

**File: `hooks/useForceLayout.ts`**
```typescript
import { useCallback, useRef } from 'react';
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  Simulation
} from 'd3-force';
import { Node, Edge } from '@xyflow/react';

interface ForceConfig {
  chargeStrength?: number;
  linkDistance?: number;
  centerStrength?: number;
  iterations?: number;
  width?: number;
  height?: number;
}

export const useForceLayout = () => {
  const simulationRef = useRef<Simulation<any, undefined> | null>(null);

  const layoutNodes = useCallback(
    (
      nodes: Node[],
      edges: Edge[],
      config: ForceConfig = {}
    ): Promise<Node[]> => {
      return new Promise(resolve => {
        if (!nodes.length) {
          resolve(nodes);
          return;
        }

        const {
          chargeStrength = -300,
          linkDistance = 100,
          centerStrength = 0.1,
          iterations = 300,
          width = 1200,
          height = 800
        } = config;

        // Stop any existing simulation
        if (simulationRef.current) {
          simulationRef.current.stop();
        }

        const d3Nodes = nodes.map((node, i) => ({
          id: node.id,
          index: i,
          x: Math.random() * width,
          y: Math.random() * height,
          vx: 0,
          vy: 0
        }));

        const d3Links = edges
          .map(edge => ({
            source: d3Nodes.findIndex(n => n.id === edge.source),
            target: d3Nodes.findIndex(n => n.id === edge.target)
          }))
          .filter(link => link.source >= 0 && link.target >= 0);

        const simulation = forceSimulation(d3Nodes)
          .force('link', forceLink(d3Links).distance(linkDistance))
          .force('charge', forceManyBody().strength(chargeStrength))
          .force('center', forceCenter(width / 2, height / 2).strength(centerStrength))
          .stop();

        // Run simulation
        simulation.tick(iterations);

        const layoutedNodes = nodes.map(node => {
          const d3Node = d3Nodes.find(n => n.id === node.id);
          return {
            ...node,
            position: {
              x: (d3Node?.x || 0) - (node.measured?.width || 150) / 2,
              y: (d3Node?.y || 0) - (node.measured?.height || 50) / 2
            }
          };
        });

        simulationRef.current = simulation;
        resolve(layoutedNodes);
      });
    },
    []
  );

  const stopSimulation = useCallback(() => {
    if (simulationRef.current) {
      simulationRef.current.stop();
    }
  }, []);

  return { layoutNodes, stopSimulation };
};
```

**Usage Component:**
```typescript
import { useState } from 'react';
import { useNodes, useEdges, useReactFlow } from '@xyflow/react';
import { useForceLayout } from '@/hooks/useForceLayout';

function ForceLayoutComponent() {
  const nodes = useNodes();
  const edges = useEdges();
  const { getNodes, setNodes } = useReactFlow();
  const { layoutNodes } = useForceLayout();
  const [isLoading, setIsLoading] = useState(false);

  const handleLayout = async () => {
    setIsLoading(true);
    try {
      const layouted = await layoutNodes(getNodes(), edges, {
        chargeStrength: -400,
        linkDistance: 120,
        iterations: 300,
        width: 1200,
        height: 800
      });
      setNodes(layouted);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button onClick={handleLayout} disabled={isLoading}>
      Arrange Organically
    </button>
  );
}

export default ForceLayoutComponent;
```

---

## 3. Master Layout Selector Component

**File: `components/LayoutSelector.tsx`**

```typescript
import React, { useState } from 'react';
import { useNodes, useEdges, useReactFlow } from '@xyflow/react';
import { useDagreLayout } from '@/hooks/useDagreLayout';
import { useELKLayout } from '@/hooks/useELKLayout';
import { useForceLayout } from '@/hooks/useForceLayout';
import './LayoutSelector.css';

type LayoutType = 'flowchart' | 'hierarchical' | 'mindmap' | 'organic';

interface LayoutOption {
  id: LayoutType;
  label: string;
  description: string;
  icon: string;
  type: 'sync' | 'async';
}

const LAYOUT_OPTIONS: LayoutOption[] = [
  {
    id: 'flowchart',
    label: 'Flow Chart',
    description: 'Top-to-bottom dependencies',
    icon: '🔄',
    type: 'sync'
  },
  {
    id: 'hierarchical',
    label: 'Hierarchical',
    description: 'Minimize crossing lines',
    icon: '🔗',
    type: 'async'
  },
  {
    id: 'mindmap',
    label: 'Mind Map',
    description: 'Central node with branches',
    icon: '🧠',
    type: 'sync'
  },
  {
    id: 'organic',
    label: 'Organic Network',
    description: 'Natural arrangement',
    icon: '🌐',
    type: 'async'
  }
];

export function LayoutSelector() {
  const nodes = useNodes();
  const edges = useEdges();
  const { getNodes, setNodes } = useReactFlow();
  const { layoutNodes: dagreLayout } = useDagreLayout();
  const { layoutNodes: elkLayout } = useELKLayout();
  const { layoutNodes: forceLayout } = useForceLayout();
  const [isLoading, setIsLoading] = useState(false);
  const [activeLayout, setActiveLayout] = useState<LayoutType | null>(null);

  const handleLayoutChange = async (layoutType: LayoutType) => {
    setIsLoading(true);
    setActiveLayout(layoutType);

    try {
      const currentNodes = getNodes();
      let layoutedNodes: Node[];

      switch (layoutType) {
        case 'flowchart':
          layoutedNodes = dagreLayout(currentNodes, edges, 'TB');
          break;

        case 'hierarchical':
          layoutedNodes = await elkLayout(currentNodes, edges, {
            'elk.direction': 'RIGHT',
            'elk.layered.spacing.nodeNodeBetweenLayers': 100,
            'elk.spacing.nodeNode': 80
          });
          break;

        case 'mindmap':
          layoutedNodes = dagreLayout(currentNodes, edges, 'LR');
          break;

        case 'organic':
          layoutedNodes = await forceLayout(currentNodes, edges, {
            chargeStrength: -400,
            linkDistance: 120,
            iterations: 300,
            width: 1200,
            height: 800
          });
          break;

        default:
          layoutedNodes = currentNodes;
      }

      setNodes(layoutedNodes);
    } catch (error) {
      console.error(`Layout error (${layoutType}):`, error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="layout-selector">
      <div className="layout-title">Layout</div>
      <div className="layout-options">
        {LAYOUT_OPTIONS.map(option => (
          <button
            key={option.id}
            className={`layout-button ${activeLayout === option.id ? 'active' : ''}`}
            onClick={() => handleLayoutChange(option.id)}
            disabled={isLoading}
            title={option.description}
          >
            <span className="layout-icon">{option.icon}</span>
            <span className="layout-label">{option.label}</span>
          </button>
        ))}
      </div>
      {isLoading && <div className="layout-loading">Calculating layout...</div>}
    </div>
  );
}

export default LayoutSelector;
```

**File: `components/LayoutSelector.css`**

```css
.layout-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: #f9f9f9;
  border-bottom: 1px solid #e0e0e0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.layout-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: #666;
  letter-spacing: 0.5px;
  padding: 0 4px;
}

.layout-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.layout-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 12px;
  background: white;
  border: 1.5px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 90px;
  text-align: center;
}

.layout-button:hover:not(:disabled) {
  border-color: #999;
  background: #fafafa;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.layout-button.active {
  border-color: #0066cc;
  background: #e6f0ff;
  color: #0066cc;
  box-shadow: 0 2px 8px rgba(0, 102, 204, 0.15);
}

.layout-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.layout-icon {
  font-size: 18px;
}

.layout-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.layout-loading {
  font-size: 12px;
  color: #666;
  text-align: center;
  padding: 8px 4px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .layout-selector {
    padding: 10px;
  }

  .layout-button {
    min-width: 80px;
    padding: 8px 10px;
    font-size: 12px;
  }

  .layout-icon {
    font-size: 16px;
  }
}
```

---

## 4. Integration with React Flow

**File: `components/DiagramContainer.tsx`**

```typescript
import React from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useReactFlow,
  useNodesState,
  useEdgesState
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import LayoutSelector from './LayoutSelector';
import CustomNode from './CustomNode';

interface DiagramContainerProps {
  initialNodes: Node[];
  initialEdges: Edge[];
}

const nodeTypes = {
  custom: CustomNode
};

export function DiagramContainer({
  initialNodes,
  initialEdges
}: DiagramContainerProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <LayoutSelector />

      <div style={{ flex: 1 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}

export default DiagramContainer;
```

---

## 5. Usage Examples

### Example 1: Requirements Graph
```typescript
const nodes = [
  {
    id: 'REQ-001',
    data: { label: 'User Login' },
    position: { x: 0, y: 0 },
    type: 'custom'
  },
  {
    id: 'TEST-001',
    data: { label: 'Test Login Flow' },
    position: { x: 0, y: 100 },
    type: 'custom'
  }
];

const edges = [
  {
    id: 'e1',
    source: 'REQ-001',
    target: 'TEST-001'
  }
];
```

### Example 2: Load from API
```typescript
function DiagramPage() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGraph() {
      try {
        const response = await fetch('/api/requirements/graph');
        const data = await response.json();
        setNodes(data.nodes);
        setEdges(data.edges);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <DiagramContainer initialNodes={nodes} initialEdges={edges} />
  );
}
```

---

## 6. Configuration Presets

**File: `config/layoutPresets.ts`**

```typescript
export const LAYOUT_PRESETS = {
  COMPACT: {
    dagre: { rankdir: 'TB', nodesep: 40, ranksep: 50 },
    elk: {
      'elk.spacing.nodeNode': 40,
      'elk.layered.spacing.nodeNodeBetweenLayers': 50
    },
    force: { chargeStrength: -200, linkDistance: 80 }
  },

  STANDARD: {
    dagre: { rankdir: 'TB', nodesep: 80, ranksep: 100 },
    elk: {
      'elk.spacing.nodeNode': 80,
      'elk.layered.spacing.nodeNodeBetweenLayers': 100
    },
    force: { chargeStrength: -300, linkDistance: 100 }
  },

  SPACIOUS: {
    dagre: { rankdir: 'TB', nodesep: 120, ranksep: 150 },
    elk: {
      'elk.spacing.nodeNode': 120,
      'elk.layered.spacing.nodeNodeBetweenLayers': 150
    },
    force: { chargeStrength: -400, linkDistance: 150 }
  },

  HORIZONTAL: {
    dagre: { rankdir: 'LR', nodesep: 100, ranksep: 150 },
    elk: {
      'elk.direction': 'RIGHT',
      'elk.spacing.nodeNode': 100,
      'elk.layered.spacing.nodeNodeBetweenLayers': 150
    }
  }
};
```

---

## 7. Testing Layout Functions

**File: `__tests__/layouts.test.ts`**

```typescript
import { useDagreLayout } from '@/hooks/useDagreLayout';
import { useELKLayout } from '@/hooks/useELKLayout';
import { useForceLayout } from '@/hooks/useForceLayout';
import { renderHook } from '@testing-library/react';

describe('Layout Hooks', () => {
  const mockNodes = [
    { id: '1', data: { label: 'Node 1' }, position: { x: 0, y: 0 }, measured: { width: 150, height: 50 } },
    { id: '2', data: { label: 'Node 2' }, position: { x: 0, y: 0 }, measured: { width: 150, height: 50 } }
  ];

  const mockEdges = [
    { id: 'e1', source: '1', target: '2' }
  ];

  test('Dagre layout positions nodes deterministically', () => {
    const { result } = renderHook(() => useDagreLayout());
    const layouted = result.current.layoutNodes(mockNodes, mockEdges, 'TB');

    expect(layouted).toHaveLength(2);
    expect(layouted[0].position).toBeDefined();
    expect(layouted[1].position).toBeDefined();
    expect(layouted[0].position.y).toBeLessThan(layouted[1].position.y);
  });

  test('ELK layout handles async positioning', async () => {
    const { result } = renderHook(() => useELKLayout());
    const layouted = await result.current.layoutNodes(mockNodes, mockEdges);

    expect(layouted).toHaveLength(2);
    expect(layouted[0].position).toBeDefined();
  });

  test('Force layout returns promise', async () => {
    const { result } = renderHook(() => useForceLayout());
    const promise = result.current.layoutNodes(mockNodes, mockEdges);

    expect(promise).toBeInstanceOf(Promise);
    const layouted = await promise;
    expect(layouted).toHaveLength(2);
  });
});
```

---

## 8. Performance Tips

### Tip 1: Memoize Layout Hooks
```typescript
const { layoutNodes } = useDagreLayout(); // Already memoized with useCallback
```

### Tip 2: Lazy Load Large Graphs
```typescript
const handleLayout = async (type) => {
  if (nodes.length > 1000) {
    // Use clustering first
    const clustered = clusterNodes(nodes);
    const layouted = await layoutNodes(clustered, edges);
    setNodes(layouted);
  } else {
    const layouted = await layoutNodes(nodes, edges);
    setNodes(layouted);
  }
};
```

### Tip 3: Debounce on Node Changes
```typescript
const handleNodeChange = useMemo(
  () => debounce((changes) => {
    onNodesChange(changes);
    // Trigger layout recalculation
  }, 300),
  []
);
```

---

## 9. Troubleshooting

### Issue: Nodes Overlapping
**Solution**: Increase `nodesep` and `ranksep` in Dagre config
```typescript
{ rankdir: 'TB', nodesep: 120, ranksep: 150 }
```

### Issue: Layout Calculation Too Slow
**Solution**: Use Dagre for large graphs, consider clustering
```typescript
if (nodes.length > 500) {
  // Use Dagre instead of ELK
  const layouted = dagreLayout(nodes, edges);
}
```

### Issue: ELK Taking Forever
**Solution**: Reduce `iterations` or disable edge routing
```typescript
{
  'elk.direction': 'DOWN',
  'elk.edgeRouting': 'POLYLINE' // Faster than ORTHOGONAL
}
```

### Issue: Force Layout Not Converging
**Solution**: Increase iterations or adjust forces
```typescript
{
  chargeStrength: -300,
  linkDistance: 100,
  iterations: 500 // Increase from default 300
}
```

---

## Summary Table

| Task | Use | Code |
|---|---|---|
| Quick hierarchical layout | Dagre | `dagreLayout(nodes, edges, 'TB')` |
| Complex DAGs | ELK | `await elkLayout(nodes, edges, config)` |
| Exploratory visualization | Force | `await forceLayout(nodes, edges)` |
| Rapid prototyping | Dagre | Simplest API |
| Enterprise production | ELK | Most configurable |

---

## Next Steps

1. Copy hook implementations to your project
2. Add `LayoutSelector` component to your diagram view
3. Test with your actual requirement graphs
4. Adjust spacing and configuration based on visual feedback
5. Implement clustering for graphs > 500 nodes
