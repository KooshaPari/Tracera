/**
 * Impact Analysis Graph Component
 * Visualizes the impact of changes on related items
 */

import { cn } from "@/lib/utils";

interface ImpactedItem {
	item_id: string;
	item_type: string;
	item_title: string;
	impact_type: "direct" | "transitive";
	impact_severity: "high" | "medium" | "low";
	distance: number;
}

interface ImpactAnalysisGraphProps {
	specId: string;
	directImpacts: ImpactedItem[];
	transitiveImpacts: ImpactedItem[];
	totalAffected: number;
	riskScore: number;
	riskCategory: string;
	byItemType?: Record<string, number>;
	bySeverity?: Record<string, number>;
	reviewRequired?: boolean;
	suggestedActions?: string[];
	className?: string;
}

const severityColors = {
	high: "bg-red-500",
	low: "bg-green-500",
	medium: "bg-yellow-500",
};

const typeIcons: Record<string, string> = {
	defect: "🐛",
	epic: "🏔",
	requirement: "📋",
	story: "📖",
	task: "✅",
	test: "🧪",
};

export function ImpactAnalysisGraph({
	specId,
	directImpacts,
	transitiveImpacts,
	totalAffected,
	riskScore,
	riskCategory,
	byItemType,
	bySeverity,
	reviewRequired,
	suggestedActions,
	className,
}: ImpactAnalysisGraphProps) {
	const riskColor =
		riskScore >= 0.7
			? "text-red-600"
			: riskScore >= 0.4
				? "text-orange-500"
				: riskScore >= 0.2
					? "text-yellow-600"
					: "text-green-600";

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-start justify-between">
				<div>
					<h3 className="text-lg font-semibold">Impact Analysis</h3>
					<p className="text-sm text-muted-foreground">
						{totalAffected} items affected by this change
					</p>
				</div>
				<div className="text-right">
					<div className={cn("text-2xl font-bold", riskColor)}>
						{Math.round(riskScore * 100)}%
					</div>
					<div className="text-sm text-muted-foreground capitalize">
						{riskCategory} Risk
					</div>
				</div>
			</div>

			{/* Review Warning */}
			{reviewRequired && (
				<div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-2">
					<span className="text-amber-600">⚠</span>
					<span className="text-sm text-amber-800">
						This change requires review due to high impact
					</span>
				</div>
			)}

			{/* Impact Summary */}
			<div className="grid grid-cols-2 md:grid-cols-4 gap-3">
				<div className="p-3 bg-muted rounded-lg text-center">
					<div className="text-xl font-bold">{directImpacts.length}</div>
					<div className="text-xs text-muted-foreground">Direct Impacts</div>
				</div>
				<div className="p-3 bg-muted rounded-lg text-center">
					<div className="text-xl font-bold">{transitiveImpacts.length}</div>
					<div className="text-xs text-muted-foreground">
						Transitive Impacts
					</div>
				</div>
				<div className="p-3 bg-muted rounded-lg text-center">
					<div className="text-xl font-bold">{totalAffected}</div>
					<div className="text-xs text-muted-foreground">Total Affected</div>
				</div>
				<div className="p-3 bg-muted rounded-lg text-center">
					<div className="text-xl font-bold">
						{Math.max(
							...[...directImpacts, ...transitiveImpacts].map(
								(i) => i.distance,
							),
							0,
						)}
					</div>
					<div className="text-xs text-muted-foreground">Max Depth</div>
				</div>
			</div>

			{/* By Type */}
			{byItemType && Object.keys(byItemType).length > 0 && (
				<div>
					<h4 className="text-sm font-medium mb-2">By Item Type</h4>
					<div className="flex flex-wrap gap-2">
						{Object.entries(byItemType).map(([type, count]) => (
							<div
								key={type}
								className="flex items-center gap-1.5 px-2 py-1 bg-muted rounded text-sm"
							>
								<span>{typeIcons[type] || "📄"}</span>
								<span className="capitalize">{type}</span>
								<span className="font-medium">({count})</span>
							</div>
						))}
					</div>
				</div>
			)}

			{/* By Severity */}
			{bySeverity && Object.keys(bySeverity).length > 0 && (
				<div>
					<h4 className="text-sm font-medium mb-2">By Severity</h4>
					<div className="flex gap-4">
						{Object.entries(bySeverity).map(([severity, count]) => (
							<div key={severity} className="flex items-center gap-2">
								<div
									className={cn(
										"w-3 h-3 rounded-full",
										severityColors[severity as keyof typeof severityColors] ||
											"bg-gray-500",
									)}
								/>
								<span className="text-sm capitalize">{severity}</span>
								<span className="text-sm font-medium">({count})</span>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Impact Visualization */}
			<div className="border rounded-lg p-4">
				<h4 className="text-sm font-medium mb-3">Impact Tree</h4>
				<div className="space-y-2">
					{/* Source Item */}
					<div className="flex items-center gap-2 p-2 bg-primary/10 rounded">
						<span className="text-lg">📌</span>
						<span className="font-medium">Source: {specId}</span>
					</div>

					{/* Direct Impacts */}
					{directImpacts.length > 0 && (
						<div className="ml-4 border-l-2 border-red-300 pl-4 space-y-1">
							<div className="text-xs font-medium text-red-600 mb-1">
								Direct Impacts ({directImpacts.length})
							</div>
							{directImpacts.slice(0, 5).map((item) => (
								<ImpactItem key={item.item_id} item={item} />
							))}
							{directImpacts.length > 5 && (
								<div className="text-xs text-muted-foreground">
									+{directImpacts.length - 5} more...
								</div>
							)}
						</div>
					)}

					{/* Transitive Impacts */}
					{transitiveImpacts.length > 0 && (
						<div className="ml-8 border-l-2 border-yellow-300 pl-4 space-y-1">
							<div className="text-xs font-medium text-yellow-600 mb-1">
								Transitive Impacts ({transitiveImpacts.length})
							</div>
							{transitiveImpacts.slice(0, 5).map((item) => (
								<ImpactItem key={item.item_id} item={item} />
							))}
							{transitiveImpacts.length > 5 && (
								<div className="text-xs text-muted-foreground">
									+{transitiveImpacts.length - 5} more...
								</div>
							)}
						</div>
					)}
				</div>
			</div>

			{/* Suggested Actions */}
			{suggestedActions && suggestedActions.length > 0 && (
				<div className="border-t pt-4">
					<h4 className="text-sm font-medium mb-2">Suggested Actions</h4>
					<ul className="space-y-1.5">
						{suggestedActions.map((action, idx) => (
							<li key={idx} className="flex items-start gap-2 text-sm">
								<span className="text-primary mt-0.5">→</span>
								<span>{action}</span>
							</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
}

function ImpactItem({ item }: { item: ImpactedItem }) {
	const icon = typeIcons[item.item_type] || "📄";
	const severityColor = severityColors[item.impact_severity];

	return (
		<div className="flex items-center gap-2 text-sm p-1.5 rounded hover:bg-muted">
			<div className={cn("w-2 h-2 rounded-full", severityColor)} />
			<span>{icon}</span>
			<span className="flex-1 truncate" title={item.item_title}>
				{item.item_title}
			</span>
			<span className="text-xs text-muted-foreground">d={item.distance}</span>
		</div>
	);
}

interface ImpactSummaryBadgeProps {
	totalAffected: number;
	riskScore: number;
	className?: string;
}

export function ImpactSummaryBadge({
	totalAffected,
	riskScore,
	className,
}: ImpactSummaryBadgeProps) {
	const riskColor =
		riskScore >= 0.7
			? "bg-red-100 text-red-700 border-red-300"
			: riskScore >= 0.4
				? "bg-orange-100 text-orange-700 border-orange-300"
				: riskScore >= 0.2
					? "bg-yellow-100 text-yellow-700 border-yellow-300"
					: "bg-green-100 text-green-700 border-green-300";

	return (
		<div
			className={cn(
				"inline-flex items-center gap-2 px-2.5 py-1 rounded-md border text-sm font-medium",
				riskColor,
				className,
			)}
		>
			<span>🔗</span>
			<span>{totalAffected} affected</span>
			<span className="opacity-70">•</span>
			<span>{Math.round(riskScore * 100)}% risk</span>
		</div>
	);
}
