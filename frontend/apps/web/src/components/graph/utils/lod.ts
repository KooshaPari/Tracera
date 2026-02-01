/**
 * Level-of-detail (LOD) for graph nodes.
 * Used for varying node representation by zoom and optionally node count
 * (skeleton/LOD design + perf B3).
 *
 * **LOD × State:** When a node is loading or errored, the node type is chosen by
 * `getNodeTypeWithLOD` (nodeRegistry): loading → `nodeLoading`, error → `nodeError`,
 * else LOD drives rich vs simple pill. Each skeleton (NodeLoadingSkeleton, NodeErrorSkeleton)
 * renders a shape that matches the LOD (VeryFar = dot, … VeryClose = full card).
 *
 * @see docs/guides/SKELETON_AND_LOD_DESIGN.md
 * @see docs/research/REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md (B3)
 */

export enum LODLevel {
	VeryFar = 0, // zoom < 0.2
	Far = 1, // 0.2 <= zoom < 0.5
	Medium = 2, // 0.5 <= zoom < 1.0
	Close = 3, // 1.0 <= zoom < 2.0
	VeryClose = 4, // zoom >= 2.0
}

/** Zoom thresholds (inclusive lower bound). */
const ZOOM_THRESHOLDS: Record<LODLevel, number> = {
	[LODLevel.VeryFar]: 0,
	[LODLevel.Far]: 0.2,
	[LODLevel.Medium]: 0.5,
	[LODLevel.Close]: 1.0,
	[LODLevel.VeryClose]: 2.0,
};

/** Default node count above which we force at most Medium LOD (simplified nodes). */
export const LOD_NODE_COUNT_THRESHOLD = 100;

/**
 * Resolve LOD level from viewport zoom.
 * Optionally force a coarser LOD when node count is high (perf: fewer heavy nodes).
 *
 * @param zoom - Current viewport zoom (e.g. from React Flow).
 * @param options - Optional: nodeCount (total nodes), forceSimplifiedAbove (default 100).
 * @returns LODLevel; when nodeCount >= forceSimplifiedAbove and zoom would give Close/VeryClose, returns Medium.
 */
export function determineLODLevel(
	zoom: number,
	options?: { nodeCount?: number; forceSimplifiedAbove?: number },
): LODLevel {
	const { nodeCount, forceSimplifiedAbove = LOD_NODE_COUNT_THRESHOLD } =
		options ?? {};

	let level: LODLevel;
	if (zoom < 0.2) level = LODLevel.VeryFar;
	else if (zoom < 0.5) level = LODLevel.Far;
	else if (zoom < 1.0) level = LODLevel.Medium;
	else if (zoom < 2.0) level = LODLevel.Close;
	else level = LODLevel.VeryClose;

	// When there are many nodes, cap at Medium so we use simplified node type
	if (
		forceSimplifiedAbove > 0 &&
		nodeCount != null &&
		nodeCount >= forceSimplifiedAbove &&
		level > LODLevel.Medium
	) {
		return LODLevel.Medium;
	}
	return level;
}

/**
 * Whether this LOD should use a simplified (light) node type (e.g. small pill, no previews).
 * True for VeryFar, Far, Medium; false for Close, VeryClose.
 */
export function shouldUseSimplifiedNode(lod: LODLevel): boolean {
	return lod <= LODLevel.Medium;
}

/** Returns the zoom value that is the lower bound for the given LOD level. */
export function getLODZoomThreshold(level: LODLevel): number {
	return ZOOM_THRESHOLDS[level];
}
