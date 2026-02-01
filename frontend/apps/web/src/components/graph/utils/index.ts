// Graph visualization utilities
// Exports all grouping, hierarchy, and drill-down utilities

// Drill-down navigation utilities
export {
	calculateLazyLoadingRequirements,
	collapseDrillDownGroup,
	createBreadcrumbs,
	createDrillDownContext,
	createDrillDownNodeGroups,
	type DrillDownBreadcrumb,
	type DrillDownContext,
	type DrillDownLevel,
	type DrillDownNodeGroup,
	expandDrillDownGroup,
	getChildrenByDrillDownLevel,
	getDrillDownPath,
	getDrillDownStats,
	getNextLevel,
	getPreviousLevel,
	getVisibleDrillDownItems,
	inferDrillDownLevel,
	navigateToChild,
	navigateUp,
	toggleDrillDownGroup,
} from "./drilldown";
// Equivalence IO (existing)
export type {
	LayoutCache,
	LayoutCacheEntry,
	NodePositions,
} from "./equivalenceIO";
export {
	cacheLayout,
	evictFromCache,
	generateCacheKey,
	getCachedLayout,
	isLayoutCacheValid,
	loadLayoutCache,
	saveLayoutCache,
} from "./equivalenceIO";
// Grouping algorithms
export {
	calculateGroupCohesion,
	calculateGroupSeparation,
	type GroupingStrategy,
	type GroupResult,
	groupByDependencies,
	groupByLinkTargets,
	groupByPaths,
	groupBySemantic,
	intersectGroupResults,
} from "./grouping";
// Hierarchy utilities
export {
	buildHierarchy,
	exportHierarchyStructure,
	findCommonAncestor,
	getAncestorChain,
	getBreadcrumbPath,
	getChildren,
	getDepth,
	getDescendantNodes,
	getHierarchyStats,
	getItemsAtDepth,
	getParent,
	getSiblings,
	type HierarchyNode,
	isAncestor,
	isDescendant,
} from "./hierarchy";
// LOD (level-of-detail) for graph nodes — skeleton/perf
export {
	determineLODLevel,
	getLODZoomThreshold,
	LOD_NODE_COUNT_THRESHOLD,
	LODLevel,
	shouldUseSimplifiedNode,
} from "./lod";
// Type styles (existing)
export { getTypeColor, getTypeIcon, getTypeLabel } from "./typeStyles";
