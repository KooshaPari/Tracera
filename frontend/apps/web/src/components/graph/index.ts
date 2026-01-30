// Graph Components - Enhanced traceability visualization
// Provides multiple perspectives: product, business, technical, UI, security, performance

// Main unified view with sidebar navigation
export {
	UnifiedGraphView,
	type DisplayMode,
	type EquivalenceMode,
	type DerivedJourney,
} from "./UnifiedGraphView";
export { GraphViewContainer, type GraphViewMode } from "./GraphViewContainer";

// Individual graph views
export { EnhancedGraphView } from "./EnhancedGraphView";
export { FlowGraphView } from "./FlowGraphView";
export { FlowGraphViewInner } from "./FlowGraphViewInner";
export { VirtualizedGraphView } from "./VirtualizedGraphView";

// Rich node components
export { GraphNodePill } from "./GraphNodePill";
export { RichNodePill, type RichNodeData } from "./RichNodePill";
export {
	QAEnhancedNode,
	type QAEnhancedNodeData,
} from "./nodes/QAEnhancedNode";
export { NodeExpandPopup } from "./nodes/NodeExpandPopup";

// UI-specific views
export { UIComponentTree } from "./UIComponentTree";
export { PageInteractionFlow } from "./PageInteractionFlow";

// Multi-dimensional traceability components
export {
	DimensionFilters,
	type DimensionFilter,
	applyDimensionFilters,
	getDimensionColor,
	getDimensionSize,
} from "./DimensionFilters";
export { EquivalencePanel } from "./EquivalencePanel";
export {
	PivotNavigation,
	type PivotTarget,
	buildPivotTargets,
} from "./PivotNavigation";
export { PageDecompositionView } from "./PageDecompositionView";
export { ComponentLibraryExplorer } from "./ComponentLibraryExplorer";
export {
	ComponentUsageMatrix,
	type ComponentUsageMatrixProps,
} from "./ComponentUsageMatrix";
export {
	DesignTokenBrowser,
	type DesignTokenBrowserProps,
} from "./DesignTokenBrowser";
export { FigmaSyncPanel, type FigmaSyncPanelProps } from "./FigmaSyncPanel";

// Supporting components
export { NodeDetailPanel } from "./NodeDetailPanel";
export { PerspectiveSelector } from "./PerspectiveSelector";
export { JourneyExplorer } from "./JourneyExplorer";

// Phase 2: Node Expansion
export { KeyboardNavigation } from "./KeyboardNavigation";
export {
	ExpandableNode,
	type ExpandableNodeData,
} from "./nodes/ExpandableNode";

// Phase 3: Screenshots
export { ThumbnailPreview } from "./ThumbnailPreview";

// Phase 4: Aggregation
export { AggregateGroupNode } from "./AggregateGroupNode";

// Phase 5: Polish
export { GraphSearch } from "./GraphSearch";
export { CrossPerspectiveSearch } from "./CrossPerspectiveSearch";
export { EditAffordances } from "./EditAffordances";

// Layouts
export {
	useDAGLayout,
	type LayoutType,
	LAYOUT_CONFIGS,
} from "./layouts/useDAGLayout";
export { LayoutSelector, getRecommendedLayout } from "./layouts/LayoutSelector";

// Virtual rendering and performance hooks
export {
	useVirtualization,
	useIntersectionVisibility,
	useProgressiveLoading,
	type ViewportBounds,
	type NodePosition,
	type LODLevel,
	type VirtualizationMetrics,
} from "./hooks/useVirtualization";
export {
	useGraphWorker,
	useNodeClustering,
	type LayoutMessage,
	type LayoutNode,
	type LayoutEdge,
	type LayoutOptions,
	type LayoutResult,
} from "./hooks/useGraphWorker";

// Cross-perspective search hook
export {
	useCrossPerspectiveSearch,
	type CrossPerspectiveSearchResult,
	type EquivalenceInfo,
	type GroupedSearchResults,
	type SearchFilters,
} from "./hooks/useCrossPerspectiveSearch";

// Types and utilities
export * from "./types";
