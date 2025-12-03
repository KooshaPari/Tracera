// Complete API Client for TraceRTM Backend
import { apiClient, handleApiResponse, safeApiCall } from './client'
import type {
  Agent,
  AgentTask,
  CreateAgentInput,
  CreateItemInput,
  CreateLinkInput,
  CreateProjectInput,
  DependencyAnalysis,
  GraphData,
  ImpactAnalysis,
  Item,
  Link,
  PaginationParams,
  Project,
  SearchQuery,
  SearchResult,
  TaskError,
  TaskResult,
  UpdateAgentInput,
  UpdateItemInput,
  UpdateLinkInput,
  UpdateProjectInput,
} from './types'

// ============================================================================
// PROJECT ENDPOINTS
// ============================================================================

export const projectsApi = {
  list: async (params?: PaginationParams): Promise<Project[]> => {
    return handleApiResponse(
      safeApiCall(
        apiClient.GET('/api/v1/projects', {
          params: { query: params },
        })
      )
    )
  },

  get: async (id: string): Promise<Project> => {
    return handleApiResponse(
      safeApiCall(
        apiClient.GET('/api/v1/projects/{id}', {
          params: { path: { id } },
        })
      )
    )
  },

  create: async (data: CreateProjectInput): Promise<Project> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/projects', {
        body: data,
      })
    )
  },

  update: async (id: string, data: UpdateProjectInput): Promise<Project> => {
    return handleApiResponse(
      apiClient.PUT('/api/v1/projects/{id}', {
        params: { path: { id } },
        body: data,
      })
    )
  },

  delete: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/projects/{id}', {
        params: { path: { id } },
      })
    )
  },
}

// ============================================================================
// ITEM ENDPOINTS
// ============================================================================

export const itemsApi = {
  list: async (params?: PaginationParams & { project_id?: string }): Promise<Item[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/items', {
        params: { query: params },
      })
    )
  },

  get: async (id: string): Promise<Item> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/items/{id}', {
        params: { path: { id } },
      })
    )
  },

  create: async (data: CreateItemInput): Promise<Item> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/items', {
        body: data,
      })
    )
  },

  update: async (id: string, data: UpdateItemInput): Promise<Item> => {
    return handleApiResponse(
      apiClient.PUT('/api/v1/items/{id}', {
        params: { path: { id } },
        body: data,
      })
    )
  },

  delete: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/items/{id}', {
        params: { path: { id } },
      })
    )
  },
}

// ============================================================================
// LINK ENDPOINTS
// ============================================================================

export const linksApi = {
  list: async (params?: PaginationParams): Promise<Link[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/links', {
        params: { query: params },
      })
    )
  },

  get: async (id: string): Promise<Link> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/links/{id}', {
        params: { path: { id } },
      })
    )
  },

  create: async (data: CreateLinkInput): Promise<Link> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/links', {
        body: data,
      })
    )
  },

  update: async (id: string, data: UpdateLinkInput): Promise<Link> => {
    return handleApiResponse(
      apiClient.PUT('/api/v1/links/{id}', {
        params: { path: { id } },
        body: data,
      })
    )
  },

  delete: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/links/{id}', {
        params: { path: { id } },
      })
    )
  },
}

// ============================================================================
// AGENT ENDPOINTS
// ============================================================================

export const agentsApi = {
  list: async (params?: PaginationParams): Promise<Agent[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/agents', {
        params: { query: params },
      })
    )
  },

  get: async (id: string): Promise<Agent> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/agents/{id}', {
        params: { path: { id } },
      })
    )
  },

  create: async (data: CreateAgentInput): Promise<Agent> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/agents', {
        body: data,
      })
    )
  },

  update: async (id: string, data: UpdateAgentInput): Promise<Agent> => {
    return handleApiResponse(
      apiClient.PUT('/api/v1/agents/{id}', {
        params: { path: { id } },
        body: data,
      })
    )
  },

  delete: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/agents/{id}', {
        params: { path: { id } },
      })
    )
  },

  // Agent Coordination
  register: async (data: CreateAgentInput): Promise<Agent> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/agents/register', {
        body: data,
      })
    )
  },

  heartbeat: async (agentId: string): Promise<void> => {
    await handleApiResponse(
      apiClient.POST('/api/v1/agents/heartbeat', {
        body: { agent_id: agentId },
      })
    )
  },

  getNextTask: async (agentId: string): Promise<AgentTask | null> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/agents/{id}/task', {
        params: { path: { id: agentId } },
      })
    )
  },

  submitTaskResult: async (data: TaskResult): Promise<void> => {
    await handleApiResponse(
      apiClient.POST('/api/v1/agents/task/result', {
        body: data,
      })
    )
  },

  submitTaskError: async (data: TaskError): Promise<void> => {
    await handleApiResponse(
      apiClient.POST('/api/v1/agents/task/error', {
        body: data,
      })
    )
  },

  assignTask: async (agentId: string, task: Partial<AgentTask>): Promise<AgentTask> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/agents/task/assign', {
        body: { agent_id: agentId, ...task },
      })
    )
  },

  listRegistered: async (): Promise<Agent[]> => {
    return handleApiResponse(apiClient.GET('/api/v1/agents/registered', {}))
  },

  getStatus: async (id: string): Promise<Agent> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/agents/{id}/status', {
        params: { path: { id } },
      })
    )
  },
}

// ============================================================================
// GRAPH ENDPOINTS
// ============================================================================

export const graphApi = {
  getAncestors: async (id: string, depth?: number): Promise<GraphData> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/ancestors/{id}', {
        params: {
          path: { id },
          query: { depth },
        },
      })
    )
  },

  getDescendants: async (id: string, depth?: number): Promise<GraphData> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/descendants/{id}', {
        params: {
          path: { id },
          query: { depth },
        },
      })
    )
  },

  findPath: async (sourceId: string, targetId: string): Promise<Item[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/path', {
        params: {
          query: { source: sourceId, target: targetId },
        },
      })
    )
  },

  findAllPaths: async (sourceId: string, targetId: string): Promise<Item[][]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/paths', {
        params: {
          query: { source: sourceId, target: targetId },
        },
      })
    )
  },

  getFullGraph: async (projectId?: string): Promise<GraphData> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/full', {
        params: {
          query: { project_id: projectId },
        },
      })
    )
  },

  detectCycles: async (projectId?: string): Promise<string[][]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/cycles', {
        params: {
          query: { project_id: projectId },
        },
      })
    )
  },

  topologicalSort: async (projectId?: string): Promise<Item[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/topo-sort', {
        params: {
          query: { project_id: projectId },
        },
      })
    )
  },

  getImpactAnalysis: async (id: string, depth?: number): Promise<ImpactAnalysis> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/impact/{id}', {
        params: {
          path: { id },
          query: { depth },
        },
      })
    )
  },

  getDependencyAnalysis: async (id: string, depth?: number): Promise<DependencyAnalysis> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/dependencies/{id}', {
        params: {
          path: { id },
          query: { depth },
        },
      })
    )
  },

  getOrphanItems: async (projectId?: string): Promise<Item[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/orphans', {
        params: {
          query: { project_id: projectId },
        },
      })
    )
  },

  traverse: async (
    id: string,
    direction: 'up' | 'down' | 'both',
    depth?: number
  ): Promise<GraphData> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/traverse/{id}', {
        params: {
          path: { id },
          query: { direction, depth },
        },
      })
    )
  },
}

// ============================================================================
// SEARCH ENDPOINTS (commented out in backend, but prepared for future use)
// ============================================================================

export const searchApi = {
  search: async (query: SearchQuery): Promise<SearchResult> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/search', {
        body: query,
      })
    )
  },

  searchGet: async (params: SearchQuery): Promise<SearchResult> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/search', {
        params: { query: params },
      })
    )
  },

  suggest: async (q: string, limit?: number): Promise<string[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/search/suggest', {
        params: {
          query: { q, limit },
        },
      })
    )
  },

  indexItem: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.POST('/api/v1/search/index/{id}', {
        params: { path: { id } },
      })
    )
  },

  batchIndex: async (ids: string[]): Promise<void> => {
    await handleApiResponse(
      apiClient.POST('/api/v1/search/batch-index', {
        body: { ids },
      })
    )
  },

  reindexAll: async (): Promise<void> => {
    await handleApiResponse(safeApiCall(apiClient.POST('/api/v1/search/reindex', {})))
  },

  getStats: async () => {
    return handleApiResponse(apiClient.GET('/api/v1/search/stats', {}))
  },

  getHealth: async () => {
    return handleApiResponse(apiClient.GET('/api/v1/search/health', {}))
  },

  deleteIndex: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/search/index/{id}', {
        params: { path: { id } },
      })
    )
  },
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export const healthCheck = async (): Promise<{ status: string; service: string }> => {
  return handleApiResponse(apiClient.GET('/health', {}))
}

// Export all APIs as a single object for convenience
export const api = {
  projects: projectsApi,
  items: itemsApi,
  links: linksApi,
  agents: agentsApi,
  graph: graphApi,
  search: searchApi,
  healthCheck,
}
