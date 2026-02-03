/**
 * Priority Matrix Component
 * Visual prioritization matrix with MoSCoW and value/effort quadrants
 */

import type { MoSCoWPriority } from "@/hooks/useItemSpecAnalytics";
import { cn } from "@/lib/utils";

interface PriorityItem {
	id: string;
	title: string;
	priority?: MoSCoWPriority;
	wsjfScore?: number;
	riceScore?: number;
	value?: number;
	effort?: number;
}

interface PriorityMatrixProps {
	items: PriorityItem[];
	onItemClick?: (item: PriorityItem) => void;
	className?: string;
}

const moscowConfig: Record<
	MoSCoWPriority,
	{ label: string; color: string; description: string }
> = {
	could: {
		color: "bg-yellow-500",
		description: "Desirable features if time permits",
		label: "Could Have",
	},
	must: {
		color: "bg-red-500",
		description: "Critical requirements that must be implemented",
		label: "Must Have",
	},
	should: {
		color: "bg-orange-500",
		description: "Important features with high value",
		label: "Should Have",
	},
	wont: {
		color: "bg-gray-400",
		description: "Features explicitly excluded this time",
		label: "Won't Have",
	},
};

export function PriorityMatrix({
	items,
	onItemClick,
	className,
}: PriorityMatrixProps) {
	// Group items by MoSCoW priority
	const grouped = items.reduce(
		(acc, item) => {
			const priority = item.priority || "could";
			if (!acc[priority]) {
				acc[priority] = [];
			}
			acc[priority].push(item);
			return acc;
		},
		{} as Record<MoSCoWPriority, PriorityItem[]>,
	);

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			<div>
				<h3 className="text-lg font-semibold">Priority Matrix</h3>
				<p className="text-sm text-muted-foreground">
					MoSCoW prioritization of {items.length} items
				</p>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
				{(["must", "should", "could", "wont"] as const).map((priority) => {
					const config = moscowConfig[priority];
					const priorityItems = grouped[priority] || [];

					return (
						<div key={priority} className="rounded-lg border overflow-hidden">
							<div className={cn("px-3 py-2 text-white", config.color)}>
								<div className="font-medium">{config.label}</div>
								<div className="text-xs opacity-90">
									{priorityItems.length} items
								</div>
							</div>
							<div className="p-2 space-y-1 max-h-48 overflow-y-auto">
								{priorityItems.length === 0 ? (
									<div className="text-sm text-muted-foreground text-center py-4">
										No items
									</div>
								) : (
									priorityItems.map((item) => (
										<button
											key={item.id}
											onClick={() => onItemClick?.(item)}
											className="w-full text-left p-2 rounded hover:bg-muted transition-colors text-sm"
										>
											<div className="font-medium truncate">{item.title}</div>
											<div className="flex gap-2 text-xs text-muted-foreground">
												{item.wsjfScore !== undefined && (
													<span>WSJF: {item.wsjfScore.toFixed(1)}</span>
												)}
												{item.riceScore !== undefined && (
													<span>RICE: {item.riceScore.toFixed(0)}</span>
												)}
											</div>
										</button>
									))
								)}
							</div>
						</div>
					);
				})}
			</div>
		</div>
	);
}

interface ValueEffortMatrixProps {
	items: PriorityItem[];
	onItemClick?: (item: PriorityItem) => void;
	className?: string;
}

export function ValueEffortMatrix({
	items,
	onItemClick,
	className,
}: ValueEffortMatrixProps) {
	// Filter items with value and effort
	const validItems = items.filter(
		(item) => item.value !== undefined && item.effort !== undefined,
	);

	// Categorize into quadrants
	const quadrants = {
		bigBets: validItems.filter(
			(i) => (i.value ?? 0) >= 50 && (i.effort ?? 0) >= 50,
		),
		fillIns: validItems.filter(
			(i) => (i.value ?? 0) < 50 && (i.effort ?? 0) < 50,
		),
		quickWins: validItems.filter(
			(i) => (i.value ?? 0) >= 50 && (i.effort ?? 0) < 50,
		),
		thankless: validItems.filter(
			(i) => (i.value ?? 0) < 50 && (i.effort ?? 0) >= 50,
		),
	};

	const quadrantConfig = {
		bigBets: {
			color: "bg-blue-100 border-blue-300",
			description: "High Value, High Effort",
			label: "Big Bets",
		},
		fillIns: {
			color: "bg-yellow-100 border-yellow-300",
			description: "Low Value, Low Effort",
			label: "Fill-Ins",
		},
		quickWins: {
			color: "bg-green-100 border-green-300",
			description: "High Value, Low Effort",
			label: "Quick Wins",
		},
		thankless: {
			color: "bg-red-100 border-red-300",
			description: "Low Value, High Effort",
			label: "Thankless Tasks",
		},
	};

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			<div>
				<h3 className="text-lg font-semibold">Value/Effort Matrix</h3>
				<p className="text-sm text-muted-foreground">
					Prioritize by value vs effort trade-offs
				</p>
			</div>

			{/* Axis Labels */}
			<div className="relative">
				<div className="absolute -left-6 top-1/2 -translate-y-1/2 -rotate-90 text-xs text-muted-foreground">
					Value →
				</div>
				<div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-6 text-xs text-muted-foreground">
					Effort →
				</div>

				<div className="grid grid-cols-2 gap-2">
					{(["quickWins", "bigBets", "fillIns", "thankless"] as const).map(
						(quadrant) => {
							const config = quadrantConfig[quadrant];
							const quadrantItems = quadrants[quadrant];

							return (
								<div
									key={quadrant}
									className={cn(
										"rounded-lg border p-3 min-h-[120px]",
										config.color,
									)}
								>
									<div className="font-medium text-sm">{config.label}</div>
									<div className="text-xs text-muted-foreground mb-2">
										{config.description}
									</div>
									<div className="space-y-1">
										{quadrantItems.slice(0, 3).map((item) => (
											<button
												key={item.id}
												onClick={() => onItemClick?.(item)}
												className="w-full text-left px-2 py-1 rounded bg-white/50 hover:bg-white/80 text-xs truncate"
											>
												{item.title}
											</button>
										))}
										{quadrantItems.length > 3 && (
											<div className="text-xs text-muted-foreground pl-2">
												+{quadrantItems.length - 3} more
											</div>
										)}
									</div>
								</div>
							);
						},
					)}
				</div>
			</div>
		</div>
	);
}

interface MoSCoWBadgeProps {
	priority: MoSCoWPriority;
	rationale?: string | null;
	size?: "sm" | "md";
	className?: string;
}

export function MoSCoWBadge({
	priority,
	rationale,
	size = "md",
	className,
}: MoSCoWBadgeProps) {
	const config = moscowConfig[priority];
	const sizeClass =
		size === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-1";

	return (
		<span
			className={cn(
				"inline-flex items-center gap-1 rounded text-white font-medium",
				config.color,
				sizeClass,
				className,
			)}
			title={rationale || config.description}
		>
			{config.label}
		</span>
	);
}

interface PrioritizationSummaryProps {
	wsjfScore?: number | null;
	riceScore?: number | null;
	moscowPriority?: MoSCoWPriority | null;
	relativeRank?: number | null;
	totalItems?: number | null;
	className?: string;
}

export function PrioritizationSummary({
	wsjfScore,
	riceScore,
	moscowPriority,
	relativeRank,
	totalItems,
	className,
}: PrioritizationSummaryProps) {
	return (
		<div className={cn("flex flex-wrap gap-3", className)}>
			{moscowPriority && <MoSCoWBadge priority={moscowPriority} size="md" />}
			{wsjfScore !== undefined && wsjfScore !== null && (
				<span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-muted text-sm">
					<span>⚖</span>
					<span>WSJF: {wsjfScore.toFixed(2)}</span>
				</span>
			)}
			{riceScore !== undefined && riceScore !== null && (
				<span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-muted text-sm">
					<span>📊</span>
					<span>RICE: {riceScore.toFixed(0)}</span>
				</span>
			)}
			{relativeRank !== undefined && relativeRank !== null && totalItems && (
				<span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-muted text-sm">
					<span>🏆</span>
					<span>
						Rank: {relativeRank}/{totalItems}
					</span>
				</span>
			)}
		</div>
	);
}
