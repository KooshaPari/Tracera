/* oxlint-disable oxc/no-async-await */
import type { SearchQuery, SearchResult } from "./types";
// Search API stub
import { searchApi } from "./endpoints";

export const fetchSearchResults = (query: SearchQuery): Promise<SearchResult> =>
	searchApi.search(query);

export const search = searchApi.search;
