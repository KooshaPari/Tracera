import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	Item,
	ItemStatus,
	Priority,
	TypedItem,
	ViewType,
} from "@tracertm/types";
import { toast } from "sonner";
import { QUERY_CONFIGS, queryKeys } from "@/lib/queryConfig";
import { useAuthStore } from "@/stores/authStore";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

function authHeaders(token: string | null): Record<string, string> {
	const headers: Record<string, string> = {};
	if (token?.trim()) {
		headers.Authorization = `Bearer ${token.trim()}`;
	}
	return headers;
}

interface ItemFilters {
	projectId?: string | undefined;
	view?: ViewType | undefined;
	status?: ItemStatus | undefined;
	parentId?: string | undefined;
	limit?: number | undefined;
}

async function fetchItems(
	filters: ItemFilters = {},
	token: string | null = null,
): Promise<{ items: TypedItem[]; total: number }> {
	const params = new URLSearchParams();

	if (filters.projectId) {
		params.set("project_id", filters.projectId);
	}
	// Note: When projectId is undefined, API will return all items

	if (filters.view) params.set("view", filters.view);
	if (filters.status) params.set("status", filters.status);
	if (filters.parentId) params.set("parent_id", filters.parentId);
	if (filters.limit) params.set("limit", String(filters.limit));

	// Phase 6.2: Include specs in the response
	params.set("include_specs", "true");

	const res = await fetch(`${API_URL}/api/v1/items?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...authHeaders(token),
		},
		credentials: "include",
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch items: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	// API returns { total: number, items: Item[] }
	const itemsArray = Array.isArray(data) ? data : data.items || [];
	// Transform snake_case to camelCase for frontend compatibility
	const transformedItems = itemsArray.map((item: any) => {
		const baseItem = {
			...item,
			createdAt: item.created_at || item.createdAt,
			updatedAt: item.updated_at || item.updatedAt,
			projectId: item.project_id || item.projectId,
		};

		// Handle spec fields (both snake_case and camelCase)
		if (item.type === "requirement") {
			return {
				...baseItem,
				adrId: item.adr_id || item.adrId,
				contractId: item.contract_id || item.contractId,
				qualityMetrics: item.quality_metrics || item.qualityMetrics,
			};
		}

		if (
			item.type === "test" ||
			item.type === "test_case" ||
			item.type === "test_suite"
		) {
			return {
				...baseItem,
				testType: item.test_type || item.testType,
				automationStatus: item.automation_status || item.automationStatus,
				testSteps: item.test_steps || item.testSteps,
				expectedResult: item.expected_result || item.expectedResult,
				lastExecutionResult:
					item.last_execution_result || item.lastExecutionResult,
			};
		}

		if (item.type === "epic") {
			return {
				...baseItem,
				acceptanceCriteria: item.acceptance_criteria || item.acceptanceCriteria,
				businessValue: item.business_value || item.businessValue,
				targetRelease: item.target_release || item.targetRelease,
			};
		}

		if (item.type === "user_story" || item.type === "story") {
			return {
				...baseItem,
				asA: item.as_a || item.asA,
				iWant: item.i_want || item.iWant,
				soThat: item.so_that || item.soThat,
				acceptanceCriteria: item.acceptance_criteria || item.acceptanceCriteria,
				storyPoints: item.story_points || item.storyPoints,
			};
		}

		if (item.type === "task") {
			return {
				...baseItem,
				estimatedHours: item.estimated_hours || item.estimatedHours,
				actualHours: item.actual_hours || item.actualHours,
				assignee: item.assignee,
				dueDate: item.due_date || item.dueDate,
			};
		}

		if (item.type === "bug" || item.type === "defect") {
			return {
				...baseItem,
				severity: item.severity,
				reproducible: item.reproducible,
				stepsToReproduce: item.steps_to_reproduce || item.stepsToReproduce,
				environment: item.environment,
				foundInVersion: item.found_in_version || item.foundInVersion,
				fixedInVersion: item.fixed_in_version || item.fixedInVersion,
			};
		}

		return baseItem;
	}) as TypedItem[];
	return {
		items: transformedItems,
		total:
			data.total || (Array.isArray(data) ? data.length : itemsArray.length),
	};
}

async function fetchItem(id: string, token: string | null): Promise<Item> {
	const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
		headers: authHeaders(token),
		credentials: "include",
	});
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

async function createItem(
	data: CreateItemData,
	token: string | null,
): Promise<Item> {
	const res = await fetch(`${API_URL}/api/v1/items`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...authHeaders(token) },
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
		credentials: "include",
	});
	if (!res.ok) throw new Error("Failed to create item");
	return res.json() as Promise<Item>;
}

// Phase 6.1: New mutation for creating items with specifications
interface CreateItemWithSpecData {
	projectId: string;
	item: Partial<Item>;
	spec: Record<string, unknown>;
}

async function createItemWithSpec(
	data: CreateItemWithSpecData,
	token: string | null,
): Promise<TypedItem> {
	const res = await fetch(`${API_URL}/api/v1/items`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...authHeaders(token) },
		body: JSON.stringify({
			// Convert camelCase to snake_case for API
			project_id: data.projectId,
			view: data.item.view,
			type: data.item.type,
			title: data.item.title,
			description: data.item.description,
			status: data.item.status,
			priority: data.item.priority,
			parent_id: data.item.parentId,
			owner: data.item.owner,
			metadata: data.item.metadata,
			// Include spec fields
			...data.spec,
		}),
		credentials: "include",
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(
			`Failed to create item with spec: ${res.status} ${errorText}`,
		);
	}
	const responseData = await res.json();
	// Transform snake_case to camelCase for frontend compatibility
	const baseItem = {
		...responseData,
		createdAt: responseData.created_at || responseData.createdAt,
		updatedAt: responseData.updated_at || responseData.updatedAt,
		projectId: responseData.project_id || responseData.projectId,
		parentId: responseData.parent_id || responseData.parentId,
	};

	// Handle type-specific fields
	if (responseData.type === "requirement") {
		return {
			...baseItem,
			adrId: responseData.adr_id || responseData.adrId,
			contractId: responseData.contract_id || responseData.contractId,
			qualityMetrics:
				responseData.quality_metrics || responseData.qualityMetrics,
		} as TypedItem;
	}

	if (
		responseData.type === "test" ||
		responseData.type === "test_case" ||
		responseData.type === "test_suite"
	) {
		return {
			...baseItem,
			testType: responseData.test_type || responseData.testType,
			automationStatus:
				responseData.automation_status || responseData.automationStatus,
			testSteps: responseData.test_steps || responseData.testSteps,
			expectedResult:
				responseData.expected_result || responseData.expectedResult,
			lastExecutionResult:
				responseData.last_execution_result || responseData.lastExecutionResult,
		} as TypedItem;
	}

	if (responseData.type === "epic") {
		return {
			...baseItem,
			acceptanceCriteria:
				responseData.acceptance_criteria || responseData.acceptanceCriteria,
			businessValue: responseData.business_value || responseData.businessValue,
			targetRelease: responseData.target_release || responseData.targetRelease,
		} as TypedItem;
	}

	if (responseData.type === "user_story" || responseData.type === "story") {
		return {
			...baseItem,
			asA: responseData.as_a || responseData.asA,
			iWant: responseData.i_want || responseData.iWant,
			soThat: responseData.so_that || responseData.soThat,
			acceptanceCriteria:
				responseData.acceptance_criteria || responseData.acceptanceCriteria,
			storyPoints: responseData.story_points || responseData.storyPoints,
		} as TypedItem;
	}

	if (responseData.type === "task") {
		return {
			...baseItem,
			estimatedHours:
				responseData.estimated_hours || responseData.estimatedHours,
			actualHours: responseData.actual_hours || responseData.actualHours,
			assignee: responseData.assignee,
			dueDate: responseData.due_date || responseData.dueDate,
		} as TypedItem;
	}

	if (responseData.type === "bug" || responseData.type === "defect") {
		return {
			...baseItem,
			severity: responseData.severity,
			reproducible: responseData.reproducible,
			stepsToReproduce:
				responseData.steps_to_reproduce || responseData.stepsToReproduce,
			environment: responseData.environment,
			foundInVersion:
				responseData.found_in_version || responseData.foundInVersion,
			fixedInVersion:
				responseData.fixed_in_version || responseData.fixedInVersion,
		} as TypedItem;
	}

	return baseItem as TypedItem;
}

async function updateItem(
	id: string,
	data: Partial<Item>,
	token: string | null,
): Promise<Item> {
	const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json", ...authHeaders(token) },
		body: JSON.stringify(data),
		credentials: "include",
	});
	if (!res.ok) throw new Error("Failed to update item");
	return res.json() as Promise<Item>;
}

async function deleteItem(id: string, token: string | null): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
		method: "DELETE",
		headers: authHeaders(token),
		credentials: "include",
	});
	if (!res.ok) throw new Error("Failed to delete item");
}

/** Token for API calls: store first, then localStorage (before store rehydration / AuthKitSync). */
function useAuthToken(): string | null {
	const storeToken = useAuthStore((s) => s.token);
	if (storeToken?.trim()) return storeToken.trim();
	if (typeof window !== "undefined") {
		const fromStorage = window.localStorage?.getItem("auth_token");
		if (fromStorage?.trim()) return fromStorage.trim();
	}
	return null;
}

export function useItems(filters?: ItemFilters) {
	const token = useAuthToken();
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
		queryKey: [...key, token ?? ""],
		queryFn: () => fetchItems(filters || {}, token),
		select: (data) => data,
		...QUERY_CONFIGS.dynamic,
	});
}

export function useItem(id: string) {
	const token = useAuthToken();
	return useQuery({
		queryKey: [...queryKeys.items.detail(id), token ?? ""],
		queryFn: () => fetchItem(id, token),
		enabled: !!id,
		...QUERY_CONFIGS.dynamic,
	});
}

export function useCreateItem() {
	const queryClient = useQueryClient();
	const token = useAuthToken();
	return useMutation({
		mutationFn: (data: CreateItemData) => createItem(data, token),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["items"] });
		},
	});
}

export function useUpdateItem() {
	const queryClient = useQueryClient();
	const token = useAuthToken();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: Partial<Item> }) =>
			updateItem(id, data, token),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["items"] });
			queryClient.invalidateQueries({ queryKey: ["items", id] });
		},
	});
}

export function useDeleteItem() {
	const queryClient = useQueryClient();
	const token = useAuthToken();
	return useMutation({
		mutationFn: (id: string) => deleteItem(id, token),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["items"] });
		},
	});
}

// Phase 6.1: New hook for creating items with specifications
export function useCreateItemWithSpec() {
	const queryClient = useQueryClient();
	const token = useAuthToken();
	return useMutation({
		mutationFn: (data: CreateItemWithSpecData) =>
			createItemWithSpec(data, token),
		onSuccess: (data) => {
			// Invalidate all items queries to refresh the list
			queryClient.invalidateQueries({ queryKey: ["items"] });

			// Show success toast notification
			toast.success("Item created successfully", {
				description: `Created ${data.type}: ${data.title}`,
			});
		},
		onError: (error: Error) => {
			// Show error toast notification
			toast.error("Failed to create item", {
				description: error.message,
			});
		},
	});
}
