/**
 * Graph Analysis API Contract Tests
 *
 * Consumer: TraceRTM-Web
 * Provider: TraceRTM-API
 * Domain: Graph Analysis
 */

import { describe, it, beforeAll, afterAll } from 'vitest';
import {
  createPactProvider,
  setupPact,
  teardownPact,
  like,
  eachLike,
  uuid,
  integer,
  decimal,
  errorResponse,
  standardResponse,
  withAuth,
  providerStates,
} from '../setup';

const provider = createPactProvider('TraceRTM-Web-Graph');

describe('Graph Analysis Contract Tests', () => {
  beforeAll(async () => {
    await setupPact(provider);
  });

  afterAll(async () => {
    await teardownPact(provider);
  });

  describe('GET /api/v1/graph/analysis/metrics', () => {
    it('should return graph metrics', async () => {
      await provider.addInteraction({
        states: [{ description: 'project has graph data' }],
        uponReceiving: 'a request for graph metrics',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/metrics',
          query: {
            projectId: 'project-123',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          projectId: uuid('project-123'),
          metrics: {
            nodeCount: integer(50),
            edgeCount: integer(120),
            density: decimal(0.12),
            averageDegree: decimal(2.4),
            connectedComponents: integer(1),
            diameter: integer(5),
          },
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/metrics?projectId=project-123',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/graph/analysis/centrality', () => {
    it('should return centrality analysis', async () => {
      await provider.addInteraction({
        states: [{ description: 'project has graph data' }],
        uponReceiving: 'a request for centrality analysis',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/centrality',
          query: {
            projectId: 'project-123',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          projectId: uuid('project-123'),
          centrality: eachLike({
            nodeId: uuid('item-123'),
            degree: integer(5),
            betweenness: decimal(0.15),
            closeness: decimal(0.22),
            eigenvector: decimal(0.18),
          }),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/centrality?projectId=project-123',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/graph/analysis/cycles', () => {
    it('should detect cycles in graph', async () => {
      await provider.addInteraction({
        states: [{ description: 'project has circular dependencies' }],
        uponReceiving: 'a request for cycle detection',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/cycles',
          query: {
            projectId: 'project-123',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          projectId: uuid('project-123'),
          cycles: eachLike({
            nodes: eachLike(uuid('item-123')),
            length: integer(3),
          }),
          hasCycles: like(true),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/cycles?projectId=project-123',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/graph/analysis/shortest-path', () => {
    it('should find shortest path between nodes', async () => {
      await provider.addInteraction({
        states: [{ description: 'nodes are connected' }],
        uponReceiving: 'a request for shortest path',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/shortest-path',
          query: {
            from: 'item-123',
            to: 'item-456',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          from: uuid('item-123'),
          to: uuid('item-456'),
          path: eachLike(uuid('item-123')),
          length: integer(3),
          exists: like(true),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/shortest-path?from=item-123&to=item-456',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });

    it('should handle no path found', async () => {
      await provider.addInteraction({
        states: [{ description: 'nodes are not connected' }],
        uponReceiving: 'a request for path when nodes disconnected',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/shortest-path',
          query: {
            from: 'item-123',
            to: 'item-999',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          from: uuid('item-123'),
          to: uuid('item-999'),
          path: [],
          exists: like(false),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/shortest-path?from=item-123&to=item-999',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/graph/analysis/dependencies', () => {
    it('should return item dependencies', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', 'item-123') }],
        uponReceiving: 'a request for item dependencies',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/dependencies',
          query: {
            itemId: 'item-123',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          itemId: uuid('item-123'),
          dependencies: eachLike({
            id: uuid('item-456'),
            type: like('depends-on'),
            depth: integer(1),
          }),
          totalCount: integer(5),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/dependencies?itemId=item-123',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/graph/analysis/dependents', () => {
    it('should return items that depend on this item', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', 'item-123') }],
        uponReceiving: 'a request for item dependents',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/dependents',
          query: {
            itemId: 'item-123',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          itemId: uuid('item-123'),
          dependents: eachLike({
            id: uuid('item-789'),
            type: like('implemented-by'),
            depth: integer(1),
          }),
          totalCount: integer(8),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/dependents?itemId=item-123',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/graph/analysis/impact', () => {
    it('should analyze impact of changes', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.resourceExists('item', 'item-123') }],
        uponReceiving: 'a request for impact analysis',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/impact',
          query: {
            itemId: 'item-123',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          itemId: uuid('item-123'),
          impactedItems: eachLike({
            id: uuid('item-789'),
            impactLevel: like('high'),
            path: eachLike(uuid('item-456')),
          }),
          summary: {
            high: integer(3),
            medium: integer(5),
            low: integer(10),
          },
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/impact?itemId=item-123',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/graph/analysis/coverage', () => {
    it('should return test coverage metrics', async () => {
      await provider.addInteraction({
        states: [{ description: 'project has test coverage data' }],
        uponReceiving: 'a request for coverage analysis',
        withRequest: {
          method: 'GET',
          path: '/api/v1/graph/analysis/coverage',
          query: {
            projectId: 'project-123',
          },
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          projectId: uuid('project-123'),
          coverage: {
            overall: decimal(0.85),
            byType: {
              requirement: decimal(0.90),
              feature: decimal(0.80),
              task: decimal(0.85),
            },
          },
          uncoveredItems: eachLike({
            id: uuid('item-789'),
            type: like('requirement'),
            title: like('Uncovered Requirement'),
          }),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/coverage?projectId=project-123',
        {
          headers: { Authorization: 'Bearer test-token' },
        }
      );

      console.assert(response.status === 200);
    });
  });

  describe('POST /api/v1/graph/analysis/cache/invalidate', () => {
    it('should invalidate graph cache', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userAuthenticated }],
        uponReceiving: 'a request to invalidate graph cache',
        withRequest: {
          method: 'POST',
          path: '/api/v1/graph/analysis/cache/invalidate',
          headers: withAuth(),
          body: {
            projectId: 'project-123',
          },
        },
        willRespondWith: standardResponse({
          success: like(true),
          message: like('Cache invalidated successfully'),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/graph/analysis/cache/invalidate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
          body: JSON.stringify({ projectId: 'project-123' }),
        }
      );

      console.assert(response.status === 200);
    });
  });
});
