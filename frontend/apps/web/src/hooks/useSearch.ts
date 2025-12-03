import { useQuery } from '@tanstack/react-query'
import { useCallback, useState } from 'react'
import { api } from '../api/endpoints'
import type { SearchQuery } from '../api/types'
import { useDebounce } from './useDebounce'

export function useSearch(initialQuery: Partial<SearchQuery> = {}) {
  const [query, setQuery] = useState<SearchQuery>({
    q: '',
    page: 1,
    per_page: 20,
    ...initialQuery,
  })

  const debouncedQuery = useDebounce(query.q, 300)

  const searchQuery = useQuery({
    queryKey: ['search', { ...query, q: debouncedQuery }],
    queryFn: () => api.search.search({ ...query, q: debouncedQuery }),
    enabled: debouncedQuery.length > 0,
  })

  const updateQuery = useCallback((updates: Partial<SearchQuery>) => {
    setQuery((prev) => ({ ...prev, ...updates }))
  }, [])

  const setSearchText = useCallback((q: string) => {
    setQuery((prev) => ({ ...prev, q, page: 1 }))
  }, [])

  const setPage = useCallback((page: number) => {
    setQuery((prev) => ({ ...prev, page }))
  }, [])

  const clearSearch = useCallback(() => {
    setQuery({
      q: '',
      page: 1,
      per_page: 20,
    })
  }, [])

  return {
    query,
    results: searchQuery.data,
    isLoading: searchQuery.isLoading,
    isError: searchQuery.isError,
    error: searchQuery.error,
    updateQuery,
    setSearchText,
    setPage,
    clearSearch,
  }
}

export function useSearchSuggestions(q: string, limit: number = 10) {
  const debouncedQuery = useDebounce(q, 200)

  return useQuery({
    queryKey: ['search-suggestions', debouncedQuery, limit],
    queryFn: () => api.search.suggest(debouncedQuery, limit),
    enabled: debouncedQuery.length > 2,
    staleTime: 60000, // 1 minute
  })
}
