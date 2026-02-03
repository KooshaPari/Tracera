import { useQuery } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import { api } from "../api/endpoints";
import type { SearchQuery } from "../api/types";
import { useDebounce } from "./useDebounce";

export function useSearch(initialQuery: Partial<SearchQuery> = {}) {
	const [query, setQuery] = useState<SearchQuery>({
		q: "",
		page: 1,
		per_page: 20,
		...initialQuery,
	});

	const debouncedQuery = useDebounce(query.q, 300);

	const searchQuery = useQuery({
		enabled: debouncedQuery.length > 0,
		queryFn: () => api.search.search({ ...query, q: debouncedQuery }),
		queryKey: ["search", { ...query, q: debouncedQuery }],
	});

	const updateQuery = useCallback((updates: Partial<SearchQuery>) => {
		setQuery((prev) => ({ ...prev, ...updates }));
	}, []);

	const setSearchText = useCallback((q: string) => {
		setQuery((prev) => ({ ...prev, q, page: 1 }));
	}, []);

	const setPage = useCallback((page: number) => {
		setQuery((prev) => ({ ...prev, page }));
	}, []);

	const clearSearch = useCallback(() => {
		setQuery({
			page: 1,
			per_page: 20,
			q: "",
		});
	}, []);

	return {
		clearSearch,
		error: searchQuery.error,
		isError: searchQuery.isError,
		isLoading: searchQuery.isLoading,
		query,
		results: searchQuery.data,
		setPage,
		setSearchText,
		updateQuery,
	};
}

export function useSearchSuggestions(q: string, limit = 10) {
	const debouncedQuery = useDebounce(q, 200);

	return useQuery({
		enabled: debouncedQuery.length > 2,
		queryFn: () => api.search.suggest(debouncedQuery, limit),
		queryKey: ["search-suggestions", debouncedQuery, limit],
		staleTime: 60000, // 1 minute
	});
}
