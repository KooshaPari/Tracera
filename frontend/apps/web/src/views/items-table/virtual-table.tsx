import type { Virtualizer } from '@tanstack/react-virtual';

import type { TypedItem } from '@tracertm/types';

import { Table, TableBody } from '@/components/ui/table';

import { ItemTableRow } from './row';
import { createVirtualContainerStyle, createVirtualRowStyle } from './virtual-utils';

interface VirtualTableProps {
  parentRef: React.RefObject<HTMLDivElement | null>;
  items: TypedItem[];
  rowVirtualizer: Virtualizer<HTMLDivElement, Element>;
  onNavigate: (item: TypedItem) => void;
  onDelete: (id: string) => void;
  onCellKeyDown: (event: React.KeyboardEvent<HTMLElement>) => void;
  emptyState: React.ReactNode;
}

function VirtualTable({
  parentRef,
  items,
  rowVirtualizer,
  onNavigate,
  onDelete,
  onCellKeyDown,
  emptyState,
}: VirtualTableProps): JSX.Element {
  let content: React.ReactNode = (
    <div className='flex h-[600px] items-center justify-center p-6'>{emptyState}</div>
  );

  if (items.length > 0) {
    content = (
      <div style={createVirtualContainerStyle(rowVirtualizer.getTotalSize())}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
          const item = items[virtualRow.index];
          if (item === undefined) {
            return null;
          }
          const rowStyle = createVirtualRowStyle(virtualRow.size, virtualRow.start);
          return (
            <div
              key={item.id}
              style={rowStyle}
              data-item-id={item.id}
              data-index={virtualRow.index}
            >
              <div className='custom-scrollbar overflow-x-auto'>
                <Table role='table' ariaLabel='Items table' ariaDescribedBy='table-instructions'>
                  <TableBody>
                    <ItemTableRow
                      item={item}
                      rowIndex={virtualRow.index}
                      onNavigate={onNavigate}
                      onDelete={onDelete}
                      onCellKeyDown={onCellKeyDown}
                    />
                  </TableBody>
                </Table>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      ref={parentRef}
      className='custom-scrollbar h-[600px] flex-1 overflow-x-hidden overflow-y-auto'
      role='region'
      aria-label='Table content with virtual scrolling'
    >
      {content}
    </div>
  );
}

export { VirtualTable };
export type { VirtualTableProps };
