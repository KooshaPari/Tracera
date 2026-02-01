// Expandable Node - Rich interactive node with progressive disclosure
// Supports: collapsed → preview → panel → full page expansion

import type { Item } from "@tracertm/types";
import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import { Separator } from "@tracertm/ui/components/Separator";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { Handle, type NodeProps, Position } from "@xyflow/react";
import {
	Bot,
	ChevronRight,
	Edit3,
	ExternalLink,
	Eye,
	Layers,
	Link2,
	Maximize2,
	Minimize2,
	MoreHorizontal,
	X,
	Zap,
} from "lucide-react";
import { memo, useCallback, useState } from "react";
import { getTypeColor, getTypeIcon } from "../utils/typeStyles";

// ============================================================================
// TYPES
// ============================================================================

export type NodeExpansionState = "collapsed" | "preview" | "panel";

export interface ExpandableNodeData {
	item: Item;
	label: string;
	type: string;
	description?: string | undefined;
	status?: string | undefined;
	priority?: string | undefined;

	// Hierarchy info
	depth?: number | undefined;
	hasChildren?: boolean | undefined;
	childCount?: number | undefined;
	parentId?: string | undefined;
	path?: string[] | undefined;

	// Preview/visual
	thumbnailUrl?: string | undefined;
	previewComponent?: string | undefined;

	// Relationships
	incomingLinks?: number | undefined;
	outgoingLinks?: number | undefined;

	// Edit capability
	canEdit?: boolean | undefined;
	editType?: "instant" | "agent_required" | "manual" | undefined;

	// State
	expansionState?: NodeExpansionState | undefined;
	isSelected?: boolean | undefined;

	// Callbacks
	onExpand?: ((nodeId: string, state: NodeExpansionState) => void) | undefined;
	onNavigate?: ((nodeId: string) => void) | undefined;
	onEdit?: ((nodeId: string) => void) | undefined;
	onViewFullPage?: ((nodeId: string) => void) | undefined;
}

// ============================================================================
// COLLAPSED NODE VIEW
// ============================================================================

interface CollapsedNodeProps {
	data: ExpandableNodeData;
	onExpand: () => void;
}

function CollapsedNodeView({ data, onExpand }: CollapsedNodeProps) {
	const TypeIcon = getTypeIcon(data.type);
	const typeColor = getTypeColor(data.type);

	return (
		<TooltipProvider>
			<Tooltip delayDuration={300}>
				<TooltipTrigger asChild>
					<div
						className={cn(
							"flex items-center gap-2 px-3 py-2 rounded-lg border-2 bg-background",
							"hover:shadow-md hover:border-primary/50 transition-all cursor-pointer",
							"min-w-[140px] max-w-[200px]",
						)}
						style={{ borderColor: `${typeColor}40` }}
						onClick={onExpand}
					>
						<div
							className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
							style={{ backgroundColor: `${typeColor}20` }}
						>
							<TypeIcon className="w-3.5 h-3.5" style={{ color: typeColor }} />
						</div>
						<span className="text-sm font-medium truncate flex-1">
							{data.label}
						</span>
						{data.childCount && data.childCount > 0 && (
							<Badge
								variant="secondary"
								className="text-[10px] px-1.5 h-5 shrink-0"
							>
								{data.childCount}
							</Badge>
						)}
						<ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
					</div>
				</TooltipTrigger>
				<TooltipContent side="right" className="max-w-[280px]">
					<div className="space-y-2">
						<div className="flex items-center gap-2">
							<TypeIcon className="w-4 h-4" style={{ color: typeColor }} />
							<span className="font-semibold">{data.label}</span>
						</div>
						<Badge variant="outline" className="text-xs">
							{data.type}
						</Badge>
						{data.description && (
							<p className="text-xs text-muted-foreground line-clamp-2">
								{data.description}
							</p>
						)}
						<div className="flex items-center gap-3 text-xs text-muted-foreground">
							{data.childCount !== undefined && data.childCount > 0 && (
								<span className="flex items-center gap-1">
									<Layers className="w-3 h-3" /> {data.childCount} children
								</span>
							)}
							{(data.incomingLinks || data.outgoingLinks) && (
								<span className="flex items-center gap-1">
									<Link2 className="w-3 h-3" />{" "}
									{(data.incomingLinks ?? 0) + (data.outgoingLinks ?? 0)} links
								</span>
							)}
						</div>
					</div>
				</TooltipContent>
			</Tooltip>
		</TooltipProvider>
	);
}

// ============================================================================
// PREVIEW NODE VIEW
// ============================================================================

interface PreviewNodeProps {
	data: ExpandableNodeData;
	onCollapse: () => void;
	onExpandMore: () => void;
	onViewFullPage: () => void;
}

function PreviewNodeView({
	data,
	onCollapse,
	onExpandMore,
	onViewFullPage,
}: PreviewNodeProps) {
	const TypeIcon = getTypeIcon(data.type);
	const typeColor = getTypeColor(data.type);

	return (
		<Card
			className="w-[280px] overflow-hidden shadow-lg border-2"
			style={{ borderColor: `${typeColor}60` }}
		>
			{/* Header */}
			<div className="p-3 border-b bg-muted/30">
				<div className="flex items-center justify-between">
					<div className="flex items-center gap-2 min-w-0">
						<div
							className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
							style={{ backgroundColor: `${typeColor}20` }}
						>
							<TypeIcon className="w-4 h-4" style={{ color: typeColor }} />
						</div>
						<div className="min-w-0">
							<h4 className="font-semibold text-sm truncate">{data.label}</h4>
							<Badge variant="outline" className="text-[10px] mt-0.5">
								{data.type}
							</Badge>
						</div>
					</div>
					<div className="flex items-center gap-1 shrink-0">
						<Button
							variant="ghost"
							size="sm"
							className="h-7 w-7 p-0"
							onClick={onExpandMore}
							title="Expand to panel"
						>
							<Maximize2 className="w-3.5 h-3.5" />
						</Button>
						<Button
							variant="ghost"
							size="sm"
							className="h-7 w-7 p-0"
							onClick={onCollapse}
							title="Collapse"
						>
							<X className="w-3.5 h-3.5" />
						</Button>
					</div>
				</div>
			</div>

			{/* Preview image/thumbnail */}
			{data.thumbnailUrl && (
				<div className="relative h-24 bg-muted/50 overflow-hidden">
					<img
						src={data.thumbnailUrl}
						alt={data.label}
						className="w-full h-full object-cover"
					/>
					<div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
				</div>
			)}

			{/* Content */}
			<div className="p-3 space-y-2">
				{data.description && (
					<p className="text-xs text-muted-foreground line-clamp-2">
						{data.description}
					</p>
				)}

				{/* Stats row */}
				<div className="flex items-center gap-3 text-xs text-muted-foreground">
					{data.status && (
						<Badge variant="secondary" className="text-[10px]">
							{data.status}
						</Badge>
					)}
					{data.childCount !== undefined && data.childCount > 0 && (
						<span className="flex items-center gap-1">
							<Layers className="w-3 h-3" /> {data.childCount}
						</span>
					)}
					{(data.incomingLinks !== undefined ||
						data.outgoingLinks !== undefined) && (
						<span className="flex items-center gap-1">
							<Link2 className="w-3 h-3" />{" "}
							{(data.incomingLinks ?? 0) + (data.outgoingLinks ?? 0)}
						</span>
					)}
				</div>

				{/* Actions */}
				<div className="flex items-center gap-2 pt-1">
					<Button
						variant="outline"
						size="sm"
						className="h-7 text-xs flex-1"
						onClick={onViewFullPage}
					>
						<ExternalLink className="w-3 h-3 mr-1" />
						Open
					</Button>
					{data.hasChildren && (
						<Button
							variant="secondary"
							size="sm"
							className="h-7 text-xs"
							onClick={onExpandMore}
						>
							<Eye className="w-3 h-3 mr-1" />
							Drill down
						</Button>
					)}
				</div>
			</div>
		</Card>
	);
}

// ============================================================================
// PANEL NODE VIEW (CONTROL PANEL)
// ============================================================================

interface PanelNodeProps {
	data: ExpandableNodeData;
	onCollapse: () => void;
	onMinimize: () => void;
	onViewFullPage: () => void;
	onEdit: () => void;
}

function PanelNodeView({
	data,
	onCollapse,
	onMinimize,
	onViewFullPage,
	onEdit,
}: PanelNodeProps) {
	const TypeIcon = getTypeIcon(data.type);
	const typeColor = getTypeColor(data.type);

	return (
		<Card
			className="w-[360px] overflow-hidden shadow-xl border-2"
			style={{ borderColor: typeColor }}
		>
			{/* Header with gradient */}
			<div
				className="p-4 border-b"
				style={{
					background: `linear-gradient(to right, ${typeColor}10, ${typeColor}05)`,
				}}
			>
				<div className="flex items-center justify-between mb-2">
					<div className="flex items-center gap-3">
						<div
							className="w-10 h-10 rounded-lg flex items-center justify-center"
							style={{
								backgroundColor: `${typeColor}20`,
								border: `2px solid ${typeColor}40`,
							}}
						>
							<TypeIcon className="w-5 h-5" style={{ color: typeColor }} />
						</div>
						<div>
							<h3 className="font-bold text-base">{data.label}</h3>
							<div className="flex items-center gap-2 mt-0.5">
								<Badge
									style={{
										backgroundColor: `${typeColor}20`,
										color: typeColor,
									}}
								>
									{data.type}
								</Badge>
								{data.status && (
									<Badge variant="outline" className="text-xs">
										{data.status}
									</Badge>
								)}
							</div>
						</div>
					</div>
					<div className="flex items-center gap-1">
						<Button
							variant="ghost"
							size="sm"
							className="h-8 w-8 p-0"
							onClick={onMinimize}
						>
							<Minimize2 className="w-4 h-4" />
						</Button>
						<Button
							variant="ghost"
							size="sm"
							className="h-8 w-8 p-0"
							onClick={onCollapse}
						>
							<X className="w-4 h-4" />
						</Button>
					</div>
				</div>

				{/* Breadcrumb path */}
				{data.path && data.path.length > 0 && (
					<div className="flex items-center gap-1 text-xs text-muted-foreground overflow-x-auto">
						{data.path.slice(-3).map((segment, i) => (
							<span key={segment} className="flex items-center gap-1">
								{i > 0 && <ChevronRight className="w-3 h-3" />}
								<span className="truncate max-w-[80px]">{segment}</span>
							</span>
						))}
					</div>
				)}
			</div>

			{/* Preview area */}
			{data.thumbnailUrl ? (
				<div className="relative h-32 bg-muted/30 overflow-hidden">
					<img
						src={data.thumbnailUrl}
						alt={data.label}
						className="w-full h-full object-cover"
					/>
					<Button
						variant="secondary"
						size="sm"
						className="absolute bottom-2 right-2 h-7"
						onClick={onViewFullPage}
					>
						<Maximize2 className="w-3 h-3 mr-1" />
						Full view
					</Button>
				</div>
			) : (
				<div className="h-20 bg-muted/30 flex items-center justify-center">
					<TypeIcon className="w-8 h-8 text-muted-foreground/30" />
				</div>
			)}

			{/* Content */}
			<ScrollArea className="h-[200px]">
				<div className="p-4 space-y-4">
					{/* Description */}
					{data.description && (
						<div>
							<h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
								Description
							</h4>
							<p className="text-sm">{data.description}</p>
						</div>
					)}

					<Separator />

					{/* Stats grid */}
					<div className="grid grid-cols-2 gap-3">
						<div className="bg-muted/30 rounded-lg p-2.5">
							<div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
								<Layers className="w-3.5 h-3.5" />
								Children
							</div>
							<div className="text-lg font-bold">{data.childCount ?? 0}</div>
						</div>
						<div className="bg-muted/30 rounded-lg p-2.5">
							<div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
								<Link2 className="w-3.5 h-3.5" />
								Links
							</div>
							<div className="text-lg font-bold">
								{(data.incomingLinks ?? 0) + (data.outgoingLinks ?? 0)}
							</div>
						</div>
					</div>

					{/* Hierarchy info */}
					{data.depth !== undefined && (
						<div className="flex items-center justify-between text-sm">
							<span className="text-muted-foreground">Depth level</span>
							<Badge variant="outline">{data.depth}</Badge>
						</div>
					)}

					{/* Edit capability */}
					{data.canEdit && (
						<div className="bg-primary/5 rounded-lg p-3 border border-primary/20">
							<div className="flex items-center gap-2 mb-2">
								{data.editType === "instant" ? (
									<Zap className="w-4 h-4 text-primary" />
								) : data.editType === "agent_required" ? (
									<Bot className="w-4 h-4 text-primary" />
								) : (
									<Edit3 className="w-4 h-4 text-primary" />
								)}
								<span className="text-sm font-medium">
									{data.editType === "instant"
										? "Instant edit available"
										: data.editType === "agent_required"
											? "Agent-assisted edit"
											: "Manual edit"}
								</span>
							</div>
							<p className="text-xs text-muted-foreground">
								{data.editType === "instant"
									? "Changes apply immediately via automation"
									: data.editType === "agent_required"
										? "An AI agent will help implement changes"
										: "Edit manually in the full editor"}
							</p>
						</div>
					)}
				</div>
			</ScrollArea>

			{/* Actions footer */}
			<div className="p-3 border-t bg-muted/20 flex items-center gap-2">
				<Button
					variant="default"
					size="sm"
					className="flex-1"
					onClick={onViewFullPage}
				>
					<ExternalLink className="w-4 h-4 mr-1.5" />
					Open full page
				</Button>
				{data.canEdit && (
					<Button variant="secondary" size="sm" onClick={onEdit}>
						{data.editType === "instant" ? (
							<Zap className="w-4 h-4" />
						) : data.editType === "agent_required" ? (
							<Bot className="w-4 h-4" />
						) : (
							<Edit3 className="w-4 h-4" />
						)}
					</Button>
				)}
				<Button variant="ghost" size="sm" className="w-9 h-9 p-0">
					<MoreHorizontal className="w-4 h-4" />
				</Button>
			</div>
		</Card>
	);
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard to validate ExpandableNodeData structure
 */
function isExpandableNodeData(data: unknown): data is ExpandableNodeData {
	if (typeof data !== "object" || data === null) {
		return false;
	}

	const obj = data as Record<string, unknown>;

	// Required properties
	if (
		typeof obj.item !== "object" ||
		obj.item === null ||
		typeof (obj.item as Record<string, unknown>).id !== "string"
	) {
		return false;
	}

	if (typeof obj.label !== "string") {
		return false;
	}

	if (typeof obj.type !== "string") {
		return false;
	}

	return true;
}

// ============================================================================
// MAIN EXPANDABLE NODE
// ============================================================================

function ExpandableNodeInner({
	data,
	selected,
}: {
	data: ExpandableNodeData;
	selected: boolean;
}) {
	const [expansionState, setExpansionState] = useState<NodeExpansionState>(
		data.expansionState ?? "collapsed",
	);

	const handleExpand = useCallback(() => {
		setExpansionState("preview");
		data.onExpand?.(data.item.id, "preview");
	}, [data]);

	const handleExpandMore = useCallback(() => {
		setExpansionState("panel");
		data.onExpand?.(data.item.id, "panel");
	}, [data]);

	const handleCollapse = useCallback(() => {
		setExpansionState("collapsed");
		data.onExpand?.(data.item.id, "collapsed");
	}, [data]);

	const handleMinimize = useCallback(() => {
		setExpansionState("preview");
		data.onExpand?.(data.item.id, "preview");
	}, [data]);

	const handleViewFullPage = useCallback(() => {
		data.onViewFullPage?.(data.item.id);
	}, [data]);

	const handleEdit = useCallback(() => {
		data.onEdit?.(data.item.id);
	}, [data]);

	return (
		<div
			className={cn(
				"relative",
				selected && "ring-2 ring-primary ring-offset-2 rounded-lg",
			)}
		>
			{/* Connection handles */}
			<Handle
				type="target"
				position={Position.Left}
				className="!w-3 !h-3 !bg-primary !border-2 !border-background"
			/>
			<Handle
				type="source"
				position={Position.Right}
				className="!w-3 !h-3 !bg-primary !border-2 !border-background"
			/>

			{/* Render based on expansion state */}
			{expansionState === "collapsed" && (
				<CollapsedNodeView data={data} onExpand={handleExpand} />
			)}

			{expansionState === "preview" && (
				<PreviewNodeView
					data={data}
					onCollapse={handleCollapse}
					onExpandMore={handleExpandMore}
					onViewFullPage={handleViewFullPage}
				/>
			)}

			{expansionState === "panel" && (
				<PanelNodeView
					data={data}
					onCollapse={handleCollapse}
					onMinimize={handleMinimize}
					onViewFullPage={handleViewFullPage}
					onEdit={handleEdit}
				/>
			)}
		</div>
	);
}

function ExpandableNodeComponent({ data: nodeData, selected }: NodeProps) {
	if (!isExpandableNodeData(nodeData)) {
		logger.error("Invalid ExpandableNodeData structure:", nodeData);
		return null;
	}
	return <ExpandableNodeInner data={nodeData} selected={selected} />;
}

export const ExpandableNode = memo(ExpandableNodeComponent);
