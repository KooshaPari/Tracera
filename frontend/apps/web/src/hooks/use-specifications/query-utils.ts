import type {
  QueryClient,
  QueryKey,
  UseMutationResult,
  UseQueryResult,
} from '@tanstack/react-query';

type QueryResult<TResult> = UseQueryResult<TResult>;

type MutationResult<TData, TVariables = void> = UseMutationResult<TData, Error, TVariables>;

const invalidateQueries = async (
  queryClient: QueryClient,
  queryKeys: QueryKey[],
): Promise<void> => {
  const invalidations: Promise<unknown>[] = [];

  for (const queryKey of queryKeys) {
    invalidations.push(queryClient.invalidateQueries({ queryKey }));
  }

  await Promise.all(invalidations);
};

export { invalidateQueries, type MutationResult, type QueryResult };
