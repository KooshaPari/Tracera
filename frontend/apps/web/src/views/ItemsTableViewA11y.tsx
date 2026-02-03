/**
 * ItemsTableView with Comprehensive Accessibility (WCAG 2.1 Level AA)
 *
 * Accessibility Features:
 * - ARIA roles: table, rowgroup, row, gridcell, columnheader
 * - Keyboard navigation: Arrow keys, Home/End, Ctrl+Home/End, PageUp/Down
 * - Roving tabindex for efficient focus management
 * - Screen reader announcements for navigation and actions
 * - Proper heading hierarchy and semantic HTML
 * - Color contrast compliance
 * - Focus indicators with sufficient size and contrast
 * - ARIA sort indicators for sortable columns
 */

import { useNavigate, useSearch } from "@tanstack/react-router";
import { useVirtualizer } from "@tanstack/react-virtual";
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
	AlertCircle,
	ArrowDown,
	ArrowUp,
	CheckCircle2,
	Clock,
	ExternalLink,
	Filter,
	Plus,
	Search,
	Terminal,
	Trash2,
	X,
} from "lucide-react";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
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
import { useTableKeyboardNavigation } from "../hooks/useTableKeyboardNavigation";

function getStatusBadge(status: ItemStatus) {
	const config = {
		blocked: {
			color: "bg-red-500/10 text-red-600 border-red-500/20",
			icon: AlertCircle,
		},
		cancelled: {
			color: "bg-orange-500/10 text-orange-600 border-orange-500/20",
			icon: X,
		},
		done: {
			color: "bg-green-500/10 text-green-600 border-green-500/20",
			icon: CheckCircle2,
		},
		in_progress: {
			color: "bg-blue-500/10 text-blue-600 border-blue-500/20",
			icon: Clock,
		},
		todo: { color: "bg-muted text-muted-foreground", icon: Terminal },
	};
	const c = config[status] || config.todo;
	return (
		<Badge
			className={cn(
				"text-[9px] font-black uppercase tracking-tighter gap-1 border",
				c.color,
			)}
		>
			<c.icon className="h-2.5 w-2.5" aria-hidden="true" />
			{status.replace("_", " ")}
		</Badge>
	);
}

function getPriorityDot(priority?: Priority) {
	const colors = {
		critical: "bg-red-500",
		high: "bg-orange-500",
		low: "bg-green-500",
		medium: "bg-blue-500",
	};
	const labels = {
		critical: "Critical priority",
		high: "High priority",
		low: "Low priority",
		medium: "Medium priority",
	};
	const level = priority || "medium";
	return (
		<div
			className={cn("h-1.5 w-1.5 rounded-full", colors[level])}
			role="img"
			aria-label={labels[level]}
		/>
	);
}

// Memoized accessible row component
interface VirtualTableRowProps {
	item: any;
	rowIndex: number;
	onDelete: (id: string) => void;
	onNavigate: (item: any) => void;
	isKeyboardFocused: boolean;
}

const VirtualTableRow = memo(
	({
		item,
		rowIndex,
		onDelete,
		onNavigate,
		isKeyboardFocused,
	}: VirtualTableRowProps) => {
		const handleNavigate = useCallback(() => {
			onNavigate(item);
		}, [item, onNavigate]);

		const handleDelete = useCallback(() => {
			onDelete(item.id);
		}, [item.id, onDelete]);

		const handleKeyDown = useCallback(
			(e: React.KeyboardEvent) => {
				if (e.key === "Enter" || e.key === " ") {
					e.preventDefault();
					handleNavigate();
				}
			},
			[handleNavigate],
		);

		return (
			<TableRow
				data-row-index={rowIndex}
				aria-rowindex={rowIndex + 2} // +1 for header, +1 for 1-based indexing
				className={cn(
					"group border-b border-border/30 hover:bg-muted/30 transition-colors",
					isKeyboardFocused && "ring-2 ring-primary ring-offset-2",
				)}
			>
				<TableCell
					data-col-index="0"
					colIndex={1}
					headerText="Node Identifier"
					className="px-6 py-4"
				>
					<button
						onClick={handleNavigate}
						onKeyDown={handleKeyDown}
						className={cn(
							"block group/link w-full text-left focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
						)}
						tabIndex={isKeyboardFocused ? 0 : -1}
						aria-label={`Item ${item.title} (ID: ${item.id.slice(0, 12)})`}
					>
						<div className="font-bold text-sm group-hover/link:text-primary transition-colors truncate">
							{item.title}
						</div>
						<div className="text-[10px] font-mono text-muted-foreground uppercase mt-0.5">
							{item.id.slice(0, 12)}
						</div>
					</button>
				</TableCell>

				<TableCell
					data-col-index="1"
					colIndex={2}
					headerText="Type"
					className="px-4 py-4"
				>
					<Badge
						variant="outline"
						className="text-[8px] font-black uppercase tracking-tighter px-1.5 h-4"
					>
						{item.type}
					</Badge>
				</TableCell>

				<TableCell
					data-col-index="2"
					colIndex={3}
					headerText="Status"
					className="px-4 py-4"
					ariaLabel={`Status: ${item.status.replace("_", " ")}`}
				>
					{getStatusBadge(item.status)}
				</TableCell>

				<TableCell
					data-col-index="3"
					colIndex={4}
					headerText="Priority"
					className="px-4 py-4"
				>
					<div className="flex items-center gap-2">
						{getPriorityDot(item.priority)}
						<span className="text-[10px] font-bold uppercase text-muted-foreground">
							{item.priority || "medium"}
						</span>
					</div>
				</TableCell>

				<TableCell
					data-col-index="4"
					colIndex={5}
					headerText="Owner"
					className="px-4 py-4"
					ariaLabel={`Owner: ${item.owner || "Unassigned"}`}
				>
					<div className="flex items-center gap-2">
						<div
							className="h-5 w-5 rounded-full bg-muted flex items-center justify-center text-[8px] font-black uppercase"
							role="img"
							aria-label={`Avatar for ${item.owner}`}
						>
							{item.owner?.charAt(0) || "?"}
						</div>
						<span className="text-[10px] font-bold uppercase text-muted-foreground">
							{item.owner || "Unassigned"}
						</span>
					</div>
				</TableCell>

				<TableCell
					data-col-index="5"
					colIndex={6}
					headerText="Actions"
					className="text-right px-6 py-4"
				>
					<div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
						<Button
							variant="ghost"
							size="icon"
							className="h-8 w-8 rounded-lg focus:ring-2 focus:ring-primary focus:ring-offset-2"
							onClick={handleNavigate}
							aria-label={`Open item details for ${item.title}`}
							tabIndex={-1}
						>
							<ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
						</Button>
						<Button
							variant="ghost"
							size="icon"
							className="h-8 w-8 rounded-lg text-destructive hover:bg-destructive/10 focus:ring-2 focus:ring-primary focus:ring-offset-2"
							onClick={handleDelete}
							aria-label={`Delete item ${item.title}`}
							tabIndex={-1}
						>
							<Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
						</Button>
					</div>
				</TableCell>
			</TableRow>
		);
	},
	(prev, next) =>
		prev.item.id === next.item.id &&
		prev.item.title === next.item.title &&
		prev.item.type === next.item.type &&
		prev.item.status === next.item.status &&
		prev.item.priority === next.item.priority &&
		prev.item.owner === next.item.owner &&
		prev.isKeyboardFocused === next.isKeyboardFocused,
);

VirtualTableRow.displayName = "VirtualTableRow";

interface ItemsTableViewA11yProps {
	projectId?: string;
	view?: ViewType;
	type?: string;
}

export function ItemsTableViewA11y({
	projectId,
	view,
	type,
}: ItemsTableViewA11yProps = {}) {
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
	const [keyboardFocusedCell, setKeyboardFocusedCell] = useState<{
		row: number;
		col: number;
	} | null>(null);

	const parentRef = useRef<HTMLDivElement>(null);
	const tableContainerId = "items-table-a11y";

	const filteredAndSortedItems = useMemo(() => {
		const filtered = items.filter((i) => {
			const matchesType =
				!effectiveTypeFilter || i.type === effectiveTypeFilter;
			const matchesQuery =
				i.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				i.id.toLowerCase().includes(searchQuery.toLowerCase());
			return matchesType && matchesQuery;
		});

		return filtered.toSorted((a, b) => {
			const dir = sortOrder === "asc" ? 1 : -1;
			if (sortColumn === "title") {
				return a.title.localeCompare(b.title) * dir;
			}
			if (sortColumn === "created") {
				return (
					(new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()) *
					dir
				);
			}
			return 0;
		});
	}, [items, effectiveTypeFilter, searchQuery, sortColumn, sortOrder]);

	// Keyboard navigation
	const { focusState: _focusState, setFocusState: _setFocusState } =
		useTableKeyboardNavigation({
			colCount: 6,
			containerId: tableContainerId,
			onNavigate: (rowIndex, colIndex) => {
				setKeyboardFocusedCell({ col: colIndex, row: rowIndex });
			},
			rowCount: filteredAndSortedItems.length,
		});

	useEffect(() => {
		if (actionParam === "create") {
			setShowCreateModal(true);
		}
	}, [actionParam]);

	const closeCreateModal = useCallback(() => {}, [navigate]);

	const handleItemNavigate = useCallback(
		(item: any) => {},
		[navigate, effectiveProjectId, view],
	);

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
				priority: newPriority,
				projectId: effectiveProjectId,
				status: newStatus,
				title: newTitle.trim(),
				type: newType || (view as any) || "feature",
				view: (view as any) || "feature",
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

	const rowVirtualizer = useVirtualizer({
		count: filteredAndSortedItems.length,
		estimateSize: () => 68,
		getScrollElement: () => parentRef.current,
		overscan: 10,
	});

	const handleDelete = useCallback(
		async (id: string) => {
			try {
				await deleteItem.mutateAsync(id);
				toast.success("Node purged from registry");
				// Announce to screen readers
				announceToScreenReader("Item deleted successfully");
			} catch {
				toast.error("Purge failure");
				announceToScreenReader("Failed to delete item");
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
						Flat-file management of project entities and artifacts. Use arrow
						keys to navigate the table.
					</p>
				</div>
				<div className="flex items-center gap-2">
					<Button
						size="sm"
						onClick={() => {}}
						className="gap-2 rounded-xl shadow-lg shadow-primary/20"
						aria-label="Create new node"
					>
						<Plus className="h-4 w-4" aria-hidden="true" /> New Node
					</Button>
				</div>
			</div>

			{/* Filters Bar with ARIA labels */}
			<Card className="p-2 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-2">
				<div className="relative flex-1 min-w-[250px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search identifiers..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						aria-label="Search items by title or ID"
					/>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				{!projectId && (
					<Select value={projectFilter || "all"} onValueChange={(v) => {}}>
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
						onValueChange={(v) => {}}
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

			{/* Accessible Table with Virtual Scrolling */}
			<Card className="border-none bg-card/50 shadow-sm rounded-[2rem] overflow-hidden flex flex-col">
				<div
					id={tableContainerId}
					className="flex flex-col"
					role="region"
					aria-label="Items table with keyboard navigation support"
					aria-describedby="table-instructions"
				>
					{/* Instructions for screen readers */}
					<div id="table-instructions" className="sr-only">
						Use arrow keys to navigate. Home and End keys jump to the first and
						last columns. Ctrl+Home and Ctrl+End jump to the first and last
						rows. Enter or Space to activate items.
					</div>

					{/* Table Header */}
					<div className="overflow-x-auto custom-scrollbar">
						<Table role="table" ariaLabel="Items table with sortable columns">
							<TableHeader>
								<TableRow className="hover:bg-transparent border-b border-border/50">
									<TableHead
										className="w-[400px] h-14 px-6 text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
										colIndex={1}
										isSortable
										sortDirection={
											sortColumn === "title"
												? (sortOrder === "asc"
													? "ascending"
													: "descending")
												: "none"
										}
									>
										<button
											onClick={() => {
												setSortColumn("title");
												setSortOrder(sortOrder === "asc" ? "desc" : "asc");
											}}
											className="flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded px-2 py-1"
											aria-label={`Node Identifier, ${sortColumn === "title" ? `sorted ${sortOrder}` : "not sorted"}`}
										>
											Node Identifier
											{sortColumn === "title" &&
												(sortOrder === "asc" ? (
													<ArrowUp className="h-3 w-3" aria-hidden="true" />
												) : (
													<ArrowDown className="h-3 w-3" aria-hidden="true" />
												))}
										</button>
									</TableHead>
									<TableHead colIndex={2}>Type</TableHead>
									<TableHead colIndex={3}>Status</TableHead>
									<TableHead colIndex={4}>Priority</TableHead>
									<TableHead colIndex={5}>Owner</TableHead>
									<TableHead colIndex={6} className="text-right px-6">
										Actions
									</TableHead>
								</TableRow>
							</TableHeader>
						</Table>
					</div>

					{/* Virtual Scrolling Container */}
					<div
						ref={parentRef}
						className="h-[600px] overflow-y-auto overflow-x-hidden custom-scrollbar flex-1"
						role="region"
						aria-label="Items table body with virtual scrolling"
					>
						{filteredAndSortedItems.length > 0 ? (
							<div
								style={{
									height: `${rowVirtualizer.getTotalSize()}px`,
									position: "relative",
									width: "100%",
								}}
							>
								{rowVirtualizer.getVirtualItems().map((virtualRow) => {
									const item = filteredAndSortedItems[virtualRow.index];
									if (!item) {
										return null;
									}

									const isFocused =
										keyboardFocusedCell?.row === virtualRow.index;

									return (
										<div
											key={item.id}
											style={{
												height: `${virtualRow.size}px`,
												left: 0,
												position: "absolute",
												top: 0,
												transform: `translateY(${virtualRow.start}px)`,
												width: "100%",
											}}
										>
											<div className="overflow-x-auto custom-scrollbar">
												<Table>
													<TableBody>
														<VirtualTableRow
															item={item}
															rowIndex={virtualRow.index}
															onDelete={handleDelete}
															onNavigate={handleItemNavigate}
															isKeyboardFocused={isFocused}
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
				</div>
			</Card>

			{/* Accessible Create Modal */}
			{showCreateModal && (
				<div className="fixed inset-0 z-50 flex items-center justify-center">
					<div
						className="fixed inset-0 bg-black/50 backdrop-blur-sm"
						onClick={closeCreateModal}
						role="presentation"
					/>
					<div
						className="relative w-full max-w-lg rounded-xl border bg-background p-6 shadow-2xl"
						role="dialog"
						aria-modal="true"
						aria-labelledby="create-modal-title"
					>
						<div className="flex items-center justify-between">
							<h2 id="create-modal-title" className="text-lg font-semibold">
								Create Node
							</h2>
							<button
								onClick={closeCreateModal}
								aria-label="Close dialog"
								className="rounded-lg p-1 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-primary"
							>
								<X className="h-5 w-5" aria-hidden="true" />
							</button>
						</div>
						<div className="mt-4 space-y-4">
							<div>
								<label
									htmlFor="node-title"
									className="block text-sm font-medium"
								>
									Title
								</label>
								<Input
									id="node-title"
									value={newTitle}
									onChange={(e) => setNewTitle(e.target.value)}
									placeholder="Enter node title"
									className="mt-1"
									aria-required="true"
								/>
							</div>
							<div className="grid gap-4 sm:grid-cols-2">
								<div>
									<label
										htmlFor="node-type"
										className="block text-sm font-medium"
									>
										Type
									</label>
									<Input
										id="node-type"
										value={newType}
										onChange={(e) => setNewType(e.target.value)}
										placeholder="feature, requirement, ui_component..."
										className="mt-1"
									/>
								</div>
								<div>
									<label
										htmlFor="node-status"
										className="block text-sm font-medium"
									>
										Status
									</label>
									<Select
										value={newStatus}
										onValueChange={(v) => setNewStatus(v as ItemStatus)}
									>
										<SelectTrigger id="node-status" className="mt-1">
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
								<label
									htmlFor="node-priority"
									className="block text-sm font-medium"
								>
									Priority
								</label>
								<Select
									value={newPriority}
									onValueChange={(v) => setNewPriority(v as Priority)}
								>
									<SelectTrigger id="node-priority" className="mt-1">
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

			{/* Screen reader announcements */}
			<div
				id="table-announcements"
				role="status"
				aria-live="polite"
				aria-atomic="true"
				className="sr-only"
			/>
		</div>
	);
}

/**
 * Announce messages to screen readers using aria-live regions
 */
function announceToScreenReader(message: string) {
	const liveRegion = document.querySelector("#table-announcements");
	if (liveRegion) {
		liveRegion.textContent = message;
	}
}
