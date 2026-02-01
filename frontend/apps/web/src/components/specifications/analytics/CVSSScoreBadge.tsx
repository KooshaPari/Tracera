/**
 * CVSS Score Badge Component
 * Displays Common Vulnerability Scoring System scores for security defects
 */

import type { CVSSSeverity } from "@/hooks/useItemSpecAnalytics";
import { cn } from "@/lib/utils";

interface CVSSScoreBadgeProps {
	baseScore: number;
	severity: CVSSSeverity;
	vector?: string;
	size?: "sm" | "md" | "lg";
	showVector?: boolean;
	className?: string;
}

const severityConfig: Record<
	CVSSSeverity,
	{ label: string; color: string; bg: string }
> = {
	none: {
		label: "None",
		color: "text-gray-700",
		bg: "bg-gray-100 border-gray-300",
	},
	low: {
		label: "Low",
		color: "text-green-700",
		bg: "bg-green-100 border-green-300",
	},
	medium: {
		label: "Medium",
		color: "text-yellow-700",
		bg: "bg-yellow-100 border-yellow-300",
	},
	high: {
		label: "High",
		color: "text-orange-700",
		bg: "bg-orange-100 border-orange-300",
	},
	critical: {
		label: "Critical",
		color: "text-red-700",
		bg: "bg-red-100 border-red-300",
	},
};

const sizeConfig = {
	sm: { badge: "text-xs px-2 py-0.5", score: "text-sm" },
	md: { badge: "text-sm px-2.5 py-1", score: "text-lg" },
	lg: { badge: "text-base px-3 py-1.5", score: "text-2xl" },
};

export function CVSSScoreBadge({
	baseScore,
	severity,
	vector,
	size = "md",
	showVector = false,
	className,
}: CVSSScoreBadgeProps) {
	const config = severityConfig[severity];
	const sizeClasses = sizeConfig[size];

	return (
		<div className={cn("inline-flex items-center gap-2", className)}>
			<div
				className={cn(
					"inline-flex items-center gap-1.5 rounded-md border font-medium",
					config.bg,
					config.color,
					sizeClasses.badge,
				)}
			>
				<span className={cn("font-bold", sizeClasses.score)}>
					{baseScore.toFixed(1)}
				</span>
				<span>{config.label}</span>
			</div>
			{showVector && vector && (
				<code className="text-xs bg-slate-100 px-2 py-1 rounded font-mono">
					{vector}
				</code>
			)}
		</div>
	);
}

interface CVSSScoreGaugeProps {
	baseScore: number;
	severity: CVSSSeverity;
	size?: number;
	className?: string;
}

export function CVSSScoreGauge({
	baseScore,
	severity,
	size = 80,
	className,
}: CVSSScoreGaugeProps) {
	const config = severityConfig[severity];
	const percentage = (baseScore / 10) * 100;

	// Calculate the stroke dasharray for the arc
	const radius = (size - 8) / 2;
	const circumference = 2 * Math.PI * radius;
	const arcLength = circumference * 0.75; // 270 degrees
	const filledLength = (arcLength * percentage) / 100;

	return (
		<div
			className={cn(
				"relative inline-flex items-center justify-center",
				className,
			)}
			style={{ width: size, height: size }}
		>
			<svg viewBox={`0 0 ${size} ${size}`} className="transform -rotate-135">
				{/* Background arc */}
				<circle
					cx={size / 2}
					cy={size / 2}
					r={radius}
					fill="none"
					stroke="currentColor"
					strokeWidth="4"
					strokeDasharray={`${arcLength} ${circumference}`}
					className="text-muted"
				/>
				{/* Filled arc */}
				<circle
					cx={size / 2}
					cy={size / 2}
					r={radius}
					fill="none"
					stroke="currentColor"
					strokeWidth="4"
					strokeDasharray={`${filledLength} ${circumference}`}
					strokeLinecap="round"
					className={config.color
						.replace("text-", "text-")
						.replace("-700", "-500")}
				/>
			</svg>
			<div className="absolute inset-0 flex flex-col items-center justify-center">
				<span className={cn("font-bold text-lg", config.color)}>
					{baseScore.toFixed(1)}
				</span>
				<span className="text-xs text-muted-foreground">{config.label}</span>
			</div>
		</div>
	);
}

interface CVSSDetailCardProps {
	baseScore: number;
	severity: CVSSSeverity;
	vector: string;
	breakdown: {
		attack_vector: string;
		attack_complexity: string;
		privileges_required: string;
		user_interaction: string;
		scope: string;
		confidentiality_impact: string;
		integrity_impact: string;
		availability_impact: string;
	};
	temporalScore?: number | null;
	environmentalScore?: number | null;
	remediationLevel?: string | null;
	className?: string;
}

export function CVSSDetailCard({
	baseScore,
	severity,
	vector,
	breakdown,
	temporalScore,
	environmentalScore,
	remediationLevel,
	className,
}: CVSSDetailCardProps) {
	const config = severityConfig[severity];

	const baseMetrics = [
		{ label: "Attack Vector", value: breakdown.attack_vector, abbr: "AV" },
		{
			label: "Attack Complexity",
			value: breakdown.attack_complexity,
			abbr: "AC",
		},
		{
			label: "Privileges Required",
			value: breakdown.privileges_required,
			abbr: "PR",
		},
		{
			label: "User Interaction",
			value: breakdown.user_interaction,
			abbr: "UI",
		},
	];

	const impactMetrics = [
		{ label: "Scope", value: breakdown.scope, abbr: "S" },
		{
			label: "Confidentiality",
			value: breakdown.confidentiality_impact,
			abbr: "C",
		},
		{ label: "Integrity", value: breakdown.integrity_impact, abbr: "I" },
		{ label: "Availability", value: breakdown.availability_impact, abbr: "A" },
	];

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-start justify-between">
				<div>
					<h3 className="text-sm font-medium text-muted-foreground mb-2">
						CVSS v3.1 Score
					</h3>
					<CVSSScoreBadge baseScore={baseScore} severity={severity} size="lg" />
				</div>
				<CVSSScoreGauge baseScore={baseScore} severity={severity} />
			</div>

			{/* Vector String */}
			<div className="p-2 bg-muted rounded">
				<div className="text-xs text-muted-foreground mb-1">Vector String</div>
				<code className="text-xs font-mono break-all">{vector}</code>
			</div>

			{/* Scores */}
			<div className="grid grid-cols-3 gap-3">
				<div className={cn("p-3 rounded-lg text-center border", config.bg)}>
					<div className={cn("text-xl font-bold", config.color)}>
						{baseScore.toFixed(1)}
					</div>
					<div className="text-xs text-muted-foreground">Base</div>
				</div>
				<div className="p-3 rounded-lg text-center bg-muted">
					<div className="text-xl font-bold">
						{temporalScore?.toFixed(1) ?? "-"}
					</div>
					<div className="text-xs text-muted-foreground">Temporal</div>
				</div>
				<div className="p-3 rounded-lg text-center bg-muted">
					<div className="text-xl font-bold">
						{environmentalScore?.toFixed(1) ?? "-"}
					</div>
					<div className="text-xs text-muted-foreground">Environmental</div>
				</div>
			</div>

			{/* Breakdown */}
			<div className="grid grid-cols-2 gap-4">
				{/* Exploitability Metrics */}
				<div>
					<h4 className="text-xs font-medium text-muted-foreground mb-2">
						Exploitability Metrics
					</h4>
					<div className="space-y-1.5">
						{baseMetrics.map((metric) => (
							<div key={metric.abbr} className="flex justify-between text-sm">
								<span className="text-muted-foreground">{metric.label}</span>
								<span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
									{metric.value}
								</span>
							</div>
						))}
					</div>
				</div>

				{/* Impact Metrics */}
				<div>
					<h4 className="text-xs font-medium text-muted-foreground mb-2">
						Impact Metrics
					</h4>
					<div className="space-y-1.5">
						{impactMetrics.map((metric) => (
							<div key={metric.abbr} className="flex justify-between text-sm">
								<span className="text-muted-foreground">{metric.label}</span>
								<span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
									{metric.value}
								</span>
							</div>
						))}
					</div>
				</div>
			</div>

			{/* Remediation Level */}
			{remediationLevel && (
				<div className="border-t pt-3">
					<div className="flex items-center justify-between text-sm">
						<span className="text-muted-foreground">Remediation Level</span>
						<span className="font-medium capitalize">{remediationLevel}</span>
					</div>
				</div>
			)}
		</div>
	);
}
