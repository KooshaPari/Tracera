import { itemsApi } from './endpoints';

const RECENT_ITEMS_LIMIT = 10;
const START_INDEX = 0;

const fetchItems = itemsApi.list;
const fetchItem = itemsApi.get;
const fetchRecentItems = async (): Promise<unknown[]> =>
  itemsApi.list({ limit: RECENT_ITEMS_LIMIT }).then((result) => {
    let items: unknown[] = [];
    if (Array.isArray(result)) {
      items = result;
    } else {
      const resultItems = (result as { items?: unknown[] }).items;
      if (Array.isArray(resultItems)) {
        items = resultItems;
      }
    }
    return items.slice(START_INDEX, RECENT_ITEMS_LIMIT);
  });
const createItem = itemsApi.create;
const updateItem = itemsApi.update;
const deleteItem = itemsApi.delete;

const fetchProjectItems = fetchItems;

export {
  createItem,
  deleteItem,
  fetchItem,
  fetchItems,
  fetchProjectItems,
  fetchRecentItems,
  updateItem,
};
