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
  deleteItem: (id: string, onSuccess: () => void) => void;
  saveItem: (payload: SavePayload, onSuccess: () => void) => void;
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
    (id: string, onSuccess: () => void): void => {
      deleteItemMutation.mutate(id, {
        onError: () => {
          toast.error('Failed to delete item');
        },
        onSuccess: () => {
          toast.success('Item deleted successfully');
          onSuccess();
        },
      });
    },
    [deleteItemMutation],
  );

  const saveItem = useCallback(
    (payload: SavePayload, onSuccess: () => void): void => {
      if (!item) {
        toast.error('Failed to update item');
        return;
      }

      updateItemMutation.mutate(
        {
          id: payload.id,
          data: {
            title: payload.title,
            description: payload.description,
            owner: normalizeOwner(payload.owner),
            status: payload.status,
            priority: payload.priority,
          },
        },
        {
          onError: () => {
            toast.error('Failed to update item');
          },
          onSuccess: () => {
            toast.success('Item updated');
            onSuccess();
          },
        },
      );
    },
    [item, updateItemMutation],
  );

  return { deleteItem, saveItem };
}

export type { ItemMutations, SavePayload };
