import type * as ReactQuery from '@tanstack/react-query';

import type * as TracerTypes from '@tracertm/types';

import * as QueryKeys from './component-library-keys';
import * as QueryClient from './query-client';
import * as ReactQueryHooks from './react-query-hooks';

const useComponentLibraries = (
  projectId: string,
  options?: ReactQuery.UseQueryOptions<TracerTypes.ComponentLibrary[]>,
): ReactQuery.UseQueryResult<TracerTypes.ComponentLibrary[]> => {
  const baseOptions: ReactQuery.UseQueryOptions<TracerTypes.ComponentLibrary[]> = {
    enabled: Boolean(projectId),
    queryFn: async (): Promise<TracerTypes.ComponentLibrary[]> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<TracerTypes.ComponentLibrary[]>(
          '/api/v1/projects/{projectId}/libraries',
          {
            params: { path: { projectId } },
          },
        ),
      ),
    queryKey: QueryKeys.componentLibraryQueryKeys.list(projectId),
  };

  const queryOptions: ReactQuery.UseQueryOptions<TracerTypes.ComponentLibrary[]> = baseOptions;
  if (options) {
    Object.assign(queryOptions, options);
  }

  return ReactQueryHooks.useQuery(queryOptions);
};

const useComponentLibrary = (
  libraryId: string,
  options?: ReactQuery.UseQueryOptions<TracerTypes.ComponentLibrary>,
): ReactQuery.UseQueryResult<TracerTypes.ComponentLibrary> => {
  const baseOptions: ReactQuery.UseQueryOptions<TracerTypes.ComponentLibrary> = {
    enabled: Boolean(libraryId),
    queryFn: async (): Promise<TracerTypes.ComponentLibrary> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<TracerTypes.ComponentLibrary>('/api/v1/libraries/{libraryId}', {
          params: { path: { libraryId } },
        }),
      ),
    queryKey: QueryKeys.componentLibraryQueryKeys.detail(libraryId),
  };

  const queryOptions: ReactQuery.UseQueryOptions<TracerTypes.ComponentLibrary> = baseOptions;
  if (options) {
    Object.assign(queryOptions, options);
  }

  return ReactQueryHooks.useQuery(queryOptions);
};

const useLibraryComponents = (
  libraryId: string,
  options?: ReactQuery.UseQueryOptions<TracerTypes.LibraryComponent[]>,
): ReactQuery.UseQueryResult<TracerTypes.LibraryComponent[]> => {
  const baseOptions: ReactQuery.UseQueryOptions<TracerTypes.LibraryComponent[]> = {
    enabled: Boolean(libraryId),
    queryFn: async (): Promise<TracerTypes.LibraryComponent[]> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<TracerTypes.LibraryComponent[]>(
          '/api/v1/libraries/{libraryId}/components',
          {
            params: { path: { libraryId } },
          },
        ),
      ),
    queryKey: QueryKeys.componentLibraryQueryKeys.components(libraryId),
  };

  const queryOptions: ReactQuery.UseQueryOptions<TracerTypes.LibraryComponent[]> = baseOptions;
  if (options) {
    Object.assign(queryOptions, options);
  }

  return ReactQueryHooks.useQuery(queryOptions);
};

const useLibraryComponent = (
  componentId: string,
  options?: ReactQuery.UseQueryOptions<TracerTypes.LibraryComponent>,
): ReactQuery.UseQueryResult<TracerTypes.LibraryComponent> => {
  const baseOptions: ReactQuery.UseQueryOptions<TracerTypes.LibraryComponent> = {
    enabled: Boolean(componentId),
    queryFn: async (): Promise<TracerTypes.LibraryComponent> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<TracerTypes.LibraryComponent>('/api/v1/components/{componentId}', {
          params: { path: { componentId } },
        }),
      ),
    queryKey: QueryKeys.componentLibraryQueryKeys.component(componentId),
  };

  const queryOptions: ReactQuery.UseQueryOptions<TracerTypes.LibraryComponent> = baseOptions;
  if (options) {
    Object.assign(queryOptions, options);
  }

  return ReactQueryHooks.useQuery(queryOptions);
};

const useComponentUsage = (
  componentId: string,
  options?: ReactQuery.UseQueryOptions<TracerTypes.ComponentUsage[]>,
): ReactQuery.UseQueryResult<TracerTypes.ComponentUsage[]> => {
  const baseOptions: ReactQuery.UseQueryOptions<TracerTypes.ComponentUsage[]> = {
    enabled: Boolean(componentId),
    queryFn: async (): Promise<TracerTypes.ComponentUsage[]> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<TracerTypes.ComponentUsage[]>(
          '/api/v1/components/{componentId}/usage',
          {
            params: { path: { componentId } },
          },
        ),
      ),
    queryKey: QueryKeys.componentLibraryQueryKeys.usage(componentId),
  };

  const queryOptions: ReactQuery.UseQueryOptions<TracerTypes.ComponentUsage[]> = baseOptions;
  if (options) {
    Object.assign(queryOptions, options);
  }

  return ReactQueryHooks.useQuery(queryOptions);
};

const useDesignTokens = (
  libraryId: string,
  options?: ReactQuery.UseQueryOptions<TracerTypes.DesignToken[]>,
): ReactQuery.UseQueryResult<TracerTypes.DesignToken[]> => {
  const baseOptions: ReactQuery.UseQueryOptions<TracerTypes.DesignToken[]> = {
    enabled: Boolean(libraryId),
    queryFn: async (): Promise<TracerTypes.DesignToken[]> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<TracerTypes.DesignToken[]>('/api/v1/libraries/{libraryId}/tokens', {
          params: { path: { libraryId } },
        }),
      ),
    queryKey: QueryKeys.componentLibraryQueryKeys.tokens(libraryId),
  };

  const queryOptions: ReactQuery.UseQueryOptions<TracerTypes.DesignToken[]> = baseOptions;
  if (options) {
    Object.assign(queryOptions, options);
  }

  return ReactQueryHooks.useQuery(queryOptions);
};

export {
  useComponentLibraries,
  useComponentLibrary,
  useComponentUsage,
  useDesignTokens,
  useLibraryComponent,
  useLibraryComponents,
};

export { componentLibraryQueryKeys } from './component-library-keys';
