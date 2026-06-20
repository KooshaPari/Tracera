import type * as ReactQuery from '@tanstack/react-query';

import type * as JourneyTypes from './journeys-types';

import * as JourneyKeys from './journeys-keys';
import * as QueryClient from './query-client';
import * as ReactQueryHooks from './react-query-hooks';

const useDerivedJourneys = (
  projectId: string,
  type?: string,
  options?: ReactQuery.UseQueryOptions<JourneyTypes.Journey[]>,
): ReactQuery.UseQueryResult<JourneyTypes.Journey[]> => {
  const queryParams: { type?: string } = {};
  const hasType = typeof type === 'string' && type !== '';
  if (hasType) {
    queryParams.type = type;
  }
  const baseOptions = {
    enabled: Boolean(projectId),
    queryFn: async (): Promise<JourneyTypes.Journey[]> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<JourneyTypes.Journey[]>('/api/v1/projects/{projectId}/journeys', {
          params: {
            path: { projectId },
            query: queryParams,
          },
        }),
      ),
    queryKey: JourneyKeys.journeyQueryKeys.list(projectId, type),
  };

  if (options) {
    return ReactQueryHooks.useQuery(Object.assign(baseOptions, options));
  }

  return ReactQueryHooks.useQuery(baseOptions);
};

const useJourney = (
  journeyId: string,
  options?: ReactQuery.UseQueryOptions<JourneyTypes.Journey>,
): ReactQuery.UseQueryResult<JourneyTypes.Journey> => {
  const baseOptions = {
    enabled: Boolean(journeyId),
    queryFn: async (): Promise<JourneyTypes.Journey> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<JourneyTypes.Journey>('/api/v1/journeys/{journeyId}', {
          params: { path: { journeyId } },
        }),
      ),
    queryKey: JourneyKeys.journeyQueryKeys.detail(journeyId),
  };

  if (options) {
    return ReactQueryHooks.useQuery(Object.assign(baseOptions, options));
  }

  return ReactQueryHooks.useQuery(baseOptions);
};

const useJourneySteps = (
  journeyId: string,
  options?: ReactQuery.UseQueryOptions<JourneyTypes.JourneyStep[]>,
): ReactQuery.UseQueryResult<JourneyTypes.JourneyStep[]> => {
  const baseOptions = {
    enabled: Boolean(journeyId),
    queryFn: async (): Promise<JourneyTypes.JourneyStep[]> =>
      QueryClient.handleApiResponse(
        QueryClient.api.get<JourneyTypes.JourneyStep[]>('/api/v1/journeys/{journeyId}/steps', {
          params: { path: { journeyId } },
        }),
      ),
    queryKey: JourneyKeys.journeyQueryKeys.steps(journeyId),
  };

  if (options) {
    return ReactQueryHooks.useQuery(Object.assign(baseOptions, options));
  }

  return ReactQueryHooks.useQuery(baseOptions);
};

export { useDerivedJourneys, useJourney, useJourneySteps };
