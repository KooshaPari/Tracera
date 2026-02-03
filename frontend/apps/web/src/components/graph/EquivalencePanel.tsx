// EquivalencePanel.tsx - Display and manage equivalence relationships
// Shows how items in different perspectives relate to the same canonical concept

import type {
	CanonicalConcept,
	CanonicalProjection,
	EquivalenceLink,
	EquivalenceStrategy,
	Item,
} from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@tracertm/ui/components/Card";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import { Separator } from "@tracertm/ui/components/Separator";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import {
	ArrowLeftRight,
	Check,
	CheckCircle2,
	ChevronDown,
	ChevronRight,
	Eye,
	GitBranch,
	Link2,
	Sparkles,
	X,
} from "lucide-react";
import { memo, useState } from "react";
import { PERSPECTIVE_CONFIGS } from "./types";

// =============================================================================
// TYPES
// =============================================================================

export interface EquivalencePanelProps {
	/** The currently selected item */
	selectedItem: Item | null;
	/** Equivalence links for the selected item */
	equivalenceLinks: EquivalenceLink[];
	/** Canonical concept if the item is part of one */
	canonicalConcept?: CanonicalConcept;
	/** All projections of the canonical concept */
	projections?: CanonicalProjection[];
	/** All items (for looking up projection details) */
	items: Item[];
	/** Callback when user wants to view an equivalent item */
	onViewItem: (itemId: string) => void;
	/** Callback when user confirms a suggested equivalence */
	onConfirmEquivalence?: (linkId: string) => void;
	/** Callback when user rejects a suggested equivalence */
	onRejectEquivalence?: (linkId: string, reason?: string) => void;
	/** Callback to create a new equivalence link */
	onCreateEquivalence?: (sourceId: string, targetId: string) => void;
	/** Whether equivalence suggestions are loading */
	isLoading?: boolean;
}

interface EquivalenceItemDisplay {
	item: Item;
	link?: EquivalenceLink;
	projection?: CanonicalProjection;
	confidence: number;
	strategy?: EquivalenceStrategy;
	status: "confirmed" | "suggested" | "rejected" | "auto_confirmed";
	perspectiveId: string;
	perspectiveColor: string;
	perspectiveLabel: string;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const STRATEGY_LABELS: Record<EquivalenceStrategy, string> = {
	api_contract: "API Contract",
	co_occurrence: "Co-occurrence",
	explicit_annotation: "Explicit Annotation",
	manual_link: "Manual Link",
	naming_pattern: "Naming Pattern",
	semantic_similarity: "Semantic Similarity",
	shared_canonical: "Shared Concept",
	structural: "Structural",
	temporal: "Temporal",
};

// Strategy icons mapping (available for future icon support)
// Const STRATEGY_ICONS: Record<EquivalenceStrategy, string> = {
// 	Explicit_annotation: "annotation",
// 	Manual_link: "link",
// 	Api_contract: "api",
// 	Shared_canonical: "concept",
// 	Naming_pattern: "naming",
// 	Semantic_similarity: "semantic",
// 	Structural: "structural",
// 	Temporal: "temporal",
// 	Co_occurrence: "co-occurrence",
// };

// =============================================================================
// COMPONENT
// =============================================================================

function EquivalencePanelComponent({
	selectedItem,
	equivalenceLinks,
	canonicalConcept,
	projections = [],
	items,
	onViewItem,
	onConfirmEquivalence,
	onRejectEquivalence,
	onCreateEquivalence: _onCreateEquivalence,
	isLoading = false,
}: EquivalencePanelProps) {
	const [isExpanded, setIsExpanded] = useState(true);
	const [showSuggestions, setShowSuggestions] = useState(true);

	// Build display items from equivalence links and projections
	const equivalenceItems = buildEquivalenceItems(
		selectedItem,
		equivalenceLinks,
		projections,
		items,
	);

	const confirmedItems = equivalenceItems.filter(
		(e) => e.status === "confirmed" || e.status === "auto_confirmed",
	);
	const suggestedItems = equivalenceItems.filter(
		(e) => e.status === "suggested",
	);

	if (!selectedItem) {
		return (
			<Card className="border-dashed">
				<CardContent className="py-8 text-center text-muted-foreground">
					<Link2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
					<p className="text-sm">Select an item to view its equivalences</p>
				</CardContent>
			</Card>
		);
	}

	return (
		<TooltipProvider>
			<Card>
				<CardHeader className="py-3 px-4">
					<div className="flex items-center justify-between">
						<div className="flex items-center gap-2">
							<Button
								variant="ghost"
								size="sm"
								className="h-6 w-6 p-0"
								onClick={() => setIsExpanded(!isExpanded)}
							>
								{isExpanded ? (
									<ChevronDown className="h-4 w-4" />
								) : (
									<ChevronRight className="h-4 w-4" />
								)}
							</Button>
							<ArrowLeftRight className="h-4 w-4 text-muted-foreground" />
							<CardTitle className="text-sm font-medium">
								Equivalences
							</CardTitle>
							{equivalenceItems.length > 0 && (
								<Badge variant="secondary" className="text-xs">
									{equivalenceItems.length}
								</Badge>
							)}
						</div>
						{canonicalConcept && (
							<Tooltip delayDuration={200}>
								<TooltipTrigger>
									<Badge variant="outline" className="gap-1 text-xs">
										<GitBranch className="h-3 w-3" />
										{canonicalConcept.name}
									</Badge>
								</TooltipTrigger>
								<TooltipContent side="left" className="max-w-xs">
									<p className="font-medium">Canonical Concept</p>
									<p className="text-xs text-muted-foreground">
										{canonicalConcept.description ||
											"This item is part of a canonical concept that spans multiple perspectives."}
									</p>
								</TooltipContent>
							</Tooltip>
						)}
					</div>
				</CardHeader>

				{isExpanded && (
					<CardContent className="pt-0 px-4 pb-4">
						{isLoading ? (
							<div className="flex items-center justify-center py-8">
								<div className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full" />
							</div>
						) : (equivalenceItems.length === 0 ? (
							<div className="text-center py-6 text-muted-foreground">
								<Link2 className="h-6 w-6 mx-auto mb-2 opacity-50" />
								<p className="text-sm">No equivalences found</p>
								<p className="text-xs mt-1">
									This item doesn&apos;t have known equivalents in other
									perspectives
								</p>
							</div>
						) : (
							<ScrollArea className="max-h-[400px]">
								<div className="space-y-3">
									{/* Confirmed equivalences */}
									{confirmedItems.length > 0 && (
										<div className="space-y-2">
											<div className="flex items-center gap-2 text-xs text-muted-foreground">
												<CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
												<span>Confirmed ({confirmedItems.length})</span>
											</div>
											{confirmedItems.map((eq) => (
												<EquivalenceItemCard
													key={eq.item.id}
													equivalence={eq}
													onViewItem={onViewItem}
												/>
											))}
										</div>
									)}

									{/* Suggested equivalences */}
									{suggestedItems.length > 0 && (
										<>
											{confirmedItems.length > 0 && <Separator />}
											<div className="space-y-2">
												<div className="flex items-center justify-between">
													<div className="flex items-center gap-2 text-xs text-muted-foreground">
														<Sparkles className="h-3.5 w-3.5 text-amber-500" />
														<span>Suggested ({suggestedItems.length})</span>
													</div>
													<Button
														variant="ghost"
														size="sm"
														className="h-6 px-2 text-xs"
														onClick={() => setShowSuggestions(!showSuggestions)}
													>
														{showSuggestions ? (
															<>
																<Eye className="h-3 w-3 mr-1" />
																Hide
															</>
														) : (
															<>
																<Eye className="h-3 w-3 mr-1" />
																Show
															</>
														)}
													</Button>
												</div>
												{showSuggestions &&
													suggestedItems.map((eq) => (
														<EquivalenceItemCard
															key={eq.item.id}
															equivalence={eq}
															onViewItem={onViewItem}
															onConfirm={
																onConfirmEquivalence && eq.link
																	? () => onConfirmEquivalence(eq.link!.id)
																	: undefined
															}
															onReject={
																onRejectEquivalence && eq.link
																	? () => onRejectEquivalence(eq.link!.id)
																	: undefined
															}
															showActions
														/>
													))}
											</div>
										</>
									)}
								</div>
							</ScrollArea>
						))}
					</CardContent>
				)}
			</Card>
		</TooltipProvider>
	);
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface EquivalenceItemCardProps {
	equivalence: EquivalenceItemDisplay;
	onViewItem: (itemId: string) => void;
	onConfirm?: () => void;
	onReject?: () => void;
	showActions?: boolean;
}

function EquivalenceItemCard({
	equivalence,
	onViewItem,
	onConfirm,
	onReject,
	showActions = false,
}: EquivalenceItemCardProps) {
	const {
		item,
		confidence,
		strategy,
		perspectiveColor,
		perspectiveLabel,
		status,
	} = equivalence;

	return (
		<div
			className="group relative flex items-start gap-3 p-2.5 rounded-lg border bg-card hover:bg-accent/50 cursor-pointer transition-colors"
			onClick={() => onViewItem(item.id)}
		>
			{/* Perspective indicator */}
			<div
				className="w-1 h-full min-h-[40px] rounded-full shrink-0"
				style={{ backgroundColor: perspectiveColor }}
			/>

			{/* Content */}
			<div className="flex-1 min-w-0">
				<div className="flex items-start justify-between gap-2">
					<div className="flex-1 min-w-0">
						<p className="text-sm font-medium truncate">{item.title}</p>
						<div className="flex items-center gap-2 mt-0.5">
							<Badge
								variant="outline"
								className="text-[10px] px-1.5 py-0"
								style={{
									borderColor: perspectiveColor,
									color: perspectiveColor,
								}}
							>
								{perspectiveLabel}
							</Badge>
							<span className="text-xs text-muted-foreground capitalize">
								{item.type}
							</span>
						</div>
					</div>

					{/* Confidence indicator */}
					<ConfidenceBadge confidence={confidence} strategy={strategy} />
				</div>

				{/* Strategy explanation */}
				{strategy && (
					<p className="text-xs text-muted-foreground mt-1.5 line-clamp-1">
						Detected via {STRATEGY_LABELS[strategy].toLowerCase()}
					</p>
				)}
			</div>

			{/* Actions for suggested items */}
			{showActions && status === "suggested" && (
				<div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
					{onConfirm && (
						<Tooltip delayDuration={200}>
							<TooltipTrigger asChild>
								<Button
									variant="ghost"
									size="sm"
									className="h-7 w-7 p-0 text-green-600 hover:text-green-700 hover:bg-green-100"
									onClick={(e) => {
										e.stopPropagation();
										onConfirm();
									}}
								>
									<Check className="h-4 w-4" />
								</Button>
							</TooltipTrigger>
							<TooltipContent>Confirm equivalence</TooltipContent>
						</Tooltip>
					)}
					{onReject && (
						<Tooltip delayDuration={200}>
							<TooltipTrigger asChild>
								<Button
									variant="ghost"
									size="sm"
									className="h-7 w-7 p-0 text-red-600 hover:text-red-700 hover:bg-red-100"
									onClick={(e) => {
										e.stopPropagation();
										onReject();
									}}
								>
									<X className="h-4 w-4" />
								</Button>
							</TooltipTrigger>
							<TooltipContent>Reject equivalence</TooltipContent>
						</Tooltip>
					)}
				</div>
			)}
		</div>
	);
}

interface ConfidenceBadgeProps {
	confidence: number;
	strategy?: EquivalenceStrategy;
}

function getConfidenceColor(conf: number): string {
	if (conf >= 0.9) {
		return "text-green-600 bg-green-100";
	}
	if (conf >= 0.7) {
		return "text-amber-600 bg-amber-100";
	}
	if (conf >= 0.5) {
		return "text-orange-600 bg-orange-100";
	}
	return "text-red-600 bg-red-100";
}

function getConfidenceLabel(conf: number): string {
	if (conf >= 0.9) {
		return "High";
	}
	if (conf >= 0.7) {
		return "Medium";
	}
	if (conf >= 0.5) {
		return "Low";
	}
	return "Very Low";
}

function ConfidenceBadge({ confidence, strategy }: ConfidenceBadgeProps) {
	return (
		<Tooltip delayDuration={200}>
			<TooltipTrigger>
				<Badge
					variant="secondary"
					className={`text-[10px] px-1.5 py-0 ${getConfidenceColor(confidence)}`}
				>
					{Math.round(confidence * 100)}%
				</Badge>
			</TooltipTrigger>
			<TooltipContent side="left">
				<div className="space-y-1">
					<p className="font-medium">
						{getConfidenceLabel(confidence)} Confidence
					</p>
					{strategy && (
						<p className="text-xs text-muted-foreground">
							Detected via: {STRATEGY_LABELS[strategy]}
						</p>
					)}
				</div>
			</TooltipContent>
		</Tooltip>
	);
}

// =============================================================================
// UTILITIES
// =============================================================================

function buildEquivalenceItems(
	selectedItem: Item | null,
	equivalenceLinks: EquivalenceLink[],
	projections: CanonicalProjection[],
	items: Item[],
): EquivalenceItemDisplay[] {
	if (!selectedItem) {
		return [];
	}

	const itemsMap = new Map(items.map((i) => [i.id, i]));
	const results: EquivalenceItemDisplay[] = [];
	const seenIds = new Set<string>();

	// Add items from equivalence links
	for (const link of equivalenceLinks) {
		const targetId =
			link.sourceItemId === selectedItem.id
				? link.targetItemId
				: link.sourceItemId;
		if (seenIds.has(targetId)) {
			continue;
		}
		seenIds.add(targetId);

		const item = itemsMap.get(targetId);
		if (!item) {
			continue;
		}

		const perspective = getPerspectiveForItem(item);

		results.push({
			confidence: link.confidence,
			item,
			link,
			perspectiveColor: perspective.color,
			perspectiveId: perspective.id,
			perspectiveLabel: perspective.label,
			status: link.status,
			strategy: link.strategies[0]?.strategy,
		});
	}

	// Add items from canonical projections
	for (const projection of projections) {
		if (projection.itemId === selectedItem.id) {
			continue;
		}
		if (seenIds.has(projection.itemId)) {
			continue;
		}
		seenIds.add(projection.itemId);

		const item = itemsMap.get(projection.itemId);
		if (!item) {
			continue;
		}

		const perspective =
			PERSPECTIVE_CONFIGS.find((p) => p.id === projection.perspective) ||
			getPerspectiveForItem(item);

		results.push({
			confidence: projection.confidence,
			item,
			perspectiveColor: perspective.color,
			perspectiveId: perspective.id,
			perspectiveLabel: perspective.label,
			projection,
			status: projection.isConfirmed
				? "confirmed"
				: (projection.isRejected
					? "rejected"
					: "suggested"),
			strategy: projection.strategy,
		});
	}

	// Sort by confidence descending
	return results.toSorted((a, b) => b.confidence - a.confidence);
}

function getPerspectiveForItem(item: Item): {
	id: string;
	color: string;
	label: string;
} {
	// Check item's perspective field first
	if (item.perspective) {
		const config = PERSPECTIVE_CONFIGS.find((p) => p.id === item.perspective);
		if (config) {
			return { color: config.color, id: config.id, label: config.label };
		}
	}

	// Fall back to type-based lookup
	const itemType = item.type.toLowerCase();

	// Technical types
	if (
		["api", "database", "code", "architecture", "infrastructure"].includes(
			itemType,
		)
	) {
		const config = PERSPECTIVE_CONFIGS.find((p) => p.id === "technical");
		return config
			? { color: config.color, id: config.id, label: config.label }
			: { color: "#22c55e", id: "technical", label: "Technical" };
	}

	// UI types
	if (
		[
			"wireframe",
			"ui_component",
			"page",
			"component",
			"layout",
			"section",
		].includes(itemType)
	) {
		const config = PERSPECTIVE_CONFIGS.find((p) => p.id === "ui");
		return config
			? { color: config.color, id: config.id, label: config.label }
			: { color: "#ec4899", id: "ui", label: "UI" };
	}

	// Product types
	if (
		["requirement", "feature", "user_story", "story", "journey"].includes(
			itemType,
		)
	) {
		const config = PERSPECTIVE_CONFIGS.find((p) => p.id === "product");
		return config
			? { color: config.color, id: config.id, label: config.label }
			: { color: "#9333ea", id: "product", label: "Product" };
	}

	// Business types
	if (["epic", "task", "bug"].includes(itemType)) {
		const config = PERSPECTIVE_CONFIGS.find((p) => p.id === "business");
		return config
			? { color: config.color, id: config.id, label: config.label }
			: { color: "#3b82f6", id: "business", label: "Business" };
	}

	// Security types
	if (["security", "vulnerability", "audit"].includes(itemType)) {
		const config = PERSPECTIVE_CONFIGS.find((p) => p.id === "security");
		return config
			? { color: config.color, id: config.id, label: config.label }
			: { color: "#ef4444", id: "security", label: "Security" };
	}

	// Default
	return { color: "#64748b", id: "all", label: "All" };
}

// =============================================================================
// EXPORTS
// =============================================================================

export const EquivalencePanel = memo(EquivalencePanelComponent);
