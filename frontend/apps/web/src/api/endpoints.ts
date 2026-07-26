import type {
  CreateItemInput,
  CreateLinkInput,
  CreateProjectInput,
  CursorPaginationResponse,
  DependencyAnalysis,
  GraphData,
  ImpactAnalysis,
  Item,
  Link,
  PaginationParams,
  Project,
  SearchQuery,
  SearchResult,
  UpdateItemInput,
  UpdateLinkInput,
  UpdateProjectInput,
} from './types';

// Complete API Client for TraceRTM Backend
/* oxlint-disable import/no-named-export, import/group-exports, import/max-dependencies, eslint/arrow-body-style, eslint/require-await, eslint/new-cap, eslint/no-ternary, eslint/sort-keys, eslint/sort-imports, eslint/id-length, eslint/max-lines, typescript-eslint/array-type, typescript-eslint/explicit-function-return-type, typescript-eslint/explicit-module-boundary-types, oxc/no-async-await */
import { client } from './client';

const { apiClient, handleApiResponse, safeApiCall } = client;

// ============================================================================
// PROJECT ENDPOINTS
// ============================================================================

export const projectsApi = {
  list: async (params?: PaginationParams): Promise<Project[]> => {
    const response = await handleApiResponse<{
      total: number;
      projects: Project[];
    }>(
      safeApiCall(
        apiClient.GET('/api/v1/projects', {
          params: { query: params },
        }),
      ),
    );
    // API returns { total: number, projects: Project[] }, extract projects array
    return Array.isArray(response) ? response : response.projects || [];
  },

  get: async (id: string): Promise<Project> => {
    return handleApiResponse(
      safeApiCall(
        apiClient.GET('/api/v1/projects/{id}', {
          params: { path: { id } },
        }),
      ),
    );
  },

  create: async (data: CreateProjectInput): Promise<Project> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/projects', {
        body: data,
      }),
    );
  },

  update: async (id: string, data: UpdateProjectInput): Promise<Project> => {
    return handleApiResponse(
      apiClient.PUT('/api/v1/projects/{id}', {
        params: { path: { id } },
        body: data,
      }),
    );
  },

  delete: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/projects/{id}', {
        params: { path: { id } },
      }),
    );
  },
};

// ============================================================================
// ITEM ENDPOINTS
// ============================================================================

export const itemsApi = {
  list: async (
    params?: PaginationParams & { project_id?: string },
  ): Promise<Item[] | CursorPaginationResponse<Item>> => {
    const response = await handleApiResponse<
      { total: number; items: Item[] } | CursorPaginationResponse<Item> | Item[]
    >(
      apiClient.GET('/api/v1/items', {
        params: { query: params },
      }),
    );
    // Handle different response formats:
    // 1. Array of items (old format)
    // 2. Cursor pagination response (new format with cursor)
    // 3. Legacy offset pagination response (with total)
    if (Array.isArray(response)) {
      return response;
    }
    if ('next_cursor' in response || 'has_more' in response) {
      // Return full cursor pagination response
      return response;
    }
    // Legacy format with total
    return response.items || [];
  },

  get: async (id: string): Promise<Item> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/items/{id}', {
        params: { path: { id } },
      }),
    );
  },

  create: async (data: CreateItemInput): Promise<Item> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/items', {
        body: data,
      }),
    );
  },

  update: async (id: string, data: UpdateItemInput): Promise<Item> => {
    return handleApiResponse(
      apiClient.PUT('/api/v1/items/{id}', {
        params: { path: { id } },
        body: data,
      }),
    );
  },

  delete: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/items/{id}', {
        params: { path: { id } },
      }),
    );
  },
};

// ============================================================================
// LINK ENDPOINTS
// ============================================================================

export const linksApi = {
  list: async (params?: PaginationParams): Promise<Link[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/links', {
        params: { query: params },
      }),
    );
  },

  get: async (id: string): Promise<Link> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/links/{id}', {
        params: { path: { id } },
      }),
    );
  },

  create: async (data: CreateLinkInput): Promise<Link> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/links', {
        body: data,
      }),
    );
  },

  update: async (id: string, data: UpdateLinkInput): Promise<Link> => {
    return handleApiResponse(
      apiClient.PUT('/api/v1/links/{id}', {
        params: { path: { id } },
        body: data,
      }),
    );
  },

  delete: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/links/{id}', {
        params: { path: { id } },
      }),
    );
  },
};

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
      }),
    );
  },

  getDescendants: async (id: string, depth?: number): Promise<GraphData> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/descendants/{id}', {
        params: {
          path: { id },
          query: { depth },
        },
      }),
    );
  },

  findPath: async (sourceId: string, targetId: string): Promise<Item[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/path', {
        params: {
          query: { source: sourceId, target: targetId },
        },
      }),
    );
  },

  findAllPaths: async (sourceId: string, targetId: string): Promise<Item[][]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/paths', {
        params: {
          query: { source: sourceId, target: targetId },
        },
      }),
    );
  },

  getFullGraph: async (projectId?: string): Promise<GraphData> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/full', {
        params: {
          query: { project_id: projectId },
        },
      }),
    );
  },

  // Alias for compatibility
  get: async (projectId?: string): Promise<GraphData> => {
    return graphApi.getFullGraph(projectId);
  },

  detectCycles: async (projectId?: string): Promise<string[][]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/cycles', {
        params: {
          query: { project_id: projectId },
        },
      }),
    );
  },

  topologicalSort: async (projectId?: string): Promise<Item[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/topo-sort', {
        params: {
          query: { project_id: projectId },
        },
      }),
    );
  },

  getImpactAnalysis: async (id: string, depth?: number): Promise<ImpactAnalysis> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/impact/{id}', {
        params: {
          path: { id },
          query: { depth },
        },
      }),
    );
  },

  getDependencyAnalysis: async (id: string, depth?: number): Promise<DependencyAnalysis> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/dependencies/{id}', {
        params: {
          path: { id },
          query: { depth },
        },
      }),
    );
  },

  getOrphanItems: async (projectId?: string): Promise<Item[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/orphans', {
        params: {
          query: { project_id: projectId },
        },
      }),
    );
  },

  traverse: async (
    id: string,
    direction: 'up' | 'down' | 'both',
    depth?: number,
  ): Promise<GraphData> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/graph/traverse/{id}', {
        params: {
          path: { id },
          query: { direction, depth },
        },
      }),
    );
  },
};

// ============================================================================
// SEARCH ENDPOINTS (commented out in backend, but prepared for future use)
// ============================================================================

export const searchApi = {
  search: async (query: SearchQuery): Promise<SearchResult> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/search', {
        body: query,
      }),
    );
  },

  searchGet: async (params: SearchQuery): Promise<SearchResult> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/search', {
        params: { query: params },
      }),
    );
  },

  suggest: async (q: string, limit?: number): Promise<string[]> => {
    return handleApiResponse(
      apiClient.GET('/api/v1/search/suggest', {
        params: {
          query: { q, limit },
        },
      }),
    );
  },

  indexItem: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.POST('/api/v1/search/index/{id}', {
        params: { path: { id } },
      }),
    );
  },

  batchIndex: async (ids: string[]): Promise<void> => {
    await handleApiResponse(
      apiClient.POST('/api/v1/search/batch-index', {
        body: { ids },
      }),
    );
  },

  reindexAll: async (): Promise<void> => {
    await handleApiResponse(safeApiCall(apiClient.POST('/api/v1/search/reindex', {})));
  },

  getStats: async () => {
    return handleApiResponse(apiClient.GET('/api/v1/search/stats', {}));
  },

  getHealth: async () => {
    return handleApiResponse(apiClient.GET('/api/v1/search/health', {}));
  },

  deleteIndex: async (id: string): Promise<void> => {
    await handleApiResponse(
      apiClient.DELETE('/api/v1/search/index/{id}', {
        params: { path: { id } },
      }),
    );
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export const healthCheck = async (): Promise<{
  status: string;
  service: string;
}> => {
  return handleApiResponse(apiClient.GET('/health', {}));
};

// ============================================================================
// EXPORT/IMPORT ENDPOINTS
// ============================================================================

/** Canonical full export: project + items + links (TraceRTM canonical format) */
export interface CanonicalExport {
  project: {
    id: string;
    name: string;
    description?: string;
    created_at?: string;
  };
  items: Array<{
    id: string;
    title: string;
    view: string;
    type: string;
    status: string;
    description?: string;
    version?: number;
  }>;
  links: Array<{ source_id: string; target_id: string; type: string }>;
}

/** Result of full import (create new project from canonical JSON) */
export interface ImportFullResult {
  project_id: string;
  items_imported: number;
  links_imported: number;
}

const isCanonicalExport = (value: unknown): value is CanonicalExport =>
  typeof value === 'object' &&
  value !== null &&
  'project' in value &&
  'items' in value &&
  'links' in value;

const hasContentString = (value: unknown): value is { content: string } =>
  typeof value === 'object' &&
  value !== null &&
  'content' in value &&
  typeof (value as Record<string, unknown>)['content'] === 'string';

export const exportImportApi = {
  export: async (
    projectId: string,
    format: 'json' | 'csv' | 'markdown' | 'full' = 'json',
  ): Promise<Blob | CanonicalExport> => {
    const response = await handleApiResponse<Record<string, unknown>>(
      apiClient.GET('/api/v1/projects/{project_id}/export', {
        params: { path: { project_id: projectId }, query: { format } },
      }),
    );
    if (format === 'full' && isCanonicalExport(response)) {
      return response;
    }
    // Backend returns object; build Blob for download (json/csv/markdown)
    if (hasContentString(response)) {
      return new Blob([response['content']], {
        type: format === 'csv' ? 'text/csv' : 'text/markdown',
      });
    }
    return new Blob([JSON.stringify(response)], { type: 'application/json' });
  },

  /** Export one project as canonical JSON (project + items + links). */
  exportFull: async (projectId: string): Promise<CanonicalExport> => {
    const out = await exportImportApi.export(projectId, 'full');
    if (isCanonicalExport(out)) {
      return out;
    }
    throw new Error('Expected canonical export format');
  },

  import: async (
    projectId: string,
    format: 'json' | 'csv',
    data: string,
  ): Promise<{
    success: boolean;
    imported_count: number;
    error_count: number;
    errors: string[];
  }> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/projects/{project_id}/import', {
        params: { path: { project_id: projectId } },
        body: { format, data },
      }),
    );
  },

  /** Import canonical JSON as a new project (POST /api/v1/import). */
  importFull: async (canonicalJson: CanonicalExport): Promise<ImportFullResult> => {
    return handleApiResponse(
      apiClient.POST('/api/v1/import', {
        body: canonicalJson as unknown,
      }),
    );
  },

  // Aliases for compatibility
  exportProject: async (
    projectId: string,
    format: 'json' | 'csv' | 'markdown' = 'json',
  ): Promise<Blob> => {
    const out = await exportImportApi.export(projectId, format);
    if (out instanceof Blob) {
      return out;
    }
    throw new Error('Expected Blob format');
  },

  importProject: async (
    projectId: string,
    format: 'json' | 'csv',
    data: string,
  ): Promise<{
    success: boolean;
    imported_count: number;
    error_count: number;
    errors: string[];
  }> => {
    return exportImportApi.import(projectId, format, data);
  },
};

// Export all APIs as a single object for convenience
export const api = {
  projects: projectsApi,
  items: itemsApi,
  links: linksApi,
  graph: graphApi,
  search: searchApi,
  exportImport: exportImportApi,
  healthCheck,
};
