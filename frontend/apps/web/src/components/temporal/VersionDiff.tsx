/**
 * VersionDiff - Side-by-side diff visualization of two versions
 *
 * Features:
 * - Visual comparison of added/removed/modified items
 * - Field-level change highlighting
 * - Statistics summary
 * - Filter by change type
 * - Expandable diff details
 */

import type {
	DiffItem,
	Version,
	VersionDiff as VersionDiffType,
} from "@tracertm/types/temporal";
import {
	ArrowRight,
	CheckCircle,
	ChevronDown,
	ChevronRight,
	Code,
	Database,
	FileText,
	Filter,
	Layout,
	Minus,
	Plus,
	RefreshCw,
	Tag,
} from "lucide-react";
import type React from "react";
import { useMemo, useState } from "react";

// =============================================================================
// TYPES
// =============================================================================

export interface VersionDiffProps {
	diff: VersionDiffType;
	versionA?: Version;
	versionB?: Version;

	// Actions
	onItemClick?: (itemId: string, side: "left" | "right") => void;

	// Layout
	className?: string;
	compact?: boolean;
}

type ChangeFilter = "all" | "added" | "removed" | "modified";
type SignificanceFilter = "all" | "breaking" | "major" | "moderate" | "minor";

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function VersionDiff({
	diff,
	versionA,
	versionB,
	onItemClick,
	className = "",
	compact = false,
}: VersionDiffProps) {
	const [changeFilter, setChangeFilter] = useState<ChangeFilter>("all");
	const [significanceFilter, setSignificanceFilter] =
		useState<SignificanceFilter>("all");
	const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
	const [viewMode, setViewMode] = useState<"unified" | "split">("unified");

	// Filter items based on current filters
	const filteredItems = useMemo(() => {
		let items: DiffItem[] = [];

		if (changeFilter === "all" || changeFilter === "added") {
			items = [...items, ...diff.added];
		}
		if (changeFilter === "all" || changeFilter === "removed") {
			items = [...items, ...diff.removed];
		}
		if (changeFilter === "all" || changeFilter === "modified") {
			items = [...items, ...diff.modified];
		}

		// Filter by significance
		if (significanceFilter !== "all") {
			items = items.filter((item) => item.significance === significanceFilter);
		}

		return items;
	}, [diff, changeFilter, significanceFilter]);

	// Toggle item expansion
	const toggleExpanded = (itemId: string) => {
		setExpandedItems((prev) => {
			const next = new Set(prev);
			if (next.has(itemId)) {
				next.delete(itemId);
			} else {
				next.add(itemId);
			}
			return next;
		});
	};

	return (
		<div className={`version-diff ${className}`}>
			{/* Header with version info */}
			<div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
				<div className="flex items-center gap-4">
					{/* Version A */}
					<div className="flex items-center gap-2">
						<div className="w-3 h-3 rounded-full bg-red-400" />
						<div>
							<span className="text-sm font-medium">
								v{diff.versionANumber}
							</span>
							{versionA?.tag && (
								<span className="ml-1.5 text-xs text-gray-500">
									<Tag className="w-3 h-3 inline" /> {versionA.tag}
								</span>
							)}
						</div>
					</div>

					<ArrowRight className="w-4 h-4 text-gray-400" />

					{/* Version B */}
					<div className="flex items-center gap-2">
						<div className="w-3 h-3 rounded-full bg-green-400" />
						<div>
							<span className="text-sm font-medium">
								v{diff.versionBNumber}
							</span>
							{versionB?.tag && (
								<span className="ml-1.5 text-xs text-gray-500">
									<Tag className="w-3 h-3 inline" /> {versionB.tag}
								</span>
							)}
						</div>
					</div>
				</div>

				<div className="flex items-center gap-2">
					{/* View mode toggle */}
					<div className="flex border border-gray-300 dark:border-gray-600 rounded-md overflow-hidden">
						<button
							onClick={() => setViewMode("unified")}
							className={`px-3 py-1 text-xs ${
								viewMode === "unified"
									? "bg-gray-200 dark:bg-gray-700"
									: "bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
							}`}
						>
							Unified
						</button>
						<button
							onClick={() => setViewMode("split")}
							className={`px-3 py-1 text-xs ${
								viewMode === "split"
									? "bg-gray-200 dark:bg-gray-700"
									: "bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
							}`}
						>
							Split
						</button>
					</div>
				</div>
			</div>

			{/* Stats Summary */}
			<DiffStatsSummary stats={diff.stats} />

			{/* Filters */}
			<div className="flex items-center gap-4 px-4 py-2 border-b border-gray-200 dark:border-gray-700">
				<div className="flex items-center gap-1">
					<Filter className="w-4 h-4 text-gray-400" />
					<span className="text-xs text-gray-500">Filter:</span>
				</div>

				{/* Change type filter */}
				<div className="flex gap-1">
					{(["all", "added", "removed", "modified"] as const).map((filter) => (
						<button
							key={filter}
							onClick={() => setChangeFilter(filter)}
							className={`
                px-2 py-1 text-xs rounded-md transition-colors
                ${
									changeFilter === filter
										? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
										: "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
								}
              `}
						>
							{filter === "all" && "All"}
							{filter === "added" && (
								<span className="flex items-center gap-1">
									<Plus className="w-3 h-3" />
									Added ({diff.stats.addedCount})
								</span>
							)}
							{filter === "removed" && (
								<span className="flex items-center gap-1">
									<Minus className="w-3 h-3" />
									Removed ({diff.stats.removedCount})
								</span>
							)}
							{filter === "modified" && (
								<span className="flex items-center gap-1">
									<RefreshCw className="w-3 h-3" />
									Modified ({diff.stats.modifiedCount})
								</span>
							)}
						</button>
					))}
				</div>

				<div className="h-4 w-px bg-gray-300 dark:bg-gray-600" />

				{/* Significance filter */}
				<select
					value={significanceFilter}
					onChange={(e) =>
						setSignificanceFilter(e.target.value as SignificanceFilter)
					}
					className="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
				>
					<option value="all">All significance</option>
					<option value="breaking">Breaking only</option>
					<option value="major">Major+</option>
					<option value="moderate">Moderate+</option>
					<option value="minor">Minor+</option>
				</select>
			</div>

			{/* Diff Items */}
			<div className="overflow-auto">
				{filteredItems.length > 0 ? (
					<div className="divide-y divide-gray-200 dark:divide-gray-700">
						{filteredItems.map((item) => (
							<DiffItemRow
								key={item.itemId}
								item={item}
								isExpanded={expandedItems.has(item.itemId)}
								onToggleExpand={() => toggleExpanded(item.itemId)}
								onItemClick={onItemClick}
								compact={compact}
							/>
						))}
					</div>
				) : (
					<div className="flex flex-col items-center justify-center p-8 text-gray-500">
						<CheckCircle className="w-10 h-10 mb-2 opacity-50" />
						<p className="text-sm">No changes match the current filters</p>
					</div>
				)}
			</div>
		</div>
	);
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface DiffStatsSummaryProps {
	stats: VersionDiffType["stats"];
}

function DiffStatsSummary({ stats }: DiffStatsSummaryProps) {
	return (
		<div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
			<div className="flex items-center gap-6">
				<div className="flex items-center gap-2">
					<Plus className="w-4 h-4 text-green-500" />
					<span className="text-sm">
						<span className="font-semibold text-green-600 dark:text-green-400">
							{stats.addedCount}
						</span>{" "}
						added
					</span>
				</div>
				<div className="flex items-center gap-2">
					<Minus className="w-4 h-4 text-red-500" />
					<span className="text-sm">
						<span className="font-semibold text-red-600 dark:text-red-400">
							{stats.removedCount}
						</span>{" "}
						removed
					</span>
				</div>
				<div className="flex items-center gap-2">
					<RefreshCw className="w-4 h-4 text-yellow-500" />
					<span className="text-sm">
						<span className="font-semibold text-yellow-600 dark:text-yellow-400">
							{stats.modifiedCount}
						</span>{" "}
						modified
					</span>
				</div>
			</div>
			<div className="text-sm text-gray-500">
				{stats.unchangedCount} unchanged
			</div>
		</div>
	);
}

interface DiffItemRowProps {
	item: DiffItem;
	isExpanded: boolean;
	onToggleExpand: () => void;
	onItemClick?: (itemId: string, side: "left" | "right") => void;
	compact: boolean;
}

function DiffItemRow({
	item,
	isExpanded,
	onToggleExpand,
	onItemClick,
	compact,
}: DiffItemRowProps) {
	const hasFieldChanges = item.fieldChanges && item.fieldChanges.length > 0;

	const changeTypeConfig = {
		added: {
			icon: Plus,
			bgColor: "bg-green-50 dark:bg-green-900/10",
			borderColor: "border-l-green-500",
			iconColor: "text-green-500",
		},
		removed: {
			icon: Minus,
			bgColor: "bg-red-50 dark:bg-red-900/10",
			borderColor: "border-l-red-500",
			iconColor: "text-red-500",
		},
		modified: {
			icon: RefreshCw,
			bgColor: "bg-yellow-50 dark:bg-yellow-900/10",
			borderColor: "border-l-yellow-500",
			iconColor: "text-yellow-500",
		},
	};

	const config = changeTypeConfig[item.changeType];
	const Icon = config.icon;

	const typeIcon = getTypeIcon(item.type);

	return (
		<div className={`${config.bgColor} border-l-4 ${config.borderColor}`}>
			{/* Main row */}
			<div
				className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-black/5 dark:hover:bg-white/5"
				onClick={() => hasFieldChanges && onToggleExpand()}
			>
				{/* Expand toggle */}
				{hasFieldChanges ? (
					<button className="p-0.5">
						{isExpanded ? (
							<ChevronDown className="w-4 h-4 text-gray-400" />
						) : (
							<ChevronRight className="w-4 h-4 text-gray-400" />
						)}
					</button>
				) : (
					<div className="w-5" />
				)}

				{/* Change type icon */}
				<Icon className={`w-4 h-4 ${config.iconColor}`} />

				{/* Item type icon */}
				<span className="text-gray-400">{typeIcon}</span>

				{/* Item info */}
				<div className="flex-1 min-w-0">
					<div className="flex items-center gap-2">
						<span className="font-medium text-sm truncate">{item.title}</span>
						<span className="text-xs text-gray-500 px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 rounded">
							{item.type}
						</span>
					</div>
					{!compact && item.changeType === "modified" && item.fieldChanges && (
						<p className="text-xs text-gray-500 mt-0.5">
							{item.fieldChanges.length} field
							{item.fieldChanges.length !== 1 ? "s" : ""} changed
						</p>
					)}
				</div>

				{/* Significance badge */}
				<SignificanceBadge significance={item.significance} />

				{/* View button */}
				{onItemClick && (
					<button
						onClick={(e) => {
							e.stopPropagation();
							onItemClick(
								item.itemId,
								item.changeType === "removed" ? "left" : "right",
							);
						}}
						className="px-2 py-1 text-xs text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded"
					>
						View
					</button>
				)}
			</div>

			{/* Expanded field changes */}
			{isExpanded && hasFieldChanges && (
				<div className="px-4 pb-3 pl-12">
					<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
						<table className="w-full text-sm">
							<thead className="bg-gray-50 dark:bg-gray-700/50">
								<tr>
									<th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
										Field
									</th>
									<th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
										Old Value
									</th>
									<th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
										New Value
									</th>
								</tr>
							</thead>
							<tbody className="divide-y divide-gray-200 dark:divide-gray-700">
								{item.fieldChanges!.map((change, index) => (
									<tr key={index}>
										<td className="px-3 py-2 font-medium text-gray-900 dark:text-gray-100">
											{change.field}
										</td>
										<td className="px-3 py-2 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/10">
											<ValueDisplay value={change.oldValue} />
										</td>
										<td className="px-3 py-2 text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/10">
											<ValueDisplay value={change.newValue} />
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</div>
			)}
		</div>
	);
}

function SignificanceBadge({
	significance,
}: {
	significance: DiffItem["significance"];
}) {
	const config = {
		breaking: { color: "red", label: "Breaking" },
		major: { color: "orange", label: "Major" },
		moderate: { color: "yellow", label: "Moderate" },
		minor: { color: "gray", label: "Minor" },
	};

	const { color, label } = config[significance];

	const colorClasses: Record<string, string> = {
		red: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
		orange:
			"bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
		yellow:
			"bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
		gray: "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
	};

	return (
		<span className={`px-1.5 py-0.5 text-xs rounded ${colorClasses[color]}`}>
			{label}
		</span>
	);
}

function ValueDisplay({ value }: { value: unknown }) {
	if (value === null || value === undefined) {
		return <span className="italic opacity-50">null</span>;
	}
	if (typeof value === "boolean") {
		return <span>{value ? "true" : "false"}</span>;
	}
	if (typeof value === "object") {
		return (
			<span className="font-mono text-xs">
				{JSON.stringify(value, null, 0).slice(0, 50)}
				{JSON.stringify(value).length > 50 ? "..." : ""}
			</span>
		);
	}
	return <span>{String(value)}</span>;
}

function getTypeIcon(type: string): React.ReactNode {
	const lowerType = type.toLowerCase();

	if (lowerType.includes("code") || lowerType.includes("function")) {
		return <Code className="w-4 h-4" />;
	}
	if (lowerType.includes("database") || lowerType.includes("schema")) {
		return <Database className="w-4 h-4" />;
	}
	if (
		lowerType.includes("ui") ||
		lowerType.includes("component") ||
		lowerType.includes("page")
	) {
		return <Layout className="w-4 h-4" />;
	}
	return <FileText className="w-4 h-4" />;
}

export default VersionDiff;
