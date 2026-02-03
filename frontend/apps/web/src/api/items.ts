/* oxlint-disable oxc/no-async-await */
// Re-export items API from endpoints
import { itemsApi } from "./endpoints";

const RECENT_ITEMS_LIMIT = 10;
const START_INDEX = 0;

const fetchItems = itemsApi.list;
const fetchItem = itemsApi.get;
const fetchRecentItems = async (): Promise<unknown[]> => {
	const result = await itemsApi.list({ limit: RECENT_ITEMS_LIMIT });
	const items = Array.isArray(result)
		? result
		: ((result as { items?: unknown[] }).items ?? []);
	return items.slice(START_INDEX, RECENT_ITEMS_LIMIT);
};
const createItem = itemsApi.create;
const updateItem = itemsApi.update;
const deleteItem = itemsApi.delete;

const itemsApiExports = {
	createItem,
	deleteItem,
	fetchItem,
	fetchItems,
	fetchRecentItems,
	updateItem,
};

// eslint-disable-next-line import/no-default-export
export default itemsApiExports;
