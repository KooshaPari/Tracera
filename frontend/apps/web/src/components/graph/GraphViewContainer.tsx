// Graph View Container - Project views in sidebar; graph type (mind map, flow chart, etc.) in combobox

import type { Item, Link } from "@tracertm/types";
import { Link as RouterLink } from "@tanstack/react-router";
import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import { Input } from "@tracertm/ui/components/Input";
import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { Separator } from "@tracertm/ui/components/Separator";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	Activity,
	ArrowDown,
	BarChart3,
	BookOpen,
	ChevronLeft,
	ChevronRight,
	CircleDot,
	Code,
	Component,
	Database,
	FileStack,
	GitBranch,
	Globe,
	Layers,
	LayoutGrid,
	Lock,
	MapPin,
	Monitor,
	Network,
	Route,
	Search,
	Share2,
	Shield,
	ShoppingCart,
	TestTube,
	Workflow,
	Zap,
} from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import type { LayoutType } from "./layouts/useDAGLayout";
import type { GraphPerspective } from "./types";
import { PERSPECTIVE_CONFIGS } from "./types";

// View types: graph/diagram styles + perspectives
export type GraphViewMode =
	| "traceability"
	| "flow-chart"
	| "dependency-graph"
	| "hierarchy"
	| "impact-map"
	| "journey-map"
	| "mind-map"
	| "gallery"
	| "page-flow"
	| "components"
	| "perspective-product"
	| "perspective-business"
	| "perspective-technical"
	| "perspective-ui"
	| "perspective-security"
	| "perspective-performance";

interface ViewConfig {
	id: GraphViewMode;
	label: string;
	description: string;
	icon: React.ComponentType<{ className?: string }>;
	category: "graph" | "diagram" | "perspective";
	perspective?: GraphPerspective;
	/** Layout to use when this view is a graph (traceability-style) view. */
	layoutPreference?: LayoutType;
}

const VIEW_CONFIGS: ViewConfig[] = [
	// ---- Graph & diagram views (same data, different layout or visualization) ----
	{
		id: "traceability",
		label: "Traceability Graph",
		description: "Full node graph with all connections",
		icon: Network,
		category: "graph",
		layoutPreference: "organic-network",
	},
	{
		id: "flow-chart",
		label: "Flow Chart",
		description: "Top-to-bottom directed flow",
		icon: ArrowDown,
		category: "graph",
		layoutPreference: "flow-chart",
	},
	{
		id: "dependency-graph",
		label: "Dependency Graph",
		description: "Dependencies and relationships",
		icon: Share2,
		category: "graph",
		layoutPreference: "flow-chart",
	},
	{
		id: "hierarchy",
		label: "Hierarchy / Tree",
		description: "Tree structure and parent-child",
		icon: GitBranch,
		category: "graph",
		layoutPreference: "tree",
	},
	{
		id: "impact-map",
		label: "Impact Map",
		description: "Impact and downstream effects",
		icon: MapPin,
		category: "graph",
		layoutPreference: "organic-network",
	},
	{
		id: "journey-map",
		label: "Journey Map",
		description: "User flows and sequences",
		icon: Route,
		category: "graph",
		layoutPreference: "timeline",
	},
	{
		id: "mind-map",
		label: "Mind Map",
		description: "Radial layout from center",
		icon: CircleDot,
		category: "graph",
		layoutPreference: "mind-map",
	},
	{
		id: "gallery",
		label: "Gallery / Grid",
		description: "Grid for quick overview",
		icon: LayoutGrid,
		category: "graph",
		layoutPreference: "gallery",
	},
	// ---- Diagram views (different visualization) ----
	{
		id: "page-flow",
		label: "Page Flow",
		description: "UI page interactions and navigation",
		icon: Workflow,
		category: "diagram",
	},
	{
		id: "components",
		label: "Component Library",
		description: "UI component tree and hierarchy",
		icon: Component,
		category: "diagram",
	},
	// ---- Perspectives (filtered by type) ----
	{
		id: "perspective-product",
		label: "Product View",
		description: "Features, epics, and user stories",
		icon: ShoppingCart,
		category: "perspective",
		perspective: "product",
	},
	{
		id: "perspective-business",
		label: "Business View",
		description: "Business rules and requirements",
		icon: FileStack,
		category: "perspective",
		perspective: "business",
	},
	{
		id: "perspective-technical",
		label: "Technical View",
		description: "Architecture and implementation",
		icon: GitBranch,
		category: "perspective",
		perspective: "technical",
	},
	{
		id: "perspective-ui",
		label: "UI/UX View",
		description: "Wireframes, mockups, and screens",
		icon: Monitor,
		category: "perspective",
		perspective: "ui",
	},
	{
		id: "perspective-security",
		label: "Security View",
		description: "Security requirements and controls",
		icon: Lock,
		category: "perspective",
		perspective: "security",
	},
	{
		id: "perspective-performance",
		label: "Performance View",
		description: "Performance requirements and metrics",
		icon: Zap,
		category: "perspective",
		perspective: "performance",
	},
];

/** Project view nav items for sidebar (Feature, API, Test, Graph, etc.) */
const PROJECT_VIEW_NAV: { label: string; viewType: string; icon: React.ComponentType<{ className?: string }> }[] = [
	{ label: "Features", viewType: "feature", icon: Layers },
	{ label: "Traceability / Graph", viewType: "graph", icon: Network },
	{ label: "Test Suite", viewType: "test", icon: TestTube },
	{ label: "API Docs", viewType: "api", icon: Globe },
	{ label: "Database", viewType: "database", icon: Database },
	{ label: "Wireframe", viewType: "wireframe", icon: LayoutGrid },
	{ label: "Matrix", viewType: "matrix", icon: BarChart3 },
	{ label: "Workflows", viewType: "workflows", icon: Activity },
	{ label: "Code", viewType: "code", icon: Code },
	{ label: "Test Cases", viewType: "test-cases", icon: TestTube },
	{ label: "Test Runs", viewType: "test-runs", icon: Activity },
	{ label: "Test Suites", viewType: "test-suites", icon: FileStack },
	{ label: "Problem", viewType: "problem", icon: Shield },
	{ label: "Process", viewType: "process", icon: Workflow },
	{ label: "Documentation", viewType: "documentation", icon: BookOpen },
];

interface GraphViewContainerProps {
	items: Item[];
	links: Link[];
	isLoading?: boolean | undefined;
	projectId?: string | undefined;
	onNavigateToItem?: ((itemId: string) => void) | undefined;
	defaultView?: GraphViewMode | undefined;
	canLoadMore?: boolean | undefined;
	visibleEdges?: number | undefined;
	totalEdges?: number | undefined;
	onLoadMore?: (() => void) | undefined;
	children: (props: {
		viewMode: GraphViewMode;
		perspective: GraphPerspective | null;
		layoutPreference: LayoutType | undefined;
		items: Item[];
		links: Link[];
		onNavigateToItem?: ((itemId: string) => void) | undefined;
	}) => React.ReactNode;
}

export function GraphViewContainer({
	items,
	links,
	projectId,
	isLoading = false,
	onNavigateToItem,
	defaultView = "traceability",
	canLoadMore: _canLoadMore = false,
	visibleEdges: _visibleEdges,
	totalEdges: _totalEdges,
	onLoadMore: _onLoadMore,
	children,
}: GraphViewContainerProps) {
	const [viewMode, setViewMode] = useState<GraphViewMode>(defaultView);
	const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
	const [viewTypeSearch, setViewTypeSearch] = useState("");

	// Get current view config
	const currentConfig = useMemo(
		() => VIEW_CONFIGS.find((c) => c.id === viewMode) || VIEW_CONFIGS[0],
		[viewMode],
	);

	// Calculate item counts per perspective
	const _perspectiveCounts = useMemo(() => {
		const counts = {
			all: items.length,
			product: 0,
			business: 0,
			technical: 0,
			ui: 0,
			security: 0,
			performance: 0,
		};

		for (const item of items) {
			const itemType = (item.type || item.view || "").toLowerCase();

			// Product items
			if (
				itemType.includes("feature") ||
				itemType.includes("epic") ||
				itemType.includes("story") ||
				itemType.includes("requirement")
			) {
				counts.product++;
			}

			// Business items
			if (
				itemType.includes("business") ||
				itemType.includes("rule") ||
				itemType.includes("process")
			) {
				counts.business++;
			}

			// Technical items
			if (
				itemType.includes("task") ||
				itemType.includes("code") ||
				itemType.includes("api") ||
				itemType.includes("service") ||
				itemType.includes("module")
			) {
				counts.technical++;
			}

			// UI items
			if (
				itemType.includes("ui") ||
				itemType.includes("wireframe") ||
				itemType.includes("mockup") ||
				itemType.includes("page") ||
				itemType.includes("component") ||
				itemType.includes("screen")
			) {
				counts.ui++;
			}

			// Security items
			if (itemType.includes("security") || itemType.includes("auth")) {
				counts.security++;
			}

			// Performance items
			if (itemType.includes("performance") || itemType.includes("metric")) {
				counts.performance++;
			}
		}

		return counts;
	}, [items]);

	// Get count for a view
	// Helper to count items by view type (available for future use)
	/*
	const getViewCount = useCallback(
		(config: ViewConfig): number | undefined => {
			if (config.category === "graph") return items.length;
			if (config.category === "diagram") {
				if (config.id === "components" || config.id === "page-flow") {
					return perspectiveCounts.ui;
				}
				return undefined;
			}
			if (config.perspective) {
				switch (config.perspective) {
					case "product":
						return perspectiveCounts.product;
					case "business":
						return perspectiveCounts.business;
					case "technical":
						return perspectiveCounts.technical;
					case "ui":
						return perspectiveCounts.ui;
					case "security":
						return perspectiveCounts.security;
					case "performance":
						return perspectiveCounts.performance;
					default:
						return perspectiveCounts.all;
				}
			}
			return undefined;
		},
		[items.length, perspectiveCounts],
	);
	*/

	// Get perspective from view mode
	const getPerspective = useCallback(
		(mode: GraphViewMode): GraphPerspective | null => {
			const config = VIEW_CONFIGS.find((c) => c.id === mode);
			return config?.perspective || null;
		},
		[],
	);

	// Handle view change
	const handleViewChange = useCallback((mode: GraphViewMode) => {
		setViewMode(mode);
	}, []);

	// Grouped views for sidebar and combobox
	const graphViews = VIEW_CONFIGS.filter((c) => c.category === "graph");
	const diagramViews = VIEW_CONFIGS.filter((c) => c.category === "diagram");
	const perspectiveViews = VIEW_CONFIGS.filter(
		(c) => c.category === "perspective",
	);
	// Combine graph and diagram views (available for future use)
// 	const __mainViews = [...graphViews, ...diagramViews];

	// Filter view configs by search (for combobox)
	const searchLower = viewTypeSearch.trim().toLowerCase();
	const filterViews = useCallback(
		(list: ViewConfig[]) =>
			searchLower
				? list.filter(
						(c) =>
							c.label.toLowerCase().includes(searchLower) ||
							c.description.toLowerCase().includes(searchLower),
					)
				: list,
		[searchLower],
	);
	const filteredGraphViews = filterViews(graphViews);
	const filteredDiagramViews = filterViews(diagramViews);
	const filteredPerspectiveViews = filterViews(perspectiveViews);

	// Loading state
	if (isLoading) {
		return (
			<div className="flex h-full">
				<div className="w-56 border-r p-4 space-y-2">
					<Skeleton className="h-10 w-full" />
					<Skeleton className="h-10 w-full" />
					<Skeleton className="h-10 w-full" />
				</div>
				<div className="flex-1 p-6 space-y-4">
					<Skeleton className="h-12 w-full" />
					<Skeleton className="h-[calc(100vh-200px)]" />
				</div>
			</div>
		);
	}

	return (
		<div className="flex h-full">
			{/* Sidebar */}
			<div
				className={cn(
					"border-r bg-muted/30 transition-all duration-300 flex flex-col shrink-0",
					sidebarCollapsed ? "w-12 sm:w-14" : "w-48 sm:w-52 md:w-56",
				)}
			>
				{/* Sidebar header */}
				<div className="p-2 sm:p-3 border-b flex items-center justify-between min-w-0">
					{!sidebarCollapsed && (
						<div className="flex items-center gap-1.5 min-w-0">
							<Layers className="h-4 w-4 sm:h-[1.1rem] shrink-0 text-primary" />
							<span className="font-semibold text-xs sm:text-sm truncate">Views</span>
						</div>
					)}
					<Button
						variant="ghost"
						size="sm"
						className="h-8 w-8 p-0"
						onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
					>
						{sidebarCollapsed ? (
							<ChevronRight className="h-4 w-4" />
						) : (
							<ChevronLeft className="h-4 w-4" />
						)}
					</Button>
				</div>

				{/* Sidebar content: project views (Feature, API, Test, Graph, etc.) */}
				<ScrollArea className="flex-1">
					<div className="p-2 space-y-1">
						{!sidebarCollapsed && (
							<div className="px-2 py-1.5 text-[10px] sm:text-[11px] font-medium text-muted-foreground uppercase tracking-wide truncate">
								Project views
							</div>
						)}
						{PROJECT_VIEW_NAV.map((nav) => {
							const isActive = nav.viewType === "graph";
							const Icon = nav.icon;
							if (!projectId) {
								return (
									<div
										key={nav.viewType}
										className={cn(
											"flex items-center gap-2 sm:gap-3 h-9 sm:h-10 px-2 sm:px-3 rounded-md min-w-0 w-full opacity-60",
											sidebarCollapsed && "justify-center px-2",
										)}
										title={sidebarCollapsed ? nav.label : undefined}
									>
										<Icon className="h-3.5 w-3.5 sm:h-4 sm:w-4 shrink-0" />
										{!sidebarCollapsed && (
											<span className="truncate flex-1 text-left text-xs sm:text-sm min-w-0">
												{nav.label}
											</span>
										)}
									</div>
								);
							}
							return (
								<RouterLink
									key={nav.viewType}
									to="/projects/$projectId/views/$viewType"
									params={{ projectId, viewType: nav.viewType }}
									className={cn(
										"flex items-center gap-2 sm:gap-3 h-9 sm:h-10 px-2 sm:px-3 rounded-md transition-all min-w-0 w-full",
										sidebarCollapsed && "justify-center px-2",
										isActive && "bg-primary/10 text-primary hover:bg-primary/15",
										!isActive && "hover:bg-muted/50",
									)}
									title={sidebarCollapsed ? nav.label : undefined}
								>
									<Icon className={cn("h-3.5 w-3.5 sm:h-4 sm:w-4 shrink-0", isActive && "text-primary")} />
									{!sidebarCollapsed && (
										<span className="truncate flex-1 text-left text-xs sm:text-sm min-w-0">
											{nav.label}
										</span>
									)}
								</RouterLink>
							);
						})}
					</div>
				</ScrollArea>

				{/* Sidebar footer */}
				{!sidebarCollapsed && (
					<div className="p-2 sm:p-3 border-t min-w-0">
						<div className="text-[10px] sm:text-[11px] text-muted-foreground truncate">
							{items.length} items · {links.length} links
						</div>
					</div>
				)}
			</div>

			{/* Main content area */}
			<div className="flex-1 flex flex-col overflow-hidden">
				{/* Top bar with combo box */}
				<div className="border-b p-2 sm:p-3 flex flex-wrap items-center justify-between gap-2 sm:gap-4 bg-background min-w-0">
					<div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
						{/* Graph / diagram view type combobox: searchable, many intuitive types */}
						<Select
							value={viewMode}
							onValueChange={(v) => {
								handleViewChange(v as GraphViewMode);
								setViewTypeSearch("");
							}}
						>
							<SelectTrigger
								className="w-full min-w-0 max-w-[240px] sm:max-w-[260px] md:max-w-[280px] h-8 sm:h-9 text-xs sm:text-sm [&>span]:truncate [&>span]:min-w-0"
								aria-label="Graph or diagram view type"
							>
								<SelectValue placeholder="View type" />
							</SelectTrigger>
							<SelectContent
								position="popper"
								sideOffset={4}
								className="max-h-[min(70vh,400px)]"
							>
								{/* Search filter */}
								<div
									className="p-1.5 sm:p-2 sticky top-0 bg-background z-10 border-b"
									onPointerDown={(e) => e.stopPropagation()}
								>
									<div className="relative">
										<Search className="absolute left-2 sm:left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 sm:h-4 sm:w-4 text-muted-foreground" />
										<Input
											placeholder="Search view types..."
											value={viewTypeSearch}
											onChange={(e) => setViewTypeSearch(e.target.value)}
											className="pl-7 sm:pl-8 h-7 sm:h-8 text-xs sm:text-sm"
											aria-label="Filter view types"
										/>
									</div>
								</div>
								<div className="p-1">
									<SelectGroup>
										<div className="px-2 py-1 text-[10px] sm:text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">
											Graph & diagram views
										</div>
										{filteredGraphViews.map((config) => (
											<SelectItem key={config.id} value={config.id}>
												<div className="flex items-center gap-2 min-w-0">
													<config.icon className="h-3.5 w-3.5 sm:h-4 sm:w-4 shrink-0" />
													<div className="min-w-0 flex-1">
														<span className="block truncate text-xs sm:text-sm">{config.label}</span>
														<span className="block text-[10px] sm:text-[11px] text-muted-foreground line-clamp-2">
															{config.description}
														</span>
													</div>
												</div>
											</SelectItem>
										))}
										{filteredDiagramViews.map((config) => (
											<SelectItem key={config.id} value={config.id}>
												<div className="flex items-center gap-2 min-w-0">
													<config.icon className="h-3.5 w-3.5 sm:h-4 sm:w-4 shrink-0" />
													<div className="min-w-0 flex-1">
														<span className="block truncate text-xs sm:text-sm">{config.label}</span>
														<span className="block text-[10px] sm:text-[11px] text-muted-foreground line-clamp-2">
															{config.description}
														</span>
													</div>
												</div>
											</SelectItem>
										))}
									</SelectGroup>
									<Separator className="my-1.5 sm:my-2" />
									<SelectGroup>
										<div className="px-2 py-1 text-[10px] sm:text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">
											Perspectives
										</div>
										{filteredPerspectiveViews.map((config) => (
											<SelectItem key={config.id} value={config.id}>
												<div className="flex items-center gap-2 min-w-0">
													<config.icon className="h-3.5 w-3.5 sm:h-4 sm:w-4 shrink-0" />
													<div className="min-w-0 flex-1">
														<span className="block truncate text-xs sm:text-sm">{config.label}</span>
														<span className="block text-[10px] sm:text-[11px] text-muted-foreground line-clamp-2">
															{config.description}
														</span>
													</div>
												</div>
											</SelectItem>
										))}
									</SelectGroup>
								</div>
							</SelectContent>
						</Select>

						{/* Current view info: responsive, line-clamp when narrow */}
						{currentConfig && (
							<div className="hidden sm:block min-w-0 flex-1 max-w-[40vw] md:max-w-[50vw] lg:max-w-none">
								<p className="text-xs sm:text-sm md:text-base text-muted-foreground truncate sm:line-clamp-2">
									{currentConfig.description}
								</p>
							</div>
						)}
					</div>

					{/* View badge */}
					{currentConfig?.perspective && (
						<Badge
							variant="outline"
							className="px-2 sm:px-3 py-0.5 sm:py-1 text-[10px] sm:text-xs shrink-0"
							style={{
								backgroundColor: `${
									PERSPECTIVE_CONFIGS.find(
										(c) => c.id === currentConfig.perspective,
									)?.color ?? "#64748b"
								}20`,
								borderColor:
									PERSPECTIVE_CONFIGS.find(
										(c) => c.id === currentConfig.perspective,
									)?.color ?? "#64748b",
							}}
						>
							{currentConfig.label}
						</Badge>
					)}
				</div>

				{/* View content */}
				<div className="flex-1 overflow-hidden relative">
					{children({
						viewMode,
						perspective: getPerspective(viewMode),
						layoutPreference: currentConfig?.layoutPreference,
						items,
						links,
						onNavigateToItem,
					})}

				</div>
			</div>
		</div>
	);
}
