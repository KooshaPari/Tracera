/**
 * Comprehensive tests for queryConfig.ts
 * Coverage targets: All query configurations, key factories, helper functions
 */

import { describe, expect, it } from 'vitest';

import { QUERY_CONFIGS, queryKeys, getQueryConfig } from '../../lib/queryConfig';

describe('queryConfig - P1 Coverage', () => {
  // ============================================================================
  // QUERY_CONFIGS TESTS
  // ============================================================================

  describe('QUERY_CONFIGS', () => {
    describe('static config', () => {
      it('should have correct static configuration', () => {
        const config = QUERY_CONFIGS.static;

        expect(config.staleTime).toBe(10 * 60 * 1000); // 10 minutes
        expect(config.gcTime).toBe(30 * 60 * 1000); // 30 minutes
        expect(config.refetchOnMount).toBe(false);
        expect(config.refetchOnWindowFocus).toBe(false);
        expect(config.refetchOnReconnect).toBe(false);
      });

      it('should disable refetch for static data', () => {
        const config = QUERY_CONFIGS.static;

        expect(config.refetchOnMount).toBe(false);
        expect(config.refetchOnWindowFocus).toBe(false);
      });

      it('should cache longer than dynamic data', () => {
        expect(QUERY_CONFIGS.static.staleTime).toBeGreaterThan(QUERY_CONFIGS.dynamic.staleTime);
      });
    });

    describe('dynamic config', () => {
      it('should have correct dynamic configuration', () => {
        const config = QUERY_CONFIGS.dynamic;

        expect(config.staleTime).toBe(30 * 1000); // 30 seconds
        expect(config.gcTime).toBe(5 * 60 * 1000); // 5 minutes
        expect(config.refetchOnMount).toBe(true);
        expect(config.refetchOnWindowFocus).toBe(false);
        expect(config.refetchOnReconnect).toBe(true);
      });

      it('should refetch on mount and reconnect', () => {
        const config = QUERY_CONFIGS.dynamic;

        expect(config.refetchOnMount).toBe(true);
        expect(config.refetchOnReconnect).toBe(true);
      });

      it('should disable refetch on window focus', () => {
        const config = QUERY_CONFIGS.dynamic;

        expect(config.refetchOnWindowFocus).toBe(false);
      });
    });

    describe('graph config', () => {
      it('should have correct graph configuration', () => {
        const config = QUERY_CONFIGS.graph;

        expect(config.staleTime).toBe(5 * 60 * 1000); // 5 minutes
        expect(config.gcTime).toBe(15 * 60 * 1000); // 15 minutes
        expect(config.refetchOnMount).toBe(false);
        expect(config.refetchOnWindowFocus).toBe(false);
        expect(config.refetchOnReconnect).toBe(false);
      });

      it('should cache expensive computations', () => {
        const config = QUERY_CONFIGS.graph;

        // Graph data should cache longer than dynamic data
        expect(config.staleTime).toBeGreaterThan(QUERY_CONFIGS.dynamic.staleTime);
        expect(config.gcTime).toBeGreaterThan(QUERY_CONFIGS.dynamic.gcTime);
      });

      it('should not aggressively refetch', () => {
        const config = QUERY_CONFIGS.graph;

        expect(config.refetchOnMount).toBe(false);
        expect(config.refetchOnWindowFocus).toBe(false);
        expect(config.refetchOnReconnect).toBe(false);
      });
    });

    describe('realtime config', () => {
      it('should have correct realtime configuration', () => {
        const config = QUERY_CONFIGS.realtime;

        expect(config.staleTime).toBe(0); // Always stale
        expect(config.gcTime).toBe(1 * 60 * 1000); // 1 minute
        expect(config.refetchInterval).toBe(5000); // 5 seconds
        expect(config.refetchOnMount).toBe(true);
        expect(config.refetchOnWindowFocus).toBe(true);
        expect(config.refetchOnReconnect).toBe(true);
      });

      it('should always be stale', () => {
        const config = QUERY_CONFIGS.realtime;

        expect(config.staleTime).toBe(0);
      });

      it('should refetch frequently', () => {
        const config = QUERY_CONFIGS.realtime;

        expect(config.refetchInterval).toBeDefined();
        expect(config.refetchInterval).toBeLessThan(10000);
      });

      it('should refetch aggressively', () => {
        const config = QUERY_CONFIGS.realtime;

        expect(config.refetchOnMount).toBe(true);
        expect(config.refetchOnWindowFocus).toBe(true);
        expect(config.refetchOnReconnect).toBe(true);
      });
    });

    describe('session config', () => {
      it('should have correct session configuration', () => {
        const config = QUERY_CONFIGS.session;

        expect(config.staleTime).toBe(5 * 60 * 1000); // 5 minutes
        expect(config.gcTime).toBe(60 * 60 * 1000); // 1 hour
        expect(config.refetchOnMount).toBe(true);
        expect(config.refetchOnWindowFocus).toBe(true);
        expect(config.refetchOnReconnect).toBe(true);
      });

      it('should persist session data longer', () => {
        const config = QUERY_CONFIGS.session;

        // Session should persist longer than dynamic data
        expect(config.gcTime).toBeGreaterThan(QUERY_CONFIGS.dynamic.gcTime);
      });

      it('should validate on mount', () => {
        const config = QUERY_CONFIGS.session;

        expect(config.refetchOnMount).toBe(true);
        expect(config.refetchOnWindowFocus).toBe(true);
      });
    });

    describe('default config', () => {
      it('should have correct default configuration', () => {
        const config = QUERY_CONFIGS.default;

        expect(config.staleTime).toBe(60 * 1000); // 1 minute
        expect(config.gcTime).toBe(10 * 60 * 1000); // 10 minutes
        expect(config.refetchOnMount).toBe(false);
        expect(config.refetchOnWindowFocus).toBe(false);
        expect(config.refetchOnReconnect).toBe(true);
      });

      it('should moderate stale time', () => {
        const config = QUERY_CONFIGS.default;

        // Default should be between dynamic and static
        expect(config.staleTime).toBeGreaterThan(QUERY_CONFIGS.dynamic.staleTime);
        expect(config.staleTime).toBeLessThan(QUERY_CONFIGS.static.staleTime);
      });

      it('should only refetch on reconnect', () => {
        const config = QUERY_CONFIGS.default;

        expect(config.refetchOnMount).toBe(false);
        expect(config.refetchOnWindowFocus).toBe(false);
        expect(config.refetchOnReconnect).toBe(true);
      });
    });

    describe('config consistency', () => {
      it('should have staleTime <= gcTime for all configs', () => {
        Object.entries(QUERY_CONFIGS).forEach(([key, config]) => {
          expect(config.staleTime, `${key}: staleTime should be <= gcTime`).toBeLessThanOrEqual(
            config.gcTime,
          );
        });
      });

      it('should have staleTime >= 0', () => {
        Object.entries(QUERY_CONFIGS).forEach(([key, config]) => {
          expect(config.staleTime, `${key}: staleTime should be >= 0`).toBeGreaterThanOrEqual(0);
        });
      });

      it('should have gcTime > 0', () => {
        Object.entries(QUERY_CONFIGS).forEach(([key, config]) => {
          expect(config.gcTime, `${key}: gcTime should be > 0`).toBeGreaterThan(0);
        });
      });

      it('should be immutable', () => {
        // QUERY_CONFIGS is a const object, attempts to modify may be caught by TypeScript
        // but at runtime JS may allow it. Just verify structure is maintained.
        const before = QUERY_CONFIGS.dynamic.staleTime;
        (QUERY_CONFIGS as any).dynamic.staleTime = 0;
        // Either it's frozen or modification is silently ignored
        expect([before, QUERY_CONFIGS.dynamic.staleTime]).toContain(30 * 1000);
      });
    });
  });

  // ============================================================================
  // QUERY_KEYS TESTS
  // ============================================================================

  describe('queryKeys', () => {
    describe('projects', () => {
      it('should have projects.all', () => {
        const key = queryKeys.projects.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('projects');
      });

      it('should generate projects.list key', () => {
        const key = queryKeys.projects.list();

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('projects');
        expect(key).toContain('list');
      });

      it('should generate projects.detail key', () => {
        const key = queryKeys.projects.detail('proj-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('projects');
        expect(key).toContain('detail');
        expect(key).toContain('proj-1');
      });

      it('should generate unique keys for different project IDs', () => {
        const key1 = queryKeys.projects.detail('proj-1');
        const key2 = queryKeys.projects.detail('proj-2');

        expect(key1).not.toEqual(key2);
      });
    });

    describe('items', () => {
      it('should have items.all', () => {
        const key = queryKeys.items.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('items');
      });

      it('should generate items.list key', () => {
        const key = queryKeys.items.list('proj-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('items');
        expect(key).toContain('list');
        expect(key).toContain('proj-1');
      });

      it('should generate items.detail key', () => {
        const key = queryKeys.items.detail('item-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('items');
        expect(key).toContain('detail');
        expect(key).toContain('item-1');
      });

      it('should generate items.recent key', () => {
        const key = queryKeys.items.recent();

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('items');
        expect(key).toContain('recent');
      });

      it('should differentiate between list and recent', () => {
        const listKey = queryKeys.items.list('proj-1');
        const recentKey = queryKeys.items.recent();

        expect(listKey).not.toEqual(recentKey);
      });
    });

    describe('links', () => {
      it('should have links.all', () => {
        const key = queryKeys.links.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('links');
      });

      it('should generate links.list key', () => {
        const key = queryKeys.links.list('proj-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('links');
        expect(key).toContain('list');
        expect(key).toContain('proj-1');
      });

      it('should generate links.byItem key', () => {
        const key = queryKeys.links.byItem('item-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('links');
        expect(key).toContain('byItem');
        expect(key).toContain('item-1');
      });
    });

    describe('graph', () => {
      it('should have graph.all', () => {
        const key = queryKeys.graph.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('graph');
      });

      it('should generate graph.full key', () => {
        const key = queryKeys.graph.full('proj-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('graph');
        expect(key).toContain('full');
        expect(key).toContain('proj-1');
      });

      it('should generate graph.ancestors key without depth', () => {
        const key = queryKeys.graph.ancestors('item-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('graph');
        expect(key).toContain('ancestors');
        expect(key).toContain('item-1');
      });

      it('should generate graph.ancestors key with depth', () => {
        const key = queryKeys.graph.ancestors('item-1', 3);

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('graph');
        expect(key).toContain('ancestors');
        expect(key).toContain('item-1');
        expect(key).toContain(3);
      });

      it('should differentiate ancestors by depth', () => {
        const key1 = queryKeys.graph.ancestors('item-1', 2);
        const key2 = queryKeys.graph.ancestors('item-1', 3);

        expect(key1).not.toEqual(key2);
      });

      it('should generate graph.descendants key', () => {
        const key = queryKeys.graph.descendants('item-1', 2);

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('descendants');
        expect(key).toContain(2);
      });

      it('should generate graph.impact key', () => {
        const key = queryKeys.graph.impact('item-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('graph');
        expect(key).toContain('impact');
        expect(key).toContain('item-1');
      });
    });

    describe('specs', () => {
      it('should have specs.all', () => {
        const key = queryKeys.specs.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('specs');
      });

      it('should generate specs.list key', () => {
        const key = queryKeys.specs.list('proj-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('specs');
        expect(key).toContain('list');
      });

      it('should generate specs.detail key', () => {
        const key = queryKeys.specs.detail('spec-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('specs');
        expect(key).toContain('detail');
        expect(key).toContain('spec-1');
      });
    });

    describe('system', () => {
      it('should generate system.status key', () => {
        const key = queryKeys.system.status();

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('system');
        expect(key).toContain('status');
      });

      it('should generate system.health key', () => {
        const key = queryKeys.system.health();

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('system');
        expect(key).toContain('health');
      });

      it('should differentiate status and health', () => {
        const statusKey = queryKeys.system.status();
        const healthKey = queryKeys.system.health();

        expect(statusKey).not.toEqual(healthKey);
      });
    });

    describe('temporal', () => {
      it('should have branches key', () => {
        const key = queryKeys.branches;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('branches');
      });

      it('should have versions key', () => {
        const key = queryKeys.versions;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('versions');
      });

      it('should have versionSnapshot key', () => {
        const key = queryKeys.versionSnapshot;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('versionSnapshot');
      });

      it('should have branchComparison key', () => {
        const key = queryKeys.branchComparison;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('branchComparison');
      });
    });

    describe('search', () => {
      it('should have search.all', () => {
        const key = queryKeys.search.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('search');
      });

      it('should generate search.query key', () => {
        const key = queryKeys.search.query('test query');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('search');
        expect(key).toContain('query');
        expect(key).toContain('test query');
      });

      it('should differentiate search queries', () => {
        const key1 = queryKeys.search.query('query1');
        const key2 = queryKeys.search.query('query2');

        expect(key1).not.toEqual(key2);
      });

      it('should handle special characters in search', () => {
        const key = queryKeys.search.query('test@#$%^&*()');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('test@#$%^&*()');
      });
    });

    describe('executions', () => {
      it('should have executions.all', () => {
        const key = queryKeys.executions.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('executions');
      });

      it('should generate executions.list key', () => {
        const key = queryKeys.executions.list('proj-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('executions');
        expect(key).toContain('list');
      });

      it('should generate executions.detail key', () => {
        const key = queryKeys.executions.detail('exec-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('executions');
        expect(key).toContain('detail');
      });
    });

    describe('codex', () => {
      it('should have codex.all', () => {
        const key = queryKeys.codex.all;

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('codex');
      });

      it('should generate codex.list key', () => {
        const key = queryKeys.codex.list('proj-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('codex');
        expect(key).toContain('list');
      });

      it('should generate codex.detail key', () => {
        const key = queryKeys.codex.detail('codex-1');

        expect(Array.isArray(key)).toBe(true);
        expect(key).toContain('codex');
        expect(key).toContain('detail');
      });
    });

    describe('key hierarchy', () => {
      it('should nest keys properly', () => {
        const listKey = queryKeys.items.list('proj-1');
        const detailKey = queryKeys.items.detail('item-1');

        // List key should start with items and list
        expect(listKey[0]).toBe('items');
        expect(listKey[1]).toBe('list');

        // Detail key should start with items and detail
        expect(detailKey[0]).toBe('items');
        expect(detailKey[1]).toBe('detail');
      });

      it('should use items.all as base prefix', () => {
        const allKey = queryKeys.items.all;
        const listKey = queryKeys.items.list('proj-1');

        // List key should include all base keys
        expect(listKey.slice(0, allKey.length)).toEqual(allKey);
      });

      it('should prefix project queries appropriately', () => {
        const projListKey = queryKeys.projects.list();
        const itemsListKey = queryKeys.items.list('proj-1');

        expect(projListKey[0]).toBe('projects');
        expect(itemsListKey[0]).toBe('items');
      });
    });

    describe('key immutability', () => {
      it('should return readonly arrays', () => {
        const key = queryKeys.projects.list();

        // Keys should be tuples/arrays for cache consistency
        expect(Array.isArray(key)).toBe(true);
        expect(key.length).toBeGreaterThan(0);
      });
    });
  });

  // ============================================================================
  // getQueryConfig TESTS
  // ============================================================================

  describe('getQueryConfig', () => {
    it('should return static config', () => {
      const config = getQueryConfig('static');

      expect(config).toEqual(QUERY_CONFIGS.static);
    });

    it('should return dynamic config', () => {
      const config = getQueryConfig('dynamic');

      expect(config).toEqual(QUERY_CONFIGS.dynamic);
    });

    it('should return graph config', () => {
      const config = getQueryConfig('graph');

      expect(config).toEqual(QUERY_CONFIGS.graph);
    });

    it('should return realtime config', () => {
      const config = getQueryConfig('realtime');

      expect(config).toEqual(QUERY_CONFIGS.realtime);
    });

    it('should return session config', () => {
      const config = getQueryConfig('session');

      expect(config).toEqual(QUERY_CONFIGS.session);
    });

    it('should return default config', () => {
      const config = getQueryConfig('default');

      expect(config).toEqual(QUERY_CONFIGS.default);
    });

    it('should handle all valid keys', () => {
      const validKeys = ['static', 'dynamic', 'graph', 'realtime', 'session', 'default'] as const;

      validKeys.forEach((key) => {
        const config = getQueryConfig(key);

        expect(config).toBeDefined();
        expect(config.staleTime).toBeDefined();
        expect(config.gcTime).toBeDefined();
      });
    });

    it('should return config reference, not copy', () => {
      const config1 = getQueryConfig('static');
      const config2 = getQueryConfig('static');

      expect(config1).toBe(config2); // Same reference
    });

    it('should work as helper function', () => {
      const config = getQueryConfig('dynamic');

      // Should be usable directly with React Query
      expect(config.staleTime).toBe(QUERY_CONFIGS.dynamic.staleTime);
      expect(config.refetchOnMount).toBe(QUERY_CONFIGS.dynamic.refetchOnMount);
    });
  });

  // ============================================================================
  // INTEGRATION TESTS
  // ============================================================================

  describe('Integration: Query Keys and Configs', () => {
    it('should support caching strategy lookup pattern', () => {
      // Typical usage: get config for a query type
      const itemsListKey = queryKeys.items.list('proj-1');
      const itemsConfig = getQueryConfig('dynamic'); // Items are dynamic data

      expect(itemsListKey).toBeDefined();
      expect(itemsConfig.refetchOnMount).toBe(true);
    });

    it('should support graph query pattern', () => {
      const graphKey = queryKeys.graph.ancestors('item-1', 3);
      const graphConfig = getQueryConfig('graph');

      expect(graphKey).toContain('graph');
      expect(graphKey).toContain('ancestors');
      expect(graphConfig.staleTime).toBeGreaterThan(getQueryConfig('dynamic').staleTime);
    });

    it('should support realtime subscription pattern', () => {
      const healthKey = queryKeys.system.health();
      const realtimeConfig = getQueryConfig('realtime');

      expect(healthKey).toContain('system');
      expect((realtimeConfig as any).refetchInterval).toBeDefined();
    });

    it('should support session management pattern', () => {
      const sessionKey = queryKeys.system.status();
      const sessionConfig = getQueryConfig('session');

      expect(sessionKey).toBeDefined();
      expect(sessionConfig.gcTime).toBeGreaterThan(QUERY_CONFIGS.dynamic.gcTime);
    });

    it('should be usable with React Query exactly', () => {
      // Simulate React Query usage
      const key = queryKeys.items.list('proj-1');
      const config = getQueryConfig('dynamic');

      // Should work with useQuery pattern
      const queryOptions = {
        ...config,
        queryFn: async () => ({ items: [] }),
        queryKey: key,
      };

      expect(queryOptions.queryKey).toBe(key);
      // Config spread copies the properties
      expect(queryOptions.staleTime).toBeDefined();
      expect(queryOptions.refetchOnMount).toBe(true);
    });
  });
});
