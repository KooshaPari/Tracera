import { useCallback, useState } from 'react';

export interface UseBulkSelectionResult {
  selected: Set<string>;
  selectedIds: string[];
  isSelected: (id: string) => boolean;
  toggle: (id: string) => void;
  selectAll: (ids: string[]) => void;
  deselectAll: () => void;
  count: number;
  hasSelection: boolean;
  clear: () => void;
}

export function useBulkSelection(): UseBulkSelectionResult {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const isSelected = useCallback((id: string) => selected.has(id), [selected]);

  const toggle = useCallback((id: string) => {
    setSelected((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  }, []);

  const selectAll = useCallback((ids: string[]) => {
    setSelected(new Set(ids));
  }, []);

  const deselectAll = useCallback(() => {
    setSelected(new Set());
  }, []);

  const clear = useCallback(() => {
    setSelected(new Set());
  }, []);

  return {
    clear,
    count: selected.size,
    deselectAll,
    hasSelection: selected.size > 0,
    isSelected,
    selectAll,
    selected,
    selectedIds: [...selected],
    toggle,
  };
}
