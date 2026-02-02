// Unified Graph View - Multi-dimensional traceability visualization
// Supports multiple perspectives, dimension filtering, and equivalence display
// Implements: Single, Split, Layered, Unified, and Pivot display modes

import type {
	CanonicalConcept,
	CanonicalProjection,
	EquivalenceLink,
	Item,
	Link,
} from "@tracertm/types";
import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { ReactFlowProvider } from "@xyflow/react";
import {
	ArrowLeftRight,
	Columns2,
	Component,
	EyeOff,
	Filter,
	Focus,
	Layers,
	Layers2,
	Link2,
	Maximize2,
	Merge,
} from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";
import {
	applyDimensionFilters,
	type DimensionFilter,
	DimensionFilters,
} from "./DimensionFilters";
import { FlowGraphViewInner } from "./FlowGraphViewInner";
import { GraphViewContainer, type GraphViewMode } from "./GraphViewContainer";
import type { LayoutType } from "./layouts/useDAGLayout";
import { PageInteractionFlow } from "./PageInteractionFlow";
import { buildPivotTargets, PivotNavigation } from "./PivotNavigation";
import type { GraphPerspective } from "./types";
import { PERSPECTIVE_CONFIGS, TYPE_TO_PERSPECTIVE } from "./types";
import { UIComponentTree } from "./UIComponentTree";

// =============================================================================
// TYPES
// =============================================================================

/**
 * Multi-perspective display modes
 */
export type DisplayMode =
	| "single" // One perspective, cross-links hidden
	| "split" // Side-by-side perspectives, equivalences as bridges
	| "layered" // Perspectives as semi-transparent layers
	| "unified" // All perspectives merged, dimension-colored
	| "pivot"; // Focus on one node, show its projections in all perspectives

/**
 * Equivalence visualization modes
 */
export type EquivalenceMode =
	| "hide" // Don't show equivalence links
	| "highlight" // Show equivalence links with special styling
	| "merge"; // Merge equivalent nodes into single composite node

/**
 * Journey/trace overlay
 */
export interface DerivedJourney {
	id: string;
	name: string;
	type: "user_flow" | "data_path" | "call_chain" | "test_trace";
	nodeIds: string[];
	links: { sourceId: string; targetId: string; type: string }[];
	color?: string;
}

/**
 * Props for UnifiedGraphView
 */
interface UnifiedGraphViewProps {
	// Core data
	items: Item[];
	links: Link[];
	isLoading?: boolean;
	projectId?: string;

	// Navigation
	onNavigateToItem?: (itemId: string) => void;
	defaultView?: GraphViewMode;

	// ✅ NEW: Progressive edge loading
	canLoadMore?: boolean | undefined;
	visibleEdges?: number | undefined;
	totalEdges?: number | undefined;
	onLoadMore?: (() => void) | undefined;

	// Multi-perspective controls
	activePerspectives?: GraphPerspective[];
	displayMode?: DisplayMode;
	onDisplayModeChange?: (mode: DisplayMode) => void;

	// Dimension filtering
	dimensionFilters?: DimensionFilter[];
	onDimensionFiltersChange?: (filters: DimensionFilter[]) => void;

	// Equivalence display
	equivalenceLinks?: EquivalenceLink[];
	equivalenceMode?: EquivalenceMode;
	onEquivalenceModeChange?: (mode: EquivalenceMode) => void;

	// Canonical concepts
	canonicalConcepts?: CanonicalConcept[];
	canonicalProjections?: CanonicalProjection[];
	showCanonicalLayer?: boolean;
	onShowCanonicalLayerChange?: (show: boolean) => void;

	// Journey overlay
	activeJourney?: DerivedJourney;
	availableJourneys?: DerivedJourney[];
	onJourneyChange?: (journey: DerivedJourney | undefined) => void;

	// Pivot mode
	focusedItemId?: string;
	onFocusedItemChange?: (itemId: string | undefined) => void;
}

// =============================================================================
// DISPLAY MODE CONFIGURATION
// =============================================================================

const DISPLAY_MODE_CONFIGS: {
	id: DisplayMode;
	label: string;
	description: string;
	icon: React.ComponentType<{ className?: string }>;
}[] = [
	{
		id: "single",
		label: "Single",
		description: "One perspective at a time",
		icon: Maximize2,
	},
	{
		id: "split",
		label: "Split",
		description: "Side-by-side comparison",
		icon: Columns2,
	},
	{
		id: "layered",
		label: "Layered",
		description: "Overlapping perspectives",
		icon: Layers2,
	},
	{
		id: "unified",
		label: "Unified",
		description: "All merged with dimensions",
		icon: Merge,
	},
	{
		id: "pivot",
		label: "Pivot",
		description: "Focus on equivalences",
		icon: Focus,
	},
];

const EQUIVALENCE_MODE_CONFIGS: {
	id: EquivalenceMode;
	label: string;
	icon: React.ComponentType<{ className?: string }>;
}[] = [
	{ id: "hide", label: "Hide", icon: EyeOff },
	{ id: "highlight", label: "Highlight", icon: Link2 },
	{ id: "merge", label: "Merge", icon: Merge },
];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Filter items and links by perspective
 */
function filterByPerspective(
	items: Item[],
	links: Link[],
	perspective: GraphPerspective | null,
): { filteredItems: Item[]; filteredLinks: Link[] } {
	if (!perspective || perspective === "all") {
		return { filteredItems: items, filteredLinks: links };
	}

	const filteredItems = items.filter((item) => {
		const itemType = (item.type || item.view || "item").toLowerCase();
		const perspectives = TYPE_TO_PERSPECTIVE[itemType] || ["all"];
		return perspectives.includes(perspective);
	});

	const itemIds = new Set(filteredItems.map((i) => i.id));
	const filteredLinks = links.filter(
		(link) => itemIds.has(link.sourceId) && itemIds.has(link.targetId),
	);

	return { filteredItems, filteredLinks };
}

/**
 * Filter items by dimension criteria
 */
function filterByDimensions(
	items: Item[],
	links: Link[],
	filters: DimensionFilter[],
): { filteredItems: Item[]; filteredLinks: Link[] } {
	if (!filters || filters.length === 0) {
		return { filteredItems: items, filteredLinks: links };
	}

	const filteredItems = applyDimensionFilters(items, filters);
	const itemIds = new Set(filteredItems.map((i) => i.id));
	const filteredLinks = links.filter(
		(link) => itemIds.has(link.sourceId) && itemIds.has(link.targetId),
	);

	return { filteredItems, filteredLinks };
}

/**
 * Add equivalence links to the graph
 */
function addEquivalenceLinks(
	links: Link[],
	equivalenceLinks: EquivalenceLink[],
	mode: EquivalenceMode,
): Link[] {
	if (mode === "hide" || !equivalenceLinks || equivalenceLinks.length === 0) {
		return links;
	}

	const equivalenceLinkObjects: Link[] = equivalenceLinks.map((eq) => ({
		id: `eq-${eq.id}`,
		projectId: eq.projectId,
		sourceId: eq.sourceItemId,
		targetId: eq.targetItemId,
		type: "same_as" as const,
		version: 1,
		createdAt: eq.createdAt,
		updatedAt: eq.updatedAt,
		// Mark as equivalence link for special styling
		metadata: {
			isEquivalence: true,
			confidence: eq.confidence,
			status: eq.status,
		},
	}));

	return [...links, ...equivalenceLinkObjects];
}

/**
 * Highlight journey nodes and links
 */
function applyJourneyOverlay(
	items: Item[],
	links: Link[],
	journey: DerivedJourney | undefined,
): { items: Item[]; links: Link[]; journeyActive: boolean } {
	if (!journey) {
		return { items, links, journeyActive: false };
	}

	const journeyNodeSet = new Set(journey.nodeIds);
	const journeyLinkSet = new Set(
		journey.links.map((l) => `${l.sourceId}-${l.targetId}`),
	);

	// Mark items as part of journey
	const markedItems = items.map((item) => ({
		...item,
		metadata: {
			...item.metadata,
			_isInJourney: journeyNodeSet.has(item.id),
			_journeyColor: journey.color,
		},
	}));

	// Mark links as part of journey
	const markedLinks = links.map((link) => ({
		...link,
		metadata: {
			...link.metadata,
			_isInJourney: journeyLinkSet.has(`${link.sourceId}-${link.targetId}`),
			_journeyColor: journey.color,
		},
	}));

	return { items: markedItems, links: markedLinks, journeyActive: true };
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Display mode selector
 */
interface DisplayModeSelectorProps {
	mode: DisplayMode;
	onChange: (mode: DisplayMode) => void;
}

const DisplayModeSelector = memo(function DisplayModeSelector({
	mode,
	onChange,
}: DisplayModeSelectorProps) {
	return (
		<TooltipProvider>
			<div className="flex items-center gap-1 p-1 bg-muted rounded-lg">
				{DISPLAY_MODE_CONFIGS.map((config) => (
					<Tooltip key={config.id} delayDuration={300}>
						<TooltipTrigger asChild>
							<Button
								variant={mode === config.id ? "secondary" : "ghost"}
								size="sm"
								className={cn(
									"h-8 w-8 p-0",
									mode === config.id && "bg-background shadow-sm",
								)}
								onClick={() => onChange(config.id)}
							>
								<config.icon className="h-4 w-4" />
							</Button>
						</TooltipTrigger>
						<TooltipContent side="bottom">
							<p className="font-medium">{config.label}</p>
							<p className="text-xs text-muted-foreground">
								{config.description}
							</p>
						</TooltipContent>
					</Tooltip>
				))}
			</div>
		</TooltipProvider>
	);
});

/**
 * Equivalence mode selector
 */
interface EquivalenceModeSelectorProps {
	mode: EquivalenceMode;
	onChange: (mode: EquivalenceMode) => void;
	equivalenceCount: number;
}

const EquivalenceModeSelector = memo(function EquivalenceModeSelector({
	mode,
	onChange,
	equivalenceCount,
}: EquivalenceModeSelectorProps) {
	if (equivalenceCount === 0) {
		return null;
	}

	return (
		<div className="flex items-center gap-2">
			<span className="text-xs text-muted-foreground">Equivalences</span>
			<div className="flex items-center gap-0.5 bg-muted p-0.5 rounded-md">
				{EQUIVALENCE_MODE_CONFIGS.map((config) => (
					<Button
						key={config.id}
						variant={mode === config.id ? "secondary" : "ghost"}
						size="sm"
						className="h-6 px-2 text-xs"
						onClick={() => onChange(config.id)}
					>
						<config.icon className="h-3 w-3 mr-1" />
						{config.label}
					</Button>
				))}
			</div>
			<Badge variant="secondary" className="text-xs">
				{equivalenceCount}
			</Badge>
		</div>
	);
});

/**
 * Journey selector
 */
interface JourneySelectorProps {
	activeJourney: DerivedJourney | undefined;
	availableJourneys: DerivedJourney[];
	onChange: (journey: DerivedJourney | undefined) => void;
}

const JourneySelector = memo(function JourneySelector({
	activeJourney,
	availableJourneys,
	onChange,
}: JourneySelectorProps) {
	if (availableJourneys.length === 0) {
		return null;
	}

	return (
		<Select
			value={activeJourney?.id || "none"}
			onValueChange={(value) => {
				if (value === "none") {
					onChange(undefined);
				} else {
					onChange(availableJourneys.find((j) => j.id === value));
				}
			}}
		>
			<SelectTrigger className="w-[180px] h-8">
				<SelectValue placeholder="Select journey" />
			</SelectTrigger>
			<SelectContent>
				<SelectItem value="none">No journey overlay</SelectItem>
				{availableJourneys.map((journey) => (
					<SelectItem key={journey.id} value={journey.id}>
						<div className="flex items-center gap-2">
							{journey.color && (
								<div
									className="w-2 h-2 rounded-full"
									style={{ backgroundColor: journey.color }}
								/>
							)}
							<span>{journey.name}</span>
						</div>
					</SelectItem>
				))}
			</SelectContent>
		</Select>
	);
});

/**
 * Split view for side-by-side perspective comparison
 */
interface SplitViewProps {
	items: Item[];
	links: Link[];
	perspectives: [GraphPerspective, GraphPerspective];
	equivalenceLinks?: EquivalenceLink[];
	onNavigateToItem?: (itemId: string) => void;
}

function SplitView({
	items,
	links,
	perspectives,
	equivalenceLinks = [],
	onNavigateToItem,
}: SplitViewProps) {
	const [leftPerspective, rightPerspective] = perspectives;

	const leftData = useMemo(
		() => filterByPerspective(items, links, leftPerspective),
		[items, links, leftPerspective],
	);

	const rightData = useMemo(
		() => filterByPerspective(items, links, rightPerspective),
		[items, links, rightPerspective],
	);

	const leftConfig = PERSPECTIVE_CONFIGS.find((c) => c.id === leftPerspective);
	const rightConfig = PERSPECTIVE_CONFIGS.find(
		(c) => c.id === rightPerspective,
	);

	return (
		<div className="flex h-full gap-2 p-2">
			{/* Left perspective */}
			<div className="flex-1 border rounded-lg overflow-hidden">
				<div
					className="px-3 py-2 border-b text-sm font-medium flex items-center gap-2"
					style={{
						backgroundColor: `${leftConfig?.color}10`,
						borderColor: leftConfig?.color,
					}}
				>
					<div
						className="w-2 h-2 rounded-full"
						style={{ backgroundColor: leftConfig?.color }}
					/>
					{leftConfig?.label}
					<Badge variant="secondary" className="ml-auto text-xs">
						{leftData.filteredItems.length}
					</Badge>
				</div>
				<div className="h-[calc(100%-44px)]">
					<ReactFlowProvider>
						<FlowGraphViewInner
							items={leftData.filteredItems}
							links={leftData.filteredLinks}
							perspective={leftPerspective}
							onNavigateToItem={onNavigateToItem}
						/>
					</ReactFlowProvider>
				</div>
			</div>

			{/* Bridge links indicator */}
			<div className="flex flex-col items-center justify-center w-10">
				<div className="flex flex-col items-center gap-2">
					<ArrowLeftRight className="h-5 w-5 text-muted-foreground" />
					{equivalenceLinks.length > 0 && (
						<Badge variant="outline" className="text-[10px]">
							{equivalenceLinks.length}
						</Badge>
					)}
				</div>
			</div>

			{/* Right perspective */}
			<div className="flex-1 border rounded-lg overflow-hidden">
				<div
					className="px-3 py-2 border-b text-sm font-medium flex items-center gap-2"
					style={{
						backgroundColor: `${rightConfig?.color}10`,
						borderColor: rightConfig?.color,
					}}
				>
					<div
						className="w-2 h-2 rounded-full"
						style={{ backgroundColor: rightConfig?.color }}
					/>
					{rightConfig?.label}
					<Badge variant="secondary" className="ml-auto text-xs">
						{rightData.filteredItems.length}
					</Badge>
				</div>
				<div className="h-[calc(100%-44px)]">
					<ReactFlowProvider>
						<FlowGraphViewInner
							items={rightData.filteredItems}
							links={rightData.filteredLinks}
							perspective={rightPerspective}
							onNavigateToItem={onNavigateToItem}
						/>
					</ReactFlowProvider>
				</div>
			</div>
		</div>
	);
}

/**
 * Pivot view showing focused item and its equivalences
 */
interface PivotViewProps {
	items: Item[];
	links: Link[];
	focusedItemId: string | undefined;
	equivalenceLinks: EquivalenceLink[];
	canonicalProjections: CanonicalProjection[];
	onNavigateToItem?: (itemId: string) => void;
	onPivot: (perspectiveId: GraphPerspective, itemId: string) => void;
}

function PivotView({
	items,
	links,
	focusedItemId,
	equivalenceLinks,
	canonicalProjections,
	onNavigateToItem,
	onPivot,
}: PivotViewProps) {
	const focusedItem = useMemo(
		() => items.find((i) => i.id === focusedItemId),
		[items, focusedItemId],
	);

	const pivotTargets = useMemo(() => {
		if (!focusedItem) return [];

		const itemEquivalences = equivalenceLinks.filter(
			(eq) =>
				eq.sourceItemId === focusedItem.id ||
				eq.targetItemId === focusedItem.id,
		);

		return buildPivotTargets(
			focusedItem,
			itemEquivalences,
			canonicalProjections,
			items,
		);
	}, [focusedItem, equivalenceLinks, canonicalProjections, items]);

	const currentPerspective = useMemo(() => {
		if (!focusedItem) return "all" as GraphPerspective;
		const itemType = (
			focusedItem.type ||
			focusedItem.view ||
			"item"
		).toLowerCase();
		const perspectives = TYPE_TO_PERSPECTIVE[itemType] || ["all"];
		return perspectives[0] as GraphPerspective;
	}, [focusedItem]);

	if (!focusedItem) {
		return (
			<div className="flex items-center justify-center h-full">
				<div className="text-center p-8">
					<Focus className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
					<h3 className="text-lg font-medium mb-2">Pivot Mode</h3>
					<p className="text-sm text-muted-foreground max-w-md">
						Select an item in the graph to see its equivalences across all
						perspectives. This view helps you understand how concepts manifest
						in different views.
					</p>
				</div>
			</div>
		);
	}

	return (
		<div className="flex h-full">
			{/* Main graph view */}
			<div className="flex-1 p-4">
				<ReactFlowProvider>
					<FlowGraphViewInner
						items={items}
						links={links}
						perspective="all"
						onNavigateToItem={onNavigateToItem}
					/>
				</ReactFlowProvider>
			</div>

			{/* Pivot sidebar */}
			<div className="w-80 border-l bg-muted/30 overflow-y-auto">
				<div className="p-4 border-b">
					<h3 className="font-semibold mb-1">{focusedItem.title}</h3>
					<p className="text-sm text-muted-foreground">
						{focusedItem.type} in {currentPerspective} view
					</p>
				</div>

				<div className="p-4">
					<PivotNavigation
						currentItem={focusedItem}
						currentPerspective={currentPerspective}
						equivalentItems={pivotTargets}
						onPivot={onPivot}
						showEmpty
					/>
				</div>

				{pivotTargets.length > 0 && (
					<div className="p-4 border-t">
						<h4 className="text-sm font-medium mb-3">Equivalent Items</h4>
						<div className="space-y-2">
							{pivotTargets.slice(0, 5).map((target) => {
								const config = PERSPECTIVE_CONFIGS.find(
									(c) => c.id === target.perspectiveId,
								);
								return (
									<button
										key={target.item.id}
										type="button"
										className="w-full text-left p-2 rounded-lg border bg-background hover:bg-muted transition-colors"
										onClick={() =>
											onPivot(target.perspectiveId, target.item.id)
										}
									>
										<div className="flex items-center gap-2 mb-1">
											<div
												className="w-2 h-2 rounded-full"
												style={{ backgroundColor: config?.color }}
											/>
											<span className="text-xs text-muted-foreground">
												{config?.label}
											</span>
											<Badge
												variant="secondary"
												className="ml-auto text-[10px]"
											>
												{Math.round(target.confidence * 100)}%
											</Badge>
										</div>
										<p className="text-sm font-medium truncate">
											{target.item.title}
										</p>
									</button>
								);
							})}
						</div>
					</div>
				)}
			</div>
		</div>
	);
}

/**
 * Component library view
 */
function ComponentLibraryView({
	items,
	links,
	onNavigateToItem,
}: {
	items: Item[];
	links: Link[];
	onNavigateToItem?: (itemId: string) => void;
}) {
	return (
		<div className="h-full p-4">
			<Card className="h-full overflow-hidden">
				<div className="p-4 border-b flex items-center gap-2">
					<Component className="h-5 w-5 text-primary" />
					<h2 className="font-semibold">UI Component Library</h2>
				</div>
				<div className="h-[calc(100%-60px)]">
					<UIComponentTree
						items={items}
						links={links}
						onSelectItem={onNavigateToItem ?? (() => {})}
						selectedItemId={null}
					/>
				</div>
			</Card>
		</div>
	);
}

// =============================================================================
// MAIN VIEW RENDERER
// =============================================================================

interface ViewRendererProps {
	viewMode: GraphViewMode;
	perspective: GraphPerspective | null;
	layoutPreference?: LayoutType;
	items: Item[];
	links: Link[];
	displayMode: DisplayMode;
	equivalenceMode: EquivalenceMode;
	equivalenceLinks: EquivalenceLink[];
	activeJourney?: DerivedJourney;
	focusedItemId?: string;
	canonicalProjections: CanonicalProjection[];
	onNavigateToItem?: (itemId: string) => void;
	onPivot: (perspectiveId: GraphPerspective, itemId: string) => void;
	splitPerspectives?: [GraphPerspective, GraphPerspective];
}

function ViewRenderer({
	viewMode,
	perspective,
	layoutPreference,
	items,
	links,
	displayMode,
	equivalenceMode,
	equivalenceLinks,
	activeJourney,
	focusedItemId,
	canonicalProjections,
	onNavigateToItem,
	onPivot,
	splitPerspectives = ["product", "technical"],
}: ViewRendererProps) {
	// Apply perspective filtering
	const { filteredItems, filteredLinks } = useMemo(
		() => filterByPerspective(items, links, perspective),
		[items, links, perspective],
	);

	// Add equivalence links if in highlight mode
	const linksWithEquivalences = useMemo(
		() => addEquivalenceLinks(filteredLinks, equivalenceLinks, equivalenceMode),
		[filteredLinks, equivalenceLinks, equivalenceMode],
	);

	// Apply journey overlay
	const { items: journeyItems, links: journeyLinks } = useMemo(
		() =>
			applyJourneyOverlay(filteredItems, linksWithEquivalences, activeJourney),
		[filteredItems, linksWithEquivalences, activeJourney],
	);

	// Handle special display modes
	if (
		displayMode === "split" &&
		viewMode !== "page-flow" &&
		viewMode !== "components"
	) {
		return (
			<SplitView
				items={items}
				links={links}
				perspectives={splitPerspectives}
				equivalenceLinks={equivalenceLinks}
				onNavigateToItem={onNavigateToItem}
			/>
		);
	}

	if (
		displayMode === "pivot" &&
		viewMode !== "page-flow" &&
		viewMode !== "components"
	) {
		return (
			<PivotView
				items={items}
				links={links}
				focusedItemId={focusedItemId}
				equivalenceLinks={equivalenceLinks}
				canonicalProjections={canonicalProjections}
				onNavigateToItem={onNavigateToItem}
				onPivot={onPivot}
			/>
		);
	}

	// Render based on view mode
	switch (viewMode) {
		case "page-flow":
			return (
				<div className="h-full p-4">
					<PageInteractionFlow
						items={items}
						links={links}
						onSelectItem={onNavigateToItem}
						onPreviewItem={onNavigateToItem}
					/>
				</div>
			);

		case "components":
			return (
				<ComponentLibraryView
					items={items}
					links={links}
					onNavigateToItem={onNavigateToItem}
				/>
			);
		default:
			return (
				<div className="h-full p-4">
					<ReactFlowProvider>
						<FlowGraphViewInner
							items={journeyItems}
							links={journeyLinks}
							perspective={perspective ?? "all"}
							defaultLayout={layoutPreference}
							onNavigateToItem={onNavigateToItem}
						/>
					</ReactFlowProvider>
				</div>
			);
	}
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function UnifiedGraphView({
	items,
	links,
	isLoading = false,
	projectId,
	onNavigateToItem,
	defaultView = "traceability",

	// ✅ NEW: Progressive edge loading
	canLoadMore,
	visibleEdges,
	totalEdges,
	onLoadMore,

	// Multi-perspective controls
	displayMode: externalDisplayMode,
	onDisplayModeChange,

	// Dimension filtering
	dimensionFilters: externalFilters = [],
	onDimensionFiltersChange,

	// Equivalence display
	equivalenceLinks = [],
	equivalenceMode: externalEquivalenceMode,
	onEquivalenceModeChange,

	// Canonical concepts
	canonicalConcepts = [],
	canonicalProjections = [],
	showCanonicalLayer = false,
	onShowCanonicalLayerChange,

	// Journey overlay
	activeJourney,
	availableJourneys = [],
	onJourneyChange,

	// Pivot mode
	focusedItemId,
	onFocusedItemChange,
}: UnifiedGraphViewProps) {
	// Internal state (used if not controlled externally)
	const [internalDisplayMode, setInternalDisplayMode] =
		useState<DisplayMode>("single");
	const [internalEquivalenceMode, setInternalEquivalenceMode] =
		useState<EquivalenceMode>("hide");
	const [internalFilters, setInternalFilters] = useState<DimensionFilter[]>([]);
	const [showFilters, setShowFilters] = useState(false);
	const [splitPerspectives, setSplitPerspectives] = useState<
		[GraphPerspective, GraphPerspective]
	>(["product", "technical"]);

	// Use external or internal state
	const displayMode = externalDisplayMode ?? internalDisplayMode;
	const equivalenceMode = externalEquivalenceMode ?? internalEquivalenceMode;
	const dimensionFilters =
		externalFilters.length > 0 ? externalFilters : internalFilters;

	// Handlers
	const handleDisplayModeChange = useCallback(
		(mode: DisplayMode) => {
			if (onDisplayModeChange) {
				onDisplayModeChange(mode);
			} else {
				setInternalDisplayMode(mode);
			}
		},
		[onDisplayModeChange],
	);

	const handleEquivalenceModeChange = useCallback(
		(mode: EquivalenceMode) => {
			if (onEquivalenceModeChange) {
				onEquivalenceModeChange(mode);
			} else {
				setInternalEquivalenceMode(mode);
			}
		},
		[onEquivalenceModeChange],
	);

	const handleFiltersChange = useCallback(
		(filters: DimensionFilter[]) => {
			if (onDimensionFiltersChange) {
				onDimensionFiltersChange(filters);
			} else {
				setInternalFilters(filters);
			}
		},
		[onDimensionFiltersChange],
	);

	const handlePivot = useCallback(
		(_perspectiveId: GraphPerspective, itemId: string) => {
			if (onFocusedItemChange) {
				onFocusedItemChange(itemId);
			}
			if (onNavigateToItem) {
				onNavigateToItem(itemId);
			}
		},
		[onFocusedItemChange, onNavigateToItem],
	);

	// Apply dimension filters
	const { filteredItems, filteredLinks } = useMemo(
		() => filterByDimensions(items, links, dimensionFilters),
		[items, links, dimensionFilters],
	);

	return (
		<div className="h-[calc(100vh-120px)] flex flex-col">
			{/* Enhanced toolbar */}
			<div className="border-b px-4 py-2 flex items-center gap-4 bg-background">
				{/* Display mode selector */}
				<DisplayModeSelector
					mode={displayMode}
					onChange={handleDisplayModeChange}
				/>

				{/* Split perspective selectors (when in split mode) */}
				{displayMode === "split" && (
					<div className="flex items-center gap-2">
						<Select
							value={splitPerspectives[0]}
							onValueChange={(v) =>
								setSplitPerspectives([
									v as GraphPerspective,
									splitPerspectives[1],
								])
							}
						>
							<SelectTrigger className="w-[140px] h-8">
								<SelectValue />
							</SelectTrigger>
							<SelectContent>
								{PERSPECTIVE_CONFIGS.filter((c) => c.id !== "all").map(
									(config) => (
										<SelectItem key={config.id} value={config.id}>
											{config.label}
										</SelectItem>
									),
								)}
							</SelectContent>
						</Select>
						<span className="text-muted-foreground">vs</span>
						<Select
							value={splitPerspectives[1]}
							onValueChange={(v) =>
								setSplitPerspectives([
									splitPerspectives[0],
									v as GraphPerspective,
								])
							}
						>
							<SelectTrigger className="w-[140px] h-8">
								<SelectValue />
							</SelectTrigger>
							<SelectContent>
								{PERSPECTIVE_CONFIGS.filter((c) => c.id !== "all").map(
									(config) => (
										<SelectItem key={config.id} value={config.id}>
											{config.label}
										</SelectItem>
									),
								)}
							</SelectContent>
						</Select>
					</div>
				)}

				<div className="flex-1" />

				{/* Equivalence mode selector */}
				<EquivalenceModeSelector
					mode={equivalenceMode}
					onChange={handleEquivalenceModeChange}
					equivalenceCount={equivalenceLinks.length}
				/>

				{/* Journey selector */}
				<JourneySelector
					activeJourney={activeJourney}
					availableJourneys={availableJourneys}
					onChange={onJourneyChange ?? (() => {})}
				/>

				{/* Dimension filters toggle */}
				<Button
					variant={showFilters ? "secondary" : "ghost"}
					size="sm"
					className="h-8"
					onClick={() => setShowFilters(!showFilters)}
				>
					<Filter className="h-4 w-4 mr-2" />
					Filters
					{dimensionFilters.length > 0 && (
						<Badge variant="secondary" className="ml-2 text-xs">
							{dimensionFilters.length}
						</Badge>
					)}
				</Button>

				{/* Canonical layer toggle */}
				{canonicalConcepts.length > 0 && (
					<Button
						variant={showCanonicalLayer ? "secondary" : "ghost"}
						size="sm"
						className="h-8"
						onClick={() => onShowCanonicalLayerChange?.(!showCanonicalLayer)}
					>
						<Layers className="h-4 w-4 mr-2" />
						Canonical
					</Button>
				)}
			</div>

			{/* Dimension filters panel */}
			{showFilters && (
				<div className="border-b">
					<DimensionFilters
						activeFilters={dimensionFilters}
						onFiltersChange={handleFiltersChange}
						displayMode="filter"
						onDisplayModeChange={() => {}}
						compact
					/>
				</div>
			)}

			{/* Main content */}
			<div className="flex-1 overflow-hidden">
				<GraphViewContainer
					items={filteredItems}
					links={filteredLinks}
					isLoading={isLoading}
					projectId={projectId}
					onNavigateToItem={onNavigateToItem}
					defaultView={defaultView}
					canLoadMore={canLoadMore}
					visibleEdges={visibleEdges}
					totalEdges={totalEdges}
					onLoadMore={onLoadMore}
				>
					{({
						viewMode,
						perspective,
						layoutPreference,
						items: viewItems,
						links: viewLinks,
						onNavigateToItem,
					}) => (
						<ViewRenderer
							viewMode={viewMode}
							perspective={perspective}
							layoutPreference={layoutPreference}
							items={viewItems}
							links={viewLinks}
							displayMode={displayMode}
							equivalenceMode={equivalenceMode}
							equivalenceLinks={equivalenceLinks}
							activeJourney={activeJourney}
							focusedItemId={focusedItemId}
							canonicalProjections={canonicalProjections}
							onNavigateToItem={onNavigateToItem}
							onPivot={handlePivot}
							splitPerspectives={splitPerspectives}
						/>
					)}
				</GraphViewContainer>
			</div>
		</div>
	);
}
