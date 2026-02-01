# Node Aggregation Implementation Guide
## Practical Patterns for React Flow in Your Traceability Application

**Target:** Ready-to-implement code patterns for your existing FlowGraphViewInner component

---

## Quick Start: Three Implementation Levels

### Level 1: Type-Based Aggregation (1-2 hours)
**What you get:** Reduces 200 nodes to 12-15 aggregate groups
**Effort:** Low - minimal changes to existing code

### Level 2: Shared Dependency Clustering (4-6 hours)
**What you get:** Reveals architectural bottlenecks and dependency patterns
**Effort:** Medium - requires pre-processing logic

### Level 3: Full Multi-Level System (2-3 days)
**What you get:** User-controlled aggregation levels with smooth UX
**Effort:** High - but maximum flexibility

---

## Level 1: Type-Based Aggregation

### Step 1: Create Aggregation Types

Add to `/frontend/apps/web/src/components/graph/types.ts`:

```typescript
// Add to existing types
export interface AggregateNodeData extends EnhancedNodeData {
  aggregateType: "type-based" | "shared-dependency" | "community";
  childNodeIds: string[];
  childCount: number;
  isExpanded: boolean;
  externalIncoming: number;
  externalOutgoing: number;
  internalConnections: number;
}

// Configuration
export const AGGREGATION_CONFIG = {
  enabled: true,
  typeThreshold: 6,        // Aggregate if >6 nodes of same type
  excludeTypes: ["requirement", "epic", "feature"], // Never aggregate
  expandByDefault: false,
} as const;
```

### Step 2: Create Aggregation Utility

New file: `/frontend/apps/web/src/components/graph/utils/aggregation.ts`

```typescript
import type { EnhancedNodeData, Link } from "../types";

interface AggregateGroup {
  type: string;
  nodes: EnhancedNodeData[];
  externalIncoming: number;
  externalOutgoing: number;
  internalConnections: number;
}

export function groupNodesByType(
  nodes: EnhancedNodeData[],
  links: Link[],
  threshold: number,
  excludeTypes: string[]
): Map<string, AggregateGroup> {
  const groups = new Map<string, EnhancedNodeData[]>();

  // Group nodes by type
  for (const node of nodes) {
    const type = node.type.toLowerCase();
    if (!groups.has(type)) {
      groups.set(type, []);
    }
    groups.get(type)!.push(node);
  }

  // Filter groups and compute statistics
  const result = new Map<string, AggregateGroup>();

  for (const [type, typeNodes] of groups) {
    // Skip excluded types or small groups
    if (excludeTypes.includes(type) || typeNodes.length <= threshold) {
      // Don't aggregate - return individual nodes
      for (const node of typeNodes) {
        result.set(`node-${node.id}`, {
          type: "individual",
          nodes: [node],
          externalIncoming: node.connections.incoming,
          externalOutgoing: node.connections.outgoing,
          internalConnections: 0,
        });
      }
      continue;
    }

    // Create aggregate
    const nodeIds = typeNodes.map(n => n.id);
    let internalConnections = 0;

    // Count internal vs external connections
    let externalIncoming = 0;
    let externalOutgoing = 0;

    const nodeIdSet = new Set(nodeIds);

    for (const link of links) {
      const isInternal =
        nodeIdSet.has(link.sourceId) && nodeIdSet.has(link.targetId);
      const fromInside = nodeIdSet.has(link.sourceId);
      const toInside = nodeIdSet.has(link.targetId);

      if (isInternal) {
        internalConnections++;
      } else if (toInside) {
        externalIncoming++;
      } else if (fromInside) {
        externalOutgoing++;
      }
    }

    result.set(`agg-${type}`, {
      type,
      nodes: typeNodes,
      externalIncoming,
      externalOutgoing,
      internalConnections,
    });
  }

  return result;
}

export function createAggregateNodeData(
  group: AggregateGroup,
  aggregateId: string
): AggregateNodeData {
  return {
    id: aggregateId,
    item: {} as any, // Aggregate has no single item
    type: group.type,
    status: "todo" as const,
    label: `${group.type.replace(/_/g, " ")} (${group.nodes.length})`,
    perspective: [] as any,
    connections: {
      incoming: group.externalIncoming,
      outgoing: group.externalOutgoing,
      total: group.externalIncoming + group.externalOutgoing,
      byType: {} as any,
    },
    depth: 0,
    hasChildren: false,
    aggregateType: "type-based",
    childNodeIds: group.nodes.map(n => n.id),
    childCount: group.nodes.length,
    isExpanded: false,
    externalIncoming: group.externalIncoming,
    externalOutgoing: group.externalOutgoing,
    internalConnections: group.internalConnections,
  };
}
```

### Step 3: Create Aggregate Node Component

New file: `/frontend/apps/web/src/components/graph/nodes/AggregateGroupNode.tsx`

```typescript
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
  ChevronDown,
  GitBranch,
  ArrowDownLeft,
  ArrowUpRight,
} from "lucide-react";
import { memo, useState, useCallback } from "react";
import type { AggregateNodeData } from "../types";
import { ENHANCED_TYPE_COLORS } from "../types";

interface AggregateGroupNodeProps
  extends NodeProps<Node<AggregateNodeData, "aggregateGroup">> {
  onExpand?: (nodeId: string, isExpanded: boolean) => void;
}

function AggregateGroupNodeComponent({
  data,
  selected,
  onExpand,
}: AggregateGroupNodeProps) {
  const [isExpanded, setIsExpanded] = useState(data.isExpanded || false);

  const bgColor = ENHANCED_TYPE_COLORS[data.type] || "#64748b";

  const handleExpandClick = useCallback(() => {
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    onExpand?.(data.id, newExpanded);
  }, [isExpanded, data.id, onExpand]);

  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-background !border-2"
        style={{ borderColor: bgColor }}
      />

      <Card
        className={`
          relative overflow-hidden transition-all duration-200 cursor-pointer
          border-2
          ${selected ? "ring-2 ring-white ring-offset-2 ring-offset-background" : ""}
          ${isExpanded ? "border-solid" : "border-dashed"}
        `}
        style={{
          borderColor: bgColor,
          backgroundColor: `${bgColor}08`,
          minWidth: 200,
          maxWidth: 280,
        }}
      >
        {/* Header */}
        <div className="p-3">
          {/* Top row: Icon + Expand Button */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div
                className="flex-shrink-0 rounded p-1.5"
                style={{ backgroundColor: `${bgColor}20` }}
              >
                <GitBranch
                  className="h-4 w-4"
                  style={{ color: bgColor }}
                />
              </div>
              <Badge
                variant="outline"
                className="text-[10px] px-1.5 h-5"
                style={{
                  backgroundColor: `${bgColor}15`,
                  color: bgColor,
                  borderColor: `${bgColor}40`,
                }}
              >
                {data.type.replace(/_/g, " ")}
              </Badge>
            </div>

            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={handleExpandClick}
            >
              <ChevronDown
                className="h-4 w-4"
                style={{
                  transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "transform 200ms",
                }}
              />
            </Button>
          </div>

          {/* Title */}
          <h4 className="font-semibold text-sm leading-tight mb-2">
            {data.label}
          </h4>

          {/* Connection Summary */}
          <div className="flex items-center gap-3 text-[10px] text-muted-foreground mb-2">
            {data.externalIncoming > 0 && (
              <div className="flex items-center gap-1">
                <ArrowDownLeft className="h-3 w-3" />
                <span>{data.externalIncoming} in</span>
              </div>
            )}
            {data.externalOutgoing > 0 && (
              <div className="flex items-center gap-1">
                <ArrowUpRight className="h-3 w-3" />
                <span>{data.externalOutgoing} out</span>
              </div>
            )}
            {data.internalConnections > 0 && (
              <div className="flex items-center gap-1">
                <GitBranch className="h-3 w-3" />
                <span>{data.internalConnections}</span>
              </div>
            )}
          </div>

          {/* Expanded Content */}
          {isExpanded && (
            <div className="mt-3 pt-3 border-t space-y-2">
              <div className="text-xs font-medium text-muted-foreground">
                {data.childCount} items:
              </div>
              <div className="space-y-1 max-h-40 overflow-auto">
                {data.childNodeIds.slice(0, 8).map(id => (
                  <div
                    key={id}
                    className="text-xs px-2 py-1 bg-muted/50 rounded truncate"
                    title={id}
                  >
                    {id}
                  </div>
                ))}
                {data.childNodeIds.length > 8 && (
                  <div className="text-xs text-muted-foreground px-2 py-1 italic">
                    +{data.childNodeIds.length - 8} more
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </Card>

      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-background !border-2"
        style={{ borderColor: bgColor }}
      />
    </>
  );
}

export const AggregateGroupNode = memo(AggregateGroupNodeComponent);
```

### Step 4: Integrate into FlowGraphViewInner

Modify `/frontend/apps/web/src/components/graph/FlowGraphViewInner.tsx`:

```typescript
import { AggregateGroupNode } from "./nodes/AggregateGroupNode";
import {
  groupNodesByType,
  createAggregateNodeData,
} from "./utils/aggregation";
import { AGGREGATION_CONFIG } from "./types";

// Add to nodeTypes object
const nodeTypes = {
  richPill: RichNodePill,
  aggregateGroup: AggregateGroupNode, // ADD THIS
} as const satisfies NodeTypes;

// Modify the enhancedNodes processing
export function FlowGraphViewInner({
  items,
  links,
  perspective: externalPerspective,
  onNavigateToItem,
  showControls = true,
  autoFit = true,
  enableAggregation = true, // NEW PROP
}: FlowGraphViewInnerProps & { enableAggregation?: boolean }) {
  // ... existing state ...
  const [expandedAggregates, setExpandedAggregates] = useState<Set<string>>(new Set());

  // After filtering by perspective, apply aggregation
  const processedNodes = useMemo(() => {
    if (!enableAggregation || AGGREGATION_CONFIG.enabled === false) {
      return filteredNodes;
    }

    const groups = groupNodesByType(
      filteredNodes,
      filteredLinks,
      AGGREGATION_CONFIG.typeThreshold,
      AGGREGATION_CONFIG.excludeTypes
    );

    // Separate aggregates from individual nodes
    const aggregates: AggregateNodeData[] = [];
    const individuals: EnhancedNodeData[] = [];

    for (const [key, group] of groups) {
      if (key.startsWith("agg-")) {
        const aggData = createAggregateNodeData(group, key);
        aggregates.push({
          ...aggData,
          isExpanded: expandedAggregates.has(key),
        });
      } else if (group.nodes.length === 1) {
        individuals.push(group.nodes[0]);
      }
    }

    return [...individuals, ...aggregates] as (EnhancedNodeData | AggregateNodeData)[];
  }, [filteredNodes, filteredLinks, enableAggregation, expandedAggregates]);

  // When creating layout, handle both node types
  const calculateLayout = useCallback((nodes: any[], layoutType: LayoutType) => {
    // ... existing layout code ...
    // The nodeWidth/nodeHeight can be adjusted for aggregate nodes
    // Aggregates typically need 20-30px more width
  }, [createNodeData]);

  // Add handler for aggregate expansion
  const handleAggregateExpand = useCallback((nodeId: string, isExpanded: boolean) => {
    setExpandedAggregates(prev => {
      const next = new Set(prev);
      if (isExpanded) {
        next.add(nodeId);
      } else {
        next.delete(nodeId);
      }
      return next;
    });
  }, []);

  // Update nodes creation to pass handler
  const initialNodes = useMemo(
    () => {
      const baseNodes = calculateLayout(processedNodes, layout);
      // Add onExpand callback to aggregate nodes
      return baseNodes.map(node => {
        if (node.type === "aggregateGroup") {
          return {
            ...node,
            data: {
              ...node.data,
              // onExpand will be called through node props
            },
          };
        }
        return node;
      });
    },
    [processedNodes, layout, calculateLayout]
  );

  // ... rest of component stays the same ...
}
```

### Step 5: Add Toggle to Controls

In the controls section, add aggregation toggle:

```typescript
{showControls && (
  <Card className="mb-3 p-2">
    <div className="flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        {/* Aggregation toggle */}
        <Button
          variant={enableAggregation ? "default" : "outline"}
          size="sm"
          onClick={() => setEnableAggregation(!enableAggregation)}
          className="h-8"
        >
          <Package className="h-4 w-4 mr-1" />
          Group ({enableAggregation ? "On" : "Off"})
        </Button>

        <Separator orientation="vertical" className="h-6" />

        {/* Layout selector */}
        {/* ... existing code ... */}
      </div>
    </div>
  </Card>
)}
```

---

## Level 2: Shared Dependency Clustering

### Step 1: Add Detection Logic

Add to `aggregation.ts`:

```typescript
export interface SharedDependencyCluster {
  hubNodeId: string;
  hubLabel: string;
  dependents: string[];
  directionality: "incoming" | "outgoing";
  strength: number; // 0-1, how tightly clustered
}

export function detectSharedDependencies(
  nodes: EnhancedNodeData[],
  links: Link[],
  minClusterSize: number = 5
): SharedDependencyCluster[] {
  const clusters: SharedDependencyCluster[] = [];
  const nodeMap = new Map(nodes.map(n => [n.id, n]));

  // Find incoming shared dependencies (multiple items depend on same thing)
  for (const hub of nodes) {
    const incomingLinks = links.filter(l => l.targetId === hub.id);

    if (incomingLinks.length >= minClusterSize) {
      const dependents = incomingLinks.map(l => l.sourceId);

      // Calculate strength: how many of these dependents ONLY depend on this hub
      const exclusiveDependents = dependents.filter(depId => {
        const depOutgoing = links.filter(l => l.sourceId === depId).length;
        return depOutgoing === 1; // Only this connection
      }).length;

      const strength = exclusiveDependents / dependents.length;

      if (dependents.length >= minClusterSize && strength > 0.2) {
        clusters.push({
          hubNodeId: hub.id,
          hubLabel: hub.label,
          dependents,
          directionality: "incoming",
          strength,
        });
      }
    }
  }

  return clusters;
}

export function createSharedDepAggregateNodeData(
  cluster: SharedDependencyCluster,
  aggregateId: string,
  nodes: EnhancedNodeData[]
): AggregateNodeData {
  const childCount = cluster.dependents.length;

  return {
    id: aggregateId,
    item: {} as any,
    type: "shared-dependency",
    status: "todo" as const,
    label: `Depend on ${cluster.hubLabel} (${childCount})`,
    perspective: [] as any,
    connections: {
      incoming: 0,
      outgoing: childCount,
      total: childCount,
      byType: {} as any,
    },
    depth: 0,
    hasChildren: false,
    aggregateType: "shared-dependency",
    childNodeIds: cluster.dependents,
    childCount,
    isExpanded: false,
    externalIncoming: 1, // To the hub
    externalOutgoing: 0,
    internalConnections: 0,
  };
}
```

### Step 2: Use Shared Dependency Detection

Update FlowGraphViewInner to include shared dependency aggregates:

```typescript
const processedNodes = useMemo(() => {
  if (!enableAggregation) {
    return filteredNodes;
  }

  const result: (EnhancedNodeData | AggregateNodeData)[] = [];
  const aggregatedNodeIds = new Set<string>();

  // 1. Type-based aggregates
  const typeGroups = groupNodesByType(
    filteredNodes,
    filteredLinks,
    AGGREGATION_CONFIG.typeThreshold,
    AGGREGATION_CONFIG.excludeTypes
  );

  const typeAggregates = Array.from(typeGroups.entries())
    .filter(([key]) => key.startsWith("agg-"))
    .map(([key, group]) => {
      group.nodes.forEach(n => aggregatedNodeIds.add(n.id));
      return createAggregateNodeData(group, key);
    });

  // 2. Shared dependency aggregates
  const sharedDepClusters = detectSharedDependencies(
    filteredNodes,
    filteredLinks,
    5 // Min cluster size
  );

  const depAggregates = sharedDepClusters.map((cluster, idx) => {
    // Only add if dependents aren't already in type aggregates
    const uncoveredDependents = cluster.dependents.filter(
      id => !aggregatedNodeIds.has(id)
    );

    if (uncoveredDependents.length >= 5) {
      return createSharedDepAggregateNodeData(
        cluster,
        `agg-shared-dep-${idx}`,
        filteredNodes
      );
    }
    return null;
  }).filter((x): x is AggregateNodeData => x !== null);

  // Get individual nodes not in any aggregate
  const aggregatedIds = new Set<string>();
  [...typeAggregates, ...depAggregates].forEach(agg => {
    agg.childNodeIds.forEach(id => aggregatedIds.add(id));
  });

  const individuals = filteredNodes.filter(n => !aggregatedIds.has(n.id));

  return [
    ...individuals,
    ...typeAggregates,
    ...depAggregates,
  ];
}, [filteredNodes, filteredLinks, enableAggregation, expandedAggregates]);
```

---

## Level 3: Edge Bundling

### Step 1: Create Bundled Edge Component

New file: `/frontend/apps/web/src/components/graph/edges/BundledEdge.tsx`

```typescript
import type { EdgeProps } from "@xyflow/react";
import { getBezierPath, BaseEdge, type Node } from "@xyflow/react";
import { Badge } from "@tracertm/ui/components/Badge";

interface BundledEdgeProps extends EdgeProps {
  data?: {
    bundledCount?: number;
  };
}

export function BundledEdge({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
  markerEnd,
  data,
}: BundledEdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const bundledCount = data?.bundledCount || 1;
  const isBundle = bundledCount > 1;

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: isBundle ? 2 + Math.log(bundledCount) : 2,
          opacity: isBundle ? 0.7 : style?.opacity || 1,
        }}
      />
      {isBundle && (
        <g>
          <circle
            cx={labelX}
            cy={labelY}
            r="12"
            fill="rgba(26, 26, 46, 0.9)"
          />
          <text
            x={labelX}
            y={labelY}
            textAnchor="middle"
            dominantBaseline="middle"
            className="text-[10px] fill-white font-semibold pointer-events-none"
          >
            {bundledCount}
          </text>
        </g>
      )}
    </>
  );
}
```

### Step 2: Bundle Edges Before Display

Add to `aggregation.ts`:

```typescript
export interface BundledEdge {
  id: string;
  source: string;
  target: string;
  bundledCount: number;
  originalEdgeIds: string[];
  isBundle: boolean;
}

export function bundleEdges(
  edges: Link[],
  aggregateNodeIds: Set<string>
): BundledEdge[] {
  const edgeMap = new Map<string, Link[]>();

  // Group edges between same pair of nodes
  for (const edge of edges) {
    const sourceIsAgg = aggregateNodeIds.has(edge.sourceId);
    const targetIsAgg = aggregateNodeIds.has(edge.targetId);

    // Only bundle if at least one is an aggregate
    if (sourceIsAgg || targetIsAgg) {
      const key = `${edge.sourceId}→${edge.targetId}`;
      if (!edgeMap.has(key)) {
        edgeMap.set(key, []);
      }
      edgeMap.get(key)!.push(edge);
    }
  }

  // Create bundled edges
  const result: BundledEdge[] = [];
  let bundleCount = 0;

  for (const [key, edges] of edgeMap) {
    if (edges.length > 1) {
      const firstEdge = edges[0];
      result.push({
        id: `bundle-${bundleCount++}`,
        source: firstEdge.sourceId,
        target: firstEdge.targetId,
        bundledCount: edges.length,
        originalEdgeIds: edges.map(e => e.id),
        isBundle: true,
      });
    } else {
      const firstEdge = edges[0];
      result.push({
        id: firstEdge.id,
        source: firstEdge.sourceId,
        target: firstEdge.targetId,
        bundledCount: 1,
        originalEdgeIds: [firstEdge.id],
        isBundle: false,
      });
    }
  }

  return result;
}
```

### Step 3: Use Bundled Edges in Component

Update edge creation in FlowGraphViewInner:

```typescript
const edgeTypes = {
  bundled: BundledEdge,
} satisfies EdgeTypes;

const initialEdges = useMemo((): Edge[] => {
  const aggregateIds = new Set(
    processedNodes
      .filter((n): n is AggregateNodeData => "aggregateType" in n)
      .map(n => n.id)
  );

  const bundled = bundleEdges(filteredLinks, aggregateIds);

  return bundled.map(edge => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: "bundled",
    data: {
      bundledCount: edge.bundledCount,
    },
    animated: false,
    style: {
      stroke: "#64748b",
      strokeWidth: 2,
    },
  }));
}, [filteredLinks, processedNodes]);
```

---

## Configuration Options

Create a settings hook:

```typescript
// /frontend/apps/web/src/hooks/useGraphAggregation.ts

export interface AggregationSettings {
  enabled: boolean;
  typeAggregation: boolean;
  typeThreshold: number;
  sharedDependencyAggregation: boolean;
  sharedDepThreshold: number;
  excludeFromAggregation: string[];
  edgeBundling: boolean;
  expandByDefault: boolean;
}

const DEFAULT_SETTINGS: AggregationSettings = {
  enabled: true,
  typeAggregation: true,
  typeThreshold: 6,
  sharedDependencyAggregation: false, // Enable after testing
  sharedDepThreshold: 5,
  excludeFromAggregation: ["requirement", "epic", "feature"],
  edgeBundling: false, // Enable after optimization
  expandByDefault: false,
};

export function useGraphAggregation() {
  const [settings, setSettings] = useState<AggregationSettings>(DEFAULT_SETTINGS);

  return { settings, setSettings };
}
```

---

## Testing Checklist

- [ ] Type-based aggregation reduces nodes by 40-60%
- [ ] Aggregate nodes display correctly with child count
- [ ] Expand/collapse toggle works smoothly
- [ ] Edge connections still show correctly to aggregates
- [ ] DOI highlighting works with aggregates
- [ ] Shared dependency detection finds patterns
- [ ] Edge bundling reduces visual clutter
- [ ] Layout algorithms handle mixed aggregate/individual nodes
- [ ] Performance acceptable with 500+ original nodes
- [ ] Search/filter still works with aggregates

---

## Performance Tips

1. **Memoization:**
   ```typescript
   const processedNodes = useMemo(() => {
     // aggregation logic
   }, [filteredNodes, filteredLinks, settings]);
   ```

2. **Lazy Loading:**
   ```typescript
   // Only expand one aggregate at a time
   const handleAggregateExpand = useCallback((nodeId: string) => {
     setExpandedAggregates(new Set([nodeId])); // Clear others
   }, []);
   ```

3. **Debounce Setting Changes:**
   ```typescript
   const debouncedSettings = useDebounce(settings, 300);
   ```

---

## Next Steps

1. Implement Level 1 (Type-Based) first
2. Test with your largest graph (500+ nodes)
3. Measure performance and UX metrics
4. Implement Level 2 if needed
5. Add Level 3 (Edge Bundling) for polish

---

**Implementation Status:** Ready to code
**Estimated Total Time:** 4-6 hours for all levels
