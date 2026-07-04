/**
 * Comprehensive tests for items store
 * Tests all CRUD operations, optimistic updates, and state management
 */

import { beforeEach, describe, expect, it } from 'vitest';

import type { CreateItemInput, Item, UpdateItemInput } from '../../api/types';

import { useItemsStore } from '../../stores/items-store';

describe('ItemsStore', () => {
  beforeEach(() => {
    // Reset store before each test
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

  const mockItem: Item = {
    createdAt: '2024-01-01T00:00:00Z',
    description: 'Test description',
    id: 'item-1',
    priority: 'high',
    projectId: 'proj-1',
    status: 'todo',
    title: 'Test Feature',
    type: 'feature',
    updatedAt: '2024-01-01T00:00:00Z',
    version: 1,
    view: 'FEATURE',
  };

  const mockItem2: Item = {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'item-2',
    priority: 'medium',
    projectId: 'proj-1',
    status: 'in_progress',
    title: 'Test Task',
    type: 'task',
    updatedAt: '2024-01-01T00:00:00Z',
    version: 1,
    view: 'FEATURE',
  };

  const mockItem3: Item = {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'item-3',
    priority: 'low',
    projectId: 'proj-2',
    status: 'done',
    title: 'Test Bug',
    type: 'bug',
    updatedAt: '2024-01-01T00:00:00Z',
    version: 1,
    view: 'FEATURE',
  };

  describe('addItem', () => {
    it('should add item to store', () => {
      const { addItem } = useItemsStore.getState();
      addItem(mockItem);

      const { items } = useItemsStore.getState();
      expect(items.get('item-1')).toEqual(mockItem);
    });

    it('should update itemsByProject index', () => {
      const { addItem } = useItemsStore.getState();
      addItem(mockItem);

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).toContain('item-1');
    });

    it('should handle multiple items for same project', () => {
      const { addItem } = useItemsStore.getState();
      addItem(mockItem);
      addItem(mockItem2);

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).toHaveLength(2);
      expect(projectItems).toContain('item-1');
      expect(projectItems).toContain('item-2');
    });

    it('should not duplicate items in project index', () => {
      const { addItem } = useItemsStore.getState();
      addItem(mockItem);
      addItem(mockItem); // Add same item again

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).toHaveLength(1);
    });

    it('should handle items from different projects', () => {
      const { addItem } = useItemsStore.getState();
      addItem(mockItem);
      addItem(mockItem3);

      const { itemsByProject } = useItemsStore.getState();
      expect(itemsByProject.get('proj-1')).toHaveLength(1);
      expect(itemsByProject.get('proj-2')).toHaveLength(1);
    });
  });

  describe('addItems', () => {
    it('should add multiple items', () => {
      const { addItems } = useItemsStore.getState();
      addItems([mockItem, mockItem2, mockItem3]);

      const { items } = useItemsStore.getState();
      expect(items.size).toBe(3);
      expect(items.get('item-1')).toEqual(mockItem);
      expect(items.get('item-2')).toEqual(mockItem2);
      expect(items.get('item-3')).toEqual(mockItem3);
    });

    it('should update all project indices', () => {
      const { addItems } = useItemsStore.getState();
      addItems([mockItem, mockItem2, mockItem3]);

      const { itemsByProject } = useItemsStore.getState();
      expect(itemsByProject.get('proj-1')).toHaveLength(2);
      expect(itemsByProject.get('proj-2')).toHaveLength(1);
    });

    it('should handle empty array', () => {
      const { addItems } = useItemsStore.getState();
      addItems([]);

      const { items } = useItemsStore.getState();
      expect(items.size).toBe(0);
    });
  });

  describe('updateItem', () => {
    it('should update existing item', () => {
      const { addItem, updateItem } = useItemsStore.getState();
      addItem(mockItem);
      updateItem('item-1', { title: 'Updated Title' });

      const { items } = useItemsStore.getState();
      const updated = items.get('item-1');
      expect(updated?.title).toBe('Updated Title');
    });

    it('should preserve unchanged fields', () => {
      const { addItem, updateItem } = useItemsStore.getState();
      addItem(mockItem);
      updateItem('item-1', { title: 'Updated Title' });

      const { items } = useItemsStore.getState();
      const updated = items.get('item-1');
      expect(updated?.status).toBe('todo');
      expect(updated?.priority).toBe('high');
    });

    it('should handle non-existent item gracefully', () => {
      const { updateItem } = useItemsStore.getState();
      updateItem('nonexistent', { title: 'Test' });

      const { items } = useItemsStore.getState();
      expect(items.get('nonexistent')).toBeUndefined();
    });

    it('should update multiple fields', () => {
      const { addItem, updateItem } = useItemsStore.getState();
      addItem(mockItem);
      updateItem('item-1', {
        priority: 'low',
        status: 'done',
        title: 'New Title',
      });

      const { items } = useItemsStore.getState();
      const updated = items.get('item-1');
      expect(updated?.title).toBe('New Title');
      expect(updated?.status).toBe('done');
      expect(updated?.priority).toBe('low');
    });
  });

  describe('removeItem', () => {
    it('should remove item from store', () => {
      const { addItem, removeItem } = useItemsStore.getState();
      addItem(mockItem);
      removeItem('item-1');

      const { items } = useItemsStore.getState();
      expect(items.get('item-1')).toBeUndefined();
    });

    it('should remove item from project index', () => {
      const { addItem, removeItem } = useItemsStore.getState();
      addItem(mockItem);
      removeItem('item-1');

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).toBeDefined();
      expect(projectItems).toEqual([]);
    });

    it('should handle non-existent item gracefully', () => {
      const { removeItem } = useItemsStore.getState();
      const sizeBefore = useItemsStore.getState().items.size;
      removeItem('nonexistent');

      const { items } = useItemsStore.getState();
      expect(items.size).toBe(sizeBefore);
    });

    it('should only remove specified item from project', () => {
      const { addItem, removeItem } = useItemsStore.getState();
      addItem(mockItem);
      addItem(mockItem2);
      removeItem('item-1');

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).toHaveLength(1);
      expect(projectItems).toContain('item-2');
    });
  });

  describe('getItem', () => {
    it('should retrieve item by ID', () => {
      const { addItem, getItem } = useItemsStore.getState();
      addItem(mockItem);

      const retrieved = getItem('item-1');
      expect(retrieved).toEqual(mockItem);
    });

    it('should return undefined for non-existent item', () => {
      const { getItem } = useItemsStore.getState();
      const retrieved = getItem('nonexistent');

      expect(retrieved).toBeUndefined();
    });
  });

  describe('getItemsByProject', () => {
    it('should retrieve all items for project', () => {
      const { addItem, getItemsByProject } = useItemsStore.getState();
      addItem(mockItem);
      addItem(mockItem2);

      const projectItems = getItemsByProject('proj-1');
      expect(projectItems).toHaveLength(2);
    });

    it('should return empty array for project with no items', () => {
      const { getItemsByProject } = useItemsStore.getState();
      const projectItems = getItemsByProject('nonexistent');

      expect(projectItems).toEqual([]);
    });

    it('should filter items by project', () => {
      const { addItem, getItemsByProject } = useItemsStore.getState();
      addItem(mockItem);
      addItem(mockItem3);

      const proj1Items = getItemsByProject('proj-1');
      const proj2Items = getItemsByProject('proj-2');

      expect(proj1Items).toHaveLength(1);
      expect(proj2Items).toHaveLength(1);
      expect(proj1Items[0]?.id).toBe('item-1');
      expect(proj2Items[0]?.id).toBe('item-3');
    });
  });

  describe('clearItems', () => {
    it('should clear all items', () => {
      const { addItem, clearItems } = useItemsStore.getState();
      addItem(mockItem);
      addItem(mockItem2);
      clearItems();

      const { items } = useItemsStore.getState();
      expect(items.size).toBe(0);
    });

    it('should clear project indices', () => {
      const { addItem, clearItems } = useItemsStore.getState();
      addItem(mockItem);
      clearItems();

      const { itemsByProject } = useItemsStore.getState();
      expect(itemsByProject.size).toBe(0);
    });
  });

  describe('optimisticCreate', () => {
    const createData: CreateItemInput = {
      description: 'Description',
      priority: 'high',
      projectId: 'proj-1',
      status: 'todo',
      title: 'New Feature',
      type: 'feature',
    };

    it('should add temporary item', () => {
      const { optimisticCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);

      const { items } = useItemsStore.getState();
      const tempItem = items.get('temp-1');
      expect(tempItem).toBeDefined();
      expect(tempItem?.title).toBe('New Feature');
    });

    it('should track pending create', () => {
      const { optimisticCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);

      const { pendingCreates } = useItemsStore.getState();
      expect(pendingCreates.get('temp-1')).toEqual(createData);
    });

    it('should set default status if not provided', () => {
      const { optimisticCreate } = useItemsStore.getState();
      const { status: _status, ...dataWithoutStatus } = createData;
      optimisticCreate('temp-1', dataWithoutStatus);

      const { items } = useItemsStore.getState();
      const tempItem = items.get('temp-1');
      expect(tempItem?.status).toBe('todo');
    });

    it('should add to project index', () => {
      const { optimisticCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).toContain('temp-1');
    });
  });

  describe('confirmCreate', () => {
    const createData: CreateItemInput = {
      priority: 'high',
      projectId: 'proj-1',
      status: 'todo',
      title: 'New Feature',
      type: 'feature',
    };

    it('should replace temporary item with real item', () => {
      const { optimisticCreate, confirmCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);
      confirmCreate('temp-1', mockItem);

      const { items } = useItemsStore.getState();
      expect(items.get('temp-1')).toBeUndefined();
      expect(items.get('item-1')).toEqual(mockItem);
    });

    it('should clear pending create', () => {
      const { optimisticCreate, confirmCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);
      confirmCreate('temp-1', mockItem);

      const { pendingCreates } = useItemsStore.getState();
      expect(pendingCreates.get('temp-1')).toBeUndefined();
    });

    it('should update project index', () => {
      const { optimisticCreate, confirmCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);
      confirmCreate('temp-1', mockItem);

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).not.toContain('temp-1');
      expect(projectItems).toContain('item-1');
    });
  });

  describe('rollbackCreate', () => {
    const createData: CreateItemInput = {
      priority: 'high',
      projectId: 'proj-1',
      status: 'todo',
      title: 'New Feature',
      type: 'feature',
    };

    it('should remove temporary item', () => {
      const { optimisticCreate, rollbackCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);
      rollbackCreate('temp-1');

      const { items } = useItemsStore.getState();
      expect(items.get('temp-1')).toBeUndefined();
    });

    it('should clear pending create', () => {
      const { optimisticCreate, rollbackCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);
      rollbackCreate('temp-1');

      const { pendingCreates } = useItemsStore.getState();
      expect(pendingCreates.get('temp-1')).toBeUndefined();
    });

    it('should remove from project index', () => {
      const { optimisticCreate, rollbackCreate } = useItemsStore.getState();
      optimisticCreate('temp-1', createData);
      rollbackCreate('temp-1');

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).not.toContain('temp-1');
    });
  });

  describe('optimisticUpdate', () => {
    const updates: UpdateItemInput = {
      status: 'done',
      title: 'Updated Title',
    };

    it('should update item immediately', () => {
      const { addItem, optimisticUpdate } = useItemsStore.getState();
      addItem(mockItem);
      optimisticUpdate('item-1', updates);

      const { items } = useItemsStore.getState();
      const updated = items.get('item-1');
      expect(updated?.title).toBe('Updated Title');
      expect(updated?.status).toBe('done');
    });

    it('should track pending update', () => {
      const { addItem, optimisticUpdate } = useItemsStore.getState();
      addItem(mockItem);
      optimisticUpdate('item-1', updates);

      const { pendingUpdates } = useItemsStore.getState();
      expect(pendingUpdates.get('item-1')).toEqual(updates);
    });

    it('should handle non-existent item gracefully', () => {
      const { optimisticUpdate } = useItemsStore.getState();
      optimisticUpdate('nonexistent', updates);

      const { items } = useItemsStore.getState();
      expect(items.get('nonexistent')).toBeUndefined();
    });
  });

  describe('confirmUpdate', () => {
    const updates: UpdateItemInput = {
      title: 'Updated Title',
    };

    it('should replace item with server response', () => {
      const { addItem, optimisticUpdate, confirmUpdate } = useItemsStore.getState();
      addItem(mockItem);
      optimisticUpdate('item-1', updates);

      const serverItem = {
        ...mockItem,
        title: 'Server Title',
        updated_at: '2024-01-02T00:00:00Z',
      };
      confirmUpdate('item-1', serverItem);

      const { items } = useItemsStore.getState();
      expect(items.get('item-1')).toEqual(serverItem);
    });

    it('should clear pending update', () => {
      const { addItem, optimisticUpdate, confirmUpdate } = useItemsStore.getState();
      addItem(mockItem);
      optimisticUpdate('item-1', updates);
      confirmUpdate('item-1', mockItem);

      const { pendingUpdates } = useItemsStore.getState();
      expect(pendingUpdates.get('item-1')).toBeUndefined();
    });
  });

  describe('rollbackUpdate', () => {
    const updates: UpdateItemInput = {
      title: 'Updated Title',
    };

    it('should clear pending update', () => {
      const { addItem, optimisticUpdate, rollbackUpdate } = useItemsStore.getState();
      addItem(mockItem);
      optimisticUpdate('item-1', updates);
      rollbackUpdate('item-1');

      const { pendingUpdates } = useItemsStore.getState();
      expect(pendingUpdates.get('item-1')).toBeUndefined();
    });

    it('should handle non-existent pending update', () => {
      const { rollbackUpdate } = useItemsStore.getState();
      rollbackUpdate('item-1');

      const { pendingUpdates } = useItemsStore.getState();
      expect(pendingUpdates.size).toBe(0);
    });
  });

  describe('optimisticDelete', () => {
    it('should remove item immediately', () => {
      const { addItem, optimisticDelete } = useItemsStore.getState();
      addItem(mockItem);
      optimisticDelete('item-1');

      const { items } = useItemsStore.getState();
      expect(items.get('item-1')).toBeUndefined();
    });

    it('should track pending delete', () => {
      const { addItem, optimisticDelete } = useItemsStore.getState();
      addItem(mockItem);
      optimisticDelete('item-1');

      const { pendingDeletes } = useItemsStore.getState();
      expect(pendingDeletes.has('item-1')).toBeTruthy();
    });

    it('should handle non-existent item gracefully', () => {
      const { optimisticDelete } = useItemsStore.getState();
      const sizeBefore = useItemsStore.getState().items.size;
      optimisticDelete('nonexistent');

      const { items } = useItemsStore.getState();
      expect(items.size).toBe(sizeBefore);
    });
  });

  describe('confirmDelete', () => {
    it('should clear pending delete', () => {
      const { addItem, optimisticDelete, confirmDelete } = useItemsStore.getState();
      addItem(mockItem);
      optimisticDelete('item-1');
      confirmDelete('item-1');

      const { pendingDeletes } = useItemsStore.getState();
      expect(pendingDeletes.has('item-1')).toBeFalsy();
    });
  });

  describe('rollbackDelete', () => {
    it('should restore deleted item', () => {
      const { addItem, optimisticDelete, rollbackDelete } = useItemsStore.getState();
      addItem(mockItem);
      optimisticDelete('item-1');
      rollbackDelete('item-1', mockItem);

      const { items } = useItemsStore.getState();
      expect(items.get('item-1')).toEqual(mockItem);
    });

    it('should clear pending delete', () => {
      const { addItem, optimisticDelete, rollbackDelete } = useItemsStore.getState();
      addItem(mockItem);
      optimisticDelete('item-1');
      rollbackDelete('item-1', mockItem);

      const { pendingDeletes } = useItemsStore.getState();
      expect(pendingDeletes.has('item-1')).toBeFalsy();
    });

    it('should restore to project index', () => {
      const { addItem, optimisticDelete, rollbackDelete } = useItemsStore.getState();
      addItem(mockItem);
      optimisticDelete('item-1');
      rollbackDelete('item-1', mockItem);

      const { itemsByProject } = useItemsStore.getState();
      const projectItems = itemsByProject.get('proj-1');
      expect(projectItems).toContain('item-1');
    });
  });

  describe('loading states', () => {
    it('should set global loading state', () => {
      const { setLoading } = useItemsStore.getState();
      setLoading(true);

      expect(useItemsStore.getState().isLoading).toBeTruthy();

      setLoading(false);
      expect(useItemsStore.getState().isLoading).toBeFalsy();
    });

    it('should track individual item loading', () => {
      const { setItemLoading } = useItemsStore.getState();
      setItemLoading('item-1', true);

      const { loadingItems } = useItemsStore.getState();
      expect(loadingItems.has('item-1')).toBeTruthy();
    });

    it('should clear individual item loading', () => {
      const { setItemLoading } = useItemsStore.getState();
      setItemLoading('item-1', true);
      setItemLoading('item-1', false);

      const { loadingItems } = useItemsStore.getState();
      expect(loadingItems.has('item-1')).toBeFalsy();
    });

    it('should track multiple items loading', () => {
      const { setItemLoading } = useItemsStore.getState();
      setItemLoading('item-1', true);
      setItemLoading('item-2', true);

      const { loadingItems } = useItemsStore.getState();
      expect(loadingItems.size).toBe(2);
      expect(loadingItems.has('item-1')).toBeTruthy();
      expect(loadingItems.has('item-2')).toBeTruthy();
    });
  });
});
