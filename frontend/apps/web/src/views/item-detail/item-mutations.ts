import { useCallback } from "react";
import { toast } from "sonner";

import type { Item, ItemStatus, Priority } from "@tracertm/types";

import { useDeleteItem, useUpdateItem } from "@/hooks/useItems";

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

export function useItemMutations(item: Item | undefined): ItemMutations {
  const deleteItemMutation = useDeleteItem();
  const updateItemMutation = useUpdateItem();

  const deleteItem = useCallback(
    (id: string, onSuccess: () => void): void => {
      if (!item?.projectId) { toast.error("Select a project before deleting a node."); return; }
      deleteItemMutation.mutate({ id, projectId: item.projectId }, {
        onError: () => {
          toast.error("Failed to delete item");
        },
        onSuccess: () => {
          toast.success("Item deleted successfully");
          onSuccess();
        },
      });
    },
    [deleteItemMutation, item],
  );

  const saveItem = useCallback(
    (payload: SavePayload, onSuccess: () => void): void => {
      if (!item?.projectId) {
        toast.error("Failed to update item");
        return;
      }

      updateItemMutation.mutate(
        {
          id: payload.id,
          projectId: item.projectId,
          data: {
            title: payload.title,
            description: payload.description,

            status: payload.status,

          },
        },
        {
          onError: () => {
            toast.error("Failed to update item");
          },
          onSuccess: () => {
            toast.success("Item updated");
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
