// Graph Components - Enhanced traceability visualization
// Provides multiple perspectives: product, business, technical, UI, security, performance

// Main unified view with sidebar navigation
export { UnifiedGraphView } from "./UnifiedGraphView";
export { GraphViewContainer, type GraphViewMode } from "./GraphViewContainer";

// Individual graph views
export { EnhancedGraphView } from "./EnhancedGraphView";
export { FlowGraphView } from "./FlowGraphView";
export { FlowGraphViewInner } from "./FlowGraphViewInner";

// Rich node components
export { GraphNodePill } from "./GraphNodePill";
export { RichNodePill, type RichNodeData } from "./RichNodePill";

// UI-specific views
export { UIComponentTree } from "./UIComponentTree";
export { PageInteractionFlow } from "./PageInteractionFlow";

// Supporting components
export { NodeDetailPanel } from "./NodeDetailPanel";
export { PerspectiveSelector } from "./PerspectiveSelector";

// Phase 2: Node Expansion
export { KeyboardNavigation } from "./KeyboardNavigation";
export { ExpandableNode, type ExpandableNodeData } from "./nodes/ExpandableNode";

// Phase 3: Screenshots
export { ThumbnailPreview } from "./ThumbnailPreview";

// Phase 4: Aggregation
export { AggregateGroupNode } from "./AggregateGroupNode";

// Phase 5: Polish
export { GraphSearch } from "./GraphSearch";
export { EditAffordances } from "./EditAffordances";

// Layouts
export { useDAGLayout, type LayoutType, LAYOUT_CONFIGS } from "./layouts/useDAGLayout";
export { LayoutSelector, getRecommendedLayout } from "./layouts/LayoutSelector";

// Types and utilities
export * from "./types";
