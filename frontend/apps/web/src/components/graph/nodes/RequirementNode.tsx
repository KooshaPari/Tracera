// RequirementNode - Type-specific node for requirement items
// Shows EARS pattern, risk level, and quality metrics

import type { RequirementItem } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { Handle, type Node, type NodeProps, Position } from "@xyflow/react";
import {
	AlertCircle,
	CheckCircle2,
	FileText,
	ShieldCheck,
	TrendingUp,
} from "lucide-react";
import { memo } from "react";

// Requirement-specific node data
export interface RequirementNodeData {
	id: string;
	item: RequirementItem;
	label: string;
	type: string;
	status: string;

	// Requirement-specific fields
	earsPatternType?:
		| "ubiquitous"
		| "event_driven"
		| "state_driven"
		| "optional"
		| "unwanted";
	riskLevel?: "low" | "medium" | "high" | "critical";
	wsjfScore?: number; // Weighted Shortest Job First score
	verifiabilityScore?: number; // 0-100, how testable is this
	verificationStatus?: "not_verified" | "partially_verified" | "verified";

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

// EARS pattern colors
const EARS_COLORS = {
	ubiquitous: "#8b5cf6",
	event_driven: "#3b82f6",
	state_driven: "#10b981",
	optional: "#f59e0b",
	unwanted: "#ef4444",
};

// Risk level colors
const RISK_COLORS = {
	low: "#22c55e",
	medium: "#f59e0b",
	high: "#f97316",
	critical: "#ef4444",
};

// Verification status icons
const VERIFICATION_ICONS = {
	not_verified: AlertCircle,
	partially_verified: TrendingUp,
	verified: CheckCircle2,
};

const VERIFICATION_COLORS = {
	not_verified: "#94a3b8",
	partially_verified: "#f59e0b",
	verified: "#22c55e",
};

function RequirementNodeComponent({
	data,
	selected,
}: NodeProps<Node<RequirementNodeData, "requirement">>) {
	const earsColor = EARS_COLORS[data.earsPatternType || "ubiquitous"];
	const riskColor = RISK_COLORS[data.riskLevel || "low"];
	const VerificationIcon =
		VERIFICATION_ICONS[data.verificationStatus || "not_verified"];
	const verificationColor =
		VERIFICATION_COLORS[data.verificationStatus || "not_verified"];

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
				style={{ borderColor: "#9333ea" }}
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
					style={{ backgroundColor: "#9333ea" }}
				/>

				{/* Content section */}
				<div className="p-3 pt-3.5">
					{/* Header: Icon + Badges */}
					<div className="flex items-start gap-2 mb-2">
						<div
							className="flex-shrink-0 rounded p-1.5"
							style={{ backgroundColor: "#9333ea20" }}
						>
							<FileText className="h-4 w-4 text-purple-600" />
						</div>

						<div className="flex-1 min-w-0 space-y-1">
							<div className="flex items-center gap-1.5 flex-wrap">
								{/* EARS Pattern Badge */}
								{data.earsPatternType && (
									<Tooltip>
										<TooltipTrigger asChild>
											<Badge
												variant="outline"
												className="text-[10px] px-1.5 h-5"
												style={{
													backgroundColor: `${earsColor}15`,
													color: earsColor,
													borderColor: `${earsColor}40`,
												}}
											>
												{data.earsPatternType.replace(/_/g, " ")}
											</Badge>
										</TooltipTrigger>
										<TooltipContent>
											<p>
												EARS Pattern: {data.earsPatternType.replace(/_/g, " ")}
											</p>
										</TooltipContent>
									</Tooltip>
								)}

								{/* Risk Badge */}
								{data.riskLevel && (
									<Tooltip>
										<TooltipTrigger asChild>
											<Badge
												variant="outline"
												className="text-[10px] px-1.5 h-5 ml-auto"
												style={{
													backgroundColor: `${riskColor}15`,
													color: riskColor,
													borderColor: `${riskColor}40`,
												}}
											>
												<AlertCircle className="h-3 w-3 mr-0.5" />
												{data.riskLevel}
											</Badge>
										</TooltipTrigger>
										<TooltipContent>
											<p>Risk Level: {data.riskLevel}</p>
										</TooltipContent>
									</Tooltip>
								)}
							</div>
						</div>
					</div>

					{/* Title */}
					<h4 className="font-semibold text-sm leading-tight line-clamp-2 mb-2">
						{data.label}
					</h4>

					{/* Quality Metrics */}
					<div className="space-y-2 mb-2">
						{/* WSJF Score */}
						{data.wsjfScore !== undefined && (
							<Tooltip>
								<TooltipTrigger asChild>
									<div className="flex items-center justify-between text-xs">
										<span className="text-muted-foreground">WSJF Score</span>
										<span className="font-medium text-purple-600">
											{data.wsjfScore.toFixed(1)}
										</span>
									</div>
								</TooltipTrigger>
								<TooltipContent>
									<p>
										Weighted Shortest Job First: {data.wsjfScore.toFixed(2)}
									</p>
								</TooltipContent>
							</Tooltip>
						)}

						{/* Verifiability Gauge */}
						{data.verifiabilityScore !== undefined && (
							<Tooltip>
								<TooltipTrigger asChild>
									<div className="space-y-1">
										<div className="flex items-center justify-between text-xs">
											<span className="text-muted-foreground flex items-center gap-1">
												<ShieldCheck className="h-3 w-3" />
												Verifiable
											</span>
											<span className="font-medium">
												{data.verifiabilityScore}%
											</span>
										</div>
										<div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
											<div
												className="h-full bg-purple-500 transition-all"
												style={{ width: `${data.verifiabilityScore}%` }}
											/>
										</div>
									</div>
								</TooltipTrigger>
								<TooltipContent>
									<p>Verifiability: {data.verifiabilityScore}%</p>
								</TooltipContent>
							</Tooltip>
						)}
					</div>

					{/* Verification Status */}
					{data.verificationStatus && (
						<div
							className="flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium"
							style={{
								backgroundColor: `${verificationColor}15`,
								color: verificationColor,
							}}
						>
							<VerificationIcon className="h-3.5 w-3.5" />
							<span>{data.verificationStatus.replace(/_/g, " ")}</span>
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
				style={{ borderColor: "#9333ea" }}
			/>
		</TooltipProvider>
	);
}

export const RequirementNode = memo(RequirementNodeComponent);
