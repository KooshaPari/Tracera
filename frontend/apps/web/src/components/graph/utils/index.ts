// Graph visualization utilities
// Exports all grouping, hierarchy, and drill-down utilities

// Grouping algorithms
export {
	groupByLinkTargets,
	groupByDependencies,
	groupByPaths,
	groupBySemantic,
	intersectGroupResults,
	calculateGroupCohesion,
	calculateGroupSeparation,
	type GroupingStrategy,
	type GroupResult,
} from "./grouping";

// Hierarchy utilities
export {
	buildHierarchy,
	getDepth,
	getParent,
	getChildren,
	getAncestorChain,
	getDescendantNodes,
	getBreadcrumbPath,
	findCommonAncestor,
	getSiblings,
	isAncestor,
	isDescendant,
	getItemsAtDepth,
	getHierarchyStats,
	exportHierarchyStructure,
	type HierarchyNode,
} from "./hierarchy";

// Drill-down navigation utilities
export {
	inferDrillDownLevel,
	getNextLevel,
	getPreviousLevel,
	createBreadcrumbs,
	getChildrenByDrillDownLevel,
	createDrillDownContext,
	createDrillDownNodeGroups,
	expandDrillDownGroup,
	collapseDrillDownGroup,
	toggleDrillDownGroup,
	getVisibleDrillDownItems,
	navigateUp,
	navigateToChild,
	getDrillDownPath,
	calculateLazyLoadingRequirements,
	getDrillDownStats,
	type DrillDownLevel,
	type DrillDownContext,
	type DrillDownBreadcrumb,
	type DrillDownNodeGroup,
} from "./drilldown";

// Type styles (existing)
export { getTypeColor, getTypeLabel, getTypeIcon } from "./typeStyles";

// Equivalence IO (existing)
export type {
	NodePositions,
	LayoutCache,
	LayoutCacheEntry,
} from "./equivalenceIO";
export {
	saveLayoutCache,
	loadLayoutCache,
	cacheLayout,
	getCachedLayout,
	evictFromCache,
	generateCacheKey,
	isLayoutCacheValid,
} from "./equivalenceIO";
