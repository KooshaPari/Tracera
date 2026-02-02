import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import type { Item } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	Input,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
	Skeleton,
} from "@tracertm/ui";
import {
	ChevronDown,
	ChevronRight,
	FileText,
	Filter,
	Layers,
	List,
	Maximize2,
	Minimize2,
	Network,
	Plus,
	Search,
	Target,
} from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";
import { cn } from "@/lib/utils";
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
	projectFilter?: string;
}

const TreeExpandButton = memo(function TreeExpandButton({
	isExpanded,
	onClick,
}: {
	isExpanded: boolean;
	onClick: () => void;
}) {
	return (
		<button
			onClick={onClick}
			className="flex h-6 w-6 items-center justify-center rounded-lg hover:bg-muted transition-colors text-muted-foreground"
		>
			{isExpanded ? (
				<ChevronDown className="h-4 w-4" />
			) : (
				<ChevronRight className="h-4 w-4" />
			)}
		</button>
	);
});

const TreeItemIcon = memo(function TreeItemIcon({
	isExpanded,
}: {
	isExpanded: boolean;
}) {
	return (
		<div
			className={cn(
				"h-8 w-8 rounded-lg flex items-center justify-center shrink-0 transition-colors",
				isExpanded
					? "bg-primary text-primary-foreground"
					: "bg-muted text-muted-foreground group-hover/link:bg-primary/10 group-hover/link:text-primary",
			)}
		>
			<FileText className="h-4 w-4" />
		</div>
	);
});

const TreeItemContent = memo(
	function TreeItemContent({
		item,
		isExpanded,
		childCount,
		projectFilter,
	}: {
		item: Item;
		isExpanded: boolean;
		childCount: number;
		projectFilter?: string;
	}) {
		return (
			<div className="flex-1 min-w-0 flex items-center gap-4">
				<Link
					to={
						projectFilter
							? `/projects/${projectFilter}/views/${String(item.view || "feature").toLowerCase()}/${item.id}`
							: "/projects"
					}
					className="flex-1 flex items-center gap-3 min-w-0 group/link"
				>
					<TreeItemIcon isExpanded={isExpanded} />
					<div className="flex flex-col min-w-0">
						<span className="text-sm font-bold truncate group-hover/link:text-primary transition-colors">
							{item.title}
						</span>
						<div className="flex items-center gap-2 mt-0.5">
							<Badge
								variant="outline"
								className="text-[8px] h-3.5 px-1 uppercase font-black tracking-tighter"
							>
								{item.type}
							</Badge>
							<span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
								{item.status}
							</span>
						</div>
					</div>
				</Link>

				<div className="hidden md:flex items-center gap-6 shrink-0 mr-4">
					{item.owner && (
						<div className="flex items-center gap-1.5">
							<div className="h-4 w-4 rounded-full bg-muted flex items-center justify-center text-[8px] font-black uppercase">
								{item.owner.charAt(0)}
							</div>
							<span className="text-[10px] font-bold text-muted-foreground uppercase">
								{item.owner}
							</span>
						</div>
					)}
					{childCount > 0 && (
						<Badge
							variant="secondary"
							className="text-[9px] font-black rounded-full px-1.5 h-4"
						>
							{childCount}
						</Badge>
					)}
				</div>
			</div>
		);
	},
	(prev, next) => (
			prev.item.id === next.item.id &&
			prev.item.title === next.item.title &&
			prev.item.type === next.item.type &&
			prev.item.status === next.item.status &&
			prev.item.owner === next.item.owner &&
			prev.isExpanded === next.isExpanded &&
			prev.childCount === next.childCount &&
			prev.projectFilter === next.projectFilter
		),
);

const TreeItem = memo(
	function TreeItem({ node, expandedIds, onToggleExpand, projectFilter }: TreeItemProps) {
		const { item, children, level } = node;
		const hasChildren = children.length > 0;
		const isExpanded = expandedIds.has(item.id);

		const handleToggle = useCallback(() => {
			onToggleExpand(item.id);
		}, [item.id, onToggleExpand]);

		return (
			<div className="select-none">
				<div
					className={cn(
						"group flex items-center gap-3 p-2 rounded-xl transition-all duration-200 border border-transparent",
						isExpanded
							? "bg-primary/[0.03] border-primary/5"
							: "hover:bg-muted/50",
					)}
					style={{ marginLeft: `${level * 20}px` }}
				>
					{hasChildren ? (
						<TreeExpandButton isExpanded={isExpanded} onClick={handleToggle} />
					) : (
						<div className="w-6 h-6 flex items-center justify-center">
							<div className="h-1 w-1 rounded-full bg-muted-foreground/30" />
						</div>
					)}

					<TreeItemContent
						item={item}
						isExpanded={isExpanded}
						childCount={children.length}
						{...(projectFilter != null ? { projectFilter } : {})}
					/>
				</div>

				{hasChildren && isExpanded && (
					<div className="mt-1 space-y-1 relative before:absolute before:left-[11px] before:top-0 before:bottom-0 before:w-px before:bg-border/50">
						{children.map((child) => (
							<TreeItem
								key={child.item.id}
								node={child}
								expandedIds={expandedIds}
								onToggleExpand={onToggleExpand}
								{...(projectFilter != null ? { projectFilter } : {})}
							/>
						))}
					</div>
				)}
			</div>
		);
	},
	(prev, next) => (
			prev.node.item.id === next.node.item.id &&
			prev.node.item.title === next.node.item.title &&
			prev.node.item.type === next.node.item.type &&
			prev.node.item.status === next.node.item.status &&
			prev.node.item.owner === next.node.item.owner &&
			prev.node.level === next.node.level &&
			prev.node.children.length === next.node.children.length &&
			prev.expandedIds.has(prev.node.item.id) ===
				next.expandedIds.has(next.node.item.id) &&
			// Compare child IDs to detect structural changes
			prev.node.children.every(
				(child, idx) =>
					next.node.children[idx] &&
					child.item.id === next.node.children[idx].item.id,
			)
		),
);

function setTreeNodeLevel(node: TreeNode, level: number): void {
	node.level = level;
	node.children.forEach((child) => setTreeNodeLevel(child, level + 1));
}

function buildTree(items: Item[]): TreeNode[] {
	const itemMap = new Map<string, TreeNode>();
	const rootNodes: TreeNode[] = [];

	items.forEach((item) => {
		itemMap.set(item.id, { children: [], item, level: 0 });
	});

	items.forEach((item) => {
		const node = itemMap.get(item.id)!;
		if (item.parentId && itemMap.has(item.parentId)) {
			const parent = itemMap.get(item.parentId)!;
			node.level = parent.level + 1; // Basic level, will be corrected in recursion if needed
			parent.children.push(node);
		} else {
			rootNodes.push(node);
		}
	});

	rootNodes.forEach((root) => setTreeNodeLevel(root, 0));

	return rootNodes;
}

export function ItemsTreeView() {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;
	const projectFilter = searchParams?.project || undefined;
	const typeFilter = searchParams?.type || undefined;

	const { data: itemsData, isLoading } = useItems({ projectId: projectFilter });
	const { data: projects } = useProjects();
	const projectsArray = useMemo(
		() => (Array.isArray(projects) ? projects : []),
		[projects],
	);
	const items = itemsData?.items ?? [];

	const [searchQuery, setSearchQuery] = useState("");
	const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

	const filteredItems = useMemo(() => {
		if (items.length === 0) {return [];}
		return items.filter((item: any) => {
			if (typeFilter && item.type !== typeFilter) {return false;}
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

	const treeNodes = useMemo(() => buildTree(filteredItems), [filteredItems]);

	const handleToggleExpand = useCallback((id: string) => {
		setExpandedIds((prev) => {
			const next = new Set(prev);
			if (next.has(id)) {next.delete(id);}
			else {next.add(id);}
			return next;
		});
	}, []);

	const toggleAll = useCallback(
		(expand: boolean) => {
			if (expand) {setExpandedIds(new Set(filteredItems.map((i) => i.id)));}
			else {setExpandedIds(new Set());}
		},
		[filteredItems],
	);

	const handleNavigateToTable = useCallback(() => {
		if (!projectFilter) {
			undefined;
			return;
		}
		undefined;
	}, [navigate, searchParams, projectFilter]);

	const handleNavigateToCreate = useCallback(() => {
		if (!projectFilter) {
			undefined;
			return;
		}
		undefined;
	}, [navigate, searchParams, projectFilter]);

	const handleProjectFilterChange = useCallback(
		(v: string) => {
			undefined;
		},
		[navigate],
	);

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<Skeleton className="h-12 w-full rounded-2xl" />
				<div className="space-y-4">
					{[1, 2, 3, 4, 5, 6].map((i) => (
						<Skeleton key={i} className="h-12 w-full rounded-xl" />
					))}
				</div>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-5xl mx-auto animate-in fade-in duration-500">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Logical Hierarchy
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Decompose requirements and features into atomic nodes.
					</p>
				</div>
				<div className="flex items-center gap-2">
					<Button
						variant="outline"
						size="sm"
						onClick={handleNavigateToTable}
						className="gap-2 rounded-xl"
					>
						<List className="h-4 w-4" /> Table
					</Button>
					<Button
						size="sm"
						onClick={handleNavigateToCreate}
						className="gap-2 rounded-xl shadow-lg shadow-primary/20"
					>
						<Plus className="h-4 w-4" /> New Node
					</Button>
				</div>
			</div>

			{/* Filters & Actions Bar */}
			<Card className="p-2 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-2">
				<div className="relative flex-1 min-w-[200px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search hierarchy..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				<Select
					value={projectFilter || "all"}
					onValueChange={handleProjectFilterChange}
				>
					<SelectTrigger className="w-[180px] h-10 border-none bg-transparent hover:bg-background/50 transition-colors">
						<div className="flex items-center gap-2">
							<Filter className="h-3.5 w-3.5 text-muted-foreground" />
							<SelectValue placeholder="All Projects" />
						</div>
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All Projects</SelectItem>
						{projectsArray.map((p) => (
							<SelectItem key={p.id} value={p.id}>
								{p.name}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
				<div className="flex items-center gap-1 ml-auto pr-2">
					<Button
						variant="ghost"
						size="icon"
						onClick={() => toggleAll(true)}
						className="h-8 w-8 text-muted-foreground hover:text-primary"
						title="Expand All"
					>
						<Maximize2 className="h-4 w-4" />
					</Button>
					<Button
						variant="ghost"
						size="icon"
						onClick={() => toggleAll(false)}
						className="h-8 w-8 text-muted-foreground hover:text-primary"
						title="Collapse All"
					>
						<Minimize2 className="h-4 w-4" />
					</Button>
				</div>
			</Card>

			{/* Tree Content */}
			<Card className="p-4 border-none bg-card/50 shadow-sm rounded-2xl min-h-[400px]">
				{treeNodes.length > 0 ? (
					<div className="space-y-1">
						{treeNodes.map((node) => (
							<TreeItem
								key={node.item.id}
								node={node}
								expandedIds={expandedIds}
								onToggleExpand={handleToggleExpand}
								{...(projectFilter != null ? { projectFilter } : {})}
							/>
						))}
					</div>
				) : (
					<div className="flex flex-col items-center justify-center py-20 text-muted-foreground/40">
						<Network className="h-16 w-16 mb-4 opacity-10" />
						<p className="text-xs font-black uppercase tracking-[0.2em]">
							No structure defined
						</p>
					</div>
				)}
			</Card>

			{/* Executive Summary */}
			<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
				{[
					{ icon: Layers, label: "Total Nodes", value: filteredItems.length },
					{ icon: Target, label: "Root Items", value: treeNodes.length },
					{
						icon: FileText,
						label: "Leaf Items",
						value: filteredItems.length - treeNodes.length,
					},
					{
						icon: Network,
						label: "Depth",
						value: Math.max(
							0,
							...filteredItems.map((i) => (i.parentId ? 1 : 0)),
						),
					},
				].map((s, i) => (
					<Card
						key={i}
						className="p-4 border-none bg-muted/30 flex items-center justify-between"
					>
						<div>
							<p className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">
								{s.label}
							</p>
							<p className="text-xl font-black">{s.value}</p>
						</div>
						<s.icon className="h-5 w-5 text-primary opacity-20" />
					</Card>
				))}
			</div>
		</div>
	);
}
