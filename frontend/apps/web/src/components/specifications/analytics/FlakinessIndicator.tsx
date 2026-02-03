/**
 * Flakiness Indicator Component
 * Displays test flakiness probability and patterns based on Meta's model
 */

import type { FlakinessPattern } from "@/hooks/useItemSpecAnalytics";
import { cn } from "@/lib/utils";

interface FlakinessIndicatorProps {
	probability: number;
	pattern?: FlakinessPattern | null;
	quarantineRecommended?: boolean;
	className?: string;
}

const patternLabels: Record<
	FlakinessPattern,
	{ label: string; description: string; icon: string }
> = {
	async: {
		description: "Asynchronous operation handling issues",
		icon: "⟳",
		label: "Async",
	},
	environment: {
		description: "Environment-specific configuration issues",
		icon: "🌍",
		label: "Environment",
	},
	network: {
		description: "Network connectivity or latency issues",
		icon: "🌐",
		label: "Network",
	},
	order_dependent: {
		description: "Test execution order dependencies",
		icon: "📋",
		label: "Order Dependent",
	},
	random: {
		description: "Random or non-deterministic behavior",
		icon: "🎲",
		label: "Random",
	},
	resource: {
		description: "Resource contention or availability issues",
		icon: "💾",
		label: "Resource",
	},
	timing: {
		description: "Race conditions or timeout issues",
		icon: "⏱",
		label: "Timing",
	},
};

function getProbabilityColor(probability: number): string {
	if (probability >= 0.7) {
		return "text-red-600";
	}
	if (probability >= 0.4) {
		return "text-orange-500";
	}
	if (probability >= 0.2) {
		return "text-yellow-600";
	}
	return "text-green-600";
}

function getProbabilityBgColor(probability: number): string {
	if (probability >= 0.7) {
		return "bg-red-500";
	}
	if (probability >= 0.4) {
		return "bg-orange-500";
	}
	if (probability >= 0.2) {
		return "bg-yellow-500";
	}
	return "bg-green-500";
}

function getProbabilityLabel(probability: number): string {
	if (probability >= 0.7) {
		return "High";
	}
	if (probability >= 0.4) {
		return "Medium";
	}
	if (probability >= 0.2) {
		return "Low";
	}
	return "Minimal";
}

export function FlakinessIndicator({
	probability,
	pattern,
	quarantineRecommended,
	className,
}: FlakinessIndicatorProps) {
	const percentage = Math.round(probability * 100);
	const colorClass = getProbabilityColor(probability);
	const bgColorClass = getProbabilityBgColor(probability);
	const label = getProbabilityLabel(probability);

	return (
		<div className={cn("flex items-center gap-3", className)}>
			{/* Gauge */}
			<div className="relative w-16 h-16">
				<svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
					{/* Background circle */}
					<circle
						cx="18"
						cy="18"
						r="16"
						fill="none"
						stroke="currentColor"
						strokeWidth="3"
						className="text-muted"
					/>
					{/* Progress arc */}
					<circle
						cx="18"
						cy="18"
						r="16"
						fill="none"
						stroke="currentColor"
						strokeWidth="3"
						strokeDasharray={`${percentage} 100`}
						strokeLinecap="round"
						className={bgColorClass.replace("bg-", "text-")}
					/>
				</svg>
				<div className="absolute inset-0 flex items-center justify-center">
					<span className={cn("text-sm font-bold", colorClass)}>
						{percentage}%
					</span>
				</div>
			</div>

			{/* Details */}
			<div className="flex-1">
				<div className="flex items-center gap-2">
					<span className={cn("font-semibold", colorClass)}>
						{label} Flakiness
					</span>
					{quarantineRecommended && (
						<span className="px-1.5 py-0.5 text-xs bg-red-100 text-red-700 rounded font-medium">
							Quarantine Recommended
						</span>
					)}
				</div>
				{pattern && (
					<div className="flex items-center gap-1.5 text-sm text-muted-foreground mt-1">
						<span>{patternLabels[pattern].icon}</span>
						<span>{patternLabels[pattern].label}</span>
						<span className="text-xs">
							- {patternLabels[pattern].description}
						</span>
					</div>
				)}
			</div>
		</div>
	);
}

interface FlakinessDetailCardProps {
	probability: number;
	entropy: number;
	pattern?: FlakinessPattern | null;
	patternConfidence?: number;
	contributingFactors?: {
		factor: string;
		weight: number;
		evidence: string | null;
	}[];
	recentRuns?: number;
	flakyRuns?: number;
	passRate?: number;
	quarantineRecommended?: boolean;
	recommendationReason?: string | null;
	className?: string;
}

export function FlakinessDetailCard({
	probability,
	entropy,
	pattern,
	patternConfidence,
	contributingFactors,
	recentRuns,
	flakyRuns,
	passRate,
	quarantineRecommended,
	recommendationReason,
	className,
}: FlakinessDetailCardProps) {
	const bgColorClass = getProbabilityBgColor(probability);

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-start justify-between">
				<FlakinessIndicator
					probability={probability}
					pattern={pattern ?? null}
					quarantineRecommended={quarantineRecommended ?? false}
				/>
			</div>

			{/* Stats */}
			<div className="grid grid-cols-3 gap-4 text-center">
				<div className="p-2 bg-muted rounded">
					<div className="text-lg font-semibold">{recentRuns ?? "-"}</div>
					<div className="text-xs text-muted-foreground">Recent Runs</div>
				</div>
				<div className="p-2 bg-muted rounded">
					<div className="text-lg font-semibold">{flakyRuns ?? "-"}</div>
					<div className="text-xs text-muted-foreground">Flaky Runs</div>
				</div>
				<div className="p-2 bg-muted rounded">
					<div className="text-lg font-semibold">
						{passRate !== undefined ? `${Math.round(passRate * 100)}%` : "-"}
					</div>
					<div className="text-xs text-muted-foreground">Pass Rate</div>
				</div>
			</div>

			{/* Entropy */}
			<div>
				<div className="flex justify-between text-sm mb-1">
					<span className="text-muted-foreground">Entropy Score</span>
					<span className="font-medium">{entropy.toFixed(3)}</span>
				</div>
				<div className="h-2 bg-muted rounded-full overflow-hidden">
					<div
						className={cn("h-full rounded-full", bgColorClass)}
						style={{ width: `${Math.min(entropy * 100, 100)}%` }}
					/>
				</div>
				<p className="text-xs text-muted-foreground mt-1">
					Higher entropy indicates more unpredictable behavior
				</p>
			</div>

			{/* Pattern Details */}
			{pattern && (
				<div className="p-3 bg-muted rounded-lg">
					<div className="flex items-center gap-2 mb-2">
						<span className="text-lg">{patternLabels[pattern].icon}</span>
						<span className="font-medium">
							{patternLabels[pattern].label} Pattern
						</span>
						{patternConfidence !== undefined && (
							<span className="text-sm text-muted-foreground">
								({Math.round(patternConfidence * 100)}% confidence)
							</span>
						)}
					</div>
					<p className="text-sm text-muted-foreground">
						{patternLabels[pattern].description}
					</p>
				</div>
			)}

			{/* Contributing Factors */}
			{contributingFactors && contributingFactors.length > 0 && (
				<div>
					<h4 className="text-sm font-medium mb-2">Contributing Factors</h4>
					<ul className="space-y-1.5">
						{contributingFactors.map((factor, idx) => (
							<li key={idx} className="flex items-start gap-2 text-sm">
								<div
									className={cn(
										"w-2 h-2 rounded-full mt-1.5 flex-shrink-0",
										factor.weight > 0.5
											? "bg-red-500"
											: (factor.weight > 0.25
												? "bg-yellow-500"
												: "bg-gray-400"),
									)}
								/>
								<div>
									<span className="font-medium">{factor.factor}</span>
									{factor.evidence && (
										<span className="text-muted-foreground">
											{" "}
											- {factor.evidence}
										</span>
									)}
								</div>
							</li>
						))}
					</ul>
				</div>
			)}

			{/* Quarantine Recommendation */}
			{quarantineRecommended && recommendationReason && (
				<div className="p-3 bg-red-50 border border-red-200 rounded-lg">
					<div className="flex items-center gap-2 text-red-700 font-medium mb-1">
						<span>⚠</span>
						<span>Quarantine Recommended</span>
					</div>
					<p className="text-sm text-red-600">{recommendationReason}</p>
				</div>
			)}
		</div>
	);
}
