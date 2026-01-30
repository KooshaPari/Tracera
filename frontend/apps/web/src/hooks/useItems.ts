import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Item, ItemStatus, Priority, ViewType } from "@tracertm/types";
import { QUERY_CONFIGS, queryKeys } from "@/lib/queryConfig";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface ItemFilters {
	projectId?: string | undefined;
	view?: ViewType | undefined;
	status?: ItemStatus | undefined;
	parentId?: string | undefined;
	limit?: number | undefined;
}

async function fetchItems(
	filters: ItemFilters = {},
): Promise<{ items: Item[]; total: number }> {
	const params = new URLSearchParams();

	if (filters.projectId) {
		params.set("project_id", filters.projectId);
	}
	// Note: When projectId is undefined, API will return all items

	if (filters.view) params.set("view", filters.view);
	if (filters.status) params.set("status", filters.status);
	if (filters.parentId) params.set("parent_id", filters.parentId);
	if (filters.limit) params.set("limit", String(filters.limit));

	const res = await fetch(`${API_URL}/api/v1/items?${params}`, {
		headers: {
			"X-Bulk-Operation": "true", // Skip rate limiting for bulk fetches
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch items: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	// API returns { total: number, items: Item[] }
	const itemsArray = Array.isArray(data) ? data : data.items || [];
	// Transform snake_case to camelCase for frontend compatibility
	const transformedItems = itemsArray.map((item: any) => ({
		...item,
		createdAt: item.created_at || item.createdAt,
		updatedAt: item.updated_at || item.updatedAt,
		projectId: item.project_id || item.projectId,
	}));
	return {
		items: transformedItems,
		total:
			data.total || (Array.isArray(data) ? data.length : itemsArray.length),
	};
}

async function fetchItem(id: string): Promise<Item> {
	const res = await fetch(`${API_URL}/api/v1/items/${id}`);
	if (!res.ok) throw new Error("Failed to fetch item");
	const data = await res.json();
	// Transform snake_case to camelCase for frontend compatibility
	return {
		...data,
		createdAt: data.created_at || data.createdAt,
		updatedAt: data.updated_at || data.updatedAt,
		projectId: data.project_id || data.projectId,
	} as Item;
}

interface CreateItemData {
	projectId: string;
	view: ViewType;
	type: string;
	title: string;
	description?: string;
	status: ItemStatus;
	priority: Priority;
	parentId?: string;
	owner?: string;
}

async function createItem(data: CreateItemData): Promise<Item> {
	const res = await fetch(`${API_URL}/api/v1/items`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			project_id: data.projectId,
			view: data.view,
			type: data.type,
			title: data.title,
			description: data.description,
			status: data.status,
			priority: data.priority,
			parent_id: data.parentId,
			owner: data.owner,
		}),
	});
	if (!res.ok) throw new Error("Failed to create item");
	return res.json() as Promise<Item>;
}

async function updateItem(id: string, data: Partial<Item>): Promise<Item> {
	const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(data),
	});
	if (!res.ok) throw new Error("Failed to update item");
	return res.json() as Promise<Item>;
}

async function deleteItem(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
		method: "DELETE",
	});
	if (!res.ok) throw new Error("Failed to delete item");
}

export function useItems(filters?: ItemFilters) {
	const key = filters?.projectId
		? [
				...queryKeys.items.list(filters.projectId),
				filters?.view ?? null,
				filters?.status ?? null,
				filters?.parentId ?? null,
				filters?.limit ?? null,
			]
		: [
				"items",
				filters?.view ?? null,
				filters?.status ?? null,
				filters?.parentId ?? null,
				filters?.limit ?? null,
			];
	return useQuery({
		queryKey: key,
		queryFn: () => fetchItems(filters || {}),
		// Enable query always - fetch all items if no projectId provided
		select: (data) => data, // Return the full object with items and total
		...QUERY_CONFIGS.dynamic, // Items change frequently
	});
}

export function useItem(id: string) {
	return useQuery({
		queryKey: queryKeys.items.detail(id),
		queryFn: () => fetchItem(id),
		enabled: !!id,
		...QUERY_CONFIGS.dynamic, // Item details change frequently
	});
}

export function useCreateItem() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createItem,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["items"] });
		},
	});
}

export function useUpdateItem() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: Partial<Item> }) =>
			updateItem(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["items"] });
			queryClient.invalidateQueries({ queryKey: ["items", id] });
		},
	});
}

export function useDeleteItem() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteItem,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["items"] });
		},
	});
}
