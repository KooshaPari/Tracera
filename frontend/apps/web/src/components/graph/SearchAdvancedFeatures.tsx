import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Bookmark, Download, Trash2 } from "lucide-react";
import { memo, useCallback, useState } from "react";
import type {
	GroupedSearchResults,
	SavedSearch,
} from "./hooks/useCrossPerspectiveSearch";

/**
 * Props for SavedSearchesPanel
 */
interface SavedSearchesPanelProps {
	savedSearches: SavedSearch[];
	onLoadSearch: (search: SavedSearch) => void;
	onDeleteSearch: (id: string) => void;
	onSaveSearch?: (query: string) => void;
	className?: string;
}

/**
 * Panel for displaying and managing saved searches
 */
export const SavedSearchesPanel = memo(function SavedSearchesPanelComponent({
	savedSearches,
	onLoadSearch,
	onDeleteSearch,
	onSaveSearch,
	className,
}: SavedSearchesPanelProps) {
	if (savedSearches.length === 0) {
		return (
			<div className={cn("text-center text-muted-foreground py-4", className)}>
				<Bookmark className="w-4 h-4 mx-auto mb-2 opacity-50" />
				<p className="text-xs">No saved searches yet</p>
			</div>
		);
	}

	return (
		<div className={cn("space-y-2", className)}>
			<p className="text-xs font-semibold text-muted-foreground uppercase">
				Saved Searches
			</p>
			{savedSearches.slice(0, 10).map((search) => (
				<div
					key={search.id}
					className="flex items-center gap-2 p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors group"
				>
					<button
						onClick={() => onLoadSearch(search)}
						className="flex-1 text-left min-w-0"
					>
						<p className="text-sm font-medium truncate">{search.query}</p>
						<p className="text-xs text-muted-foreground">
							{new Date(search.createdAt).toLocaleDateString()}
						</p>
					</button>
					<Button
						variant="ghost"
						size="sm"
						className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100"
						onClick={() => onDeleteSearch(search.id)}
					>
						<Trash2 className="w-3 h-3" />
					</Button>
				</div>
			))}
		</div>
	);
});

/**
 * Props for SearchSuggestionsPanel
 */
interface SearchSuggestionsPanelProps {
	suggestions: string[];
	onSelectSuggestion: (suggestion: string) => void;
	className?: string;
}

/**
 * Panel for displaying search suggestions
 */
export const SearchSuggestionsPanel = memo(
	function SearchSuggestionsPanelComponent({
		suggestions,
		onSelectSuggestion,
		className,
	}: SearchSuggestionsPanelProps) {
		if (suggestions.length === 0) {
			return null;
		}

		return (
			<div className={cn("space-y-2", className)}>
				<p className="text-xs font-semibold text-muted-foreground uppercase">
					Suggestions
				</p>
				<div className="flex flex-wrap gap-2">
					{suggestions.map((suggestion) => (
						<Button
							key={suggestion}
							variant="outline"
							size="sm"
							className="text-xs h-7"
							onClick={() => onSelectSuggestion(suggestion)}
						>
							{suggestion}
						</Button>
					))}
				</div>
			</div>
		);
	},
);

/**
 * Props for SearchResultsExport
 */
interface SearchResultsExportProps {
	results: GroupedSearchResults[];
	query: string;
	onExportJSON?: (filename: string) => void;
	onExportCSV?: (filename: string) => void;
	className?: string;
}

/**
 * Component for exporting search results
 */
export const SearchResultsExport = memo(function SearchResultsExportComponent({
	results,
	query,
	onExportJSON,
	onExportCSV,
	className,
}: SearchResultsExportProps) {
	const totalResults = results.reduce((sum, group) => sum + group.count, 0);

	if (totalResults === 0) {
		return null;
	}

	const filename = `search-${query.replace(/\s+/g, "-")}-${Date.now()}`;

	return (
		<div className={cn("flex items-center gap-2", className)}>
			<span className="text-xs text-muted-foreground">
				Export {totalResults} result{totalResults !== 1 ? "s" : ""}:
			</span>
			<Button
				variant="outline"
				size="sm"
				className="h-7 text-xs gap-1"
				onClick={() => onExportJSON?.(`${filename}.json`)}
			>
				<Download className="w-3 h-3" />
				JSON
			</Button>
			<Button
				variant="outline"
				size="sm"
				className="h-7 text-xs gap-1"
				onClick={() => onExportCSV?.(`${filename}.csv`)}
			>
				<Download className="w-3 h-3" />
				CSV
			</Button>
		</div>
	);
});

/**
 * Props for SearchMetrics
 */
interface SearchMetricsProps {
	results: GroupedSearchResults[];
	query: string;
	executionTime?: number;
	cacheHit?: boolean;
	className?: string;
}

/**
 * Component for displaying search metrics
 */
export const SearchMetrics = memo(function SearchMetricsComponent({
	results,
	query,
	executionTime,
	cacheHit,
	className,
}: SearchMetricsProps) {
	const totalResults = results.reduce((sum, group) => sum + group.count, 0);
	const perspectiveCount = results.length;

	return (
		<div className={cn("flex flex-wrap gap-3", className)}>
			<div className="text-xs">
				<span className="text-muted-foreground">Total Results: </span>
				<span className="font-semibold">{totalResults}</span>
			</div>
			<div className="text-xs">
				<span className="text-muted-foreground">Perspectives: </span>
				<span className="font-semibold">{perspectiveCount}</span>
			</div>
			{executionTime !== undefined && (
				<div className="text-xs">
					<span className="text-muted-foreground">Time: </span>
					<span className="font-semibold">{executionTime.toFixed(0)}ms</span>
				</div>
			)}
			{cacheHit && (
				<Badge variant="secondary" className="h-5 text-[10px]">
					Cache Hit
				</Badge>
			)}
		</div>
	);
});

/**
 * Props for QuickFilterButtons
 */
interface QuickFilterButtonsProps {
	items?: Array<{ label: string; value: string; count: number }>;
	onFilterSelect?: (value: string) => void;
	className?: string;
}

/**
 * Quick filter buttons for common search refinements
 */
export const QuickFilterButtons = memo(function QuickFilterButtonsComponent({
	items = [],
	onFilterSelect,
	className,
}: QuickFilterButtonsProps) {
	if (items.length === 0) {
		return null;
	}

	return (
		<div className={cn("flex flex-wrap gap-2", className)}>
			{items.map((item) => (
				<Button
					key={item.value}
					variant="outline"
					size="sm"
					className="h-7 text-xs"
					onClick={() => onFilterSelect?.(item.value)}
				>
					{item.label}
					<Badge variant="secondary" className="ml-1 h-4 text-[8px]">
						{item.count}
					</Badge>
				</Button>
			))}
		</div>
	);
});

/**
 * Props for SaveSearchButton
 */
interface SaveSearchButtonProps {
	query: string;
	onSave: (query: string) => void;
	className?: string;
	isSaved?: boolean;
}

/**
 * Button to save the current search
 */
export const SaveSearchButton = memo(function SaveSearchButtonComponent({
	query,
	onSave,
	className,
	isSaved = false,
}: SaveSearchButtonProps) {
	const [showFeedback, setShowFeedback] = useState(false);

	const handleClick = useCallback(() => {
		onSave(query);
		setShowFeedback(true);
		setTimeout(() => setShowFeedback(false), 2000);
	}, [query, onSave]);

	return (
		<Button
			variant={isSaved ? "default" : "outline"}
			size="sm"
			className="h-8 text-xs gap-1"
			onClick={handleClick}
		>
			<Bookmark className={cn("w-3 h-3", isSaved && "fill-current")} />
			{showFeedback ? "Saved!" : "Save Search"}
		</Button>
	);
});

/**
 * Props for DimensionFilterGroup
 */
interface DimensionFilterGroupProps {
	dimensions: Array<{ key: string; values: string[] }>;
	selectedDimension?: string;
	selectedValue?: string;
	onDimensionSelect: (key: string) => void;
	onValueSelect: (key: string, value: string) => void;
	className?: string;
}

/**
 * Component for dimension-based filtering
 */
export const DimensionFilterGroup = memo(
	function DimensionFilterGroupComponent({
		dimensions,
		selectedDimension,
		selectedValue,
		onDimensionSelect,
		onValueSelect,
		className,
	}: DimensionFilterGroupProps) {
		if (dimensions.length === 0) {
			return null;
		}

		return (
			<div className={cn("space-y-2", className)}>
				<p className="text-xs font-semibold text-muted-foreground uppercase">
					Dimensions
				</p>
				<div className="space-y-2">
					{dimensions.map((dim) => (
						<div key={dim.key} className="space-y-1">
							<button
								onClick={() => onDimensionSelect(dim.key)}
								className={cn(
									"text-xs font-medium w-full text-left px-2 py-1 rounded transition-colors",
									selectedDimension === dim.key
										? "bg-primary text-primary-foreground"
										: "text-muted-foreground hover:text-foreground",
								)}
							>
								{dim.key}
							</button>
							{selectedDimension === dim.key && (
								<div className="flex flex-wrap gap-1 px-2">
									{dim.values.map((value) => (
										<Button
											key={value}
											variant="outline"
											size="sm"
											className={cn(
												"h-6 text-[10px]",
												selectedValue === value &&
													"bg-primary text-primary-foreground border-primary",
											)}
											onClick={() => onValueSelect(dim.key, value)}
										>
											{value}
										</Button>
									))}
								</div>
							)}
						</div>
					))}
				</div>
			</div>
		);
	},
);
