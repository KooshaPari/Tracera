/**
 * Tests for uiStore
 */

import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';

import { useUIStore } from '../../stores/uiStore';

describe('uiStore', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('sidebar', () => {
    it('should toggle sidebar', () => {
      const { result } = renderHook(() => useUIStore());
      const initialState = result.current.sidebarOpen;

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarOpen).toBe(!initialState);
    });

    it('should set sidebar width', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setSidebarWidth(300);
      });

      expect(result.current.sidebarWidth).toBe(300);
    });
  });

  describe('theme', () => {
    it('should toggle dark mode', () => {
      const { result } = renderHook(() => useUIStore());
      const initial = result.current.isDarkMode;

      act(() => {
        result.current.toggleDarkMode();
      });

      expect(result.current.isDarkMode).toBe(!initial);
    });
  });

  describe('view and selection', () => {
    it('should set current view', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setCurrentView('TEST');
      });

      expect(result.current.currentView).toBe('TEST');
    });

    it('should select item', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.selectItem('item-1');
      });

      expect(result.current.selectedItemId).toBe('item-1');
    });

    it('should toggle item selection', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleItemSelection('item-1');
      });

      expect(result.current.selectedItemIds).toContain('item-1');

      act(() => {
        result.current.toggleItemSelection('item-1');
      });

      expect(result.current.selectedItemIds).not.toContain('item-1');
    });

    it('should clear selection', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.selectItem('item-1');
        result.current.toggleItemSelection('item-2');
        result.current.clearSelection();
      });

      expect(result.current.selectedItemId).toBeNull();
      expect(result.current.selectedItemIds).toEqual([]);
    });
  });

  describe('command palette', () => {
    it('should toggle command palette', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleCommandPalette();
      });

      expect(result.current.commandPaletteOpen).toBeTruthy();

      act(() => {
        result.current.toggleCommandPalette();
      });

      expect(result.current.commandPaletteOpen).toBeFalsy();
    });
  });

  describe('search', () => {
    it('should set search query', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setSearchQuery('test query');
      });

      expect(result.current.searchQuery).toBe('test query');
    });

    it('should toggle search', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleSearch();
      });

      expect(result.current.searchOpen).toBeTruthy();
    });
  });

  describe('filters', () => {
    it('should set status filter', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setStatusFilter(['open', 'in_progress']);
      });

      expect(result.current.statusFilter).toEqual(['open', 'in_progress']);
    });

    it('should set priority filter', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setPriorityFilter(['high', 'critical']);
      });

      expect(result.current.priorityFilter).toEqual(['high', 'critical']);
    });
  });

  describe('layout', () => {
    it('should set layout mode', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setLayoutMode('kanban');
      });

      expect(result.current.layoutMode).toBe('kanban');
    });

    it('should set grid columns', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setGridColumns(4);
      });

      expect(result.current.gridColumns).toBe(4);
    });
  });
});
