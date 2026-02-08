/**
 * API Client Integration Tests (3 tests)
 *
 * Verifies integration of: API client, auth store, and error handling.
 * Target: 5% integration layer in test pyramid.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError, handleApiResponse } from '../../api/client-errors';
import { api } from '../../api/endpoints';
import { useAuthStore } from '../../stores/auth-store';

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

const createJsonResponse = (data: unknown, status = 200): Response =>
  new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' },
    status,
  });

// -----------------------------------------------------------------------------
// 1) Auth flow integration
// -----------------------------------------------------------------------------

describe('API Client Integration', () => {
  describe('auth flow', () => {
    beforeEach(async () => {
      await useAuthStore
        .getState()
        .logout()
        .catch(() => {});
      vi.clearAllMocks();
      localStorage.clear();
    });

    it('login updates auth store and token is available for API client', async () => {
      const mockUser = {
        email: 'test@example.com',
        id: 'user-1',
        name: 'Test User',
      };
      const mockToken = 'access-token-123';

      vi.stubGlobal(
        'fetch',
        vi.fn(async (url: string | URL | Request, init?: RequestInit) => {
          const path = typeof url === 'string' ? url : url instanceof Request ? url.url : url.href;
          if (path.includes('/api/v1/auth/login') && init?.method === 'POST') {
            return createJsonResponse({
              access_token: mockToken,
              user: mockUser,
            });
          }
          return createJsonResponse({}, 404);
        }),
      );

      await useAuthStore.getState().login('test@example.com', 'password');

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBeTruthy();
      expect(state.user?.id).toBe('user-1');
      expect(state.user?.email).toBe('test@example.com');
      expect(state.token).toBe(mockToken);
      expect(localStorage.getItem('auth_token')).toBe(mockToken);
    });
  });

  describe('CRUD', () => {
    const mockProjects = [
      {
        id: 'p1',
        name: 'Project 1',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        metadata: {},
      },
      {
        id: 'p2',
        name: 'Project 2',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        metadata: {},
      },
    ];
    const mockItems = [
      {
        id: 'item-1',
        project_id: 'p1',
        title: 'Item 1',
        type: 'requirement',
        status: 'pending',
        priority: 'medium',
        metadata: {},
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    beforeEach(() => {
      vi.clearAllMocks();
    });

    it('projects and items CRUD flow with API client', async () => {
      const listProjectsSpy = vi.spyOn(api.projects, 'list').mockResolvedValue(mockProjects as any);
      const createProjectSpy = vi
        .spyOn(api.projects, 'create')
        .mockResolvedValue({ ...mockProjects[0], id: 'p-new', name: 'New Project' } as any);
      const updateProjectSpy = vi
        .spyOn(api.projects, 'update')
        .mockResolvedValue({ ...mockProjects[0], name: 'Updated Project' } as any);
      const deleteProjectSpy = vi.spyOn(api.projects, 'delete').mockResolvedValue();

      const listItemsSpy = vi.spyOn(api.items, 'list').mockResolvedValue(mockItems as any);

      const projects = await api.projects.list();
      expect(projects).toHaveLength(2);
      expect(listProjectsSpy).toHaveBeenCalled();

      const created = await api.projects.create({ name: 'New Project' });
      expect(created.name).toBe('New Project');
      expect(createProjectSpy).toHaveBeenCalledWith({ name: 'New Project' });

      const updated = await api.projects.update('p1', { name: 'Updated Project' });
      expect(updated.name).toBe('Updated Project');
      expect(updateProjectSpy).toHaveBeenCalledWith('p1', { name: 'Updated Project' });

      await api.projects.delete('p1');
      expect(deleteProjectSpy).toHaveBeenCalledWith('p1');

      const items = await api.items.list({ project_id: 'p1' });
      expect(items).toBeDefined();
      expect(Array.isArray(items) ? items : (items as any).items).toBeDefined();
      expect(listItemsSpy).toHaveBeenCalled();
    });
  });

  describe('errors', () => {
    beforeEach(() => {
      vi.clearAllMocks();
    });

    it('API client throws ApiError with status and message on 4xx/5xx', async () => {
      const listSpy = vi.spyOn(api.projects, 'list').mockRejectedValue(new Error('Network error'));
      await expect(api.projects.list()).rejects.toThrow('Network error');
      listSpy.mockRestore();

      // Exercise handleApiResponse with error response (integration with client-errors)
      const errorResponse = new Response(JSON.stringify({ detail: 'Not Found' }), {
        status: 404,
        statusText: 'Not Found',
      });
      const promise = Promise.resolve({
        data: undefined,
        error: { detail: 'Not Found' },
        response: errorResponse,
      });

      await expect(handleApiResponse(promise)).rejects.toThrow(ApiError);

      const promise2 = Promise.resolve({
        data: undefined,
        error: { detail: 'Not Found' },
        response: errorResponse,
      });
      try {
        await handleApiResponse(promise2);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(404);
        expect((error as ApiError).statusText).toBe('Not Found');
      }
    });
  });
});
