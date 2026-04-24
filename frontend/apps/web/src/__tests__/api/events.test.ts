/**
 * Tests for Events API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchEvent, fetchEvents } from '@/api/events';

// Mock the client
vi.mock('@/api/client', () => ({
  client: {
    apiClient: {
      GET: vi.fn(),
    },
    handleApiResponse: vi.fn(),
    safeApiCall: vi.fn(),
  },
}));

import { client } from '@/api/client';

const { apiClient, handleApiResponse, safeApiCall } = client;

describe('Events API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchEvents, () => {
    it('should fetch events without params', async () => {
      const mockEvents = [
        {
          id: '1',
          payload: {},
          projectId: 'proj-1',
          timestamp: '2024-01-01',
          type: 'item_created',
        },
      ];
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockEvents,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockEvents,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(handleApiResponse).mockResolvedValue(mockEvents);

      const result = await fetchEvents();
      expect(result).toEqual(mockEvents);
      expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/events', {
        params: { query: undefined },
      });
    });

    it('should fetch events with params', async () => {
      const mockEvents = [];
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockEvents,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockEvents,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(handleApiResponse).mockResolvedValue(mockEvents);

      const result = await fetchEvents({ limit: 10, offset: 0 });
      expect(result).toEqual(mockEvents);
      expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/events', {
        params: { query: { limit: 10, offset: 0 } },
      });
    });

    it('should return empty array on error', async () => {
      vi.mocked(apiClient.GET).mockRejectedValue(new Error('Network error'));
      vi.mocked(safeApiCall).mockRejectedValue(new Error('Network error'));
      vi.mocked(handleApiResponse).mockRejectedValue(new Error('Network error'));

      const result = await fetchEvents();
      expect(result).toEqual([]);
    });
  });

  describe(fetchEvent, () => {
    it('should fetch a single event by id', async () => {
      const mockEvent = {
        id: '1',
        payload: {},
        timestamp: '2024-01-01',
        type: 'item_created',
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockEvent,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockEvent,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(handleApiResponse).mockResolvedValue(mockEvent);

      const result = await fetchEvent('1');
      expect(result).toEqual(mockEvent);
      expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/events/{id}', {
        params: { path: { id: '1' } },
      });
    });

    it('should return undefined on error', async () => {
      vi.mocked(apiClient.GET).mockRejectedValue(new Error('Not found'));
      vi.mocked(safeApiCall).mockRejectedValue(new Error('Not found'));
      vi.mocked(handleApiResponse).mockRejectedValue(new Error('Not found'));

      const result = await fetchEvent('non-existent');
      expect(result).toBeUndefined();
    });
  });
});
