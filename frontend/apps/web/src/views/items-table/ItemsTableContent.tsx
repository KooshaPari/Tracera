import { useVirtualizer } from '@tanstack/react-virtual';
import { Filter } from 'lucide-react';
import React from 'react';

import type { TypedItem } from '@tracertm/types';

import { ResponsiveCardView } from '@/components/mobile/ResponsiveCardView';
import { EmptyState } from '@/components/ui/empty-state';
import { Table, TableBody } from '@/components/ui/table';
import { ListLoadingSkeleton, ModalLoadingOverlay } from '@/lib/lazy-loading';
import { cn } from '@/lib/utils';
import { Card } from '@tracertm/ui';

import { buildCardItems } from './card-items';
import itemsTableConstants from './constants';
import itemsTableFormatters from './formatters';
import { ItemTableRow } from './row';
import { TableHeaderRow } from './table-header';
import { useItemsTableKeyboardNav } from './useItemsTableKeyboardNav';
import { VirtualTable } from './virtual-table';

interface ItemsTableLabels {
  title: string;
  description: string;
  emptyTitle: string;
  emptyDescription: string;
  createModalTitle?: string | undefined;
  createButtonLabel?: string | undefined;
  newButtonLabel?: string | undefined;
}

interface ItemsTableContentProps {
  filteredItems: TypedItem[];
  isLoading: boolean;
  labels: ItemsTableLabels;
  liveMessageValue: string;
  showLoadingState: boolean;
  sortColumn: string;
  sortOrder: 'asc' | 'desc';
  onSortColumnChange: (next: string) => void;
  onSortOrderChange: (next: 'asc' | 'desc') => void;
  onNavigate: (item: TypedItem) => void;
  onDelete: (id: string) => void;
  onCreate: () => void;
}

function ItemsTableContent({
  filteredItems,
  isLoading,
  labels,
  liveMessageValue,
  showLoadingState,
  sortColumn,
  sortOrder,
  onSortColumnChange,
  onSortOrderChange,
  onNavigate,
  onDelete,
  onCreate,
}: ItemsTableContentProps): JSX.Element {
  const parentRef = React.useRef<HTMLDivElement | null>(null);

  const [liveMessage, setLiveMessage] = React.useState(liveMessageValue);
  React.useEffect(() => {
    setLiveMessage(liveMessageValue);
  }, [liveMessageValue]);

  const emptyStateActions = React.useMemo(() => {
    const label = labels.newButtonLabel ?? itemsTableConstants.DEFAULT_NEW_LABEL;
    return [
      {
        label,
        onClick: (): void => {
          onCreate();
        },
      },
    ];
  }, [labels.newButtonLabel, onCreate]);

  const emptyStateNode = React.useMemo(
    () => (
      <EmptyState
        icon={Filter}
        title={labels.emptyTitle}
        description={labels.emptyDescription}
        actions={emptyStateActions}
        variant='compact'
      />
    ),
    [emptyStateActions, labels.emptyDescription, labels.emptyTitle],
  );

  const measureElement = React.useMemo(() => {
    if (globalThis.window === undefined) {
      return;
    }
    const userAgent = globalThis.navigator?.userAgent ?? itemsTableConstants.EMPTY_STRING;
    if (userAgent.includes('Firefox')) {
      return;
    }
    return (element: Element): number => element.getBoundingClientRect().height;
  }, []);

  const rowVirtualizer = useVirtualizer({
    count: filteredItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => itemsTableConstants.VIRTUAL_ROW_HEIGHT,
    overscan: itemsTableConstants.VIRTUAL_OVERSCAN,
    ...(measureElement !== undefined ? { measureElement } : {}),
  });

  const handleSortChange = React.useCallback(
    (column: string): void => {
      onSortColumnChange(column);
      onSortOrderChange(sortOrder === 'asc' ? 'desc' : 'asc');
      rowVirtualizer.scrollToIndex(0, { align: 'center', behavior: 'auto' });
    },
    [onSortColumnChange, onSortOrderChange, rowVirtualizer, sortOrder],
  );

  const onCellKeyDown = useItemsTableKeyboardNav({
    items: filteredItems,
    onNavigate,
  });

  const showEmptyState = filteredItems.length === 0;
  const showInlineTable = filteredItems.length <= itemsTableConstants.TABLE_MAX_INLINE;

  const loadingOverlay = React.useMemo(
    () => (
      <ModalLoadingOverlay
        isVisible={showLoadingState}
        message={itemsTableFormatters.getSearchMessage(liveMessage, labels.title)}
        detail='Refreshing items'
      />
    ),
    [labels.title, liveMessage, showLoadingState],
  );

  const cardItems = React.useMemo(
    () => buildCardItems(filteredItems, onNavigate, onDelete),
    [filteredItems, onNavigate, onDelete],
  );

  if (isLoading) {
    return (
      <ListLoadingSkeleton
        message={itemsTableFormatters.getSearchMessage(liveMessageValue, labels.title)}
        rowCount={itemsTableConstants.LOADING_ROW_COUNT}
        dataTestId='items-live-region'
      />
    );
  }

  return (
    <div className='mx-auto max-w-[1600px] space-y-6 px-4 pb-20 sm:space-y-8 sm:px-6'>
      {loadingOverlay}
      <div
        role='status'
        aria-live='polite'
        aria-atomic='true'
        data-testid='items-live-region'
        className='sr-only'
      >
        {liveMessageValue}
      </div>
      <div id='table-instructions' className='sr-only'>
        Use arrow keys to move between cells. Press Home and End to jump to first or last column.
        PageUp and PageDown move several rows.
      </div>

      <div className='md:hidden'>
        <ResponsiveCardView items={cardItems} isLoading={false} emptyState={emptyStateNode} />
      </div>

      <div className='hidden md:block'>
        <Card className='bg-card/50 flex flex-col overflow-hidden rounded-[2rem] border-none shadow-sm'>
          {showEmptyState && (
            <div
              className={cn(
                'flex items-center justify-center p-6',
                `min-h-[${itemsTableConstants.TABLE_MIN_HEIGHT}px]`,
              )}
            >
              {emptyStateNode}
            </div>
          )}
          {!showEmptyState && showInlineTable && (
            <div className='custom-scrollbar overflow-x-auto'>
              <Table role='table' ariaLabel='Items table' ariaDescribedBy='table-instructions'>
                <TableHeaderRow
                  sortColumn={sortColumn}
                  sortOrder={sortOrder}
                  onSort={handleSortChange}
                />
                <TableBody>
                  {filteredItems.map((item, index) => (
                    <ItemTableRow
                      key={item.id}
                      item={item}
                      rowIndex={index}
                      onNavigate={onNavigate}
                      onDelete={onDelete}
                      onCellKeyDown={onCellKeyDown}
                    />
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
          {!showEmptyState && !showInlineTable && (
            <>
              <div className='custom-scrollbar overflow-x-auto'>
                <Table role='table' ariaLabel='Items table' ariaDescribedBy='table-instructions'>
                  <TableHeaderRow
                    sortColumn={sortColumn}
                    sortOrder={sortOrder}
                    onSort={handleSortChange}
                  />
                </Table>
              </div>
              <VirtualTable
                parentRef={parentRef}
                items={filteredItems}
                rowVirtualizer={rowVirtualizer}
                onNavigate={onNavigate}
                onDelete={onDelete}
                onCellKeyDown={onCellKeyDown}
                emptyState={emptyStateNode}
              />
            </>
          )}
        </Card>
      </div>
    </div>
  );
}

export { ItemsTableContent };
export type { ItemsTableContentProps, ItemsTableLabels };
