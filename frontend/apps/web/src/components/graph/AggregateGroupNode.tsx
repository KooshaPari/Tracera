// Aggregate Group Node Component
// Renders aggregated items as a single expandable node
// Supports expanding/collapsing with animated transitions

import type { Item } from "@tracertm/types";
import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Handle, type NodeProps, Position } from "@xyflow/react";
import {
	ChevronDown,
	ChevronRight,
	Grid2X2,
	Maximize2,
	Minimize2,
} from "lucide-react";
import { memo, useCallback } from "react";
import { logger } from '@/lib/logger';
import type { AggregateGroup } from "../../utils/aggregation";
import { getTypeColor } from "./utils/typeStyles";

/**
 * Data structure for aggregate group node
 */
export interface AggregateNodeData {
	group: AggregateGroup;
	items: Item[];
	isExpanded: boolean;
	onToggle: (groupId: string) => void;
	onItemSelect?: (itemId: string) => void;
}

/**
 * Type guard to validate AggregateNodeData structure
 */
function isAggregateNodeData(data: unknown): data is AggregateNodeData {
	if (typeof data !== "object" || data === null) {
		return false;
	}

	const obj = data as Record<string, unknown>;

	// Validate group property
	if (
		typeof obj['group'] !== "object" ||
		obj['group'] === null ||
		typeof (obj['group'] as Record<string, unknown>)['id'] !== "string"
	) {
		return false;
	}

	// Validate items array
	if (!Array.isArray(obj['items'])) {
		return false;
	}

	// Validate isExpanded boolean
	if (typeof obj['isExpanded'] !== "boolean") {
		return false;
	}

	// Validate onToggle function
	if (typeof obj['onToggle'] !== "function") {
		return false;
	}

	return true;
}

/**
 * Collapsed view of aggregate group
 */
function CollapsedGroupView({
	data,
	onToggle,
}: {
	data: AggregateNodeData;
	onToggle: () => void;
}) {
	const typeColor = getTypeColor(data.group.type);

	return (
		<div
			className={cn(
				"px-4 py-3 rounded-lg border-2 bg-background",
				"hover:shadow-lg hover:border-primary/60 transition-all cursor-pointer",
				"flex items-center gap-3 min-w-[200px] max-w-[280px]",
			)}
			style={{ borderColor: `${typeColor}40` }}
			onClick={onToggle}
		>
			{/* Icon and type */}
			<div
				className="w-8 h-8 rounded-md flex items-center justify-center shrink-0"
				style={{ backgroundColor: `${typeColor}20` }}
			>
				<Grid2X2 className="w-4 h-4" style={{ color: typeColor }} />
			</div>

			{/* Text content */}
			<div className="flex-1 min-w-0">
				<div className="text-sm font-semibold truncate">{data.group.type}</div>
				<div className="text-xs text-muted-foreground truncate">
					{data.group.itemCount} items
				</div>
			</div>

			{/* Count badge */}
			<Badge
				className="shrink-0 text-white"
				style={{ backgroundColor: typeColor }}
			>
				{data.group.itemCount}
			</Badge>

			{/* Expand icon */}
			<ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
		</div>
	);
}

/**
 * Preview/expanded view of aggregate group
 */
function ExpandedGroupView({
	data,
	onToggle,
}: {
	data: AggregateNodeData;
	onToggle: () => void;
}) {
	const typeColor = getTypeColor(data.group.type);

	return (
		<Card
			className="w-[360px] overflow-hidden shadow-xl border-2"
			style={{ borderColor: typeColor }}
		>
			{/* Header */}
			<div
				className="p-4 border-b"
				style={{
					background: `linear-gradient(to right, ${typeColor}15, ${typeColor}05)`,
				}}
			>
				<div className="flex items-center justify-between mb-2">
					<div className="flex items-center gap-3 flex-1 min-w-0">
						<div
							className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
							style={{ backgroundColor: `${typeColor}25` }}
						>
							<Grid2X2 className="w-5 h-5" style={{ color: typeColor }} />
						</div>
						<div className="min-w-0">
							<h3 className="font-bold text-base capitalize truncate">
								{data.group.type}
							</h3>
							<Badge variant="outline" className="text-[10px] mt-1">
								Aggregated
							</Badge>
						</div>
					</div>
					<Button
						variant="ghost"
						size="sm"
						className="h-8 w-8 p-0 shrink-0"
						onClick={onToggle}
					>
						<Minimize2 className="w-4 h-4" />
					</Button>
				</div>
			</div>

			{/* Stats */}
			<div className="px-4 py-3 border-b bg-muted/20 grid grid-cols-3 gap-2">
				<div className="text-center">
					<div className="text-2xl font-bold" style={{ color: typeColor }}>
						{data.group.itemCount}
					</div>
					<div className="text-xs text-muted-foreground">Items</div>
				</div>
				<div className="text-center">
					<div className="text-2xl font-bold text-blue-500">
						{data.group.commonDependencies.length}
					</div>
					<div className="text-xs text-muted-foreground">Common deps</div>
				</div>
				<div className="text-center">
					<div className="text-2xl font-bold text-green-500">
						{data.group.commonDependents.length}
					</div>
					<div className="text-xs text-muted-foreground">Dependents</div>
				</div>
			</div>

			{/* Items list */}
			<div className="max-h-[300px] overflow-y-auto">
				<div className="p-3 space-y-2">
					{data.items.slice(0, 15).map((item) => (
						<div
							key={item.id}
							className={cn(
								"p-2 rounded-md border bg-card text-sm hover:bg-accent transition-colors",
								"truncate cursor-pointer text-xs",
							)}
							onClick={() => data.onItemSelect?.(item.id)}
							title={item.title}
						>
							<div className="truncate font-medium text-foreground">
								{item.title}
							</div>
							{item.description && (
								<div className="text-muted-foreground truncate text-[10px]">
									{item.description}
								</div>
							)}
						</div>
					))}
					{data.items.length > 15 && (
						<div className="p-2 text-xs text-muted-foreground text-center">
							+{data.items.length - 15} more items
						</div>
					)}
				</div>
			</div>

			{/* Footer */}
			<div className="p-3 border-t bg-muted/30 flex gap-2">
				<Button
					variant="secondary"
					size="sm"
					className="flex-1 text-xs"
					onClick={onToggle}
				>
					<ChevronDown className="w-3 h-3 mr-1" />
					Collapse
				</Button>
				<Button variant="outline" size="sm" className="flex-1 text-xs">
					<Maximize2 className="w-3 h-3 mr-1" />
					Drill down
				</Button>
			</div>
		</Card>
	);
}

/**
 * Aggregate group node component
 */
function AggregateGroupNodeComponent({ data: nodeData, selected }: NodeProps) {
	const handleToggle = useCallback(() => {
		if (isAggregateNodeData(nodeData)) nodeData.onToggle(nodeData.group.id);
	}, [nodeData]);

	if (!isAggregateNodeData(nodeData)) {
		logger.error("Invalid AggregateNodeData structure:", nodeData);
		return null;
	}

	const data = nodeData;

	return (
		<div
			className={
				cn(
					"relative transition-all",
					selected && "ring-2 ring-primary ring-offset-2 rounded-lg",
				) as string
			}
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
			{data.isExpanded ? (
				<ExpandedGroupView data={data} onToggle={handleToggle} />
			) : (
				<CollapsedGroupView data={data} onToggle={handleToggle} />
			)}
		</div>
	);
}

export const AggregateGroupNode = memo(AggregateGroupNodeComponent);
