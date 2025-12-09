// Search API stub
import { searchApi } from './endpoints'
import type { SearchQuery, SearchResult } from './types'

export const fetchSearchResults = async (query: SearchQuery): Promise<SearchResult[]> => {
  return searchApi.search(query)
}

export const search = searchApi.search
