const queryKeys = {
  item: (id: string) => ['items', id] as const,
  mutations: (filters?: Record<string, unknown>) => ['mutations', filters] as const,
  project: (id: string) => ['projects', id] as const,
  projectItems: (projectId: string, filters?: Record<string, unknown>) =>
    ['projects', projectId, 'items', filters] as const,
  projectLinks: (projectId: string) => ['projects', projectId, 'links'] as const,
  projects: ['projects'] as const,
};

export { queryKeys };
