// ComponentLibraryExplorer.tsx - Browse and search component libraries
// Shows components, props, variants, and usage locations

import type {
	ComponentCategory,
	ComponentLibrary,
	DesignToken,
	LibraryComponent,
} from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@tracertm/ui/components/Card";
import {
	Collapsible,
	CollapsibleContent,
	CollapsibleTrigger,
} from "@tracertm/ui/components/Collapsible";
import { Input } from "@tracertm/ui/components/Input";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import {
	AlertCircle,
	Archive,
	ArrowUpRight,
	Beaker,
	BookOpen,
	Box,
	Check,
	ChevronDown,
	ChevronRight,
	Code,
	Component,
	ExternalLink,
	Eye,
	Figma,
	Grid3x3,
	Layers,
	LayoutGrid,
	Library,
	Package,
	Palette,
	RefreshCw,
	Search,
	Settings,
	Square,
	Zap,
} from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";

// =============================================================================
// TYPES
// =============================================================================

export interface ComponentLibraryExplorerProps {
	/** Available component libraries */
	libraries: ComponentLibrary[];
	/** All components across libraries */
	components: LibraryComponent[];
	/** Design tokens */
	tokens?: DesignToken[];
	/** Currently selected library ID */
	selectedLibraryId?: string;
	/** Callback when library selection changes */
	onSelectLibrary?: (libraryId: string) => void;
	/** Callback when a component is selected */
	onSelectComponent: (componentId: string) => void;
	/** Currently selected component ID */
	selectedComponentId?: string | null;
	/** Callback to view component in Storybook */
	onViewInStorybook?: (componentId: string) => void;
	/** Callback to view component in Figma */
	onViewInFigma?: (componentId: string) => void;
	/** Callback to view component in code */
	onViewInCode?: (componentId: string) => void;
	/** Callback to sync a library */
	onSyncLibrary?: (libraryId: string) => void;
	/** Loading state */
	isLoading?: boolean;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const CATEGORY_ICONS: Record<
	ComponentCategory,
	React.ComponentType<{ className?: string }>
> = {
	atom: Square,
	"data-display": Eye,
	"data-entry": Box,
	feedback: AlertCircle,
	layout: LayoutGrid,
	molecule: Grid3x3,
	navigation: ArrowUpRight,
	organism: Layers,
	other: Component,
	overlay: Layers,
	page: Box,
	template: LayoutGrid,
	utility: Settings,
};

const CATEGORY_LABELS: Record<ComponentCategory, string> = {
	atom: "Atoms",
	"data-display": "Data Display",
	"data-entry": "Data Entry",
	feedback: "Feedback",
	layout: "Layout",
	molecule: "Molecules",
	navigation: "Navigation",
	organism: "Organisms",
	other: "Other",
	overlay: "Overlays",
	page: "Pages",
	template: "Templates",
	utility: "Utilities",
};

const STATUS_CONFIG = {
	beta: { color: "#f59e0b", icon: Beaker, label: "Beta" },
	deprecated: { color: "#ef4444", icon: Archive, label: "Deprecated" },
	experimental: { color: "#8b5cf6", icon: Zap, label: "Experimental" },
	stable: { color: "#22c55e", icon: Check, label: "Stable" },
};

// =============================================================================
// COMPONENT
// =============================================================================

function ComponentLibraryExplorerComponent({
	libraries,
	components,
	tokens = [],
	selectedLibraryId,
	onSelectLibrary,
	onSelectComponent,
	selectedComponentId,
	onViewInStorybook,
	onViewInFigma,
	onViewInCode,
	onSyncLibrary,
	isLoading = false,
}: ComponentLibraryExplorerProps) {
	const [searchQuery, setSearchQuery] = useState("");
	const [activeTab, setActiveTab] = useState<"components" | "tokens">(
		"components",
	);
	const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
		new Set(),
	);
	const [filterStatus, setFilterStatus] = useState<
		LibraryComponent["status"] | "all"
	>("all");

	// Current library
	const currentLibrary = useMemo(() => {
		if (!selectedLibraryId && libraries.length > 0) {
			return libraries[0];
		}
		return libraries.find((l) => l.id === selectedLibraryId);
	}, [libraries, selectedLibraryId]);

	// Filter components by library
	const libraryComponents = useMemo(() => {
		if (!currentLibrary) {
			return [];
		}
		return components.filter((c) => c.libraryId === currentLibrary.id);
	}, [components, currentLibrary]);

	// Filter and group components
	const { filteredComponents, groupedByCategory, stats } = useMemo(() => {
		let filtered = libraryComponents;

		// Filter by search query
		if (searchQuery) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(
				(c) =>
					c.name.toLowerCase().includes(query) ||
					c.displayName.toLowerCase().includes(query) ||
					c.description?.toLowerCase().includes(query) ||
					c.tags?.some((t) => t.toLowerCase().includes(query)),
			);
		}

		// Filter by status
		if (filterStatus !== "all") {
			filtered = filtered.filter((c) => c.status === filterStatus);
		}

		// Group by category
		const grouped = new Map<ComponentCategory, LibraryComponent[]>();
		for (const component of filtered) {
			const { category } = component;
			if (!grouped.has(category)) {
				grouped.set(category, []);
			}
			grouped.get(category)!.push(component);
		}

		// Sort within each category
		for (const [, list] of grouped) {
			list.sort((a, b) => a.displayName.localeCompare(b.displayName));
		}

		// Stats
		const stats = {
			beta: libraryComponents.filter((c) => c.status === "beta").length,
			deprecated: libraryComponents.filter((c) => c.status === "deprecated")
				.length,
			stable: libraryComponents.filter((c) => c.status === "stable").length,
			total: libraryComponents.length,
		};

		return { filteredComponents: filtered, groupedByCategory: grouped, stats };
	}, [libraryComponents, searchQuery, filterStatus]);

	// Handle category toggle
	const toggleCategory = useCallback((category: string) => {
		setExpandedCategories((prev) => {
			const next = new Set(prev);
			if (next.has(category)) {
				next.delete(category);
			} else {
				next.add(category);
			}
			return next;
		});
	}, []);

	const expandAllCategories = useCallback(() => {
		const allCategories = new Set([...groupedByCategory.keys()] as string[]);
		setExpandedCategories(allCategories);
	}, [groupedByCategory]);

	const collapseAllCategories = useCallback(() => {
		setExpandedCategories(new Set());
	}, []);

	if (libraries.length === 0) {
		return (
			<Card className="h-full">
				<CardContent className="h-full flex items-center justify-center">
					<div className="text-center py-12 text-muted-foreground">
						<Library className="h-12 w-12 mx-auto mb-3 opacity-50" />
						<p className="text-sm font-medium">No component libraries</p>
						<p className="text-xs mt-1 max-w-xs mx-auto">
							Connect a Storybook or Figma to import your component library
						</p>
					</div>
				</CardContent>
			</Card>
		);
	}

	return (
		<TooltipProvider>
			<Card className="h-full flex flex-col overflow-hidden">
				{/* Header */}
				<CardHeader className="py-3 px-4 border-b">
					<div className="flex items-center justify-between">
						<div className="flex items-center gap-2">
							<Library className="h-5 w-5 text-green-500" />
							<CardTitle className="text-sm font-semibold">
								Component Library
							</CardTitle>
						</div>

						{/* Library selector (if multiple) */}
						{libraries.length > 1 && (
							<select
								className="text-xs border rounded px-2 py-1 bg-background"
								value={currentLibrary?.id || ""}
								onChange={(e) => onSelectLibrary?.(e.target.value)}
							>
								{libraries.map((lib) => (
									<option key={lib.id} value={lib.id}>
										{lib.name}
									</option>
								))}
							</select>
						)}
					</div>

					{/* Library info */}
					{currentLibrary && (
						<div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
							<span className="flex items-center gap-1">
								<Package className="h-3 w-3" />v{currentLibrary.version}
							</span>
							<span className="flex items-center gap-1">
								<Component className="h-3 w-3" />
								{stats.total} components
							</span>
							{currentLibrary.storybookUrl && (
								<a
									href={currentLibrary.storybookUrl}
									target="_blank"
									rel="noopener noreferrer"
									className="flex items-center gap-1 hover:text-foreground"
								>
									<BookOpen className="h-3 w-3" />
									Storybook
									<ExternalLink className="h-2.5 w-2.5" />
								</a>
							)}
							{onSyncLibrary && (
								<Button
									variant="ghost"
									size="sm"
									className="h-5 px-1.5 text-xs gap-1"
									onClick={() => onSyncLibrary(currentLibrary.id)}
									disabled={isLoading}
								>
									<RefreshCw
										className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`}
									/>
									Sync
								</Button>
							)}
						</div>
					)}
				</CardHeader>

				{/* Stats Row */}
				<div className="px-4 py-2 border-b bg-muted/30 flex items-center gap-3">
					<Button
						variant={filterStatus === "all" ? "default" : "ghost"}
						size="sm"
						className="h-6 px-2 text-xs"
						onClick={() => setFilterStatus("all")}
					>
						All ({stats.total})
					</Button>
					<Button
						variant={filterStatus === "stable" ? "default" : "ghost"}
						size="sm"
						className="h-6 px-2 text-xs gap-1"
						onClick={() => setFilterStatus("stable")}
					>
						<Check className="h-3 w-3 text-green-500" />
						{stats.stable}
					</Button>
					<Button
						variant={filterStatus === "beta" ? "default" : "ghost"}
						size="sm"
						className="h-6 px-2 text-xs gap-1"
						onClick={() => setFilterStatus("beta")}
					>
						<Beaker className="h-3 w-3 text-amber-500" />
						{stats.beta}
					</Button>
					{stats.deprecated > 0 && (
						<Button
							variant={filterStatus === "deprecated" ? "default" : "ghost"}
							size="sm"
							className="h-6 px-2 text-xs gap-1"
							onClick={() => setFilterStatus("deprecated")}
						>
							<Archive className="h-3 w-3 text-red-500" />
							{stats.deprecated}
						</Button>
					)}
				</div>

				{/* Search */}
				<div className="px-4 py-2 border-b">
					<div className="relative">
						<Search className="absolute left-2.5 top-2 h-4 w-4 text-muted-foreground" />
						<Input
							placeholder="Search components..."
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							className="pl-8 h-8 text-sm"
						/>
					</div>
				</div>

				{/* Tabs */}
				<Tabs
					value={activeTab}
					onValueChange={(v) => setActiveTab(v as typeof activeTab)}
					className="flex-1 flex flex-col overflow-hidden"
				>
					<TabsList className="w-full justify-start px-4 h-9 bg-transparent border-b rounded-none">
						<TabsTrigger value="components" className="text-xs">
							<Component className="h-3.5 w-3.5 mr-1" />
							Components
						</TabsTrigger>
						<TabsTrigger value="tokens" className="text-xs">
							<Palette className="h-3.5 w-3.5 mr-1" />
							Tokens
						</TabsTrigger>
					</TabsList>

					<TabsContent
						value="components"
						className="flex-1 overflow-hidden m-0"
					>
						<ScrollArea className="h-full">
							<div className="p-2">
								{/* Expand/Collapse controls */}
								<div className="flex gap-2 mb-2 px-2">
									<Button
										variant="ghost"
										size="sm"
										className="h-6 px-2 text-xs"
										onClick={expandAllCategories}
									>
										Expand All
									</Button>
									<Button
										variant="ghost"
										size="sm"
										className="h-6 px-2 text-xs"
										onClick={collapseAllCategories}
									>
										Collapse All
									</Button>
								</div>

								{/* Categories */}
								{filteredComponents.length > 0 ? (
									[...groupedByCategory.entries()].map(
										([category, categoryComponents]) => (
											<CategorySection
												key={category}
												category={category}
												components={categoryComponents}
												isExpanded={expandedCategories.has(category)}
												onToggle={() => toggleCategory(category)}
												selectedComponentId={selectedComponentId}
												onSelectComponent={onSelectComponent}
												onViewInStorybook={onViewInStorybook}
												onViewInFigma={onViewInFigma}
												onViewInCode={onViewInCode}
											/>
										),
									)
								) : (
									<div className="text-center py-8 text-muted-foreground">
										<Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
										<p className="text-sm">No components found</p>
										<p className="text-xs mt-1">Try a different search term</p>
									</div>
								)}
							</div>
						</ScrollArea>
					</TabsContent>

					<TabsContent value="tokens" className="flex-1 overflow-hidden m-0">
						<ScrollArea className="h-full">
							<TokensGrid tokens={tokens} libraryId={currentLibrary?.id} />
						</ScrollArea>
					</TabsContent>
				</Tabs>
			</Card>
		</TooltipProvider>
	);
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface CategorySectionProps {
	category: ComponentCategory;
	components: LibraryComponent[];
	isExpanded: boolean;
	onToggle: () => void;
	selectedComponentId?: string | null;
	onSelectComponent: (id: string) => void;
	onViewInStorybook?: (id: string) => void;
	onViewInFigma?: (id: string) => void;
	onViewInCode?: (id: string) => void;
}

function CategorySection({
	category,
	components,
	isExpanded,
	onToggle,
	selectedComponentId,
	onSelectComponent,
	onViewInStorybook,
	onViewInFigma,
	onViewInCode,
}: CategorySectionProps) {
	const Icon = CATEGORY_ICONS[category] || Component;
	const label = CATEGORY_LABELS[category] || category;

	return (
		<Collapsible open={isExpanded} onOpenChange={onToggle}>
			<CollapsibleTrigger asChild>
				<Button
					variant="ghost"
					className="w-full justify-start gap-2 h-8 px-2 mb-1"
				>
					{isExpanded ? (
						<ChevronDown className="h-3.5 w-3.5" />
					) : (
						<ChevronRight className="h-3.5 w-3.5" />
					)}
					<Icon className="h-3.5 w-3.5 text-muted-foreground" />
					<span className="text-sm font-medium">{label}</span>
					<Badge variant="secondary" className="ml-auto text-xs">
						{components.length}
					</Badge>
				</Button>
			</CollapsibleTrigger>
			<CollapsibleContent>
				<div className="pl-6 space-y-0.5 mb-2">
					{components.map((component) => (
						<ComponentListItem
							key={component.id}
							component={component}
							isSelected={selectedComponentId === component.id}
							onSelect={() => onSelectComponent(component.id)}
							onViewInStorybook={
								onViewInStorybook
									? () => onViewInStorybook(component.id)
									: undefined
							}
							onViewInFigma={
								onViewInFigma ? () => onViewInFigma(component.id) : undefined
							}
							onViewInCode={
								onViewInCode ? () => onViewInCode(component.id) : undefined
							}
						/>
					))}
				</div>
			</CollapsibleContent>
		</Collapsible>
	);
}

interface ComponentListItemProps {
	component: LibraryComponent;
	isSelected: boolean;
	onSelect: () => void;
	onViewInStorybook?: () => void;
	onViewInFigma?: () => void;
	onViewInCode?: () => void;
}

function ComponentListItem({
	component,
	isSelected,
	onSelect,
	onViewInStorybook,
	onViewInFigma,
	onViewInCode,
}: ComponentListItemProps) {
	const statusConfig = STATUS_CONFIG[component.status];

	return (
		<div
			className={`
				group flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer transition-colors
				${isSelected ? "bg-primary/10 ring-1 ring-primary/30" : "hover:bg-muted"}
			`}
			onClick={onSelect}
		>
			{/* Thumbnail */}
			{component.thumbnailUrl ? (
				<img
					src={component.thumbnailUrl}
					alt=""
					className="w-8 h-8 rounded border object-cover shrink-0"
				/>
			) : (
				<div className="w-8 h-8 rounded border bg-muted flex items-center justify-center shrink-0">
					<Component className="h-4 w-4 text-muted-foreground" />
				</div>
			)}

			{/* Content */}
			<div className="flex-1 min-w-0">
				<div className="flex items-center gap-1.5">
					<span className="text-sm font-medium truncate">
						{component.displayName}
					</span>
					<Tooltip delayDuration={200}>
						<TooltipTrigger>
							<statusConfig.icon
								className="h-3 w-3 shrink-0"
								style={{ color: statusConfig.color }}
							/>
						</TooltipTrigger>
						<TooltipContent>{statusConfig.label}</TooltipContent>
					</Tooltip>
				</div>
				{component.description && (
					<p className="text-xs text-muted-foreground truncate">
						{component.description}
					</p>
				)}
			</div>

			{/* Actions */}
			<div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
				{component.storybookUrl && onViewInStorybook && (
					<Tooltip delayDuration={200}>
						<TooltipTrigger asChild>
							<Button
								variant="ghost"
								size="sm"
								className="h-6 w-6 p-0"
								onClick={(e) => {
									e.stopPropagation();
									onViewInStorybook();
								}}
							>
								<BookOpen className="h-3.5 w-3.5" />
							</Button>
						</TooltipTrigger>
						<TooltipContent>View in Storybook</TooltipContent>
					</Tooltip>
				)}
				{component.figmaUrl && onViewInFigma && (
					<Tooltip delayDuration={200}>
						<TooltipTrigger asChild>
							<Button
								variant="ghost"
								size="sm"
								className="h-6 w-6 p-0"
								onClick={(e) => {
									e.stopPropagation();
									onViewInFigma();
								}}
							>
								<Figma className="h-3.5 w-3.5" />
							</Button>
						</TooltipTrigger>
						<TooltipContent>View in Figma</TooltipContent>
					</Tooltip>
				)}
				{component.codeRef && onViewInCode && (
					<Tooltip delayDuration={200}>
						<TooltipTrigger asChild>
							<Button
								variant="ghost"
								size="sm"
								className="h-6 w-6 p-0"
								onClick={(e) => {
									e.stopPropagation();
									onViewInCode();
								}}
							>
								<Code className="h-3.5 w-3.5" />
							</Button>
						</TooltipTrigger>
						<TooltipContent>View source code</TooltipContent>
					</Tooltip>
				)}
			</div>

			{/* Usage count */}
			{component.usageCount > 0 && (
				<Tooltip delayDuration={200}>
					<TooltipTrigger>
						<Badge variant="secondary" className="text-[10px] px-1.5 shrink-0">
							{component.usageCount}
						</Badge>
					</TooltipTrigger>
					<TooltipContent>Used {component.usageCount} times</TooltipContent>
				</Tooltip>
			)}
		</div>
	);
}

interface TokensGridProps {
	tokens: DesignToken[];
	libraryId?: string;
}

function TokensGrid({ tokens, libraryId }: TokensGridProps) {
	const libraryTokens = tokens.filter(
		(t) => !libraryId || t.libraryId === libraryId,
	);

	// Group by type
	const groupedTokens = useMemo(() => {
		const grouped = new Map<string, DesignToken[]>();
		for (const token of libraryTokens) {
			const { type } = token;
			if (!grouped.has(type)) {
				grouped.set(type, []);
			}
			grouped.get(type)!.push(token);
		}
		return grouped;
	}, [libraryTokens]);

	if (libraryTokens.length === 0) {
		return (
			<div className="p-8 text-center text-muted-foreground">
				<Palette className="h-8 w-8 mx-auto mb-2 opacity-50" />
				<p className="text-sm">No design tokens found</p>
			</div>
		);
	}

	return (
		<div className="p-4 space-y-4">
			{[...groupedTokens.entries()].map(([type, typeTokens]) => (
				<div key={type}>
					<h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
						{type}
					</h4>
					<div className="grid grid-cols-2 gap-2">
						{typeTokens.slice(0, 20).map((token) => (
							<TokenCard key={token.id} token={token} />
						))}
					</div>
					{typeTokens.length > 20 && (
						<p className="text-xs text-muted-foreground mt-2">
							+{typeTokens.length - 20} more
						</p>
					)}
				</div>
			))}
		</div>
	);
}

interface TokenCardProps {
	token: DesignToken;
}

function TokenCard({ token }: TokenCardProps) {
	const isColor = token.type === "color";

	return (
		<div className="flex items-center gap-2 p-2 rounded-md border bg-card">
			{isColor && (
				<div
					className="w-6 h-6 rounded border shrink-0"
					style={{ backgroundColor: token.resolvedValue || token.value }}
				/>
			)}
			<div className="flex-1 min-w-0">
				<p className="text-xs font-medium truncate">{token.name}</p>
				<p className="text-[10px] text-muted-foreground truncate">
					{token.resolvedValue || token.value}
				</p>
			</div>
		</div>
	);
}

// =============================================================================
// EXPORTS
// =============================================================================

export const ComponentLibraryExplorer = memo(ComponentLibraryExplorerComponent);
