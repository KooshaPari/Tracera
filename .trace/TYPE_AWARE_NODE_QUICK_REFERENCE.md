# Type-Aware Node System - Quick Reference

**Last Updated**: 2026-01-30

---

## 🚀 Quick Start

### Creating Type-Specific Items

```typescript
import { CreateItemDialog } from "@/components/forms";

// In your component
<CreateItemDialog
  projectId={projectId}
  initialType="requirement"  // or "test", "epic", etc.
  onSuccess={(item) => console.log("Created:", item)}
  onCancel={() => console.log("Cancelled")}
/>
```

### Rendering Type-Aware Graphs

```typescript
import { nodeTypes, getNodeTypeForItem } from "@/components/graph/nodeRegistry";
import { itemToNodeData } from "@/components/graph/utils/nodeDataTransformers";
import { ReactFlow } from "@xyflow/react";

function MyGraph({ items, links }) {
  const nodes = items.map(item => {
    const connections = { incoming: 0, outgoing: 0, total: 0 };
    const nodeData = itemToNodeData(item, connections);
    const nodeType = getNodeTypeForItem(item.type, nodeData);

    return {
      id: item.id,
      type: nodeType,
      data: nodeData,
      position: { x: 0, y: 0 },
    };
  });

  return <ReactFlow nodes={nodes} nodeTypes={nodeTypes} />;
}
```

---

## 📋 Import Cheat Sheet

```typescript
// Type guards and typed items
import {
  isRequirementItem,
  isTestItem,
  isEpicItem,
  isUserStoryItem,
  isTaskItem,
  isDefectItem,
  hasSpec,
  type TypedItem,
  type RequirementItem,
  type TestItem,
  type EpicItem,
} from "@tracertm/types";

// Type configuration
import {
  getItemTypeConfig,
  getItemTypesForView,
  isTypeValidForView,
  getItemTypeIcon,
  getItemTypeColor,
  getItemTypeLabel,
  ITEM_TYPE_CONFIGS,
} from "@/lib/itemTypeConfig";

// Node components and registry
import { nodeTypes, getNodeTypeForItem } from "@/components/graph/nodeRegistry";
import { itemToNodeData } from "@/components/graph/utils/nodeDataTransformers";
import { TestNode, RequirementNode, EpicNode } from "@/components/graph/nodes";

// Form components
import { CreateItemDialog } from "@/components/forms";
```

---

## 🎯 Common Use Cases

### 1. Filter Items by Type

```typescript
const items: Item[] = [...]; // your items

// Get all test items
const tests = items.filter(isTestItem);

// Get all requirements
const requirements = items.filter(isRequirementItem);

// Get all epics
const epics = items.filter(isEpicItem);
```

### 2. Type-Safe Field Access

```typescript
function displayItem(item: Item) {
  if (isTestItem(item)) {
    // TypeScript knows item is TestItem
    return `Test: ${item.title} - ${item.automationStatus}`;
  }

  if (isRequirementItem(item)) {
    // TypeScript knows item is RequirementItem
    return `Req: ${item.title} - ADR: ${item.adrId}`;
  }

  return `Item: ${item.title}`;
}
```

### 3. Get Type Metadata

```typescript
const config = getItemTypeConfig("requirement");

// Use the config
const color = config.color;           // "#9333ea"
const icon = config.icon;             // "requirement"
const label = config.label;           // "Requirement"
const requiresSpec = config.requiresSpec; // true

// Quick helpers
const quickColor = getItemTypeColor("test");     // "#22c55e"
const quickIcon = getItemTypeIcon("epic");        // "epic"
const quickLabel = getItemTypeLabel("user_story"); // "User Story"
```

### 4. Validate Type for View

```typescript
// Get all valid types for a view
const featureTypes = getItemTypesForView("FEATURE");
// Returns: requirement, epic, user_story, feature, task

// Check if type is valid for view
const isValid = isTypeValidForView("test", "FEATURE"); // false
const isValid2 = isTypeValidForView("requirement", "FEATURE"); // true
```

### 5. Transform API Data to Node Data

```typescript
// Single item
const item: Item = { /* from API */ };
const connections = { incoming: 2, outgoing: 3, total: 5 };
const nodeData = itemToNodeData(item, connections);

// Multiple items
const items: Item[] = [...];
const connectionMap = new Map([
  ["item-1", { incoming: 2, outgoing: 3, total: 5 }],
  ["item-2", { incoming: 1, outgoing: 2, total: 3 }],
]);
const nodesData = itemsToNodeData(items, connectionMap);
```

---

## 🎨 Available Item Types

### Requirements & Planning
| Type         | Color   | Icon        | Requires Spec |
|--------------|---------|-------------|---------------|
| requirement  | Purple  | requirement | ✅            |
| epic         | Violet  | epic        |               |
| user_story   | Violet  | user_story  |               |
| story        | Violet  | story       |               |
| task         | Slate   | task        |               |

### Testing
| Type        | Color | Icon       |
|-------------|-------|------------|
| test        | Green | test       |
| test_case   | Green | test_case  |
| test_suite  | Green | test_suite |

### Defects
| Type   | Color | Icon   |
|--------|-------|--------|
| bug    | Red   | bug    |
| defect | Red   | defect |

### Features
| Type    | Color  | Icon    |
|---------|--------|---------|
| feature | Purple | feature |

### Technical
| Type            | Color  | Icon            |
|-----------------|--------|-----------------|
| api             | Amber  | api             |
| database        | Violet | database        |
| code            | Blue   | code            |
| architecture    | Indigo | architecture    |
| infrastructure  | Cyan   | infrastructure  |
| configuration   | Slate  | configuration   |

### UI/UX
| Type         | Color | Icon         |
|--------------|-------|--------------|
| wireframe    | Pink  | wireframe    |
| ui_component | Pink  | ui_component |
| page         | Pink  | page         |
| component    | Pink  | component    |

### Security & Performance
| Type         | Color   | Icon         |
|--------------|---------|--------------|
| security     | Red     | security     |
| vulnerability| Red     | vulnerability|
| performance  | Emerald | performance  |
| monitoring   | Teal    | monitoring   |

---

## 🧩 Type-Specific Node Features

### TestNode (Green #22c55e)
```typescript
interface TestNodeData {
  testType?: string;              // "unit", "integration", "e2e"
  framework?: string;             // "jest", "playwright", "vitest"
  flakinessScore?: number;        // 0-100, visual warning if > 50
  coveragePercent?: number;       // 0-100, shown as meter
  safetyLevel?: "safe" | "quarantined" | "disabled";
  lastRunStatus?: "passed" | "failed" | "skipped" | "error";
}
```
**Visual Features**:
- 🟢 Green accent bar
- ⚠️ Quarantine warning banner if quarantined
- 📊 Flakiness score with color warning
- 🛡️ Safety level badge
- ✅ Last run status indicator

### RequirementNode (Purple #9333ea)
```typescript
interface RequirementNodeData {
  earsPatternType?: "ubiquitous" | "event_driven" | "state_driven" | "optional" | "unwanted";
  riskLevel?: "low" | "medium" | "high" | "critical";
  wsjfScore?: number;             // Weighted Shortest Job First
  verifiabilityScore?: number;    // 0-100, testability
  verificationStatus?: "not_verified" | "partially_verified" | "verified";
}
```
**Visual Features**:
- 🟣 Purple accent bar
- 📝 EARS pattern badge
- ⚠️ Risk level indicator
- 📈 WSJF score display
- 🔍 Verifiability progress gauge
- ✓ Verification status badge

### EpicNode (Deep Purple #7c3aed)
```typescript
interface EpicNodeData {
  businessValue?: "low" | "medium" | "high" | "critical";
  timelineProgress?: number;      // 0-100
  storyCount?: number;
  completedStoryCount?: number;
}
```
**Visual Features**:
- 🟣 Deep purple accent bar
- 💼 Business value badge
- 📅 Timeline progress bar
- 📊 Story completion tracker (completed/total)
- 🎉 Completion celebration badge (when 100%)

---

## 🔧 Customizing Nodes

### Adding a New Item Type

```typescript
// 1. Define the type in @tracertm/types
export interface MyCustomItem extends Item {
  type: "my_custom_type";
  customField?: string;
  customMetric?: number;
}

// 2. Add to discriminated union
export type TypedItem = RequirementItem | TestItem | MyCustomItem | ...;

// 3. Create type guard
export function isMyCustomItem(item: Item): item is MyCustomItem {
  return item.type === "my_custom_type";
}

// 4. Add to configuration registry (itemTypeConfig.ts)
{
  type: "my_custom_type",
  label: "My Custom Type",
  description: "Description of custom type",
  icon: "custom",
  color: "#ff6b6b",
  allowedViews: ["FEATURE", "CUSTOM"],
  requiresSpec: false,
  defaultPriority: "medium",
}

// 5. Create specialized node (optional)
// /components/graph/nodes/MyCustomNode.tsx
export interface MyCustomNodeData {
  id: string;
  item: MyCustomItem;
  label: string;
  customField?: string;
  customMetric?: number;
  connections: { incoming: number; outgoing: number; total: number };
}

export function MyCustomNode({ data }: NodeProps<MyCustomNodeData>) {
  return (
    <Card>
      <div className="absolute top-0 left-0 right-0 h-1" style={{ backgroundColor: "#ff6b6b" }} />
      {/* Your custom node UI */}
    </Card>
  );
}

// 6. Register in nodeRegistry.ts
export const nodeTypes: NodeTypes = {
  my_custom_type: MyCustomNode,
  // ... other types
};

// 7. Add transformer (nodeDataTransformers.ts)
function transformMyCustomItem(item: MyCustomItem): Partial<MyCustomNodeData> {
  return {
    customField: item.customField,
    customMetric: item.customMetric,
  };
}
```

### Customizing Node Appearance

```typescript
// Change colors
const CUSTOM_COLORS = {
  my_type: "#custom-color",
};

// Change sizes
const NODE_WIDTHS = {
  default: 260,
  my_type: 300,  // Wider node
};

// Add custom badges
{data.myCustomField && (
  <Badge variant="outline" className="text-[10px]">
    {data.myCustomField}
  </Badge>
)}
```

---

## 🐛 Troubleshooting

### Node Shows as Default Instead of Type-Specific

**Problem**: Your item shows as RichNodePill instead of TestNode/RequirementNode/EpicNode

**Solution**:
```typescript
// Check node type selection
const nodeType = getNodeTypeForItem(item.type, nodeData);
console.log("Selected type:", nodeType);
console.log("Item type:", item.type);
console.log("Available types:", Object.keys(nodeTypes));

// Verify node is registered
import { nodeTypes } from "@/components/graph/nodeRegistry";
console.log("Registered types:", Object.keys(nodeTypes));
```

### TypeScript Error: Property Doesn't Exist

**Problem**: `Property 'automationStatus' does not exist on type 'Item'`

**Solution**: Use type guards
```typescript
// ❌ Wrong
console.log(item.automationStatus); // Error!

// ✅ Correct
if (isTestItem(item)) {
  console.log(item.automationStatus); // OK
}
```

### Missing Node Metrics

**Problem**: Node doesn't show expected fields (flakiness, coverage, etc.)

**Solution**: Check data transformation
```typescript
// Debug the transformation
const nodeData = itemToNodeData(item, connections);
console.log("Transformed data:", nodeData);
console.log("Item metadata:", item.metadata);

// Verify item has the right structure
console.log("Item type:", item.type);
console.log("Is test item?", isTestItem(item));
```

### CreateItemDialog Not Working

**Problem**: Dialog doesn't submit or shows errors

**Solution**:
```typescript
// Verify required props
<CreateItemDialog
  projectId={projectId}        // Required
  initialType="test"            // Optional, defaults to "requirement"
  onSuccess={(item) => {        // Required
    console.log("Created:", item);
  }}
  onCancel={() => {             // Optional
    console.log("Cancelled");
  }}
/>

// Check network requests
// Open DevTools > Network tab
// Look for POST to /api/v1/items
```

---

## 📊 Performance Tips

### 1. Batch Transform Items
```typescript
// ✅ Good: Transform in batch
const connectionMap = calculateConnectionMap(items, links);
const nodesData = itemsToNodeData(items, connectionMap);

// ❌ Bad: Transform one by one
items.forEach(item => {
  const connections = calculateConnections(item, links); // Slow!
  const nodeData = itemToNodeData(item, connections);
});
```

### 2. Memoize Expensive Computations
```typescript
import { useMemo } from "react";

const nodes = useMemo(() => {
  return items.map(item => {
    const nodeData = itemToNodeData(item, connectionMap.get(item.id));
    return { id: item.id, data: nodeData, ... };
  });
}, [items, connectionMap]);
```

### 3. Use Connection Map
```typescript
// Pre-compute connections
const connectionMap = new Map(
  items.map(item => [
    item.id,
    {
      incoming: links.filter(l => l.targetId === item.id).length,
      outgoing: links.filter(l => l.sourceId === item.id).length,
      total: links.filter(l => l.sourceId === item.id || l.targetId === item.id).length,
    }
  ])
);
```

---

## 🎓 Best Practices

### ✅ DO

- Use type guards before accessing specialized fields
- Leverage `getItemTypeConfig()` for consistent styling
- Transform data in batches for performance
- Provide default values for optional fields
- Use memoization for expensive operations
- Test with various data states (missing fields, edge cases)

### ❌ DON'T

- Access type-specific fields without type guards
- Hardcode colors/icons (use configuration)
- Transform items individually in loops
- Assume all fields are present
- Re-render on every state change
- Forget to handle unknown/generic types

---

## 📚 Additional Resources

- **Type Definitions**: `/frontend/packages/types/src/index.ts`
- **Configuration Registry**: `/frontend/apps/web/src/lib/itemTypeConfig.ts`
- **Node Components**: `/frontend/apps/web/src/components/graph/nodes/`
- **Data Transformers**: `/frontend/apps/web/src/components/graph/utils/nodeDataTransformers.ts`
- **Complete Implementation**: `.trace/TYPE_AWARE_NODE_SYSTEM_COMPLETE.md`
- **Phase 1 Details**: `.trace/TYPE_AWARE_NODE_PHASE_1_COMPLETE.md`
- **Phase 5 Details**: `PHASE_5_TYPE_AWARE_NODES_IMPLEMENTATION.md`

---

## 🆘 Getting Help

### Check Documentation
1. Read this Quick Reference
2. Review implementation complete docs
3. Check existing node components for patterns

### Debug Your Code
```typescript
// Enable debug logging
console.log("Item:", item);
console.log("Type guard:", isTestItem(item));
console.log("Config:", getItemTypeConfig(item.type));
console.log("Node data:", itemToNodeData(item));
console.log("Node type:", getNodeTypeForItem(item.type, nodeData));
```

### Common Solutions
- Type errors → Use type guards
- Missing fields → Check data transformation
- Wrong node type → Verify node registry
- Performance issues → Batch operations, memoize

---

**Version**: 1.0.0
**Last Updated**: 2026-01-30
**Status**: Production Ready (pending lodash-es fix)
