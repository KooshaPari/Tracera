/**
 * RequirementDetailView Component
 *
 * Displays detailed information about requirement items with EARS patterns,
 * quality metrics, risk assessment, verification status, and traceability.
 * Implements ISO 29148 quality visualization.
 */

import { isRequirementItem } from "@tracertm/types";
import type { RequirementItem } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	Progress,
	Separator,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import { format } from "date-fns";
import {
	AlertCircle,
	AlertTriangle,
	ArrowRight,
	BookText,
	CheckCircle2,
	Clock,
	FileText,
	GitBranch,
	Info,
	Link2,
	Shield,
	Sparkles,
	Target,
	TrendingUp,
	XCircle,
} from "lucide-react";
import { useState } from "react";
import { useRequirementSpecByItem } from "@/hooks/useItemSpecs";
import { cn } from "@/lib/utils";

interface RequirementDetailViewProps {
	item: RequirementItem;
	projectId: string;
}

// =============================================================================
// Style Constants
// =============================================================================

const EARS_PATTERN_STYLES = {
	complex: {
		bg: "bg-indigo-500/10",
		border: "border-indigo-500/30",
		description: "Multi-condition requirement",
		example:
			"When user logs in, while session is valid, the system shall grant access",
		label: "Complex",
		text: "text-indigo-600",
	},
	event_driven: {
		bg: "bg-blue-500/10",
		border: "border-blue-500/30",
		description: "When <trigger> occurs",
		example: "When user clicks submit, the system shall validate form data",
		label: "Event-Driven",
		text: "text-blue-600",
	},
	optional: {
		bg: "bg-amber-500/10",
		border: "border-amber-500/30",
		description: "Where <feature> is enabled",
		example: "Where debug mode is enabled, the system shall log all events",
		label: "Optional",
		text: "text-amber-600",
	},
	state_driven: {
		bg: "bg-green-500/10",
		border: "border-green-500/30",
		description: "While <state> holds",
		example: "While offline mode is active, the system shall queue requests",
		label: "State-Driven",
		text: "text-green-600",
	},
	ubiquitous: {
		bg: "bg-purple-500/10",
		border: "border-purple-500/30",
		description: "Always applies - no conditions",
		example: "The system shall encrypt all stored passwords",
		label: "Ubiquitous",
		text: "text-purple-600",
	},
	unwanted: {
		bg: "bg-red-500/10",
		border: "border-red-500/30",
		description: "Shall not behavior",
		example: "The system shall not store credit card numbers in plain text",
		label: "Unwanted",
		text: "text-red-600",
	},
} as const;

const RISK_LEVEL_STYLES = {
	critical: {
		bg: "bg-red-500",
		icon: AlertCircle,
		label: "Critical",
		text: "text-white",
	},
	high: {
		bg: "bg-orange-500",
		icon: AlertTriangle,
		label: "High",
		text: "text-white",
	},
	low: {
		bg: "bg-green-500",
		icon: CheckCircle2,
		label: "Low",
		text: "text-white",
	},
	medium: {
		bg: "bg-yellow-500",
		icon: AlertTriangle,
		label: "Medium",
		text: "text-white",
	},
	minimal: {
		bg: "bg-blue-500",
		icon: CheckCircle2,
		label: "Minimal",
		text: "text-white",
	},
} as const;

const VERIFICATION_STATUS_STYLES = {
	expired: {
		bg: "bg-orange-500/10",
		icon: AlertTriangle,
		label: "Expired",
		text: "text-orange-600",
	},
	failed: {
		bg: "bg-red-500/10",
		icon: XCircle,
		label: "Failed",
		text: "text-red-600",
	},
	pending: {
		bg: "bg-yellow-500/10",
		icon: Clock,
		label: "Pending",
		text: "text-yellow-600",
	},
	unverified: {
		bg: "bg-muted",
		icon: Clock,
		label: "Unverified",
		text: "text-muted-foreground",
	},
	verified: {
		bg: "bg-green-500/10",
		icon: CheckCircle2,
		label: "Verified",
		text: "text-green-600",
	},
} as const;

// =============================================================================
// Helper Functions
// =============================================================================

function QualityGauge({
	label,
	score,
	className,
}: {
	label: string;
	score: number;
	className?: string;
}) {
	const percentage = Math.round(score * 100);
	const color =
		percentage >= 80
			? "bg-green-500"
			: (percentage >= 60
				? "bg-yellow-500"
				: "bg-red-500");

	return (
		<div className={cn("space-y-2", className)}>
			<div className="flex items-center justify-between text-sm">
				<span className="font-medium">{label}</span>
				<span className="text-muted-foreground font-bold tabular-nums">
					{percentage}%
				</span>
			</div>
			<Progress value={percentage} className="h-2">
				<div className={cn("h-full transition-all", color)} />
			</Progress>
		</div>
	);
}

function QualityRadarMini({
	verifiability,
	traceability,
	clarity,
}: {
	verifiability: number;
	traceability: number;
	clarity: number;
}) {
	return (
		<div className="grid grid-cols-3 gap-3">
			<div className="text-center space-y-1">
				<div className="text-2xl font-black tabular-nums text-purple-600">
					{Math.round(verifiability * 100)}
				</div>
				<div className="text-[10px] text-muted-foreground uppercase tracking-widest">
					Verifiability
				</div>
			</div>
			<div className="text-center space-y-1">
				<div className="text-2xl font-black tabular-nums text-blue-600">
					{Math.round(traceability * 100)}
				</div>
				<div className="text-[10px] text-muted-foreground uppercase tracking-widest">
					Traceability
				</div>
			</div>
			<div className="text-center space-y-1">
				<div className="text-2xl font-black tabular-nums text-green-600">
					{Math.round(clarity * 100)}
				</div>
				<div className="text-[10px] text-muted-foreground uppercase tracking-widest">
					Clarity
				</div>
			</div>
		</div>
	);
}

// =============================================================================
// Main Component
// =============================================================================

export function RequirementDetailView({
	item,
	projectId,
}: RequirementDetailViewProps) {
	const [activeTab, setActiveTab] = useState("overview");

	// Fetch requirement spec data (must be called unconditionally)
	const {
		data: spec,
		isLoading: specLoading,
		error: specError,
	} = useRequirementSpecByItem(projectId, item.id);

	// Type guard check
	if (!isRequirementItem(item)) {
		return (
			<Card className="border-0 bg-muted/40 p-8">
				<div className="flex items-center gap-3 text-muted-foreground">
					<AlertCircle className="h-5 w-5" />
					<p>
						This item is not a requirement. Cannot display requirement details.
					</p>
				</div>
			</Card>
		);
	}

	if (specLoading) {
		return (
			<Card className="border-0 bg-card/50 p-8">
				<div className="space-y-4 animate-pulse">
					<div className="h-8 bg-muted rounded w-1/3" />
					<div className="h-24 bg-muted rounded" />
					<div className="h-48 bg-muted rounded" />
				</div>
			</Card>
		);
	}

	if (specError || !spec) {
		return (
			<Card className="border-0 bg-card/50 p-8">
				<div className="flex flex-col items-center justify-center space-y-4 py-8">
					<FileText className="h-12 w-12 text-muted-foreground opacity-20" />
					<div className="text-center space-y-2">
						<h3 className="text-lg font-bold">No Specification Data</h3>
						<p className="text-sm text-muted-foreground">
							This requirement doesn't have detailed specification data yet.
						</p>
					</div>
					<Button variant="outline" size="sm">
						<Sparkles className="h-4 w-4 mr-2" />
						Create Specification
					</Button>
				</div>
			</Card>
		);
	}

	const earsStyle =
		EARS_PATTERN_STYLES[spec.requirement_type] ||
		EARS_PATTERN_STYLES.ubiquitous;
	const riskStyle = RISK_LEVEL_STYLES[spec.risk_level] || RISK_LEVEL_STYLES.low;
	const verificationStyle =
		VERIFICATION_STATUS_STYLES[spec.verification_status] ||
		VERIFICATION_STATUS_STYLES.unverified;

	const RiskIcon = riskStyle.icon;
	const VerificationIcon = verificationStyle.icon;

	// Calculate quality metrics
	const qualityScores = {
		clarity: spec.completeness_score || 0,
		traceability:
			spec.upstream_count + spec.downstream_count > 0
				? Math.min((spec.upstream_count + spec.downstream_count) / 10, 1)
				: 0,
		verifiability: spec.testability_score || 0,
	};

	return (
		<div className="space-y-6">
			{/* Header Card */}
			<Card className="border-0 bg-gradient-to-br from-purple-500/5 via-background to-blue-500/5 shadow-lg">
				<CardHeader className="pb-4">
					<div className="flex items-start justify-between gap-4">
						<div className="space-y-3 flex-1">
							<div className="flex items-center gap-2 flex-wrap">
								<Badge
									className={cn(
										"text-[10px] font-black uppercase tracking-wider",
										earsStyle.bg,
										earsStyle.text,
										earsStyle.border,
										"border",
									)}
								>
									<FileText className="h-3 w-3 mr-1" />
									{earsStyle.label}
								</Badge>
								<Badge
									className={cn(
										"text-[10px] font-black uppercase",
										riskStyle.bg,
										riskStyle.text,
									)}
								>
									<RiskIcon className="h-3 w-3 mr-1" />
									{riskStyle.label} Risk
								</Badge>
								<Badge
									className={cn(
										"text-[10px]",
										verificationStyle.bg,
										verificationStyle.text,
									)}
								>
									<VerificationIcon className="h-3 w-3 mr-1" />
									{verificationStyle.label}
								</Badge>
							</div>
							<CardTitle className="text-2xl">{item.title}</CardTitle>
							<CardDescription className="text-base">
								{item.description || "No description provided"}
							</CardDescription>
						</div>

						{/* Overall Quality Score */}
						{spec.overall_quality_score !== undefined && (
							<div className="text-center space-y-1">
								<div className="text-4xl font-black tabular-nums text-purple-600">
									{Math.round(spec.overall_quality_score)}
								</div>
								<div className="text-[10px] text-muted-foreground uppercase tracking-widest">
									Quality Score
								</div>
							</div>
						)}
					</div>
				</CardHeader>
			</Card>

			{/* Tabs */}
			<Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
				<TabsList className="bg-muted/60 p-1 rounded-xl w-full grid grid-cols-6">
					<TabsTrigger value="overview" className="rounded-lg">
						Overview
					</TabsTrigger>
					<TabsTrigger value="ears" className="rounded-lg">
						EARS Pattern
					</TabsTrigger>
					<TabsTrigger value="quality" className="rounded-lg">
						Quality
					</TabsTrigger>
					<TabsTrigger value="risk" className="rounded-lg">
						Risk & Verification
					</TabsTrigger>
					<TabsTrigger value="traceability" className="rounded-lg">
						Traceability
					</TabsTrigger>
					<TabsTrigger value="history" className="rounded-lg">
						History
					</TabsTrigger>
				</TabsList>

				{/* Overview Tab */}
				<TabsContent value="overview" className="space-y-6 pt-6">
					<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
						<Card className="border-0 bg-muted/40 p-4">
							<div className="space-y-2">
								<div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
									EARS Pattern
								</div>
								<div className={cn("text-lg font-bold", earsStyle.text)}>
									{earsStyle.label}
								</div>
								<div className="text-xs text-muted-foreground">
									{earsStyle.description}
								</div>
							</div>
						</Card>

						<Card className="border-0 bg-muted/40 p-4">
							<div className="space-y-2">
								<div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
									Risk Assessment
								</div>
								<div className="flex items-center gap-2">
									<RiskIcon className={cn("h-5 w-5", riskStyle.text)} />
									<div className="text-lg font-bold">{riskStyle.label}</div>
								</div>
								{spec.wsjf_score && (
									<div className="text-xs text-muted-foreground">
										WSJF: {spec.wsjf_score.toFixed(1)}
									</div>
								)}
							</div>
						</Card>

						<Card className="border-0 bg-muted/40 p-4">
							<div className="space-y-2">
								<div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
									Verification
								</div>
								<div className="flex items-center gap-2">
									<VerificationIcon
										className={cn("h-5 w-5", verificationStyle.text)}
									/>
									<div className="text-lg font-bold">
										{verificationStyle.label}
									</div>
								</div>
								{spec.verified_at && (
									<div className="text-xs text-muted-foreground">
										{format(new Date(spec.verified_at), "MMM d, yyyy")}
									</div>
								)}
							</div>
						</Card>
					</div>

					{/* Quality Metrics Mini */}
					<Card className="border-0 bg-card/50 p-6">
						<h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-4">
							Quality Dimensions
						</h3>
						<QualityRadarMini
							verifiability={qualityScores.verifiability}
							traceability={qualityScores.traceability}
							clarity={qualityScores.clarity}
						/>
					</Card>

					{/* Constraint Summary */}
					{spec.constraint_target !== undefined && (
						<Card className="border-0 bg-muted/40 p-6">
							<h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-4">
								Performance Constraint
							</h3>
							<div className="flex items-center gap-6">
								<div className="text-center">
									<div className="text-3xl font-black tabular-nums">
										{spec.constraint_target}
									</div>
									<div className="text-xs text-muted-foreground">
										{spec.constraint_unit || "units"}
									</div>
								</div>
								{spec.constraint_tolerance !== undefined && (
									<>
										<Separator orientation="vertical" className="h-12" />
										<div className="text-center">
											<div className="text-xl font-bold tabular-nums">
												±{spec.constraint_tolerance}
											</div>
											<div className="text-xs text-muted-foreground">
												Tolerance
											</div>
										</div>
									</>
								)}
								<div className="flex-1 text-right">
									<Badge variant="outline" className="text-xs">
										{spec.constraint_type} constraint
									</Badge>
								</div>
							</div>
						</Card>
					)}
				</TabsContent>

				{/* EARS Specification Tab */}
				<TabsContent value="ears" className="space-y-6 pt-6">
					<Card className="border-0 bg-card/50 p-6">
						<CardHeader className="px-0 pt-0">
							<CardTitle className="flex items-center gap-2">
								<FileText className="h-5 w-5 text-purple-600" />
								EARS Pattern Breakdown
							</CardTitle>
							<CardDescription>
								Easy Approach to Requirements Syntax (EARS) - {earsStyle.label}
							</CardDescription>
						</CardHeader>
						<CardContent className="px-0 pb-0 space-y-4">
							{/* Pattern Components */}
							<div className="space-y-3">
								{spec.ears_trigger && (
									<div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
										<div className="flex items-start gap-3">
											<Badge
												variant="outline"
												className="text-[10px] font-black shrink-0"
											>
												WHEN (Trigger)
											</Badge>
											<p className="text-sm flex-1">{spec.ears_trigger}</p>
										</div>
									</div>
								)}

								{spec.ears_precondition && (
									<div className="p-4 rounded-lg bg-green-500/5 border border-green-500/20">
										<div className="flex items-start gap-3">
											<Badge
												variant="outline"
												className="text-[10px] font-black shrink-0"
											>
												WHILE (Precondition)
											</Badge>
											<p className="text-sm flex-1">{spec.ears_precondition}</p>
										</div>
									</div>
								)}

								{spec.ears_postcondition && (
									<div className="p-4 rounded-lg bg-purple-500/5 border border-purple-500/20">
										<div className="flex items-start gap-3">
											<Badge
												variant="outline"
												className="text-[10px] font-black shrink-0"
											>
												SHALL (Postcondition)
											</Badge>
											<p className="text-sm flex-1">
												{spec.ears_postcondition}
											</p>
										</div>
									</div>
								)}

								{!spec.ears_trigger &&
									!spec.ears_precondition &&
									!spec.ears_postcondition && (
										<div className="p-8 rounded-lg bg-muted/40 text-center">
											<Info className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
											<p className="text-sm text-muted-foreground">
												No EARS pattern components defined yet
											</p>
										</div>
									)}
							</div>

							{/* Pattern Example */}
							<Separator />
							<div className="space-y-2">
								<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
									Pattern Example
								</h4>
								<div className="p-4 rounded-lg bg-muted/30 italic text-sm">
									{earsStyle.example}
								</div>
							</div>

							{/* Pre/Post Conditions */}
							{(spec.preconditions.length > 0 ||
								spec.postconditions.length > 0) && (
								<>
									<Separator />
									<div className="grid grid-cols-2 gap-4">
										{spec.preconditions.length > 0 && (
											<div className="space-y-2">
												<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
													Preconditions
												</h4>
												<ul className="space-y-1">
													{spec.preconditions.map((pre, i) => (
														<li
															key={i}
															className="flex items-start gap-2 text-sm"
														>
															<span className="text-muted-foreground">•</span>
															<span>{pre}</span>
														</li>
													))}
												</ul>
											</div>
										)}

										{spec.postconditions.length > 0 && (
											<div className="space-y-2">
												<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
													Postconditions
												</h4>
												<ul className="space-y-1">
													{spec.postconditions.map((post, i) => (
														<li
															key={i}
															className="flex items-start gap-2 text-sm"
														>
															<span className="text-muted-foreground">•</span>
															<span>{post}</span>
														</li>
													))}
												</ul>
											</div>
										)}
									</div>
								</>
							)}
						</CardContent>
					</Card>
				</TabsContent>

				{/* Quality Metrics Tab */}
				<TabsContent value="quality" className="space-y-6 pt-6">
					<Card className="border-0 bg-card/50 p-6">
						<CardHeader className="px-0 pt-0">
							<CardTitle className="flex items-center gap-2">
								<Target className="h-5 w-5 text-purple-600" />
								Quality Dimensions (ISO 29148)
							</CardTitle>
							<CardDescription>
								Automated quality analysis based on industry standards
							</CardDescription>
						</CardHeader>
						<CardContent className="px-0 pb-0 space-y-6">
							{/* Quality Gauges */}
							<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
								<QualityGauge
									label="Verifiability"
									score={qualityScores.verifiability}
								/>
								<QualityGauge
									label="Traceability"
									score={qualityScores.traceability}
								/>
								<QualityGauge label="Clarity" score={qualityScores.clarity} />
							</div>

							{/* Additional Scores */}
							{(spec.ambiguity_score !== undefined ||
								spec.completeness_score !== undefined) && (
								<>
									<Separator />
									<div className="grid grid-cols-2 gap-4">
										{spec.ambiguity_score !== undefined && (
											<div className="space-y-2">
												<QualityGauge
													label="Ambiguity Score"
													score={1 - spec.ambiguity_score}
												/>
												<p className="text-xs text-muted-foreground">
													Lower is better (inverted for display)
												</p>
											</div>
										)}
										{spec.completeness_score !== undefined && (
											<div className="space-y-2">
												<QualityGauge
													label="Completeness"
													score={spec.completeness_score}
												/>
											</div>
										)}
									</div>
								</>
							)}

							{/* Quality Issues/Smells */}
							{spec.quality_issues && spec.quality_issues.length > 0 && (
								<>
									<Separator />
									<div className="space-y-3">
										<h4 className="text-sm font-black uppercase tracking-widest text-muted-foreground">
											Requirement Smells
										</h4>
										<div className="space-y-2">
											{spec.quality_issues.map((issue, i) => (
												<div
													key={i}
													className={cn(
														"p-3 rounded-lg flex items-start gap-3",
														issue.severity === "error"
															? "bg-red-500/10 border border-red-500/20"
															: (issue.severity === "warning"
																? "bg-yellow-500/10 border border-yellow-500/20"
																: "bg-blue-500/10 border border-blue-500/20"),
													)}
												>
													<AlertCircle
														className={cn(
															"h-4 w-4 shrink-0 mt-0.5",
															issue.severity === "error"
																? "text-red-600"
																: (issue.severity === "warning"
																	? "text-yellow-600"
																	: "text-blue-600"),
														)}
													/>
													<div className="flex-1 space-y-1">
														<p className="text-sm font-medium">
															{issue.message}
														</p>
														{issue.suggestion && (
															<p className="text-xs text-muted-foreground">
																{issue.suggestion}
															</p>
														)}
													</div>
												</div>
											))}
										</div>
									</div>
								</>
							)}
						</CardContent>
					</Card>
				</TabsContent>

				{/* Risk & Verification Tab */}
				<TabsContent value="risk" className="space-y-6 pt-6">
					<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
						{/* Risk Assessment */}
						<Card className="border-0 bg-card/50 p-6">
							<CardHeader className="px-0 pt-0">
								<CardTitle className="flex items-center gap-2">
									<Shield className="h-5 w-5 text-orange-600" />
									Risk Assessment
								</CardTitle>
							</CardHeader>
							<CardContent className="px-0 pb-0 space-y-4">
								<div className="flex items-center gap-3">
									<div
										className={cn(
											"h-16 w-16 rounded-2xl flex items-center justify-center",
											riskStyle.bg,
										)}
									>
										<RiskIcon className="h-8 w-8 text-white" />
									</div>
									<div>
										<div className="text-2xl font-black">{riskStyle.label}</div>
										<div className="text-sm text-muted-foreground">
											Risk Level
										</div>
									</div>
								</div>

								{spec.wsjf_score !== undefined && (
									<>
										<Separator />
										<div className="space-y-2">
											<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
												WSJF Score
											</h4>
											<div className="flex items-baseline gap-2">
												<div className="text-3xl font-black tabular-nums text-purple-600">
													{spec.wsjf_score.toFixed(1)}
												</div>
												<div className="text-sm text-muted-foreground">
													Weighted Shortest Job First
												</div>
											</div>
										</div>
									</>
								)}

								{spec.risk_factors && spec.risk_factors.length > 0 && (
									<>
										<Separator />
										<div className="space-y-2">
											<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
												Risk Factors
											</h4>
											<ul className="space-y-1">
												{spec.risk_factors.map((factor, i) => (
													<li
														key={i}
														className="flex items-start gap-2 text-sm"
													>
														<AlertTriangle className="h-4 w-4 text-orange-500 shrink-0 mt-0.5" />
														<span>{factor}</span>
													</li>
												))}
											</ul>
										</div>
									</>
								)}
							</CardContent>
						</Card>

						{/* Verification Status */}
						<Card className="border-0 bg-card/50 p-6">
							<CardHeader className="px-0 pt-0">
								<CardTitle className="flex items-center gap-2">
									<CheckCircle2 className="h-5 w-5 text-green-600" />
									Verification Status
								</CardTitle>
							</CardHeader>
							<CardContent className="px-0 pb-0 space-y-4">
								<div
									className={cn(
										"flex items-center gap-3 p-4 rounded-lg",
										verificationStyle.bg,
									)}
								>
									<VerificationIcon
										className={cn("h-6 w-6", verificationStyle.text)}
									/>
									<div>
										<div className="font-bold">{verificationStyle.label}</div>
										<div className="text-xs text-muted-foreground">
											Current status
										</div>
									</div>
								</div>

								{spec.verified_at && (
									<>
										<Separator />
										<div className="space-y-2">
											<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
												Verification Details
											</h4>
											<div className="space-y-1 text-sm">
												<div className="flex items-center justify-between">
													<span className="text-muted-foreground">
														Verified On
													</span>
													<span className="font-medium">
														{format(new Date(spec.verified_at), "PPP")}
													</span>
												</div>
												{spec.verified_by && (
													<div className="flex items-center justify-between">
														<span className="text-muted-foreground">
															Verified By
														</span>
														<span className="font-medium">
															{spec.verified_by}
														</span>
													</div>
												)}
											</div>
										</div>
									</>
								)}

								{/* Test Coverage Links */}
								<Separator />
								<div className="space-y-2">
									<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
										Test Coverage
									</h4>
									<Button variant="outline" size="sm" className="w-full">
										<Link2 className="h-4 w-4 mr-2" />
										View Linked Tests
									</Button>
								</div>
							</CardContent>
						</Card>
					</div>
				</TabsContent>

				{/* Traceability Tab */}
				<TabsContent value="traceability" className="space-y-6 pt-6">
					<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
						{/* Linked ADR */}
						<Card className="border-0 bg-card/50 p-6">
							<CardHeader className="px-0 pt-0">
								<CardTitle className="flex items-center gap-2 text-base">
									<BookText className="h-4 w-4 text-blue-600" />
									Linked Architecture Decision
								</CardTitle>
							</CardHeader>
							<CardContent className="px-0 pb-0">
								{item.adrId ? (
									<div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/20 flex items-center justify-between">
										<div className="space-y-1">
											<div className="font-medium">ADR #{item.adrId}</div>
											<div className="text-xs text-muted-foreground">
												Architecture Decision Record
											</div>
										</div>
										<Button variant="ghost" size="sm">
											<ArrowRight className="h-4 w-4" />
										</Button>
									</div>
								) : (
									<div className="text-sm text-muted-foreground text-center py-4">
										No ADR linked
									</div>
								)}
							</CardContent>
						</Card>

						{/* Linked Contract */}
						<Card className="border-0 bg-card/50 p-6">
							<CardHeader className="px-0 pt-0">
								<CardTitle className="flex items-center gap-2 text-base">
									<FileText className="h-4 w-4 text-purple-600" />
									Linked Contract
								</CardTitle>
							</CardHeader>
							<CardContent className="px-0 pb-0">
								{item.contractId ? (
									<div className="p-3 rounded-lg bg-purple-500/5 border border-purple-500/20 flex items-center justify-between">
										<div className="space-y-1">
											<div className="font-medium">
												Contract #{item.contractId}
											</div>
											<div className="text-xs text-muted-foreground">
												Design by Contract
											</div>
										</div>
										<Button variant="ghost" size="sm">
											<ArrowRight className="h-4 w-4" />
										</Button>
									</div>
								) : (
									<div className="text-sm text-muted-foreground text-center py-4">
										No contract linked
									</div>
								)}
							</CardContent>
						</Card>

						{/* Upstream/Downstream */}
						<Card className="border-0 bg-card/50 p-6">
							<CardHeader className="px-0 pt-0">
								<CardTitle className="flex items-center gap-2 text-base">
									<TrendingUp className="h-4 w-4 text-orange-600" />
									Upstream Requirements
								</CardTitle>
							</CardHeader>
							<CardContent className="px-0 pb-0">
								<div className="text-center py-4">
									<div className="text-3xl font-black tabular-nums text-orange-600">
										{spec.upstream_count}
									</div>
									<div className="text-xs text-muted-foreground mt-1">
										Parent requirements
									</div>
								</div>
							</CardContent>
						</Card>

						<Card className="border-0 bg-card/50 p-6">
							<CardHeader className="px-0 pt-0">
								<CardTitle className="flex items-center gap-2 text-base">
									<GitBranch className="h-4 w-4 text-green-600" />
									Downstream Impact
								</CardTitle>
							</CardHeader>
							<CardContent className="px-0 pb-0">
								<div className="text-center py-4">
									<div className="text-3xl font-black tabular-nums text-green-600">
										{spec.downstream_count}
									</div>
									<div className="text-xs text-muted-foreground mt-1">
										Child requirements
									</div>
								</div>
							</CardContent>
						</Card>
					</div>
				</TabsContent>

				{/* History Tab */}
				<TabsContent value="history" className="space-y-6 pt-6">
					<Card className="border-0 bg-card/50 p-6">
						<CardHeader className="px-0 pt-0">
							<CardTitle className="flex items-center gap-2">
								<Clock className="h-5 w-5 text-blue-600" />
								Change History
							</CardTitle>
							<CardDescription>
								Track requirement evolution and volatility
							</CardDescription>
						</CardHeader>
						<CardContent className="px-0 pb-0 space-y-4">
							<div className="grid grid-cols-3 gap-4">
								<div className="text-center space-y-1">
									<div className="text-2xl font-black tabular-nums">
										{spec.change_count}
									</div>
									<div className="text-xs text-muted-foreground">
										Total Changes
									</div>
								</div>
								{spec.volatility_index !== undefined && (
									<div className="text-center space-y-1">
										<div className="text-2xl font-black tabular-nums text-amber-600">
											{spec.volatility_index.toFixed(2)}
										</div>
										<div className="text-xs text-muted-foreground">
											Volatility Index
										</div>
									</div>
								)}
								{spec.last_changed_at && (
									<div className="text-center space-y-1">
										<div className="text-sm font-bold">
											{format(new Date(spec.last_changed_at), "MMM d")}
										</div>
										<div className="text-xs text-muted-foreground">
											Last Changed
										</div>
									</div>
								)}
							</div>

							<Separator />

							{/* Change History Timeline */}
							<div className="space-y-2">
								<h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
									Recent Changes
								</h4>
								<div className="text-sm text-muted-foreground text-center py-8">
									Change history visualization coming soon
								</div>
							</div>
						</CardContent>
					</Card>
				</TabsContent>
			</Tabs>
		</div>
	);
}
