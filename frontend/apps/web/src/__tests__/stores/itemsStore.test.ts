/**
 * Tests for itemsStore
 */

import { beforeEach, describe, expect, it } from 'vitest';

import type { Item, ItemStatus, Priority, ViewType } from '@tracertm/types';

import { useItemsStore } from '../../stores/items-store';

const createMockItem = (overrides: Partial<Item> = {}): Item => ({
  createdAt: new Date().toISOString(),
  description: 'Test item',
  id: 'item-1',
  priority: 'medium' as Priority,
  projectId: 'proj-1',
  status: 'todo' as ItemStatus,
  title: 'Test item',
  type: 'feature',
  updatedAt: new Date().toISOString(),
  version: 1,
  view: 'FEATURE' as ViewType,
  ...overrides,
});

describe('itemsStore', () => {
  beforeEach(() => {
    // Reset store state
    useItemsStore.setState({
      isLoading: false,
      items: new Map(),
      itemsByProject: new Map(),
      loadingItems: new Set(),
      pendingCreates: new Map(),
      pendingDeletes: new Set(),
      pendingUpdates: new Map(),
    });
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = useItemsStore.getState();

      expect(state.items.size).toBe(0);
      expect(state.itemsByProject.size).toBe(0);
      expect(state.isLoading).toBeFalsy();
      expect(state.loadingItems.size).toBe(0);
      expect(state.pendingCreates.size).toBe(0);
      expect(state.pendingUpdates.size).toBe(0);
      expect(state.pendingDeletes.size).toBe(0);
    });
  });

  describe('addItem', () => {
    it('should add an item to the store', () => {
      const item = createMockItem({ id: 'item-1', projectId: 'proj-1' });

      useItemsStore.getState().addItem(item);

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')).toEqual(item);
      expect(state.itemsByProject.get('proj-1')).toContain('item-1');
    });

    it('should not duplicate items in project index', () => {
      const item = createMockItem({ id: 'item-1', projectId: 'proj-1' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().addItem(item);

      const state = useItemsStore.getState();
      const projectItems = state.itemsByProject.get('proj-1');
      expect(projectItems?.filter((id) => id === 'item-1').length).toBe(1);
    });
  });

  describe('addItems', () => {
    it('should add multiple items', () => {
      const items = [
        createMockItem({ id: 'item-1', projectId: 'proj-1' }),
        createMockItem({ id: 'item-2', projectId: 'proj-1' }),
      ];

      useItemsStore.getState().addItems(items);

      const state = useItemsStore.getState();
      expect(state.items.size).toBe(2);
      expect(state.itemsByProject.get('proj-1')?.length).toBe(2);
    });
  });

  describe('updateItem', () => {
    it('should update an item', () => {
      const item = createMockItem({ id: 'item-1', title: 'Original' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().updateItem('item-1', { title: 'Updated' });

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')?.title).toBe('Updated');
    });

    it('should not update non-existent item', () => {
      useItemsStore.getState().updateItem('non-existent', { title: 'Updated' });

      const state = useItemsStore.getState();
      expect(state.items.get('non-existent')).toBeUndefined();
    });
  });

  describe('removeItem', () => {
    it('should remove an item', () => {
      const item = createMockItem({ id: 'item-1', projectId: 'proj-1' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().removeItem('item-1');

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')).toBeUndefined();
      expect(state.itemsByProject.get('proj-1')).not.toContain('item-1');
    });
  });

  describe('getItem', () => {
    it('should retrieve an item by id', () => {
      const item = createMockItem({ id: 'item-1' });

      useItemsStore.getState().addItem(item);

      const retrieved = useItemsStore.getState().getItem('item-1');
      expect(retrieved).toEqual(item);
    });
  });

  describe('getItemsByProject', () => {
    it('should retrieve items by project id', () => {
      const items = [
        createMockItem({ id: 'item-1', projectId: 'proj-1' }),
        createMockItem({ id: 'item-2', projectId: 'proj-1' }),
        createMockItem({ id: 'item-3', projectId: 'proj-2' }),
      ];

      useItemsStore.getState().addItems(items);

      const projectItems = useItemsStore.getState().getItemsByProject('proj-1');
      expect(projectItems.length).toBe(2);
      expect(projectItems.map((i) => i.id)).toContain('item-1');
      expect(projectItems.map((i) => i.id)).toContain('item-2');
    });
  });

  describe('optimistic creates', () => {
    it('should optimistically create an item', () => {
      const data = {
        projectId: 'proj-1',
        title: 'New Item',
        type: 'feature',
      };

      useItemsStore.getState().optimisticCreate('temp-1', data);

      const state = useItemsStore.getState();
      expect(state.items.get('temp-1')).toBeTruthy();
      expect(state.pendingCreates.get('temp-1')).toEqual(data);
    });

    it('should confirm optimistic create', () => {
      const data = {
        projectId: 'proj-1',
        title: 'New Item',
        type: 'feature',
      };
      const realItem = createMockItem({ id: 'real-1', ...data });

      useItemsStore.getState().optimisticCreate('temp-1', data);
      useItemsStore.getState().confirmCreate('temp-1', realItem);

      const state = useItemsStore.getState();
      expect(state.items.get('temp-1')).toBeUndefined();
      expect(state.items.get('real-1')).toEqual(realItem);
      expect(state.pendingCreates.get('temp-1')).toBeUndefined();
    });

    it('should rollback optimistic create', () => {
      const data = {
        projectId: 'proj-1',
        title: 'New Item',
        type: 'feature',
      };

      useItemsStore.getState().optimisticCreate('temp-1', data);
      useItemsStore.getState().rollbackCreate('temp-1');

      const state = useItemsStore.getState();
      expect(state.items.get('temp-1')).toBeUndefined();
      expect(state.pendingCreates.get('temp-1')).toBeUndefined();
    });
  });

  describe('optimistic updates', () => {
    it('should optimistically update an item', () => {
      const item = createMockItem({ id: 'item-1', title: 'Original' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().optimisticUpdate('item-1', { title: 'Updated' });

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')?.title).toBe('Updated');
      expect(state.pendingUpdates.get('item-1')).toEqual({
        title: 'Updated',
      });
    });

    it('should confirm optimistic update', () => {
      const item = createMockItem({ id: 'item-1', title: 'Original' });
      const updated = createMockItem({ id: 'item-1', title: 'Updated' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().optimisticUpdate('item-1', { title: 'Updated' });
      useItemsStore.getState().confirmUpdate('item-1', updated);

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')).toEqual(updated);
      expect(state.pendingUpdates.get('item-1')).toBeUndefined();
    });
  });

  describe('optimistic deletes', () => {
    it('should optimistically delete an item', () => {
      const item = createMockItem({ id: 'item-1', projectId: 'proj-1' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().optimisticDelete('item-1');

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')).toBeUndefined();
      expect(state.pendingDeletes.has('item-1')).toBeTruthy();
    });

    it('should confirm optimistic delete', () => {
      const item = createMockItem({ id: 'item-1' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().optimisticDelete('item-1');
      useItemsStore.getState().confirmDelete('item-1');

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')).toBeUndefined();
      expect(state.pendingDeletes.has('item-1')).toBeFalsy();
    });

    it('should rollback optimistic delete', () => {
      const item = createMockItem({ id: 'item-1', projectId: 'proj-1' });

      useItemsStore.getState().addItem(item);
      useItemsStore.getState().optimisticDelete('item-1');
      useItemsStore.getState().rollbackDelete('item-1', item);

      const state = useItemsStore.getState();
      expect(state.items.get('item-1')).toEqual(item);
      expect(state.pendingDeletes.has('item-1')).toBeFalsy();
    });
  });

  describe('loading states', () => {
    it('should set global loading state', () => {
      useItemsStore.getState().setLoading(true);

      let state = useItemsStore.getState();
      expect(state.isLoading).toBeTruthy();

      useItemsStore.getState().setLoading(false);

      state = useItemsStore.getState();
      expect(state.isLoading).toBeFalsy();
    });

    it('should set item-specific loading state', () => {
      useItemsStore.getState().setItemLoading('item-1', true);

      let state = useItemsStore.getState();
      expect(state.loadingItems.has('item-1')).toBeTruthy();

      useItemsStore.getState().setItemLoading('item-1', false);

      state = useItemsStore.getState();
      expect(state.loadingItems.has('item-1')).toBeFalsy();
    });
  });
});
