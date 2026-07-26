import type { Table as TableType } from '@tanstack/react-table';

import { motion } from 'framer-motion';
import { ChevronDown, Download, Filter, Grid, List, MoreHorizontal } from 'lucide-react';
import * as React from 'react';

import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/enterprise-button';
import { Input } from '@/components/ui/input';

interface DataTableToolbarProps<TData> {
  table: TableType<TData>;
  searchQuery: string;
  onSearchChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  searchPlaceholder: string;
  enableExport: boolean;
  enableBulkActions: boolean;
  enableColumnReordering: boolean;
  bulkActions?: React.ReactNode;
  isCompact: boolean;
  onToggleCompact: (value: boolean) => void;
  onExport: () => void;
}

const TOOLBAR_ANIMATION = {
  animate: { opacity: 1, y: 0 },
  initial: { opacity: 0, y: -10 },
  transition: { duration: 0.2 },
};

const SELECTION_ANIMATION = {
  animate: { opacity: 1, scale: 1 },
  initial: { opacity: 0, scale: 0.9 },
};

export function DataTableToolbar<TData>({
  table,
  searchQuery,
  onSearchChange,
  searchPlaceholder,
  enableExport,
  enableBulkActions,
  enableColumnReordering,
  bulkActions,
  isCompact,
  onToggleCompact,
  onExport,
}: DataTableToolbarProps<TData>): React.JSX.Element {
  const selectedRowCount = table.getFilteredSelectedRowModel().rows.length;

  const handleStatusFilterAll = React.useCallback(() => {
    table.getColumn('status')?.setFilterValue('');
  }, [table]);

  const handleStatusFilterActive = React.useCallback(() => {
    table.getColumn('status')?.setFilterValue('active');
  }, [table]);

  const handleStatusFilterPending = React.useCallback(() => {
    table.getColumn('status')?.setFilterValue('pending');
  }, [table]);

  const handleStatusFilterCompleted = React.useCallback(() => {
    table.getColumn('status')?.setFilterValue('completed');
  }, [table]);

  const columnVisibilityItems = React.useMemo(
    () =>
      table
        .getAllColumns()
        .filter((column) => column.getCanHide())
        .map((column) => (
          <DropdownMenuCheckboxItem
            key={column.id}
            className='capitalize'
            checked={column.getIsVisible()}
            onCheckedChange={(value: boolean) => {
              column.toggleVisibility(Boolean(value));
            }}
          >
            {column.id}
          </DropdownMenuCheckboxItem>
        )),
    [table],
  );

  return (
    <motion.div
      className='flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center'
      {...TOOLBAR_ANIMATION}
    >
      <div className='flex flex-1 items-center gap-2'>
        <div className='relative'>
          <Input
            placeholder={searchPlaceholder}
            value={searchQuery}
            onChange={onSearchChange}
            className='w-full pl-9 sm:w-[300px]'
          />
          <Filter className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
        </div>

        {table.getColumn('status') && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <span>
                <Button variant='outline' className='h-8'>
                  <Grid className='mr-2 h-4 w-4' />
                  Status
                  <ChevronDown className='ml-2 h-4 w-4' />
                </Button>
              </span>
            </DropdownMenuTrigger>
            <DropdownMenuContent className='w-[150px]'>
              <DropdownMenuItem onClick={handleStatusFilterAll}>All Status</DropdownMenuItem>
              <DropdownMenuItem onClick={handleStatusFilterActive}>Active</DropdownMenuItem>
              <DropdownMenuItem onClick={handleStatusFilterPending}>Pending</DropdownMenuItem>
              <DropdownMenuItem onClick={handleStatusFilterCompleted}>Completed</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      <div className='flex items-center gap-2'>
        {enableBulkActions && selectedRowCount > 0 && bulkActions && (
          <motion.div className='flex items-center gap-2' {...SELECTION_ANIMATION}>
            <Badge variant='secondary' className='px-2 py-1'>
              {selectedRowCount} selected
            </Badge>
            {bulkActions}
          </motion.div>
        )}

        <div className='flex items-center gap-1'>
          {enableExport && (
            <Button variant='outline' size='sm' onClick={onExport}>
              <Download className='mr-2 h-4 w-4' />
              Export
            </Button>
          )}

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <span>
                <Button variant='outline' size='sm'>
                  <MoreHorizontal className='h-4 w-4' />
                </Button>
              </span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end'>
              {enableColumnReordering && (
                <>
                  <DropdownMenuLabel>Column Order</DropdownMenuLabel>
                  <DropdownMenuItem>
                    <List className='mr-2 h-4 w-4' />
                    Reset to Default
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuLabel>Toggle Columns</DropdownMenuLabel>
              {columnVisibilityItems}
              <DropdownMenuSeparator />
              <DropdownMenuCheckboxItem checked={isCompact} onCheckedChange={onToggleCompact}>
                Compact View
              </DropdownMenuCheckboxItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </motion.div>
  );
}
