import type * as ReactQuery from '@tanstack/react-query';

import type * as TracerTypes from '@tracertm/types';

import * as QueryKeys from './component-library-keys';
import * as QueryClient from './query-client';
import * as ReactQueryHooks from './react-query-hooks';

interface CreateComponentLibraryInput {
  projectId: string;
  name: string;
  description?: string;
  version?: string;
}

interface UpdateComponentLibraryInput {
  name?: string;
  description?: string;
  version?: string;
}

interface CreateLibraryComponentInput {
  libraryId: string;
  name: string;
  description?: string;
  category: string;
  properties?: Record<string, unknown>;
  variant?: string;
}

interface UpdateLibraryComponentInput {
  name?: string;
  description?: string;
  category?: string;
  properties?: Record<string, unknown>;
  variant?: string;
}

const useCreateComponentLibrary = (
  options?: ReactQuery.UseMutationOptions<
    TracerTypes.ComponentLibrary,
    Error,
    CreateComponentLibraryInput
  >,
): ReactQuery.UseMutationResult<
  TracerTypes.ComponentLibrary,
  Error,
  CreateComponentLibraryInput
> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    TracerTypes.ComponentLibrary,
    Error,
    CreateComponentLibraryInput
  > = {
    mutationFn: async (input: CreateComponentLibraryInput): Promise<TracerTypes.ComponentLibrary> =>
      QueryClient.handleApiResponse(
        QueryClient.api.post<TracerTypes.ComponentLibrary>(
          '/api/v1/projects/{projectId}/libraries',
          {
            body: {
              description: input.description,
              name: input.name,
              version: input.version,
            },
            params: { path: { projectId: input.projectId } },
          },
        ),
      ),
    onSuccess: async (data: TracerTypes.ComponentLibrary): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QueryKeys.componentLibraryQueryKeys.list(data.projectId),
      });
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    TracerTypes.ComponentLibrary,
    Error,
    CreateComponentLibraryInput
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const useUpdateComponentLibrary = (
  options?: ReactQuery.UseMutationOptions<
    TracerTypes.ComponentLibrary,
    Error,
    { libraryId: string; data: UpdateComponentLibraryInput }
  >,
): ReactQuery.UseMutationResult<
  TracerTypes.ComponentLibrary,
  Error,
  { libraryId: string; data: UpdateComponentLibraryInput }
> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    TracerTypes.ComponentLibrary,
    Error,
    { libraryId: string; data: UpdateComponentLibraryInput }
  > = {
    mutationFn: async (input: {
      libraryId: string;
      data: UpdateComponentLibraryInput;
    }): Promise<TracerTypes.ComponentLibrary> =>
      QueryClient.handleApiResponse(
        QueryClient.api.put<TracerTypes.ComponentLibrary>('/api/v1/libraries/{libraryId}', {
          body: input.data,
          params: { path: { libraryId: input.libraryId } },
        }),
      ),
    onSuccess: async (data: TracerTypes.ComponentLibrary): Promise<void> => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: QueryKeys.componentLibraryQueryKeys.detail(data.id),
        }),
        queryClient.invalidateQueries({
          queryKey: QueryKeys.componentLibraryQueryKeys.lists(),
        }),
      ]);
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    TracerTypes.ComponentLibrary,
    Error,
    { libraryId: string; data: UpdateComponentLibraryInput }
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const useDeleteComponentLibrary = (
  options?: ReactQuery.UseMutationOptions<void, Error, string>,
): ReactQuery.UseMutationResult<void, Error, string> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<void, Error, string> = {
    mutationFn: async (libraryId: string): Promise<void> =>
      QueryClient.handleApiResponse(
        QueryClient.api.del<void>('/api/v1/libraries/{libraryId}', {
          params: { path: { libraryId } },
        }),
      ),
    onSuccess: async (): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QueryKeys.componentLibraryQueryKeys.lists(),
      });
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<void, Error, string> = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const useCreateLibraryComponent = (
  options?: ReactQuery.UseMutationOptions<
    TracerTypes.LibraryComponent,
    Error,
    CreateLibraryComponentInput
  >,
): ReactQuery.UseMutationResult<
  TracerTypes.LibraryComponent,
  Error,
  CreateLibraryComponentInput
> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    TracerTypes.LibraryComponent,
    Error,
    CreateLibraryComponentInput
  > = {
    mutationFn: async (input: CreateLibraryComponentInput): Promise<TracerTypes.LibraryComponent> =>
      QueryClient.handleApiResponse(
        QueryClient.api.post<TracerTypes.LibraryComponent>(
          '/api/v1/libraries/{libraryId}/components',
          {
            body: {
              category: input.category,
              description: input.description,
              name: input.name,
              properties: input.properties,
              variant: input.variant,
            },
            params: { path: { libraryId: input.libraryId } },
          },
        ),
      ),
    onSuccess: async (data: TracerTypes.LibraryComponent): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QueryKeys.componentLibraryQueryKeys.components(data.libraryId),
      });
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    TracerTypes.LibraryComponent,
    Error,
    CreateLibraryComponentInput
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const useUpdateLibraryComponent = (
  options?: ReactQuery.UseMutationOptions<
    TracerTypes.LibraryComponent,
    Error,
    { componentId: string; data: UpdateLibraryComponentInput }
  >,
): ReactQuery.UseMutationResult<
  TracerTypes.LibraryComponent,
  Error,
  { componentId: string; data: UpdateLibraryComponentInput }
> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    TracerTypes.LibraryComponent,
    Error,
    { componentId: string; data: UpdateLibraryComponentInput }
  > = {
    mutationFn: async (input: {
      componentId: string;
      data: UpdateLibraryComponentInput;
    }): Promise<TracerTypes.LibraryComponent> =>
      QueryClient.handleApiResponse(
        QueryClient.api.put<TracerTypes.LibraryComponent>('/api/v1/components/{componentId}', {
          body: input.data,
          params: { path: { componentId: input.componentId } },
        }),
      ),
    onSuccess: async (data: TracerTypes.LibraryComponent): Promise<void> => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: QueryKeys.componentLibraryQueryKeys.component(data.id),
        }),
        queryClient.invalidateQueries({
          queryKey: QueryKeys.componentLibraryQueryKeys.components(data.libraryId),
        }),
      ]);
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    TracerTypes.LibraryComponent,
    Error,
    { componentId: string; data: UpdateLibraryComponentInput }
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const useDeleteLibraryComponent = (
  options?: ReactQuery.UseMutationOptions<void, Error, { componentId: string; libraryId: string }>,
): ReactQuery.UseMutationResult<void, Error, { componentId: string; libraryId: string }> => {
  const queryClient = ReactQueryHooks.useQueryClient();

  const baseOptions: ReactQuery.UseMutationOptions<
    void,
    Error,
    { componentId: string; libraryId: string }
  > = {
    mutationFn: async (input: { componentId: string; libraryId: string }): Promise<void> =>
      QueryClient.handleApiResponse(
        QueryClient.api.del<void>('/api/v1/components/{componentId}', {
          params: { path: { componentId: input.componentId } },
        }),
      ),
    onSuccess: async (
      data: void,
      variables: { componentId: string; libraryId: string },
    ): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QueryKeys.componentLibraryQueryKeys.components(variables.libraryId),
      });
      return data;
    },
  };

  const mutationOptions: ReactQuery.UseMutationOptions<
    void,
    Error,
    { componentId: string; libraryId: string }
  > = {};
  Object.assign(mutationOptions, baseOptions, options);

  return ReactQueryHooks.useMutation(mutationOptions);
};

const componentLibraryMutationsLibrary = {
  useCreateComponentLibrary,
  useCreateLibraryComponent,
  useDeleteComponentLibrary,
  useDeleteLibraryComponent,
  useUpdateComponentLibrary,
  useUpdateLibraryComponent,
};

export { componentLibraryMutationsLibrary };
