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

import type {
  ColumnDef,
  ColumnFiltersState,
  RowSelectionState,
  SortingState,
  VisibilityState,
} from '@tanstack/react-table';

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowUpDown } from 'lucide-react';
import * as React from 'react';

import { Button } from '@/components/ui/enterprise-button';
import { DataTablePagination } from '@/components/ui/enterprise-table-pagination';
import { DataTableToolbar } from '@/components/ui/enterprise-table-toolbar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils';

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

const ROW_ANIMATION = {
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  initial: { opacity: 0, y: 10 },
  transition: { duration: 0.15 },
};

const SKELETON_ROWS = 5;

export function DataTable<TData, TValue>({
  columns,
  data,
  searchPlaceholder = 'Search...',
  enableColumnResizing = true,
  enableColumnReordering = true,
  enableRowSelection = true,
  enableExport = true,
  enableBulkActions = true,
  bulkActions,
  loading = false,
  pagination: paginationProps,
}: DataTableProps<TData, TValue>): React.JSX.Element {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({});
  const [searchQuery, setSearchQuery] = React.useState('');
  const [isCompact, setIsCompact] = React.useState(false);

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
    state: { columnFilters, columnVisibility, rowSelection, sorting },
    enableColumnResizing,
    enableRowSelection,
    manualPagination: Boolean(paginationProps),
    ...(paginationProps?.pageCount !== undefined && { pageCount: paginationProps.pageCount }),
  });

  const handleSearchChange = React.useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  }, []);

  const handleToggleCompact = React.useCallback((value: boolean) => {
    setIsCompact(Boolean(value));
  }, []);

  const handleExport = React.useCallback(() => {
    const csv = [
      table
        .getVisibleFlatColumns()
        .map((col) => col.id)
        .join(','),
      table.getRowModel().rows.map((row) =>
        row
          .getVisibleCells()
          .map((cell) => String(cell.getValue()))
          .join(','),
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `export_${new Date().toISOString().split('T')[0]}.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  }, [table]);

  React.useEffect(() => {
    if (!paginationProps) return;
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
    table.setOptions((prev) => ({ ...prev, data: globalFilter }));
  }, [searchQuery, table, data, paginationProps]);

  return (
    <div className='space-y-4'>
      <DataTableToolbar
        table={table}
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        searchPlaceholder={searchPlaceholder}
        enableExport={enableExport}
        enableBulkActions={enableBulkActions}
        enableColumnReordering={enableColumnReordering}
        bulkActions={bulkActions}
        isCompact={isCompact}
        onToggleCompact={handleToggleCompact}
        onExport={handleExport}
      />

      <div className='bg-card rounded-md border'>
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className='bg-muted/30'>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    className={cn(
                      'font-medium',
                      header.column.getCanSort() && 'cursor-pointer hover:bg-muted/50',
                      isCompact && 'px-2 py-1',
                    )}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    {header.isPlaceholder ? null : (
                      <div className='flex items-center space-x-2'>
                        <span>
                          {flexRender(header.column.columnDef.header, header.getContext())}
                        </span>
                        {header.column.getCanSort() && (
                          <Button variant='ghost' size='sm' className='h-6 w-6 p-0'>
                            <ArrowUpDown
                              className={cn(
                                'h-3 w-3',
                                header.column.getIsSorted() === 'asc' && 'rotate-180',
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
                Array.from({ length: SKELETON_ROWS }).map((_, index) => (
                  <TableRow key={`skeleton-${String(index)}`}>
                    {columns.map((_, colIndex) => (
                      <TableCell
                        key={String(colIndex)}
                        className={isCompact ? 'px-2 py-1' : undefined}
                      >
                        <div className='bg-muted h-4 animate-pulse rounded' />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : table.getRowModel().rows.length > 0 ? (
                table.getRowModel().rows.map((row) => (
                  <motion.tr
                    key={row.id}
                    data-state={row.getIsSelected() && 'selected'}
                    {...ROW_ANIMATION}
                    className={cn(
                      'hover:bg-muted/50 transition-colors',
                      isCompact && 'divide-x divide-border',
                    )}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id} className={cn(isCompact && 'px-2 py-1')}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </motion.tr>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className='text-muted-foreground h-24 text-center'
                  >
                    No results found.
                  </TableCell>
                </TableRow>
              )}
            </AnimatePresence>
          </TableBody>
        </Table>
      </div>

      {!paginationProps && <DataTablePagination table={table} />}
    </div>
  );
}

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
  cell: (props: { row: { original: TData }; getValue: () => TValue }) => React.ReactNode;
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
    accessorFn: () => null as TValue,
    meta: {
      ...meta,
      isAction: meta?.['isAction'],
      isSticky: meta?.['isSticky'],
    },
  } as ColumnDef<TData, TValue>;
}
