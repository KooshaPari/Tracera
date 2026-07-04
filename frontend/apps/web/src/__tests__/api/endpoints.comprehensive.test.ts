/**
 * Comprehensive tests for API endpoints
 * Goal: Increase coverage from 17% to 95%
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  exportImportApi,
  graphApi,
  healthCheck,
  itemsApi,
  linksApi,
  projectsApi,
  searchApi,
} from '../../api/endpoints';
import { mockItems, mockLinks, mockProjects } from '../mocks/data';

// Mock the client module - must use factory function for hoisting
vi.mock('../../api/client', () => {
  const mockApiClient = {
    DELETE: vi.fn(),
    GET: vi.fn(),
    POST: vi.fn(),
    PUT: vi.fn(),
    use: vi.fn(),
  };

  const mockHandleApiResponse = vi.fn();
  const mockSafeApiCall = vi.fn();

  class MockApiError extends Error {
    constructor(
      public status: number,
      public statusText: string,
      public data?: unknown,
    ) {
      super(`API Error ${status}: ${statusText}`);
      this.name = 'ApiError';
    }
  }

  return {
    client: {
      ApiError: MockApiError,
      apiClient: mockApiClient,
      handleApiResponse: mockHandleApiResponse,
      safeApiCall: mockSafeApiCall,
    },
  };
});

import { client } from '../../api/client';

const { ApiError, apiClient, handleApiResponse, safeApiCall } = client;

describe('API Endpoints - Comprehensive Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock: successful response
    vi.mocked(handleApiResponse).mockImplementation(async (promise: Promise<Response>) => {
      if (!promise) {
        throw new ApiError(500, 'Null promise');
      }
      const result = (await promise) as unknown as {
        error?: unknown;
        response?: { status?: number };
        data?: unknown;
      };
      if (result?.error) {
        throw new ApiError(result.response?.status ?? 500, 'Error', result.error as string);
      }
      return result?.data;
    });
    vi.mocked(safeApiCall).mockImplementation(async (promise: any) => {
      if (!promise) {
        throw new ApiError(500, 'Null promise');
      }
      return promise;
    });
  });

  // ============================================================================
  // PROJECTS API
  // ============================================================================

  describe(projectsApi, () => {
    describe('list', () => {
      it('should list projects without params', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockProjects,
          error: undefined,
          response: new Response(),
        });
        vi.mocked(safeApiCall).mockResolvedValue({
          data: mockProjects,
          error: undefined,
          response: new Response(),
        });

        const result = await projectsApi.list();
        expect(result).toEqual(mockProjects);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/projects', {
          params: { query: undefined },
        });
      });

      it('should list projects with pagination params', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockProjects,
          error: undefined,
          response: new Response(),
        });
        vi.mocked(safeApiCall).mockResolvedValue({
          data: mockProjects,
          error: undefined,
          response: new Response(),
        });

        const result = await projectsApi.list({ limit: 10, offset: 0 });
        expect(result).toEqual(mockProjects);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/projects', {
          params: { query: { limit: 10, offset: 0 } },
        });
      });

      it('should handle errors', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: undefined,
          error: { message: 'Not found' },
          response: new Response(null, { status: 404 }),
        });
        vi.mocked(safeApiCall).mockResolvedValue({
          data: undefined,
          error: { message: 'Not found' },
          response: new Response(null, { status: 404 }),
        });

        await expect(projectsApi.list()).rejects.toThrow();
      });
    });

    describe('get', () => {
      it('should get a project by id', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockProjects[0],
          error: undefined,
          response: new Response(),
        });
        vi.mocked(safeApiCall).mockResolvedValue({
          data: mockProjects[0],
          error: undefined,
          response: new Response(),
        });

        const result = await projectsApi.get('proj-1');
        expect(result).toEqual(mockProjects[0]);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/projects/{id}', {
          params: { path: { id: 'proj-1' } },
        });
      });

      it('should handle 404 errors', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: undefined,
          error: { message: 'Not found' },
          response: new Response(null, { status: 404 }),
        });
        vi.mocked(safeApiCall).mockResolvedValue({
          data: undefined,
          error: { message: 'Not found' },
          response: new Response(null, { status: 404 }),
        });

        await expect(projectsApi.get('non-existent')).rejects.toThrow();
      });
    });

    describe('create', () => {
      it('should create a project', async () => {
        const newProject = { description: 'Test', name: 'New Project' };
        const created = { ...mockProjects[0], ...newProject, id: 'new-id' };

        vi.mocked(apiClient.POST).mockResolvedValue({
          data: created,
          error: undefined,
          response: new Response(),
        });

        const result = await projectsApi.create(newProject);
        expect(result).toEqual(created);
        expect(apiClient.POST).toHaveBeenCalledWith('/api/v1/projects', {
          body: newProject,
        });
      });

      it('should handle creation errors', async () => {
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: undefined,
          error: { message: 'Validation failed' },
          response: new Response(null, { status: 400 }),
        });

        await expect(projectsApi.create({ name: '' })).rejects.toThrow();
      });
    });

    describe('update', () => {
      it('should update a project', async () => {
        const updates = { name: 'Updated Project' };
        const updated = { ...mockProjects[0], ...updates };

        vi.mocked(apiClient.PUT).mockResolvedValue({
          data: updated,
          error: undefined,
          response: new Response(),
        });

        const result = await projectsApi.update('proj-1', updates);
        expect(result).toEqual(updated);
        expect(apiClient.PUT).toHaveBeenCalledWith('/api/v1/projects/{id}', {
          body: updates,
          params: { path: { id: 'proj-1' } },
        });
      });
    });

    describe('delete', () => {
      it('should delete a project', async () => {
        vi.mocked(apiClient.DELETE).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });

        await expect(projectsApi.delete('proj-1')).resolves.toBeUndefined();
        expect(apiClient.DELETE).toHaveBeenCalledWith('/api/v1/projects/{id}', {
          params: { path: { id: 'proj-1' } },
        });
      });
    });
  });

  // ============================================================================
  // ITEMS API
  // ============================================================================

  describe(itemsApi, () => {
    describe('list', () => {
      it('should list items without params', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockItems,
          error: undefined,
          response: new Response(),
        });

        const result = await itemsApi.list();
        expect(result).toEqual(mockItems);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/items', {
          params: { query: undefined },
        });
      });

      it('should list items with project_id filter', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockItems,
          error: undefined,
          response: new Response(),
        });

        const result = await itemsApi.list({ project_id: 'proj-1' });
        expect(result).toEqual(mockItems);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/items', {
          params: { query: { project_id: 'proj-1' } },
        });
      });

      it('should list items with pagination and project_id', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockItems,
          error: undefined,
          response: new Response(),
        });

        const result = await itemsApi.list({
          limit: 10,
          offset: 0,
          project_id: 'proj-1',
        });
        expect(result).toEqual(mockItems);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/items', {
          params: { query: { limit: 10, offset: 0, project_id: 'proj-1' } },
        });
      });
    });

    describe('get', () => {
      it('should get an item by id', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockItems[0],
          error: undefined,
          response: new Response(),
        });

        const result = await itemsApi.get('item-1');
        expect(result).toEqual(mockItems[0]);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/items/{id}', {
          params: { path: { id: 'item-1' } },
        });
      });
    });

    describe('create', () => {
      it('should create an item', async () => {
        const newItem = {
          project_id: 'proj-1',
          status: 'pending' as const,
          title: 'New Item',
          type: 'feature' as const,
        };
        const created = { ...mockItems[0], ...newItem, id: 'new-id' };

        vi.mocked(apiClient.POST).mockResolvedValue({
          data: created,
          error: undefined,
          response: new Response(),
        });

        const result = await itemsApi.create(newItem);
        expect(result).toEqual(created);
        expect(apiClient.POST).toHaveBeenCalledWith('/api/v1/items', {
          body: newItem,
        });
      });
    });

    describe('update', () => {
      it('should update an item', async () => {
        const updates = { title: 'Updated Item' };
        const updated = { ...mockItems[0], ...updates };

        vi.mocked(apiClient.PUT).mockResolvedValue({
          data: updated,
          error: undefined,
          response: new Response(),
        });

        const result = await itemsApi.update('item-1', updates);
        expect(result).toEqual(updated);
      });
    });

    describe('delete', () => {
      it('should delete an item', async () => {
        vi.mocked(apiClient.DELETE).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });

        await expect(itemsApi.delete('item-1')).resolves.toBeUndefined();
      });
    });
  });

  // ============================================================================
  // LINKS API
  // ============================================================================

  describe(linksApi, () => {
    describe('list', () => {
      it('should list links', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockLinks,
          error: undefined,
          response: new Response(),
        });

        const result = await linksApi.list();
        expect(result).toEqual(mockLinks);
      });

      it('should list links with pagination', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockLinks,
          error: undefined,
          response: new Response(),
        });

        const result = await linksApi.list({ limit: 10, offset: 0 });
        expect(result).toEqual(mockLinks);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/links', {
          params: { query: { limit: 10, offset: 0 } },
        });
      });
    });

    describe('get', () => {
      it('should get a link by id', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockLinks[0],
          error: undefined,
          response: new Response(),
        });

        const result = await linksApi.get('link-1');
        expect(result).toEqual(mockLinks[0]);
      });
    });

    describe('create', () => {
      it('should create a link', async () => {
        const newLink = {
          source_id: 'item-1',
          target_id: 'item-2',
          type: 'implements' as const,
        };
        const created = { ...mockLinks[0], ...newLink, id: 'new-link' };

        vi.mocked(apiClient.POST).mockResolvedValue({
          data: created,
          error: undefined,
          response: new Response(),
        });

        const result = await linksApi.create(newLink);
        expect(result).toEqual(created);
      });
    });

    describe('update', () => {
      it('should update a link', async () => {
        const updates = { type: 'tests' as const };
        const updated = { ...mockLinks[0], ...updates };

        vi.mocked(apiClient.PUT).mockResolvedValue({
          data: updated,
          error: undefined,
          response: new Response(),
        });

        const result = await linksApi.update('link-1', updates);
        expect(result).toEqual(updated);
      });
    });

    describe('delete', () => {
      it('should delete a link', async () => {
        vi.mocked(apiClient.DELETE).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });

        await expect(linksApi.delete('link-1')).resolves.toBeUndefined();
      });
    });
  });

  // ============================================================================
  // GRAPH API
  // ============================================================================

  describe(graphApi, () => {
    describe('getAncestors', () => {
      it('should get ancestors without depth', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getAncestors('item-1');
        expect(result).toEqual(mockGraph);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/ancestors/{id}', {
          params: { path: { id: 'item-1' }, query: { depth: undefined } },
        });
      });

      it('should get ancestors with depth', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getAncestors('item-1', 5);
        expect(result).toEqual(mockGraph);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/ancestors/{id}', {
          params: { path: { id: 'item-1' }, query: { depth: 5 } },
        });
      });
    });

    describe('getDescendants', () => {
      it('should get descendants', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getDescendants('item-1', 3);
        expect(result).toEqual(mockGraph);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/descendants/{id}', {
          params: { path: { id: 'item-1' }, query: { depth: 3 } },
        });
      });
    });

    describe('findPath', () => {
      it('should find path between items', async () => {
        const mockPath = [mockItems[0], mockItems[1]];
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockPath,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.findPath('item-1', 'item-2');
        expect(result).toEqual(mockPath);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/path', {
          params: { query: { source: 'item-1', target: 'item-2' } },
        });
      });
    });

    describe('findAllPaths', () => {
      it('should find all paths between items', async () => {
        const mockPaths = [[mockItems[0], mockItems[1]]];
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockPaths,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.findAllPaths('item-1', 'item-2');
        expect(result).toEqual(mockPaths);
      });
    });

    describe('getFullGraph', () => {
      it('should get full graph without projectId', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getFullGraph();
        expect(result).toEqual(mockGraph);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/full', {
          params: { query: { project_id: undefined } },
        });
      });

      it('should get full graph with projectId', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getFullGraph('proj-1');
        expect(result).toEqual(mockGraph);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/full', {
          params: { query: { project_id: 'proj-1' } },
        });
      });
    });

    describe('get (alias)', () => {
      it('should call getFullGraph', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        // Mock getFullGraph to be callable
        vi.spyOn(graphApi, 'getFullGraph').mockResolvedValue(mockGraph);

        const result = await graphApi.get('proj-1');
        expect(result).toEqual(mockGraph);
        expect(graphApi.getFullGraph).toHaveBeenCalledWith('proj-1');
      });
    });

    describe('detectCycles', () => {
      it('should detect cycles', async () => {
        const mockCycles = [['item-1', 'item-2', 'item-1']];
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockCycles,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.detectCycles('proj-1');
        expect(result).toEqual(mockCycles);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/cycles', {
          params: { query: { project_id: 'proj-1' } },
        });
      });
    });

    describe('topologicalSort', () => {
      it('should perform topological sort', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockItems,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.topologicalSort('proj-1');
        expect(result).toEqual(mockItems);
      });
    });

    describe('getImpactAnalysis', () => {
      it('should get impact analysis', async () => {
        const mockAnalysis = {
          affected_count: 0,
          affected_items: [],
          depth: 5,
          item_id: 'item-1',
        };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockAnalysis,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getImpactAnalysis('item-1', 5);
        expect(result).toEqual(mockAnalysis);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/impact/{id}', {
          params: { path: { id: 'item-1' }, query: { depth: 5 } },
        });
      });
    });

    describe('getDependencyAnalysis', () => {
      it('should get dependency analysis', async () => {
        const mockAnalysis = {
          dependencies: [],
          dependency_count: 0,
          depth: 5,
          item_id: 'item-1',
        };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockAnalysis,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getDependencyAnalysis('item-1', 5);
        expect(result).toEqual(mockAnalysis);
      });
    });

    describe('getOrphanItems', () => {
      it('should get orphan items', async () => {
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockItems,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.getOrphanItems('proj-1');
        expect(result).toEqual(mockItems);
      });
    });

    describe('traverse', () => {
      it('should traverse up', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.traverse('item-1', 'up', 3);
        expect(result).toEqual(mockGraph);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/graph/traverse/{id}', {
          params: {
            path: { id: 'item-1' },
            query: { depth: 3, direction: 'up' },
          },
        });
      });

      it('should traverse down', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.traverse('item-1', 'down', 3);
        expect(result).toEqual(mockGraph);
      });

      it('should traverse both directions', async () => {
        const mockGraph = { edges: [], nodes: [] };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockGraph,
          error: undefined,
          response: new Response(),
        });

        const result = await graphApi.traverse('item-1', 'both', 3);
        expect(result).toEqual(mockGraph);
      });
    });
  });

  // ============================================================================
  // SEARCH API
  // ============================================================================

  describe(searchApi, () => {
    describe('search', () => {
      it('should search with query', async () => {
        const mockResult = { items: [], query: 'test', total: 0 };
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: mockResult,
          error: undefined,
          response: new Response(),
        });

        const result = await searchApi.search({ q: 'test' });
        expect(result).toEqual(mockResult);
        expect(apiClient.POST).toHaveBeenCalledWith('/api/v1/search', {
          body: { q: 'test' },
        });
      });
    });

    describe('searchGet', () => {
      it('should search via GET', async () => {
        const mockResult = { items: [], query: 'test', total: 0 };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockResult,
          error: undefined,
          response: new Response(),
        });

        const result = await searchApi.searchGet({ q: 'test' });
        expect(result).toEqual(mockResult);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/search', {
          params: { query: { q: 'test' } },
        });
      });
    });

    describe('suggest', () => {
      it('should get suggestions', async () => {
        const mockSuggestions = ['test', 'testing', 'tested'];
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockSuggestions,
          error: undefined,
          response: new Response(),
        });

        const result = await searchApi.suggest('test', 10);
        expect(result).toEqual(mockSuggestions);
        expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/search/suggest', {
          params: { query: { limit: 10, q: 'test' } },
        });
      });

      it('should get suggestions without limit', async () => {
        const mockSuggestions = ['test'];
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockSuggestions,
          error: undefined,
          response: new Response(),
        });

        const result = await searchApi.suggest('test');
        expect(result).toEqual(mockSuggestions);
      });
    });

    describe('indexItem', () => {
      it('should index an item', async () => {
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });

        await expect(searchApi.indexItem('item-1')).resolves.toBeUndefined();
        expect(apiClient.POST).toHaveBeenCalledWith('/api/v1/search/index/{id}', {
          params: { path: { id: 'item-1' } },
        });
      });
    });

    describe('batchIndex', () => {
      it('should batch index items', async () => {
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });

        await expect(searchApi.batchIndex(['item-1', 'item-2'])).resolves.toBeUndefined();
        expect(apiClient.POST).toHaveBeenCalledWith('/api/v1/search/batch-index', {
          body: { ids: ['item-1', 'item-2'] },
        });
      });
    });

    describe('reindexAll', () => {
      it('should reindex all', async () => {
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });
        vi.mocked(safeApiCall).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });

        await expect(searchApi.reindexAll()).resolves.toBeUndefined();
        expect(apiClient.POST).toHaveBeenCalledWith('/api/v1/search/reindex', {});
      });
    });

    describe('getStats', () => {
      it('should get search stats', async () => {
        const mockStats = { indexed: 95, total: 100 };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockStats,
          error: undefined,
          response: new Response(),
        });

        const result = await searchApi.getStats();
        expect(result).toEqual(mockStats);
      });
    });

    describe('getHealth', () => {
      it('should get search health', async () => {
        const mockHealth = { status: 'healthy' };
        vi.mocked(apiClient.GET).mockResolvedValue({
          data: mockHealth,
          error: undefined,
          response: new Response(),
        });

        const result = await searchApi.getHealth();
        expect(result).toEqual(mockHealth);
      });
    });

    describe('deleteIndex', () => {
      it('should delete index', async () => {
        vi.mocked(apiClient.DELETE).mockResolvedValue({
          data: undefined,
          error: undefined,
          response: new Response(),
        });

        await expect(searchApi.deleteIndex('item-1')).resolves.toBeUndefined();
      });
    });
  });

  // ============================================================================
  // EXPORT/IMPORT API
  // ============================================================================

  describe(exportImportApi, () => {
    describe('export', () => {
      it('should export project as JSON', async () => {
        const mockBlob = new Blob(['{"data": "test"}'], {
          type: 'application/json',
        });
        globalThis.fetch = vi.fn().mockResolvedValue({
          blob: async () => mockBlob,
          ok: true,
        }) as typeof fetch;

        const result = await exportImportApi.export('proj-1', 'json');
        expect(result).toBeInstanceOf(Blob);
        expect(globalThis.fetch).toHaveBeenCalledWith('/api/v1/projects/proj-1/export?format=json');
      });

      it('should export project as CSV', async () => {
        const mockBlob = new Blob(['id,name'], { type: 'text/csv' });
        globalThis.fetch = vi.fn().mockResolvedValue({
          blob: async () => mockBlob,
          ok: true,
        }) as typeof fetch;

        const result = await exportImportApi.export('proj-1', 'csv');
        expect(result).toBeInstanceOf(Blob);
      });

      it('should export project as markdown', async () => {
        const mockBlob = new Blob(['# Project'], { type: 'text/markdown' });
        globalThis.fetch = vi.fn().mockResolvedValue({
          blob: async () => mockBlob,
          ok: true,
        }) as typeof fetch;

        const result = await exportImportApi.export('proj-1', 'markdown');
        expect(result).toBeInstanceOf(Blob);
      });

      it('should handle export errors', async () => {
        globalThis.fetch = vi.fn().mockResolvedValue({
          ok: false,
          status: 500,
        }) as typeof fetch;

        await expect(exportImportApi.export('proj-1', 'json')).rejects.toThrow('Export failed');
      });
    });

    describe('import', () => {
      it('should import project data', async () => {
        const mockResult = {
          error_count: 0,
          errors: [],
          imported_count: 10,
          success: true,
        };
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: mockResult,
          error: undefined,
          response: new Response(),
        });

        const result = await exportImportApi.import('proj-1', 'json', '{"data": "test"}');
        expect(result).toEqual(mockResult);
        expect(apiClient.POST).toHaveBeenCalledWith('/api/v1/projects/{project_id}/import', {
          body: { data: '{"data": "test"}', format: 'json' },
          params: { path: { project_id: 'proj-1' } },
        });
      });

      it('should handle import errors', async () => {
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: undefined,
          error: { message: 'Invalid format' },
          response: new Response(null, { status: 400 }),
        });

        await expect(exportImportApi.import('proj-1', 'json', 'invalid')).rejects.toThrow();
      });
    });

    describe('exportProject (alias)', () => {
      it('should call export', async () => {
        const mockBlob = new Blob(['test'], { type: 'application/json' });
        globalThis.fetch = vi.fn().mockResolvedValue({
          blob: async () => mockBlob,
          ok: true,
        }) as typeof fetch;

        // Mock export to be callable
        vi.spyOn(exportImportApi, 'export').mockResolvedValue(mockBlob);

        const result = await exportImportApi.exportProject('proj-1', 'json');
        expect(result).toBeInstanceOf(Blob);
        expect(exportImportApi.export).toHaveBeenCalledWith('proj-1', 'json');
      });
    });

    describe('importProject (alias)', () => {
      it('should call import', async () => {
        const mockResult = {
          error_count: 0,
          errors: [],
          imported_count: 10,
          success: true,
        };
        vi.mocked(apiClient.POST).mockResolvedValue({
          data: mockResult,
          error: undefined,
          response: new Response(),
        });

        // Mock import to be callable
        vi.spyOn(exportImportApi, 'import').mockResolvedValue(mockResult);

        const result = await exportImportApi.importProject('proj-1', 'json', '{"data": "test"}');
        expect(result).toEqual(mockResult);
        expect(exportImportApi.import).toHaveBeenCalledWith('proj-1', 'json', '{"data": "test"}');
      });
    });
  });

  // ============================================================================
  // HEALTH CHECK
  // ============================================================================

  describe(healthCheck, () => {
    it('should perform health check', async () => {
      const mockHealth = { service: 'api', status: 'ok' };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockHealth,
        error: undefined,
        response: new Response(),
      });

      const result = await healthCheck();
      expect(result).toEqual(mockHealth);
      expect(apiClient.GET).toHaveBeenCalledWith('/health', {});
    });

    it('should handle health check errors', async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: undefined,
        error: { message: 'Service unavailable' },
        response: new Response(null, { status: 503 }),
      });

      await expect(healthCheck()).rejects.toThrow();
    });
  });
});
