/**
 * GapAnalysis - Uncovered items list with priority sorting
 * Shows items without test coverage, ADR links, or contracts
 */

import {
	Button,
	Card,
	CardContent,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import { motion } from "framer-motion";
import {
	AlertCircle,
	AlertTriangle,
	BookOpen,
	CheckCircle2,
	ChevronRight,
	FileText,
	Shield,
	Zap,
} from "lucide-react";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

interface GapItem {
	id: string;
	label: string;
	priority: "critical" | "high" | "medium" | "low";
	gapType: "no_tests" | "no_adr" | "no_contract" | "orphaned";
	affectedItems?: number;
	impact?: string;
	suggestion?: string;
	linkedResources?: Array<{
		type: "test_case" | "adr" | "contract";
		id: string;
		label: string;
	}>;
}

interface GapAnalysisProps {
	items: GapItem[];
	onItemClick?: (item: GapItem) => void;
	onCreateLink?: (gap: GapItem, resourceType: string) => void;
	className?: string;
}

const GAP_TYPE_CONFIG = {
	no_tests: {
		icon: AlertCircle,
		label: "No Test Coverage",
		color: "text-red-600",
		bg: "bg-red-50 dark:bg-red-900/20",
	},
	no_adr: {
		icon: FileText,
		label: "No ADR Link",
		color: "text-amber-600",
		bg: "bg-amber-50 dark:bg-amber-900/20",
	},
	no_contract: {
		icon: Shield,
		label: "No Contract",
		color: "text-blue-600",
		bg: "bg-blue-50 dark:bg-blue-900/20",
	},
	orphaned: {
		icon: AlertTriangle,
		label: "Orphaned Item",
		color: "text-purple-600",
		bg: "bg-purple-50 dark:bg-purple-900/20",
	},
};

const PRIORITY_CONFIG = {
	critical: {
		icon: AlertCircle,
		label: "Critical",
		color: "text-red-600",
		badge: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200",
	},
	high: {
		icon: AlertTriangle,
		label: "High",
		color: "text-orange-600",
		badge:
			"bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-200",
	},
	medium: {
		icon: AlertTriangle,
		label: "Medium",
		color: "text-yellow-600",
		badge:
			"bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200",
	},
	low: {
		icon: CheckCircle2,
		label: "Low",
		color: "text-blue-600",
		badge: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200",
	},
};

export function GapAnalysis({
	items,
	onItemClick,
	onCreateLink,
	className,
}: GapAnalysisProps) {
	const [sortBy, setSortBy] = useState<"priority" | "impact">("priority");
	const [selectedGapType, setSelectedGapType] = useState<"all" | string>("all");

	const sortedItems = useMemo(() => {
		let filtered = items;

		if (selectedGapType !== "all") {
			filtered = items.filter((item) => item.gapType === selectedGapType);
		}

		return [...filtered].sort((a: GapItem, b: GapItem) => {
			if (sortBy === "priority") {
				const priorityOrder = {
					critical: 0,
					high: 1,
					medium: 2,
					low: 3,
				};
				return priorityOrder[a.priority] - priorityOrder[b.priority];
			} else {
				return (b.affectedItems || 0) - (a.affectedItems || 0);
			}
		});
	}, [items, sortBy, selectedGapType]);

	const stats = useMemo(() => {
		return {
			totalGaps: items.length,
			critical: items.filter((i) => i.priority === "critical").length,
			highPriority: items.filter((i) => i.priority === "high").length,
			noTests: items.filter((i) => i.gapType === "no_tests").length,
			noAdr: items.filter((i) => i.gapType === "no_adr").length,
			noContract: items.filter((i) => i.gapType === "no_contract").length,
		};
	}, [items]);

	return (
		<motion.div
			className={cn("space-y-6", className)}
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			transition={{ duration: 0.3 }}
		>
			{/* Stats Cards */}
			<div className="grid grid-cols-2 md:grid-cols-6 gap-3">
				<Card>
					<CardContent className="pt-4">
						<div className="text-2xl font-bold text-red-600">
							{stats.totalGaps}
						</div>
						<p className="text-xs text-muted-foreground">Total Gaps</p>
					</CardContent>
				</Card>
				<Card>
					<CardContent className="pt-4">
						<div className="text-2xl font-bold text-red-700">
							{stats.critical}
						</div>
						<p className="text-xs text-muted-foreground">Critical</p>
					</CardContent>
				</Card>
				<Card>
					<CardContent className="pt-4">
						<div className="text-2xl font-bold text-orange-600">
							{stats.highPriority}
						</div>
						<p className="text-xs text-muted-foreground">High</p>
					</CardContent>
				</Card>
				<Card>
					<CardContent className="pt-4">
						<div className="text-2xl font-bold text-red-600">
							{stats.noTests}
						</div>
						<p className="text-xs text-muted-foreground">No Tests</p>
					</CardContent>
				</Card>
				<Card>
					<CardContent className="pt-4">
						<div className="text-2xl font-bold text-amber-600">
							{stats.noAdr}
						</div>
						<p className="text-xs text-muted-foreground">No ADR</p>
					</CardContent>
				</Card>
				<Card>
					<CardContent className="pt-4">
						<div className="text-2xl font-bold text-blue-600">
							{stats.noContract}
						</div>
						<p className="text-xs text-muted-foreground">No Contract</p>
					</CardContent>
				</Card>
			</div>

			{/* Filter Tabs */}
			<Tabs defaultValue="all" onValueChange={setSelectedGapType}>
				<TabsList className="w-full justify-start">
					<TabsTrigger value="all">All Gaps</TabsTrigger>
					<TabsTrigger value="no_tests">Missing Tests</TabsTrigger>
					<TabsTrigger value="no_adr">Missing ADR</TabsTrigger>
					<TabsTrigger value="no_contract">Missing Contract</TabsTrigger>
					<TabsTrigger value="orphaned">Orphaned</TabsTrigger>
				</TabsList>

				<div className="mt-4 flex items-center justify-between">
					<div className="text-sm text-muted-foreground">
						Showing {sortedItems.length} gap(s)
					</div>
					<div className="flex gap-2">
						<Button
							variant={sortBy === "priority" ? "default" : "outline"}
							size="sm"
							onClick={() => setSortBy("priority")}
						>
							By Priority
						</Button>
						<Button
							variant={sortBy === "impact" ? "default" : "outline"}
							size="sm"
							onClick={() => setSortBy("impact")}
						>
							By Impact
						</Button>
					</div>
				</div>

				<TabsContent value="all" className="space-y-3 mt-4">
					{sortedItems.length === 0 ? (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-8">
								<CheckCircle2 className="h-12 w-12 mx-auto mb-3 opacity-20" />
								<p>No gaps detected - excellent coverage!</p>
							</CardContent>
						</Card>
					) : (
						sortedItems.map((item: GapItem, idx: number) => (
							<motion.div
								key={item.id}
								initial={{ opacity: 0, x: -10 }}
								animate={{ opacity: 1, x: 0 }}
								transition={{ delay: idx * 0.05 }}
							>
								<GapCard
									item={item}
									onClick={() => onItemClick?.(item)}
									onCreateLink={(resourceType) =>
										onCreateLink?.(item, resourceType)
									}
								/>
							</motion.div>
						))
					)}
				</TabsContent>

				<TabsContent value="no_tests" className="space-y-3 mt-4">
					{sortedItems.length === 0 ? (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-8">
								<CheckCircle2 className="h-12 w-12 mx-auto mb-3 opacity-20" />
								<p>All items have test coverage!</p>
							</CardContent>
						</Card>
					) : (
						sortedItems.map((item: GapItem, idx: number) => (
							<motion.div
								key={item.id}
								initial={{ opacity: 0, x: -10 }}
								animate={{ opacity: 1, x: 0 }}
								transition={{ delay: idx * 0.05 }}
							>
								<GapCard
									item={item}
									onClick={() => onItemClick?.(item)}
									onCreateLink={(resourceType) =>
										onCreateLink?.(item, resourceType)
									}
								/>
							</motion.div>
						))
					)}
				</TabsContent>

				<TabsContent value="no_adr" className="space-y-3 mt-4">
					{sortedItems.length === 0 ? (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-8">
								<CheckCircle2 className="h-12 w-12 mx-auto mb-3 opacity-20" />
								<p>All items have ADR links!</p>
							</CardContent>
						</Card>
					) : (
						sortedItems.map((item: GapItem, idx: number) => (
							<motion.div
								key={item.id}
								initial={{ opacity: 0, x: -10 }}
								animate={{ opacity: 1, x: 0 }}
								transition={{ delay: idx * 0.05 }}
							>
								<GapCard
									item={item}
									onClick={() => onItemClick?.(item)}
									onCreateLink={(resourceType) =>
										onCreateLink?.(item, resourceType)
									}
								/>
							</motion.div>
						))
					)}
				</TabsContent>

				<TabsContent value="no_contract" className="space-y-3 mt-4">
					{sortedItems.length === 0 ? (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-8">
								<CheckCircle2 className="h-12 w-12 mx-auto mb-3 opacity-20" />
								<p>All items have contracts!</p>
							</CardContent>
						</Card>
					) : (
						sortedItems.map((item: GapItem, idx: number) => (
							<motion.div
								key={item.id}
								initial={{ opacity: 0, x: -10 }}
								animate={{ opacity: 1, x: 0 }}
								transition={{ delay: idx * 0.05 }}
							>
								<GapCard
									item={item}
									onClick={() => onItemClick?.(item)}
									onCreateLink={(resourceType) =>
										onCreateLink?.(item, resourceType)
									}
								/>
							</motion.div>
						))
					)}
				</TabsContent>

				<TabsContent value="orphaned" className="space-y-3 mt-4">
					{sortedItems.length === 0 ? (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-8">
								<CheckCircle2 className="h-12 w-12 mx-auto mb-3 opacity-20" />
								<p>No orphaned items found!</p>
							</CardContent>
						</Card>
					) : (
						sortedItems.map((item: GapItem, idx: number) => (
							<motion.div
								key={item.id}
								initial={{ opacity: 0, x: -10 }}
								animate={{ opacity: 1, x: 0 }}
								transition={{ delay: idx * 0.05 }}
							>
								<GapCard
									item={item}
									onClick={() => onItemClick?.(item)}
									onCreateLink={(resourceType) =>
										onCreateLink?.(item, resourceType)
									}
								/>
							</motion.div>
						))
					)}
				</TabsContent>
			</Tabs>
		</motion.div>
	);
}

interface GapCardProps {
	item: GapItem;
	onClick: () => void;
	onCreateLink: (resourceType: string) => void;
}

function GapCard({ item, onClick, onCreateLink }: GapCardProps) {
	const gapConfig = GAP_TYPE_CONFIG[item.gapType];
	const priorityConfig = PRIORITY_CONFIG[item.priority];
	const GapIcon = gapConfig.icon;

	return (
		<Card
			className="cursor-pointer hover:shadow-md transition-all border-l-4"
			style={{
				borderLeftColor: {
					critical: "#dc2626",
					high: "#ea580c",
					medium: "#eab308",
					low: "#0284c7",
				}[item.priority],
			}}
			onClick={onClick}
		>
			<CardContent className="pt-6">
				<div className="flex items-start justify-between gap-4">
					{/* Left: Icon and Content */}
					<div className="flex items-start gap-3 flex-1 min-w-0">
						<div className={cn("p-2 rounded-lg shrink-0 mt-0.5", gapConfig.bg)}>
							<GapIcon className={cn("w-4 h-4", gapConfig.color)} />
						</div>

						<div className="flex-1 min-w-0">
							<div className="flex items-center gap-2 mb-1">
								<h4 className="font-semibold truncate">{item.label}</h4>
								<span
									className={cn(
										"text-xs font-medium px-2 py-0.5 rounded-full shrink-0",
										priorityConfig.badge,
									)}
								>
									{priorityConfig.label}
								</span>
							</div>

							<p className="text-sm text-muted-foreground mb-2">
								{gapConfig.label}
							</p>

							{item.suggestion && (
								<p className="text-xs text-muted-foreground bg-muted/30 rounded px-2 py-1 mb-2">
									{item.suggestion}
								</p>
							)}

							{item.linkedResources && item.linkedResources.length > 0 && (
								<div className="flex flex-wrap gap-1">
									{item.linkedResources.map((resource) => (
										<span
											key={`${resource.type}-${resource.id}`}
											className="inline-flex items-center gap-1 text-xs bg-muted rounded px-2 py-1"
										>
											{resource.type === "test_case" && (
												<BookOpen className="w-3 h-3" />
											)}
											{resource.type === "adr" && (
												<FileText className="w-3 h-3" />
											)}
											{resource.type === "contract" && (
												<Shield className="w-3 h-3" />
											)}
											{resource.label}
										</span>
									))}
								</div>
							)}
						</div>
					</div>

					{/* Right: Actions */}
					<div className="flex items-center gap-1 shrink-0">
						{item.affectedItems && (
							<div className="text-right mr-2">
								<div className="text-xs text-muted-foreground">Affects</div>
								<div className="font-bold text-sm">{item.affectedItems}</div>
							</div>
						)}
						<ChevronRight className="w-4 h-4 text-muted-foreground" />
					</div>
				</div>

				{/* Quick Actions */}
				<div className="flex gap-2 mt-3 pt-3 border-t border-border/50">
					<Button
						variant="ghost"
						size="sm"
						className="text-xs h-7"
						onClick={(e) => {
							e.stopPropagation();
							onCreateLink("test_case");
						}}
					>
						<Zap className="w-3 h-3 mr-1" />
						Add Test
					</Button>
					<Button
						variant="ghost"
						size="sm"
						className="text-xs h-7"
						onClick={(e) => {
							e.stopPropagation();
							onCreateLink("adr");
						}}
					>
						<FileText className="w-3 h-3 mr-1" />
						Link ADR
					</Button>
					<Button
						variant="ghost"
						size="sm"
						className="text-xs h-7"
						onClick={(e) => {
							e.stopPropagation();
							onCreateLink("contract");
						}}
					>
						<Shield className="w-3 h-3 mr-1" />
						Add Contract
					</Button>
				</div>
			</CardContent>
		</Card>
	);
}
