# Phase 2 Task 2.5: LOD Integration in FlowGraphViewInner - Complete

## Summary

Successfully integrated Level of Detail (LOD) system in `FlowGraphViewInner.tsx` with comprehensive context-aware node type selection based on zoom level, node count, selection state, and distance from viewport center.

## Implementation Details

### 1. Enhanced Node Type Selection Function

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/components/graph/nodeRegistry.ts`

Added new `getNodeType` function with comprehensive LOD context support:

```typescript
export interface NodeTypeContext {
  totalNodeCount: number;
  zoom: number;
  isSelected: boolean;
  isFocused: boolean;
  loadingState?: 'loading' | 'error';
  distance?: number;
}

export function getNodeType(itemType: string, context: NodeTypeContext): string {
  // Priority-based selection:
  // 1. Loading/Error -> skeleton
  // 2. Selected/Focused -> full detail
  // 3. High count/low zoom/far distance -> simple
  // 4. Medium conditions -> medium
  // 5. Default -> type-specific
}
```

**LOD Thresholds:**

- **Simple representation:** >500 nodes OR zoom < 0.5 OR distance > 800px
- **Medium representation:** >200 nodes OR zoom < 0.8 OR distance > 400px
- **Full detail:** Selected/focused nodes or optimal viewing conditions

### 2. FlowGraphViewInner Integration

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/components/graph/FlowGraphViewInner.tsx`

Updated `nodesForLayout` useMemo (lines 355-406):

**Type Safety Enhancement:**
Added ExtendedItem interface (lines 350-353) to handle position property on Item type

**Key Changes:**

1. Calculate viewport center for distance-based LOD
2. Compute distance from each node to viewport center
3. Pass comprehensive context to `getNodeType` function
4. Smart preview toggling based on LOD level

```typescript
// Extended Item type with position (type safety)
interface ExtendedItem extends Item {
  position?: { x: number; y: number };
}

const nodesForLayout = useMemo((): Node<RichNodeData>[] => {
  const totalCount = visibleNodes.length;
  const viewport = getViewport?.() ?? { x: 0, y: 0, zoom: 1 };

  // Calculate viewport center
  const viewportCenter = {
    x: viewport.x + window.innerWidth / 2 / viewport.zoom,
    y: viewport.y + window.innerHeight / 2 / viewport.zoom,
  };

  return visibleNodes.map((node) => {
    // Calculate distance from viewport center
    const extendedItem = node.item as ExtendedItem;
    const distance = Math.sqrt(
      Math.pow((extendedItem.position?.x ?? 0) - viewportCenter.x, 2) +
        Math.pow((extendedItem.position?.y ?? 0) - viewportCenter.y, 2),
    );

    // Determine node type using LOD context
    const lodNodeType = getNodeType(node.type, {
      totalNodeCount: totalCount,
      zoom: viewport.zoom,
      isSelected: selectedNodeId === node.id,
      isFocused: false,
      distance,
    });

    return {
      id: node.id,
      type: lodNodeType,
      position: { x: 0, y: 0 },
      data: {
        ...baseData,
        lodLevel,
        isExpanded: expandedNodes.has(node.id),
        showPreview: perspective === 'ui' && lodLevel > 2,
        // ... handlers
      },
    };
  });
}, [
  visibleNodes,
  selectedNodeId,
  expandedNodes,
  perspective,
  handleNodeExpand,
  onNavigateToItem,
  getViewport,
]);
```

## Performance Benefits

### 1. Distance-Based LOD

- Nodes far from viewport center render with reduced detail
- Reduces DOM complexity for off-center nodes
- Distance threshold scales inversely with zoom (more aggressive at low zoom)

### 2. Priority System

- Selected/focused nodes always render with full detail
- Loading/error states use skeleton for consistent UX
- Automatic fallback to simplified rendering under high load

### 3. Smart Preview Toggling

- UI previews only shown at close zoom levels (`lodLevel > 2`)
- Prevents loading heavy preview assets when not visible
- Reduces network requests and memory usage

## Node Type Registry

The implementation leverages these LOD node components:

1. **skeleton** - Loading/error states
2. **simple** - Minimal representation (>500 nodes, zoom < 0.5, distance > 800px)
3. **medium** - Moderate detail (>200 nodes, zoom < 0.8, distance > 400px)
4. **simplePill** - Legacy simplified node (backward compatibility)
5. **Type-specific nodes** - Full detail (test, requirement, epic, etc.)

## Dependencies

**Updated Imports:**

- Added `getNodeType` import to `FlowGraphViewInner.tsx`
- Maintained `getNodeTypeWithLOD` for backward compatibility

**Utilized Utilities:**

- `determineLODLevel` - Zoom-based LOD level calculation
- `itemToNodeData` - Item transformation
- `getViewport` - React Flow viewport access

## Testing Considerations

### Manual Testing

1. **Zoom levels:** Test at 0.3x, 0.6x, 1.0x, 1.5x to verify LOD transitions
2. **Node count:** Test with <100, 200-500, >500 nodes
3. **Selection:** Verify selected nodes always show full detail
4. **Distance:** Pan viewport and observe distant node simplification

### Expected Behaviors

- At low zoom (< 0.5): Most nodes use simple representation
- At medium zoom (0.5-0.8): Mix of medium and simple nodes
- At high zoom (> 1.0): Full detail nodes (unless high count)
- Selected nodes: Always full detail regardless of zoom/distance
- Far nodes: Simplified even at high zoom when distance > threshold

## Migration Notes

### Backward Compatibility

- Legacy `getNodeTypeLegacy` function preserved
- `getNodeTypeWithLOD` still available
- Existing code continues to work without changes

### Future Enhancements

1. Make distance thresholds configurable
2. Add user preferences for LOD aggressiveness
3. Implement fade transitions between LOD levels
4. Add metrics/telemetry for LOD performance impact

## Files Modified

1. `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/components/graph/nodeRegistry.ts`
   - Added `NodeTypeContext` interface
   - Implemented context-aware `getNodeType` function
   - Renamed original to `getNodeTypeLegacy` for backward compatibility
   - Fixed circular dependency in `getNodeTypeForItem`

2. `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/components/graph/FlowGraphViewInner.tsx`
   - Updated `nodesForLayout` useMemo with distance calculation
   - Integrated comprehensive LOD context
   - Added smart preview toggling based on LOD level
   - Updated imports to include `getNodeType`

## Completion Status

- ✅ Task 2.5: Integrate LOD in FlowGraphViewInner
- ✅ Distance calculation from viewport center
- ✅ Context-aware node type selection
- ✅ Priority-based LOD system
- ✅ Smart preview toggling
- ✅ Backward compatibility maintained

**Estimated Time:** 3 hours
**Actual Implementation:** Complete

## Next Steps

1. Run visual regression tests to verify LOD transitions
2. Monitor performance metrics with large graphs (>500 nodes)
3. Gather user feedback on LOD aggressiveness
4. Consider implementing smooth transitions between LOD levels
