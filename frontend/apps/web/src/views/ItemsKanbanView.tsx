import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import type { Item, ItemStatus } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	Input,
	Skeleton,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui";
import {
	AlertCircle,
	CheckCircle2,
	ClipboardList,
	Clock,
	List,
	MoreVertical,
	Plus,
	Search,
	User,
	Filter,
	ArrowRight,
} from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";
import { useItems, useUpdateItem } from "../hooks/useItems";
import { useProjects } from "../hooks/useProjects";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface KanbanColumn {
	status: ItemStatus;
	title: string;
	color: string;
	icon: React.ComponentType<{ className?: string }>;
}

const columns: KanbanColumn[] = [
	{
		status: "todo",
		title: "BACKLOG",
		color: "border-t-muted",
		icon: ClipboardList,
	},
	{
		status: "in_progress",
		title: "ACTIVE",
		color: "border-t-blue-500",
		icon: Clock,
	},
	{
		status: "done",
		title: "RESOLVED",
		color: "border-t-green-500",
		icon: CheckCircle2,
	},
	{
		status: "blocked",
		title: "BLOCKED",
		color: "border-t-red-500",
		icon: AlertCircle,
	},
];

interface ItemCardProps {
	item: Item;
	onDragStart: (item: Item) => void;
}

const ItemCard = memo(
	function ItemCard({ item, onDragStart }: ItemCardProps) {
		const handleDragStart = useCallback(() => {
			onDragStart(item);
		}, [item, onDragStart]);

		return (
			<div
				draggable
				onDragStart={handleDragStart}
				className="group bg-card hover:bg-accent/5 transition-all cursor-grab active:cursor-grabbing border border-border/50 rounded-xl p-4 shadow-sm hover:shadow-md"
			>
				<Link to={`/items/${item.id}`}>
					<div className="space-y-3">
						<div className="flex justify-between items-start gap-2">
							<Badge
								variant="outline"
								className="text-[9px] px-1.5 h-4 font-black uppercase tracking-tighter shrink-0"
							>
								{item.type}
							</Badge>
							<button className="opacity-0 group-hover:opacity-100 transition-opacity">
								<MoreVertical className="h-3.5 w-3.5 text-muted-foreground" />
							</button>
						</div>

						<h3 className="text-sm font-bold leading-snug group-hover:text-primary transition-colors line-clamp-2">
							{item.title}
						</h3>

						<div className="flex items-center justify-between gap-2 pt-1">
							<div className="flex items-center gap-1.5">
								{item.owner ? (
									<div className="h-5 w-5 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary">
										{item.owner.charAt(0).toUpperCase()}
									</div>
								) : (
									<div className="h-5 w-5 rounded-full bg-muted flex items-center justify-center">
										<User className="h-3 w-3 text-muted-foreground" />
									</div>
								)}
								<span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider truncate max-w-[80px]">
									{item.owner || "Unassigned"}
								</span>
							</div>

							{item.priority && (
								<div
									className={cn(
										"h-1.5 w-1.5 rounded-full",
										item.priority === "critical"
											? "bg-red-500"
											: item.priority === "high"
												? "bg-orange-500"
												: item.priority === "medium"
													? "bg-blue-500"
													: "bg-green-500",
									)}
									title={`Priority: ${item.priority}`}
								/>
							)}
						</div>
					</div>
				</Link>
			</div>
		);
	},
	(prev, next) => {
		// Custom comparison for memoization
		// Return true if props are equal (skip re-render), false if different
		return (
			prev.item.id === next.item.id &&
			prev.item.title === next.item.title &&
			prev.item.type === next.item.type &&
			prev.item.status === next.item.status &&
			prev.item.priority === next.item.priority &&
			prev.item.owner === next.item.owner
		);
	},
);

export function ItemsKanbanView() {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;
	const projectFilter = searchParams?.project || undefined;
	const typeFilter = searchParams?.type || undefined;

	const { data: itemsData, isLoading } = useItems({ projectId: projectFilter });
	const { data: projects } = useProjects();
	const projectsArray = Array.isArray(projects) ? projects : [];
	const items = itemsData?.items ?? [];
	const updateItem = useUpdateItem();

	const [searchQuery, setSearchQuery] = useState("");
	const [draggedItem, setDraggedItem] = useState<Item | null>(null);
	const [isDraggingOver, setIsDraggingOver] = useState<string | null>(null);

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

	const itemsByStatus = useMemo(() => {
		const grouped: Record<string, Item[]> = {
			todo: [],
			in_progress: [],
			done: [],
			blocked: [],
		};
		filteredItems.forEach((item) => {
			const status = item.status;
			if (status && grouped[status]) {
				grouped[status].push(item);
			}
		});
		return grouped;
	}, [filteredItems]);

	const handleDrop = useCallback(
		async (newStatus: ItemStatus) => {
			setIsDraggingOver(null);
			if (!draggedItem || draggedItem.status === newStatus) {
				setDraggedItem(null);
				return;
			}

			try {
				// Optimistic UI update could go here
				await updateItem.mutateAsync({
					id: draggedItem.id,
					data: { status: newStatus },
				});
				toast.success(`Moved to ${newStatus.replace("_", " ")}`);
				setDraggedItem(null);
			} catch (err) {
				toast.error("Failed to update status");
			}
		},
		[draggedItem, updateItem],
	);

	const handleDragStart = useCallback((item: Item) => {
		setDraggedItem(item);
	}, []);

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<div className="flex justify-between items-center">
					<Skeleton className="h-10 w-48" />
					<Skeleton className="h-10 w-64" />
				</div>
				<div className="flex gap-6 overflow-hidden">
					{[1, 2, 3, 4].map((i) => (
						<Skeleton key={i} className="flex-1 h-[600px] rounded-2xl" />
					))}
				</div>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1800px] mx-auto animate-in fade-in duration-500">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Kanban Workflow
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Manage lifecycle and status transitions for project nodes.
					</p>
				</div>
				<div className="flex items-center gap-2">
					<Button
						variant="outline"
						size="sm"
						onClick={() =>
							navigate({ to: "/items", search: searchParams } as any)
						}
						className="gap-2 rounded-xl"
					>
						<List className="h-4 w-4" /> Table
					</Button>
					<Button
						size="sm"
						onClick={() =>
							navigate({
								to: "/items",
								search: { ...searchParams, action: "create" } as any,
							})
						}
						className="gap-2 rounded-xl shadow-lg shadow-primary/20"
					>
						<Plus className="h-4 w-4" /> New Item
					</Button>
				</div>
			</div>

			{/* Filters Control Bar */}
			<Card className="p-2 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-2">
				<div className="relative flex-1 min-w-[200px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Filter items..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				<Select
					value={projectFilter || "all"}
					onValueChange={(v) =>
						navigate({
							search: (prev: any) => ({
								...prev,
								project: v === "all" ? undefined : v,
							}),
						} as any)
					}
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
				<Select
					value={typeFilter || "all"}
					onValueChange={(v) =>
						navigate({
							search: (prev: any) => ({
								...prev,
								type: v === "all" ? undefined : v,
							}),
						} as any)
					}
				>
					<SelectTrigger className="w-[150px] h-10 border-none bg-transparent hover:bg-background/50 transition-colors">
						<SelectValue placeholder="All Types" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All Types</SelectItem>
						{["requirement", "feature", "test", "bug", "task"].map((t) => (
							<SelectItem key={t} value={t} className="capitalize">
								{t}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</Card>

			{/* Kanban Board */}
			<div className="flex gap-6 overflow-x-auto pb-8 min-h-[70vh] -mx-6 px-6 custom-scrollbar">
				{columns.map((column) => {
					const colItems = itemsByStatus[column.status] || [];
					const isOver = isDraggingOver === column.status;

					return (
						<div
							key={column.status}
							className="flex-1 min-w-[320px] flex flex-col space-y-4"
							onDragOver={(e) => {
								e.preventDefault();
								setIsDraggingOver(column.status);
							}}
							onDragLeave={() => setIsDraggingOver(null)}
							onDrop={() => handleDrop(column.status)}
						>
							<div
								className={cn(
									"flex items-center justify-between p-3 rounded-2xl border-t-4 transition-all",
									column.color,
									isOver ? "bg-primary/5 scale-[1.02]" : "bg-muted/30",
								)}
							>
								<div className="flex items-center gap-2">
									<column.icon className="h-4 w-4 text-muted-foreground" />
									<h2 className="text-[10px] font-black uppercase tracking-[0.2em]">
										{column.title}
									</h2>
								</div>
								<Badge
									variant="secondary"
									className="text-[10px] font-black rounded-full h-5 px-2"
								>
									{colItems.length}
								</Badge>
							</div>

							<div
								className={cn(
									"flex-1 flex flex-col gap-3 p-2 rounded-2xl transition-colors duration-200",
									isOver
										? "bg-primary/5 ring-2 ring-primary/20 ring-dashed"
										: "transparent",
								)}
							>
								{colItems.map((item) => (
									<ItemCard
										key={item.id}
										item={item}
										onDragStart={handleDragStart}
									/>
								))}
								{colItems.length === 0 && (
									<div className="flex flex-col items-center justify-center py-12 text-muted-foreground/30 border-2 border-dashed border-border/50 rounded-2xl">
										<ArrowRight className="h-8 w-8 mb-2 rotate-90" />
										<p className="text-[10px] font-bold uppercase tracking-widest text-center">
											Empty Drop Zone
										</p>
									</div>
								)}
							</div>
						</div>
					);
				})}
			</div>
		</div>
	);
}
