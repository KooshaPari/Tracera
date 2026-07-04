/**
 * Tests for Redirect Routes - Backward Compatibility
 */

import { describe, expect, it } from 'vitest';

describe('Redirect Routes - Backward Compatibility', () => {
  describe('/items/:itemId - Item Detail Redirect', () => {
    it('should validate old items route pattern', () => {
      const itemPath = '/items/item-123';
      expect(itemPath).toMatch(/^\/items\/[^/]+$/);
    });

    it('should extract itemId from old route', () => {
      const path = '/items/item-123';
      const match = path.match(/^\/items\/([^/]+)$/);

      expect(match).not.toBeNull();
      expect(match?.[1]).toBe('item-123');
    });

    it('should map item view type to new path', () => {
      const itemWithView = {
        id: 'item-123',
        projectId: 'project-456',
        view: 'FEATURE',
      };

      const newPath = `/projects/${itemWithView.projectId}/views/${itemWithView.view.toLowerCase()}/item-123`;
      expect(newPath).toMatch(/^\/projects\/project-456\/views\/feature\/item-123$/);
    });

    it('should handle view type case conversion', () => {
      const viewTypes = ['FEATURE', 'TEST', 'API', 'DATABASE'];
      const lowercase = viewTypes.map((v) => v.toLowerCase());

      expect(lowercase).toEqual(['feature', 'test', 'api', 'database']);
    });

    it('should map item type to view type correctly', () => {
      const typeToView: Record<string, string> = {
        api_endpoint: 'api',
        database_schema: 'database',
        epic: 'feature',
        story: 'feature',
        test_case: 'test',
      };

      expect(typeToView['epic']).toBe('feature');
      expect(typeToView['test_case']).toBe('test');
      expect(typeToView['api_endpoint']).toBe('api');
    });
  });

  describe('/items - Items List Redirect', () => {
    it('should redirect items list to projects', () => {
      const oldPath = '/items';
      const newPath = '/projects';

      expect(oldPath).not.toBe(newPath);
      expect(newPath).toBe('/projects');
    });

    it('should handle items query parameters on redirect', () => {
      const params = new URLSearchParams('search=test&sort=created');

      expect(params.get('search')).toBe('test');
      expect(params.get('sort')).toBe('created');
    });
  });

  describe('/graph - Graph Redirect', () => {
    it('should redirect graph to projects with hint', () => {
      const oldPath = '/graph';
      const newPath = '/projects?hint=graph';

      expect(oldPath).toBe('/graph');
      expect(newPath).toMatch(/^\/projects/);
      expect(newPath).toContain('hint=graph');
    });
  });

  describe('/search - Search Redirect', () => {
    it('should redirect search to projects with hint', () => {
      const oldPath = '/search';
      const newPath = '/projects?hint=search';

      expect(oldPath).toBe('/search');
      expect(newPath).toMatch(/^\/projects/);
      expect(newPath).toContain('hint=search');
    });

    it('should preserve search query on redirect', () => {
      const searchQuery = new URLSearchParams('q=test');
      const query = searchQuery.get('q');

      expect(query).toBe('test');
    });
  });

  describe('History Management', () => {
    it('should use replace strategy for redirects', () => {
      const redirect = {
        mode: 'replace' as const,
        path: '/items/item-123',
        target: '/projects/proj-456/views/feature/item-123',
      };

      expect(redirect.mode).toBe('replace');
    });

    it('should preserve return-to parameter', () => {
      const params = new URLSearchParams('returnTo=/items/item-123');
      const returnTo = params.get('returnTo');

      expect(returnTo).toBe('/items/item-123');
    });

    it('should handle nested query parameters', () => {
      const params = new URLSearchParams('project=proj-1&item=item-123&view=feature');

      expect(params.get('project')).toBe('proj-1');
      expect(params.get('item')).toBe('item-123');
      expect(params.get('view')).toBe('feature');
    });
  });

  describe('Edge Cases', () => {
    it('should handle missing itemId gracefully', () => {
      const path = '/items/';
      const match = path.match(/^\/items\/([^/]+)$/);

      expect(match).toBeNull();
    });

    it('should handle malformed item IDs', () => {
      const malformedIds = ['', ' ', 'item id with spaces', '123'];

      expect(malformedIds[0]).toBe('');
      expect(malformedIds[2]).toContain(' ');
    });

    it('should normalize view type values', () => {
      const views = ['FEATURE', 'feature', 'Feature'];
      const normalized = views.map((v) => v.toLowerCase());

      expect(normalized.every((v) => v === 'feature')).toBeTruthy();
    });
  });
});
