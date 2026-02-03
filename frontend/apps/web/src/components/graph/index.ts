// Graph Components - Enhanced traceability visualization
// Provides multiple perspectives: product, business, technical, UI, security, performance

// Phase 4: Aggregation
export { AggregateGroupNode } from "./AggregateGroupNode";
export { ClusterNode, type ClusterNodeData } from "./ClusterNode";
export { ClusteredGraphView } from "./ClusteredGraphView";
export { ComponentLibraryExplorer } from "./ComponentLibraryExplorer";
export {
	ComponentUsageMatrix,
	type ComponentUsageMatrixProps,
} from "./ComponentUsageMatrix";
export { CrossPerspectiveSearch } from "./CrossPerspectiveSearch";
export {
	DesignTokenBrowser,
	type DesignTokenBrowserProps,
} from "./DesignTokenBrowser";
// Multi-dimensional traceability components
export type { DimensionFilter } from "@tracertm/types";
export {
	applyDimensionFilters,
	DimensionFilters,
	getDimensionColor,
	getDimensionSize,
} from "./DimensionFilters";
export { EditAffordances } from "./EditAffordances";
// Individual graph views
export { EnhancedGraphView } from "./EnhancedGraphView";
export {
	EquivalenceExport,
	type EquivalenceExportProps,
} from "./EquivalenceExport";
export {
	EquivalenceImport,
	type EquivalenceImportProps,
} from "./EquivalenceImport";
export { EquivalencePanel } from "./EquivalencePanel";
export { FigmaSyncPanel, type FigmaSyncPanelProps } from "./FigmaSyncPanel";
export { FlowGraphView } from "./FlowGraphView";
export { FlowGraphViewInner } from "./FlowGraphViewInner";
// Rich node components
export { GraphNodePill } from "./GraphNodePill";
// Phase 5: Polish
export { GraphSearch } from "./GraphSearch";
export { GraphSkeleton } from "./GraphSkeleton";
export { ErrorState } from "./ErrorState";
export { LoadingTransition } from "./LoadingTransition";
export { LoadingProgress } from "./LoadingProgress";
// Error Recovery Components
export { EnhancedErrorState } from "./EnhancedErrorState";
export { GraphErrorBoundary } from "./GraphErrorBoundary";
export { NetworkErrorState } from "./NetworkErrorState";
export { TimeoutErrorState } from "./TimeoutErrorState";
export { RecoveryProgress } from "./RecoveryProgress";
export { GraphViewContainer, type GraphViewMode } from "./GraphViewContainer";
export { GraphToolbar } from "./GraphToolbar";
export { FilterControls } from "./FilterControls";
export { ExportControls } from "./ExportControls";
export { PerformanceStats } from "./PerformanceStats";
export { PerformanceOverlay } from "./PerformanceOverlay";
export { PerformanceChart } from "./PerformanceChart";
// Cross-perspective search hook
export {
	type CrossPerspectiveSearchResult,
	type EquivalenceInfo,
	type GroupedSearchResults,
	type SearchFilters,
	useCrossPerspectiveSearch,
} from "./hooks/useCrossPerspectiveSearch";
export {
	useGraphKeyboardShortcuts,
	KEYBOARD_SHORTCUTS,
} from "./hooks/useGraphKeyboardShortcuts";
export {
	type LayoutEdge,
	type LayoutMessage,
	type LayoutNode,
	type LayoutOptions,
	type LayoutResult,
	useGraphWorker,
	useNodeClustering,
} from "./hooks/useGraphWorker";
// Virtual rendering and performance hooks
export {
	type LODLevel,
	type NodePosition,
	useIntersectionVisibility,
	useProgressiveLoading,
	useVirtualization,
	type ViewportBounds,
	type VirtualizationMetrics,
} from "./hooks/useVirtualization";
export { JourneyExplorer } from "./JourneyExplorer";
// Phase 2: Node Expansion
export { KeyboardNavigation } from "./KeyboardNavigation";
export { getRecommendedLayout, LayoutSelector } from "./layouts/LayoutSelector";
// Layouts
export {
	LAYOUT_CONFIGS,
	type LayoutType,
	useDAGLayout,
} from "./layouts/useDAGLayout";
// Supporting components
export { NodeDetailPanel } from "./NodeDetailPanel";
export {
	ExpandableNode,
	type ExpandableNodeData,
} from "./nodes/ExpandableNode";
export { NodeExpandPopup } from "./nodes/NodeExpandPopup";
export {
	QAEnhancedNode,
	type QAEnhancedNodeData,
} from "./nodes/QAEnhancedNode";
export { PageDecompositionView } from "./PageDecompositionView";
export { PageInteractionFlow } from "./PageInteractionFlow";
export { PerspectiveSelector } from "./PerspectiveSelector";
export {
	buildPivotTargets,
	PivotNavigation,
	type PivotTarget,
} from "./PivotNavigation";
export { type RichNodeData, RichNodePill } from "./RichNodePill";
export { type MediumPillData, MediumPill } from "./MediumPill";
export { SimplePill, type SimplePillData } from "./SimplePill";
export { SkeletonPill } from "./SkeletonPill";
// Rich node interaction components
export { NodeActions } from "./NodeActions";
export { NodeContextMenu } from "./NodeContextMenu";
export { NodeHoverTooltip } from "./NodeHoverTooltip";
export { NodeQuickActions } from "./NodeQuickActions";
// Phase 3: Screenshots
export { ThumbnailPreview } from "./ThumbnailPreview";
// Types and utilities
export * from "./types";
// UI-specific views
export { UIComponentTree } from "./UIComponentTree";
// Main unified view with sidebar navigation
export {
	type DerivedJourney,
	type DisplayMode,
	type EquivalenceMode,
	UnifiedGraphView,
} from "./UnifiedGraphView";
export { VirtualizedGraphView } from "./VirtualizedGraphView";

// Phase 6: WebGL Rendering (Sigma.js)
export { SigmaGraphView } from "./SigmaGraphView";
export { RichNodeDetailPanel } from "./sigma/RichNodeDetailPanel";
export {
	customNodeRenderer,
	customEdgeRenderer,
	sigmaRenderers,
} from "./sigma/customRenderers";

// Phase 6: Hybrid Graph (Task #26) - Automatic threshold switching
export { HybridGraphView } from "./HybridGraphView";

// Safe Components with Error Boundaries (Phase 2 Code Quality)
export {
	SafeGraphViewContainer,
	SafeFlowGraphView,
	SafeEnhancedGraphView,
	SafeVirtualizedGraphView,
	SafeUnifiedGraphView,
} from "./SafeGraphComponents";
