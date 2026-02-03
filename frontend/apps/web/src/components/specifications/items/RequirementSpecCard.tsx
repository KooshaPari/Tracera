/**
 * RequirementSpec Card Component
 *
 * Displays requirement specification with EARS pattern visualization,
 * constraint indicators, verification status, and quality metrics.
 * Implements ISO 29148 quality visualization.
 */

import {
	Badge,
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Progress,
	Separator,
} from "@tracertm/ui";
import { format } from "date-fns";
import {
	AlertTriangle,
	ArrowRight,
	CheckCircle2,
	Clock,
	FileText,
	GitBranch,
	Shield,
	Target,
	TrendingDown,
	TrendingUp,
	XCircle,
} from "lucide-react";
import type { RequirementSpec } from "@/hooks/useItemSpecs";
import { cn } from "@/lib/utils";
import { QualityScoreGauge } from "./QualityScoreGauge";

interface RequirementSpecCardProps {
	spec: RequirementSpec;
	onClick?: () => void;
	className?: string;
	compact?: boolean;
	showQuality?: boolean;
}

const requirementTypeLabels: Record<
	string,
	{ label: string; description: string }
> = {
	complex: { description: "Multi-condition requirement", label: "Complex" },
	event_driven: { description: "When <trigger> occurs", label: "Event-Driven" },
	optional: { description: "Where <feature> is enabled", label: "Optional" },
	state_driven: { description: "While <state> holds", label: "State-Driven" },
	ubiquitous: { description: "Always applies", label: "Ubiquitous" },
	unwanted: { description: "Shall not behavior", label: "Unwanted" },
};

const constraintTypeStyles = {
	hard: { bg: "bg-red-500/10", label: "Hard Constraint", text: "text-red-600" },
	optimizable: {
		bg: "bg-green-500/10",
		label: "Optimizable",
		text: "text-green-600",
	},
	soft: {
		bg: "bg-yellow-500/10",
		label: "Soft Constraint",
		text: "text-yellow-600",
	},
};

const verificationStatusStyles = {
	expired: {
		bg: "bg-orange-500/10",
		icon: AlertTriangle,
		text: "text-orange-600",
	},
	failed: { bg: "bg-red-500/10", icon: XCircle, text: "text-red-600" },
	pending: { bg: "bg-yellow-500/10", icon: Clock, text: "text-yellow-600" },
	unverified: { bg: "bg-muted", icon: Clock, text: "text-muted-foreground" },
	verified: {
		bg: "bg-green-500/10",
		icon: CheckCircle2,
		text: "text-green-600",
	},
};

const riskLevelStyles = {
	critical: { bg: "bg-red-500", text: "text-white" },
	high: { bg: "bg-orange-500", text: "text-white" },
	low: { bg: "bg-green-500", text: "text-white" },
	medium: { bg: "bg-yellow-500", text: "text-white" },
	minimal: { bg: "bg-blue-500", text: "text-white" },
};

export function RequirementSpecCard({
	spec,
	onClick,
	className,
	compact = false,
	showQuality = true,
}: RequirementSpecCardProps) {
	const reqType = requirementTypeLabels[spec.requirement_type] || {
		description: "",
		label: spec.requirement_type,
	};
	const constraintStyle = constraintTypeStyles[spec.constraint_type];
	const verificationStyle = verificationStatusStyles[spec.verification_status];
	const riskStyle = riskLevelStyles[spec.risk_level];
	const VerificationIcon = verificationStyle.icon;

	// Build EARS pattern display
	const buildEarsPattern = () => {
		const parts: string[] = [];
		if (spec.ears_trigger) {
			parts.push(`When ${spec.ears_trigger}`);
		}
		if (spec.ears_precondition) {
			parts.push(`while ${spec.ears_precondition}`);
		}
		if (spec.ears_postcondition) {
			parts.push(`the system shall ${spec.ears_postcondition}`);
		}
		return parts.join(", ");
	};

	if (compact) {
		return (
			<Card
				className={cn(
					"hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer",
					className,
				)}
				onClick={onClick}
			>
				<CardContent className="p-3">
					<div className="flex items-start justify-between gap-2">
						<div className="flex-1 min-w-0">
							<div className="flex items-center gap-2 mb-1 flex-wrap">
								<Badge
									variant="outline"
									className="text-[10px] font-black uppercase"
								>
									{reqType.label}
								</Badge>
								<Badge
									className={cn(
										"text-[10px]",
										verificationStyle.bg,
										verificationStyle.text,
									)}
								>
									<VerificationIcon className="w-2.5 h-2.5 mr-1" />
									{spec.verification_status}
								</Badge>
							</div>
							<p className="text-xs text-muted-foreground line-clamp-2">
								{buildEarsPattern() || "No EARS pattern defined"}
							</p>
							{spec.overall_quality_score !== undefined && (
								<div className="flex items-center gap-2 mt-2">
									<span className="text-[10px] text-muted-foreground">
										Quality:
									</span>
									<Progress
										value={spec.overall_quality_score}
										className="h-1 flex-1"
									/>
									<span className="text-xs font-bold tabular-nums">
										{spec.overall_quality_score.toFixed(0)}%
									</span>
								</div>
							)}
						</div>
						<Button variant="ghost" size="sm" className="h-7 shrink-0">
							<ArrowRight className="w-3 h-3" />
						</Button>
					</div>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card
			className={cn(
				"hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200",
				onClick && "cursor-pointer",
				className,
			)}
			onClick={onClick}
		>
			<CardHeader className="pb-3">
				<div className="flex justify-between items-start gap-4">
					<div className="flex-1">
						<div className="flex items-center gap-2 mb-2 flex-wrap">
							<Badge
								variant="outline"
								className="text-[10px] font-black uppercase"
							>
								<FileText className="w-2.5 h-2.5 mr-1" />
								{reqType.label}
							</Badge>
							<Badge
								className={cn(
									"text-[10px]",
									constraintStyle.bg,
									constraintStyle.text,
								)}
							>
								<Target className="w-2.5 h-2.5 mr-1" />
								{constraintStyle.label}
							</Badge>
							<Badge
								className={cn(
									"text-[10px]",
									verificationStyle.bg,
									verificationStyle.text,
								)}
							>
								<VerificationIcon className="w-2.5 h-2.5 mr-1" />
								{spec.verification_status}
							</Badge>
							<Badge
								className={cn("text-[10px]", riskStyle.bg, riskStyle.text)}
							>
								<Shield className="w-2.5 h-2.5 mr-1" />
								{spec.risk_level} risk
							</Badge>
						</div>
						<CardTitle className="text-sm font-semibold">
							Requirement Specification
						</CardTitle>
						<p className="text-xs text-muted-foreground mt-1">
							{reqType.description}
						</p>
					</div>

					{/* Quality Score Mini */}
					{spec.overall_quality_score !== undefined && (
						<div className="text-right">
							<div className="text-2xl font-black tabular-nums">
								{spec.overall_quality_score.toFixed(0)}
							</div>
							<div className="text-[10px] text-muted-foreground uppercase">
								Quality
							</div>
						</div>
					)}
				</div>
			</CardHeader>

			<CardContent className="space-y-4">
				{/* EARS Pattern */}
				{(spec.ears_trigger ||
					spec.ears_precondition ||
					spec.ears_postcondition) && (
					<div className="space-y-2">
						<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
							EARS Pattern
						</h4>
						<div className="p-3 rounded-lg bg-muted/30 space-y-2">
							{spec.ears_trigger && (
								<div className="flex items-start gap-2">
									<Badge variant="outline" className="text-[9px] shrink-0">
										WHEN
									</Badge>
									<span className="text-xs">{spec.ears_trigger}</span>
								</div>
							)}
							{spec.ears_precondition && (
								<div className="flex items-start gap-2">
									<Badge variant="outline" className="text-[9px] shrink-0">
										WHILE
									</Badge>
									<span className="text-xs">{spec.ears_precondition}</span>
								</div>
							)}
							{spec.ears_postcondition && (
								<div className="flex items-start gap-2">
									<Badge variant="outline" className="text-[9px] shrink-0">
										SHALL
									</Badge>
									<span className="text-xs">{spec.ears_postcondition}</span>
								</div>
							)}
						</div>
					</div>
				)}

				{/* Constraints */}
				{spec.constraint_target !== undefined && (
					<div className="space-y-2">
						<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
							Performance Constraint
						</h4>
						<div className="flex items-center gap-4 p-3 rounded-lg bg-muted/30">
							<div className="text-center">
								<div className="text-xl font-black tabular-nums">
									{spec.constraint_target}
								</div>
								<div className="text-[10px] text-muted-foreground">
									{spec.constraint_unit || "units"}
								</div>
							</div>
							{spec.constraint_tolerance !== undefined && (
								<>
									<Separator orientation="vertical" className="h-8" />
									<div className="text-center">
										<div className="text-sm font-bold tabular-nums">
											\u00B1{spec.constraint_tolerance}
										</div>
										<div className="text-[10px] text-muted-foreground">
											Tolerance
										</div>
									</div>
								</>
							)}
						</div>
					</div>
				)}

				{/* Pre/Post Conditions */}
				{(spec.preconditions.length > 0 || spec.postconditions.length > 0) && (
					<div className="grid grid-cols-2 gap-3">
						{spec.preconditions.length > 0 && (
							<div className="space-y-1">
								<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
									Preconditions
								</h4>
								<ul className="text-xs space-y-1">
									{spec.preconditions.slice(0, 3).map((pre, i) => (
										<li key={i} className="flex items-start gap-1">
											<span className="text-muted-foreground">•</span>
											<span className="line-clamp-1">{pre}</span>
										</li>
									))}
									{spec.preconditions.length > 3 && (
										<li className="text-muted-foreground text-[10px]">
											+{spec.preconditions.length - 3} more
										</li>
									)}
								</ul>
							</div>
						)}
						{spec.postconditions.length > 0 && (
							<div className="space-y-1">
								<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
									Postconditions
								</h4>
								<ul className="text-xs space-y-1">
									{spec.postconditions.slice(0, 3).map((post, i) => (
										<li key={i} className="flex items-start gap-1">
											<span className="text-muted-foreground">•</span>
											<span className="line-clamp-1">{post}</span>
										</li>
									))}
									{spec.postconditions.length > 3 && (
										<li className="text-muted-foreground text-[10px]">
											+{spec.postconditions.length - 3} more
										</li>
									)}
								</ul>
							</div>
						)}
					</div>
				)}

				{/* Quality Scores Detail */}
				{showQuality &&
					spec.quality_scores &&
					Object.keys(spec.quality_scores).length > 0 && (
						<div className="space-y-2">
							<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
								Quality Dimensions
							</h4>
							<QualityScoreGauge
								overallScore={spec.overall_quality_score ?? 0}
								dimensions={Object.entries(spec.quality_scores).map(
									([dim, score]) => ({
										dimension: dim,
										score: score as number,
									}),
								)}
								issues={spec.quality_issues ?? []}
								size="sm"
								showDetails
							/>
						</div>
					)}

				{/* Traceability & Impact */}
				<div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
					<div className="flex items-center gap-4">
						<div className="flex items-center gap-1">
							<TrendingUp className="w-3 h-3" />
							<span>{spec.upstream_count} upstream</span>
						</div>
						<div className="flex items-center gap-1">
							<TrendingDown className="w-3 h-3" />
							<span>{spec.downstream_count} downstream</span>
						</div>
						<div className="flex items-center gap-1">
							<GitBranch className="w-3 h-3" />
							<span>{spec.change_count} changes</span>
						</div>
					</div>
					{spec.wsjf_score !== undefined && (
						<Badge variant="outline" className="text-[10px]">
							WSJF: {spec.wsjf_score.toFixed(1)}
						</Badge>
					)}
				</div>

				{/* Verification Evidence */}
				{spec.verified_at && (
					<div className="text-[10px] text-muted-foreground">
						Verified {format(new Date(spec.verified_at), "MMM d, yyyy")}
						{spec.verified_by && ` by ${spec.verified_by}`}
					</div>
				)}
			</CardContent>
		</Card>
	);
}
