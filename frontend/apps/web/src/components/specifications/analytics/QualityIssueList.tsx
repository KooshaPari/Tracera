/**
 * Quality Issue List Component
 * Displays a list of quality issues with severity indicators and suggestions
 */

import type {
	AnalyticsQualityIssue,
	QualityDimension,
} from "@/hooks/useItemSpecAnalytics";
import { cn } from "@/lib/utils";

interface QualityIssueListProps {
	issues: AnalyticsQualityIssue[];
	maxItems?: number;
	showSuggestions?: boolean;
	groupByDimension?: boolean;
	className?: string;
}

const severityConfig = {
	error: {
		label: "Error",
		icon: "✕",
		color: "text-red-600 bg-red-50 border-red-200",
		iconColor: "text-red-600",
	},
	warning: {
		label: "Warning",
		icon: "⚠",
		color: "text-yellow-700 bg-yellow-50 border-yellow-200",
		iconColor: "text-yellow-600",
	},
	info: {
		label: "Info",
		icon: "ℹ",
		color: "text-blue-600 bg-blue-50 border-blue-200",
		iconColor: "text-blue-600",
	},
};

const dimensionLabels: Record<QualityDimension, string> = {
	unambiguity: "Unambiguity",
	completeness: "Completeness",
	verifiability: "Verifiability",
	consistency: "Consistency",
	necessity: "Necessity",
	singularity: "Singularity",
	feasibility: "Feasibility",
	traceability: "Traceability",
};

export function QualityIssueList({
	issues,
	maxItems,
	showSuggestions = true,
	groupByDimension = false,
	className,
}: QualityIssueListProps) {
	const displayIssues = maxItems ? issues.slice(0, maxItems) : issues;
	const hasMore = maxItems && issues.length > maxItems;

	if (groupByDimension) {
		const grouped = displayIssues.reduce(
			(acc, issue) => {
				const dim = issue.dimension;
				if (!acc[dim]) acc[dim] = [];
				acc[dim].push(issue);
				return acc;
			},
			{} as Record<string, AnalyticsQualityIssue[]>,
		);

		return (
			<div className={cn("space-y-4", className)}>
				{Object.entries(grouped).map(([dimension, dimIssues]) => (
					<div key={dimension} className="space-y-2">
						<h4 className="text-sm font-semibold">
							{dimensionLabels[dimension as QualityDimension] || dimension}
						</h4>
						<div className="space-y-2 pl-2">
							{dimIssues.map((issue, idx) => (
								<QualityIssueItem
									key={idx}
									issue={issue}
									showSuggestion={showSuggestions}
									compact
								/>
							))}
						</div>
					</div>
				))}
				{hasMore && (
					<p className="text-sm text-muted-foreground">
						And {issues.length - maxItems} more issues...
					</p>
				)}
			</div>
		);
	}

	return (
		<div className={cn("space-y-2", className)}>
			{displayIssues.map((issue, idx) => (
				<QualityIssueItem
					key={idx}
					issue={issue}
					showSuggestion={showSuggestions}
				/>
			))}
			{hasMore && (
				<p className="text-sm text-muted-foreground">
					And {issues.length - maxItems} more issues...
				</p>
			)}
		</div>
	);
}

interface QualityIssueItemProps {
	issue: AnalyticsQualityIssue;
	showSuggestion?: boolean;
	compact?: boolean;
}

export function QualityIssueItem({
	issue,
	showSuggestion = true,
	compact = false,
}: QualityIssueItemProps) {
	const config = severityConfig[issue.severity];
	const dimensionLabel = dimensionLabels[issue.dimension] || issue.dimension;

	if (compact) {
		return (
			<div
				className={cn(
					"flex items-start gap-2 text-sm",
					config.color,
					"p-2 rounded border",
				)}
			>
				<span className={cn("flex-shrink-0", config.iconColor)}>
					{config.icon}
				</span>
				<div className="flex-1 min-w-0">
					<p className="break-words">{issue.message}</p>
					{showSuggestion && issue.suggestion && (
						<p className="text-xs mt-1 opacity-80">💡 {issue.suggestion}</p>
					)}
				</div>
			</div>
		);
	}

	return (
		<div className={cn("rounded-lg border p-3", config.color)}>
			<div className="flex items-start gap-3">
				<span className={cn("text-lg flex-shrink-0", config.iconColor)}>
					{config.icon}
				</span>
				<div className="flex-1 min-w-0">
					<div className="flex items-center gap-2 mb-1">
						<span className="font-medium">{config.label}</span>
						<span className="text-xs px-1.5 py-0.5 rounded bg-white/50">
							{dimensionLabel}
						</span>
						{issue.line_reference && (
							<span className="text-xs font-mono opacity-70">
								Line {issue.line_reference}
							</span>
						)}
					</div>
					<p className="text-sm break-words">{issue.message}</p>
					{showSuggestion && issue.suggestion && (
						<div className="mt-2 p-2 bg-white/30 rounded text-sm">
							<span className="font-medium">Suggestion: </span>
							{issue.suggestion}
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

interface QualityIssueSummaryProps {
	criticalCount: number;
	warningCount: number;
	infoCount?: number;
	className?: string;
}

export function QualityIssueSummary({
	criticalCount,
	warningCount,
	infoCount = 0,
	className,
}: QualityIssueSummaryProps) {
	return (
		<div className={cn("flex items-center gap-4 text-sm", className)}>
			{criticalCount > 0 && (
				<div className="flex items-center gap-1.5">
					<span className="text-red-600">{severityConfig.error.icon}</span>
					<span className="font-medium">{criticalCount}</span>
					<span className="text-muted-foreground">errors</span>
				</div>
			)}
			{warningCount > 0 && (
				<div className="flex items-center gap-1.5">
					<span className="text-yellow-600">{severityConfig.warning.icon}</span>
					<span className="font-medium">{warningCount}</span>
					<span className="text-muted-foreground">warnings</span>
				</div>
			)}
			{infoCount > 0 && (
				<div className="flex items-center gap-1.5">
					<span className="text-blue-600">{severityConfig.info.icon}</span>
					<span className="font-medium">{infoCount}</span>
					<span className="text-muted-foreground">info</span>
				</div>
			)}
			{criticalCount === 0 && warningCount === 0 && infoCount === 0 && (
				<div className="flex items-center gap-1.5 text-green-600">
					<span>✓</span>
					<span>No issues found</span>
				</div>
			)}
		</div>
	);
}
