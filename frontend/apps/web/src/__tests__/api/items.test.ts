/**
 * Tests for Items API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  createItem,
  deleteItem,
  fetchItem,
  fetchItems,
  fetchRecentItems,
  updateItem,
} from '@/api/items';

// Mock endpoints
vi.mock('@/api/endpoints', () => ({
  itemsApi: {
    create: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
    list: vi.fn(),
    update: vi.fn(),
  },
}));

import { itemsApi } from '@/api/endpoints';

import { mockItems } from '../mocks/data';

describe('Items API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchItems, () => {
    it('should fetch items', async () => {
      vi.mocked(itemsApi.list).mockResolvedValue(mockItems);

      const result = await fetchItems();
      expect(result).toEqual(mockItems);
      // List can be called with no args (optional parameter)
      expect(itemsApi.list).toHaveBeenCalled();
    });

    it('should fetch items with params', async () => {
      vi.mocked(itemsApi.list).mockResolvedValue(mockItems);

      const result = await fetchItems({ limit: 10, project_id: 'proj-1' });
      expect(result).toEqual(mockItems);
      expect(itemsApi.list).toHaveBeenCalledWith({
        limit: 10,
        project_id: 'proj-1',
      });
    });
  });

  describe(fetchItem, () => {
    it('should fetch a single item', async () => {
      vi.mocked(itemsApi.get).mockResolvedValue(mockItems[0]);

      const result = await fetchItem('item-1');
      expect(result).toEqual(mockItems[0]);
      expect(itemsApi.get).toHaveBeenCalledWith('item-1');
    });
  });

  describe(fetchRecentItems, () => {
    it('should fetch recent items (first 10)', async () => {
      const manyItems = Array.from({ length: 20 }, (_, i) => ({
        ...mockItems[0],
        id: `item-${i}`,
      }));
      vi.mocked(itemsApi.list).mockResolvedValue(manyItems);

      const result = await fetchRecentItems();
      expect(result).toHaveLength(10);
      expect(itemsApi.list).toHaveBeenCalledWith({ limit: 10 });
    });

    it('should handle fewer than 10 items', async () => {
      const fewItems = mockItems.slice(0, 3);
      vi.mocked(itemsApi.list).mockResolvedValue(fewItems);

      const result = await fetchRecentItems();
      expect(result).toHaveLength(3);
      expect(result).toEqual(fewItems);
    });
  });

  describe(createItem, () => {
    it('should create an item', async () => {
      const newItem = {
        project_id: 'proj-1',
        status: 'pending' as const,
        title: 'New Item',
        type: 'feature' as const,
      };
      const created = { ...mockItems[0], ...newItem, id: 'new-id' };
      vi.mocked(itemsApi.create).mockResolvedValue(created);

      const result = await createItem(newItem);
      expect(result).toEqual(created);
      expect(itemsApi.create).toHaveBeenCalledWith(newItem);
    });
  });

  describe(updateItem, () => {
    it('should update an item', async () => {
      const updates = { title: 'Updated Item' };
      const updated = { ...mockItems[0], ...updates };
      vi.mocked(itemsApi.update).mockResolvedValue(updated);

      const result = await updateItem('item-1', updates);
      expect(result).toEqual(updated);
      expect(itemsApi.update).toHaveBeenCalledWith('item-1', updates);
    });
  });

  describe(deleteItem, () => {
    it('should delete an item', async () => {
      vi.mocked(itemsApi.delete).mockResolvedValue();

      await expect(deleteItem('item-1')).resolves.toBeUndefined();
      expect(itemsApi.delete).toHaveBeenCalledWith('item-1');
    });
  });
});
