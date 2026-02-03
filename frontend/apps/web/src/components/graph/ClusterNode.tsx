/**
 * Cluster Node Component
 *
 * Specialized visualization for clustered nodes in large graphs.
 * Supports hierarchical expansion/collapse and visual cluster metrics.
 */

import type { Item, Link } from "@tracertm/types";
import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";
import {
	ChevronDown,
	ChevronRight,
	Layers,
	Maximize2,
	Minimize2,
	Network,
} from "lucide-react";
import { memo, useCallback, useMemo } from "react";
import type { ClusterNode as ClusterNodeType } from "../../lib/graphClustering";
import { getTypeColor } from "./utils/typeStyles";
import { logger } from "@/lib/logger";

/**
 * Data structure for cluster node
 */
export interface ClusterNodeData {
	cluster: ClusterNodeType;
	items: Item[];
	links: Link[];
	isExpanded: boolean;
	level: number;
	onToggle: (clusterId: string) => void;
	onDrillDown?: (clusterId: string) => void;
	onItemSelect?: (itemId: string) => void;
}

/**
 * Type guard for ClusterNodeData
 */
function isClusterNodeData(data: unknown): data is ClusterNodeData {
	if (typeof data !== "object" || data === null) {
		return false;
	}

	const obj = data as Record<string, unknown>;

	// Validate cluster property
	if (
		typeof obj["cluster"] !== "object" ||
		obj["cluster"] === null ||
		typeof (obj["cluster"] as Record<string, unknown>)["id"] !== "string"
	) {
		return false;
	}

	// Validate isExpanded boolean
	if (typeof obj["isExpanded"] !== "boolean") {
		return false;
	}

	// Validate onToggle function
	if (typeof obj["onToggle"] !== "function") {
		return false;
	}

	return true;
}

/**
 * Calculate cluster visual size based on node count
 */
function getClusterSize(nodeCount: number): { width: number; height: number } {
	const baseSize = 80;
	const scaleFactor = Math.log10(nodeCount + 1) * 20;
	const size = Math.min(baseSize + scaleFactor, 200);

	return { height: size, width: size };
}

/**
 * Collapsed cluster view
 */
function CollapsedClusterView({
	data,
	onToggle,
}: {
	data: ClusterNodeData;
	onToggle: () => void;
}) {
	const { cluster } = data;
	const typeColor = getTypeColor(cluster.metadata.dominantType || "unknown");
	const { width, height } = getClusterSize(cluster.size);

	// Calculate density metric (0-1)
	const density =
		cluster.metadata.internalEdges /
		Math.max((cluster.size * (cluster.size - 1)) / 2, 1);

	return (
		<div
			className={cn(
				"rounded-lg border-2 bg-background/95 backdrop-blur-sm",
				"hover:shadow-xl hover:border-primary/60 transition-all cursor-pointer",
				"flex flex-col items-center justify-center gap-2 p-3",
				"relative",
			)}
			style={{
				borderColor: `${typeColor}40`,
				height,
				width,
			}}
			onClick={onToggle}
		>
			{/* Level indicator */}
			<div className="absolute top-1 left-1">
				<Badge
					variant="secondary"
					className="text-[10px] px-1 py-0 h-4"
					style={{ backgroundColor: `${typeColor}20` }}
				>
					L{cluster.level}
				</Badge>
			</div>

			{/* Icon */}
			<div
				className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
				style={{ backgroundColor: `${typeColor}25` }}
			>
				<Layers className="w-5 h-5" style={{ color: typeColor }} />
			</div>

			{/* Size badge */}
			<Badge
				className="text-white font-bold"
				style={{ backgroundColor: typeColor }}
			>
				{cluster.size}
			</Badge>

			{/* Type label */}
			<div
				className="text-xs font-semibold text-center truncate max-w-full px-1"
				style={{ color: typeColor }}
			>
				{cluster.metadata.dominantType}
			</div>

			{/* Density indicator */}
			<div className="w-full h-1 bg-muted rounded-full overflow-hidden">
				<div
					className="h-full transition-all"
					style={{
						backgroundColor: typeColor,
						width: `${density * 100}%`,
					}}
				/>
			</div>

			{/* Expand icon */}
			<ChevronRight className="absolute bottom-1 right-1 w-3 h-3 text-muted-foreground" />
		</div>
	);
}

/**
 * Expanded cluster view with metrics and preview
 */
function ExpandedClusterView({
	data,
	onToggle,
}: {
	data: ClusterNodeData;
	onToggle: () => void;
}) {
	const { cluster, items } = data;
	const typeColor = getTypeColor(cluster.metadata.dominantType || "unknown");

	// Calculate additional metrics
	const totalEdges =
		cluster.metadata.internalEdges + cluster.metadata.externalEdges;
	const cohesion =
		totalEdges > 0 ? cluster.metadata.internalEdges / totalEdges : 0;

	// Get type distribution entries sorted by count
	const typeEntries = Object.entries(
		cluster.metadata.typeDistribution,
	).toSorted((a, b) => b[1] - a[1]);

	return (
		<Card
			className="w-[400px] overflow-hidden shadow-2xl border-2"
			style={{ borderColor: typeColor }}
		>
			{/* Header */}
			<div
				className="p-4 border-b"
				style={{
					background: `linear-gradient(135deg, ${typeColor}20, ${typeColor}05)`,
				}}
			>
				<div className="flex items-center justify-between mb-3">
					<div className="flex items-center gap-3 flex-1 min-w-0">
						<div
							className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
							style={{ backgroundColor: `${typeColor}30` }}
						>
							<Network className="w-6 h-6" style={{ color: typeColor }} />
						</div>
						<div className="min-w-0">
							<h3 className="font-bold text-base">
								Cluster {cluster.id.split("-").pop()}
							</h3>
							<div className="flex items-center gap-2 mt-1">
								<Badge variant="outline" className="text-[10px]">
									Level {cluster.level}
								</Badge>
								<Badge
									variant="outline"
									className="text-[10px]"
									style={{ borderColor: typeColor, color: typeColor }}
								>
									{cluster.metadata.dominantType}
								</Badge>
							</div>
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

			{/* Metrics */}
			<div className="px-4 py-3 border-b bg-muted/20">
				<div className="grid grid-cols-4 gap-3 mb-3">
					<div className="text-center">
						<div className="text-2xl font-bold" style={{ color: typeColor }}>
							{cluster.size}
						</div>
						<div className="text-[10px] text-muted-foreground">Nodes</div>
					</div>
					<div className="text-center">
						<div className="text-2xl font-bold text-green-500">
							{cluster.metadata.internalEdges}
						</div>
						<div className="text-[10px] text-muted-foreground">Internal</div>
					</div>
					<div className="text-center">
						<div className="text-2xl font-bold text-orange-500">
							{cluster.metadata.externalEdges}
						</div>
						<div className="text-[10px] text-muted-foreground">External</div>
					</div>
					<div className="text-center">
						<div className="text-2xl font-bold text-blue-500">
							{cluster.metadata.avgDegree.toFixed(1)}
						</div>
						<div className="text-[10px] text-muted-foreground">Avg Degree</div>
					</div>
				</div>

				{/* Cohesion bar */}
				<div className="space-y-1">
					<div className="flex items-center justify-between text-[10px]">
						<span className="text-muted-foreground">Cohesion</span>
						<span className="font-semibold">
							{(cohesion * 100).toFixed(0)}%
						</span>
					</div>
					<div className="w-full h-2 bg-muted rounded-full overflow-hidden">
						<div
							className="h-full transition-all"
							style={{
								backgroundColor:
									cohesion > 0.7
										? "#22c55e"
										: (cohesion > 0.4
											? "#f59e0b"
											: "#ef4444"),
								width: `${cohesion * 100}%`,
							}}
						/>
					</div>
				</div>
			</div>

			{/* Type distribution */}
			<div className="px-4 py-3 border-b">
				<div className="text-xs font-semibold mb-2 text-muted-foreground">
					Type Distribution
				</div>
				<div className="space-y-1.5">
					{typeEntries.slice(0, 5).map(([type, count]) => {
						const percentage = (count / cluster.size) * 100;
						const color = getTypeColor(type);
						return (
							<div key={type} className="space-y-0.5">
								<div className="flex items-center justify-between text-[11px]">
									<span className="capitalize">
										{type.replaceAll(/_/g, " ")}
									</span>
									<span className="font-semibold">{count}</span>
								</div>
								<div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
									<div
										className="h-full transition-all"
										style={{
											backgroundColor: color,
											width: `${percentage}%`,
										}}
									/>
								</div>
							</div>
						);
					})}
				</div>
			</div>

			{/* Item preview */}
			<div className="max-h-[200px] overflow-y-auto">
				<div className="p-3 space-y-1.5">
					<div className="text-xs font-semibold mb-2 text-muted-foreground">
						Preview ({Math.min(10, items.length)} of {items.length})
					</div>
					{items.slice(0, 10).map((item) => (
						<div
							key={item.id}
							className={cn(
								"p-2 rounded-md border bg-card text-xs hover:bg-accent transition-colors",
								"cursor-pointer truncate",
							)}
							onClick={() => data.onItemSelect?.(item.id)}
							title={item.title}
						>
							<div className="truncate font-medium">{item.title}</div>
						</div>
					))}
					{items.length > 10 && (
						<div className="p-2 text-[10px] text-muted-foreground text-center">
							+{items.length - 10} more items
						</div>
					)}
				</div>
			</div>

			{/* Actions */}
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
				<Button
					variant="outline"
					size="sm"
					className="flex-1 text-xs"
					onClick={() => data.onDrillDown?.(cluster.id)}
				>
					<Maximize2 className="w-3 h-3 mr-1" />
					Drill Down
				</Button>
			</div>
		</Card>
	);
}

/**
 * Cluster node component
 */
function ClusterNodeComponent({ data: nodeData, selected }: NodeProps) {
	const handleToggle = useCallback(() => {
		if (isClusterNodeData(nodeData)) {
			nodeData.onToggle(nodeData.cluster.id);
		}
	}, [nodeData]);

	if (!isClusterNodeData(nodeData)) {
		logger.error("Invalid ClusterNodeData structure:", nodeData);
		return null;
	}

	const data = nodeData;

	// Calculate handle positions based on size
	useMemo(() => getClusterSize(data.cluster.size), [data.cluster.size]);

	return (
		<div
			className={cn(
				"relative transition-all",
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
			<Handle
				type="target"
				position={Position.Top}
				className="!w-3 !h-3 !bg-primary !border-2 !border-background"
			/>
			<Handle
				type="source"
				position={Position.Bottom}
				className="!w-3 !h-3 !bg-primary !border-2 !border-background"
			/>

			{/* Render based on expansion state */}
			{data.isExpanded ? (
				<ExpandedClusterView data={data} onToggle={handleToggle} />
			) : (
				<CollapsedClusterView data={data} onToggle={handleToggle} />
			)}
		</div>
	);
}

export const ClusterNode = memo(ClusterNodeComponent);
