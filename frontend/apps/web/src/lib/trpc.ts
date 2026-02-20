/**
 * TRPC Integration for TraceRTM (Placeholder/Stub)
 *
 * This is a placeholder implementation for future TRPC integration.
 * Currently, the app uses OpenAPI/REST endpoints via apiClient.
 *
 * When TRPC backend is ready, this file will be updated to:
 * - Import actual AppRouter from @/server/trpc
 * - Replace REST calls with type-safe TRPC procedures
 * - Enable real-time subscriptions
 */

// Placeholder AppRouter type - will be replaced with actual router when backend is ready
export type AppRouter = {
  projects: {
    list: { useQuery: () => any };
    get: { useQuery: (id: string) => any };
    create: { useMutation: () => any };
    update: { useMutation: () => any };
    delete: { useMutation: () => any };
    getMetrics: { useQuery: () => any };
    exportData: { useMutation: () => any };
    getAuditHistory: { useQuery: () => any };
  };
  items: {
    list: { useQuery: (params?: any) => any };
    get: { useQuery: (id: string) => any };
    create: { useMutation: () => any };
    update: { useMutation: () => any };
    delete: { useMutation: () => any };
    search: { useQuery: (query: string) => any };
    getFeatures: { useQuery: (projectId: string) => any };
    getCode: { useQuery: (projectId: string) => any };
    getTests: { useQuery: (projectId: string) => any };
    getApis: { useQuery: (projectId: string) => any };
    getDatabases: { useQuery: (projectId: string) => any };
    getWireframes: { useQuery: (projectId: string) => any };
    bulkCreate: { useMutation: () => any };
    bulkUpdate: { useMutation: () => any };
    bulkDelete: { useMutation: () => any };
    clone: { useMutation: () => any };
    getImpact: { useQuery: (id: string) => any };
    getTraceability: { useQuery: (id: string) => any };
    getDependencies: { useQuery: (id: string) => any };
  };
  links: {
    list: { useQuery: (params?: any) => any };
    create: { useMutation: () => any };
    delete: { useMutation: () => any };
    getTransitive: { useQuery: (id: string) => any };
    getCycles: { useQuery: (projectId: string) => any };
    getPaths: { useQuery: (params: { from: string; to: string }) => any };
    validateRelationships: { useQuery: (projectId: string) => any };
    mergeDuplicateLinks: { useMutation: () => any };
  };
  subscriptions: {
    onProjectChange: { useSubscription: (params: any, options?: any) => any };
    onItemUpdate: { useSubscription: (params: any, options?: any) => any };
    onLinkChange: { useSubscription: (params: any, options?: any) => any };
  };
};

// Placeholder TRPC React client - will be replaced when @trpc/react-query is properly configured
export const trpc = {
  createClient: (_config: any) => ({
    links: [],
  }),
  projects: {
    list: { useQuery: () => ({ data: [], isLoading: false, error: null }) },
    get: {
      useQuery: (_id: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    create: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    update: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    delete: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    getMetrics: {
      useQuery: () => ({ data: null, isLoading: false, error: null }),
    },
    exportData: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    getAuditHistory: {
      useQuery: () => ({ data: [], isLoading: false, error: null }),
    },
  },
  items: {
    list: {
      useQuery: (_params?: any) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    get: {
      useQuery: (_id: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    create: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    update: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    delete: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    search: {
      useQuery: (_query: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    getFeatures: {
      useQuery: (_projectId: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    getCode: {
      useQuery: (_projectId: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    getTests: {
      useQuery: (_projectId: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    getApis: {
      useQuery: (_projectId: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    getDatabases: {
      useQuery: (_projectId: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    getWireframes: {
      useQuery: (_projectId: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    bulkCreate: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    bulkUpdate: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    bulkDelete: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    clone: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    getImpact: {
      useQuery: (_id: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    getTraceability: {
      useQuery: (_id: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    getDependencies: {
      useQuery: (_id: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
  },
  links: {
    list: {
      useQuery: (_params?: any) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    create: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    delete: { useMutation: () => ({ mutate: () => {}, isLoading: false }) },
    getTransitive: {
      useQuery: (_id: string) => ({ data: [], isLoading: false, error: null }),
    },
    getCycles: {
      useQuery: (_projectId: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    getPaths: {
      useQuery: (_params: { from: string; to: string }) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    validateRelationships: {
      useQuery: (_projectId: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    mergeDuplicateLinks: {
      useMutation: () => ({ mutate: () => {}, isLoading: false }),
    },
  },
  search: {
    semantic: {
      useQuery: (_query: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    hybrid: {
      useQuery: (_query: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    suggestions: {
      useQuery: (_query: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    withContext: {
      useQuery: (_params: any) => ({ data: [], isLoading: false, error: null }),
    },
    fuzzy: {
      useQuery: (_query: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    phonetic: {
      useQuery: (_query: string) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
  },
  graph: {
    getData: {
      useQuery: (_params: any) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    getSubgraph: {
      useQuery: (_params: any) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    getNeighbors: {
      useQuery: (_id: string) => ({ data: [], isLoading: false, error: null }),
    },
    shortestPath: {
      useQuery: (_params: { from: string; to: string }) => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    },
    centrality: {
      useQuery: (_projectId: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    clustering: {
      useQuery: (_projectId: string) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
  },
  subscriptions: {
    onProjectChange: {
      useSubscription: (_params: any, _options?: any) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    onItemUpdate: {
      useSubscription: (_params: any, _options?: any) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
    onLinkChange: {
      useSubscription: (_params: any, _options?: any) => ({
        data: null,
        isLoading: false,
        error: null,
      }),
    },
  },
} as any;

/**
 * Placeholder TRPC client factory
 * Will be replaced with actual TRPC client when backend is ready
 */
export const createTRPCClient = () => {
  return {
    links: [],
  };
};

/**
 * Placeholder API procedures
 * These will be replaced with actual TRPC procedures when backend is ready
 */
export const apiProcedures = {
  projects: trpc.projects,
  items: trpc.items,
  links: trpc.links,
  search: trpc.search,
  graph: trpc.graph,
  subscriptions: trpc.subscriptions,
};

/**
 * Migration utilities placeholder
 * Will be implemented when TRPC backend is ready
 */
export const migrateToTRPC = {
  projects: () => apiProcedures.projects.list.useQuery(),
  projectItems: (_projectId: string, _filters?: any) =>
    apiProcedures.items.list.useQuery({ projectId: _projectId, ..._filters }),
  realtime: {
    subscribe: (_channel: string, _callback: (event: any) => void) => {
      // Placeholder - will be implemented with actual TRPC subscriptions
      return apiProcedures.subscriptions.onItemUpdate.useSubscription(
        { channel: _channel },
        { onData: _callback },
      );
    },
  },
};
