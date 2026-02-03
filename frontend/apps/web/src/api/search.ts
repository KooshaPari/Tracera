/* oxlint-disable oxc/no-async-await */
// Search API stub
import { searchApi } from "./endpoints";
import type { SearchQuery, SearchResult } from "./types";

export const fetchSearchResults = (query: SearchQuery): Promise<SearchResult> =>
	searchApi.search(query);

const { search } = searchApi;
export default { fetchSearchResults, search };
