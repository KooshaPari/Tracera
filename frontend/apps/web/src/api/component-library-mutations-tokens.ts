import type * as ReactQuery from '@tanstack/react-query';

import type * as TracerTypes from '@tracertm/types';

import * as QueryKeys from './component-library-keys';
import * as QueryClient from './query-client';
import * as ReactQueryHooks from './react-query-hooks';

interface CreateDesignTokenInput {
  libraryId: string;
  name: string;
  type: string;
  value: unknown;
  category: string;
  description?: string;
}

interface UpdateDesignTokenInput {
  name?: string;
  type?: string;
  value?: unknown;
  category?: string;
  description?: string;
}

const useCreateDesignToken = (
  options?: ReactQuery.UseMutationOptions<TracerTypes.DesignToken, Error, CreateDesignTokenInput>,
): ReactQuery.UseMutationResult<TracerTypes.DesignToken, Error, CreateDesignTokenInput> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    TracerTypes.DesignToken,
    Error,
    CreateDesignTokenInput
  > = {
    mutationFn: async (input: CreateDesignTokenInput): Promise<TracerTypes.DesignToken> =>
      QueryClient.handleApiResponse(
        QueryClient.api.post<TracerTypes.DesignToken>('/api/v1/libraries/{libraryId}/tokens', {
          body: {
            category: input.category,
            description: input.description,
            name: input.name,
            type: input.type,
            value: input.value,
          },
          params: { path: { libraryId: input.libraryId } },
        }),
      ),
    onSuccess: async (data: TracerTypes.DesignToken): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QueryKeys.componentLibraryQueryKeys.tokens(data.libraryId),
      });
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    TracerTypes.DesignToken,
    Error,
    CreateDesignTokenInput
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const useUpdateDesignToken = (
  options?: ReactQuery.UseMutationOptions<
    TracerTypes.DesignToken,
    Error,
    { tokenId: string; data: UpdateDesignTokenInput }
  >,
): ReactQuery.UseMutationResult<
  TracerTypes.DesignToken,
  Error,
  { tokenId: string; data: UpdateDesignTokenInput }
> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    TracerTypes.DesignToken,
    Error,
    { tokenId: string; data: UpdateDesignTokenInput }
  > = {
    mutationFn: async (input: {
      tokenId: string;
      data: UpdateDesignTokenInput;
    }): Promise<TracerTypes.DesignToken> =>
      QueryClient.handleApiResponse(
        QueryClient.api.put<TracerTypes.DesignToken>('/api/v1/tokens/{tokenId}', {
          body: input.data,
          params: { path: { tokenId: input.tokenId } },
        }),
      ),
    onSuccess: async (data: TracerTypes.DesignToken): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QueryKeys.componentLibraryQueryKeys.tokens(data.libraryId),
      });
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    TracerTypes.DesignToken,
    Error,
    { tokenId: string; data: UpdateDesignTokenInput }
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const useDeleteDesignToken = (
  options?: ReactQuery.UseMutationOptions<void, Error, { tokenId: string; libraryId: string }>,
): ReactQuery.UseMutationResult<void, Error, { tokenId: string; libraryId: string }> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    void,
    Error,
    { tokenId: string; libraryId: string }
  > = {
    mutationFn: async (input: { tokenId: string; libraryId: string }): Promise<void> =>
      QueryClient.handleApiResponse(
        QueryClient.api.del<void>('/api/v1/tokens/{tokenId}', {
          params: { path: { tokenId: input.tokenId } },
        }),
      ),
    onSuccess: async (
      _data: void,
      variables: { tokenId: string; libraryId: string },
    ): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QueryKeys.componentLibraryQueryKeys.tokens(variables.libraryId),
      });
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    void,
    Error,
    { tokenId: string; libraryId: string }
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const componentLibraryMutationsTokens = {
  useCreateDesignToken,
  useDeleteDesignToken,
  useUpdateDesignToken,
};

export { componentLibraryMutationsTokens };
