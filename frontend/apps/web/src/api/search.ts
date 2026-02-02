// Search API stub
import { searchApi } from "./endpoints";
import type { SearchQuery, SearchResult } from "./types";

export const fetchSearchResults = (
	query: SearchQuery,
): Promise<SearchResult> => {
	return searchApi.search(query);
};

const { search } = searchApi;
export { search };
