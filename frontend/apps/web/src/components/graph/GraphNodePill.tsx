// Rich Graph Node Component - Block Pill Style with UI Preview

import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import {
	AlertCircle,
	CheckCircle2,
	Circle,
	Clock,
	Code,
	Database,
	FileText,
	GitBranch,
	Image,
	Layout,
	Link2,
	Monitor,
	Shield,
	TestTube2,
	XCircle,
	Zap,
} from "lucide-react";
import { memo } from "react";
import type { EnhancedNodeData } from "./types";
import { ENHANCED_TYPE_COLORS, STATUS_OPACITY } from "./types";

interface GraphNodePillProps {
	node: EnhancedNodeData;
	isSelected: boolean;
	isHighlighted: boolean;
	onSelect: (nodeId: string) => void;
	onExpand: (nodeId: string) => void;
	showPreview: boolean;
}

// Icon mapping for item types
const TYPE_ICONS: Record<
	string,
	React.ComponentType<{ className?: string }>
> = {
	requirement: FileText,
	feature: Zap,
	epic: GitBranch,
	user_story: FileText,
	story: FileText,
	api: Code,
	database: Database,
	code: Code,
	architecture: Layout,
	infrastructure: Monitor,
	wireframe: Image,
	ui_component: Layout,
	page: Monitor,
	component: Layout,
	test: TestTube2,
	test_case: TestTube2,
	test_suite: TestTube2,
	security: Shield,
	vulnerability: AlertCircle,
	audit: Shield,
	performance: Zap,
	monitoring: Monitor,
	metric: Zap,
	task: Circle,
	bug: AlertCircle,
	journey: GitBranch,
};

// Status icons
const STATUS_ICONS: Record<
	string,
	React.ComponentType<{ className?: string }>
> = {
	done: CheckCircle2,
	completed: CheckCircle2,
	in_progress: Clock,
	todo: Circle,
	pending: Circle,
	blocked: XCircle,
	cancelled: XCircle,
};

function GraphNodePillComponent({
	node,
	isSelected,
	isHighlighted,
	onSelect,
	onExpand,
	showPreview,
}: GraphNodePillProps) {
	const TypeIcon = TYPE_ICONS[node.type] || Circle;
	const StatusIcon = STATUS_ICONS[node.status] || Circle;
	const bgColor = ENHANCED_TYPE_COLORS[node.type] || "#64748b";
	const opacity = STATUS_OPACITY[node.status] || 1;

	const handleClick = (e: React.MouseEvent) => {
		e.stopPropagation();
		onSelect(node.id);
	};

	const handleDoubleClick = (e: React.MouseEvent) => {
		e.stopPropagation();
		onExpand(node.id);
	};

	return (
		<TooltipProvider>
			<Tooltip delayDuration={300}>
				<TooltipTrigger asChild>
					<div
						onClick={handleClick}
						onDoubleClick={handleDoubleClick}
						className={`
              relative cursor-pointer transition-all duration-200 ease-out
              ${isSelected ? "scale-105 z-20" : "hover:scale-102 z-10"}
              ${isHighlighted ? "ring-2 ring-white ring-offset-2 ring-offset-background" : ""}
            `}
						style={{ opacity }}
					>
						{/* Main Pill Container */}
						<Card
							className={`
                overflow-hidden border-2 transition-all duration-200
                ${isSelected ? "shadow-lg shadow-primary/20" : "shadow-md"}
              `}
							style={{
								borderColor: isSelected ? "#fff" : bgColor,
								minWidth:
									showPreview && node.uiPreview?.screenshotUrl
										? "180px"
										: "140px",
							}}
						>
							{/* UI Preview Section (if applicable) */}
							{showPreview && node.uiPreview?.screenshotUrl && (
								<div
									className="h-24 bg-cover bg-center bg-no-repeat border-b"
									style={{
										backgroundImage: `url(${node.uiPreview.screenshotUrl})`,
										borderColor: bgColor,
									}}
								>
									{/* Interactive overlay indicator */}
									{node.uiPreview.interactiveWidgetUrl && (
										<div className="absolute top-1 right-1 bg-black/60 rounded px-1.5 py-0.5 text-[10px] text-white flex items-center gap-1">
											<Monitor className="h-3 w-3" />
											Interactive
										</div>
									)}
								</div>
							)}

							{/* Node Content */}
							<div
								className="p-2.5"
								style={{
									backgroundColor: `${bgColor}15`,
								}}
							>
								{/* Header: Type Icon + Title */}
								<div className="flex items-start gap-2">
									<div
										className="shrink-0 rounded-md p-1.5"
										style={{ backgroundColor: bgColor }}
									>
										<TypeIcon className="h-3.5 w-3.5 text-white" />
									</div>
									<div className="min-w-0 flex-1">
										<p className="text-xs font-semibold text-foreground leading-tight line-clamp-2">
											{node.label}
										</p>
									</div>
								</div>

								{/* Status & Connections Row */}
								<div className="mt-2 flex items-center justify-between gap-2">
									<Badge
										variant="secondary"
										className="text-[10px] px-1.5 py-0 h-5 flex items-center gap-1"
										style={{
											backgroundColor: `${bgColor}25`,
											color: bgColor,
										}}
									>
										<StatusIcon className="h-2.5 w-2.5" />
										{node.status}
									</Badge>

									{/* Connection count */}
									{node.connections.total > 0 && (
										<div className="flex items-center gap-1 text-[10px] text-muted-foreground">
											<Link2 className="h-3 w-3" />
											<span>{node.connections.total}</span>
										</div>
									)}
								</div>

								{/* Type indicator bar */}
								<div
									className="mt-2 h-1 rounded-full"
									style={{ backgroundColor: bgColor }}
								/>
							</div>
						</Card>

						{/* Children indicator */}
						{node.hasChildren && (
							<div
								className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-4 h-1 rounded-full"
								style={{ backgroundColor: bgColor }}
							/>
						)}
					</div>
				</TooltipTrigger>
				<TooltipContent side="right" className="max-w-xs">
					<div className="space-y-2">
						<div className="flex items-center gap-2">
							<div className="rounded p-1" style={{ backgroundColor: bgColor }}>
								<TypeIcon className="h-3 w-3 text-white" />
							</div>
							<span className="font-medium">{node.type}</span>
						</div>
						<p className="text-sm">
							{node.item.description || "No description"}
						</p>
						{node.item.owner && (
							<p className="text-xs text-muted-foreground">
								Owner: {node.item.owner}
							</p>
						)}
						<div className="text-xs text-muted-foreground">
							{node.connections.incoming} incoming, {node.connections.outgoing}{" "}
							outgoing
						</div>
					</div>
				</TooltipContent>
			</Tooltip>
		</TooltipProvider>
	);
}

export const GraphNodePill = memo(GraphNodePillComponent);
