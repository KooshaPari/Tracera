# Graph Components Audit

## Summary

Comprehensive audit of 35 graph visualization components with integration status and recommendations.

## Active Components (Primary Views)

### Core Views - ACTIVELY USED

- **UnifiedGraphView** ✅ - Main graph visualization with sidebar, multiple perspectives
- **GraphViewContainer** ✅ - Router integration wrapper for graph views
- **EnhancedGraphView** ✅ - Enhanced rendering with node details
- **FlowGraphView** ✅ - Data flow visualization
- **FlowGraphViewInner** ✅ - Inner flow graph implementation
- **VirtualizedGraphView** ✅ - Virtual scrolling optimization for large graphs

### Supporting Components - ACTIVELY USED

- **GraphNodePill** ✅ - Inline node representation
- **RichNodePill** ✅ - Rich node with metadata
- **NodeDetailPanel** ✅ - Detailed node information display
- **PerspectiveSelector** ✅ - Switch between perspectives
- **GraphSearch** ✅ - Graph search functionality
- **KeyboardNavigation** ✅ - Keyboard controls
- **ThumbnailPreview** ✅ - Node preview thumbnails
- **AggregateGroupNode** ✅ - Grouped node aggregation
- **EditAffordances** ✅ - In-graph editing UI
- **PivotNavigation** ✅ - Cross-perspective navigation
- **LayoutSelector** ✅ - Layout switching
- **DimensionFilters** ✅ - Multi-dimensional filtering

## Advanced Components - NEEDS INTEGRATION

### Cross-Perspective Features

- **CrossPerspectiveSearch** ⚠️ - Search across perspectives
  - Status: Implemented but not wired to main search
  - Location: `/src/components/graph/CrossPerspectiveSearch.tsx`
  - Used in: Tests only
  - Action: Integrate with GraphSearch component

### Equivalence Management

- **EquivalencePanel** ⚠️ - Manage equivalence mappings
  - Status: Implemented
  - Location: `/src/components/graph/EquivalencePanel.tsx`
  - Used in: Storybook only
  - Action: Add UI toggle/modal to display

- **EquivalenceExport** ⚠️ - Export equivalence data
  - Status: Implemented
  - Location: `/src/components/graph/EquivalenceExport.tsx`
  - Used in: Tests only
  - Action: Add to settings/admin panel

- **EquivalenceImport** ⚠️ - Import equivalence data
  - Status: Implemented
  - Location: `/src/components/graph/EquivalenceImport.tsx`
  - Used in: Tests only
  - Action: Add to settings/admin panel

### UI/Component Analysis

- **UIComponentTree** ⚠️ - Component hierarchy visualization
  - Status: Implemented
  - Location: `/src/components/graph/UIComponentTree.tsx`
  - Used in: Storybook only
  - Action: Integrate into UI perspective view

- **PageInteractionFlow** ⚠️ - Page interaction diagrams
  - Status: Implemented
  - Location: `/src/components/graph/PageInteractionFlow.tsx`
  - Used in: Tests only
  - Action: Integrate into UI perspective view

## Exploratory Components - ASSESS FOR REMOVAL

### Design System Tools

- **DesignTokenBrowser** ⚠️ - Browse design tokens
  - Status: Implemented with .example variant
  - Location: `/src/components/graph/DesignTokenBrowser.tsx`
  - Used in: Storybook, examples
  - Assessment: Valuable for design system work but not critical
  - Recommendation: Keep as optional feature, add toggle in UI view

- **ComponentUsageMatrix** ⚠️ - Component usage analysis
  - Status: Implemented
  - Location: `/src/components/graph/ComponentUsageMatrix.tsx`
  - Used in: Storybook only
  - Assessment: Useful for component analytics
  - Recommendation: Integrate into UI perspective analytics panel

- **ComponentLibraryExplorer** ⚠️ - Browse component library
  - Status: Implemented
  - Location: `/src/components/graph/ComponentLibraryExplorer.tsx`
  - Used in: Storybook only
  - Assessment: UI/UX analysis tool
  - Recommendation: Integrate into UI perspective sidebar

### Code Tracing

- **UICodeTracePanel** ⚠️ - Trace UI code relationships
  - Status: Implemented with .integration variant
  - Location: `/src/components/graph/UICodeTracePanel.tsx`
  - Used in: Tests only
  - Assessment: Maps UI components to code
  - Recommendation: Integrate into UI perspective details panel

- **UICodeTracePanel.integration** ⚠️ - Integration version
  - Status: Separate file
  - Assessment: Duplicate/variant
  - Recommendation: Consolidate into main UICodeTracePanel

### Feature Analysis

- **JourneyExplorer** ⚠️ - Journey/flow visualization
  - Status: Implemented
  - Location: `/src/components/graph/JourneyExplorer.tsx`
  - Used in: Tests only
  - Assessment: Valuable for product perspective
  - Recommendation: Integrate into product perspective view

- **PageDecompositionView** ⚠️ - Page hierarchy decomposition
  - Status: Implemented
  - Location: `/src/components/graph/PageDecompositionView.tsx`
  - Used in: Storybook only
  - Assessment: UI decomposition analysis
  - Recommendation: Integrate into UI perspective as "Structure" view

### Design Integration

- **FigmaSyncPanel** ⚠️ - Figma design synchronization
  - Status: Implemented with Props interface
  - Location: `/src/components/graph/FigmaSyncPanel.tsx`
  - Used in: Storybook only
  - Assessment: Design system integration
  - Recommendation: Defer to v2, keep as optional feature

### Node Components (nodes/ subdirectory)

- **ExpandableNode** ✅ - Expandable node functionality
- **NodeExpandPopup** ✅ - Expansion popup
- **QAEnhancedNode** ✅ - QA-enhanced node (docs/code)

## Hooks (Advanced Features)

### Performance Optimization

- **useVirtualization** ✅ - Virtual scrolling
- **useGraphWorker** ✅ - Web worker layout computation
- **useCrossPerspectiveSearch** ⚠️ - Cross-perspective search logic
  - Status: Implemented
  - Used in: Tests only
  - Action: Wire to CrossPerspectiveSearch component

## Search Features

### Main Search

- **GraphSearch** ✅ - Primary search component

### Advanced Search

- **SearchAdvancedFeatures** ⚠️ - Advanced search UI
  - Status: Implemented
  - Used in: Storybook only
  - Action: Integrate with GraphSearch advanced mode

## Recommendation Priority

### HIGH - Integrate Soon (Sprint 15-16)

1. CrossPerspectiveSearch - Wire to main search UI
2. EquivalencePanel/Export/Import - Add to settings/admin
3. UIComponentTree/PageInteractionFlow - Integrate into UI perspective
4. JourneyExplorer - Integrate into product perspective
5. SearchAdvancedFeatures - Add to search component

### MEDIUM - Integrate Later (Sprint 17+)

1. ComponentLibraryExplorer - Add to UI perspective sidebar
2. ComponentUsageMatrix - Add analytics panel
3. PageDecompositionView - Add structure view
4. DesignTokenBrowser - Add as toggle in UI view
5. UICodeTracePanel consolidation - Merge variants

### LOW - Optional/Defer

1. FigmaSyncPanel - Design system v2 feature
2. DesignTokenBrowser - Enhancement, not critical

## Integration Checklist

### For Each Unused Component

- [ ] Define where it should appear in UI (route/view/panel)
- [ ] Create navigation/toggle to access it
- [ ] Wire state management (if needed)
- [ ] Add E2E tests for workflows
- [ ] Update navigation documentation
- [ ] Add feature flags if experimental

### Documentation Requirements

- [ ] Update COMPONENT_AUDIT.md with status
- [ ] Add JSDoc comments explaining purpose
- [ ] Add props validation and error boundaries
- [ ] Create integration examples in Storybook

## Files to Consolidate/Remove

### Duplicates

- `UICodeTracePanel.integration.tsx` - Merge with main file
- `DesignTokenBrowser.example.tsx` - Move to storybook stories

### Cleanup

After integration decisions, create `/DEAD_CODE.md` documenting:

- Components removed and why
- Migration paths for old code
- Timeline of deprecation
