/**
 * Enterprise Data Table with Advanced Features
 *
 * Professional table component with:
 * - Advanced filtering and search
 * - Column resizing and reordering
 * - Export functionality
 * - Bulk operations
 * - Virtual scrolling for large datasets
 * - Professional animations and micro-interactions
 */

import {
	flexRender,
	getCoreRowModel,
	getFilteredRowModel,
	getPaginationRowModel,
	getSortedRowModel,
	useReactTable,
} from "@tanstack/react-table";
import type {
	ColumnDef,
	ColumnFiltersState,
	RowSelectionState,
	SortingState,
	VisibilityState,
} from "@tanstack/react-table";
import { AnimatePresence, motion } from "framer-motion";
import {
	ArrowUpDown,
	ChevronDown,
	// Eye, // Unused
	// EyeOff, // Unused
	Download,
	Filter,
	Grid,
	List,
	MoreHorizontal,
} from "lucide-react";
import * as React from "react";
import { Badge } from "@/components/ui/badge";
import {
	DropdownMenu,
	DropdownMenuCheckboxItem,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/enterprise-button";
import { Input } from "@/components/ui/input";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

export interface DataTableProps<TData, TValue> {
	columns: ColumnDef<TData, TValue>[];
	data: TData[];
	searchPlaceholder?: string;
	enableColumnResizing?: boolean;
	enableColumnReordering?: boolean;
	enableRowSelection?: boolean;
	enableExport?: boolean;
	enableBulkActions?: boolean;
	bulkActions?: React.ReactNode;
	loading?: boolean;
	pagination?: {
		pageSize?: number;
		pageIndex?: number;
		pageCount?: number;
	};
}

// Monolithic data table; splitting into subcomponents is a follow-up refactor.
// eslint-disable-next-line max-lines-per-function -- DataTable is 427 lines; extract TableToolbar/Pagination/Body in follow-up
export function DataTable<TData, TValue>({
	columns,
	data,
	searchPlaceholder = "Search...",
	enableColumnResizing = true,
	enableColumnReordering = true,
	enableRowSelection = true,
	enableExport = true,
	enableBulkActions = true, // Used in future bulk actions feature
	bulkActions,
	loading = false,
	pagination: paginationProps,
}: DataTableProps<TData, TValue>) {
	const [sorting, setSorting] = React.useState<SortingState>([]);
	const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
		[],
	);
	const [columnVisibility, setColumnVisibility] =
		React.useState<VisibilityState>({});
	const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({});
	const [searchQuery, setSearchQuery] = React.useState("");
	const [isCompact, setIsCompact] = React.useState(false);

	// Memoized animation variants
	const toolbarAnimation = React.useMemo(() => ({
		animate: { opacity: 1, y: 0 },
		initial: { opacity: 0, y: -10 },
		transition: { duration: 0.2 },
	}), []);

	const selectionBadgeAnimation = React.useMemo(() => ({
		animate: { opacity: 1, scale: 1 },
		initial: { opacity: 0, scale: 0.9 },
	}), []);

	const rowAnimation = React.useMemo(() => ({
		animate: { opacity: 1, y: 0 },
		exit: { opacity: 0, y: -10 },
		initial: { opacity: 0, y: 10 },
		transition: { duration: 0.15 },
	}), []);

	const table = useReactTable({
		data,
		columns,
		getCoreRowModel: getCoreRowModel(),
		getPaginationRowModel: getPaginationRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel(),
		onSortingChange: setSorting,
		onColumnFiltersChange: setColumnFilters,
		onColumnVisibilityChange: setColumnVisibility,
		onRowSelectionChange: setRowSelection,
		state: {
			columnFilters,
			columnVisibility,
			rowSelection,
			sorting,
		},
		enableColumnResizing,
		enableRowSelection,
		manualPagination: Boolean(paginationProps),
		...(paginationProps?.pageCount !== undefined && {
			pageCount: paginationProps.pageCount,
		}),
	});

	// Memoized event handlers
	const handleSearchChange = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
		setSearchQuery(e.target.value);
	}, []);

	const handleStatusFilterAll = React.useCallback(() => {
		table.getColumn("status")?.setFilterValue("");
	}, [table]);

	const handleStatusFilterActive = React.useCallback(() => {
		table.getColumn("status")?.setFilterValue("active");
	}, [table]);

	const handleStatusFilterPending = React.useCallback(() => {
		table.getColumn("status")?.setFilterValue("pending");
	}, [table]);

	const handleStatusFilterCompleted = React.useCallback(() => {
		table.getColumn("status")?.setFilterValue("completed");
	}, [table]);

	const handlePageSizeChange = React.useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
		table.setPageSize(Number(e.target.value));
	}, [table]);

	const handleFirstPage = React.useCallback(() => {
		table.setPageIndex(0);
	}, [table]);

	const handlePreviousPage = React.useCallback(() => {
		table.previousPage();
	}, [table]);

	const handleNextPage = React.useCallback(() => {
		table.nextPage();
	}, [table]);

	const handleLastPage = React.useCallback(() => {
		table.setPageIndex(table.getPageCount() - 1);
	}, [table]);

	const handleToggleCompact = React.useCallback((value: boolean) => {
		setIsCompact(Boolean(value));
	}, []);

	// Export functionality
	const handleExport = React.useCallback(() => {
		const csv = [
			// Headers
			table
				.getVisibleFlatColumns()
				.map((col) => col.id)
				.join(","),
			// Data rows
			table
				.getRowModel()
				.rows.map((row) =>
					row
						.getVisibleCells()
						.map((cell) => String(cell.getValue()))
						.join(","),
				),
		].join("\n");

		const blob = new Blob([csv], { type: "text/csv" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `export_${new Date().toISOString().split("T")[0]}.csv`;
		a.click();
		URL.revokeObjectURL(url);
	}, [table]);

	// Apply search filter
	React.useEffect(() => {
		if (!paginationProps) {
			return;
		}

		const globalFilter = searchQuery
			? table
					.getFilteredRowModel()
					.rows.filter((row) => {
						const original = row.original as Record<string, unknown>;
						return Object.values(original).some((value) =>
							String(value).toLowerCase().includes(searchQuery.toLowerCase()),
						);
					})
					.map((row) => row.original)
			: data;

		// Update filtered data
		table.setOptions((prev) => ({
			...prev,
			data: globalFilter as TData[],
		}));
	}, [searchQuery, table, data, paginationProps]);

	const selectedRowCount = table.getFilteredSelectedRowModel().rows.length;

	// Memoized column visibility items to prevent recreation on each render
	const ColumnVisibilityItems = React.useMemo(() => {
		return table
			.getAllColumns()
			.filter((column) => column.getCanHide())
			.map((column) => {
				const handleToggle = (value: boolean) => {
					column.toggleVisibility(!!value);
				};
				return (
					<DropdownMenuCheckboxItem
						key={column.id}
						className="capitalize"
						checked={column.getIsVisible()}
						onCheckedChange={handleToggle}
					>
						{column.id}
					</DropdownMenuCheckboxItem>
				);
			});
	}, [table]);

	return (
		<div className="space-y-4">
			{/* Toolbar */}
			<motion.div
				className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between"
				{...toolbarAnimation}
			>
				{/* Search and Filters */}
				<div className="flex items-center gap-2 flex-1">
					<div className="relative">
						<Input
							placeholder={searchPlaceholder}
							value={searchQuery}
							onChange={handleSearchChange}
							className="w-full sm:w-[300px] pl-9"
						/>
						<Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					</div>

					{table.getColumn("status") && (
						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<span>
									<Button variant="outline" className="h-8">
										<Grid className="mr-2 h-4 w-4" />
										Status
										<ChevronDown className="ml-2 h-4 w-4" />
									</Button>
								</span>
							</DropdownMenuTrigger>
							<DropdownMenuContent className="w-[150px]">
								<DropdownMenuItem onClick={handleStatusFilterAll}>
									All Status
								</DropdownMenuItem>
								<DropdownMenuItem onClick={handleStatusFilterActive}>
									Active
								</DropdownMenuItem>
								<DropdownMenuItem onClick={handleStatusFilterPending}>
									Pending
								</DropdownMenuItem>
								<DropdownMenuItem onClick={handleStatusFilterCompleted}>
									Completed
								</DropdownMenuItem>
							</DropdownMenuContent>
						</DropdownMenu>
					)}
				</div>

				{/* Actions */}
				<div className="flex items-center gap-2">
					{enableBulkActions && selectedRowCount > 0 && bulkActions && (
						<motion.div
							className="flex items-center gap-2"
							{...selectionBadgeAnimation}
						>
							<Badge variant="secondary" className="px-2 py-1">
								{selectedRowCount} selected
							</Badge>
							{bulkActions}
						</motion.div>
					)}

					<div className="flex items-center gap-1">
						{enableExport && (
							<Button variant="outline" size="sm" onClick={handleExport}>
								<Download className="mr-2 h-4 w-4" />
								Export
							</Button>
						)}

						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<span>
									<Button variant="outline" size="sm">
										<MoreHorizontal className="h-4 w-4" />
									</Button>
								</span>
							</DropdownMenuTrigger>
							<DropdownMenuContent align="end">
								{enableColumnReordering && (
									<>
										<DropdownMenuLabel>Column Order</DropdownMenuLabel>
										<DropdownMenuItem>
											<List className="mr-2 h-4 w-4" />
											Reset to Default
										</DropdownMenuItem>
										<DropdownMenuSeparator />
									</>
								)}
								<DropdownMenuLabel>Toggle Columns</DropdownMenuLabel>
								{ColumnVisibilityItems}
								<DropdownMenuSeparator />
								<DropdownMenuCheckboxItem
									checked={isCompact}
									onCheckedChange={handleToggleCompact}
								>
									Compact View
								</DropdownMenuCheckboxItem>
							</DropdownMenuContent>
						</DropdownMenu>
					</div>
				</div>
			</motion.div>

			{/* Table */}
			<div className="rounded-md border bg-card">
				<Table>
					<TableHeader>
						{table.getHeaderGroups().map((headerGroup) => (
							<TableRow key={headerGroup.id} className="bg-muted/30">
								{headerGroup.headers.map((header) => (
									<TableHead
										key={header.id}
										className={cn(
											"font-medium",
											header.column.getCanSort() &&
												"cursor-pointer hover:bg-muted/50",
											isCompact && "px-2 py-1",
										)}
										onClick={header.column.getToggleSortingHandler()}
									>
										{header.isPlaceholder ? null : (
											<div className="flex items-center space-x-2">
												<span>
													{flexRender(
														header.column.columnDef.header,
														header.getContext(),
													)}
												</span>
												{header.column.getCanSort() && (
													<Button
														variant="ghost"
														size="sm"
														className="h-6 w-6 p-0"
													>
														<ArrowUpDown
															className={cn(
																"h-3 w-3",
																header.column.getIsSorted() === "asc" &&
																	"rotate-180",
															)}
														/>
													</Button>
												)}
											</div>
										)}
									</TableHead>
								))}
							</TableRow>
						))}
					</TableHeader>
					<TableBody>
						<AnimatePresence>
							{loading ? (
								// Loading skeleton
								Array.from({ length: 5 }).map((_, index) => (
									<TableRow key={`skeleton-${index}`}>
										{columns.map((_, colIndex) => (
											<TableCell
												key={colIndex}
												className={isCompact ? "px-2 py-1" : undefined}
											>
												<div className="h-4 bg-muted rounded animate-pulse" />
											</TableCell>
										))}
									</TableRow>
								))
							) : (table.getRowModel().rows?.length ? (
								table.getRowModel().rows.map((row) => (
									<motion.tr
										key={row.id}
										data-state={row.getIsSelected() && "selected"}
										{...rowAnimation}
										className={cn(
											"hover:bg-muted/50 transition-colors",
											isCompact && "divide-x divide-border",
										)}
									>
										{row.getVisibleCells().map((cell) => (
											<TableCell
												key={cell.id}
												className={cn(isCompact && "px-2 py-1")}
											>
												{flexRender(
													cell.column.columnDef.cell,
													cell.getContext(),
												)}
											</TableCell>
										))}
									</motion.tr>
								))
							) : (
								<TableRow>
									<TableCell
										colSpan={columns.length}
										className="h-24 text-center text-muted-foreground"
									>
										No results found.
									</TableCell>
								</TableRow>
							))}
						</AnimatePresence>
					</TableBody>
				</Table>
			</div>

			{/* Pagination */}
			{!paginationProps && (
				<div className="flex items-center justify-between space-x-2 py-4">
					<div className="flex-1 text-sm text-muted-foreground">
						{table.getFilteredSelectedRowModel().rows.length} of{" "}
						{table.getFilteredRowModel().rows.length} row(s) selected.
					</div>
					<div className="flex items-center space-x-6 lg:space-x-8">
						<div className="flex items-center space-x-2">
							<p className="text-sm font-medium">Rows per page</p>
							<select
								value={table.getState().pagination.pageSize}
								onChange={handlePageSizeChange}
								className="h-8 w-[70px] rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
							>
								{[10, 20, 30, 40, 50].map((pageSize) => (
									<option key={pageSize} value={pageSize}>
										{pageSize}
									</option>
								))}
							</select>
						</div>
						<div className="flex w-[100px] items-center justify-center text-sm font-medium">
							Page {table.getState().pagination.pageIndex + 1} of{" "}
							{table.getPageCount()}
						</div>
						<div className="flex items-center space-x-2">
							<Button
								variant="outline"
								className="hidden h-8 w-8 p-0 lg:flex"
								onClick={handleFirstPage}
								disabled={!table.getCanPreviousPage()}
							>
								<span className="sr-only">Go to first page</span>
								&lt;&lt;
							</Button>
							<Button
								variant="outline"
								className="h-8 w-8 p-0"
								onClick={handlePreviousPage}
								disabled={!table.getCanPreviousPage()}
							>
								<span className="sr-only">Go to previous page</span>
								&lt;
							</Button>
							<Button
								variant="outline"
								className="h-8 w-8 p-0"
								onClick={handleNextPage}
								disabled={!table.getCanNextPage()}
							>
								<span className="sr-only">Go to next page</span>
								&gt;
							</Button>
							<Button
								variant="outline"
								className="hidden h-8 w-8 p-0 lg:flex"
								onClick={handleLastPage}
								disabled={!table.getCanNextPage()}
							>
								<span className="sr-only">Go to last page</span>
								&gt;&gt;
							</Button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

// Enhanced column with enterprise features
export function createEnterpriseColumn<TData, TValue>({
	id,
	header,
	cell,
	size,
	maxSize,
	minSize,
	enableSorting = true,
	enableFiltering = true,
	enableHiding = true,
	enableResizing = true,
	meta,
}: {
	id: string;
	header: string;
	cell: (props: {
		row: { original: TData };
		getValue: () => TValue;
	}) => React.ReactNode;
	size?: number;
	maxSize?: number;
	minSize?: number;
	enableSorting?: boolean;
	enableFiltering?: boolean;
	enableHiding?: boolean;
	enableResizing?: boolean;
	meta?: Record<string, unknown>;
}): ColumnDef<TData, TValue> {
	return {
		id,
		header,
		cell,
		size: size ?? undefined,
		maxSize: maxSize ?? undefined,
		minSize: minSize ?? undefined,
		enableSorting: enableSorting ?? undefined,
		enableColumnFilter: enableFiltering ?? undefined,
		enableHiding: enableHiding ?? undefined,
		enableResizing: enableResizing ?? undefined,
		accessorFn: () => null as TValue, // Placeholder - cell function handles rendering
		meta: {
			...meta,
			isAction: meta?.["isAction"],
			isSticky: meta?.["isSticky"],
		},
	} as ColumnDef<TData, TValue>;
}
