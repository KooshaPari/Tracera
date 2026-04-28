/**
 * TanStack Query Configuration
 *
 * Tiered caching strategies based on data type:
 * - Static: Rarely changing data (projects list, item types)
 * - Dynamic: Frequently changing data (items, links)
 * - Graph: Expensive computations (graph data, traversals)
 * - Realtime: Live data (websocket-backed, notifications)
 */

export const QUERY_CONFIGS = {
  /**
   * Static data - projects list, item types, schemas
   * Changes rarely, safe to cache longer
   */
  static: {
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  },

  /**
   * Dynamic data - items, links, specifications
   * Changes frequently, needs fresher data
   */
  dynamic: {
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  },

  /**
   * Graph data - expensive graph computations
   * Moderate staleness acceptable, expensive to recompute
   */
  graph: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  },

  /**
   * Realtime data - websocket-backed, notifications
   * Always stale, refresh frequently
   */
  realtime: {
    staleTime: 0, // Always stale
    gcTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 5000, // 5 seconds
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  },

  /**
   * User session data - auth state, preferences
   * Should persist but validate on mount
   */
  session: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  },

  /**
   * Default configuration - moderate staleness
   */
  default: {
    staleTime: 60 * 1000, // 1 minute
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  },
} as const;

/**
 * Query key factories for consistent cache management
 */
export const queryKeys = {
  // Projects
  projects: {
    all: ['projects'] as const,
    list: () => [...queryKeys.projects.all, 'list'] as const,
    detail: (id: string) => [...queryKeys.projects.all, 'detail', id] as const,
  },

  // Items
  items: {
    all: ['items'] as const,
    list: (projectId: string) => [...queryKeys.items.all, 'list', projectId] as const,
    detail: (id: string) => [...queryKeys.items.all, 'detail', id] as const,
    recent: () => [...queryKeys.items.all, 'recent'] as const,
  },

  // Links
  links: {
    all: ['links'] as const,
    list: (projectId: string) => [...queryKeys.links.all, 'list', projectId] as const,
    byItem: (itemId: string) => [...queryKeys.links.all, 'byItem', itemId] as const,
  },

  // Graph
  graph: {
    all: ['graph'] as const,
    full: (projectId: string) => [...queryKeys.graph.all, 'full', projectId] as const,
    ancestors: (itemId: string, depth?: number) =>
      [...queryKeys.graph.all, 'ancestors', itemId, depth] as const,
    descendants: (itemId: string, depth?: number) =>
      [...queryKeys.graph.all, 'descendants', itemId, depth] as const,
    impact: (itemId: string) => [...queryKeys.graph.all, 'impact', itemId] as const,
  },

  // Specifications
  specs: {
    all: ['specs'] as const,
    list: (projectId: string) => [...queryKeys.specs.all, 'list', projectId] as const,
    detail: (id: string) => [...queryKeys.specs.all, 'detail', id] as const,
  },

  // System
  system: {
    status: () => ['system', 'status'] as const,
    health: () => ['system', 'health'] as const,
  },

  // Temporal (Branches & Versions)
  branches: ['branches'] as const,
  versions: ['versions'] as const,
  versionSnapshot: ['versionSnapshot'] as const,
  branchComparison: ['branchComparison'] as const,

  // Search
  search: {
    all: ['search'] as const,
    query: (q: string) => [...queryKeys.search.all, 'query', q] as const,
  },

  // Executions
  executions: {
    all: ['executions'] as const,
    list: (projectId: string) => [...queryKeys.executions.all, 'list', projectId] as const,
    detail: (id: string) => [...queryKeys.executions.all, 'detail', id] as const,
  },

  // Codex
  codex: {
    all: ['codex'] as const,
    list: (projectId: string) => [...queryKeys.codex.all, 'list', projectId] as const,
    detail: (id: string) => [...queryKeys.codex.all, 'detail', id] as const,
  },
} as const;

/**
 * Helper to get config for a specific query type
 */
export function getQueryConfig(type: keyof typeof QUERY_CONFIGS) {
  return QUERY_CONFIGS[type];
}
