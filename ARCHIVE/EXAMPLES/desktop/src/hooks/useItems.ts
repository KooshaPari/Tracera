import { useState, useEffect, useCallback } from 'react';
import { itemApi, Item, ItemType } from '../lib/api';
import { listen } from '@tauri-apps/api/event';

export function useItems(projectId: string, itemType?: ItemType) {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadItems = useCallback(async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await itemApi.list(projectId, itemType);
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load items');
      console.error('Failed to load items:', err);
    } finally {
      setLoading(false);
    }
  }, [projectId, itemType]);

  useEffect(() => {
    loadItems();

    // Listen for sync events to refresh items
    const unlisten = listen('sync-completed', () => {
      loadItems();
    });

    return () => {
      unlisten.then(fn => fn());
    };
  }, [loadItems]);

  const createItem = useCallback(
    async (
      item_type: ItemType,
      title: string,
      content: string,
      status: string,
      priority?: string
    ) => {
      try {
        const item = await itemApi.create(projectId, item_type, title, content, status, priority);
        setItems(prev => [item, ...prev]);
        return item;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create item');
        throw err;
      }
    },
    [projectId]
  );

  const updateItem = useCallback(async (item: Item) => {
    try {
      await itemApi.update(item);
      setItems(prev =>
        prev.map(i => (i.id === item.id ? item : i))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update item');
      throw err;
    }
  }, []);

  const deleteItem = useCallback(async (id: string) => {
    try {
      await itemApi.delete(id);
      setItems(prev => prev.filter(i => i.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete item');
      throw err;
    }
  }, []);

  return {
    items,
    loading,
    error,
    loadItems,
    createItem,
    updateItem,
    deleteItem,
  };
}
