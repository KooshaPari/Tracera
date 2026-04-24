const componentLibraryQueryKeys = {
  all: ['componentLibrary'] as const,
  component: (componentId: string) => ['componentLibrary', 'component', componentId] as const,
  components: (libraryId: string) => ['componentLibrary', 'components', libraryId] as const,
  detail: (id: string) => [...componentLibraryQueryKeys.details(), id] as const,
  details: () => [...componentLibraryQueryKeys.all, 'detail'] as const,
  list: (projectId: string) => [...componentLibraryQueryKeys.lists(), projectId] as const,
  lists: () => [...componentLibraryQueryKeys.all, 'list'] as const,
  tokens: (libraryId: string) => ['componentLibrary', 'tokens', libraryId] as const,
  usage: (componentId: string) => ['componentLibrary', 'usage', componentId] as const,
};

export { componentLibraryQueryKeys };
