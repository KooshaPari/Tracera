import * as React from 'react';

import { cn } from '@/lib/utils';

interface AccessibleTableProps extends React.HTMLAttributes<HTMLTableElement> {
  /** ARIA label for the table */
  ariaLabel?: string;
  /** ARIA label ID for the table */
  ariaLabelledBy?: string;
  /** Accessible description of the table */
  ariaDescribedBy?: string;
}

const Table = React.forwardRef<HTMLTableElement, AccessibleTableProps>(
  ({ className, ariaLabel, ariaLabelledBy, ariaDescribedBy, ...props }, ref) => (
    <div className='relative w-full overflow-auto'>
      <table
        ref={ref}
        className={cn('w-full caption-bottom text-sm', className)}
        aria-label={ariaLabel}
        aria-labelledby={ariaLabelledBy}
        aria-describedby={ariaDescribedBy}
        {...props}
      />
    </div>
  ),
);
Table.displayName = 'Table';

const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead ref={ref} className={cn('[&_tr]:border-b', className)} {...props} />
));
TableHeader.displayName = 'TableHeader';

const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody ref={ref} className={cn('[&_tr:last-child]:border-0', className)} {...props} />
));
TableBody.displayName = 'TableBody';

const TableFooter = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tfoot
    ref={ref}
    className={cn('border-t bg-muted/50 font-medium [&>tr]:last:border-b-0', className)}
    {...props}
  />
));
TableFooter.displayName = 'TableFooter';

interface AccessibleTableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  /** Whether this row is selected */
  isSelected?: boolean;
  /** Row index for aria-rowindex */
  rowIndex?: number;
}

const TableRow = React.forwardRef<HTMLTableRowElement, AccessibleTableRowProps>(
  ({ className, isSelected, rowIndex, ...props }, ref) => (
    <tr
      ref={ref}
      className={cn(
        'border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted',
        className,
      )}
      aria-rowindex={rowIndex}
      aria-selected={isSelected}
      {...props}
    />
  ),
);
TableRow.displayName = 'TableRow';

interface AccessibleTableHeadProps extends React.ThHTMLAttributes<HTMLTableCellElement> {
  /** Sort direction for aria-sort */
  sortDirection?: 'ascending' | 'descending' | 'none' | 'other';
  /** Column index for aria-colindex */
  colIndex?: number;
  /** Whether this column is sortable */
  isSortable?: boolean;
}

const TableHead = React.forwardRef<HTMLTableCellElement, AccessibleTableHeadProps>(
  ({ className, sortDirection, colIndex, isSortable, ...props }, ref) => (
    <th
      ref={ref}
      className={cn(
        'h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0',
        isSortable && 'cursor-pointer hover:bg-muted/30',
        className,
      )}
      role='columnheader'
      aria-colindex={colIndex}
      aria-sort={sortDirection ?? 'none'}
      {...props}
    />
  ),
);
TableHead.displayName = 'TableHead';

interface AccessibleTableCellProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  /** Cell content label for screen readers */
  ariaLabel?: string;
  /** Column index for aria-colindex */
  colIndex?: number;
  /** Header text for this cell */
  headerText?: string;
}

const TableCell = React.forwardRef<HTMLTableCellElement, AccessibleTableCellProps>(
  ({ className, ariaLabel, colIndex, headerText, ...props }, ref) => (
    <td
      ref={ref}
      className={cn('p-4 align-middle [&:has([role=checkbox])]:pr-0', className)}
      aria-label={
        ariaLabel ?? (headerText ? `${headerText}: ${String(props.children)}` : undefined)
      }
      aria-colindex={colIndex}
      {...props}
    />
  ),
);
TableCell.displayName = 'TableCell';

const TableCaption = React.forwardRef<
  HTMLTableCaptionElement,
  React.HTMLAttributes<HTMLTableCaptionElement>
>(({ className, ...props }, ref) => (
  <caption ref={ref} className={cn('mt-4 text-sm text-muted-foreground', className)} {...props} />
));
TableCaption.displayName = 'TableCaption';

export { Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption };
