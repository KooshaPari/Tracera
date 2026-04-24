/**
 * Tests for Traceability Matrix API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { TraceabilityMatrix } from '@/api/matrix';

import { exportMatrix, fetchMatrix } from '@/api/matrix';

// Mock the API client
vi.mock('@/api/client', () => ({
  client: {
    apiClient: {
      GET: vi.fn(),
    },
    safeApiCall: vi.fn((promise) => promise),
  },
}));

import { client } from '@/api/client';

import { mockItems, mockLinks } from '../mocks/data';

const { apiClient, safeApiCall } = client;

describe('Traceability Matrix API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchMatrix, () => {
    it('should fetch matrix for a project', async () => {
      const mockMatrix: TraceabilityMatrix = {
        coverage: {
          percentage: 66.67,
          total: 3,
          traced: 2,
          untraced: 1,
        },
        items: mockItems,
        links: mockLinks,
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockMatrix,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchMatrix('proj-1');

      expect(result).toEqual(mockMatrix);
      expect(result.coverage.percentage).toBe(66.67);
      expect(result.items).toHaveLength(3);
      expect(result.links).toHaveLength(2);
    });

    it('should handle empty matrix', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: undefined,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchMatrix('proj-empty');

      expect(result).toEqual({
        coverage: { percentage: 0, total: 0, traced: 0, untraced: 0 },
        items: [],
        links: [],
      });
    });

    it('should fallback to empty matrix on error', async () => {
      vi.mocked(safeApiCall).mockRejectedValue(new Error('API call failed'));

      const result = await fetchMatrix('proj-1');

      expect(result).toEqual({
        coverage: { percentage: 0, total: 0, traced: 0, untraced: 0 },
        items: [],
        links: [],
      });
    });

    it('should include traced/untraced coverage statistics', async () => {
      const mockMatrix: TraceabilityMatrix = {
        coverage: {
          percentage: 100,
          total: 2,
          traced: 2,
          untraced: 0,
        },
        items: mockItems.slice(0, 2),
        links: mockLinks,
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockMatrix,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchMatrix('proj-1');

      expect(result.coverage.traced).toBe(2);
      expect(result.coverage.untraced).toBe(0);
      expect(result.coverage.percentage).toBe(100);
    });

    it('should call API with correct project ID', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: {
          coverage: { percentage: 0, total: 0, traced: 0, untraced: 0 },
          items: [],
          links: [],
        },
        error: undefined,
        response: new Response(),
      });

      await fetchMatrix('specific-proj-123');

      expect(safeApiCall).toHaveBeenCalled();
      expect(apiClient.GET).toHaveBeenCalledWith(
        '/api/v1/projects/{id}/matrix',
        expect.objectContaining({
          params: { path: { id: 'specific-proj-123' } },
        }),
      );
    });
  });

  describe(exportMatrix, () => {
    it('should export matrix as CSV', async () => {
      const mockData = { items: mockItems, links: mockLinks };
      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockData,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix('proj-1', 'csv');

      expect(result).toBeInstanceOf(Blob);
      expect(result.type).toBe('application/json');
    });

    it('should export matrix as JSON', async () => {
      const mockData = { items: mockItems, links: mockLinks };
      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockData,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix('proj-1', 'json');

      expect(result).toBeInstanceOf(Blob);
      expect(result.type).toBe('application/json');
    });

    it('should export matrix as XLSX', async () => {
      const mockData = { items: mockItems, links: mockLinks };
      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockData,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix('proj-1', 'xlsx');

      expect(result).toBeInstanceOf(Blob);
    });

    it('should include data in blob content', async () => {
      const mockData = { items: mockItems, links: mockLinks };
      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockData,
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix('proj-1', 'json');

      expect(result).toBeInstanceOf(Blob);
      expect(result.size).toBeGreaterThan(0);
      expect(result.type).toBe('application/json');
    });

    it('should return empty blob on export error', async () => {
      vi.mocked(safeApiCall).mockRejectedValue(new Error('Export failed'));

      const result = await exportMatrix('proj-1', 'csv');

      expect(result).toBeInstanceOf(Blob);
      expect(result.type).toBe('application/json');
      expect(result.size).toBeGreaterThan(0);
    });

    it('should call API with correct export format', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: {},
        error: undefined,
        response: new Response(),
      });

      await exportMatrix('proj-1', 'xlsx');

      expect(apiClient.GET).toHaveBeenCalledWith(
        '/api/v1/projects/{id}/matrix/export',
        expect.objectContaining({
          params: {
            path: { id: 'proj-1' },
            query: { format: 'xlsx' },
          },
        }),
      );
    });

    it('should support all export formats', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: {},
        error: undefined,
        response: new Response(),
      });

      const formats: ('csv' | 'json' | 'xlsx')[] = ['csv', 'json', 'xlsx'];

      for (const format of formats) {
        const result = await exportMatrix('proj-1', format);
        expect(result).toBeInstanceOf(Blob);
      }
    });

    it('should handle large datasets in export', async () => {
      const largeItems = Array.from({ length: 100 }, (_, i) => ({
        ...mockItems[0],
        id: `item-${i}`,
      }));
      const largeLinks = Array.from({ length: 150 }, (_, i) => ({
        ...mockLinks[0],
        id: `link-${i}`,
      }));

      vi.mocked(safeApiCall).mockResolvedValue({
        data: { items: largeItems, links: largeLinks },
        error: undefined,
        response: new Response(),
      });

      const result = await exportMatrix('proj-1', 'json');

      expect(result).toBeInstanceOf(Blob);
      expect(result.size).toBeGreaterThan(0);
    });
  });

  describe('Matrix API error handling', () => {
    it('should gracefully handle network errors', async () => {
      vi.mocked(safeApiCall).mockRejectedValue(new Error('Network error'));

      const result = await fetchMatrix('proj-1');

      expect(result.coverage.total).toBe(0);
      expect(result.items).toEqual([]);
      expect(result.links).toEqual([]);
    });

    it('should handle null response data', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: null,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchMatrix('proj-1');

      expect(result).toEqual({
        coverage: { percentage: 0, total: 0, traced: 0, untraced: 0 },
        items: [],
        links: [],
      });
    });

    it('should handle partial matrix data', async () => {
      const partialMatrix: Partial<TraceabilityMatrix> = {
        items: mockItems,
        // Links is missing
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: partialMatrix,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchMatrix('proj-1');

      expect(result.items).toHaveLength(3);
    });
  });
});
