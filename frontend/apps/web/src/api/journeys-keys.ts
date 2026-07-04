const journeyQueryKeys = {
  all: ['journeys'] as const,
  detail: (id: string) => [...journeyQueryKeys.details(), id] as const,
  details: () => [...journeyQueryKeys.all, 'detail'] as const,
  list: (projectId: string, type?: string) =>
    [...journeyQueryKeys.lists(), projectId, type] as const,
  lists: () => [...journeyQueryKeys.all, 'list'] as const,
  steps: (journeyId: string) => ['journeys', 'steps', journeyId] as const,
};

export { journeyQueryKeys };
