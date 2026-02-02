/**
 * ADRTimeline - Chronological visualization of Architecture Decision Records
 * Shows decision evolution over time with status transitions and links
 */

import type { ADR, ADRStatus } from "@tracertm/types";
import { Badge, Button, Card } from "@tracertm/ui";
import {
	AlertTriangle,
	Calendar,
	CheckCircle2,
	ChevronDown,
	ChevronUp,
	Clock,
	Filter,
	GitBranch,
	XCircle,
} from "lucide-react";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

interface ADRTimelineProps {
	adrs: ADR[];
	onADRClick?: (adr: ADR) => void;
	className?: string;
}

const STATUS_CONFIG: Record<
	ADRStatus,
	{ icon: typeof CheckCircle2; color: string; bg: string; line: string }
> = {
	proposed: {
		icon: Clock,
		color: "text-yellow-600",
		bg: "bg-yellow-500",
		line: "border-yellow-500/30",
	},
	accepted: {
		icon: CheckCircle2,
		color: "text-green-600",
		bg: "bg-green-500",
		line: "border-green-500/30",
	},
	deprecated: {
		icon: AlertTriangle,
		color: "text-orange-600",
		bg: "bg-orange-500",
		line: "border-orange-500/30",
	},
	superseded: {
		icon: GitBranch,
		color: "text-blue-600",
		bg: "bg-blue-500",
		line: "border-blue-500/30",
	},
	rejected: {
		icon: XCircle,
		color: "text-red-600",
		bg: "bg-red-500",
		line: "border-red-500/30",
	},
};

interface TimelineNode {
	adr: ADR;
	year: number;
	month: number;
	supersedes?: ADR | undefined;
}

export function ADRTimeline({ adrs, onADRClick, className }: ADRTimelineProps) {
	const [expandedId, setExpandedId] = useState<string | null>(null);
	const [statusFilter, setStatusFilter] = useState<ADRStatus | "all">("all");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

	// Group ADRs by year/month and sort
	const timelineData = useMemo(() => {
		const filtered =
			statusFilter === "all"
				? adrs
				: adrs.filter((a) => a.status === statusFilter);

		const sorted = [...filtered].toSorted((a, b) => {
			const dateA = new Date(a.date || a.createdAt).getTime();
			const dateB = new Date(b.date || b.createdAt).getTime();
			return sortOrder === "desc" ? dateB - dateA : dateA - dateB;
		});

		// Group by year
		const byYear: Record<number, TimelineNode[]> = {};
		for (const adr of sorted) {
			const date = new Date(adr.date || adr.createdAt);
			const year = date.getFullYear();
			const month = date.getMonth();

			if (!byYear[year]) byYear[year] = [];

			// Find superseded ADR
			const supersedes = adr.supersedes
				? adrs.find((a) => a.adrNumber === adr.supersedes)
				: undefined;

			byYear[year].push({ adr, year, month, supersedes });
		}

		return byYear;
	}, [adrs, statusFilter, sortOrder]);

	const years = Object.keys(timelineData)
		.map(Number)
		.toSorted((a, b) => (sortOrder === "desc" ? b - a : a - b));

	const monthNames = [
		"Jan",
		"Feb",
		"Mar",
		"Apr",
		"May",
		"Jun",
		"Jul",
		"Aug",
		"Sep",
		"Oct",
		"Nov",
		"Dec",
	];

	return (
		<div className={cn("space-y-6", className)}>
			{/* Controls */}
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<Filter className="h-4 w-4 text-muted-foreground" />
					<div className="flex gap-1">
						{(
							[
								"all",
								"accepted",
								"proposed",
								"deprecated",
								"superseded",
							] as const
						).map((status) => (
							<Button
								key={status}
								variant={statusFilter === status ? "default" : "ghost"}
								size="sm"
								className="h-7 text-xs capitalize"
								onClick={() => setStatusFilter(status)}
							>
								{status}
							</Button>
						))}
					</div>
				</div>

				<Button
					variant="outline"
					size="sm"
					className="h-7 text-xs gap-1"
					onClick={() => setSortOrder(sortOrder === "desc" ? "asc" : "desc")}
				>
					<Calendar className="h-3 w-3" />
					{sortOrder === "desc" ? "Newest First" : "Oldest First"}
					{sortOrder === "desc" ? (
						<ChevronDown className="h-3 w-3" />
					) : (
						<ChevronUp className="h-3 w-3" />
					)}
				</Button>
			</div>

			{/* Timeline */}
			<div className="relative">
				{years.map((year, yearIndex) => (
					<div key={year} className="relative">
						{/* Year marker */}
						<div className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm py-2 mb-4">
							<div className="flex items-center gap-3">
								<div className="h-px flex-1 bg-border" />
								<span className="text-lg font-black tracking-tight">
									{year}
								</span>
								<div className="h-px flex-1 bg-border" />
							</div>
						</div>

						{/* ADRs for this year */}
						<div className="relative pl-8 space-y-4 pb-8">
							{/* Vertical timeline line */}
							{yearIndex < years.length - 1 && (
								<div className="absolute left-[11px] top-0 bottom-0 w-px bg-border" />
							)}

							{(timelineData[year] || []).map((node, _index) => {
								const { adr, month, supersedes } = node;
								const config = STATUS_CONFIG[adr.status];
								const StatusIcon = config.icon;
								const isExpanded = expandedId === adr.id;

								return (
									<div key={adr.id} className="relative group">
										{/* Timeline dot */}
										<div
											className={cn(
												"absolute left-[-20px] top-4 w-6 h-6 rounded-full flex items-center justify-center z-10",
												config.bg,
												"ring-4 ring-background",
											)}
										>
											<StatusIcon className="h-3 w-3 text-white" />
										</div>

										{/* Connection line to superseded ADR */}
										{supersedes && (
											<div className="absolute left-[-8px] top-7 w-4 h-px border-t-2 border-dashed border-blue-500/50" />
										)}

										{/* ADR Card */}
										<Card
											className={cn(
												"transition-all cursor-pointer hover:shadow-md",
												"border-l-4",
												config.line,
											)}
											onClick={() => setExpandedId(isExpanded ? null : adr.id)}
										>
											<div className="p-4">
												{/* Header */}
												<div className="flex items-start justify-between gap-3">
													<div>
														<div className="flex items-center gap-2 mb-1">
															<span className="text-[10px] font-mono text-muted-foreground">
																{monthNames[month]} · {adr.adrNumber}
															</span>
															<Badge
																variant="outline"
																className={cn(
																	"text-[9px] h-4",
																	config.color,
																	"border-current",
																)}
															>
																{adr.status}
															</Badge>
														</div>
														<h4 className="font-semibold">{adr.title}</h4>
													</div>

													{adr.complianceScore !== undefined && (
														<div
															className={cn(
																"text-xs font-bold px-2 py-0.5 rounded-full",
																adr.complianceScore >= 80
																	? "bg-green-500/10 text-green-600"
																	: adr.complianceScore >= 60
																		? "bg-yellow-500/10 text-yellow-600"
																		: "bg-red-500/10 text-red-600",
															)}
														>
															{Math.round(adr.complianceScore)}%
														</div>
													)}
												</div>

												{/* Expanded content */}
												{isExpanded && (
													<div className="mt-4 pt-4 border-t border-border/50 space-y-3 animate-in fade-in slide-in-from-top-2 duration-200">
														{adr.context && (
															<div>
																<div className="text-[9px] font-black uppercase tracking-wider text-muted-foreground mb-1">
																	Context
																</div>
																<p className="text-sm text-muted-foreground">
																	{adr.context}
																</p>
															</div>
														)}

														{adr.decision && (
															<div className="bg-muted/30 rounded-lg p-3">
																<div className="text-[9px] font-black uppercase tracking-wider text-muted-foreground mb-1">
																	Decision
																</div>
																<p className="text-sm">{adr.decision}</p>
															</div>
														)}

														{supersedes && (
															<div className="flex items-center gap-2 text-xs text-blue-600">
																<GitBranch className="h-3 w-3" />
																<span>
																	Supersedes{" "}
																	<span className="font-mono">
																		{supersedes.adrNumber}
																	</span>
																	: {supersedes.title}
																</span>
															</div>
														)}

														<div className="flex justify-end pt-2">
															<Button
																size="sm"
																className="h-7 text-xs"
																onClick={(e) => {
																	e.stopPropagation();
																	onADRClick?.(adr);
																}}
															>
																View Details
															</Button>
														</div>
													</div>
												)}

												{/* Collapse indicator */}
												{!isExpanded && (adr.context || adr.decision) && (
													<p className="text-sm text-muted-foreground mt-2 line-clamp-1">
														{adr.context || adr.decision}
													</p>
												)}
											</div>
										</Card>
									</div>
								);
							})}
						</div>
					</div>
				))}

				{years.length === 0 && (
					<div className="text-center py-12 text-muted-foreground">
						<Calendar className="h-12 w-12 mx-auto mb-3 opacity-20" />
						<p className="text-sm">No ADRs match the current filter</p>
					</div>
				)}
			</div>
		</div>
	);
}
