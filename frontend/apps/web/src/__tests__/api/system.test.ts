/**
 * Tests for System API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchSystemStatus } from '@/api/system';

// Mock client
vi.mock('@/api/client', () => ({
  client: {
    apiClient: {
      GET: vi.fn(),
    },
  },
}));
vi.mock('@/api/mcp-config', () => ({
  getMcpConfig: vi.fn(),
}));

import { client } from '@/api/client';
import { getMcpConfig } from '@/api/mcp-config';

const { apiClient } = client;

describe('System API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchSystemStatus, () => {
    it('should fetch system status successfully', async () => {
      const mockStatus = {
        queuedJobs: 2,
        status: 'healthy' as const,
        uptime: 99.9,
        version: '1.0.0',
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: mockStatus,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(getMcpConfig).mockResolvedValue({
        auth_mode: 'authkit',
        mcp_base_url: 'http://localhost:9000',
        requires_auth: true,
      });

      const result = await fetchSystemStatus();
      expect(result).toEqual({
        ...mockStatus,
        mcp: {
          authMode: 'authkit',
          baseUrl: 'http://localhost:9000',
          requiresAuth: true,
        },
      });
      expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/health', {});
    });

    it('should return mock data when endpoint fails', async () => {
      vi.mocked(apiClient.GET).mockRejectedValue(new Error('Network error'));
      vi.mocked(getMcpConfig).mockResolvedValue({
        mcp_base_url: 'http://localhost:9000',
      });

      const result = await fetchSystemStatus();
      expect(result).toEqual({
        queuedJobs: 0,
        status: 'healthy',
        uptime: 99.9,
      });
    });

    it('should merge response data with defaults', async () => {
      const responseData = {
        status: 'degraded' as const,
        version: '2.0.0',
      };
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: responseData,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(getMcpConfig).mockResolvedValue({
        auth_mode: 'authkit',
        mcp_base_url: 'http://localhost:9000',
        requires_auth: true,
      });

      const result = await fetchSystemStatus();
      expect(result).toEqual({
        status: 'healthy', // Overridden by response
        uptime: 99.9,
        queuedJobs: 0,
        mcp: {
          authMode: 'authkit',
          baseUrl: 'http://localhost:9000',
          requiresAuth: true,
        },
        ...responseData,
      });
      expect(result.status).toBe('degraded');
      expect(result.version).toBe('2.0.0');
    });

    it('should handle empty response data', async () => {
      vi.mocked(apiClient.GET).mockResolvedValue({
        data: null,
        error: undefined,
        response: new Response(),
      });
      vi.mocked(getMcpConfig).mockResolvedValue({
        mcp_base_url: 'http://localhost:9000',
      });

      const result = await fetchSystemStatus();
      expect(result).toEqual({
        queuedJobs: 0,
        status: 'healthy',
        uptime: 99.9,
      });
    });
  });
});
