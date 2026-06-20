import type { TypedItem } from '@tracertm/types';

import itemsTableConstants from './constants';

interface UseItemsTableKeyboardNavArgs {
  items: TypedItem[];
  onNavigate: (item: TypedItem) => void;
}

interface CellPosition {
  rowIndex: number;
  colIndex: number;
}

const ARROW_DELTAS: Record<string, { rowDelta: number; colDelta: number }> = {
  ArrowDown: { rowDelta: 1, colDelta: 0 },
  ArrowLeft: { rowDelta: 0, colDelta: -1 },
  ArrowRight: { rowDelta: 0, colDelta: 1 },
  ArrowUp: { rowDelta: -1, colDelta: 0 },
};

function readCellPosition(target: HTMLElement): CellPosition | undefined {
  const rowAttr = target.dataset['rowIndex'];
  const colAttr = target.dataset['colIndex'];
  if (rowAttr === undefined || colAttr === undefined) {
    return undefined;
  }

  const rowIndex = Number.parseInt(rowAttr, 10);
  const colIndex = Number.parseInt(colAttr, 10);
  if (Number.isNaN(rowIndex) || Number.isNaN(colIndex)) {
    return undefined;
  }

  return { colIndex, rowIndex };
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function getNextCellPosition({
  key,
  ctrlKey,
  rowIndex,
  colIndex,
  maxRow,
  maxCol,
}: {
  key: string;
  ctrlKey: boolean;
  rowIndex: number;
  colIndex: number;
  maxRow: number;
  maxCol: number;
}): CellPosition | undefined {
  const arrowDelta = ARROW_DELTAS[key];
  if (arrowDelta !== undefined) {
    return {
      colIndex: clamp(colIndex + arrowDelta.colDelta, 0, maxCol),
      rowIndex: clamp(rowIndex + arrowDelta.rowDelta, 0, maxRow),
    };
  }

  if (key === 'Home') {
    return { colIndex: 0, rowIndex: ctrlKey ? 0 : rowIndex };
  }
  if (key === 'End') {
    return { colIndex: maxCol, rowIndex: ctrlKey ? maxRow : rowIndex };
  }

  if (key === 'PageDown') {
    return {
      colIndex,
      rowIndex: clamp(rowIndex + itemsTableConstants.KEYBOARD_PAGE_OFFSET, 0, maxRow),
    };
  }
  if (key === 'PageUp') {
    return {
      colIndex,
      rowIndex: clamp(rowIndex - itemsTableConstants.KEYBOARD_PAGE_OFFSET, 0, maxRow),
    };
  }

  return undefined;
}

function useItemsTableKeyboardNav({
  items,
  onNavigate,
}: UseItemsTableKeyboardNavArgs): (event: React.KeyboardEvent<HTMLElement>) => void {
  return (event: React.KeyboardEvent<HTMLElement>): void => {
    if (event.target !== event.currentTarget) {
      return;
    }

    const position = readCellPosition(event.currentTarget);
    if (position === undefined) {
      return;
    }

    const maxRow = Math.max(items.length - itemsTableConstants.ROW_INDEX_OFFSET, 0);
    const maxCol = itemsTableConstants.MAX_COL_INDEX;

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      const item = items[position.rowIndex];
      if (item !== undefined) {
        onNavigate(item);
      }
      return;
    }

    const nextPosition = getNextCellPosition({
      colIndex: position.colIndex,
      ctrlKey: event.ctrlKey,
      key: event.key,
      maxCol,
      maxRow,
      rowIndex: position.rowIndex,
    });
    if (nextPosition === undefined) {
      return;
    }

    event.preventDefault();
    const selector = `[data-row-index="${nextPosition.rowIndex}"][data-col-index="${nextPosition.colIndex}"]`;
    const next = document.querySelector(selector);
    if (next instanceof HTMLElement) {
      next.focus();
    }
  };
}

export { useItemsTableKeyboardNav };
export type { UseItemsTableKeyboardNavArgs };
