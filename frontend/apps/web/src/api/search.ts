import { searchApi } from "./endpoints";
import type { SearchQuery, SearchResult } from "./types";

// Search API stub
const fetchSearchResults = async (
	query: SearchQuery,
): Promise<SearchResult> => await searchApi.search(query);

const { search } = searchApi;

export { fetchSearchResults, search };
