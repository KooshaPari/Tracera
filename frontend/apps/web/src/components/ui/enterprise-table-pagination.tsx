import type { Table as TableType } from '@tanstack/react-table';

import * as React from 'react';

import { Button } from '@/components/ui/enterprise-button';

const PAGE_SIZE_OPTIONS = [10, 20, 30, 40, 50] as const;

interface DataTablePaginationProps<TData> {
  table: TableType<TData>;
}

export function DataTablePagination<TData>({
  table,
}: DataTablePaginationProps<TData>): React.JSX.Element {
  const handlePageSizeChange = React.useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      table.setPageSize(Number(event.target.value));
    },
    [table],
  );

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

  return (
    <div className='flex items-center justify-between space-x-2 py-4'>
      <div className='text-muted-foreground flex-1 text-sm'>
        {table.getFilteredSelectedRowModel().rows.length} of{' '}
        {table.getFilteredRowModel().rows.length} row(s) selected.
      </div>
      <div className='flex items-center space-x-6 lg:space-x-8'>
        <div className='flex items-center space-x-2'>
          <p className='text-sm font-medium'>Rows per page</p>
          <select
            value={table.getState().pagination.pageSize}
            onChange={handlePageSizeChange}
            className='border-input bg-background ring-offset-background focus:ring-ring h-8 w-[70px] rounded-md border px-3 py-1 text-sm focus:ring-2 focus:ring-offset-2 focus:outline-none'
          >
            {PAGE_SIZE_OPTIONS.map((pageSize) => (
              <option key={pageSize} value={pageSize}>
                {pageSize}
              </option>
            ))}
          </select>
        </div>
        <div className='flex w-[100px] items-center justify-center text-sm font-medium'>
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </div>
        <div className='flex items-center space-x-2'>
          <Button
            variant='outline'
            className='hidden h-8 w-8 p-0 lg:flex'
            onClick={handleFirstPage}
            disabled={!table.getCanPreviousPage()}
          >
            <span className='sr-only'>Go to first page</span>
            &lt;&lt;
          </Button>
          <Button
            variant='outline'
            className='h-8 w-8 p-0'
            onClick={handlePreviousPage}
            disabled={!table.getCanPreviousPage()}
          >
            <span className='sr-only'>Go to previous page</span>
            &lt;
          </Button>
          <Button
            variant='outline'
            className='h-8 w-8 p-0'
            onClick={handleNextPage}
            disabled={!table.getCanNextPage()}
          >
            <span className='sr-only'>Go to next page</span>
            &gt;
          </Button>
          <Button
            variant='outline'
            className='hidden h-8 w-8 p-0 lg:flex'
            onClick={handleLastPage}
            disabled={!table.getCanNextPage()}
          >
            <span className='sr-only'>Go to last page</span>
            &gt;&gt;
          </Button>
        </div>
      </div>
    </div>
  );
}
