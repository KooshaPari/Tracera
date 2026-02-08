import { ArrowDown, ArrowUp } from 'lucide-react';

import { TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { cn } from '@/lib/utils';

import itemsTableConstants from './constants';
import itemsTableFormatters from './formatters';

interface TableHeaderProps {
  sortColumn: string;
  sortOrder: 'asc' | 'desc';
  onSort: (column: string) => void;
}

function TableHeaderRow({ sortColumn, sortOrder, onSort }: TableHeaderProps): JSX.Element {
  const sortDirection = itemsTableFormatters.getSortDirection(sortColumn, sortOrder, 'title');
  const ariaLabel = `Node Identifier ${itemsTableFormatters.getSortAriaLabel(sortColumn, sortOrder, 'title')}`;
  let sortIcon: JSX.Element | undefined;
  if (sortColumn === 'title' && sortOrder === 'asc') {
    sortIcon = <ArrowUp className='h-3 w-3' />;
  }
  if (sortColumn === 'title' && sortOrder === 'desc') {
    sortIcon = <ArrowDown className='h-3 w-3' />;
  }

  return (
    <TableHeader>
      <TableRow role='row' className='border-border/50 border-b hover:bg-transparent'>
        <TableHead
          colIndex={itemsTableConstants.ROW_INDEX_OFFSET}
          sortDirection={sortDirection}
          className={cn(
            'bg-card/50 sticky top-0 z-10 h-14 px-6 text-[10px] font-black tracking-widest uppercase',
            `w-[${itemsTableConstants.TABLE_HEADER_WIDTH}px]`,
          )}
        >
          <button
            type='button'
            onClick={() => {
              onSort('title');
            }}
            className='hover:text-primary flex items-center gap-2 transition-colors'
            aria-label={ariaLabel}
          >
            Node Identifier <span className='sr-only'>Title</span>
            {sortIcon}
          </button>
        </TableHead>
        <TableHead
          colIndex={itemsTableConstants.ROW_INDEX_OFFSET + 1}
          className='bg-card/50 sticky top-0 z-10 text-[10px] font-black tracking-widest uppercase'
        >
          Type
        </TableHead>
        <TableHead
          colIndex={itemsTableConstants.ROW_INDEX_OFFSET + 2}
          className='bg-card/50 sticky top-0 z-10 text-[10px] font-black tracking-widest uppercase'
        >
          Status
        </TableHead>
        <TableHead
          colIndex={itemsTableConstants.ROW_INDEX_OFFSET + 3}
          className='bg-card/50 sticky top-0 z-10 text-[10px] font-black tracking-widest uppercase'
        >
          Priority
        </TableHead>
        <TableHead
          colIndex={itemsTableConstants.ROW_INDEX_OFFSET + 4}
          className='bg-card/50 sticky top-0 z-10 text-[10px] font-black tracking-widest uppercase'
        >
          Owner
        </TableHead>
        <TableHead
          colIndex={itemsTableConstants.ROW_INDEX_OFFSET + 5}
          className='bg-card/50 sticky top-0 z-10 px-6 text-right text-[10px] font-black tracking-widest uppercase'
        >
          Actions
        </TableHead>
      </TableRow>
    </TableHeader>
  );
}

export { TableHeaderRow };
