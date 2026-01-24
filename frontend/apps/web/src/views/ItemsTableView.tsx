import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import type { ItemStatus, Priority } from "@tracertm/types";
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
import { ArrowDown, ArrowUp, ArrowUpDown, X } from "lucide-react";
import { useMemo, useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { useDeleteItem, useItems, useUpdateItem } from "../hooks/useItems";
import { useProjects } from "../hooks/useProjects";

interface TableColumn {
	id: string;
	header: string;
	width?: string;
	sortable?: boolean;
}

const columns: TableColumn[] = [
	{ id: "select", header: "", width: "w-12" },
	{ id: "title", header: "Title", sortable: true },
	{ id: "type", header: "Type", width: "w-32", sortable: true },
	{ id: "status", header: "Status", width: "w-32", sortable: true },
	{ id: "priority", header: "Priority", width: "w-24", sortable: true },
	{ id: "owner", header: "Owner", width: "w-32", sortable: true },
	{ id: "created", header: "Created", width: "w-32", sortable: true },
	{ id: "actions", header: "", width: "w-24" },
];

function getStatusColor(status: ItemStatus): string {
	switch (status) {
		case "done":
			return "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20";
		case "in_progress":
			return "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20";
		case "blocked":
			return "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20";
		default:
			return "bg-muted text-muted-foreground";
	}
}

function getPriorityColor(priority?: Priority): string {
	switch (priority) {
		case "critical":
			return "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20";
		case "high":
			return "bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20";
		case "medium":
			return "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20";
		case "low":
			return "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20";
		default:
			return "bg-muted text-muted-foreground";
	}
}

interface BulkActionsBarProps {
	selectedCount: number;
	onClearSelection: () => void;
	onBulkDelete: () => void;
	onBulkStatusChange: (status: ItemStatus) => void;
}

function BulkActionsBar({
	selectedCount,
	onClearSelection,
	onBulkDelete,
	onBulkStatusChange,
}: BulkActionsBarProps) {
	return (
		<Card className="border-primary/20 bg-primary/5 p-4">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-4">
					<Badge variant="secondary" className="px-3 py-1">
						{selectedCount} item{selectedCount !== 1 ? "s" : ""} selected
					</Badge>
					<Button variant="ghost" size="sm" onClick={onClearSelection}>
						<X className="mr-2 h-4 w-4" />
						Clear
					</Button>
				</div>
				<div className="flex items-center gap-2">
					<Select
						onValueChange={(value) => onBulkStatusChange(value as ItemStatus)}
					>
						<SelectTrigger className="w-[180px]">
							<SelectValue placeholder="Change Status..." />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="todo">To Do</SelectItem>
							<SelectItem value="in_progress">In Progress</SelectItem>
							<SelectItem value="done">Done</SelectItem>
							<SelectItem value="blocked">Blocked</SelectItem>
						</SelectContent>
					</Select>
					<Button variant="destructive" size="sm" onClick={onBulkDelete}>
						Delete
					</Button>
				</div>
			</div>
		</Card>
	);
}

export function ItemsTableView() {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;
	const projectFilter = searchParams?.project || undefined;
	const typeFilter = searchParams?.type || undefined;
	const statusFilter = searchParams?.status || undefined;

	const updateSearchParams = (updates: Record<string, string | undefined>) => {
		navigate({
			search: (prev: any) => {
				const newSearch = { ...(prev || {}), ...updates };
				return newSearch as any;
			},
		} as any);
	};

	const {
		data: itemsData,
		isLoading,
		error,
	} = useItems({ projectId: projectFilter });
	// Extract items array from new hook structure
	const items = itemsData?.items || [];
	// Extract items array from new hook structure
	const _itemsArray = itemsData?.items || items || [];
	const { data: projects } = useProjects();
	// Ensure projects is always an array
	const projectsArray = Array.isArray(projects) ? projects : [];
	const updateItem = useUpdateItem();
	const deleteItem = useDeleteItem();

	const [searchQuery, setSearchQuery] = useState("");
	const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
	const [sortColumn, setSortColumn] = useState<string>("created");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
	const [currentPage, setCurrentPage] = useState(1);
	const pageSize = 20;

	// Filter and sort items
	const filteredAndSortedItems = useMemo(() => {
		if (!items) return [];

		const filtered = items.filter((item) => {
			if (typeFilter && item.type !== typeFilter) return false;
			if (statusFilter && item.status !== statusFilter) return false;
			if (searchQuery) {
				const query = searchQuery.toLowerCase();
				return (
					item.title.toLowerCase().includes(query) ||
					item.description?.toLowerCase().includes(query) ||
					item.type.toLowerCase().includes(query)
				);
			}
			return true;
		});

		filtered.sort((a, b) => {
			let comparison = 0;

			switch (sortColumn) {
				case "title":
					comparison = a.title.localeCompare(b.title);
					break;
				case "type":
					comparison = a.type.localeCompare(b.type);
					break;
				case "status":
					comparison = a.status.localeCompare(b.status);
					break;
				case "priority":
					comparison = (a.priority || "").localeCompare(b.priority || "");
					break;
				case "owner":
					comparison = (a.owner || "").localeCompare(b.owner || "");
					break;
				case "created": {
					const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0;
					const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0;
					comparison = dateA - dateB;
					break;
				}
			}

			return sortOrder === "asc" ? comparison : -comparison;
		});

		return filtered;
	}, [items, typeFilter, statusFilter, searchQuery, sortColumn, sortOrder]);

	// Pagination
	const totalPages = Math.ceil(filteredAndSortedItems.length / pageSize);
	const paginatedItems = filteredAndSortedItems.slice(
		(currentPage - 1) * pageSize,
		currentPage * pageSize,
	);

	const handleSort = (column: string) => {
		if (sortColumn === column) {
			setSortOrder(sortOrder === "asc" ? "desc" : "asc");
		} else {
			setSortColumn(column);
			setSortOrder("asc");
		}
	};

	const handleSelectAll = (checked: boolean) => {
		if (checked) {
			setSelectedItems(new Set(paginatedItems.map((item) => item.id)));
		} else {
			setSelectedItems(new Set());
		}
	};

	const handleSelectItem = (id: string, checked: boolean) => {
		const newSelection = new Set(selectedItems);
		if (checked) {
			newSelection.add(id);
		} else {
			newSelection.delete(id);
		}
		setSelectedItems(newSelection);
	};

	const handleBulkDelete = async () => {
		if (!confirm(`Delete ${selectedItems.size} items?`)) return;

		for (const id of selectedItems) {
			await deleteItem.mutateAsync(id);
		}
		setSelectedItems(new Set());
	};

	const handleBulkStatusChange = async (status: ItemStatus) => {
		if (!status) return;

		for (const id of selectedItems) {
			await updateItem.mutateAsync({ id, data: { status } });
		}
		setSelectedItems(new Set());
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

	const allSelected =
		paginatedItems.length > 0 &&
		paginatedItems.every((item) => selectedItems.has(item.id));

	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Items</h1>
					<p className="mt-2 text-muted-foreground">
						Manage all project items in table view
					</p>
				</div>
				<div className="flex items-center gap-2">
					<Link to="/items/kanban">
						<Button variant="outline" size="sm">
							Kanban View
						</Button>
					</Link>
					<Link to="/items/tree">
						<Button variant="outline" size="sm">
							Tree View
						</Button>
					</Link>
					<Link to={`/items?${searchParams}&action=create`}>
						<Button size="sm">+ New Item</Button>
					</Link>
				</div>
			</div>

			{/* Filters */}
			<Card className="p-4">
				<div className="grid grid-cols-1 gap-4 md:grid-cols-4">
					<Input
						type="search"
						placeholder="Search items..."
						value={searchQuery}
						onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
							setSearchQuery((e.currentTarget as HTMLInputElement).value)
						}
						className="w-full"
					/>
					{projects && (
						<Select
							value={projectFilter || "all"}
							onValueChange={(value) =>
								updateSearchParams({
									project: value === "all" ? undefined : value,
								})
							}
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
						onValueChange={(value) =>
							updateSearchParams({ type: value === "all" ? undefined : value })
						}
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
					<Select
						value={statusFilter || "all"}
						onValueChange={(value) =>
							updateSearchParams({
								status: value === "all" ? undefined : value,
							})
						}
					>
						<SelectTrigger>
							<SelectValue placeholder="All Statuses" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="all">All Statuses</SelectItem>
							<SelectItem value="todo">To Do</SelectItem>
							<SelectItem value="in_progress">In Progress</SelectItem>
							<SelectItem value="done">Done</SelectItem>
							<SelectItem value="blocked">Blocked</SelectItem>
						</SelectContent>
					</Select>
				</div>
			</Card>

			{/* Bulk Actions */}
			{selectedItems.size > 0 && (
				<BulkActionsBar
					selectedCount={selectedItems.size}
					onClearSelection={() => setSelectedItems(new Set())}
					onBulkDelete={handleBulkDelete}
					onBulkStatusChange={handleBulkStatusChange}
				/>
			)}

			{/* Table */}
			<Card>
				<div className="overflow-x-auto">
					<Table>
						<TableHeader>
							<TableRow>
								{columns.map((column) => (
									<TableHead
										key={column.id}
										className={cn(
											column.width,
											column.id === "select" && "w-12",
											column.id === "actions" && "w-24",
										)}
									>
										{column.id === "select" ? (
											<Checkbox
												checked={allSelected}
												onCheckedChange={handleSelectAll}
												aria-label="Select all"
											/>
										) : column.sortable ? (
											<button
												onClick={() => handleSort(column.id)}
												className="flex items-center gap-2 hover:text-foreground transition-colors"
											>
												{column.header}
												{sortColumn === column.id ? (
													sortOrder === "asc" ? (
														<ArrowUp className="h-4 w-4 text-foreground" />
													) : (
														<ArrowDown className="h-4 w-4 text-foreground" />
													)
												) : (
													<ArrowUpDown className="h-4 w-4 text-muted-foreground" />
												)}
											</button>
										) : (
											column.header
										)}
									</TableHead>
								))}
							</TableRow>
						</TableHeader>
						<TableBody>
							{paginatedItems.length === 0 ? (
								<TableRow>
									<TableCell
										colSpan={columns.length}
										className="h-24 text-center text-muted-foreground"
									>
										No items found
									</TableCell>
								</TableRow>
							) : (
								paginatedItems.map((item) => (
									<TableRow key={item.id}>
										<TableCell>
											<Checkbox
												checked={selectedItems.has(item.id)}
												onCheckedChange={(checked) =>
													handleSelectItem(item.id, checked as boolean)
												}
												aria-label={`Select ${item.title}`}
											/>
										</TableCell>
										<TableCell>
											<Link
												to={`/items/${item.id}`}
												className="font-medium hover:text-primary transition-colors"
											>
												{item.title}
											</Link>
										</TableCell>
										<TableCell>
											<Badge variant="secondary">{item.type}</Badge>
										</TableCell>
										<TableCell>
											<Badge
												variant="outline"
												className={cn(
													"capitalize",
													getStatusColor(item.status),
												)}
											>
												{item.status.replace("_", " ")}
											</Badge>
										</TableCell>
										<TableCell>
											{item.priority && (
												<Badge
													variant="outline"
													className={cn(
														"capitalize",
														getPriorityColor(item.priority),
													)}
												>
													{item.priority}
												</Badge>
											)}
										</TableCell>
										<TableCell className="text-muted-foreground">
											{item.owner || "-"}
										</TableCell>
										<TableCell className="text-muted-foreground">
											{item.createdAt
												? new Date(item.createdAt).toLocaleDateString()
												: "N/A"}
										</TableCell>
										<TableCell>
											<Link to={`/items/${item.id}`}>
												<Button variant="ghost" size="sm">
													View
												</Button>
											</Link>
										</TableCell>
									</TableRow>
								))
							)}
						</TableBody>
					</Table>
				</div>

				{/* Pagination */}
				{totalPages > 1 && (
					<div className="flex flex-col gap-4 border-t px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
						<div className="text-sm text-muted-foreground">
							Showing {(currentPage - 1) * pageSize + 1} to{" "}
							{Math.min(currentPage * pageSize, filteredAndSortedItems.length)}{" "}
							of {filteredAndSortedItems.length} items
						</div>
						<div className="flex items-center gap-2">
							<Button
								variant="outline"
								size="sm"
								onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
								disabled={currentPage === 1}
							>
								Previous
							</Button>
							<span className="text-sm text-muted-foreground">
								Page {currentPage} of {totalPages}
							</span>
							<Button
								variant="outline"
								size="sm"
								onClick={() =>
									setCurrentPage((p) => Math.min(totalPages, p + 1))
								}
								disabled={currentPage === totalPages}
							>
								Next
							</Button>
						</div>
					</div>
				)}
			</Card>
		</div>
	);
}
