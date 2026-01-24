import type { Item, ItemStatus, Priority } from "@tracertm/types";
import { create } from "zustand";

interface CreateItemInput {
	projectId: string;
	type: string;
	title: string;
	description?: string;
	status?: ItemStatus;
	priority?: Priority;
	parentId?: string;
}

interface UpdateItemInput {
	type?: string;
	title?: string;
	description?: string;
	status?: ItemStatus;
	priority?: Priority;
	parentId?: string;
}

interface ItemsState {
	// Items cache
	items: Map<string, Item>;
	itemsByProject: Map<string, string[]>;

	// Loading states
	isLoading: boolean;
	loadingItems: Set<string>;

	// Optimistic updates
	pendingCreates: Map<string, CreateItemInput>;
	pendingUpdates: Map<string, UpdateItemInput>;
	pendingDeletes: Set<string>;

	// Actions - Basic CRUD
	addItem: (item: Item) => void;
	addItems: (items: Item[]) => void;
	updateItem: (id: string, updates: Partial<Item>) => void;
	removeItem: (id: string) => void;
	getItem: (id: string) => Item | undefined;
	getItemsByProject: (projectId: string) => Item[];
	clearItems: () => void;

	// Actions - Optimistic updates
	optimisticCreate: (tempId: string, data: CreateItemInput) => void;
	confirmCreate: (tempId: string, item: Item) => void;
	rollbackCreate: (tempId: string) => void;

	optimisticUpdate: (id: string, updates: UpdateItemInput) => void;
	confirmUpdate: (id: string, item: Item) => void;
	rollbackUpdate: (id: string) => void;

	optimisticDelete: (id: string) => void;
	confirmDelete: (id: string) => void;
	rollbackDelete: (id: string, item: Item) => void;

	// Actions - Loading states
	setLoading: (loading: boolean) => void;
	setItemLoading: (id: string, loading: boolean) => void;
}

export const useItemsStore = create<ItemsState>((set, get) => ({
	// Initial state
	items: new Map(),
	itemsByProject: new Map(),
	isLoading: false,
	loadingItems: new Set(),
	pendingCreates: new Map(),
	pendingUpdates: new Map(),
	pendingDeletes: new Set(),

	// Basic CRUD
	addItem: (item) => {
		set((state) => {
			const newItems = new Map(state.items);
			newItems.set(item.id, item);

			const newItemsByProject = new Map(state.itemsByProject);
			const projectItems = newItemsByProject.get(item.projectId) || [];
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
		items.forEach((item) => get().addItem(item));
	},

	updateItem: (id, updates) => {
		set((state) => {
			const item = state.items.get(id);
			if (!item) return state;

			const newItems = new Map(state.items);
			newItems.set(id, { ...item, ...updates });

			return { items: newItems };
		});
	},

	removeItem: (id) => {
		set((state) => {
			const item = state.items.get(id);
			if (!item) return state;

			const newItems = new Map(state.items);
			newItems.delete(id);

			const newItemsByProject = new Map(state.itemsByProject);
			const projectItems = newItemsByProject.get(item.projectId) || [];
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

	getItem: (id) => {
		return get().items.get(id);
	},

	getItemsByProject: (projectId) => {
		const itemIds = get().itemsByProject.get(projectId) || [];
		const items = get().items;
		return itemIds.map((id) => items.get(id)!).filter(Boolean);
	},

	clearItems: () => {
		set({
			items: new Map(),
			itemsByProject: new Map(),
		});
	},

	// Optimistic creates
	optimisticCreate: (tempId, data) => {
		const tempItem: Item = {
			id: tempId,
			projectId: data.projectId,
			view: "FEATURE" as any, // Default view type
			type: data.type,
			title: data.title,
			...(data.description !== undefined && { description: data.description }),
			status: (data.status || "todo") as any,
			priority: data.priority || "medium",
			...(data.parentId !== undefined && { parentId: data.parentId }),
			version: 1,
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
		};

		set((state) => {
			const newPendingCreates = new Map(state.pendingCreates);
			newPendingCreates.set(tempId, data);
			return { pendingCreates: newPendingCreates };
		});

		get().addItem(tempItem);
	},

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

	rollbackCreate: (tempId) => {
		get().removeItem(tempId);

		set((state) => {
			const newPendingCreates = new Map(state.pendingCreates);
			newPendingCreates.delete(tempId);
			return { pendingCreates: newPendingCreates };
		});
	},

	// Optimistic updates
	optimisticUpdate: (id, updates) => {
		const item = get().getItem(id);
		if (!item) return;

		set((state) => {
			const newPendingUpdates = new Map(state.pendingUpdates);
			newPendingUpdates.set(id, updates);
			return { pendingUpdates: newPendingUpdates };
		});

		get().updateItem(id, updates);
	},

	confirmUpdate: (id, item) => {
		get().addItem(item);

		set((state) => {
			const newPendingUpdates = new Map(state.pendingUpdates);
			newPendingUpdates.delete(id);
			return { pendingUpdates: newPendingUpdates };
		});
	},

	rollbackUpdate: (id) => {
		const pendingUpdate = get().pendingUpdates.get(id);
		if (!pendingUpdate) return;

		// Revert to previous state (would need to store original values)
		set((state) => {
			const newPendingUpdates = new Map(state.pendingUpdates);
			newPendingUpdates.delete(id);
			return { pendingUpdates: newPendingUpdates };
		});
	},

	// Optimistic deletes
	optimisticDelete: (id) => {
		const item = get().getItem(id);
		if (!item) return;

		set((state) => {
			const newPendingDeletes = new Set(state.pendingDeletes);
			newPendingDeletes.add(id);
			return { pendingDeletes: newPendingDeletes };
		});

		get().removeItem(id);
	},

	confirmDelete: (id) => {
		set((state) => {
			const newPendingDeletes = new Set(state.pendingDeletes);
			newPendingDeletes.delete(id);
			return { pendingDeletes: newPendingDeletes };
		});
	},

	rollbackDelete: (id, item) => {
		get().addItem(item);

		set((state) => {
			const newPendingDeletes = new Set(state.pendingDeletes);
			newPendingDeletes.delete(id);
			return { pendingDeletes: newPendingDeletes };
		});
	},

	// Loading states
	setLoading: (loading) => {
		set({ isLoading: loading });
	},

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
}));
