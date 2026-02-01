/**
 * Quality Score Gauge Component
 *
 * Visual gauge showing overall quality score with breakdown by dimension.
 * Implements ISO 29148 quality dimensions visualization.
 */

import { Badge, Progress } from "@tracertm/ui";
import {
	AlertCircle,
	AlertTriangle,
	CheckCircle2,
	Eye,
	Info,
	Shield,
	Target,
	Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface QualityDimension {
	dimension: string;
	score: number;
	weight?: number;
}

interface QualityIssue {
	dimension: string;
	severity: "error" | "warning" | "info";
	message: string;
	suggestion?: string;
}

interface QualityScoreGaugeProps {
	overallScore?: number;
	dimensions?: QualityDimension[];
	issues?: QualityIssue[];
	size?: "sm" | "md" | "lg";
	showDetails?: boolean;
	className?: string;
}

const dimensionIcons: Record<
	string,
	React.ComponentType<{ className?: string }>
> = {
	ambiguity: Eye,
	completeness: Target,
	testability: CheckCircle2,
	consistency: Shield,
	feasibility: Zap,
	verifiability: CheckCircle2,
	traceability: Target,
};

const severityStyles = {
	error: {
		bg: "bg-red-500/10",
		text: "text-red-600",
		border: "border-red-500/20",
		icon: AlertCircle,
	},
	warning: {
		bg: "bg-yellow-500/10",
		text: "text-yellow-600",
		border: "border-yellow-500/20",
		icon: AlertTriangle,
	},
	info: {
		bg: "bg-blue-500/10",
		text: "text-blue-600",
		border: "border-blue-500/20",
		icon: Info,
	},
};

function getScoreColor(score: number): string {
	if (score >= 90) return "text-green-500";
	if (score >= 70) return "text-yellow-500";
	if (score >= 50) return "text-orange-500";
	return "text-red-500";
}

// Progress color can be used for custom Progress component styling
// function getProgressColor(score: number): string {
// 	if (score >= 90) return "bg-green-500";
// 	if (score >= 70) return "bg-yellow-500";
// 	if (score >= 50) return "bg-orange-500";
// 	return "bg-red-500";
// }

export function QualityScoreGauge({
	overallScore,
	dimensions = [],
	issues = [],
	size = "md",
	showDetails = true,
	className,
}: QualityScoreGaugeProps) {
	const score = overallScore ?? 0;
	const sizeClasses = {
		sm: "text-2xl",
		md: "text-4xl",
		lg: "text-6xl",
	};

	return (
		<div className={cn("space-y-4", className)}>
			{/* Main Score */}
			<div className="flex items-center gap-4">
				<div
					className={cn(
						"font-black tabular-nums",
						sizeClasses[size],
						getScoreColor(score),
					)}
				>
					{score.toFixed(0)}
					<span className="text-muted-foreground text-base font-normal">
						/100
					</span>
				</div>
				<div className="flex-1">
					<div className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1">
						Quality Score
					</div>
					<Progress value={score} className="h-2" />
				</div>
			</div>

			{/* Dimension Breakdown */}
			{showDetails && dimensions.length > 0 && (
				<div className="space-y-2">
					<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
						Quality Dimensions
					</h4>
					<div className="grid grid-cols-2 gap-2">
						{dimensions.map((dim) => {
							const Icon =
								dimensionIcons[dim.dimension.toLowerCase()] || Target;
							return (
								<div
									key={dim.dimension}
									className="flex items-center gap-2 p-2 rounded-lg bg-muted/30"
								>
									<Icon className="h-3.5 w-3.5 text-muted-foreground" />
									<div className="flex-1 min-w-0">
										<div className="flex items-center justify-between">
											<span className="text-xs font-medium truncate capitalize">
												{dim.dimension}
											</span>
											<span
												className={cn(
													"text-xs font-bold tabular-nums",
													getScoreColor(dim.score),
												)}
											>
												{dim.score.toFixed(0)}
											</span>
										</div>
										<Progress value={dim.score} className="h-1 mt-1" />
									</div>
								</div>
							);
						})}
					</div>
				</div>
			)}

			{/* Quality Issues */}
			{showDetails && issues.length > 0 && (
				<div className="space-y-2">
					<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
						Issues ({issues.length})
					</h4>
					<div className="space-y-2 max-h-48 overflow-y-auto">
						{issues.map((issue, idx) => {
							const style = severityStyles[issue.severity];
							const Icon = style.icon;
							return (
								<div
									key={idx}
									className={cn(
										"p-2 rounded-lg border",
										style.bg,
										style.border,
									)}
								>
									<div className="flex items-start gap-2">
										<Icon className={cn("h-3.5 w-3.5 mt-0.5", style.text)} />
										<div className="flex-1 min-w-0">
											<div className="flex items-center gap-2 mb-0.5">
												<Badge
													variant="outline"
													className={cn(
														"text-[9px] font-black uppercase",
														style.text,
														style.border,
													)}
												>
													{issue.dimension}
												</Badge>
											</div>
											<p className="text-xs">{issue.message}</p>
											{issue.suggestion && (
												<p className="text-[10px] text-muted-foreground mt-1 italic">
													{issue.suggestion}
												</p>
											)}
										</div>
									</div>
								</div>
							);
						})}
					</div>
				</div>
			)}
		</div>
	);
}
