import { useCallback } from 'react';
import { toast } from 'sonner';

import type { Item, ItemStatus, Priority } from '@tracertm/types';

import { useDeleteItem, useUpdateItem } from '@/hooks/useItems';

interface SavePayload {
  id: string;
  title: string;
  description: string;
  owner: string;
  status: ItemStatus;
  priority: Priority;
}

interface ItemMutations {
  deleteItem: (id: string) => Promise<void>;
  saveItem: (payload: SavePayload) => Promise<void>;
}

function normalizeOwner(owner: string): string | undefined {
  const trimmed = owner.trim();
  if (trimmed.length === 0) {
    return;
  }
  return trimmed;
}

export function useItemMutations(item: Item | undefined): ItemMutations {
  const deleteItemMutation = useDeleteItem();
  const updateItemMutation = useUpdateItem();

  const deleteItem = useCallback(
    async (id: string): Promise<void> => {
      await deleteItemMutation.mutateAsync(id);
      toast.success('Item deleted successfully');
    },
    [deleteItemMutation],
  );

  const saveItem = useCallback(
    async (payload: SavePayload): Promise<void> => {
      if (!item) {
        toast.error('Failed to update item');
        return;
      }

      await updateItemMutation.mutateAsync({
        id: payload.id,
        data: {
          title: payload.title,
          description: payload.description,
          owner: normalizeOwner(payload.owner),
          status: payload.status,
          priority: payload.priority,
        },
      });
      toast.success('Item updated');
    },
    [item, updateItemMutation],
  );

  return { deleteItem, saveItem };
}

export type { ItemMutations, SavePayload };
