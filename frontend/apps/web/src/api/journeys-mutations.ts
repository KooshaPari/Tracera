import type * as ReactQuery from '@tanstack/react-query';

import type * as JourneyTypes from './journeys-types';

import * as JourneyKeys from './journeys-keys';
import * as QueryClient from './query-client';
import * as ReactQueryHooks from './react-query-hooks';

const useDetectJourneys = (
  options?: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey[],
    Error,
    JourneyTypes.DetectJourneysInput
  >,
): ReactQuery.UseMutationResult<
  JourneyTypes.Journey[],
  Error,
  JourneyTypes.DetectJourneysInput
> => {
  const queryClient = ReactQueryHooks.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey[],
    Error,
    JourneyTypes.DetectJourneysInput
  > = {
    mutationFn: async (
      input: JourneyTypes.DetectJourneysInput,
    ): Promise<JourneyTypes.Journey[]> => {
      const { projectId, minLength, maxLength, types } = input;
      return QueryClient.handleApiResponse(
        QueryClient.api.post<JourneyTypes.Journey[]>(
          '/api/v1/projects/{projectId}/journeys/detect',
          {
            body: { maxLength, minLength, types },
            params: { path: { projectId } },
          },
        ),
      );
    },
    onSuccess: async (
      _data: JourneyTypes.Journey[],
      variables: JourneyTypes.DetectJourneysInput,
    ): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.list(variables.projectId),
      });
    },
  };

  let mergedOptions = baseOptions;
  if (options) {
    mergedOptions = Object.assign(baseOptions, options);
  }

  return ReactQueryHooks.useMutation<
    JourneyTypes.Journey[],
    Error,
    JourneyTypes.DetectJourneysInput
  >(mergedOptions);
};

const useCreateJourney = (
  options?: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey,
    Error,
    JourneyTypes.CreateJourneyInput
  >,
): ReactQuery.UseMutationResult<JourneyTypes.Journey, Error, JourneyTypes.CreateJourneyInput> => {
  const queryClient = ReactQueryHooks.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey,
    Error,
    JourneyTypes.CreateJourneyInput
  > = {
    mutationFn: async (input: JourneyTypes.CreateJourneyInput): Promise<JourneyTypes.Journey> => {
      const { projectId, name, description, type, itemIds, metadata } = input;
      return QueryClient.handleApiResponse(
        QueryClient.api.post<JourneyTypes.Journey>('/api/v1/projects/{projectId}/journeys', {
          body: { description, itemIds, metadata, name, type },
          params: { path: { projectId } },
        }),
      );
    },
    onSuccess: async (data: JourneyTypes.Journey): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.list(data.projectId),
      });
    },
  };

  let mergedOptions = baseOptions;
  if (options) {
    mergedOptions = Object.assign(baseOptions, options);
  }

  return ReactQueryHooks.useMutation<JourneyTypes.Journey, Error, JourneyTypes.CreateJourneyInput>(
    mergedOptions,
  );
};

const useUpdateJourney = (
  options?: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey,
    Error,
    { journeyId: string; data: JourneyTypes.UpdateJourneyInput }
  >,
): ReactQuery.UseMutationResult<
  JourneyTypes.Journey,
  Error,
  { journeyId: string; data: JourneyTypes.UpdateJourneyInput }
> => {
  const queryClient = ReactQueryHooks.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey,
    Error,
    { journeyId: string; data: JourneyTypes.UpdateJourneyInput }
  > = {
    mutationFn: async (input: {
      journeyId: string;
      data: JourneyTypes.UpdateJourneyInput;
    }): Promise<JourneyTypes.Journey> =>
      QueryClient.handleApiResponse(
        QueryClient.api.put<JourneyTypes.Journey>('/api/v1/journeys/{journeyId}', {
          body: input.data,
          params: { path: { journeyId: input.journeyId } },
        }),
      ),
    onSuccess: async (data: JourneyTypes.Journey): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.detail(data.id),
      });
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.list(data.projectId),
      });
    },
  };

  let mergedOptions = baseOptions;
  if (options) {
    mergedOptions = Object.assign(baseOptions, options);
  }

  return ReactQueryHooks.useMutation<
    JourneyTypes.Journey,
    Error,
    { journeyId: string; data: JourneyTypes.UpdateJourneyInput }
  >(mergedOptions);
};

const useDeleteJourney = (
  options?: ReactQuery.UseMutationOptions<void, Error, string>,
): ReactQuery.UseMutationResult<void, Error, string> => {
  const queryClient = ReactQueryHooks.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<void, Error, string> = {
    mutationFn: async (journeyId: string): Promise<void> =>
      QueryClient.handleApiResponse(
        QueryClient.api.del<void>('/api/v1/journeys/{journeyId}', {
          params: { path: { journeyId } },
        }),
      ),
    onSuccess: async (): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.lists(),
      });
    },
  };

  let mergedOptions = baseOptions;
  if (options) {
    mergedOptions = Object.assign(baseOptions, options);
  }

  return ReactQueryHooks.useMutation<void, Error, string>(mergedOptions);
};

const useAddJourneyStep = (
  options?: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey,
    Error,
    { journeyId: string; itemId: string; order?: number }
  >,
): ReactQuery.UseMutationResult<
  JourneyTypes.Journey,
  Error,
  { journeyId: string; itemId: string; order?: number }
> => {
  const queryClient = ReactQueryHooks.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<
    JourneyTypes.Journey,
    Error,
    { journeyId: string; itemId: string; order?: number }
  > = {
    mutationFn: async (input: {
      journeyId: string;
      itemId: string;
      order?: number;
    }): Promise<JourneyTypes.Journey> =>
      QueryClient.handleApiResponse(
        QueryClient.api.post<JourneyTypes.Journey>('/api/v1/journeys/{journeyId}/steps', {
          body: { itemId: input.itemId, order: input.order },
          params: { path: { journeyId: input.journeyId } },
        }),
      ),
    onSuccess: async (data: JourneyTypes.Journey): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.detail(data.id),
      });
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.steps(data.id),
      });
    },
  };

  let mergedOptions = baseOptions;
  if (options) {
    mergedOptions = Object.assign(baseOptions, options);
  }

  return ReactQueryHooks.useMutation<
    JourneyTypes.Journey,
    Error,
    { journeyId: string; itemId: string; order?: number }
  >(mergedOptions);
};

const useRemoveJourneyStep = (
  options?: ReactQuery.UseMutationOptions<void, Error, { journeyId: string; stepItemId: string }>,
): ReactQuery.UseMutationResult<void, Error, { journeyId: string; stepItemId: string }> => {
  const queryClient = ReactQueryHooks.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<
    void,
    Error,
    { journeyId: string; stepItemId: string }
  > = {
    mutationFn: async (input: { journeyId: string; stepItemId: string }): Promise<void> =>
      QueryClient.handleApiResponse(
        QueryClient.api.del<void>('/api/v1/journeys/{journeyId}/steps/{itemId}', {
          params: {
            path: { itemId: input.stepItemId, journeyId: input.journeyId },
          },
        }),
      ),
    onSuccess: async (
      _data: void,
      variables: { journeyId: string; stepItemId: string },
    ): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.detail(variables.journeyId),
      });
      await queryClient.invalidateQueries({
        queryKey: JourneyKeys.journeyQueryKeys.steps(variables.journeyId),
      });
    },
  };

  let mergedOptions = baseOptions;
  if (options) {
    mergedOptions = Object.assign(baseOptions, options);
  }

  return ReactQueryHooks.useMutation<void, Error, { journeyId: string; stepItemId: string }>(
    mergedOptions,
  );
};

export {
  useAddJourneyStep,
  useCreateJourney,
  useDeleteJourney,
  useDetectJourneys,
  useRemoveJourneyStep,
  useUpdateJourney,
};
