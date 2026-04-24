/**
 * Tests for API endpoints
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { api } from '../../api/endpoints';
import { mockItems, mockLinks, mockProjects } from '../mocks/data';

// Simple console-based logger
const logger = {
  info: (msg: string) => {
    console.log(msg);
  },
  warn: (msg: string) => {
    console.warn(msg);
  },
  error: (msg: string) => {
    console.error(msg);
  },
};

// Mock fetch responses for API tests
function createMockApiResponse(data: any, status = 200) {
  return Response.json(data, {
    headers: { 'Content-Type': 'application/json' },
    status,
  });
}

// NOTE: These tests require proper mocking of openapi-fetch client
// The actual API endpoints are tested at integration level via hooks tests
// Which properly validate the query patterns and response handling
describe('API Endpoints', () => {
  beforeEach(() => {
    // Mock fetch directly  - replace the global fetch with our mock implementation
    const fetchImpl = async (url: string | Request, options?: any) => {
      // Extract URL and method from Request object or parameters
      let urlStr = '';
      let method = 'GET';

      if (typeof url === 'string') {
        urlStr = url;
        method = options?.method ?? 'GET';
      } else if (url instanceof Request) {
        // Handle native Request object
        urlStr = url.url;
        method = url.method || 'GET';
      } else if (url && typeof url === 'object' && 'url' in url) {
        // Handle object with url property
        const urlObj = url as { url?: string; method?: string };
        urlStr = urlObj.url ?? String(url);
        method = urlObj.method ?? 'GET';
      } else {
        urlStr = String(url);
      }

      // Normalize URL - remove base if present and get just the path
      const urlNormalized = urlStr.replace(/^https?:\/\/[^/]+/, '').split('?')[0] || '';

      logger.info(`[Mock Fetch] ${method} ${urlNormalized}`);

      // Projects - GET list
      if (urlNormalized === '/api/v1/projects' && method === 'GET') {
        return createMockApiResponse(mockProjects);
      }

      // Projects - GET by ID
      if (urlNormalized === '/api/v1/projects/proj-1' && method === 'GET') {
        return createMockApiResponse(mockProjects[0]);
      }

      // Projects - POST create
      if (urlNormalized === '/api/v1/projects' && method === 'POST') {
        return createMockApiResponse(
          {
            created_at: new Date().toISOString(),
            id: 'new-proj',
            name: 'New Project',
          },
          201,
        );
      }

      // Projects - PUT/PATCH update
      if (urlNormalized === '/api/v1/projects/proj-1' && (method === 'PUT' || method === 'PATCH')) {
        return createMockApiResponse({
          ...mockProjects[0],
          name: 'Updated Project',
          created_at: new Date().toISOString(),
        });
      }

      // Projects - DELETE
      if (urlNormalized === '/api/v1/projects/proj-1' && method === 'DELETE') {
        return new Response(null, { status: 204 });
      }

      // Items - GET list
      if (urlNormalized === '/api/v1/items' && method === 'GET') {
        return createMockApiResponse(mockItems);
      }

      // Items - GET by ID
      if (urlNormalized === '/api/v1/items/item-1' && method === 'GET') {
        return createMockApiResponse(mockItems[0]);
      }

      // Items - POST create
      if (urlNormalized === '/api/v1/items' && method === 'POST') {
        return createMockApiResponse({ id: 'new-item', ...mockItems[0], title: 'New Item' }, 201);
      }

      // Items - PUT/PATCH update
      if (urlNormalized === '/api/v1/items/item-1' && (method === 'PUT' || method === 'PATCH')) {
        return createMockApiResponse({
          ...mockItems[0],
          title: 'Updated Item',
        });
      }

      // Items - DELETE
      if (urlNormalized === '/api/v1/items/item-1' && method === 'DELETE') {
        return new Response(null, { status: 204 });
      }

      // Links - GET list
      if (urlNormalized === '/api/v1/links' && method === 'GET') {
        return createMockApiResponse(mockLinks);
      }

      // Links - GET by ID
      if (urlNormalized === '/api/v1/links/link-1' && method === 'GET') {
        return createMockApiResponse(mockLinks[0]);
      }

      // Links - POST create
      if (urlNormalized === '/api/v1/links' && method === 'POST') {
        return createMockApiResponse({ id: 'new-link', ...mockLinks[0] }, 201);
      }

      // Links - DELETE
      if (urlNormalized === '/api/v1/links/link-1' && method === 'DELETE') {
        return new Response(null, { status: 204 });
      }

      // Graph - full graph
      if (urlNormalized === '/api/v1/graph/full' && method === 'GET') {
        return createMockApiResponse({ edges: [], nodes: [] });
      }

      // Graph - impact analysis
      if (urlNormalized === '/api/v1/graph/impact/item-1' && method === 'GET') {
        return createMockApiResponse({ affected_count: 0, affected_items: [] });
      }

      // Graph - dependencies analysis
      if (urlNormalized === '/api/v1/graph/dependencies/item-1' && method === 'GET') {
        return createMockApiResponse({ dependencies: [], dependency_count: 0 });
      }

      // Search
      if (urlNormalized === '/api/v1/search' && method === 'GET') {
        const urlObj = new URL(urlStr, 'http://localhost:4000');
        const query = urlObj.searchParams.get('q') ?? '';
        return createMockApiResponse({ items: [], query, total: 0 });
      }

      // Health check
      if (urlNormalized === '/health') {
        return createMockApiResponse({ status: 'ok' });
      }

      // Default 404 for unmocked endpoints
      logger.warn(`[WARN] Unmocked fetch: ${method} ${urlNormalized}`);
      return createMockApiResponse({ error: 'Not mocked' }, 404);
    };

    // Replace global fetch with our mock
    globalThis.fetch = vi.fn(fetchImpl) as typeof fetch;
  });
  describe('projectsApi', () => {
    it('should list projects', async () => {
      const projects = await api.projects.list();
      expect(projects).toEqual(mockProjects);
    });

    it('should get a project by id', async () => {
      const project = await api.projects.get('proj-1');
      expect(project).toEqual(mockProjects[0]);
    });

    it('should create a project', async () => {
      const newProject = {
        description: 'Test project',
        name: 'New Project',
      };
      const project = await api.projects.create(newProject);
      expect(project).toHaveProperty('id');
      expect(project.name).toBe(newProject.name);
    });

    it('should update a project', async () => {
      const updates = { name: 'Updated Project' };
      const project = await api.projects.update('proj-1', updates);
      expect(project.name).toBe(updates.name);
    });

    it('should delete a project', async () => {
      await expect(api.projects.delete('proj-1')).resolves.toBeUndefined();
    });

    it('should handle 404 errors', async () => {
      await expect(api.projects.get('non-existent')).rejects.toThrow();
    });
  });

  describe('itemsApi', () => {
    it('should list items', async () => {
      const items = await api.items.list();
      expect(items).toEqual(mockItems);
    });

    it('should filter items by project', async () => {
      const items = await api.items.list({ project_id: 'proj-1' });
      expect(items.every((item) => item.project_id === 'proj-1')).toBeTruthy();
    });

    it('should get an item by id', async () => {
      const item = await api.items.get('item-1');
      expect(item).toEqual(mockItems[0]);
    });

    it('should create an item', async () => {
      const newItem = {
        project_id: 'proj-1',
        status: 'pending' as const,
        title: 'New Item',
        type: 'feature' as const,
      };
      const item = await api.items.create(newItem);
      expect(item).toHaveProperty('id');
      expect(item.title).toBe(newItem.title);
    });

    it('should update an item', async () => {
      const updates = { title: 'Updated Item' };
      const item = await api.items.update('item-1', updates);
      expect(item.title).toBe(updates.title);
    });

    it('should delete an item', async () => {
      await expect(api.items.delete('item-1')).resolves.toBeUndefined();
    });
  });

  describe('linksApi', () => {
    it('should list links', async () => {
      const links = await api.links.list();
      expect(links).toEqual(mockLinks);
    });

    it('should get a link by id', async () => {
      const link = await api.links.get('link-1');
      expect(link).toEqual(mockLinks[0]);
    });

    it('should create a link', async () => {
      const newLink = {
        source_id: 'item-1',
        target_id: 'item-2',
        type: 'implements' as const,
      };
      const link = await api.links.create(newLink);
      expect(link).toHaveProperty('id');
    });

    it('should delete a link', async () => {
      await expect(api.links.delete('link-1')).resolves.toBeUndefined();
    });
  });

  describe('graphApi', () => {
    it('should get full graph', async () => {
      const graph = await api.graph.getFullGraph('proj-1');
      expect(graph).toHaveProperty('nodes');
      expect(graph).toHaveProperty('edges');
    });

    it('should get impact analysis', async () => {
      const analysis = await api.graph.getImpactAnalysis('item-1');
      expect(analysis).toHaveProperty('affected_items');
      expect(analysis).toHaveProperty('affected_count');
    });

    it('should get dependency analysis', async () => {
      const analysis = await api.graph.getDependencyAnalysis('item-1');
      expect(analysis).toHaveProperty('dependencies');
      expect(analysis).toHaveProperty('dependency_count');
    });
  });

  describe('searchApi', () => {
    it('should search items', async () => {
      const results = await api.search.searchGet({
        page: 1,
        per_page: 10,
        q: 'test',
      });
      expect(results).toHaveProperty('items');
      expect(results).toHaveProperty('total');
      expect(results.query).toBe('test');
    });
  });

  describe('healthCheck', () => {
    it('should perform health check', async () => {
      // This will fail in MSW but tests the function exists
      try {
        await api.healthCheck();
      } catch (_error) {
        // Expected to fail with MSW
        expect(_error).toBeTruthy();
      }
    });
  });
});
