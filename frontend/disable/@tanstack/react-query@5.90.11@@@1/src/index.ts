/* istanbul ignore file */

// Re-export core
export * from "@tanstack/query-core";
export type { HydrationBoundaryProps } from "./HydrationBoundary";
export { HydrationBoundary } from "./HydrationBoundary";
export { IsRestoringProvider, useIsRestoring } from "./IsRestoringProvider";
export type {
	DefinedInitialDataInfiniteOptions,
	UndefinedInitialDataInfiniteOptions,
	UnusedSkipTokenInfiniteOptions,
} from "./infiniteQueryOptions";
export { infiniteQueryOptions } from "./infiniteQueryOptions";
export { mutationOptions } from "./mutationOptions";
export type { QueryClientProviderProps } from "./QueryClientProvider";
export {
	QueryClientContext,
	QueryClientProvider,
	useQueryClient,
} from "./QueryClientProvider";
export type {
	QueryErrorClearResetFunction,
	QueryErrorIsResetFunction,
	QueryErrorResetBoundaryFunction,
	QueryErrorResetBoundaryProps,
	QueryErrorResetFunction,
} from "./QueryErrorResetBoundary";
export {
	QueryErrorResetBoundary,
	useQueryErrorResetBoundary,
} from "./QueryErrorResetBoundary";
export type {
	DefinedInitialDataOptions,
	UndefinedInitialDataOptions,
	UnusedSkipTokenOptions,
} from "./queryOptions";
export { queryOptions } from "./queryOptions";
// React Query
export * from "./types";
export { useInfiniteQuery } from "./useInfiniteQuery";
export { useIsFetching } from "./useIsFetching";
export { useMutation } from "./useMutation";
export { useIsMutating, useMutationState } from "./useMutationState";
export { usePrefetchInfiniteQuery } from "./usePrefetchInfiniteQuery";
export { usePrefetchQuery } from "./usePrefetchQuery";
export type { QueriesOptions, QueriesResults } from "./useQueries";
export { useQueries } from "./useQueries";
export { useQuery } from "./useQuery";
export { useSuspenseInfiniteQuery } from "./useSuspenseInfiniteQuery";
export type {
	SuspenseQueriesOptions,
	SuspenseQueriesResults,
} from "./useSuspenseQueries";
export { useSuspenseQueries } from "./useSuspenseQueries";
export { useSuspenseQuery } from "./useSuspenseQuery";
