// UI Component Tree - Storybook-like view for UI components and pages

import type { Item, Link } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Input } from "@tracertm/ui/components/Input";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import {
	ChevronDown,
	ChevronRight,
	Component,
	ExternalLink,
	FileCode,
	FolderOpen,
	Layers,
	LayoutGrid,
	Monitor,
	Search,
} from "lucide-react";
import { memo, useMemo, useState } from "react";
import { ENHANCED_TYPE_COLORS } from "./types";

interface UIComponentTreeProps {
	items: Item[];
	links: Link[];
	onSelectItem: (itemId: string) => void;
	selectedItemId: string | null;
}

// UI-related item types
const UI_TYPES = [
	"wireframe",
	"ui_component",
	"page",
	"component",
	"screen",
	"layout",
];

// Tree node structure
interface TreeNode {
	id: string;
	item: Item;
	children: TreeNode[];
	depth: number;
	hasInteraction: boolean;
	linkedPages: string[];
}

function buildUITree(items: Item[], links: Link[]): TreeNode[] {
	// Filter to UI items only
	const uiItems = items.filter(
		(item) =>
			UI_TYPES.includes(item.type?.toLowerCase() || "") ||
			item.view?.toLowerCase().includes("ui") ||
			item.view?.toLowerCase().includes("wireframe"),
	);

	// Build parent-child relationships
	const itemMap = new Map(items.map((item) => [item.id, item]));
	const childrenMap = new Map<string, Item[]>();

	// Group by parent
	for (const item of uiItems) {
		const parentId = item.parentId || "root";
		if (!childrenMap.has(parentId)) {
			childrenMap.set(parentId, []);
		}
		childrenMap.get(parentId)!.push(item);
	}

	// Build interaction map (which pages link to which)
	const interactionMap = new Map<string, string[]>();
	for (const link of links) {
		if (link.type === "related_to" || link.type === "depends_on") {
			const source = itemMap.get(link.sourceId);
			const target = itemMap.get(link.targetId);
			if (
				source &&
				target &&
				UI_TYPES.includes(source.type?.toLowerCase() || "") &&
				UI_TYPES.includes(target.type?.toLowerCase() || "")
			) {
				if (!interactionMap.has(source.id)) {
					interactionMap.set(source.id, []);
				}
				interactionMap.get(source.id)!.push(target.id);
			}
		}
	}

	// Recursive tree builder
	function buildNode(item: Item, depth: number): TreeNode {
		const children = childrenMap.get(item.id) || [];
		const linkedPages = interactionMap.get(item.id) || [];

		return {
			id: item.id,
			item,
			children: children
				.sort((a, b) => (a.title || "").localeCompare(b.title || ""))
				.map((child) => buildNode(child, depth + 1)),
			depth,
			hasInteraction: linkedPages.length > 0,
			linkedPages,
		};
	}

	// Build tree from root items
	const rootItems =
		childrenMap.get("root") || uiItems.filter((i) => !i.parentId);

	// Group by type for better organization
	const pages = rootItems.filter(
		(i) => i.type === "page" || i.type === "screen",
	);
	const components = rootItems.filter(
		(i) => i.type === "component" || i.type === "ui_component",
	);
	const wireframes = rootItems.filter((i) => i.type === "wireframe");
	const layouts = rootItems.filter((i) => i.type === "layout");
	const other = rootItems.filter(
		(i) =>
			![
				"page",
				"screen",
				"component",
				"ui_component",
				"wireframe",
				"layout",
			].includes(i.type || ""),
	);

	return [
		...pages.map((item) => buildNode(item, 0)),
		...wireframes.map((item) => buildNode(item, 0)),
		...layouts.map((item) => buildNode(item, 0)),
		...components.map((item) => buildNode(item, 0)),
		...other.map((item) => buildNode(item, 0)),
	];
}

interface TreeItemProps {
	node: TreeNode;
	selectedId: string | null;
	expandedIds: Set<string>;
	onToggle: (id: string) => void;
	onSelect: (id: string) => void;
	itemMap: Map<string, Item>;
}

function TreeItem({
	node,
	selectedId,
	expandedIds,
	onToggle,
	onSelect,
	itemMap,
}: TreeItemProps) {
	const isExpanded = expandedIds.has(node.id);
	const isSelected = selectedId === node.id;
	const hasChildren = node.children.length > 0;
	const bgColor = ENHANCED_TYPE_COLORS[node.item.type || ""] || "#64748b";

	const typeIcon =
		{
			page: Monitor,
			screen: Monitor,
			component: Component,
			ui_component: Component,
			wireframe: LayoutGrid,
			layout: Layers,
		}[node.item.type || ""] || FileCode;

	const Icon = typeIcon;

	return (
		<div>
			<div
				className={`
          flex items-center gap-1.5 px-2 py-1.5 rounded-md cursor-pointer transition-colors
          ${isSelected ? "bg-primary/10 text-primary" : "hover:bg-muted"}
        `}
				style={{ paddingLeft: `${node.depth * 16 + 8}px` }}
				onClick={() => onSelect(node.id)}
			>
				{/* Expand/Collapse */}
				{hasChildren ? (
					<button
						onClick={(e) => {
							e.stopPropagation();
							onToggle(node.id);
						}}
						className="p-0.5 hover:bg-muted-foreground/20 rounded"
					>
						{isExpanded ? (
							<ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
						) : (
							<ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
						)}
					</button>
				) : (
					<span className="w-4.5" />
				)}

				{/* Icon */}
				<div
					className="rounded p-1"
					style={{ backgroundColor: `${bgColor}20` }}
				>
					<Icon className="h-3.5 w-3.5" style={{ color: bgColor }} />
				</div>

				{/* Title */}
				<span className="flex-1 text-sm truncate">
					{node.item.title || "Untitled"}
				</span>

				{/* Indicators */}
				{node.hasInteraction && (
					<span title="Has page interactions">
						<ExternalLink className="h-3 w-3 text-muted-foreground" />
					</span>
				)}
				{node.children.length > 0 && (
					<Badge variant="secondary" className="text-[10px] px-1.5 h-4">
						{node.children.length}
					</Badge>
				)}
			</div>

			{/* Children */}
			{isExpanded && hasChildren && (
				<div>
					{node.children.map((child) => (
						<TreeItem
							key={child.id}
							node={child}
							selectedId={selectedId}
							expandedIds={expandedIds}
							onToggle={onToggle}
							onSelect={onSelect}
							itemMap={itemMap}
						/>
					))}
				</div>
			)}
		</div>
	);
}

function UIComponentTreeComponent({
	items,
	links,
	onSelectItem,
	selectedItemId,
}: UIComponentTreeProps) {
	const [searchQuery, setSearchQuery] = useState("");
	const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
	const [activeTab, setActiveTab] = useState<"tree" | "interactions">("tree");

	const tree = useMemo(() => buildUITree(items, links), [items, links]);
	const itemMap = useMemo(() => new Map(items.map((i) => [i.id, i])), [items]);

	// Filter tree by search
	const filteredTree = useMemo(() => {
		if (!searchQuery) return tree;

		const query = searchQuery.toLowerCase();

		function filterNode(node: TreeNode): TreeNode | null {
			const matchesTitle = (node.item.title || "")
				.toLowerCase()
				.includes(query);
			const matchesType = (node.item.type || "").toLowerCase().includes(query);

			const filteredChildren = node.children
				.map(filterNode)
				.filter((n): n is TreeNode => n !== null);

			if (matchesTitle || matchesType || filteredChildren.length > 0) {
				return { ...node, children: filteredChildren };
			}
			return null;
		}

		return tree.map(filterNode).filter((n): n is TreeNode => n !== null);
	}, [tree, searchQuery]);

	// Build page interaction matrix
	const interactionMatrix = useMemo(() => {
		const matrix: { from: Item; to: Item; linkType: string }[] = [];

		for (const link of links) {
			const source = itemMap.get(link.sourceId);
			const target = itemMap.get(link.targetId);

			if (source && target) {
				const sourceIsUI = UI_TYPES.includes(source.type?.toLowerCase() || "");
				const targetIsUI = UI_TYPES.includes(target.type?.toLowerCase() || "");

				if (sourceIsUI && targetIsUI) {
					matrix.push({ from: source, to: target, linkType: link.type });
				}
			}
		}

		return matrix;
	}, [links, itemMap]);

	const handleToggle = (id: string) => {
		const newExpanded = new Set(expandedIds);
		if (newExpanded.has(id)) {
			newExpanded.delete(id);
		} else {
			newExpanded.add(id);
		}
		setExpandedIds(newExpanded);
	};

	const expandAll = () => {
		const allIds = new Set<string>();
		function collectIds(node: TreeNode) {
			allIds.add(node.id);
			node.children.forEach(collectIds);
		}
		tree.forEach(collectIds);
		setExpandedIds(allIds);
	};

	const collapseAll = () => {
		setExpandedIds(new Set());
	};

	// Count stats
	const stats = useMemo(() => {
		let pages = 0;
		let components = 0;
		let wireframes = 0;

		function countNode(node: TreeNode) {
			if (node.item.type === "page" || node.item.type === "screen") pages++;
			else if (
				node.item.type === "component" ||
				node.item.type === "ui_component"
			)
				components++;
			else if (node.item.type === "wireframe") wireframes++;
			node.children.forEach(countNode);
		}

		tree.forEach(countNode);
		return {
			pages,
			components,
			wireframes,
			interactions: interactionMatrix.length,
		};
	}, [tree, interactionMatrix]);

	return (
		<Card className="h-full flex flex-col overflow-hidden">
			{/* Header */}
			<div className="p-4 border-b space-y-3">
				<div className="flex items-center justify-between">
					<div className="flex items-center gap-2">
						<LayoutGrid className="h-5 w-5 text-pink-500" />
						<h3 className="font-semibold">UI Component Library</h3>
					</div>
				</div>

				{/* Stats */}
				<div className="flex gap-3 text-xs">
					<div className="flex items-center gap-1">
						<Monitor className="h-3 w-3 text-blue-500" />
						<span>{stats.pages} Pages</span>
					</div>
					<div className="flex items-center gap-1">
						<Component className="h-3 w-3 text-green-500" />
						<span>{stats.components} Components</span>
					</div>
					<div className="flex items-center gap-1">
						<LayoutGrid className="h-3 w-3 text-pink-500" />
						<span>{stats.wireframes} Wireframes</span>
					</div>
					<div className="flex items-center gap-1">
						<ExternalLink className="h-3 w-3 text-orange-500" />
						<span>{stats.interactions} Interactions</span>
					</div>
				</div>

				{/* Search */}
				<div className="relative">
					<Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search components..."
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						className="pl-8 h-9"
					/>
				</div>

				{/* Tab Toggle */}
				<div className="flex gap-1 p-1 bg-muted rounded-lg">
					<Button
						variant={activeTab === "tree" ? "default" : "ghost"}
						size="sm"
						className="flex-1 h-7 text-xs"
						onClick={() => setActiveTab("tree")}
					>
						<FolderOpen className="h-3.5 w-3.5 mr-1" />
						Tree View
					</Button>
					<Button
						variant={activeTab === "interactions" ? "default" : "ghost"}
						size="sm"
						className="flex-1 h-7 text-xs"
						onClick={() => setActiveTab("interactions")}
					>
						<ExternalLink className="h-3.5 w-3.5 mr-1" />
						Interactions
					</Button>
				</div>
			</div>

			{/* Content */}
			<ScrollArea className="flex-1">
				{activeTab === "tree" ? (
					<div className="p-2">
						{/* Expand/Collapse Controls */}
						<div className="flex gap-2 mb-2 px-2">
							<Button
								variant="ghost"
								size="sm"
								className="h-6 text-xs"
								onClick={expandAll}
							>
								Expand All
							</Button>
							<Button
								variant="ghost"
								size="sm"
								className="h-6 text-xs"
								onClick={collapseAll}
							>
								Collapse All
							</Button>
						</div>

						{/* Tree */}
						{filteredTree.length > 0 ? (
							filteredTree.map((node) => (
								<TreeItem
									key={node.id}
									node={node}
									selectedId={selectedItemId}
									expandedIds={expandedIds}
									onToggle={handleToggle}
									onSelect={onSelectItem}
									itemMap={itemMap}
								/>
							))
						) : (
							<div className="text-center py-8 text-muted-foreground">
								<LayoutGrid className="h-12 w-12 mx-auto mb-2 opacity-50" />
								<p className="text-sm">No UI components found</p>
								<p className="text-xs mt-1">
									Add wireframes, pages, or components to see them here
								</p>
							</div>
						)}
					</div>
				) : (
					<div className="p-4 space-y-3">
						{/* Interaction Matrix */}
						<h4 className="text-sm font-medium text-muted-foreground">
							Page Interactions
						</h4>
						{interactionMatrix.length > 0 ? (
							<div className="space-y-2">
								{interactionMatrix.slice(0, 20).map((interaction, idx) => (
									<div
										key={idx}
										className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg text-sm"
									>
										<Button
											variant="ghost"
											size="sm"
											className="h-6 px-2 text-xs"
											onClick={() => onSelectItem(interaction.from.id)}
										>
											{interaction.from.title}
										</Button>
										<ChevronRight className="h-4 w-4 text-muted-foreground" />
										<Badge variant="outline" className="text-[10px]">
											{interaction.linkType.replace(/_/g, " ")}
										</Badge>
										<ChevronRight className="h-4 w-4 text-muted-foreground" />
										<Button
											variant="ghost"
											size="sm"
											className="h-6 px-2 text-xs"
											onClick={() => onSelectItem(interaction.to.id)}
										>
											{interaction.to.title}
										</Button>
									</div>
								))}
								{interactionMatrix.length > 20 && (
									<p className="text-xs text-muted-foreground text-center">
										+{interactionMatrix.length - 20} more interactions
									</p>
								)}
							</div>
						) : (
							<div className="text-center py-8 text-muted-foreground">
								<ExternalLink className="h-12 w-12 mx-auto mb-2 opacity-50" />
								<p className="text-sm">No page interactions found</p>
								<p className="text-xs mt-1">
									Link UI items with "related_to" to map interactions
								</p>
							</div>
						)}
					</div>
				)}
			</ScrollArea>
		</Card>
	);
}

export const UIComponentTree = memo(UIComponentTreeComponent);
