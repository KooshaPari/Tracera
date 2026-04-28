import { describe, expect, it } from 'vitest';

import type { Item, Link } from '@tracertm/types';

import { performCrossPerspectiveSearch } from '../../components/graph/hooks/useCrossPerspectiveSearch';

describe('useCrossPerspectiveSearch', () => {
  const mockItems: Item[] = [
    {
      createdAt: '2025-01-01',
      description: 'Handle user login and registration',
      id: '1',
      perspective: 'feature',
      priority: 'high',
      projectId: 'p1',
      status: 'done',
      title: 'User Authentication',
      type: 'Feature',
      updatedAt: '2025-01-01',
      version: 1,
      view: 'feature',
    },
    {
      createdAt: '2025-01-01',
      description: 'React component for user login',
      equivalentItemIds: ['1'],
      id: '2',
      perspective: 'code',
      priority: 'high',
      projectId: 'p1',
      status: 'done',
      title: 'LoginForm',
      type: 'Component',
      updatedAt: '2025-01-01',
      version: 1,
      view: 'code',
    },
    {
      createdAt: '2025-01-01',
      description: 'Tests for auth module',
      id: '3',
      perspective: 'test',
      priority: 'high',
      projectId: 'p1',
      status: 'in_progress',
      title: 'Authentication Tests',
      type: 'TestSuite',
      updatedAt: '2025-01-01',
      version: 1,
      view: 'test',
    },
    {
      createdAt: '2025-01-01',
      description: 'Stores user account information',
      id: '4',
      perspective: 'database',
      priority: 'critical',
      projectId: 'p1',
      status: 'done',
      title: 'users_table',
      type: 'Table',
      updatedAt: '2025-01-01',
      version: 1,
      view: 'database',
    },
    {
      createdAt: '2025-01-01',
      description: 'Login endpoint',
      equivalentItemIds: ['1'],
      id: '5',
      perspective: 'api',
      priority: 'high',
      projectId: 'p1',
      status: 'done',
      title: 'POST /auth/login',
      type: 'Endpoint',
      updatedAt: '2025-01-01',
      version: 1,
      view: 'api',
    },
  ];

  const mockLinks: Link[] = [
    {
      confidence: 0.95,
      createdAt: '2025-01-01',
      id: 'l1',
      projectId: 'p1',
      sourceId: '1',
      targetId: '2',
      type: 'same_as',
    },
    {
      confidence: 0.9,
      createdAt: '2025-01-01',
      id: 'l2',
      projectId: 'p1',
      sourceId: '1',
      targetId: '5',
      type: 'same_as',
    },
    {
      confidence: 0.85,
      createdAt: '2025-01-01',
      id: 'l3',
      projectId: 'p1',
      sourceId: '1',
      targetId: '3',
      type: 'tests',
    },
  ];

  describe('performSearch', () => {
    it('should return empty array when query is empty', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, '');
      expect(results).toEqual([]);
    });

    it('should return empty array when query is whitespace only', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, '   ');
      expect(results).toEqual([]);
    });

    it('should find items by exact title match', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'User Authentication');
      expect(results).toHaveLength(1);
      expect(results[0].results).toHaveLength(1);
      expect(results[0].results[0].item.id).toBe('1');
    });

    it('should find items by partial title match (case-insensitive)', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      expect(results.length).toBeGreaterThan(0);
      const flatResults = results.flatMap((r) => r.results);
      expect(flatResults.some((r) => r.item.id === '1')).toBeTruthy();
      expect(flatResults.some((r) => r.item.id === '3')).toBeTruthy();
    });

    it('should find items by description match', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'React component');
      expect(results.length).toBeGreaterThan(0);
      const flatResults = results.flatMap((r) => r.results);
      expect(flatResults.some((r) => r.item.id === '2')).toBeTruthy();
    });

    it('should find items by type match', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'Component');
      expect(results.length).toBeGreaterThan(0);
      const flatResults = results.flatMap((r) => r.results);
      expect(flatResults.some((r) => r.item.id === '2')).toBeTruthy();
    });

    it('should group results by perspective', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      expect(results.length).toBeGreaterThan(1);
      results.forEach((group) => {
        expect(group.perspective).toBeTruthy();
        expect(group.results.length).toBeGreaterThan(0);
        expect(group.count).toBe(group.results.length);
      });
    });

    it('should sort groups alphabetically by perspective', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'authentication');
      for (let i = 1; i < results.length; i++) {
        expect(
          results[i].perspective.localeCompare(results[i - 1].perspective),
        ).toBeGreaterThanOrEqual(0);
      }
    });

    it('should sort results by score (descending)', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      results.forEach((group) => {
        for (let i = 1; i < group.results.length; i++) {
          expect(group.results[i].score).toBeLessThanOrEqual(group.results[i - 1].score);
        }
      });
    });

    it('should identify equivalences from explicit IDs', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      const item1Results = results.flatMap((r) => r.results).filter((r) => r.item.id === '1');
      if (item1Results.length > 0) {
        const { equivalences } = item1Results[0];
        expect(equivalences.length).toBeGreaterThan(0);
        expect(equivalences.some((e) => e.equivalentItemId === '2')).toBeTruthy();
        expect(equivalences.some((e) => e.equivalentItemId === '5')).toBeTruthy();
      }
    });

    it('should identify equivalences from links', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      const item1Results = results.flatMap((r) => r.results).filter((r) => r.item.id === '1');
      if (item1Results.length > 0) {
        const { equivalences } = item1Results[0];
        expect(equivalences.some((e) => e.linkType === 'same_as')).toBeTruthy();
      }
    });

    it('should not duplicate equivalences', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      const item1Results = results.flatMap((r) => r.results).filter((r) => r.item.id === '1');
      if (item1Results.length > 0) {
        const { equivalences } = item1Results[0];
        const ids = equivalences.map((e) => e.equivalentItemId);
        expect(ids.length).toBe(new Set(ids).size);
      }
    });

    it('should apply type filter', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth', {
        type: 'Component',
      });
      const flatResults = results.flatMap((r) => r.results);
      flatResults.forEach((result) => {
        expect(result.item.type).toBe('Component');
      });
    });

    it('should apply status filter', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth', {
        status: 'done',
      });
      const flatResults = results.flatMap((r) => r.results);
      flatResults.forEach((result) => {
        expect(result.item.status).toBe('done');
      });
    });

    it('should apply perspective filter', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth', {
        perspectives: ['code', 'api'],
      });
      expect(results.every((g) => ['code', 'api'].includes(g.perspective))).toBeTruthy();
    });

    it('should score exact title matches higher than substring matches', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'users_table');
      const flatResults = results.flatMap((r) => r.results);
      expect(flatResults.some((r) => r.item.id === '4')).toBeTruthy();
    });

    it('should handle special characters in search', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, '/auth/login');
      const flatResults = results.flatMap((r) => r.results);
      expect(flatResults.some((r) => r.item.id === '5')).toBeTruthy();
    });
  });

  describe('Match type detection', () => {
    it('should detect title matches', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'User Authentication');
      const flatResults = results.flatMap((r) => r.results);
      const titleMatch = flatResults.find((r) => r.item.id === '1');
      expect(titleMatch?.matchType).toBe('title');
    });

    it('should detect description matches', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'React component');
      const flatResults = results.flatMap((r) => r.results);
      const descMatch = flatResults.find((r) => r.item.id === '2');
      expect(descMatch?.matchType).toBe('description');
    });

    it('should detect type matches', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'TestSuite');
      const flatResults = results.flatMap((r) => r.results);
      const typeMatch = flatResults.find((r) => r.item.id === '3');
      expect(typeMatch?.matchType).toBe('type');
    });
  });

  describe('Equivalence confidence sorting', () => {
    it('should sort equivalences by confidence (descending)', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      const item1Results = results.flatMap((r) => r.results).filter((r) => r.item.id === '1');
      if (item1Results.length > 0) {
        const { equivalences } = item1Results[0];
        for (let i = 1; i < equivalences.length; i++) {
          expect(equivalences[i].confidence).toBeLessThanOrEqual(equivalences[i - 1].confidence);
        }
      }
    });
  });

  describe('Cross-perspective discovery', () => {
    it('should identify items from multiple perspectives for same concept', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      const perspectives = results.map((r) => r.perspective);
      expect(perspectives.length).toBeGreaterThan(1);
    });

    it('should show equivalence relationships across perspectives', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');
      const flatResults = results.flatMap((r) => r.results);
      const item1 = flatResults.find((r) => r.item.id === '1');
      if (item1?.equivalences.length) {
        const equivPerspectives = item1.equivalences.map((e) => e.equivalentPerspective);
        expect(equivPerspectives).toContain('code');
        expect(equivPerspectives).toContain('api');
      }
    });
  });

  describe('Performance', () => {
    it('should handle large result sets efficiently', () => {
      const largeItems: Item[] = Array.from({ length: 1000 }, (_, i) => ({
        ...mockItems[0],
        id: `item-${i}`,
        title: `Item ${i} with auth`,
      }));

      const startTime = performance.now();
      const results = performCrossPerspectiveSearch(largeItems, mockLinks, 'auth');
      const endTime = performance.now();

      expect(results.length).toBeGreaterThan(0);
      expect(endTime - startTime).toBeLessThan(100);
    });
  });
});
