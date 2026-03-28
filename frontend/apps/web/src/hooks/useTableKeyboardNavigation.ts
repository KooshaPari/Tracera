import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Accessible Table Keyboard Navigation Hook
 *
 * Implements WCAG 2.1 Level AA keyboard navigation for tables:
 * - Arrow keys: Navigate between cells
 * - Home/End: Jump to first/last column in row
 * - Ctrl+Home/End: Jump to first/last row
 * - Tab: Move focus out of table
 * - Roving tabindex pattern for efficient focus management
 */

interface UseTableKeyboardNavigationProps {
  rowCount: number;
  colCount: number;
  onNavigate?: ((rowIndex: number, colIndex: number) => void) | undefined;
  containerId?: string | undefined;
}

interface FocusState {
  rowIndex: number;
  colIndex: number;
}

export function useTableKeyboardNavigation({
  rowCount,
  colCount,
  onNavigate,
  containerId,
}: UseTableKeyboardNavigationProps) {
  const [focusState, setFocusState] = useState<FocusState>({
    colIndex: 0,
    rowIndex: 0,
  });
  const containerRef = useRef<HTMLDivElement>(null);

  // Get focusable element at given coordinates
  const getFocusableElement = useCallback(
    (rowIdx: number, colIdx: number): HTMLElement | null => {
      if (containerId) {
        const container = document.querySelector(`#${containerId}`);
        if (!container) {
          return null;
        }

        const row = container.querySelector(`[data-row-index="${rowIdx}"]`);
        if (!row) {
          return null;
        }

        const cell = row.querySelector(`[data-col-index="${colIdx}"]`);
        if (!cell) {
          return null;
        }

        // Find focusable element within cell
        const focusable = cell.querySelector<HTMLElement>(
          "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])",
        );

        return (focusable ?? cell) as HTMLElement;
      }

      return null;
    },
    [containerId],
  );

  // Handle keyboard events
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const { key, ctrlKey, metaKey } = event;
      let newRowIndex = focusState.rowIndex;
      let newColIndex = focusState.colIndex;
      let shouldPreventDefault = false;

      const isMac = /Mac|iPhone|iPad|iPod/.test(navigator.platform);
      const isCtrlKey = isMac ? metaKey : ctrlKey;

      switch (key) {
        // Arrow Left: Move to previous column
        case 'ArrowLeft': {
          newColIndex = Math.max(0, focusState.colIndex - 1);
          shouldPreventDefault = true;
          break;
        }

        // Arrow Right: Move to next column
        case 'ArrowRight': {
          newColIndex = Math.min(colCount - 1, focusState.colIndex + 1);
          shouldPreventDefault = true;
          break;
        }

        // Arrow Up: Move to previous row
        case 'ArrowUp': {
          newRowIndex = Math.max(0, focusState.rowIndex - 1);
          shouldPreventDefault = true;
          break;
        }

        // Arrow Down: Move to next row
        case 'ArrowDown': {
          newRowIndex = Math.min(rowCount - 1, focusState.rowIndex + 1);
          shouldPreventDefault = true;
          break;
        }

        // Home: Jump to first column in row
        case 'Home': {
          if (!isCtrlKey) {
            newColIndex = 0;
            shouldPreventDefault = true;
          } else {
            // Ctrl+Home: Jump to first cell in table
            newRowIndex = 0;
            newColIndex = 0;
            shouldPreventDefault = true;
          }
          break;
        }

        // End: Jump to last column in row
        case 'End': {
          if (!isCtrlKey) {
            newColIndex = colCount - 1;
            shouldPreventDefault = true;
          } else {
            // Ctrl+End: Jump to last cell in table
            newRowIndex = rowCount - 1;
            newColIndex = colCount - 1;
            shouldPreventDefault = true;
          }
          break;
        }

        // PageUp: Jump up 5 rows
        case 'PageUp': {
          newRowIndex = Math.max(0, focusState.rowIndex - 5);
          shouldPreventDefault = true;
          break;
        }

        // PageDown: Jump down 5 rows
        case 'PageDown': {
          newRowIndex = Math.min(rowCount - 1, focusState.rowIndex + 5);
          shouldPreventDefault = true;
          break;
        }
      }

      if (shouldPreventDefault) {
        event.preventDefault();

        // Update focus state
        setFocusState({
          colIndex: newColIndex,
          rowIndex: newRowIndex,
        });

        // Call callback if provided
        if (onNavigate) {
          onNavigate(newRowIndex, newColIndex);
        }

        // Set focus to new element
        setTimeout(() => {
          const element = getFocusableElement(newRowIndex, newColIndex);
          if (element) {
            element.focus();
            // Announce to screen readers
            const announcement = `Navigated to row ${newRowIndex + 1}, column ${newColIndex + 1}`;
            announceToScreenReader(announcement);
          }
        }, 0);
      }
    },
    [focusState, rowCount, colCount, onNavigate, getFocusableElement],
  );

  // Setup event listeners
  useEffect(() => {
    const container = containerId
      ? (document.querySelector(`#${containerId}`) as HTMLElement | null)
      : containerRef.current;

    if (!container) {
      return;
    }

    container.addEventListener('keydown', handleKeyDown);

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }, [containerId, handleKeyDown]);

  return {
    containerRef,
    focusState,
    setFocusState,
  };
}

/**
 * Announce messages to screen readers using aria-live regions
 */
function announceToScreenReader(message: string) {
  // Get or create live region
  let liveRegion = document.querySelector('#table-announcements');
  if (!liveRegion) {
    liveRegion = document.createElement('div');
    liveRegion.id = 'table-announcements';
    liveRegion.setAttribute('role', 'status');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    document.body.append(liveRegion);
  }

  liveRegion.textContent = message;
}

/**
 * Roving Tabindex Hook
 * Manages focus for efficient keyboard navigation without tabindex spam
 */
export function useRovingTabindex(itemCount: number, onNavigate?: (index: number) => void) {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const itemsRef = useRef<(HTMLElement | null)[]>([]);

  // Set roving tabindex
  useEffect(() => {
    itemsRef.current.forEach((item, index) => {
      if (!item) {
        return;
      }
      item.tabIndex = index === focusedIndex ? 0 : -1;
    });
  }, [focusedIndex]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      let newIndex = focusedIndex;
      let handled = false;

      switch (event.key) {
        case 'ArrowDown':
        case 'ArrowRight': {
          newIndex = (focusedIndex + 1) % itemCount;
          handled = true;
          break;
        }
        case 'ArrowUp':
        case 'ArrowLeft': {
          newIndex = focusedIndex === 0 ? itemCount - 1 : focusedIndex - 1;
          handled = true;
          break;
        }
        case 'Home': {
          newIndex = 0;
          handled = true;
          break;
        }
        case 'End': {
          newIndex = itemCount - 1;
          handled = true;
          break;
        }
      }

      if (handled) {
        event.preventDefault();
        setFocusedIndex(newIndex);
        if (onNavigate) {
          onNavigate(newIndex);
        }

        // Focus the new item
        setTimeout(() => {
          itemsRef.current[newIndex]?.focus();
        }, 0);
      }
    },
    [focusedIndex, itemCount, onNavigate],
  );

  return {
    focusedIndex,
    handleKeyDown,
    itemsRef,
    setFocusedIndex,
  };
}
