import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import type { Item } from "@tracertm/types";
import { Alert } from "@tracertm/ui/components/Alert";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Input } from "@tracertm/ui/components/Input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { Lightbulb } from "lucide-react";
import { useMemo, useState } from "react";
import { useItems } from "../hooks/useItems";
import { useProjects } from "../hooks/useProjects";

interface TreeNode {
	item: Item;
	children: TreeNode[];
	level: number;
}

interface TreeItemProps {
	node: TreeNode;
	expandedIds: Set<string>;
	onToggleExpand: (id: string) => void;
}

function TreeItem({ node, expandedIds, onToggleExpand }: TreeItemProps) {
	const { item, children, level } = node;
	const hasChildren = children.length > 0;
	const isExpanded = expandedIds.has(item.id);

	return (
		<div className="select-none">
			<div
				className={`flex items-center gap-2 p-3 rounded-lg hover:bg-muted/50 transition-colors`}
				style={{ paddingLeft: `${level * 24 + 12}px` }}
			>
				{hasChildren && (
					<Button
						variant="ghost"
						size="sm"
						onClick={() => onToggleExpand(item.id)}
						className="flex-shrink-0 h-5 w-5 p-0"
					>
						{isExpanded ? "▼" : "▶"}
					</Button>
				)}
				{!hasChildren && <div className="w-5" />}

				<div className="flex-1 flex items-center gap-3">
					<Link to={`/items/${item.id}`} className="flex-1 group">
						<div className="flex items-center gap-2">
							<span className="font-medium group-hover:text-primary transition-colors">
								{item.title}
							</span>
							<Badge variant="secondary" className="text-xs">
								{item.type}
							</Badge>
							<Badge
								variant={
									item.status === "done"
										? "success"
										: item.status === "in_progress"
											? "info"
											: item.status === "blocked"
												? "destructive"
												: "secondary"
								}
								className="text-xs"
							>
								{item.status.replace("_", " ")}
							</Badge>
						</div>
					</Link>

					{item.owner && (
						<span className="text-sm text-muted-foreground">{item.owner}</span>
					)}

					{hasChildren && (
						<span className="text-sm text-muted-foreground">
							{children.length} {children.length === 1 ? "child" : "children"}
						</span>
					)}
				</div>
			</div>

			{hasChildren && isExpanded && (
				<div>
					{children.map((child) => (
						<TreeItem
							key={child.item.id}
							node={child}
							expandedIds={expandedIds}
							onToggleExpand={onToggleExpand}
						/>
					))}
				</div>
			)}
		</div>
	);
}

function buildTree(items: Item[]): TreeNode[] {
	const itemMap = new Map<string, TreeNode>();
	const rootNodes: TreeNode[] = [];

	// Create nodes for all items
	items.forEach((item) => {
		itemMap.set(item.id, {
			item,
			children: [],
			level: 0,
		});
	});

	// Build parent-child relationships
	items.forEach((item) => {
		const node = itemMap.get(item.id)!;

		if (item.parentId) {
			const parent = itemMap.get(item.parentId);
			if (parent) {
				node.level = parent.level + 1;
				parent.children.push(node);
			} else {
				// Parent not found, treat as root
				rootNodes.push(node);
			}
		} else {
			// No parent, this is a root node
			rootNodes.push(node);
		}
	});

	return rootNodes;
}

export function ItemsTreeView() {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;
	const projectFilter = searchParams?.project || undefined;
	const typeFilter = searchParams?.type || undefined;

	const {
		data: itemsData,
		isLoading,
		error,
	} = useItems({ projectId: projectFilter });
	const { data: projects } = useProjects();
	// Ensure projects is always an array
	const projectsArray = Array.isArray(projects) ? projects : [];
	const items = itemsData?.items ?? [];

	const [searchQuery, setSearchQuery] = useState("");
	const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
	const [expandAll, setExpandAll] = useState(false);

	// Filter items
	const filteredItems = useMemo(() => {
		if (!items.length) return [];

		return items.filter((item: any) => {
			if (typeFilter && item.type !== typeFilter) return false;
			if (searchQuery) {
				const query = searchQuery.toLowerCase();
				return (
					item.title.toLowerCase().includes(query) ||
					item.description?.toLowerCase().includes(query)
				);
			}
			return true;
		});
	}, [items, typeFilter, searchQuery]);

	// Build tree structure
	const treeNodes = useMemo(() => buildTree(filteredItems), [filteredItems]);

	// Count stats
	const stats = useMemo(() => {
		const totalItems = filteredItems.length;
		const rootItems = filteredItems.filter((item) => !item.parentId).length;
		const childItems = totalItems - rootItems;
		const maxDepth = Math.max(
			0,
			...filteredItems.map((item) => {
				let depth = 0;
				let current = item;
				const visited = new Set<string>();
				while (current.parentId && !visited.has(current.id)) {
					visited.add(current.id);
					const parent = filteredItems.find((i) => i.id === current.parentId);
					if (parent) {
						depth++;
						current = parent;
					} else {
						break;
					}
				}
				return depth;
			}),
		);

		return { totalItems, rootItems, childItems, maxDepth };
	}, [filteredItems]);

	const handleToggleExpand = (id: string) => {
		const newExpanded = new Set(expandedIds);
		if (newExpanded.has(id)) {
			newExpanded.delete(id);
		} else {
			newExpanded.add(id);
		}
		setExpandedIds(newExpanded);
	};

	const handleExpandAll = () => {
		if (expandAll) {
			setExpandedIds(new Set());
		} else {
			const allIds = new Set(filteredItems.map((item) => item.id));
			setExpandedIds(allIds);
		}
		setExpandAll(!expandAll);
	};

	if (isLoading) {
		return (
			<div className="space-y-6">
				<Skeleton className="h-12 w-full" />
				<Skeleton className="h-96" />
			</div>
		);
	}

	if (error) {
		return (
			<Alert variant="destructive">Failed to load items: {error.message}</Alert>
		);
	}

	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Tree View</h1>
					<p className="mt-2 text-muted-foreground">
						Hierarchical view of items and their relationships
					</p>
				</div>
				<div className="flex items-center gap-2">
					<Link to="/items">
						<Button variant="outline">Table View</Button>
					</Link>
					<Link to="/items/kanban">
						<Button variant="outline">Kanban View</Button>
					</Link>
					<Link to={`/items?action=create`}>
						<Button>+ New Item</Button>
					</Link>
				</div>
			</div>

			{/* Filters */}
			<Card className="p-4">
				<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
					<Input
						type="search"
						placeholder="Search items..."
						value={searchQuery}
						onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
							setSearchQuery((e.currentTarget as HTMLInputElement).value)
						}
					/>
					{projects && (
						<Select
							value={projectFilter || "all"}
							onValueChange={(value) => {
								navigate({
									search: (prev: any) => {
										const newSearch = {
											...(prev || {}),
											project: value === "all" ? undefined : value,
										};
										return newSearch as any;
									},
								} as any);
							}}
						>
							<SelectTrigger>
								<SelectValue placeholder="All Projects" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="all">All Projects</SelectItem>
								{projectsArray.map((project) => (
									<SelectItem key={project.id} value={project.id}>
										{project.name}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					)}
					<Select
						value={typeFilter || "all"}
						onValueChange={(value) => {
							navigate({
								search: (prev: any) => {
									const newSearch = {
										...(prev || {}),
										type: value === "all" ? undefined : value,
									};
									return newSearch as any;
								},
							} as any);
						}}
					>
						<SelectTrigger>
							<SelectValue placeholder="All Types" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="all">All Types</SelectItem>
							<SelectItem value="requirement">Requirement</SelectItem>
							<SelectItem value="feature">Feature</SelectItem>
							<SelectItem value="test">Test</SelectItem>
							<SelectItem value="bug">Bug</SelectItem>
						</SelectContent>
					</Select>
					<Button onClick={handleExpandAll}>
						{expandAll ? "Collapse All" : "Expand All"}
					</Button>
				</div>
			</Card>

			{/* Stats */}
			<div className="grid grid-cols-4 gap-4">
				<Card className="p-4">
					<div className="text-sm font-medium text-muted-foreground">
						Total Items
					</div>
					<div className="mt-2 text-2xl font-semibold">{stats.totalItems}</div>
				</Card>
				<Card className="p-4">
					<div className="text-sm font-medium text-muted-foreground">
						Root Items
					</div>
					<div className="mt-2 text-2xl font-semibold">{stats.rootItems}</div>
				</Card>
				<Card className="p-4">
					<div className="text-sm font-medium text-muted-foreground">
						Child Items
					</div>
					<div className="mt-2 text-2xl font-semibold">{stats.childItems}</div>
				</Card>
				<Card className="p-4">
					<div className="text-sm font-medium text-muted-foreground">
						Max Depth
					</div>
					<div className="mt-2 text-2xl font-semibold">{stats.maxDepth}</div>
				</Card>
			</div>

			{/* Tree */}
			<Card className="p-4">
				{treeNodes.length > 0 ? (
					<div className="space-y-1">
						{treeNodes.map((node) => (
							<TreeItem
								key={node.item.id}
								node={node}
								expandedIds={expandedIds}
								onToggleExpand={handleToggleExpand}
							/>
						))}
					</div>
				) : (
					<div className="text-center py-12 text-muted-foreground">
						<p>No items found</p>
					</div>
				)}
			</Card>

			{/* Help Text */}
			<Card className="p-4 bg-primary/10 border-primary/20">
				<div className="flex items-start gap-3">
					<Lightbulb className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
					<div>
						<h3 className="font-medium mb-1">How to use</h3>
						<p className="text-sm text-muted-foreground">
							Click the arrows to expand/collapse items with children. Items are
							organized by parent-child relationships.
						</p>
					</div>
				</div>
			</Card>
		</div>
	);
}
