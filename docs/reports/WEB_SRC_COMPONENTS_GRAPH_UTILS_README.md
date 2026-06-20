# Graph Visualization Utilities

Enhanced hierarchy and grouping algorithms for graph visualization with drill-down navigation support.

## Overview

This module provides comprehensive utilities for:

- **Grouping algorithms**: Multiple strategies for organizing items in the graph
- **Hierarchy utilities**: Parent-child relationships, depth calculation, and breadcrumb paths
- **Drill-down navigation**: Progressive disclosure from Project → Repository → Module → File → Function

## Modules

### grouping.ts

Grouping strategies for organizing items based on their relationships.

#### Available Strategies

1. **Link Targets Grouping** (`groupByLinkTargets`)
   - Groups items that share common targets
   - Useful for finding items with similar outgoing dependencies
   - Includes cohesion metrics based on target overlap

   ```typescript
   const groups = groupByLinkTargets(items, links, minGroupSize: 2);
   ```

2. **Dependencies Grouping** (`groupByDependencies`)
   - Groups items with identical dependencies
   - Useful for finding items that depend on the same things
   - Helps identify reusable patterns

   ```typescript
   const groups = groupByDependencies(items, links, minGroupSize: 2);
   ```

3. **Paths Grouping** (`groupByPaths`)
   - Groups items that form connected paths/journeys
   - Uses connected component detection (DFS)
   - Perfect for trace path identification
   - Returns groups with perfect cohesion (1.0) for fully connected components

   ```typescript
   const groups = groupByPaths(items, links, minGroupSize: 2);
   ```

4. **Semantic Grouping** (`groupBySemantic`)
   - Groups items by semantic similarity (type-based primarily)
   - Includes title similarity metrics
   - Good baseline for initial categorization

   ```typescript
   const groups = groupBySemantic(items, minGroupSize: 2);
   ```

#### Metrics

Each group includes optional metrics:

- **cohesion** (0-1): How tightly grouped (internal connections)
- **separation** (0-1): How distinct from other groups
- **commonality** (0-1): Shared characteristics

#### Advanced Functions

- `intersectGroupResults()`: Find items matching multiple grouping criteria
- `calculateGroupCohesion()`: Measure internal connectivity
- `calculateGroupSeparation()`: Measure independence between groups

### hierarchy.ts

Hierarchy utilities for managing parent-child relationships.

#### Core Functions

**Building Hierarchies**

```typescript
const hierarchy = buildHierarchy(items, links);
// Creates a Map<string, HierarchyNode> from parent_of links
```

**Navigation**

```typescript
getParent(itemId, hierarchy); // Immediate parent
getChildren(itemId, hierarchy); // All direct children
getAncestorChain(itemId, hierarchy); // Path to root
getDescendantNodes(itemId, hierarchy); // All descendants
getSiblings(itemId, hierarchy); // Same parent items
```

**Relationships**

```typescript
isAncestor(potentialAncestorId, itemId, hierarchy);
isDescendant(potentialDescendantId, itemId, hierarchy);
findCommonAncestor(itemId1, itemId2, hierarchy);
```

**Analysis**

```typescript
getItemsAtDepth(depth, hierarchy); // All items at depth N
getHierarchyStats(hierarchy); // Overall statistics
```

**Display**

```typescript
getBreadcrumbPath(itemId, hierarchy); // For breadcrumb UI
exportHierarchyStructure(hierarchy); // For export/analysis
```

#### HierarchyNode Properties

Each node includes:

- `id`, `item`: Item identification
- `parentId`, `childrenIds`: Relationships
- `depth`: Distance from root
- `ancestors`, `descendants`: All related items
- `hierarchyPath`: Full path from root
- `isRoot`, `isLeaf`, `isOrphan`: Classification

### drilldown.ts

Progressive disclosure navigation for exploring hierarchies.

#### Drill-Down Levels

```typescript
type DrillDownLevel = 'project' | 'repository' | 'module' | 'file' | 'function';
```

Levels are hierarchical: Project → Repository → Module → File → Function

#### Core Functions

**Navigation**

```typescript
getNextLevel(currentLevel); // Next level down
getPreviousLevel(currentLevel); // Previous level up
navigateUp(itemId, hierarchy); // Go to parent
navigateToChild(itemId, childIndex, hierarchy);
```

**Context Management**

```typescript
createDrillDownContext({ itemId, items, hierarchyMap, expandedGroups? })
// Returns current drill-down state including:
// - currentLevel, itemId, itemTitle
// - breadcrumbs, parentInfo
// - visibleItems, childrenAvailable
```

**Grouping for UI**

```typescript
createDrillDownNodeGroups({ itemId, items, hierarchyMap, maxItemsPerGroup? })
// Creates expandable groups for current level
// Handles splitting large groups automatically
```

**Expansion Management**

```typescript
toggleDrillDownGroup(groupId, expandedGroups);
expandDrillDownGroup(groupId, expandedGroups);
collapseDrillDownGroup(groupId, expandedGroups);
```

**Breadcrumbs**

```typescript
createBreadcrumbs(itemId, hierarchyMap);
getDrillDownPath(itemId, hierarchyMap);
```

**Lazy Loading**

```typescript
calculateLazyLoadingRequirements(rootItemId, maxDepth, hierarchy);
getDrillDownStats(itemId, hierarchy);
```

## Data Structures

### GroupResult

```typescript
interface GroupResult {
  groupId: string;
  strategy: GroupingStrategy;
  label: string;
  itemIds: string[];
  itemCount: number;
  metrics?: {
    cohesion?: number; // 0-1
    separation?: number; // 0-1
    commonality?: number; // 0-1
  };
  metadata?: Record<string, unknown>;
}
```

### HierarchyNode

```typescript
interface HierarchyNode {
  id: string;
  item: Item;
  parentId?: string;
  childrenIds: string[];
  depth: number;
  ancestors: string[];
  descendants: string[];
  hierarchyPath: string[];
  isRoot: boolean;
  isLeaf: boolean;
  isOrphan: boolean;
}
```

### DrillDownContext

```typescript
interface DrillDownContext {
  currentLevel: DrillDownLevel;
  itemId: string;
  itemTitle: string;
  parentId?: string;
  parentTitle?: string;
  breadcrumbs: DrillDownBreadcrumb[];
  visibleItems: string[];
  childrenAvailable: boolean;
}
```

## Usage Patterns

### Pattern 1: Multi-Strategy Grouping

```typescript
const groupingResults = [
  groupByLinkTargets(items, links),
  groupByDependencies(items, links),
  groupByPaths(items, links),
];

const commonGroups = intersectGroupResults(groupingResults);
// Find items that match multiple grouping criteria
```

### Pattern 2: Drill-Down Navigation

```typescript
const hierarchy = buildHierarchy(items, links);
const context = createDrillDownContext({ itemId, items, hierarchyMap: hierarchy });

if (context.childrenAvailable) {
  const groups = createDrillDownNodeGroups({ itemId, items, hierarchyMap: hierarchy });
  // Render expandable groups for next level
}

// Navigate
if (userClicksUp) {
  const parentId = navigateUp(itemId, hierarchy);
}
```

### Pattern 3: Breadcrumb Trail

```typescript
const breadcrumbs = createBreadcrumbs(itemId, hierarchy);
// Render: [root] > [parent] > [current]

const path = getDrillDownPath(itemId, hierarchy);
// For analytics: track navigation path
```

### Pattern 4: Hierarchy Analysis

```typescript
const stats = getHierarchyStats(hierarchy);
console.log(`Tree depth: ${stats.maxDepth}`);
console.log(`Leaves: ${stats.leafCount}`);
console.log(`Distribution by depth:`, stats.depthDistribution);

const atDepth2 = getItemsAtDepth(2, hierarchy);
// Get all items at specific level for visualization
```

## Performance Considerations

- **Grouping**: O(n + m) where n = items, m = links
- **Hierarchy Building**: O(n + m) with BFS traversal
- **Drill-Down Navigation**: O(h) where h = hierarchy depth (typically small)
- **Memory**: Stores full hierarchy maps - suitable for typical graphs (<10k nodes)

## Testing

Comprehensive test suite included:

- `grouping.test.ts`: 19 tests covering all grouping strategies
- `hierarchy.test.ts`: 31 tests for hierarchy operations
- `drilldown.test.ts`: 34 tests for navigation and contexts

Run tests:

```bash
bun run test -- "src/__tests__/components/graph/utils"
```

## Integration

These utilities are designed to work with:

- XFlow visualization components
- React state management (Zustand/Redux)
- Existing aggregation system in `src/utils/aggregation.ts`

Import all utilities:

```typescript
import * as GraphUtils from './components/graph/utils';
```

Or import specific modules:

```typescript
import { groupByPaths, groupBySemantic } from './components/graph/utils/grouping';
import { buildHierarchy, getChildren } from './components/graph/utils/hierarchy';
import { createDrillDownContext } from './components/graph/utils/drilldown';
```

## Future Enhancements

- Semantic similarity using embeddings (vector similarity)
- Weighted grouping based on link importance
- Advanced community detection algorithms
- Graph clustering optimizations
- Caching strategies for large hierarchies
- Incremental hierarchy updates
