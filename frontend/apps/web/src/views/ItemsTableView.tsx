import { useLocation, useNavigate, useSearch } from "@tanstack/react-router";
import { useVirtualizer } from "@tanstack/react-virtual";
import type { ItemStatus, Priority, ViewType } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
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
	Loader,
	MoreVertical,
	Plus,
	Search,
	Terminal,
	Trash2,
	X,
} from "lucide-react";
import {
	forwardRef,
	memo,
	useCallback,
	useEffect,
	useImperativeHandle,
	useMemo,
	useRef,
	useState,
} from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/ui/empty-state";
import { ListLoadingSkeleton } from "@/lib/lazy-loading";
import { ResponsiveCardView } from "@/components/mobile";
import type { CardItem } from "@/components/mobile";
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
			data-testid="status-badge"
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
		low: "bg-green-500",
		medium: "bg-blue-500",
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
	onNavigate: (item: any) => void;
	rowIndex: number;
	onCellKeyDown?: (event: React.KeyboardEvent<HTMLElement>) => void;
	isVisible?: boolean;
}

const VirtualTableRow = memo(
	({
		item,
		onDelete,
		onNavigate,
		rowIndex,
		onCellKeyDown,
	}: VirtualTableRowProps) => {
		const handleNavigate = useCallback(() => {
			onNavigate(item);
		}, [item, onNavigate]);

		const handleDelete = useCallback(() => {
			onDelete(item.id);
		}, [item.id, onDelete]);

		return (
			<TableRow
				role="row"
				rowIndex={rowIndex + 1}
				data-testid="item-card"
				className="group border-b border-border/30 hover:bg-muted/30 active:bg-muted/40 transition-all duration-200 ease-out"
			>
				<TableCell
					role="gridcell"
					tabIndex={0}
					data-testid="item-card"
					data-row-index={rowIndex}
					data-col-index={0}
					className="px-6 py-4 focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none"
					onKeyDown={onCellKeyDown}
				>
					<button
						data-testid="item-card"
						onClick={handleNavigate}
						className="block group/link w-full text-left"
					>
						<div
							data-testid="item-title"
							className="font-bold text-sm group-hover/link:text-primary transition-colors truncate"
						>
							{item.title}
						</div>
						<div className="text-[10px] font-mono text-muted-foreground uppercase mt-0.5">
							{item.id.slice(0, 12)}
						</div>
					</button>
				</TableCell>
				<TableCell
					role="gridcell"
					tabIndex={0}
					data-row-index={rowIndex}
					data-col-index={1}
					headerText="Type"
					className="focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none"
					onKeyDown={onCellKeyDown}
				>
					<Badge
						variant="outline"
						className="text-[8px] font-black uppercase tracking-tighter px-1.5 h-4"
					>
						{item.type}
					</Badge>
				</TableCell>
				<TableCell
					role="gridcell"
					tabIndex={0}
					data-row-index={rowIndex}
					data-col-index={2}
					headerText="Status"
					className="focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none"
					onKeyDown={onCellKeyDown}
				>
					{getStatusBadge(item.status)}
				</TableCell>
				<TableCell
					role="gridcell"
					tabIndex={0}
					data-row-index={rowIndex}
					data-col-index={3}
					headerText="Priority"
					className="focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none"
					onKeyDown={onCellKeyDown}
				>
					<div className="flex items-center gap-2">
						{getPriorityDot(item.priority)}
						<span className="text-[10px] font-bold uppercase text-muted-foreground">
							{item.priority || "medium"}
						</span>
					</div>
				</TableCell>
				<TableCell
					role="gridcell"
					tabIndex={0}
					data-row-index={rowIndex}
					data-col-index={4}
					headerText="Owner"
					className="focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none"
					onKeyDown={onCellKeyDown}
				>
					<div className="flex items-center gap-2">
						<div className="h-5 w-5 rounded-full bg-muted flex items-center justify-center text-[8px] font-black uppercase">
							{item.owner?.charAt(0) || "?"}
						</div>
						<span className="text-[10px] font-bold uppercase text-muted-foreground">
							{item.owner || "Unassigned"}
						</span>
					</div>
				</TableCell>
				<TableCell
					role="gridcell"
					tabIndex={0}
					data-row-index={rowIndex}
					data-col-index={5}
					headerText="Actions"
					className="text-right px-6 focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none"
					onKeyDown={onCellKeyDown}
				>
					<div className="flex justify-end gap-1">
						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<span>
									<Button
										variant="ghost"
										size="icon"
										className="h-8 w-8 rounded-lg"
										data-testid="item-menu"
										aria-label={`Open item actions for ${item.title}`}
									>
										<MoreVertical className="h-3.5 w-3.5" />
									</Button>
								</span>
							</DropdownMenuTrigger>
							<DropdownMenuContent align="end">
								<DropdownMenuItem onClick={handleNavigate}>
									View
								</DropdownMenuItem>
								<DropdownMenuItem onClick={handleDelete}>
									Delete
								</DropdownMenuItem>
							</DropdownMenuContent>
						</DropdownMenu>
						<Button
							variant="ghost"
							size="icon"
							className="h-8 w-8 rounded-lg"
							onClick={handleNavigate}
							aria-label={`Open item ${item.title}`}
						>
							<ExternalLink className="h-3.5 w-3.5" />
						</Button>
						<Button
							variant="ghost"
							size="icon"
							className="h-8 w-8 rounded-lg text-destructive hover:bg-destructive/10"
							onClick={handleDelete}
							aria-label={`Delete item ${item.title}`}
						>
							<Trash2 className="h-3.5 w-3.5" />
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
		prev.rowIndex === next.rowIndex &&
		prev.isVisible === next.isVisible,
);

/** View-specific titles and empty-state copy for list/table views */
const VIEW_LABELS: Record<
	string,
	{
		title: string;
		description: string;
		emptyTitle: string;
		emptyDescription: string;
		createModalTitle?: string;
		createButtonLabel?: string;
		newButtonLabel?: string;
	}
> = {
	api: {
		createButtonLabel: "Create Endpoint",
		createModalTitle: "Create API Endpoint",
		description: "REST API contracts and specifications",
		emptyDescription: "Add an endpoint or schema to document your API.",
		emptyTitle: "No API endpoints yet",
		newButtonLabel: "New Endpoint",
		title: "API Endpoints",
	},
	architecture: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Architecture Item",
		description: "Architecture decisions and components",
		emptyDescription: "Add an architecture artifact to get started.",
		emptyTitle: "No architecture items yet",
		newButtonLabel: "New Item",
		title: "Architecture",
	},
	code: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Code Item",
		description: "Code and component traceability",
		emptyDescription: "Add modules, files, or functions to trace.",
		emptyTitle: "No code items yet",
		newButtonLabel: "New Item",
		title: "Code",
	},
	configuration: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Configuration Item",
		description: "Configuration and settings",
		emptyDescription: "Add configuration artifacts.",
		emptyTitle: "No configuration items yet",
		newButtonLabel: "New Item",
		title: "Configuration",
	},
	database: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Database Item",
		description: "Schema and table-level artifacts",
		emptyDescription: "Add tables or schema artifacts to trace.",
		emptyTitle: "No database items yet",
		newButtonLabel: "New Item",
		title: "Database",
	},
	dataflow: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Dataflow",
		description: "Data flows and pipelines",
		emptyDescription: "Add a data flow or pipeline to get started.",
		emptyTitle: "No dataflow items yet",
		newButtonLabel: "New Item",
		title: "Dataflow",
	},
	dependency: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Item",
		description: "Dependency and relationship view",
		emptyDescription: "Add items and links to see dependencies.",
		emptyTitle: "No dependencies yet",
		newButtonLabel: "New Item",
		title: "Dependencies",
	},
	domain: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Domain Item",
		description: "Domain model and concepts",
		emptyDescription: "Add entities or concepts to build your domain model.",
		emptyTitle: "No domain items yet",
		newButtonLabel: "New Item",
		title: "Domain",
	},
	feature: {
		createButtonLabel: "Create Feature",
		createModalTitle: "Create Feature",
		description: "Manage feature requirements and user stories",
		emptyDescription: "Create your first feature or epic to get started.",
		emptyTitle: "No features yet",
		newButtonLabel: "New Feature",
		title: "Features",
	},
	infrastructure: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Infrastructure Item",
		description: "Infrastructure and deployment",
		emptyDescription: "Add infrastructure or deployment artifacts.",
		emptyTitle: "No infrastructure items yet",
		newButtonLabel: "New Item",
		title: "Infrastructure",
	},
	journey: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Journey",
		description: "User journeys and flows",
		emptyDescription: "Add a user journey or flow to get started.",
		emptyTitle: "No journey items yet",
		newButtonLabel: "New Journey",
		title: "Journey",
	},
	monitoring: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Monitoring Item",
		description: "Monitoring and observability",
		emptyDescription: "Add monitoring or observability artifacts.",
		emptyTitle: "No monitoring items yet",
		newButtonLabel: "New Item",
		title: "Monitoring",
	},
	performance: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Performance Item",
		description: "Performance requirements and metrics",
		emptyDescription: "Add performance requirements or metrics.",
		emptyTitle: "No performance items yet",
		newButtonLabel: "New Item",
		title: "Performance",
	},
	security: {
		createButtonLabel: "Create Item",
		createModalTitle: "Create Security Item",
		description: "Security requirements and controls",
		emptyDescription: "Add security requirements or controls.",
		emptyTitle: "No security items yet",
		newButtonLabel: "New Item",
		title: "Security",
	},
	test: {
		createButtonLabel: "Create Test",
		createModalTitle: "Create Test",
		description: "Test cases and scenarios",
		emptyDescription: "Create a test case or scenario to get started.",
		emptyTitle: "No tests yet",
		newButtonLabel: "New Test",
		title: "Tests",
	},
	wireframe: {
		createButtonLabel: "Create Wireframe",
		createModalTitle: "Create Wireframe",
		description: "UI wireframes and mockups",
		emptyDescription: "Add a wireframe to get started.",
		emptyTitle: "No wireframes yet",
		newButtonLabel: "New Wireframe",
		title: "Wireframes",
	},
};

function getViewLabels(view?: ViewType | string) {
	const key = typeof view === "string" ? view.toLowerCase() : "";
	return (
		VIEW_LABELS[key] ?? {
			createButtonLabel: "Create Item",
			createModalTitle: "Create Item",
			description: "Manage project items and artifacts in a unified registry.",
			emptyDescription: "Create your first item to get started.",
			emptyTitle: "No items yet",
			newButtonLabel: "New Item",
			title: "Item Registry",
		}
	);
}

interface ItemsTableViewProps {
	projectId?: string;
	view?: ViewType;
	type?: string;
}

interface VirtualTableHandle {
	scrollToItem: (index: number, behavior?: "smooth" | "auto") => void;
	getVisibleRange: () => { start: number; end: number } | null;
	getScrollPercentage: () => number;
}

// Forwardable virtual table container
const VirtualTableContainer = forwardRef<VirtualTableHandle, any>(
	(
		{
			parentRef,
			filteredAndSortedItems,
			rowVirtualizer,
			onDelete,
			onNavigate,
			onCellKeyDown,
			emptyState,
		},
		ref,
	) => {
		// Expose methods to parent component
		useImperativeHandle(
			ref,
			() => ({
				getScrollPercentage: () => {
					const element = parentRef.current;
					if (!element) {
						return 0;
					}
					const scrollHeight = element.scrollHeight - element.clientHeight;
					return scrollHeight > 0 ? element.scrollTop / scrollHeight : 0;
				},
				getVisibleRange: () => {
					const items = rowVirtualizer.getVirtualItems();
					return items.length > 0
						? {
								end: items.at(-1)?.index ?? 0,
								start: items[0]?.index ?? 0,
							}
						: null;
				},
				scrollToItem: (index: number, behavior: "smooth" | "auto" = "auto") => {
					if (parentRef.current && index >= 0) {
						rowVirtualizer.scrollToIndex(index, { align: "center", behavior });
					}
				},
			}),
			[rowVirtualizer, parentRef],
		);

		return (
			<div
				ref={parentRef}
				className="h-[600px] overflow-y-auto overflow-x-hidden custom-scrollbar flex-1"
				role="region"
				aria-label="Table content with virtual scrolling"
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
									data-item-id={item.id}
									data-index={virtualRow.index}
								>
									<div className="overflow-x-auto custom-scrollbar">
										<Table
											role="table"
											ariaLabel="Items table"
											ariaDescribedBy="table-instructions"
										>
											<TableBody>
												<VirtualTableRow
													item={item}
													onDelete={onDelete}
													onNavigate={onNavigate}
													rowIndex={virtualRow.index}
													onCellKeyDown={onCellKeyDown}
													isVisible
												/>
											</TableBody>
										</Table>
									</div>
								</div>
							);
						})}
					</div>
				) : (
					<div className="h-[600px] flex items-center justify-center p-6">
						{emptyState ?? (
							<div className="flex flex-col items-center justify-center text-muted-foreground/30">
								<Terminal className="h-12 w-12 mb-4 opacity-10" />
								<p className="text-[10px] font-black uppercase tracking-[0.3em]">
									No items yet
								</p>
							</div>
						)}
					</div>
				)}
			</div>
		);
	},
);

VirtualTableContainer.displayName = "VirtualTableContainer";

export function ItemsTableView({
	projectId,
	view,
	type,
}: ItemsTableViewProps = {}) {
	const navigate = useNavigate();
	const location = useLocation();
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
	const [newDescription, setNewDescription] = useState("");
	const [newType, setNewType] = useState(type || "feature");
	const [newPriority, setNewPriority] = useState<Priority>("medium");
	const [newStatus, setNewStatus] = useState<ItemStatus>("todo");
	const [formError, setFormError] = useState<string | null>(null);

	const [searchQuery, setSearchQuery] = useState("");
	const [sortColumn, setSortColumn] = useState<string>("created");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
	const [showLoadingState, setShowLoadingState] = useState(false);
	const [liveMessage, setLiveMessage] = useState("Items loaded.");
	const lastFocusedRef = useRef<HTMLElement | null>(null);
	const titleInputRef = useRef<HTMLInputElement | null>(null);
	const modalRef = useRef<HTMLDivElement | null>(null);
	const hasTabbedInModalRef = useRef(false);

	// Virtual scroll container ref and handle ref
	const parentRef = useRef<HTMLDivElement>(null);
	const virtualTableRef = useRef<VirtualTableHandle>(null);

	useEffect(() => {
		if (actionParam === "create") {
			setShowCreateModal(true);
		}
	}, [actionParam]);

	const closeCreateModal = useCallback(() => {}, [navigate]);

	const handleItemNavigate = useCallback(
		(item: any) => {},
		[navigate, effectiveProjectId, view, location.pathname],
	);

	const handleCreate = useCallback(async () => {
		if (!effectiveProjectId) {
			toast.error("Select a project before creating a node.");
			setFormError("Select a project before creating a node.");
			return;
		}
		if (!newTitle.trim()) {
			toast.error("Title is required.");
			setFormError("Title is required.");
			return;
		}
		try {
			await createItem.mutateAsync({
				description: newDescription.trim() || undefined,
				priority: newPriority,
				projectId: effectiveProjectId,
				status: newStatus,
				title: newTitle.trim(),
				type: newType || (view as any) || "feature",
				view: (view as any) || "feature",
			});
			toast.success("Node created");
			setLiveMessage("Item created.");
			setNewTitle("");
			setNewDescription("");
			setNewType(type || "feature");
			closeCreateModal();
		} catch {
			toast.error("Failed to create node");
			setFormError("Failed to create node.");
		}
	}, [
		effectiveProjectId,
		newTitle,
		newDescription,
		newType,
		newStatus,
		newPriority,
		view,
		type,
		createItem,
		closeCreateModal,
	]);

	const handleRefresh = useCallback(() => {
		setShowLoadingState(true);
		setLiveMessage("Loading items...");
		globalThis.setTimeout(() => {
			setShowLoadingState(false);
			setLiveMessage("Items loaded.");
		}, 250);
	}, []);

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

	// Virtual scroll setup with dynamic row heights
	const rowVirtualizer = useVirtualizer({
		count: filteredAndSortedItems.length,
		getScrollElement: () => parentRef.current,
		estimateSize: () => 68, // Base row height (TableRow with padding)
		overscan: 15, // Render 15 extra rows outside viewport for smoother scrolling
		measureElement:
			typeof globalThis.window !== "undefined" &&
			navigator.userAgent.indexOf("Firefox") === -1
				? (element) => element?.getBoundingClientRect().height
				: undefined,
	});

	// Measure rendering performance
	useEffect(() => {
		const handleLoadingComplete = () => {
			setShowLoadingState(false);
		};

		if (!isLoading && filteredAndSortedItems.length > 0) {
			// Small delay to ensure DOM is ready
			const timer = setTimeout(handleLoadingComplete, 100);
			return () => clearTimeout(timer);
		}
	}, [isLoading, filteredAndSortedItems.length]);

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

	// Handle sort changes - reset scroll position for better UX
	const handleSortChange = useCallback((column: string) => {
		setSortColumn(column);
		setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
		// Reset to top when sorting
		if (virtualTableRef.current) {
			virtualTableRef.current.scrollToItem(0, "auto");
		}
	}, []);

	const handleCellKeyDown = useCallback(
		(event: React.KeyboardEvent<HTMLElement>) => {
			if (event.target !== event.currentTarget) {
				return;
			}
			const target = event.currentTarget as HTMLElement;
			const rowAttr = target.getAttribute("data-row-index");
			const colAttr = target.getAttribute("data-col-index");
			if (rowAttr == null || colAttr == null) {
				return;
			}

			const rowIndex = Number.parseInt(rowAttr, 10);
			const colIndex = Number.parseInt(colAttr, 10);
			const maxRow = Math.max(filteredAndSortedItems.length - 1, 0);
			const maxCol = 5;
			let nextRow = rowIndex;
			let nextCol = colIndex;

			switch (event.key) {
				case "Enter":
				case " ": {
					event.preventDefault();
					const item = filteredAndSortedItems[rowIndex];
					if (item) {
						handleItemNavigate(item);
					}
					return;
				}
				case "ArrowRight": {
					nextCol = Math.min(maxCol, colIndex + 1);
					break;
				}
				case "ArrowLeft": {
					nextCol = Math.max(0, colIndex - 1);
					break;
				}
				case "ArrowDown": {
					nextRow = Math.min(maxRow, rowIndex + 1);
					break;
				}
				case "ArrowUp": {
					nextRow = Math.max(0, rowIndex - 1);
					break;
				}
				case "Home": {
					nextCol = 0;
					if (event.ctrlKey) {
						nextRow = 0;
					}
					break;
				}
				case "End": {
					nextCol = maxCol;
					if (event.ctrlKey) {
						nextRow = maxRow;
					}
					break;
				}
				case "PageDown": {
					nextRow = Math.min(maxRow, rowIndex + 5);
					break;
				}
				case "PageUp": {
					nextRow = Math.max(0, rowIndex - 5);
					break;
				}
				default: {
					return;
				}
			}

			event.preventDefault();
			const selector = `[data-row-index="${nextRow}"][data-col-index="${nextCol}"]`;
			const next = document.querySelector(selector) as HTMLElement | null;
			if (next) {
				next.focus();
			}
		},
		[filteredAndSortedItems, handleItemNavigate],
	);

	useEffect(() => {
		if (!showCreateModal) {
			return;
		}
		lastFocusedRef.current = document.activeElement as HTMLElement | null;
		hasTabbedInModalRef.current = false;
		const timer = globalThis.setTimeout(() => {
			titleInputRef.current?.focus();
		}, 0);

		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === "Escape") {
				event.preventDefault();
				closeCreateModal();
				return;
			}
			if (event.key !== "Tab") {
				return;
			}
			if (
				document.activeElement === titleInputRef.current &&
				!hasTabbedInModalRef.current
			) {
				event.preventDefault();
				hasTabbedInModalRef.current = true;
				return;
			}
			const modal = modalRef.current;
			if (!modal) {
				return;
			}
			const focusable = [
				...modal.querySelectorAll<HTMLElement>(
					[
						"button",
						"input",
						"textarea",
						"select",
						"[tabindex]:not([tabindex='-1'])",
					].join(","),
				),
			].filter((el) => !el.hasAttribute("disabled") && el.tabIndex !== -1);
			if (focusable.length === 0) {
				return;
			}
			const first = focusable[0];
			const last = focusable.at(-1);
			const active = document.activeElement as HTMLElement | null;
			if (!active || !modal.contains(active)) {
				event.preventDefault();
				first.focus();
				if (first === titleInputRef.current) {
					hasTabbedInModalRef.current = true;
				}
				return;
			}
			if (event.shiftKey && document.activeElement === first) {
				event.preventDefault();
				last.focus();
				return;
			}
			if (!event.shiftKey && document.activeElement === last) {
				event.preventDefault();
				first.focus();
			}
		};
		globalThis.addEventListener("keydown", handleKeyDown);

		return () => {
			globalThis.clearTimeout(timer);
			globalThis.removeEventListener("keydown", handleKeyDown);
		};
	}, [showCreateModal, closeCreateModal]);

	if (isLoading || showLoadingState) {
		const labels = getViewLabels(view);
		return (
			<ListLoadingSkeleton
				message={liveMessage || `Loading ${labels.title.toLowerCase()}...`}
				rowCount={6}
				dataTestId="items-live-region"
			/>
		);
	}

	const labels = getViewLabels(view);
	const emptyStateNode = (
		<EmptyState
			icon={Terminal}
			title={labels.emptyTitle}
			description={labels.emptyDescription}
			actions={[
				{
					label: labels.newButtonLabel ?? "New Item",
					onClick: () => {},
				},
			]}
			variant="compact"
		/>
	);

	// Build card items for mobile view
	const cardItems: CardItem[] = filteredAndSortedItems.map((item) => ({
		actions: (
			<div className="flex items-center gap-2 w-full">
				<Button
					variant="ghost"
					size="sm"
					className="h-8 w-8 rounded-lg flex-1 min-h-[40px]"
					onClick={() => handleItemNavigate(item)}
					aria-label={`Open item ${item.title}`}
				>
					<ExternalLink className="h-3.5 w-3.5" />
					<span className="sr-only">View</span>
				</Button>
				<Button
					variant="ghost"
					size="sm"
					className="h-8 w-8 rounded-lg text-destructive hover:bg-destructive/10 flex-1 min-h-[40px]"
					onClick={() => handleDelete(item.id)}
					aria-label={`Delete item ${item.title}`}
				>
					<Trash2 className="h-3.5 w-3.5" />
					<span className="sr-only">Delete</span>
				</Button>
			</div>
		),
		badge: (
			<Badge
				variant="outline"
				className="text-[8px] font-black uppercase tracking-tighter px-1.5 h-5"
			>
				{item.type}
			</Badge>
		),
		id: item.id,
		onClick: () => handleItemNavigate(item),
		owner: (
			<div className="flex items-center gap-2">
				<div className="h-5 w-5 rounded-full bg-muted flex items-center justify-center text-[8px] font-black uppercase">
					{item.owner?.charAt(0) || "?"}
				</div>
				<span className="text-[10px] font-bold uppercase text-muted-foreground">
					{item.owner || "Unassigned"}
				</span>
			</div>
		),
		priority: (
			<div className="flex items-center gap-1">
				{getPriorityDot(item.priority)}
				<span className="text-[10px] font-bold uppercase text-muted-foreground">
					{item.priority || "medium"}
				</span>
			</div>
		),
		status: getStatusBadge(item.status),
		subtitle: item.id.slice(0, 12),
		title: item.title,
	}));

	return (
		<div className="px-4 sm:px-6 py-6 sm:py-8 space-y-6 sm:space-y-8 max-w-[1600px] mx-auto animate-in-fade-up pb-20">
			<div
				role="status"
				aria-live="polite"
				aria-atomic="true"
				data-testid="items-live-region"
				className="text-xs text-muted-foreground"
			>
				{liveMessage}
			</div>
			<div id="table-instructions" className="sr-only">
				Use arrow keys to move between cells. Press Home and End to jump to
				first or last column. PageUp and PageDown move several rows.
			</div>
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						{labels.title}
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						{labels.description}
					</p>
				</div>
				<div className="flex items-center gap-2">
					<Button
						variant="outline"
						size="sm"
						onClick={handleRefresh}
						className="gap-2 rounded-xl"
					>
						Refresh
					</Button>
					<Button
						size="sm"
						onClick={() => {}}
						aria-label={labels.newButtonLabel ?? "Create new item"}
						className="gap-2 rounded-xl shadow-lg shadow-primary/20 min-h-[44px]"
					>
						<Plus className="h-4 w-4" /> {labels.newButtonLabel ?? "New Item"}
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
						aria-label="Search items by title or ID"
					/>
					<Button
						variant="ghost"
						size="icon"
						aria-label="Search items"
						className="absolute right-2 top-1/2 h-8 w-8 -translate-y-1/2"
					>
						<Search className="h-4 w-4" />
					</Button>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				<div className="text-[10px] text-muted-foreground/60 px-2 hidden lg:block">
					Showing {filteredAndSortedItems.length} of {items.length} items
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				<Button
					variant="ghost"
					size="sm"
					aria-label="Filter items"
					className="h-10 px-3"
				>
					<Filter className="h-4 w-4" />
				</Button>
				{!projectId && (
					<Select value={projectFilter || "all"} onValueChange={(v) => {}}>
						<SelectTrigger
							role="button"
							className="w-[180px] h-10 border-none bg-transparent hover:bg-background/50 transition-colors"
						>
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
						<SelectTrigger
							role="button"
							className="w-[140px] h-10 border-none bg-transparent hover:bg-background/50 transition-colors"
						>
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

			{/* Mobile Card View */}
			<div className="md:hidden">
				<ResponsiveCardView
					items={cardItems}
					isLoading={false}
					emptyState={emptyStateNode}
				/>
			</div>

			{/* Desktop Table View */}
			<div className="hidden md:block">
				<Card className="border-none bg-card/50 shadow-sm rounded-[2rem] overflow-hidden flex flex-col">
					{filteredAndSortedItems.length === 0 ? (
						<div className="flex min-h-[400px] items-center justify-center p-6">
							{emptyStateNode}
						</div>
					) : (filteredAndSortedItems.length <= 200 ? (
						<div className="overflow-x-auto custom-scrollbar">
							<Table
								role="table"
								ariaLabel="Items table"
								ariaDescribedBy="table-instructions"
							>
								<TableHeader>
									<TableRow
										role="row"
										className="hover:bg-transparent border-b border-border/50"
									>
										<TableHead
											colIndex={1}
											sortDirection={
												sortColumn === "title"
													? (sortOrder === "asc"
														? "ascending"
														: "descending")
													: "none"
											}
											className="w-[400px] h-14 px-6 text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
										>
											<button
												onClick={() => handleSortChange("title")}
												className="flex items-center gap-2 hover:text-primary transition-colors"
												aria-label={`Node Identifier ${sortColumn === "title" ? `sorted ${sortOrder}` : "not sorted"}`}
											>
												Node Identifier <span className="sr-only">Title</span>
												{sortColumn === "title" &&
													(sortOrder === "asc" ? (
														<ArrowUp className="h-3 w-3" />
													) : (
														<ArrowDown className="h-3 w-3" />
													))}
											</button>
										</TableHead>
										<TableHead
											colIndex={2}
											className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
										>
											Type
										</TableHead>
										<TableHead
											colIndex={3}
											className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
										>
											Status
										</TableHead>
										<TableHead
											colIndex={4}
											className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
										>
											Priority
										</TableHead>
										<TableHead
											colIndex={5}
											className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
										>
											Owner
										</TableHead>
										<TableHead
											colIndex={6}
											className="text-right px-6 text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
										>
											Actions
										</TableHead>
									</TableRow>
								</TableHeader>
								<TableBody>
									{filteredAndSortedItems.map((item, index) => (
										<VirtualTableRow
											key={item.id}
											item={item}
											onDelete={handleDelete}
											onNavigate={handleItemNavigate}
											rowIndex={index}
											onCellKeyDown={handleCellKeyDown}
										/>
									))}
								</TableBody>
							</Table>
						</div>
					) : (
						<>
							<div className="overflow-x-auto custom-scrollbar">
								<Table
									role="table"
									ariaLabel="Items table"
									ariaDescribedBy="table-instructions"
								>
									<TableHeader>
										<TableRow
											role="row"
											className="hover:bg-transparent border-b border-border/50"
										>
											<TableHead
												colIndex={1}
												sortDirection={
													sortColumn === "title"
														? (sortOrder === "asc"
															? "ascending"
															: "descending")
														: "none"
												}
												className="w-[400px] h-14 px-6 text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
											>
												<button
													onClick={() => handleSortChange("title")}
													className="flex items-center gap-2 hover:text-primary transition-colors"
													aria-label={`Node Identifier ${sortColumn === "title" ? `sorted ${sortOrder}` : "not sorted"}`}
												>
													Node Identifier <span className="sr-only">Title</span>
													{sortColumn === "title" &&
														(sortOrder === "asc" ? (
															<ArrowUp className="h-3 w-3" />
														) : (
															<ArrowDown className="h-3 w-3" />
														))}
												</button>
											</TableHead>
											<TableHead
												colIndex={2}
												className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
											>
												Type
											</TableHead>
											<TableHead
												colIndex={3}
												className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
											>
												Status
											</TableHead>
											<TableHead
												colIndex={4}
												className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
											>
												Priority
											</TableHead>
											<TableHead
												colIndex={5}
												className="text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
											>
												Owner
											</TableHead>
											<TableHead
												colIndex={6}
												className="text-right px-6 text-[10px] font-black uppercase tracking-widest sticky top-0 bg-card/50 z-10"
											>
												Actions
											</TableHead>
										</TableRow>
									</TableHeader>
								</Table>
							</div>
							<VirtualTableContainer
								ref={virtualTableRef}
								parentRef={parentRef}
								filteredAndSortedItems={filteredAndSortedItems}
								rowVirtualizer={rowVirtualizer}
								onDelete={handleDelete}
								onNavigate={handleItemNavigate}
								onCellKeyDown={handleCellKeyDown}
								emptyState={emptyStateNode}
							/>
						</>
					))}
				</Card>
			</div>

			{showCreateModal && (
				<div className="fixed inset-0 z-50 flex items-center justify-center">
					<div
						className="fixed inset-0 bg-black/50 backdrop-blur-sm"
						onClick={closeCreateModal}
					/>
					<div
						ref={modalRef}
						className="relative w-full max-w-lg rounded-xl border bg-background p-6 shadow-2xl"
						role="dialog"
						aria-modal="true"
						aria-labelledby="create-item-title"
					>
						<div className="flex items-center justify-between">
							<h2 id="create-item-title" className="text-lg font-semibold">
								{labels.createModalTitle ?? "Create Item"}
							</h2>
							<button
								onClick={closeCreateModal}
								id="close-create-item"
								aria-label="Close dialog"
								tabIndex={-1}
								className="rounded-lg p-1 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-primary"
							>
								<X className="h-5 w-5" />
							</button>
						</div>
						<div className="mt-4 space-y-4">
							{formError && (
								<div
									role="alert"
									aria-live="assertive"
									className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
								>
									{formError}
								</div>
							)}
							<div>
								<label
									htmlFor="item-title"
									className="block text-sm font-medium"
								>
									Title
								</label>
								<Input
									id="item-title"
									name="title"
									ref={titleInputRef}
									value={newTitle}
									onChange={(e) => setNewTitle(e.target.value)}
									placeholder="Enter item title"
									className="mt-1"
									aria-label="Title"
								/>
							</div>
							<div>
								<label
									htmlFor="item-description"
									className="block text-sm font-medium"
								>
									Description
								</label>
								<textarea
									id="item-description"
									name="description"
									value={newDescription}
									onChange={(e) => setNewDescription(e.target.value)}
									placeholder="Describe the item"
									className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
									aria-label="Description"
								/>
							</div>
							<div className="grid gap-4 sm:grid-cols-2">
								<div>
									<label
										htmlFor="item-type"
										className="block text-sm font-medium"
									>
										Type
									</label>
									<Select value={newType} onValueChange={setNewType}>
										<SelectTrigger
											id="item-type"
											aria-label="Type"
											className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
										>
											<SelectValue placeholder="Select type" />
										</SelectTrigger>
										<SelectContent>
											{["feature", "requirement", "test", "bug", "task"].map(
												(t) => (
													<SelectItem key={t} value={t}>
														{t}
													</SelectItem>
												),
											)}
										</SelectContent>
									</Select>
								</div>
								<div>
									<label
										htmlFor="item-status"
										className="block text-sm font-medium"
									>
										Status
									</label>
									<select
										id="item-status"
										name="status"
										value={newStatus}
										onChange={(e) => setNewStatus(e.target.value as ItemStatus)}
										tabIndex={-1}
										className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
										aria-label="Status"
									>
										{[
											"todo",
											"in_progress",
											"done",
											"blocked",
											"cancelled",
										].map((s) => (
											<option key={s} value={s}>
												{s.replace("_", " ")}
											</option>
										))}
									</select>
								</div>
							</div>
							<div>
								<label
									htmlFor="item-priority"
									className="block text-sm font-medium"
								>
									Priority
								</label>
								<select
									id="item-priority"
									name="priority"
									value={newPriority}
									onChange={(e) => setNewPriority(e.target.value as Priority)}
									tabIndex={-1}
									className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
									aria-label="Priority"
								>
									{["low", "medium", "high", "critical"].map((p) => (
										<option key={p} value={p}>
											{p}
										</option>
									))}
								</select>
							</div>
							<div className="flex justify-end gap-2 pt-2">
								<Button
									id="create-item-save"
									onClick={handleCreate}
									disabled={createItem.isPending}
								>
									{createItem.isPending
										? "Creating..."
										: (labels.createButtonLabel ?? "Create Item")}
								</Button>
								<Button
									id="create-item-cancel"
									variant="ghost"
									onClick={closeCreateModal}
								>
									Cancel
								</Button>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
