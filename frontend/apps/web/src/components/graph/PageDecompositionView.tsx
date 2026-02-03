// PageDecompositionView.tsx - Hierarchical page → element breakdown
// Shows UI structure: Site → Page → Layout → Section → Component → Element

import type { Item, Link, UIEntityType } from "@tracertm/types";
import { ENTITY_DEPTH_LEVELS } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card, CardHeader, CardTitle } from "@tracertm/ui/components/Card";
import { Input } from "@tracertm/ui/components/Input";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import { Separator } from "@tracertm/ui/components/Separator";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import {
	Box,
	ChevronDown,
	ChevronRight,
	Code,
	Component,
	FolderOpen,
	Globe,
	Grid3x3,
	Image,
	Layers,
	LayoutGrid,
	LayoutPanelLeft,
	Maximize2,
	Monitor,
	MousePointer2,
	PanelLeft,
	Route,
	Search,
	Square,
	SquareStack,
} from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";

// =============================================================================
// TYPES
// =============================================================================

export interface PageDecompositionViewProps {
	/** All items in the project */
	items: Item[];
	/** Links between items */
	links: Link[];
	/** Callback when an item is selected */
	onSelectItem: (itemId: string) => void;
	/** Currently selected item ID */
	selectedItemId: string | null;
	/** Callback to view item in code */
	onViewInCode?: (itemId: string) => void;
	/** Callback to view item in design */
	onViewInDesign?: (itemId: string) => void;
	/** Root site/application ID to start from (optional) */
	rootId?: string;
}

interface DecompositionNode {
	id: string;
	item: Item;
	entityType: UIEntityType;
	depth: number;
	children: DecompositionNode[];
	route?: string;
	componentPath?: string;
	hasScreenshot: boolean;
	interactionCount: number;
	childCount: number;
}

interface DecompositionStats {
	sites: number;
	pages: number;
	layouts: number;
	sections: number;
	components: number;
	elements: number;
	modals: number;
	total: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

// Icon mapping for entity types
const ENTITY_ICONS: Record<
	UIEntityType,
	React.ComponentType<{ className?: string }>
> = {
	component: Component,
	drawer: LayoutPanelLeft,
	element: Square,
	layout: LayoutPanelLeft,
	modal: Maximize2,
	page: Monitor,
	popup: MousePointer2,
	section: Grid3x3,
	site: Globe,
	subcomponent: Box,
	subsection: SquareStack,
	toast: PanelLeft,
};

// Colors for entity types
const ENTITY_COLORS: Record<UIEntityType, string> = {
	component: "#22c55e",
	drawer: "#0ea5e9",
	element: "#64748b",
	layout: "#ec4899",
	modal: "#6366f1",
	page: "#8b5cf6",
	popup: "#a855f7",
	section: "#f59e0b",
	site: "#3b82f6",
	subcomponent: "#10b981",
	subsection: "#f97316",
	toast: "#14b8a6",
};

// Label mapping
const ENTITY_LABELS: Record<UIEntityType, string> = {
	component: "Component",
	drawer: "Drawer",
	element: "Element",
	layout: "Layout",
	modal: "Modal",
	page: "Page",
	popup: "Popup",
	section: "Section",
	site: "Site",
	subcomponent: "Sub-component",
	subsection: "Subsection",
	toast: "Toast",
};

// =============================================================================
// COMPONENT
// =============================================================================

function PageDecompositionViewComponent({
	items,
	links,
	onSelectItem,
	selectedItemId,
	onViewInCode,
	onViewInDesign,
	rootId,
}: PageDecompositionViewProps) {
	const [searchQuery, setSearchQuery] = useState("");
	const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
	const [viewMode, setViewMode] = useState<"tree" | "outline" | "visual">(
		"tree",
	);
	const [showDepthIndicator, setShowDepthIndicator] = useState(true);

	// Build decomposition tree
	const { tree, stats /* _itemMap */ } = useMemo(
		() => buildDecompositionTree(items, links, rootId),
		[items, links, rootId],
	);

	// Filter tree by search
	const filteredTree = useMemo(() => {
		if (!searchQuery) {
			return tree;
		}
		return filterTree(tree, searchQuery.toLowerCase());
	}, [tree, searchQuery]);

	// Handle expand/collapse
	const handleToggle = useCallback((id: string) => {
		setExpandedIds((prev) => {
			const next = new Set(prev);
			if (next.has(id)) {
				next.delete(id);
			} else {
				next.add(id);
			}
			return next;
		});
	}, []);

	const expandAll = useCallback(() => {
		const allIds = new Set<string>();
		function collectIds(node: DecompositionNode) {
			allIds.add(node.id);
			node.children.forEach(collectIds);
		}
		tree.forEach(collectIds);
		setExpandedIds(allIds);
	}, [tree]);

	const collapseAll = useCallback(() => {
		setExpandedIds(new Set());
	}, []);

	const expandToDepth = useCallback(
		(maxDepth: number) => {
			const ids = new Set<string>();
			function collectIds(node: DecompositionNode, currentDepth: number) {
				if (currentDepth < maxDepth) {
					ids.add(node.id);
					node.children.forEach((child) => collectIds(child, currentDepth + 1));
				}
			}
			tree.forEach((node) => collectIds(node, 0));
			setExpandedIds(ids);
		},
		[tree],
	);

	return (
		<TooltipProvider>
			<Card className="h-full flex flex-col overflow-hidden">
				{/* Header */}
				<CardHeader className="py-3 px-4 border-b">
					<div className="flex items-center justify-between">
						<div className="flex items-center gap-2">
							<Layers className="h-5 w-5 text-pink-500" />
							<CardTitle className="text-sm font-semibold">
								Page Decomposition
							</CardTitle>
						</div>
						<div className="flex items-center gap-1">
							{/* View mode toggle */}
							<div className="flex items-center gap-0.5 p-0.5 bg-muted rounded-md">
								<Button
									variant={viewMode === "tree" ? "default" : "ghost"}
									size="sm"
									className="h-6 w-6 p-0"
									onClick={() => setViewMode("tree")}
								>
									<FolderOpen className="h-3.5 w-3.5" />
								</Button>
								<Button
									variant={viewMode === "outline" ? "default" : "ghost"}
									size="sm"
									className="h-6 w-6 p-0"
									onClick={() => setViewMode("outline")}
								>
									<LayoutGrid className="h-3.5 w-3.5" />
								</Button>
							</div>
						</div>
					</div>
				</CardHeader>

				{/* Stats Row */}
				<div className="px-4 py-2 border-b bg-muted/30">
					<div className="flex flex-wrap gap-x-4 gap-y-1 text-xs">
						<StatBadge
							icon={Globe}
							count={stats.sites}
							label="Sites"
							color={ENTITY_COLORS.site}
						/>
						<StatBadge
							icon={Monitor}
							count={stats.pages}
							label="Pages"
							color={ENTITY_COLORS.page}
						/>
						<StatBadge
							icon={LayoutPanelLeft}
							count={stats.layouts}
							label="Layouts"
							color={ENTITY_COLORS.layout}
						/>
						<StatBadge
							icon={Grid3x3}
							count={stats.sections}
							label="Sections"
							color={ENTITY_COLORS.section}
						/>
						<StatBadge
							icon={Component}
							count={stats.components}
							label="Components"
							color={ENTITY_COLORS.component}
						/>
						<StatBadge
							icon={Square}
							count={stats.elements}
							label="Elements"
							color={ENTITY_COLORS.element}
						/>
					</div>
				</div>

				{/* Search & Controls */}
				<div className="px-4 py-2 border-b space-y-2">
					<div className="relative">
						<Search className="absolute left-2.5 top-2 h-4 w-4 text-muted-foreground" />
						<Input
							placeholder="Search pages, components..."
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							className="pl-8 h-8 text-sm"
						/>
					</div>
					<div className="flex items-center justify-between">
						<div className="flex gap-1">
							<Button
								variant="ghost"
								size="sm"
								className="h-6 px-2 text-xs"
								onClick={expandAll}
							>
								Expand All
							</Button>
							<Button
								variant="ghost"
								size="sm"
								className="h-6 px-2 text-xs"
								onClick={collapseAll}
							>
								Collapse All
							</Button>
							<Separator orientation="vertical" className="h-4 mx-1" />
							<Button
								variant="ghost"
								size="sm"
								className="h-6 px-2 text-xs"
								onClick={() => expandToDepth(2)}
							>
								Pages
							</Button>
							<Button
								variant="ghost"
								size="sm"
								className="h-6 px-2 text-xs"
								onClick={() => expandToDepth(4)}
							>
								Sections
							</Button>
						</div>
						<Button
							variant="ghost"
							size="sm"
							className={`h-6 px-2 text-xs ${showDepthIndicator ? "bg-muted" : ""}`}
							onClick={() => setShowDepthIndicator(!showDepthIndicator)}
						>
							Depth
						</Button>
					</div>
				</div>

				{/* Tree Content */}
				<ScrollArea className="flex-1">
					<div className="p-2">
						{filteredTree.length > 0 ? (
							filteredTree.map((node) => (
								<DecompositionTreeItem
									key={node.id}
									node={node}
									selectedId={selectedItemId}
									expandedIds={expandedIds}
									onToggle={handleToggle}
									onSelect={onSelectItem}
									onViewInCode={onViewInCode}
									onViewInDesign={onViewInDesign}
									showDepthIndicator={showDepthIndicator}
									viewMode={viewMode}
								/>
							))
						) : (
							<EmptyState searchQuery={searchQuery} />
						)}
					</div>
				</ScrollArea>
			</Card>
		</TooltipProvider>
	);
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface StatBadgeProps {
	icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
	count: number;
	label: string;
	color: string;
}

function StatBadge({ icon: Icon, count, label, color }: StatBadgeProps) {
	if (count === 0) {
		return null;
	}
	return (
		<div className="flex items-center gap-1">
			<Icon className="h-3 w-3" style={{ color }} />
			<span className="font-medium">{count}</span>
			<span className="text-muted-foreground">{label}</span>
		</div>
	);
}

interface DecompositionTreeItemProps {
	node: DecompositionNode;
	selectedId: string | null;
	expandedIds: Set<string>;
	onToggle: (id: string) => void;
	onSelect: (id: string) => void;
	onViewInCode?: (itemId: string) => void;
	onViewInDesign?: (itemId: string) => void;
	showDepthIndicator: boolean;
	viewMode: "tree" | "outline" | "visual";
}

function DecompositionTreeItem({
	node,
	selectedId,
	expandedIds,
	onToggle,
	onSelect,
	onViewInCode,
	onViewInDesign: _onViewInDesign,
	showDepthIndicator,
	viewMode,
}: DecompositionTreeItemProps) {
	const isExpanded = expandedIds.has(node.id);
	const isSelected = selectedId === node.id;
	const hasChildren = node.children.length > 0;

	const Icon = ENTITY_ICONS[node.entityType] || Box;
	const color = ENTITY_COLORS[node.entityType] || "#64748b";
	const label = ENTITY_LABELS[node.entityType] || node.entityType;

	const indentPx =
		viewMode === "outline" ? node.depth * 24 + 8 : node.depth * 16 + 8;

	return (
		<div>
			<div
				className={`
					group flex items-center gap-1.5 px-2 py-1.5 rounded-md cursor-pointer transition-colors
					${isSelected ? "bg-primary/10 ring-1 ring-primary/30" : "hover:bg-muted"}
				`}
				style={{ paddingLeft: `${indentPx}px` }}
				onClick={() => onSelect(node.id)}
			>
				{/* Depth indicator */}
				{showDepthIndicator && (
					<div className="flex items-center gap-0.5 mr-1">
						{Array.from({ length: Math.min(node.depth, 5) }).map((_, i) => (
							<div
								key={i}
								className="w-0.5 h-3 rounded-full opacity-30"
								style={{ backgroundColor: color }}
							/>
						))}
					</div>
				)}

				{/* Expand/Collapse */}
				{hasChildren ? (
					<button
						onClick={(e) => {
							e.stopPropagation();
							onToggle(node.id);
						}}
						className="p-0.5 hover:bg-muted-foreground/20 rounded shrink-0"
					>
						{isExpanded ? (
							<ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
						) : (
							<ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
						)}
					</button>
				) : (
					<span className="w-4.5 shrink-0" />
				)}

				{/* Icon */}
				<div
					className="rounded p-1 shrink-0"
					style={{ backgroundColor: `${color}20` }}
				>
					<Icon className="h-3.5 w-3.5" style={{ color }} />
				</div>

				{/* Content */}
				<div className="flex-1 min-w-0 flex items-center gap-2">
					<span className="text-sm truncate font-medium">
						{node.item.title || "Untitled"}
					</span>

					{/* Entity type badge */}
					{viewMode === "outline" && (
						<Badge
							variant="outline"
							className="text-[10px] px-1.5 py-0 shrink-0"
							style={{ borderColor: `${color}50`, color }}
						>
							{label}
						</Badge>
					)}

					{/* Route indicator */}
					{node.route && (
						<Tooltip delayDuration={200}>
							<TooltipTrigger asChild>
								<Badge
									variant="secondary"
									className="text-[10px] px-1.5 py-0 shrink-0"
								>
									<Route className="h-2.5 w-2.5 mr-0.5" />
									{node.route}
								</Badge>
							</TooltipTrigger>
							<TooltipContent>Route: {node.route}</TooltipContent>
						</Tooltip>
					)}
				</div>

				{/* Indicators */}
				<div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
					{node.hasScreenshot && (
						<Tooltip delayDuration={200}>
							<TooltipTrigger asChild>
								<Image className="h-3 w-3 text-muted-foreground" />
							</TooltipTrigger>
							<TooltipContent>Has screenshot</TooltipContent>
						</Tooltip>
					)}
					{node.interactionCount > 0 && (
						<Tooltip delayDuration={200}>
							<TooltipTrigger asChild>
								<div className="flex items-center gap-0.5">
									<MousePointer2 className="h-3 w-3 text-muted-foreground" />
									<span className="text-[10px] text-muted-foreground">
										{node.interactionCount}
									</span>
								</div>
							</TooltipTrigger>
							<TooltipContent>
								{node.interactionCount} interactions
							</TooltipContent>
						</Tooltip>
					)}
					{node.componentPath && onViewInCode && (
						<Tooltip delayDuration={200}>
							<TooltipTrigger asChild>
								<Button
									variant="ghost"
									size="sm"
									className="h-5 w-5 p-0"
									onClick={(e) => {
										e.stopPropagation();
										onViewInCode(node.id);
									}}
								>
									<Code className="h-3 w-3" />
								</Button>
							</TooltipTrigger>
							<TooltipContent>View in code</TooltipContent>
						</Tooltip>
					)}
				</div>

				{/* Child count */}
				{hasChildren && (
					<Badge
						variant="secondary"
						className="text-[10px] px-1.5 h-4 shrink-0"
					>
						{node.childCount}
					</Badge>
				)}
			</div>

			{/* Children */}
			{isExpanded && hasChildren && (
				<div>
					{node.children.map((child) => (
						<DecompositionTreeItem
							key={child.id}
							node={child}
							selectedId={selectedId}
							expandedIds={expandedIds}
							onToggle={onToggle}
							onSelect={onSelect}
							onViewInCode={onViewInCode}
							showDepthIndicator={showDepthIndicator}
							viewMode={viewMode}
						/>
					))}
				</div>
			)}
		</div>
	);
}

interface EmptyStateProps {
	searchQuery: string;
}

function EmptyState({ searchQuery }: EmptyStateProps) {
	return (
		<div className="text-center py-12 text-muted-foreground">
			<Layers className="h-12 w-12 mx-auto mb-3 opacity-50" />
			{searchQuery ? (
				<>
					<p className="text-sm font-medium">No matching items</p>
					<p className="text-xs mt-1">Try a different search term</p>
				</>
			) : (
				<>
					<p className="text-sm font-medium">No UI structure found</p>
					<p className="text-xs mt-1 max-w-xs mx-auto">
						Add pages, layouts, sections, and components to see the
						decomposition hierarchy
					</p>
				</>
			)}
		</div>
	);
}

// =============================================================================
// UTILITIES
// =============================================================================

function buildDecompositionTree(
	items: Item[],
	links: Link[],
	rootId?: string,
): {
	tree: DecompositionNode[];
	stats: DecompositionStats;
	itemMap: Map<string, Item>;
} {
	const itemMap = new Map(items.map((i) => [i.id, i]));
	const childrenMap = new Map<string, Item[]>();
	const stats: DecompositionStats = {
		components: 0,
		elements: 0,
		layouts: 0,
		modals: 0,
		pages: 0,
		sections: 0,
		sites: 0,
		total: 0,
	};

	// Filter to UI items and infer entity type
	const uiItems = items.filter((item) => {
		const type = item.type?.toLowerCase() || "";
		return (
			isValidUIType(type) ||
			item.view?.toLowerCase().includes("ui") ||
			item.view?.toLowerCase().includes("wireframe")
		);
	});

	// Build parent-child map
	for (const item of uiItems) {
		const parentId = item.parentId || "root";
		if (!childrenMap.has(parentId)) {
			childrenMap.set(parentId, []);
		}
		childrenMap.get(parentId)!.push(item);
	}

	// Build interaction counts (include UI interaction link types; LinkType union may not include these in all packages)
	const interactionCounts = new Map<string, number>();
	const interactionTypes = ["navigates_to", "opens", "triggers"];
	for (const link of links) {
		if (interactionTypes.includes(link.type as string)) {
			interactionCounts.set(
				link.sourceId,
				(interactionCounts.get(link.sourceId) || 0) + 1,
			);
		}
	}

	// Recursive node builder
	function buildNode(item: Item, depth: number): DecompositionNode {
		const entityType = inferEntityType(item);
		const children = (childrenMap.get(item.id) || [])
			.toSorted((a, b) => {
				// Sort by entity depth, then by title
				const depthA = ENTITY_DEPTH_LEVELS[inferEntityType(a)] || 0;
				const depthB = ENTITY_DEPTH_LEVELS[inferEntityType(b)] || 0;
				if (depthA !== depthB) {
					return depthA - depthB;
				}
				return (a.title || "").localeCompare(b.title || "");
			})
			.map((child) => buildNode(child, depth + 1));

		// Count stats
		updateStats(entityType, stats);
		stats.total += 1;

		// Get metadata
		const metadata = item.metadata as Record<string, unknown> | undefined;

		return {
			childCount: countAllChildren(children),
			children,
			componentPath: (metadata?.["componentPath"] as string) || undefined,
			depth,
			entityType,
			hasScreenshot: !!(metadata?.["screenshotUrl"] || metadata?.["thumbnailUrl"]),
			id: item.id,
			interactionCount: interactionCounts.get(item.id) || 0,
			item,
			route: (metadata?.["route"] as string) || undefined,
		};
	}

	// Build tree from roots
	let rootItems: Item[];
	if (rootId) {
		const root = itemMap.get(rootId);
		rootItems = root ? [root] : [];
	} else {
		rootItems = childrenMap.get("root") || uiItems.filter((i) => !i.parentId);
	}

	// Group and sort root items
	const sortedRoots = rootItems.toSorted((a, b) => {
		const typeOrder = ["site", "page", "screen", "layout", "wireframe"];
		const aOrder = typeOrder.indexOf(a.type?.toLowerCase() || "");
		const bOrder = typeOrder.indexOf(b.type?.toLowerCase() || "");
		if (aOrder !== bOrder) {
			return aOrder - bOrder;
		}
		return (a.title || "").localeCompare(b.title || "");
	});

	const tree = sortedRoots.map((item) => buildNode(item, 0));

	return { itemMap, stats, tree };
}

function inferEntityType(item: Item): UIEntityType {
	const type = item.type?.toLowerCase() || "";

	// Direct mappings
	const typeMap: Record<string, UIEntityType> = {
		app: "site",
		application: "site",
		area: "section",
		atom: "element",
		block: "component",
		component: "component",
		dialog: "modal",
		drawer: "drawer",
		element: "element",
		frame: "layout",
		layout: "layout",
		modal: "modal",
		notification: "toast",
		page: "page",
		panel: "drawer",
		popover: "popup",
		popup: "popup",
		primitive: "element",
		region: "section",
		route: "page",
		screen: "page",
		section: "section",
		sidebar: "drawer",
		site: "site",
		subcomponent: "subcomponent",
		subsection: "subsection",
		template: "layout",
		toast: "toast",
		ui_component: "component",
		view: "page",
		widget: "component",
	};

	return typeMap[type] || "component";
}

function isValidUIType(type: string): boolean {
	const validTypes = [
		"site",
		"application",
		"app",
		"page",
		"screen",
		"view",
		"route",
		"layout",
		"template",
		"frame",
		"section",
		"region",
		"area",
		"subsection",
		"component",
		"widget",
		"block",
		"ui_component",
		"subcomponent",
		"element",
		"atom",
		"primitive",
		"modal",
		"dialog",
		"popup",
		"popover",
		"toast",
		"notification",
		"drawer",
		"sidebar",
		"panel",
		"wireframe",
	];
	return validTypes.includes(type);
}

function updateStats(entityType: UIEntityType, stats: DecompositionStats) {
	switch (entityType) {
		case "site": {
			stats.sites++;
			break;
		}
		case "page": {
			stats.pages++;
			break;
		}
		case "layout": {
			stats.layouts++;
			break;
		}
		case "section":
		case "subsection": {
			stats.sections++;
			break;
		}
		case "component":
		case "subcomponent": {
			stats.components++;
			break;
		}
		case "element": {
			stats.elements++;
			break;
		}
		case "modal":
		case "popup":
		case "drawer":
		case "toast": {
			stats.modals++;
			break;
		}
	}
}

function countAllChildren(children: DecompositionNode[]): number {
	let count = children.length;
	for (const child of children) {
		count += countAllChildren(child.children);
	}
	return count;
}

function filterTree(
	tree: DecompositionNode[],
	query: string,
): DecompositionNode[] {
	function filterNode(node: DecompositionNode): DecompositionNode | null {
		const matchesTitle = (node.item.title || "").toLowerCase().includes(query);
		const matchesType = node.entityType.toLowerCase().includes(query);
		const matchesRoute = (node.route || "").toLowerCase().includes(query);

		const filteredChildren = node.children
			.map(filterNode)
			.filter((n): n is DecompositionNode => n !== null);

		if (
			matchesTitle ||
			matchesType ||
			matchesRoute ||
			filteredChildren.length > 0
		) {
			return { ...node, children: filteredChildren };
		}
		return null;
	}

	return tree.map(filterNode).filter((n): n is DecompositionNode => n !== null);
}

// =============================================================================
// EXPORTS
// =============================================================================

export const PageDecompositionView = memo(PageDecompositionViewComponent);
