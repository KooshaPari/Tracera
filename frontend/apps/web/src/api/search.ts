import type { SearchQuery, SearchResult } from './types';

import { searchApi } from './endpoints';

// Search API stub
const fetchSearchResults = async (query: SearchQuery): Promise<SearchResult> =>
  await searchApi.search(query);

const { search } = searchApi;

export { fetchSearchResults, search };
