import { create } from 'zustand';

import type { Item, ItemStatus, Priority, ViewType } from '@tracertm/types';

interface CreateItemInput {
  projectId: string;
  type: string;
  title: string;
  description?: string | undefined;
  status?: ItemStatus | undefined;
  priority?: Priority | undefined;
  parentId?: string | undefined;
}

interface UpdateItemInput {
  type?: string | undefined;
  title?: string | undefined;
  description?: string | undefined;
  status?: ItemStatus | undefined;
  priority?: Priority | undefined;
  parentId?: string | undefined;
}

interface ItemsDataState {
  isLoading: boolean;
  items: Map<string, Item>;
  itemsByProject: Map<string, string[]>;
  loadingItems: Set<string>;
  pendingCreates: Map<string, CreateItemInput>;
  pendingDeletes: Set<string>;
  pendingUpdates: Map<string, UpdateItemInput>;
}

interface ItemsActions {
  addItem: (item: Item) => void;
  addItems: (items: Item[]) => void;
  clearItems: () => void;
  confirmCreate: (tempId: string, item: Item) => void;
  confirmDelete: (id: string) => void;
  confirmUpdate: (id: string, item: Item) => void;
  getItem: (id: string) => Item | undefined;
  getItemsByProject: (projectId: string) => Item[];
  optimisticCreate: (tempId: string, data: CreateItemInput) => void;
  optimisticDelete: (id: string) => void;
  optimisticUpdate: (id: string, updates: UpdateItemInput) => void;
  removeItem: (id: string) => void;
  removePendingMutation?: never;
  rollbackCreate: (tempId: string) => void;
  rollbackDelete: (id: string, item: Item) => void;
  rollbackUpdate: (id: string) => void;
  setItemLoading: (id: string, loading: boolean) => void;
  setLoading: (loading: boolean) => void;
  updateItem: (id: string, updates: Partial<Item>) => void;
}

type ItemsState = ItemsDataState & ItemsActions;

type StoreSetter = (
  partial: Partial<ItemsState> | ((state: ItemsState) => Partial<ItemsState> | ItemsState),
) => void;

type StoreGetter = () => ItemsState;

const DEFAULT_VIEW: ViewType = 'FEATURE';
const DEFAULT_STATUS: ItemStatus = 'todo';
const DEFAULT_PRIORITY: Priority = 'medium';

const createInitialState = (): ItemsDataState => ({
  isLoading: false,
  items: new Map(),
  itemsByProject: new Map(),
  loadingItems: new Set(),
  pendingCreates: new Map(),
  pendingDeletes: new Set(),
  pendingUpdates: new Map(),
});

const buildTempItem = (tempId: string, data: CreateItemInput): Item => {
  const { description } = data;
  const { parentId } = data;
  const now = new Date().toISOString();

  return {
    createdAt: now,
    ...(description !== undefined ? { description } : {}),
    id: tempId,
    ...(parentId !== undefined ? { parentId } : {}),
    priority: data.priority ?? DEFAULT_PRIORITY,
    projectId: data.projectId,
    status: data.status ?? DEFAULT_STATUS,
    title: data.title,
    type: data.type,
    updatedAt: now,
    version: 1,
    view: DEFAULT_VIEW,
  };
};

const createCollectionActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<ItemsActions, 'addItem' | 'addItems' | 'clearItems' | 'removeItem'> => ({
  addItem: (item) => {
    set((state) => {
      const newItems = new Map(state.items);
      newItems.set(item.id, item);

      const newItemsByProject = new Map(state.itemsByProject);
      const projectItems = newItemsByProject.get(item.projectId) ?? [];
      if (!projectItems.includes(item.id)) {
        newItemsByProject.set(item.projectId, [...projectItems, item.id]);
      }

      return {
        items: newItems,
        itemsByProject: newItemsByProject,
      };
    });
  },
  addItems: (items) => {
    items.forEach((item) => {
      get().addItem(item);
    });
  },
  clearItems: () => {
    set({
      items: new Map(),
      itemsByProject: new Map(),
    });
  },
  removeItem: (id) => {
    set((state) => {
      const item = state.items.get(id);
      if (!item) {
        return state;
      }

      const newItems = new Map(state.items);
      newItems.delete(id);

      const newItemsByProject = new Map(state.itemsByProject);
      const projectItems = newItemsByProject.get(item.projectId) ?? [];
      newItemsByProject.set(
        item.projectId,
        projectItems.filter((itemId) => itemId !== id),
      );

      return {
        items: newItems,
        itemsByProject: newItemsByProject,
      };
    });
  },
});

const createQueryActions = (
  get: StoreGetter,
): Pick<ItemsActions, 'getItem' | 'getItemsByProject'> => ({
  getItem: (id) => get().items.get(id),
  getItemsByProject: (projectId) => {
    const itemIds = get().itemsByProject.get(projectId) ?? [];
    const itemsMap = get().items;
    const items: Item[] = [];
    for (const itemId of itemIds) {
      const item = itemsMap.get(itemId);
      if (item) {
        items.push(item);
      }
    }
    return items;
  },
});

const createUpdateActions = (set: StoreSetter): Pick<ItemsActions, 'updateItem'> => ({
  updateItem: (id, updates) => {
    set((state) => {
      const item = state.items.get(id);
      if (!item) {
        return state;
      }

      const newItems = new Map(state.items);
      newItems.set(id, { ...item, ...updates });

      return { items: newItems };
    });
  },
});

const createOptimisticCreateActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<ItemsActions, 'confirmCreate' | 'optimisticCreate' | 'rollbackCreate'> => ({
  confirmCreate: (tempId, item) => {
    // Remove temp item and add real item
    get().removeItem(tempId);
    get().addItem(item);

    set((state) => {
      const newPendingCreates = new Map(state.pendingCreates);
      newPendingCreates.delete(tempId);
      return { pendingCreates: newPendingCreates };
    });
  },
  optimisticCreate: (tempId, data) => {
    const tempItem = buildTempItem(tempId, data);

    set((state) => {
      const newPendingCreates = new Map(state.pendingCreates);
      newPendingCreates.set(tempId, data);
      return { pendingCreates: newPendingCreates };
    });

    get().addItem(tempItem);
  },
  rollbackCreate: (tempId) => {
    get().removeItem(tempId);

    set((state) => {
      const newPendingCreates = new Map(state.pendingCreates);
      newPendingCreates.delete(tempId);
      return { pendingCreates: newPendingCreates };
    });
  },
});

const createOptimisticUpdateActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<ItemsActions, 'confirmUpdate' | 'optimisticUpdate' | 'rollbackUpdate'> => ({
  confirmUpdate: (id, item) => {
    get().addItem(item);

    set((state) => {
      const newPendingUpdates = new Map(state.pendingUpdates);
      newPendingUpdates.delete(id);
      return { pendingUpdates: newPendingUpdates };
    });
  },
  optimisticUpdate: (id, updates) => {
    const item = get().getItem(id);
    if (!item) {
      return;
    }

    set((state) => {
      const newPendingUpdates = new Map(state.pendingUpdates);
      newPendingUpdates.set(id, updates);
      return { pendingUpdates: newPendingUpdates };
    });

    get().updateItem(id, updates as Partial<Item>);
  },
  rollbackUpdate: (id) => {
    const pendingUpdate = get().pendingUpdates.get(id);
    if (!pendingUpdate) {
      return;
    }

    // Revert to previous state (would need to store original values)
    set((state) => {
      const newPendingUpdates = new Map(state.pendingUpdates);
      newPendingUpdates.delete(id);
      return { pendingUpdates: newPendingUpdates };
    });
  },
});

const createOptimisticDeleteActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<ItemsActions, 'confirmDelete' | 'optimisticDelete' | 'rollbackDelete'> => ({
  confirmDelete: (id) => {
    set((state) => {
      const newPendingDeletes = new Set(state.pendingDeletes);
      newPendingDeletes.delete(id);
      return { pendingDeletes: newPendingDeletes };
    });
  },
  optimisticDelete: (id) => {
    const item = get().getItem(id);
    if (!item) {
      return;
    }

    set((state) => {
      const newPendingDeletes = new Set(state.pendingDeletes);
      newPendingDeletes.add(id);
      return { pendingDeletes: newPendingDeletes };
    });

    get().removeItem(id);
  },
  rollbackDelete: (id, item) => {
    get().addItem(item);

    set((state) => {
      const newPendingDeletes = new Set(state.pendingDeletes);
      newPendingDeletes.delete(id);
      return { pendingDeletes: newPendingDeletes };
    });
  },
});

const createLoadingActions = (
  set: StoreSetter,
): Pick<ItemsActions, 'setItemLoading' | 'setLoading'> => ({
  setItemLoading: (id, loading) => {
    set((state) => {
      const newLoadingItems = new Set(state.loadingItems);
      if (loading) {
        newLoadingItems.add(id);
      } else {
        newLoadingItems.delete(id);
      }
      return { loadingItems: newLoadingItems };
    });
  },
  setLoading: (loading) => {
    set({ isLoading: loading });
  },
});

const buildItemsStore = (set: StoreSetter, get: StoreGetter): ItemsState => ({
  ...createInitialState(),
  ...createCollectionActions(set, get),
  ...createQueryActions(get),
  ...createUpdateActions(set),
  ...createOptimisticCreateActions(set, get),
  ...createOptimisticUpdateActions(set, get),
  ...createOptimisticDeleteActions(set, get),
  ...createLoadingActions(set),
});

export const useItemsStore = create<ItemsState>((set, get) => buildItemsStore(set, get));

export type { CreateItemInput, UpdateItemInput };
