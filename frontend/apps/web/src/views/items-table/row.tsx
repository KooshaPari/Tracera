import { ExternalLink, MoreVertical, Trash2 } from 'lucide-react';

import type { TypedItem } from '@tracertm/types';

import { TableCell, TableRow } from '@/components/ui/table';
import {
  Badge,
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@tracertm/ui';

import itemsTableConstants from './constants';
import itemsTableFormatters from './formatters';
import { PriorityDot } from './priority-dot';
import { StatusBadge } from './status-badges';

interface TableRowProps {
  item: TypedItem;
  rowIndex: number;
  onNavigate: (item: TypedItem) => void;
  onDelete: (id: string) => void;
  onCellKeyDown: (event: React.KeyboardEvent<HTMLElement>) => void;
}

function ItemTableRow({
  item,
  rowIndex,
  onNavigate,
  onDelete,
  onCellKeyDown,
}: TableRowProps): JSX.Element {
  const handleNavigate = (): void => {
    onNavigate(item);
  };

  const handleDelete = (): void => {
    onDelete(item.id);
  };

  const owner = itemsTableFormatters.getItemOwnerLabel(item.owner);
  const priorityLabel = itemsTableFormatters.getPriorityLabel(item.priority);

  return (
    <TableRow
      role='row'
      rowIndex={rowIndex + itemsTableConstants.ROW_INDEX_OFFSET}
      data-testid='item-card'
      className='group border-border/30 hover:bg-muted/30 active:bg-muted/40 border-b transition-all duration-200 ease-out'
    >
      <TableCell
        role='gridcell'
        tabIndex={0}
        data-testid='item-card'
        data-row-index={rowIndex}
        data-col-index={0}
        className='focus-visible:ring-primary/40 px-6 py-4 focus-visible:ring-2 focus-visible:outline-none'
        onKeyDown={onCellKeyDown}
      >
        <button
          type='button'
          data-testid='item-card'
          onClick={handleNavigate}
          className='group/link block w-full text-left'
        >
          <div
            data-testid='item-title'
            className='group-hover/link:text-primary truncate text-sm font-bold transition-colors'
          >
            {item.title}
          </div>
          <div className='text-muted-foreground mt-0.5 font-mono text-[10px] uppercase'>
            {item.id.slice(0, itemsTableConstants.ITEM_ID_PREFIX_LENGTH)}
          </div>
        </button>
      </TableCell>
      <TableCell
        role='gridcell'
        tabIndex={0}
        data-row-index={rowIndex}
        data-col-index={1}
        headerText='Type'
        className='focus-visible:ring-primary/40 focus-visible:ring-2 focus-visible:outline-none'
        onKeyDown={onCellKeyDown}
      >
        <Badge
          variant='outline'
          className='h-4 px-1.5 text-[8px] font-black tracking-tighter uppercase'
        >
          {item.type}
        </Badge>
      </TableCell>
      <TableCell
        role='gridcell'
        tabIndex={0}
        data-row-index={rowIndex}
        data-col-index={2}
        headerText='Status'
        className='focus-visible:ring-primary/40 focus-visible:ring-2 focus-visible:outline-none'
        onKeyDown={onCellKeyDown}
      >
        <StatusBadge status={item.status} />
      </TableCell>
      <TableCell
        role='gridcell'
        tabIndex={0}
        data-row-index={rowIndex}
        data-col-index={3}
        headerText='Priority'
        className='focus-visible:ring-primary/40 focus-visible:ring-2 focus-visible:outline-none'
        onKeyDown={onCellKeyDown}
      >
        <div className='flex items-center gap-2'>
          <PriorityDot priority={item.priority} />
          <span className='text-muted-foreground text-[10px] font-bold uppercase'>
            {priorityLabel}
          </span>
        </div>
      </TableCell>
      <TableCell
        role='gridcell'
        tabIndex={0}
        data-row-index={rowIndex}
        data-col-index={4}
        headerText='Owner'
        className='focus-visible:ring-primary/40 focus-visible:ring-2 focus-visible:outline-none'
        onKeyDown={onCellKeyDown}
      >
        <div className='flex items-center gap-2'>
          <div className='bg-muted flex h-5 w-5 items-center justify-center rounded-full text-[8px] font-black uppercase'>
            {owner.initial}
          </div>
          <span className='text-muted-foreground text-[10px] font-bold uppercase'>
            {owner.label}
          </span>
        </div>
      </TableCell>
      <TableCell
        role='gridcell'
        tabIndex={0}
        data-row-index={rowIndex}
        data-col-index={5}
        headerText='Actions'
        className='focus-visible:ring-primary/40 px-6 text-right focus-visible:ring-2 focus-visible:outline-none'
        onKeyDown={onCellKeyDown}
      >
        <div className='flex justify-end gap-1'>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <span>
                <Button
                  variant='ghost'
                  size='icon'
                  className='h-8 w-8 rounded-lg'
                  data-testid='item-menu'
                  aria-label={`Open item actions for ${item.title}`}
                >
                  <MoreVertical className='h-3.5 w-3.5' />
                </Button>
              </span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end'>
              <DropdownMenuItem onClick={handleNavigate}>View</DropdownMenuItem>
              <DropdownMenuItem onClick={handleDelete}>Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button
            variant='ghost'
            size='icon'
            className='h-8 w-8 rounded-lg'
            onClick={handleNavigate}
            aria-label={`Open item ${item.title}`}
          >
            <ExternalLink className='h-3.5 w-3.5' />
          </Button>
          <Button
            variant='ghost'
            size='icon'
            className='text-destructive hover:bg-destructive/10 h-8 w-8 rounded-lg'
            onClick={handleDelete}
            aria-label={`Delete item ${item.title}`}
          >
            <Trash2 className='h-3.5 w-3.5' />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

export { ItemTableRow };
export type { TableRowProps };
