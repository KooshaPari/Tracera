import { useNavigate, useSearch } from "@tanstack/react-router";
import type { ItemStatus, Priority, ViewType } from "@tracertm/types";
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
	ArrowDown,
	ArrowUp,
	X,
	Plus,
	Search,
	Trash2,
	ExternalLink,
	Filter,
	Activity,
	CheckCircle2,
	Clock,
	AlertCircle,
	Terminal,
} from "lucide-react";
import { toast } from "sonner";
import { useCallback, useEffect, useMemo, useState, useRef, memo } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { useCreateItem, useDeleteItem, useItems } from "../hooks/useItems";
import { useProjects } from "../hooks/useProjects";

function getStatusBadge(status: ItemStatus) {
	const config = {
		done: {
			color: "bg-green-500/10 text-green-600 border-green-500/20",
			icon: CheckCircle2,
		},
		in_progress: {
			color: "bg-blue-500/10 text-blue-600 border-blue-500/20",
			icon: Clock,
		},
		blocked: {
			color: "bg-red-500/10 text-red-600 border-red-500/20",
			icon: AlertCircle,
		},
		todo: { color: "bg-muted text-muted-foreground", icon: Terminal },
		cancelled: {
			color: "bg-orange-500/10 text-orange-600 border-orange-500/20",
			icon: X,
		},
	};
	const c = config[status] || config.todo;
	return (
		<Badge
			className={cn(
				"text-[9px] font-black uppercase tracking-tighter gap-1 border",
				c.color,
			)}
		>
			<c.icon className="h-2.5 w-2.5" />
			{status.replace("_", " ")}
		</Badge>
	);
}

function getPriorityDot(priority?: Priority) {
	const colors = {
		critical: "bg-red-500",
		high: "bg-orange-500",
		medium: "bg-blue-500",
		low: "bg-green-500",
	};
	return (
		<div
			className={cn("h-1.5 w-1.5 rounded-full", colors[priority || "medium"])}
		/>
	);
}

// Memoized row component for optimal rendering performance
interface VirtualTableRowProps {
	item: any;
	onDelete: (id: string) => void;
	onNavigate: (path: string) => void;
}

const VirtualTableRow = memo(
	({ item, onDelete, onNavigate }: VirtualTableRowProps) => {
		const handleNavigate = useCallback(() => {
			onNavigate(`/items/${item.id}`);
		}, [item.id, onNavigate]);

		const handleDelete = useCallback(() => {
			onDelete(item.id);
		}, [item.id, onDelete]);

		return (
			<TableRow className="group border-b border-border/30 hover:bg-muted/30 transition-colors">
				<TableCell className="px-6 py-4">
					<button
						onClick={handleNavigate}
						className="block group/link w-full text-left"
					>
						<div className="font-bold text-sm group-hover/link:text-primary transition-colors truncate">
							{item.title}
						</div>
						<div className="text-[10px] font-mono text-muted-foreground uppercase mt-0.5">
							{item.id.slice(0, 12)}
						</div>
					</button>
				</TableCell>
				<TableCell>
					<Badge
						variant="outline"
						className="text-[8px] font-black uppercase tracking-tighter px-1.5 h-4"
					>
						{item.type}
					</Badge>
				</TableCell>
				<TableCell>{getStatusBadge(item.status)}</TableCell>
				<TableCell>
					<div className="flex items-center gap-2">
						{getPriorityDot(item.priority)}
						<span className="text-[10px] font-bold uppercase text-muted-foreground">
							{item.priority || "medium"}
						</span>
					</div>
				</TableCell>
				<TableCell>
					<div className="flex items-center gap-2">
						<div className="h-5 w-5 rounded-full bg-muted flex items-center justify-center text-[8px] font-black uppercase">
							{item.owner?.charAt(0) || "?"}
						</div>
						<span className="text-[10px] font-bold uppercase text-muted-foreground">
							{item.owner || "Unassigned"}
						</span>
					</div>
				</TableCell>
				<TableCell className="text-right px-6">
					<div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
						<Button
							variant="ghost"
							size="icon"
							className="h-8 w-8 rounded-lg"
							onClick={handleNavigate}
						>
							<ExternalLink className="h-3.5 w-3.5" />
						</Button>
						<Button
							variant="ghost"
							size="icon"
							className="h-8 w-8 rounded-lg text-destructive hover:bg-destructive/10"
							onClick={handleDelete}
						>
							<Trash2 className="h-3.5 w-3.5" />
						</Button>
					</div>
				</TableCell>
			</TableRow>
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

interface ItemsTableViewProps {
	projectId?: string;
	view?: ViewType;
	type?: string;
}

export function ItemsTableView({
	projectId,
	view,
	type,
}: ItemsTableViewProps = {}) {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;
	const projectFilter = searchParams?.project;
	const typeFilter = searchParams?.type;
	const actionParam = searchParams?.action;

	const effectiveProjectId = projectId || projectFilter;
	const effectiveTypeFilter = type || typeFilter;

	const { data: itemsData, isLoading } = useItems({
		projectId: effectiveProjectId,
		view,
	});
	const items = itemsData?.items || [];
	const { data: projects } = useProjects();
	const projectsArray = Array.isArray(projects) ? projects : [];
	const deleteItem = useDeleteItem();
	const createItem = useCreateItem();

	const [showCreateModal, setShowCreateModal] = useState(false);
	const [newTitle, setNewTitle] = useState("");
	const [newType, setNewType] = useState(type || "feature");
	const [newPriority, setNewPriority] = useState<Priority>("medium");
	const [newStatus, setNewStatus] = useState<ItemStatus>("todo");

	const [searchQuery, setSearchQuery] = useState("");
	const [sortColumn, setSortColumn] = useState<string>("created");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

	// Virtual scroll container ref
	const parentRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (actionParam === "create") {
			setShowCreateModal(true);
		}
	}, [actionParam]);

	const closeCreateModal = useCallback(() => {
		setShowCreateModal(false);
		navigate({
			search: (prev: any) => {
				const { action, ...rest } = prev || {};
				return rest;
			},
		} as any);
	}, [navigate]);

	const handleCreate = useCallback(async () => {
		if (!effectiveProjectId) {
			toast.error("Select a project before creating a node.");
			return;
		}
		if (!newTitle.trim()) {
			toast.error("Title is required.");
			return;
		}
		try {
			await createItem.mutateAsync({
				projectId: effectiveProjectId,
				view: (view as any) || "feature",
				type: newType || (view as any) || "feature",
				title: newTitle.trim(),
				status: newStatus,
				priority: newPriority,
			});
			toast.success("Node created");
			setNewTitle("");
			setNewType(type || "feature");
			closeCreateModal();
		} catch {
			toast.error("Failed to create node");
		}
	}, [
		effectiveProjectId,
		newTitle,
		newType,
		newStatus,
		newPriority,
		view,
		type,
		createItem,
		closeCreateModal,
	]);

	const filteredAndSortedItems = useMemo(() => {
		const filtered = items.filter((i) => {
			const matchesType =
				!effectiveTypeFilter || i.type === effectiveTypeFilter;
			const matchesQuery =
				i.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				i.id.toLowerCase().includes(searchQuery.toLowerCase());
			return matchesType && matchesQuery;
		});

		return filtered.sort((a, b) => {
			const dir = sortOrder === "asc" ? 1 : -1;
			if (sortColumn === "title") return a.title.localeCompare(b.title) * dir;
			if (sortColumn === "created")
				return (
					(new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()) *
					dir
				);
			return 0;
		});
	}, [items, effectiveTypeFilter, searchQuery, sortColumn, sortOrder]);

	// Virtual scroll setup
	const rowVirtualizer = useVirtualizer({
		count: filteredAndSortedItems.length,
		getScrollElement: () => parentRef.current,
		estimateSize: () => 68, // Estimated row height (TableRow with padding)
		overscan: 10, // Render 10 extra rows outside viewport for smoother scrolling
	});

	const handleDelete = useCallback(
		async (id: string) => {
			try {
				await deleteItem.mutateAsync(id);
				toast.success("Node purged from registry");
			} catch {
				toast.error("Purge failure");
			}
		},
		[deleteItem],
	);

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="space-y-4">
					{[1, 2, 3, 4, 5, 6].map((i) => (
						<Skeleton key={i} className="h-16 w-full rounded-xl" />
					))}
				</div>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1600px] mx-auto animate-in fade-in duration-500 pb-20">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Node Registry
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Flat-file management of project entities and artifacts.
					</p>
				</div>
				<div className="flex items-center gap-2">
					<Button
						variant="outline"
						size="sm"
						onClick={() =>
							navigate({ to: "/items/kanban", search: searchParams } as any)
						}
						className="gap-2 rounded-xl"
					>
						<Activity className="h-4 w-4" /> Workflow
					</Button>
					<Button
						size="sm"
						onClick={() =>
							navigate({
								search: (prev: any) => ({ ...prev, action: "create" }),
							} as any)
						}
						className="gap-2 rounded-xl shadow-lg shadow-primary/20"
					>
						<Plus className="h-4 w-4" /> New Node
					</Button>
				</div>
			</div>

			{/* Filters Bar */}
			<Card className="p-2 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-2">
				<div className="relative flex-1 min-w-[250px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search identifiers..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				{!projectId && (
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
							<SelectItem value="all">Global Scope</SelectItem>
							{projectsArray.map((p) => (
								<SelectItem key={p.id} value={p.id}>
									{p.name}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				)}
				{!type && (
					<Select
						value={effectiveTypeFilter || "all"}
						onValueChange={(v) =>
							navigate({
								search: (prev: any) => ({
									...prev,
									type: v === "all" ? undefined : v,
								}),
							} as any)
						}
					>
						<SelectTrigger className="w-[140px] h-10 border-none bg-transparent hover:bg-background/50 transition-colors">
							<SelectValue placeholder="All Types" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="all">Any Type</SelectItem>
							{["requirement", "feature", "test", "bug", "task"].map((t) => (
								<SelectItem key={t} value={t} className="capitalize">
									{t}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				)}
			</Card>

			{/* Table Content with Virtual Scrolling */}
			<Card className="border-none bg-card/50 shadow-sm rounded-[2rem] overflow-hidden flex flex-col">
				<div className="overflow-x-auto custom-scrollbar">
					<Table>
						<TableHeader>
							<TableRow className="hover:bg-transparent border-b border-border/50">
								<TableHead className="w-[400px] h-14 px-6 text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10">
									<button
										onClick={() => {
											setSortColumn("title");
											setSortOrder(sortOrder === "asc" ? "desc" : "asc");
										}}
										className="flex items-center gap-2"
									>
										Node Identifier{" "}
										{sortColumn === "title" &&
											(sortOrder === "asc" ? (
												<ArrowUp className="h-3 w-3" />
											) : (
												<ArrowDown className="h-3 w-3" />
											))}
									</button>
								</TableHead>
								<TableHead className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10">
									Type
								</TableHead>
								<TableHead className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10">
									Status
								</TableHead>
								<TableHead className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10">
									Priority
								</TableHead>
								<TableHead className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10">
									Owner
								</TableHead>
								<TableHead className="text-right px-6 text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10">
									Actions
								</TableHead>
							</TableRow>
						</TableHeader>
					</Table>
				</div>

				{/* Virtual scrolling container */}
				<div
					ref={parentRef}
					className="h-[600px] overflow-y-auto overflow-x-hidden custom-scrollbar flex-1"
				>
					{filteredAndSortedItems.length > 0 ? (
						<div
							style={{
								height: `${rowVirtualizer.getTotalSize()}px`,
								width: "100%",
								position: "relative",
							}}
						>
							{rowVirtualizer.getVirtualItems().map((virtualRow) => {
								const item = filteredAndSortedItems[virtualRow.index];
								if (!item) return null;

								return (
									<div
										key={item.id}
										style={{
											position: "absolute",
											top: 0,
											left: 0,
											width: "100%",
											height: `${virtualRow.size}px`,
											transform: `translateY(${virtualRow.start}px)`,
										}}
									>
										<div className="overflow-x-auto custom-scrollbar">
											<Table>
												<TableBody>
													<VirtualTableRow
														item={item}
														onDelete={handleDelete}
														onNavigate={(path: string) =>
															navigate({ to: path } as any)
														}
													/>
												</TableBody>
											</Table>
										</div>
									</div>
								);
							})}
						</div>
					) : (
						<div className="h-[600px] flex items-center justify-center">
							<div className="flex flex-col items-center justify-center text-muted-foreground/30">
								<Terminal className="h-12 w-12 mb-4 opacity-10" />
								<p className="text-[10px] font-black uppercase tracking-[0.3em]">
									Registry Vacant
								</p>
							</div>
						</div>
					)}
				</div>
			</Card>

			{showCreateModal && (
				<div className="fixed inset-0 z-50 flex items-center justify-center">
					<div
						className="fixed inset-0 bg-black/50 backdrop-blur-sm"
						onClick={closeCreateModal}
					/>
					<div className="relative w-full max-w-lg rounded-xl border bg-background p-6 shadow-2xl">
						<div className="flex items-center justify-between">
							<h2 className="text-lg font-semibold">Create Node</h2>
							<button
								onClick={closeCreateModal}
								aria-label="Close dialog"
								className="rounded-lg p-1 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-primary"
							>
								<X className="h-5 w-5" />
							</button>
						</div>
						<div className="mt-4 space-y-4">
							<div>
								<label className="block text-sm font-medium">Title</label>
								<Input
									value={newTitle}
									onChange={(e) => setNewTitle(e.target.value)}
									placeholder="Enter node title"
									className="mt-1"
								/>
							</div>
							<div className="grid gap-4 sm:grid-cols-2">
								<div>
									<label className="block text-sm font-medium">Type</label>
									<Input
										value={newType}
										onChange={(e) => setNewType(e.target.value)}
										placeholder="feature, requirement, ui_component..."
										className="mt-1"
									/>
								</div>
								<div>
									<label className="block text-sm font-medium">Status</label>
									<Select
										value={newStatus}
										onValueChange={(v) => setNewStatus(v as ItemStatus)}
									>
										<SelectTrigger className="mt-1">
											<SelectValue placeholder="Status" />
										</SelectTrigger>
										<SelectContent>
											{[
												"todo",
												"in_progress",
												"done",
												"blocked",
												"cancelled",
											].map((s) => (
												<SelectItem key={s} value={s}>
													{s.replace("_", " ")}
												</SelectItem>
											))}
										</SelectContent>
									</Select>
								</div>
							</div>
							<div>
								<label className="block text-sm font-medium">Priority</label>
								<Select
									value={newPriority}
									onValueChange={(v) => setNewPriority(v as Priority)}
								>
									<SelectTrigger className="mt-1">
										<SelectValue placeholder="Priority" />
									</SelectTrigger>
									<SelectContent>
										{["low", "medium", "high", "critical"].map((p) => (
											<SelectItem key={p} value={p}>
												{p}
											</SelectItem>
										))}
									</SelectContent>
								</Select>
							</div>
							<div className="flex justify-end gap-2 pt-2">
								<Button variant="ghost" onClick={closeCreateModal}>
									Cancel
								</Button>
								<Button onClick={handleCreate} disabled={createItem.isPending}>
									{createItem.isPending ? "Creating..." : "Create Node"}
								</Button>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
