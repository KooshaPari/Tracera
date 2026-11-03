import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import type { CreateItemData, CreateItemWithSpecData } from "@/hooks/use-items/items-utils";
import type { Item, TypedItem, ViewType, ItemStatus } from "@tracertm/types";

import itemsUtils from "@/hooks/use-items/items-utils";
import { ITEM_STATUS_VALUES, PRIORITY_VALUES, VIEW_TYPE_VALUES } from "@/hooks/useItems/constants";
import { QUERY_CONFIGS, queryKeys } from "@/lib/queryConfig";
import { useAuthStore } from "@/stores/authStore";
import { API_ORIGIN } from "@/config/api-origin";

const API_URL = API_ORIGIN;

interface ItemFilters {
  projectId?: string | undefined;
  view?: ViewType | undefined;
  status?: ItemStatus | undefined;
  parentId?: string | undefined;
  limit?: number | undefined;
  offset?: number | undefined;
}

interface ItemsResponse {
  items: TypedItem[];
  total: number;
  unsupportedFields: string[];
}

class ItemsRequestError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`Failed to fetch items: HTTP ${status}`);
    this.name = "ItemsRequestError";
    this.status = status;
  }
}

function authHeaders(token: string | undefined): Record<string, string> {
  const headers: Record<string, string> = {};
  const trimmedToken = itemsUtils.readNonEmptyString(token);
  if (trimmedToken !== undefined) {
    headers["Authorization"] = `Bearer ${trimmedToken.trim()}`;
  }
  return headers;
}

function buildQueryParams(filters: ItemFilters): URLSearchParams {
  const params = new URLSearchParams();

  if (itemsUtils.readNonEmptyString(filters.projectId) !== undefined) {
    params.set("project_id", filters.projectId ?? itemsUtils.EMPTY_STRING);
  }

  if (filters.view !== undefined) {
    params.set("view", filters.view);
  }
  if (filters.status !== undefined) {
    params.set("status", filters.status);
  }
  if (filters.limit !== undefined) {
    params.set("limit", String(filters.limit));
  }
  if (filters.offset !== undefined) {
    params.set("offset", String(filters.offset));
  }

  return params;
}

async function fetchItems(filters: ItemFilters = {}, token?: string): Promise<ItemsResponse> {
  if (itemsUtils.readNonEmptyString(filters.parentId) !== undefined) {
    throw new Error("Parent filtering is not supported by the items API");
  }
  const params = buildQueryParams(filters);

  const res = await fetch(`${API_URL}/api/v1/items?${params}`, {
    credentials: "include",
    headers: {
      "X-Bulk-Operation": "true",
      ...authHeaders(token),
    },
  });
  if (res.ok) {
    const data = (await res.json()) as unknown;
    if (
      !itemsUtils.isRecord(data) ||
      Array.isArray(data) ||
      !Array.isArray(data["items"]) ||
      !data["items"].every((item: unknown) => itemsUtils.isRecord(item) && !Array.isArray(item)) ||
      typeof data["total"] !== "number" ||
      !Number.isSafeInteger(data["total"]) ||
      data["total"] < 0 ||
      data["items"].length !==
        Math.min(filters.limit ?? 50, Math.max(0, data["total"] - (filters.offset ?? 0)))
    ) {
      throw new Error("Invalid items list response");
    }
    const itemsArray = itemsUtils.extractItemsArray(data);
    const unsupported = new Set<string>();
    for (const entry of itemsArray) {
      if (!VIEW_TYPE_VALUES.some((value) => value === entry["view"])) unsupported.add("view");
      if (!ITEM_STATUS_VALUES.some((value) => value === entry["status"])) unsupported.add("status");
      if (!PRIORITY_VALUES.some((value) => value === entry["priority"]))
        unsupported.add("priority");
      if (
        typeof entry["version"] !== "number" ||
        !Number.isSafeInteger(entry["version"]) ||
        entry["version"] < 0
      )
        unsupported.add("version");
    }
    const transformedItems = itemsArray.map((entry) => itemsUtils.normalizeItem(entry));
    if (new Set(transformedItems.map((item) => item.id)).size !== transformedItems.length) {
      throw new Error("Items response contains duplicate IDs");
    }
    const projectId = itemsUtils.readNonEmptyString(filters.projectId);
    if (projectId !== undefined && transformedItems.some((item) => item.projectId !== projectId)) {
      throw new Error("Items response contains records from another project");
    }
    return {
      items: transformedItems,
      total: data["total"],
      unsupportedFields: [...unsupported],
    };
  }
  throw new ItemsRequestError(res.status);
}

async function fetchItem(id: string, token: string | undefined): Promise<Item> {
  const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
    credentials: "include",
    headers: authHeaders(token),
  });
  if (res.ok) {
    const data = (await res.json()) as unknown;
    if (itemsUtils.isRecord(data)) {
      return itemsUtils.normalizeBaseItem(data);
    }
    throw new Error("Invalid item payload");
  }
  throw new Error("Failed to fetch item");
}

async function createItem(data: CreateItemData, token: string | undefined): Promise<Item> {
  const res = await fetch(`${API_URL}/api/v1/items`, {
    body: JSON.stringify({
      description: data["description"],
      owner: data["owner"],
      parent_id: data["parentId"],
      priority: data["priority"],
      project_id: data["projectId"],
      status: data.status,
      title: data["title"],
      type: data.type,
      view: data["view"],
    }),
    credentials: "include",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    method: "POST",
  });
  if (res.ok) {
    const responseData = (await res.json()) as unknown;
    if (itemsUtils.isRecord(responseData)) {
      return itemsUtils.normalizeBaseItem(responseData);
    }
    throw new Error("Invalid item payload");
  }
  throw new Error("Failed to create item");
}

async function createItemWithSpec(
  data: CreateItemWithSpecData,
  token: string | undefined,
): Promise<TypedItem> {
  const res = await fetch(`${API_URL}/api/v1/items`, {
    body: JSON.stringify({
      project_id: data["projectId"],
      view: data["item"].view,
      type: data["item"].type,
      title: data["item"].title,
      description: data["item"].description,
      status: data["item"].status,
      priority: data["item"].priority,
      parent_id: data["item"].parentId,
      owner: data["item"].owner,
      metadata: data["item"].metadata,
      ...data["spec"],
    }),
    credentials: "include",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    method: "POST",
  });
  if (res.ok) {
    const responseData = (await res.json()) as unknown;
    if (itemsUtils.isRecord(responseData)) {
      return itemsUtils.normalizeItem(responseData);
    }
    throw new Error("Invalid item payload");
  }
  const errorText = await res.text();
  throw new Error(`Failed to create item with spec: ${res.status} ${errorText}`);
}

async function updateItem(
  id: string,
  data: Partial<Item>,
  token: string | undefined,
): Promise<Item> {
  const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
    body: JSON.stringify(data),
    credentials: "include",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    method: "PATCH",
  });
  if (res.ok) {
    const responseData = (await res.json()) as unknown;
    if (itemsUtils.isRecord(responseData)) {
      return itemsUtils.normalizeBaseItem(responseData);
    }
    throw new Error("Invalid item payload");
  }
  throw new Error("Failed to update item");
}

async function deleteItem(id: string, token: string | undefined): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/items/${id}`, {
    credentials: "include",
    headers: authHeaders(token),
    method: "DELETE",
  });
  if (res.ok) {
    return;
  }
  throw new Error("Failed to delete item");
}

function useAuthToken(): string | undefined {
  const storeToken = useAuthStore((state) => state.token);
  const trimmedStoreToken = itemsUtils.readNonEmptyString(storeToken);
  if (trimmedStoreToken !== undefined) {
    return trimmedStoreToken.trim();
  }
  if (globalThis.window !== undefined) {
    const fromStorage = globalThis.localStorage?.getItem("auth_token");
    const trimmedStorageToken = itemsUtils.readNonEmptyString(fromStorage);
    if (trimmedStorageToken !== undefined) {
      return trimmedStorageToken.trim();
    }
  }
  return undefined;
}

function buildItemsQueryKey(
  filters: ItemFilters | undefined,
  token: string | undefined,
): unknown[] {
  const key: unknown[] = [];
  const projectId = itemsUtils.readNonEmptyString(filters?.projectId);
  if (projectId === undefined) {
    key.push("items");
  } else {
    key.push(...queryKeys.items.list(projectId));
  }
  key.push(filters?.view);
  key.push(filters?.status);
  key.push(filters?.parentId);
  key.push(filters?.limit);
  key.push(filters?.offset);
  if (token === undefined) {
    key.push(itemsUtils.EMPTY_STRING);
  } else {
    key.push(token);
  }
  return key;
}

function useItems(filters?: ItemFilters): ReturnType<typeof useQuery<ItemsResponse>> {
  const token = useAuthToken();
  const key = buildItemsQueryKey(filters, token);
  return useQuery({
    queryKey: key,
    queryFn: async (): Promise<ItemsResponse> => {
      const result = await fetchItems(filters ?? {}, token);
      return result;
    },
    ...QUERY_CONFIGS.dynamic,
  });
}

function useItem(id: string): ReturnType<typeof useQuery<Item>> {
  const token = useAuthToken();
  const enabled = id.trim() !== itemsUtils.EMPTY_STRING;
  return useQuery({
    queryKey: [...queryKeys.items.detail(id), token ?? itemsUtils.EMPTY_STRING],
    queryFn: async (): Promise<Item> => {
      const result = await fetchItem(id, token);
      return result;
    },
    enabled,
    ...QUERY_CONFIGS.dynamic,
  });
}

function useCreateItem(): ReturnType<typeof useMutation<Item, Error, CreateItemData>> {
  const queryClient = useQueryClient();
  const token = useAuthToken();
  return useMutation({
    mutationFn: async (data: CreateItemData): Promise<Item> => {
      const result = await createItem(itemsUtils.normalizeCreateItemData(data), token);
      return result;
    },
    onSuccess: async (): Promise<void> => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
  });
}

function useUpdateItem(): ReturnType<
  typeof useMutation<Item, Error, { id: string; data: Partial<Item> }>
> {
  const queryClient = useQueryClient();
  const token = useAuthToken();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Item> }): Promise<Item> => {
      const result = await updateItem(id, data, token);
      return result;
    },
    onSuccess: async (): Promise<void> => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
  });
}

function useDeleteItem(): ReturnType<typeof useMutation<void, Error, string>> {
  const queryClient = useQueryClient();
  const token = useAuthToken();
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await deleteItem(id, token);
    },
    onSuccess: async (): Promise<void> => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
  });
}

function useCreateItemWithSpec(): ReturnType<
  typeof useMutation<TypedItem, Error, CreateItemWithSpecData>
> {
  const queryClient = useQueryClient();
  const token = useAuthToken();
  return useMutation({
    mutationFn: async (data: CreateItemWithSpecData): Promise<TypedItem> => {
      const result = await createItemWithSpec(
        itemsUtils.normalizeCreateItemWithSpecData(data),
        token,
      );
      return result;
    },
    onError: (error: Error): void => {
      toast.error("Failed to create item", {
        description: error.message,
      });
    },
    onSuccess: async (data: TypedItem): Promise<void> => {
      await queryClient.invalidateQueries({ queryKey: ["items"] });
      toast.success("Item created successfully", {
        description: `Created ${data.type}: ${data["title"]}`,
      });
    },
  });
}

export { useItems, useItem, useCreateItem, useUpdateItem, useDeleteItem, useCreateItemWithSpec };
