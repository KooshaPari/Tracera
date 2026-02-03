/**
 * CoverageHeatmap - Requirement coverage visualization grid
 * Shows coverage intensity with hover details and click navigation
 */

import { motion } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface CoverageCell {
	id: string;
	label: string;
	coverage: number; // 0-100
	testCases?: number;
	adrs?: number;
	contracts?: number;
	linked?: boolean;
}

interface CoverageHeatmapProps {
	data: CoverageCell[];
	onCellClick?: (cell: CoverageCell) => void;
	columns?: number;
	className?: string;
}

function getCoverageColor(coverage: number): string {
	if (coverage >= 90) {
		return "bg-emerald-600";
	} // Full coverage
	if (coverage >= 70) {
		return "bg-emerald-500";
	}
	if (coverage >= 50) {
		return "bg-amber-500";
	}
	if (coverage >= 30) {
		return "bg-orange-500";
	}
	if (coverage >= 10) {
		return "bg-red-500";
	}
	return "bg-slate-300"; // No coverage
}

function getCoverageOpacity(coverage: number): string {
	if (coverage === 0) {
		return "opacity-30";
	}
	if (coverage < 20) {
		return "opacity-40";
	}
	if (coverage < 40) {
		return "opacity-60";
	}
	if (coverage < 60) {
		return "opacity-75";
	}
	return "opacity-100";
}

export function CoverageHeatmap({
	data,
	onCellClick,
	columns = 8,
	className,
}: CoverageHeatmapProps) {
	const [hoveredId, setHoveredId] = useState<string | null>(null);
	const [hoveredDetails, setHoveredDetails] = useState<CoverageCell | null>(
		null,
	);

	return (
		<motion.div
			className={cn("space-y-4", className)}
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			transition={{ duration: 0.3 }}
		>
			{/* Summary Stats */}
			<div className="grid grid-cols-4 gap-3 text-xs">
				<div className="bg-muted/30 rounded-lg p-3">
					<div className="text-muted-foreground">Total Items</div>
					<div className="text-xl font-bold">{data.length}</div>
				</div>
				<div className="bg-muted/30 rounded-lg p-3">
					<div className="text-muted-foreground">Avg Coverage</div>
					<div className="text-xl font-bold">
						{Math.round(
							data.reduce((sum, c) => sum + c.coverage, 0) / data.length,
						)}
						%
					</div>
				</div>
				<div className="bg-muted/30 rounded-lg p-3">
					<div className="text-muted-foreground">Fully Covered</div>
					<div className="text-xl font-bold">
						{data.filter((c) => c.coverage >= 90).length}
					</div>
				</div>
				<div className="bg-muted/30 rounded-lg p-3">
					<div className="text-muted-foreground">Uncovered</div>
					<div className="text-xl font-bold">
						{data.filter((c) => c.coverage === 0).length}
					</div>
				</div>
			</div>

			{/* Heatmap Grid */}
			<div className="border rounded-lg p-4 bg-card">
				<div
					className="gap-2 grid"
					style={{
						gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
					}}
				>
					{data.map((cell, idx) => (
						<motion.div
							key={cell.id}
							initial={{ opacity: 0, scale: 0.8 }}
							animate={{ opacity: 1, scale: 1 }}
							transition={{ delay: idx * 0.01 }}
							onMouseEnter={() => {
								setHoveredId(cell.id);
								setHoveredDetails(cell);
							}}
							onMouseLeave={() => {
								setHoveredId(null);
								setHoveredDetails(null);
							}}
							className="relative"
						>
							<motion.button
								onClick={() => onCellClick?.(cell)}
								className={cn(
									"w-full aspect-square rounded-lg transition-all",
									"border border-border/50 hover:border-primary",
									"cursor-pointer relative group overflow-hidden",
									getCoverageColor(cell.coverage),
									getCoverageOpacity(cell.coverage),
									"hover:ring-2 hover:ring-primary/50 hover:shadow-lg",
								)}
								whileHover={{ scale: 1.05 }}
								whileTap={{ scale: 0.95 }}
							>
								{/* Coverage percentage */}
								<div className="absolute inset-0 flex items-center justify-center">
									<span className="text-sm font-bold text-white drop-shadow-md">
										{cell.coverage}%
									</span>
								</div>

								{/* Hover indicator */}
								{hoveredId === cell.id && (
									<motion.div
										className="absolute inset-0 bg-white/10 backdrop-blur-sm flex items-center justify-center"
										initial={{ opacity: 0 }}
										animate={{ opacity: 1 }}
									>
										<ChevronRight className="w-4 h-4 text-white" />
									</motion.div>
								)}

								{/* Linked indicator */}
								{cell.linked && (
									<div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full ring-2 ring-white/30" />
								)}
							</motion.button>

							{/* Tooltip */}
							{hoveredDetails && hoveredDetails.id === cell.id && (
								<motion.div
									className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-popover border border-border rounded-lg shadow-lg p-3 w-72 z-50"
									initial={{ opacity: 0, y: 5 }}
									animate={{ opacity: 1, y: 0 }}
									exit={{ opacity: 0, y: 5 }}
								>
									<div className="space-y-3">
										<div>
											<div className="font-semibold text-sm">{cell.label}</div>
											<div className="text-xs text-muted-foreground">
												Requirement ID: {cell.id}
											</div>
										</div>

										<div className="grid grid-cols-3 gap-2 text-xs">
											<div>
												<div className="text-muted-foreground">Coverage</div>
												<div className="font-bold text-lg">
													{cell.coverage}%
												</div>
											</div>
											{cell.testCases !== undefined && (
												<div>
													<div className="text-muted-foreground">Tests</div>
													<div className="font-bold text-lg">
														{cell.testCases}
													</div>
												</div>
											)}
											{cell.adrs !== undefined && (
												<div>
													<div className="text-muted-foreground">ADRs</div>
													<div className="font-bold text-lg">{cell.adrs}</div>
												</div>
											)}
										</div>

										{cell.contracts !== undefined && (
											<div className="text-xs text-muted-foreground">
												{cell.contracts} contract(s) linked
											</div>
										)}

										{cell.coverage < 50 && (
											<div className="text-xs bg-amber-500/10 text-amber-700 rounded px-2 py-1 border border-amber-500/20">
												Low coverage - Consider adding tests or documentation
											</div>
										)}
									</div>
									<div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1 w-2 h-2 bg-popover border-r border-b border-border rotate-45" />
								</motion.div>
							)}
						</motion.div>
					))}
				</div>
			</div>

			{/* Legend */}
			<div className="flex flex-wrap gap-4 text-xs">
				<div className="flex items-center gap-2">
					<div className="w-4 h-4 rounded bg-emerald-600" />
					<span className="text-muted-foreground">&ge;90% (Excellent)</span>
				</div>
				<div className="flex items-center gap-2">
					<div className="w-4 h-4 rounded bg-amber-500" />
					<span className="text-muted-foreground">50-70% (Fair)</span>
				</div>
				<div className="flex items-center gap-2">
					<div className="w-4 h-4 rounded bg-red-500" />
					<span className="text-muted-foreground">&lt;30% (Poor)</span>
				</div>
				<div className="flex items-center gap-2">
					<div className="w-2 h-2 rounded-full bg-white ring-2 ring-white/30" />
					<span className="text-muted-foreground">Linked item</span>
				</div>
			</div>

			{/* Empty State */}
			{data.length === 0 && (
				<div className="text-center py-12 text-muted-foreground">
					<p className="text-sm">No requirements to display</p>
				</div>
			)}
		</motion.div>
	);
}
