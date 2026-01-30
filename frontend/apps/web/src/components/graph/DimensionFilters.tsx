// DimensionFilters.tsx - Filter/highlight nodes by orthogonal dimensions
// Dimensions are cross-cutting concerns (maturity, complexity, coverage, risk)
// that apply to items regardless of their perspective

import { Button } from "@tracertm/ui/components/Button";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from "@tracertm/ui/components/Popover";
import { Badge } from "@tracertm/ui/components/Badge";
import { Slider } from "@tracertm/ui/components/Slider";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import {
	Activity,
	AlertTriangle,
	Boxes,
	CheckCircle2,
	Eye,
	EyeOff,
	Filter,
	Highlighter,
	Layers,
	Palette,
	Target,
	TrendingUp,
	X,
} from "lucide-react";
import { memo, useCallback, useState } from "react";
import type {
	DimensionFilter,
	DimensionDisplayMode,
	MaturityLevel,
	ComplexityLevel,
	RiskLevel,
} from "@tracertm/types";

// =============================================================================
// TYPES
// =============================================================================

export interface DimensionFiltersProps {
	/** Currently active dimension filters */
	activeFilters: DimensionFilter[];
	/** Callback when filters change */
	onFiltersChange: (filters: DimensionFilter[]) => void;
	/** How to display matching items */
	displayMode: DimensionDisplayMode;
	/** Callback when display mode changes */
	onDisplayModeChange: (mode: DimensionDisplayMode) => void;
	/** Whether the filters panel is expanded */
	isExpanded?: boolean;
	/** Compact mode for toolbar */
	compact?: boolean;
}

interface DimensionConfig {
	id: keyof DimensionValues;
	label: string;
	icon: React.ComponentType<{ className?: string }>;
	color: string;
	type: "enum" | "range";
	values?: string[];
	min?: number;
	max?: number;
}

interface DimensionValues {
	maturity: MaturityLevel;
	complexity: ComplexityLevel;
	coverage: number;
	risk: RiskLevel;
}

// =============================================================================
// CONFIGURATION
// =============================================================================

const DIMENSION_CONFIGS: DimensionConfig[] = [
	{
		id: "maturity",
		label: "Maturity",
		icon: TrendingUp,
		color: "#3b82f6",
		type: "enum",
		values: [
			"idea",
			"draft",
			"defined",
			"implemented",
			"verified",
			"stable",
			"deprecated",
		],
	},
	{
		id: "complexity",
		label: "Complexity",
		icon: Boxes,
		color: "#f59e0b",
		type: "enum",
		values: ["trivial", "simple", "moderate", "complex", "very_complex"],
	},
	{
		id: "coverage",
		label: "Coverage",
		icon: Target,
		color: "#22c55e",
		type: "range",
		min: 0,
		max: 100,
	},
	{
		id: "risk",
		label: "Risk",
		icon: AlertTriangle,
		color: "#ef4444",
		type: "enum",
		values: ["none", "low", "medium", "high", "critical"],
	},
];

const DISPLAY_MODE_OPTIONS: {
	id: DimensionDisplayMode;
	label: string;
	icon: React.ComponentType<{ className?: string }>;
}[] = [
	{ id: "filter", label: "Filter", icon: Filter },
	{ id: "highlight", label: "Highlight", icon: Highlighter },
	{ id: "color", label: "Color", icon: Palette },
	{ id: "size", label: "Size", icon: Layers },
];

const MATURITY_COLORS: Record<MaturityLevel, string> = {
	idea: "#94a3b8",
	draft: "#64748b",
	defined: "#3b82f6",
	implemented: "#8b5cf6",
	verified: "#22c55e",
	stable: "#10b981",
	deprecated: "#ef4444",
};

const COMPLEXITY_COLORS: Record<ComplexityLevel, string> = {
	trivial: "#22c55e",
	simple: "#84cc16",
	moderate: "#f59e0b",
	complex: "#ef4444",
	very_complex: "#dc2626",
};

const RISK_COLORS: Record<RiskLevel, string> = {
	none: "#22c55e",
	low: "#84cc16",
	medium: "#f59e0b",
	high: "#ef4444",
	critical: "#dc2626",
};

// =============================================================================
// COMPONENT
// =============================================================================

function DimensionFiltersComponent({
	activeFilters,
	onFiltersChange,
	displayMode,
	onDisplayModeChange,
	isExpanded = false,
	compact = false,
}: DimensionFiltersProps) {
	const [isOpen, setIsOpen] = useState(isExpanded);

	const handleAddFilter = useCallback(
		(dimension: keyof DimensionValues, value: string | number | string[]) => {
			const existingIndex = activeFilters.findIndex(
				(f) => f.dimension === dimension,
			);
			const newFilter: DimensionFilter = {
				dimension,
				operator: Array.isArray(value) ? "in" : "eq",
				value,
			};

			if (existingIndex >= 0) {
				const updated = [...activeFilters];
				updated[existingIndex] = newFilter;
				onFiltersChange(updated);
			} else {
				onFiltersChange([...activeFilters, newFilter]);
			}
		},
		[activeFilters, onFiltersChange],
	);

	const handleRemoveFilter = useCallback(
		(dimension: string) => {
			onFiltersChange(activeFilters.filter((f) => f.dimension !== dimension));
		},
		[activeFilters, onFiltersChange],
	);

	const handleClearAll = useCallback(() => {
		onFiltersChange([]);
	}, [onFiltersChange]);

	const getActiveFilterValue = (dimension: string) => {
		return activeFilters.find((f) => f.dimension === dimension)?.value;
	};

	if (compact) {
		return (
			<CompactDimensionFilters
				activeFilters={activeFilters}
				onFiltersChange={onFiltersChange}
				displayMode={displayMode}
				onDisplayModeChange={onDisplayModeChange}
			/>
		);
	}

	return (
		<TooltipProvider>
			<div className="flex flex-col gap-2">
				{/* Header with display mode toggle */}
				<div className="flex items-center justify-between">
					<div className="flex items-center gap-2">
						<Activity className="h-4 w-4 text-muted-foreground" />
						<span className="text-sm font-medium">Dimensions</span>
						{activeFilters.length > 0 && (
							<Badge variant="secondary" className="text-xs">
								{activeFilters.length} active
							</Badge>
						)}
					</div>
					<div className="flex items-center gap-1">
						{/* Display mode selector */}
						<div className="flex items-center gap-0.5 p-0.5 bg-muted/50 rounded-md">
							{DISPLAY_MODE_OPTIONS.map((option) => {
								const Icon = option.icon;
								const isActive = displayMode === option.id;
								return (
									<Tooltip key={option.id} delayDuration={200}>
										<TooltipTrigger asChild>
											<Button
												variant={isActive ? "default" : "ghost"}
												size="sm"
												className="h-7 w-7 p-0"
												onClick={() => onDisplayModeChange(option.id)}
											>
												<Icon className="h-3.5 w-3.5" />
											</Button>
										</TooltipTrigger>
										<TooltipContent side="bottom">
											{option.label} mode
										</TooltipContent>
									</Tooltip>
								);
							})}
						</div>
						{activeFilters.length > 0 && (
							<Button
								variant="ghost"
								size="sm"
								className="h-7 px-2 text-xs"
								onClick={handleClearAll}
							>
								Clear all
							</Button>
						)}
					</div>
				</div>

				{/* Dimension filters */}
				<div className="grid grid-cols-2 gap-2">
					{DIMENSION_CONFIGS.map((config) => {
						const Icon = config.icon;
						const currentValue = getActiveFilterValue(config.id);
						const isActive = currentValue !== undefined;

						return (
							<Popover key={config.id}>
								<PopoverTrigger asChild>
									<Button
										variant={isActive ? "default" : "outline"}
										size="sm"
										className="justify-start gap-2 h-8"
										style={
											isActive
												? {
														backgroundColor: config.color,
														borderColor: config.color,
													}
												: undefined
										}
									>
										<Icon className="h-3.5 w-3.5" />
										<span className="text-xs">{config.label}</span>
										{isActive && (
											<Badge
												variant="secondary"
												className="ml-auto text-[10px] px-1.5 py-0 bg-white/20"
											>
												{formatFilterValue(currentValue)}
											</Badge>
										)}
									</Button>
								</PopoverTrigger>
								<PopoverContent className="w-64 p-3" align="start">
									<DimensionFilterEditor
										config={config}
										value={currentValue}
										onChange={(value) => handleAddFilter(config.id, value)}
										onClear={() => handleRemoveFilter(config.id)}
									/>
								</PopoverContent>
							</Popover>
						);
					})}
				</div>

				{/* Active filter pills */}
				{activeFilters.length > 0 && (
					<div className="flex flex-wrap gap-1.5 pt-1">
						{activeFilters.map((filter) => {
							const config = DIMENSION_CONFIGS.find(
								(c) => c.id === filter.dimension,
							);
							if (!config) return null;
							const Icon = config.icon;

							return (
								<Badge
									key={filter.dimension}
									variant="secondary"
									className="gap-1.5 pr-1"
									style={{
										backgroundColor: `${config.color}20`,
										color: config.color,
									}}
								>
									<Icon className="h-3 w-3" />
									<span className="text-xs">
										{config.label}: {formatFilterValue(filter.value)}
									</span>
									<Button
										variant="ghost"
										size="sm"
										className="h-4 w-4 p-0 hover:bg-transparent"
										onClick={() =>
											handleRemoveFilter(filter.dimension as string)
										}
									>
										<X className="h-3 w-3" />
									</Button>
								</Badge>
							);
						})}
					</div>
				)}
			</div>
		</TooltipProvider>
	);
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface DimensionFilterEditorProps {
	config: DimensionConfig;
	value: string | number | string[] | undefined;
	onChange: (value: string | number | string[]) => void;
	onClear: () => void;
}

function DimensionFilterEditor({
	config,
	value,
	onChange,
	onClear,
}: DimensionFilterEditorProps) {
	if (config.type === "range") {
		const numValue = typeof value === "number" ? value : 50;
		return (
			<div className="space-y-3">
				<div className="flex items-center justify-between">
					<span className="text-sm font-medium">{config.label}</span>
					{value !== undefined && (
						<Button
							variant="ghost"
							size="sm"
							className="h-6 px-2 text-xs"
							onClick={onClear}
						>
							Clear
						</Button>
					)}
				</div>
				<div className="space-y-2">
					<div className="flex items-center justify-between text-xs text-muted-foreground">
						<span>{config.min}%</span>
						<span className="font-medium text-foreground">{numValue}%</span>
						<span>{config.max}%</span>
					</div>
					<Slider
						value={[numValue]}
						min={config.min}
						max={config.max}
						step={5}
						onValueChange={([v]) => onChange(v)}
						className="w-full"
					/>
				</div>
				<p className="text-xs text-muted-foreground">
					Show items with {config.label.toLowerCase()} &ge; {numValue}%
				</p>
			</div>
		);
	}

	// Enum type
	const selectedValues = Array.isArray(value) ? value : value ? [value] : [];

	return (
		<div className="space-y-3">
			<div className="flex items-center justify-between">
				<span className="text-sm font-medium">{config.label}</span>
				{value !== undefined && (
					<Button
						variant="ghost"
						size="sm"
						className="h-6 px-2 text-xs"
						onClick={onClear}
					>
						Clear
					</Button>
				)}
			</div>
			<div className="flex flex-wrap gap-1.5">
				{config.values?.map((v) => {
					const isSelected = selectedValues.includes(v);
					const color = getDimensionValueColor(config.id, v);

					return (
						<Button
							key={v}
							variant={isSelected ? "default" : "outline"}
							size="sm"
							className="h-7 text-xs capitalize"
							style={
								isSelected
									? { backgroundColor: color, borderColor: color }
									: undefined
							}
							onClick={() => {
								if (isSelected) {
									const newValues = selectedValues.filter((sv) => sv !== v);
									if (newValues.length === 0) {
										onClear();
									} else {
										onChange(newValues.length === 1 ? newValues[0] : newValues);
									}
								} else {
									const newValues = [...selectedValues, v];
									onChange(newValues.length === 1 ? newValues[0] : newValues);
								}
							}}
						>
							{v.replace("_", " ")}
						</Button>
					);
				})}
			</div>
		</div>
	);
}

interface CompactDimensionFiltersProps {
	activeFilters: DimensionFilter[];
	onFiltersChange: (filters: DimensionFilter[]) => void;
	displayMode: DimensionDisplayMode;
	onDisplayModeChange: (mode: DimensionDisplayMode) => void;
}

function CompactDimensionFilters({
	activeFilters,
	onFiltersChange,
	displayMode,
	onDisplayModeChange,
}: CompactDimensionFiltersProps) {
	return (
		<TooltipProvider>
			<Popover>
				<PopoverTrigger asChild>
					<Button
						variant={activeFilters.length > 0 ? "default" : "outline"}
						size="sm"
						className="gap-2 h-8"
					>
						<Activity className="h-3.5 w-3.5" />
						<span className="text-xs">Dimensions</span>
						{activeFilters.length > 0 && (
							<Badge
								variant="secondary"
								className="text-[10px] px-1.5 py-0 bg-white/20"
							>
								{activeFilters.length}
							</Badge>
						)}
					</Button>
				</PopoverTrigger>
				<PopoverContent className="w-80 p-4" align="end">
					<DimensionFiltersComponent
						activeFilters={activeFilters}
						onFiltersChange={onFiltersChange}
						displayMode={displayMode}
						onDisplayModeChange={onDisplayModeChange}
					/>
				</PopoverContent>
			</Popover>
		</TooltipProvider>
	);
}

// =============================================================================
// UTILITIES
// =============================================================================

function formatFilterValue(
	value: string | number | boolean | string[] | number[] | undefined,
): string {
	if (value === undefined) return "";
	if (Array.isArray(value)) {
		return value.length === 1 ? String(value[0]) : `${value.length} selected`;
	}
	if (typeof value === "number") return `${value}%`;
	return String(value).replace("_", " ");
}

function getDimensionValueColor(dimension: string, value: string): string {
	if (dimension === "maturity") {
		return MATURITY_COLORS[value as MaturityLevel] || "#64748b";
	}
	if (dimension === "complexity") {
		return COMPLEXITY_COLORS[value as ComplexityLevel] || "#64748b";
	}
	if (dimension === "risk") {
		return RISK_COLORS[value as RiskLevel] || "#64748b";
	}
	return "#64748b";
}

// =============================================================================
// EXPORTS
// =============================================================================

export const DimensionFilters = memo(DimensionFiltersComponent);

// Export utility functions for use in graph rendering
export { DIMENSION_CONFIGS, MATURITY_COLORS, COMPLEXITY_COLORS, RISK_COLORS };

/**
 * Apply dimension filters to a list of items
 * Returns items that match all active filters
 */
export function applyDimensionFilters<
	T extends { dimensions?: Record<string, unknown> },
>(items: T[], filters: DimensionFilter[]): T[] {
	if (filters.length === 0) return items;

	return items.filter((item) => {
		return filters.every((filter) => {
			const itemValue = item.dimensions?.[filter.dimension];
			if (itemValue === undefined) return false;

			switch (filter.operator) {
				case "eq":
					return itemValue === filter.value;
				case "neq":
					return itemValue !== filter.value;
				case "gt":
					return (
						typeof itemValue === "number" &&
						itemValue > (filter.value as number)
					);
				case "gte":
					return (
						typeof itemValue === "number" &&
						itemValue >= (filter.value as number)
					);
				case "lt":
					return (
						typeof itemValue === "number" &&
						itemValue < (filter.value as number)
					);
				case "lte":
					return (
						typeof itemValue === "number" &&
						itemValue <= (filter.value as number)
					);
				case "in":
					return (
						Array.isArray(filter.value) &&
						filter.value.includes(itemValue as string)
					);
				case "not_in":
					return (
						Array.isArray(filter.value) &&
						!filter.value.includes(itemValue as string)
					);
				default:
					return true;
			}
		});
	});
}

/**
 * Get color for an item based on its dimension value and the current color dimension
 */
export function getDimensionColor(
	dimensions: Record<string, unknown> | undefined,
	colorDimension: keyof DimensionValues,
): string | undefined {
	if (!dimensions) return undefined;
	const value = dimensions[colorDimension];
	if (value === undefined) return undefined;

	return getDimensionValueColor(colorDimension, String(value));
}

/**
 * Get relative size (0-1) for an item based on its dimension value
 */
export function getDimensionSize(
	dimensions: Record<string, unknown> | undefined,
	sizeDimension: keyof DimensionValues,
): number {
	if (!dimensions) return 0.5;
	const value = dimensions[sizeDimension];
	if (value === undefined) return 0.5;

	if (typeof value === "number") {
		// Normalize 0-100 to 0.3-1.0
		return 0.3 + (value / 100) * 0.7;
	}

	// For enum types, map to size
	const config = DIMENSION_CONFIGS.find((c) => c.id === sizeDimension);
	if (config?.values) {
		const index = config.values.indexOf(value as string);
		if (index >= 0) {
			return 0.3 + (index / (config.values.length - 1)) * 0.7;
		}
	}

	return 0.5;
}
