// Advanced Filter Controls for Graph Visualization
// Provides multi-select filters for node types, perspectives, and attributes

import { Button } from "@tracertm/ui/components/Button";
import { Badge } from "@tracertm/ui/components/Badge";
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from "@tracertm/ui/components/Popover";
import { Separator } from "@tracertm/ui/components/Separator";
import { Check, ChevronDown, X } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { ENHANCED_TYPE_COLORS, PERSPECTIVE_CONFIGS } from "./types";
import type { GraphPerspective } from "./types";

interface FilterControlsProps {
	// Perspective filter
	perspective?: GraphPerspective;
	onPerspectiveChange?: (perspective: GraphPerspective) => void;

	// Node type filter
	nodeTypes?: string[];
	selectedNodeTypes?: string[];
	onNodeTypeFilterChange?: (types: string[]) => void;

	// Status filter (optional)
	statuses?: string[];
	selectedStatuses?: string[];
	onStatusFilterChange?: (statuses: string[]) => void;

	// Callbacks
	onClose?: () => void;
	className?: string;
}

export function FilterControls({
	perspective,
	onPerspectiveChange,
	nodeTypes = [],
	selectedNodeTypes = [],
	onNodeTypeFilterChange,
	statuses = [],
	selectedStatuses = [],
	onStatusFilterChange,
	onClose,
	className,
}: FilterControlsProps) {
	const [showPerspectives, setShowPerspectives] = useState(false);
	const [showNodeTypes, setShowNodeTypes] = useState(false);
	const [showStatuses, setShowStatuses] = useState(false);

	// Handle perspective selection
	const handlePerspectiveSelect = useCallback(
		(p: GraphPerspective) => {
			onPerspectiveChange?.(p);
			setShowPerspectives(false);
		},
		[onPerspectiveChange],
	);

	// Handle node type toggle
	const handleNodeTypeToggle = useCallback(
		(type: string) => {
			if (!onNodeTypeFilterChange) {
				return;
			}

			const newTypes = selectedNodeTypes.includes(type)
				? selectedNodeTypes.filter((t) => t !== type)
				: [...selectedNodeTypes, type];

			onNodeTypeFilterChange(newTypes);
		},
		[selectedNodeTypes, onNodeTypeFilterChange],
	);

	// Handle status toggle
	const handleStatusToggle = useCallback(
		(status: string) => {
			if (!onStatusFilterChange) {
				return;
			}

			const newStatuses = selectedStatuses.includes(status)
				? selectedStatuses.filter((s) => s !== status)
				: [...selectedStatuses, status];

			onStatusFilterChange(newStatuses);
		},
		[selectedStatuses, onStatusFilterChange],
	);

	// Clear all filters
	const handleClearAll = useCallback(() => {
		onPerspectiveChange?.("all");
		onNodeTypeFilterChange?.([]);
		onStatusFilterChange?.([]);
	}, [onPerspectiveChange, onNodeTypeFilterChange, onStatusFilterChange]);

	// Active filter count
	const activeFilterCount = useMemo(() => {
		let count = 0;
		if (perspective && perspective !== "all") count += 1;
		if (selectedNodeTypes.length > 0) count += 1;
		if (selectedStatuses.length > 0) count += 1;
		return count;
	}, [perspective, selectedNodeTypes, selectedStatuses]);

	// Current perspective config
	const currentPerspective = useMemo(
		() =>
			PERSPECTIVE_CONFIGS.find((c) => c.id === perspective) ||
			PERSPECTIVE_CONFIGS[0],
		[perspective],
	);

	return (
		<div className={`flex flex-col gap-3 ${className || ""}`}>
			<div className="flex items-center justify-between">
				<h3 className="text-sm font-medium">Filters</h3>
				<div className="flex items-center gap-2">
					{activeFilterCount > 0 && (
						<>
							<Badge variant="secondary" className="text-xs">
								{activeFilterCount} active
							</Badge>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleClearAll}
								className="h-7 text-xs"
							>
								Clear all
							</Button>
						</>
					)}
					{onClose && (
						<Button
							variant="ghost"
							size="sm"
							onClick={onClose}
							className="h-7 w-7 p-0"
						>
							<X className="h-3.5 w-3.5" />
						</Button>
					)}
				</div>
			</div>

			<div className="flex flex-wrap items-center gap-2">
				{/* Perspective filter */}
				{onPerspectiveChange && (
					<Popover open={showPerspectives} onOpenChange={setShowPerspectives}>
						<PopoverTrigger asChild>
							<Button
								variant="outline"
								size="sm"
								className="h-8 gap-2"
								style={{
									borderColor: currentPerspective?.color,
									color: currentPerspective?.color,
								}}
							>
								<span className="text-xs font-medium">
									{currentPerspective?.label || "All"}
								</span>
								<ChevronDown className="h-3 w-3 opacity-50" />
							</Button>
						</PopoverTrigger>
						<PopoverContent className="w-64 p-2" align="start">
							<div className="space-y-1">
								{PERSPECTIVE_CONFIGS.map((config) => (
									<button
										key={config.id}
										onClick={() => handlePerspectiveSelect(config.id)}
										className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md hover:bg-accent text-left transition-colors"
									>
										<div
											className="h-3 w-3 rounded-full shrink-0"
											style={{ backgroundColor: config.color }}
										/>
										<div className="flex-1 min-w-0">
											<div className="text-sm font-medium">{config.label}</div>
											<div className="text-xs text-muted-foreground truncate">
												{config.description}
											</div>
										</div>
										{perspective === config.id && (
											<Check className="h-4 w-4 text-primary shrink-0" />
										)}
									</button>
								))}
							</div>
						</PopoverContent>
					</Popover>
				)}

				<Separator orientation="vertical" className="h-6" />

				{/* Node type filter */}
				{onNodeTypeFilterChange && nodeTypes.length > 0 && (
					<Popover open={showNodeTypes} onOpenChange={setShowNodeTypes}>
						<PopoverTrigger asChild>
							<Button variant="outline" size="sm" className="h-8 gap-2">
								<span className="text-xs font-medium">
									Node Types
									{selectedNodeTypes.length > 0 && (
										<Badge variant="secondary" className="ml-1.5 text-xs px-1">
											{selectedNodeTypes.length}
										</Badge>
									)}
								</span>
								<ChevronDown className="h-3 w-3 opacity-50" />
							</Button>
						</PopoverTrigger>
						<PopoverContent className="w-64 p-2" align="start">
							<div className="space-y-1 max-h-64 overflow-y-auto">
								{nodeTypes.map((type) => {
									const isSelected = selectedNodeTypes.includes(type);
									const color = ENHANCED_TYPE_COLORS[type] || "#64748b";

									return (
										<button
											key={type}
											onClick={() => handleNodeTypeToggle(type)}
											className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md hover:bg-accent text-left transition-colors"
										>
											<div
												className="h-3 w-3 rounded shrink-0"
												style={{ backgroundColor: color }}
											/>
											<span className="flex-1 text-sm capitalize">
												{type.replaceAll(/_/g, " ")}
											</span>
											{isSelected && (
												<Check className="h-4 w-4 text-primary shrink-0" />
											)}
										</button>
									);
								})}
							</div>
						</PopoverContent>
					</Popover>
				)}

				{/* Status filter */}
				{onStatusFilterChange && statuses.length > 0 && (
					<>
						<Separator orientation="vertical" className="h-6" />
						<Popover open={showStatuses} onOpenChange={setShowStatuses}>
							<PopoverTrigger asChild>
								<Button variant="outline" size="sm" className="h-8 gap-2">
									<span className="text-xs font-medium">
										Status
										{selectedStatuses.length > 0 && (
											<Badge
												variant="secondary"
												className="ml-1.5 text-xs px-1"
											>
												{selectedStatuses.length}
											</Badge>
										)}
									</span>
									<ChevronDown className="h-3 w-3 opacity-50" />
								</Button>
							</PopoverTrigger>
							<PopoverContent className="w-48 p-2" align="start">
								<div className="space-y-1">
									{statuses.map((status) => {
										const isSelected = selectedStatuses.includes(status);

										return (
											<button
												key={status}
												onClick={() => handleStatusToggle(status)}
												className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md hover:bg-accent text-left transition-colors"
											>
												<span className="flex-1 text-sm capitalize">
													{status.replaceAll(/_/g, " ")}
												</span>
												{isSelected && (
													<Check className="h-4 w-4 text-primary shrink-0" />
												)}
											</button>
										);
									})}
								</div>
							</PopoverContent>
						</Popover>
					</>
				)}
			</div>

			{/* Active filters summary */}
			{activeFilterCount > 0 && (
				<div className="flex flex-wrap gap-1.5">
					{perspective && perspective !== "all" && (
						<Badge
							variant="secondary"
							className="text-xs gap-1"
							style={{
								backgroundColor: currentPerspective?.color + "20",
								color: currentPerspective?.color,
							}}
						>
							<span>{currentPerspective?.label}</span>
							<button
								onClick={() => onPerspectiveChange?.("all")}
								className="hover:opacity-70"
							>
								<X className="h-3 w-3" />
							</button>
						</Badge>
					)}

					{selectedNodeTypes.map((type) => {
						const color = ENHANCED_TYPE_COLORS[type] || "#64748b";
						return (
							<Badge
								key={type}
								variant="secondary"
								className="text-xs gap-1"
								style={{
									backgroundColor: color + "20",
									color: color,
								}}
							>
								<span className="capitalize">{type.replaceAll(/_/g, " ")}</span>
								<button
									onClick={() => handleNodeTypeToggle(type)}
									className="hover:opacity-70"
								>
									<X className="h-3 w-3" />
								</button>
							</Badge>
						);
					})}

					{selectedStatuses.map((status) => (
						<Badge key={status} variant="secondary" className="text-xs gap-1">
							<span className="capitalize">{status.replaceAll(/_/g, " ")}</span>
							<button
								onClick={() => handleStatusToggle(status)}
								className="hover:opacity-70"
							>
								<X className="h-3 w-3" />
							</button>
						</Badge>
					))}
				</div>
			)}
		</div>
	);
}
