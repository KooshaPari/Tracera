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

const ZOOM_THRESHOLD_VERY_FAR = 0;
const ZOOM_THRESHOLD_FAR = 0.2;
const ZOOM_THRESHOLD_MEDIUM = 0.5;
const ZOOM_THRESHOLD_CLOSE = 1;
const ZOOM_THRESHOLD_VERY_CLOSE = 2;

export enum LODLevel {
  VeryFar,
  Far,
  Medium,
  Close,
  VeryClose,
}

/** Zoom thresholds (inclusive lower bound). */
const ZOOM_THRESHOLDS: Record<LODLevel, number> = {
  [LODLevel.VeryFar]: ZOOM_THRESHOLD_VERY_FAR,
  [LODLevel.Far]: ZOOM_THRESHOLD_FAR,
  [LODLevel.Medium]: ZOOM_THRESHOLD_MEDIUM,
  [LODLevel.Close]: ZOOM_THRESHOLD_CLOSE,
  [LODLevel.VeryClose]: ZOOM_THRESHOLD_VERY_CLOSE,
};

const LOD_STEPS: { level: LODLevel; maxZoom: number }[] = [
  { level: LODLevel.VeryFar, maxZoom: ZOOM_THRESHOLD_FAR },
  { level: LODLevel.Far, maxZoom: ZOOM_THRESHOLD_MEDIUM },
  { level: LODLevel.Medium, maxZoom: ZOOM_THRESHOLD_CLOSE },
  { level: LODLevel.Close, maxZoom: ZOOM_THRESHOLD_VERY_CLOSE },
];

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
const determineLODLevel = (
  zoom: number,
  options?: { nodeCount?: number; forceSimplifiedAbove?: number },
): LODLevel => {
  const { nodeCount, forceSimplifiedAbove = LOD_NODE_COUNT_THRESHOLD } = options ?? {};

  let level = LODLevel.VeryClose;
  for (const step of LOD_STEPS) {
    if (zoom < step.maxZoom) {
      ({ level } = step);
      break;
    }
  }

  const hasNodeCount = nodeCount !== undefined && nodeCount !== null;
  if (
    forceSimplifiedAbove > 0 &&
    hasNodeCount &&
    nodeCount >= forceSimplifiedAbove &&
    level > LODLevel.Medium
  ) {
    return LODLevel.Medium;
  }
  return level;
};

/**
 * Whether this LOD should use a simplified (light) node type (e.g. small pill, no previews).
 * True for VeryFar, Far, Medium; false for Close, VeryClose.
 */
const shouldUseSimplifiedNode = (lod: LODLevel): boolean => lod <= LODLevel.Medium;

/** Returns the zoom value that is the lower bound for the given LOD level. */
const getLODZoomThreshold = (level: LODLevel): number => ZOOM_THRESHOLDS[level];

export { determineLODLevel, getLODZoomThreshold, shouldUseSimplifiedNode };
