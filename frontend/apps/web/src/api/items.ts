// Re-export items API from endpoints
import { itemsApi } from "./endpoints";

const RECENT_ITEMS_LIMIT = 10;
const START_INDEX = 0;

export const fetchItems = itemsApi.list;
export const fetchItem = itemsApi.get;
export const fetchRecentItems = async () => {
	const result = await itemsApi.list({ limit: RECENT_ITEMS_LIMIT });
	const items = Array.isArray(result) ? result : (result as { items?: unknown[] }).items ?? [];
	return items.slice(START_INDEX, RECENT_ITEMS_LIMIT);
};
export const createItem = itemsApi.create;
export const updateItem = itemsApi.update;
export const deleteItem = itemsApi.delete;
