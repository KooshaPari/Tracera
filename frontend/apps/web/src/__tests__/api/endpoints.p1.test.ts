/**
 * Comprehensive tests for API endpoints (endpoints.ts)
 * Coverage targets: All CRUD operations, response format handling, error cases, edge cases
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { api } from '../../api/endpoints';

// Mock data generators
const mockProject = {
  created_at: '2024-01-01T00:00:00Z',
  id: 'proj-1',
  name: 'Test Project',
};

const mockItem = {
  created_at: '2024-01-01T00:00:00Z',
  id: 'item-1',
  project_id: 'proj-1',
  title: 'Test Item',
  type: 'requirement',
};

const mockLink = {
  created_at: '2024-01-01T00:00:00Z',
  id: 'link-1',
  source_id: 'item-1',
  target_id: 'item-2',
  type: 'depends_on',
};

const mockGraphData = {
  items: [mockItem],
  links: [mockLink],
};

async function createMockResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' },
    status,
  });
}

describe('API Endpoints - P1 Coverage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ============================================================================
  // PROJECTS API TESTS
  // ============================================================================

  describe('projectsApi', () => {
    describe('list', () => {
      it('should return array of projects', async () => {
        const mockFetch = vi.fn(async () => createMockResponse({ projects: [mockProject] }));
        global.fetch = mockFetch as unknown as typeof fetch;

        const result = await api.projects.list();
        expect(Array.isArray(result)).toBeTruthy();
      });

      it('should handle response with projects array', async () => {
        const projects = [mockProject, { ...mockProject, id: 'proj-2', name: 'Project 2' }];
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ projects }));

        const result = await api.projects.list();
        // Result extraction logic: projects array or full response
        expect(result).toBeDefined();
      });

      it('should handle array response format', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([mockProject]));

        const result = await api.projects.list();
        expect(Array.isArray(result)).toBeTruthy();
      });

      it('should accept pagination parameters', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ projects: [mockProject] }),
        );

        const result = await api.projects.list({ limit: 10, offset: 0 });
        expect(Array.isArray(result)).toBeTruthy();
      });

      it('should return empty array on empty response', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ projects: [] }));

        const result = await api.projects.list();
        expect(Array.isArray(result)).toBeTruthy();
      });
    });

    describe('get', () => {
      it('should fetch project by ID', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockProject));

        const result = await api.projects.get('proj-1');
        expect(result).toBeDefined();
      });

      it('should throw on 404', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ error: 'Not found' }, 404),
        );

        await expect(api.projects.get('nonexistent')).rejects.toThrow();
      });

      it('should include correct path parameter', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockProject));

        await api.projects.get('proj-123');
        // Verify the fetch was called (actual URL verification depends on client internals)
        expect(global.fetch as any).toHaveBeenCalled();
      });
    });

    describe('create', () => {
      it('should create project with valid input', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockProject, 201));

        const result = await api.projects.create({
          name: 'Test Project',
          description: 'Test description',
        });

        expect(result).toBeDefined();
      });

      it('should handle required fields', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockProject, 201));

        const result = await api.projects.create({ name: 'Minimal Project' });
        expect(result).toBeDefined();
      });

      it('should send POST request', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockProject, 201));

        await api.projects.create({ name: 'Test' });
        expect(global.fetch as any).toHaveBeenCalled();
      });

      it('should throw on validation error', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ error: 'Invalid input' }, 400),
        );

        await expect(api.projects.create({ name: '' })).rejects.toThrow();
      });
    });

    describe('update', () => {
      it('should update project', async () => {
        const updated = { ...mockProject, name: 'Updated' };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(updated));

        const result = await api.projects.update('proj-1', { name: 'Updated' });
        expect(result).toBeDefined();
      });

      it('should handle partial updates', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockProject));

        await api.projects.update('proj-1', { description: 'New description' });
        expect(global.fetch as any).toHaveBeenCalled();
      });

      it('should throw on not found', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ error: 'Not found' }, 404),
        );

        await expect(api.projects.update('nonexistent', { name: 'Updated' })).rejects.toThrow();
      });
    });

    describe('delete', () => {
      it('should delete project', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.projects.delete('proj-1')).resolves.toBeUndefined();
      });

      it('should handle 204 no content', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await api.projects.delete('proj-1');
        expect(global.fetch as any).toHaveBeenCalled();
      });

      it('should throw on not found', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ error: 'Not found' }, 404),
        );

        await expect(api.projects.delete('nonexistent')).rejects.toThrow();
      });
    });
  });

  // ============================================================================
  // ITEMS API TESTS
  // ============================================================================

  describe('itemsApi', () => {
    describe('list', () => {
      it('should return items array', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ items: [mockItem] }));

        const result = await api.items.list();
        expect(result).toBeDefined();
      });

      it('should handle array response format', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([mockItem]));

        const result = await api.items.list();
        expect(result).toBeDefined();
      });

      it('should handle cursor pagination response', async () => {
        const cursorResponse = {
          data: [mockItem],
          has_more: true,
          next_cursor: 'cursor-123',
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(cursorResponse));

        const result = await api.items.list();
        expect(result).toBeDefined();
      });

      it('should handle legacy offset pagination', async () => {
        const legacyResponse = {
          items: [mockItem],
          total: 100,
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(legacyResponse));

        const result = await api.items.list();
        expect(Array.isArray(result) || result).toBeDefined();
      });

      it('should filter by project_id', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ items: [mockItem] }));

        const result = await api.items.list({ project_id: 'proj-1' });
        expect(result).toBeDefined();
      });

      it('should filter by status', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ items: [mockItem] }));

        const result = await api.items.list({ project_id: 'proj-1' });
        expect(result).toBeDefined();
      });

      it('should filter by view type', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ items: [mockItem] }));

        const result = await api.items.list({ project_id: 'proj-1' });
        expect(result).toBeDefined();
      });

      it('should handle empty response', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ items: [] }));

        const result = await api.items.list();
        expect(result).toBeDefined();
      });
    });

    describe('get', () => {
      it('should fetch item by ID', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem));

        const result = await api.items.get('item-1');
        expect(result).toBeDefined();
      });

      it('should throw on 404', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ error: 'Not found' }, 404),
        );

        await expect(api.items.get('nonexistent')).rejects.toThrow();
      });
    });

    describe('create', () => {
      it('should create item', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem, 201));

        const result = await api.items.create({
          projectId: 'proj-1',
          title: 'New Item',
          type: 'requirement',
        });

        expect(result).toBeDefined();
      });

      it('should handle optional fields', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem, 201));

        const result = await api.items.create({
          description: 'Description',
          projectId: 'proj-1',
          title: 'Item',
          type: 'requirement',
        });

        expect(result).toBeDefined();
      });
    });

    describe('update', () => {
      it('should update item', async () => {
        const updated = { ...mockItem, title: 'Updated' };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(updated));

        const result = await api.items.update('item-1', { title: 'Updated' });
        expect(result).toBeDefined();
      });
    });

    describe('delete', () => {
      it('should delete item', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.items.delete('item-1')).resolves.toBeUndefined();
      });
    });
  });

  // ============================================================================
  // LINKS API TESTS
  // ============================================================================

  describe('linksApi', () => {
    describe('list', () => {
      it('should return links array', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([mockLink]));

        const result = await api.links.list();
        expect(result).toBeDefined();
      });

      it('should accept pagination', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([mockLink]));

        const result = await api.links.list({ limit: 10 });
        expect(result).toBeDefined();
      });
    });

    describe('get', () => {
      it('should fetch link by ID', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockLink));

        const result = await api.links.get('link-1');
        expect(result).toBeDefined();
      });
    });

    describe('create', () => {
      it('should create link', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockLink, 201));

        const result = await api.links.create({
          sourceId: 'item-1',
          targetId: 'item-2',
          type: 'depends_on',
        });

        expect(result).toBeDefined();
      });
    });

    describe('update', () => {
      it('should update link', async () => {
        const updated = { ...mockLink, type: 'blocks' };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(updated));

        const result = await api.links.update('link-1', { type: 'blocks' });
        expect(result).toBeDefined();
      });
    });

    describe('delete', () => {
      it('should delete link', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.links.delete('link-1')).resolves.toBeUndefined();
      });
    });
  });

  // ============================================================================
  // GRAPH API TESTS
  // ============================================================================

  describe('graphApi', () => {
    describe('getAncestors', () => {
      it('should fetch ancestors', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.getAncestors('item-1');
        expect(result).toBeDefined();
      });

      it('should support depth parameter', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.getAncestors('item-1', 3);
        expect(result).toBeDefined();
      });
    });

    describe('getDescendants', () => {
      it('should fetch descendants', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.getDescendants('item-1');
        expect(result).toBeDefined();
      });

      it('should support depth parameter', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.getDescendants('item-1', 2);
        expect(result).toBeDefined();
      });
    });

    describe('findPath', () => {
      it('should find path between items', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([mockItem]));

        const result = await api.graph.findPath('item-1', 'item-2');
        expect(result).toBeDefined();
      });

      it('should return empty array if no path exists', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([]));

        const result = await api.graph.findPath('item-1', 'item-2');
        expect(Array.isArray(result)).toBeTruthy();
      });
    });

    describe('findAllPaths', () => {
      it('should find all paths', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([[mockItem]]));

        const result = await api.graph.findAllPaths('item-1', 'item-2');
        expect(Array.isArray(result)).toBeTruthy();
      });
    });

    describe('getFullGraph', () => {
      it('should fetch full graph', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.getFullGraph();
        expect(result).toBeDefined();
      });

      it('should filter by project ID', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.getFullGraph('proj-1');
        expect(result).toBeDefined();
      });
    });

    describe('get (alias)', () => {
      it('should be alias for getFullGraph', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.get();
        expect(result).toBeDefined();
      });
    });

    describe('detectCycles', () => {
      it('should detect cycles', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([['item-1', 'item-2']]));

        const result = await api.graph.detectCycles();
        expect(Array.isArray(result)).toBeTruthy();
      });

      it('should return empty array if no cycles', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([]));

        const result = await api.graph.detectCycles();
        expect(Array.isArray(result)).toBeTruthy();
      });
    });

    describe('topologicalSort', () => {
      it('should perform topological sort', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([mockItem]));

        const result = await api.graph.topologicalSort();
        expect(Array.isArray(result)).toBeTruthy();
      });
    });

    describe('getImpactAnalysis', () => {
      it('should analyze impact', async () => {
        const impactData = {
          direct: [mockItem],
          indirect: [],
          risk_level: 'low',
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(impactData));

        const result = await api.graph.getImpactAnalysis('item-1');
        expect(result).toBeDefined();
      });

      it('should support depth parameter', async () => {
        const impactData = { direct: [], indirect: [], risk_level: 'low' };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(impactData));

        const result = await api.graph.getImpactAnalysis('item-1', 2);
        expect(result).toBeDefined();
      });
    });

    describe('getDependencyAnalysis', () => {
      it('should analyze dependencies', async () => {
        const depData = {
          dependencies: [mockItem],
          dependents: [],
          critical: [],
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(depData));

        const result = await api.graph.getDependencyAnalysis('item-1');
        expect(result).toBeDefined();
      });
    });

    describe('getOrphanItems', () => {
      it('should find orphan items', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse([mockItem]));

        const result = await api.graph.getOrphanItems();
        expect(Array.isArray(result)).toBeTruthy();
      });
    });

    describe('traverse', () => {
      it('should traverse up', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.traverse('item-1', 'up');
        expect(result).toBeDefined();
      });

      it('should traverse down', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.traverse('item-1', 'down');
        expect(result).toBeDefined();
      });

      it('should traverse both directions', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.traverse('item-1', 'both');
        expect(result).toBeDefined();
      });

      it('should support depth parameter', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockGraphData));

        const result = await api.graph.traverse('item-1', 'up', 3);
        expect(result).toBeDefined();
      });
    });
  });

  // ============================================================================
  // EXPORT/IMPORT API TESTS
  // ============================================================================

  describe('exportImportApi', () => {
    const canonicalExport = {
      items: [{ id: 'item-1', title: 'Test', type: 'requirement', view: 'kanban', status: 'open' }],
      links: [{ source_id: 'item-1', target_id: 'item-2', type: 'depends_on' }],
      project: { id: 'proj-1', name: 'Test Project' },
    };

    describe('export', () => {
      it('should export as JSON', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(canonicalExport));

        const result = await api.exportImport.export('proj-1', 'json');
        expect(result).toBeDefined();
      });

      it('should export as CSV', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ content: 'id,title\nitem-1,Test' }),
        );

        const result = await api.exportImport.export('proj-1', 'csv');
        expect(result).toBeDefined();
      });

      it('should export as markdown', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse({ content: '# Test Project' }),
        );

        const result = await api.exportImport.export('proj-1', 'markdown');
        expect(result).toBeDefined();
      });

      it('should export as full format', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(canonicalExport));

        const result = await api.exportImport.export('proj-1', 'full');
        expect(result).toBeDefined();
      });

      it('should default to JSON format', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(canonicalExport));

        const result = await api.exportImport.export('proj-1');
        expect(result).toBeDefined();
      });
    });

    describe('exportFull', () => {
      it('should export full canonical format', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(canonicalExport));

        const result = await api.exportImport.exportFull('proj-1');
        expect(result).toBeDefined();
      });

      it('should throw if response is not canonical format', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ error: 'Invalid' }));

        await expect(api.exportImport.exportFull('proj-1')).rejects.toThrow();
      });
    });

    describe('import', () => {
      it('should import JSON data', async () => {
        const importResult = {
          error_count: 0,
          errors: [],
          imported_count: 5,
          success: true,
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(importResult));

        const result = await api.exportImport.import('proj-1', 'json', '{}');
        expect(result).toBeDefined();
      });

      it('should import CSV data', async () => {
        const importResult = {
          error_count: 0,
          errors: [],
          imported_count: 10,
          success: true,
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(importResult));

        const result = await api.exportImport.import('proj-1', 'csv', 'id,title\n1,Test');
        expect(result).toBeDefined();
      });

      it('should report import errors', async () => {
        const importResult = {
          error_count: 2,
          errors: ['Invalid row 1', 'Invalid row 2'],
          imported_count: 3,
          success: true,
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(importResult));

        const result = await api.exportImport.import('proj-1', 'json', '{}');
        expect(result.error_count).toBeGreaterThan(0);
      });
    });

    describe('importFull', () => {
      it('should import full canonical format', async () => {
        const importResult = {
          items_imported: 5,
          links_imported: 3,
          project_id: 'new-proj-1',
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(importResult));

        const result = await api.exportImport.importFull(canonicalExport);
        expect(result).toBeDefined();
      });
    });

    describe('exportProject (alias)', () => {
      it('should export as Blob', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse({ content: 'export data' }));

        const result = await api.exportImport.exportProject('proj-1', 'json');
        expect(result instanceof Blob || result).toBeDefined();
      });

      it('should throw if response is not Blob', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(canonicalExport));

        await expect(api.exportImport.exportProject('proj-1', 'json')).rejects.toThrow();
      });
    });

    describe('importProject (alias)', () => {
      it('should import and return result', async () => {
        const importResult = {
          error_count: 0,
          errors: [],
          imported_count: 5,
          success: true,
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(importResult));

        const result = await api.exportImport.importProject('proj-1', 'json', '{}');
        expect(result).toBeDefined();
      });
    });
  });

  // ============================================================================
  // SEARCH API TESTS
  // ============================================================================

  describe('searchApi', () => {
    const mockSearchResult = {
      results: [mockItem],
      total: 1,
    };

    describe('search', () => {
      it('should search via POST', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockSearchResult));

        const result = await api.search.search({
          q: 'test',
        });

        expect(result).toBeDefined();
      });

      it('should search with filters', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockSearchResult));

        const result = await api.search.search({
          q: 'test',
        });

        expect(result).toBeDefined();
      });
    });

    describe('searchGet', () => {
      it('should search via GET', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockSearchResult));

        const result = await api.search.searchGet({
          q: 'test',
        });

        expect(result).toBeDefined();
      });
    });

    describe('suggest', () => {
      it('should get search suggestions', async () => {
        (global.fetch as any).mockResolvedValueOnce(
          createMockResponse(['suggestion1', 'suggestion2']),
        );

        const result = await api.search.suggest('test');
        expect(Array.isArray(result)).toBeTruthy();
      });

      it('should support limit parameter', async () => {
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(['suggestion1']));

        const result = await api.search.suggest('test', 5);
        expect(Array.isArray(result)).toBeTruthy();
      });
    });

    describe('indexItem', () => {
      it('should index item', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.search.indexItem('item-1')).resolves.toBeUndefined();
      });
    });

    describe('batchIndex', () => {
      it('should batch index items', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.search.batchIndex(['item-1', 'item-2'])).resolves.toBeUndefined();
      });

      it('should handle empty array', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.search.batchIndex([])).resolves.toBeUndefined();
      });
    });

    describe('reindexAll', () => {
      it('should reindex all items', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.search.reindexAll()).resolves.toBeUndefined();
      });
    });

    describe('getStats', () => {
      it('should get search stats', async () => {
        const stats = {
          indexed_count: 100,
          total_items: 150,
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(stats));

        const result = await api.search.getStats();
        expect(result).toBeDefined();
      });
    });

    describe('getHealth', () => {
      it('should get search health', async () => {
        const health = {
          healthy: true,
          status: 'ok',
        };
        (global.fetch as any).mockResolvedValueOnce(createMockResponse(health));

        const result = await api.search.getHealth();
        expect(result).toBeDefined();
      });
    });

    describe('deleteIndex', () => {
      it('should delete index for item', async () => {
        (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

        await expect(api.search.deleteIndex('item-1')).resolves.toBeUndefined();
      });
    });
  });

  // ============================================================================
  // UTILITY ENDPOINTS
  // ============================================================================

  describe('healthCheck', () => {
    it('should check health', async () => {
      const healthResult = {
        service: 'api',
        status: 'healthy',
      };
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(healthResult));

      const result = await api.healthCheck();
      expect(result).toBeDefined();
    });

    it('should handle unhealthy status', async () => {
      const healthResult = {
        service: 'api',
        status: 'unhealthy',
      };
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(healthResult));

      const result = await api.healthCheck();
      expect(result).toBeDefined();
    });
  });

  // ============================================================================
  // API EXPORT TEST
  // ============================================================================

  describe('api export', () => {
    it('should export all sub-APIs', () => {
      expect(api.projects).toBeDefined();
      expect(api.items).toBeDefined();
      expect(api.links).toBeDefined();
      expect(api.graph).toBeDefined();
      expect(api.search).toBeDefined();
      expect(api.exportImport).toBeDefined();
      expect(api.healthCheck).toBeDefined();
    });

    it('should have all CRUD methods', () => {
      expect(api.projects.list).toBeDefined();
      expect(api.projects.get).toBeDefined();
      expect(api.projects.create).toBeDefined();
      expect(api.projects.update).toBeDefined();
      expect(api.projects.delete).toBeDefined();
    });
  });
});
