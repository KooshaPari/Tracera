/**
 * Graph Library - Hybrid Architecture
 *
 * Exports both legacy and Graphology-based graph data structures
 */

// Graphology Data Layer (NEW - for 100k+ nodes)
export {
	GraphologyDataLayer,
	createGraphologyDataLayer,
	getGraphologyDataLayer,
	resetGraphologyDataLayer,
} from "./GraphologyDataLayer";

export type {
	GraphologyNodeData,
	GraphologyEdgeData,
	GraphStats,
	PerformanceMetrics,
	LayoutOptions,
} from "./GraphologyDataLayer";

// Incremental Graph Builder (Legacy)
export { IncrementalGraphBuilder } from "./IncrementalGraphBuilder";
export type {
	GraphNode,
	GraphEdge,
	StreamChunk,
	ProgressInfo,
	StreamMetadata,
	ViewportBounds,
	GraphBuildResult,
	BuildOptions,
} from "./IncrementalGraphBuilder";
