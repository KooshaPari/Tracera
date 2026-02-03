/* eslint-disable complexity, func-style, jsx-max-depth, max-lines-per-function, no-magic-numbers, react-perf/jsx-no-new-object-as-prop, react-perf/jsx-no-new-function-as-prop, sort-imports */
// EpicNode - Type-specific node for epic items
// Shows business value, timeline progress, and story completion

import type { EpicItem } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { Handle, Position } from "@xyflow/react";
import type { Node, NodeProps } from "@xyflow/react";
import { CheckCircle2, Circle, GitBranch, TrendingUp } from "lucide-react";
import { memo } from "react";

// Epic-specific node data
export interface EpicNodeData {
	id: string;
	item: EpicItem;
	label: string;
	type: string;
	status: string;

	// Epic-specific fields
	businessValue?: "low" | "medium" | "high" | "critical";
	timelineProgress?: number; // 0-100
	storyCount?: number; // Total stories
	completedStoryCount?: number; // Completed stories

	// Connection counts
	connections: {
		incoming: number;
		outgoing: number;
		total: number;
	};

	// Callbacks
	onSelect?: ((id: string) => void) | undefined;

	// Index signature for React Flow compatibility
	[key: string]: unknown;
}

// Business value colors
const BUSINESS_VALUE_COLORS = {
	critical: "#f59e0b",
	high: "#10b981",
	low: "#94a3b8",
	medium: "#3b82f6",
};

function EpicNodeComponent({
	data,
	selected,
}: NodeProps<Node<EpicNodeData, "epic">>) {
	const businessValueColor =
		BUSINESS_VALUE_COLORS[data.businessValue || "medium"];
	const storyCompletion = data.storyCount
		? ((data.completedStoryCount || 0) / data.storyCount) * 100
		: 0;

	const handleClick = () => {
		data.onSelect?.(data.id);
	};

	return (
		<TooltipProvider>
			{/* Input handle */}
			<Handle
				type="target"
				position={Position.Left}
				className="!w-3 !h-3 !bg-background !border-2"
				style={{ borderColor: "#7c3aed" }}
			/>

			{/* Main card */}
			<Card
				className={`
          relative overflow-hidden transition-all duration-200 cursor-pointer w-[260px]
          ${selected ? "ring-2 ring-white ring-offset-2 ring-offset-background" : ""}
        `}
				onClick={handleClick}
			>
				{/* Color accent bar */}
				<div
					className="absolute top-0 left-0 right-0 h-1"
					style={{ backgroundColor: "#7c3aed" }}
				/>

				{/* Content section */}
				<div className="p-3 pt-3.5">
					{/* Header: Icon + Badges */}
					<div className="flex items-start gap-2 mb-2">
						<div
							className="flex-shrink-0 rounded p-1.5"
							style={{ backgroundColor: "#7c3aed20" }}
						>
							<GitBranch className="h-4 w-4 text-purple-700" />
						</div>

						<div className="flex-1 min-w-0 space-y-1">
							<div className="flex items-center gap-1.5 flex-wrap">
								{/* Type Badge */}
								<Badge
									variant="outline"
									className="text-[10px] px-1.5 h-5"
									style={{
										backgroundColor: "#7c3aed15",
										borderColor: "#7c3aed40",
										color: "#7c3aed",
									}}
								>
									Epic
								</Badge>

								{/* Business Value Badge */}
								{data.businessValue && (
									<Tooltip>
										<TooltipTrigger asChild>
											<Badge
												variant="outline"
												className="text-[10px] px-1.5 h-5 ml-auto"
												style={{
													backgroundColor: `${businessValueColor}15`,
													borderColor: `${businessValueColor}40`,
													color: businessValueColor,
												}}
											>
												<TrendingUp className="h-3 w-3 mr-0.5" />
												{data.businessValue}
											</Badge>
										</TooltipTrigger>
										<TooltipContent>
											<p>Business Value: {data.businessValue}</p>
										</TooltipContent>
									</Tooltip>
								)}
							</div>
						</div>
					</div>

					{/* Title */}
					<h4 className="font-semibold text-sm leading-tight line-clamp-2 mb-3">
						{data.label}
					</h4>

					{/* Progress Metrics */}
					<div className="space-y-2.5">
						{/* Timeline Progress */}
						{data.timelineProgress !== undefined && (
							<Tooltip>
								<TooltipTrigger asChild>
									<div className="space-y-1">
										<div className="flex items-center justify-between text-xs">
											<span className="text-muted-foreground">Timeline</span>
											<span className="font-medium">
												{data.timelineProgress}%
											</span>
										</div>
										<div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
											<div
												className="h-full bg-blue-500 transition-all"
												style={{ width: `${data.timelineProgress}%` }}
											/>
										</div>
									</div>
								</TooltipTrigger>
								<TooltipContent>
									<p>Timeline Progress: {data.timelineProgress}%</p>
								</TooltipContent>
							</Tooltip>
						)}

						{/* Story Completion */}
						{data.storyCount !== undefined && (
							<Tooltip>
								<TooltipTrigger asChild>
									<div className="space-y-1">
										<div className="flex items-center justify-between text-xs">
											<span className="text-muted-foreground flex items-center gap-1">
												<Circle className="h-3 w-3" />
												Stories
											</span>
											<span className="font-medium">
												{data.completedStoryCount || 0} / {data.storyCount}
											</span>
										</div>
										<div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
											<div
												className="h-full bg-purple-500 transition-all"
												style={{ width: `${storyCompletion}%` }}
											/>
										</div>
									</div>
								</TooltipTrigger>
								<TooltipContent>
									<p>
										Stories: {data.completedStoryCount || 0} completed of{" "}
										{data.storyCount} total ({storyCompletion.toFixed(0)}%)
									</p>
								</TooltipContent>
							</Tooltip>
						)}
					</div>

					{/* Completion Badge */}
					{storyCompletion === 100 && (
						<div className="flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium mt-2 bg-green-500/15 text-green-600">
							<CheckCircle2 className="h-3.5 w-3.5" />
							<span>All stories completed</span>
						</div>
					)}

					{/* Footer: Status badge and connections */}
					<div className="flex items-center justify-between mt-2 pt-2 border-t text-[10px] text-muted-foreground">
						<Badge variant="secondary" className="text-[10px] px-1.5 h-4">
							{data.status}
						</Badge>
						<span className="flex items-center gap-0.5">
							{data.connections.total} links
						</span>
					</div>
				</div>
			</Card>

			{/* Output handle */}
			<Handle
				type="source"
				position={Position.Right}
				className="!w-3 !h-3 !bg-background !border-2"
				style={{ borderColor: "#7c3aed" }}
			/>
		</TooltipProvider>
	);
}

export const EpicNode = memo(EpicNodeComponent);
