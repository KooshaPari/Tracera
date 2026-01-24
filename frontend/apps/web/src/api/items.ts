// Re-export items API from endpoints
import { itemsApi } from "./endpoints";

export const fetchItems = itemsApi.list;
export const fetchItem = itemsApi.get;
export const fetchRecentItems = async () => {
	const items = await itemsApi.list({ limit: 10 });
	return items.slice(0, 10);
};
export const createItem = itemsApi.create;
export const updateItem = itemsApi.update;
export const deleteItem = itemsApi.delete;
