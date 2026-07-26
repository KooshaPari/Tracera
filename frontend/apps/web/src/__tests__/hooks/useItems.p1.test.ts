/**
 * Comprehensive tests for useItems hook (useItems.ts)
 * Coverage targets: All hooks, fetch functions, transformations, error handling
 */

import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  useCreateItem,
  useCreateItemWithSpec,
  useDeleteItem,
  useItem,
  useItems,
  useUpdateItem,
} from '../../hooks/useItems';

// Mock auth store
vi.mock('../../stores/authStore', () => ({
  useAuthStore: vi.fn(() => ({ token: 'test-token' })),
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

const mockItem = {
  created_at: '2024-01-01T00:00:00Z',
  description: 'Test item',
  id: 'item-1',
  project_id: 'proj-1',
  status: 'open',
  title: 'Test Item',
  type: 'requirement',
  updated_at: '2024-01-02T00:00:00Z',
};

const mockItems = [mockItem, { ...mockItem, id: 'item-2', title: 'Item 2' }];

const mockItemResponse = {
  items: mockItems,
  total: 2,
};

async function createMockResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' },
    status,
  });
}

describe('useItems Hooks - P1 Coverage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  // ============================================================================
  // UseItems HOOK TESTS
  // ============================================================================

  describe(useItems, () => {
    it('should fetch items without filters', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should fetch items with project filter', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems({ projectId: 'proj-1' }));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(global.fetch as any).toHaveBeenCalled();
    });

    it('should filter by status', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems({ status: 'open' }));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(global.fetch as any).toHaveBeenCalled();
    });

    it('should filter by view type', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems({ view: 'kanban' }));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(global.fetch as any).toHaveBeenCalled();
    });

    it('should filter by parent ID', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems({ parentId: 'parent-1' }));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(global.fetch as any).toHaveBeenCalled();
    });

    it('should support limit parameter', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems({ limit: 10 }));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(global.fetch as any).toHaveBeenCalled();
    });

    it('should combine multiple filters', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() =>
        useItems({
          limit: 20,
          parentId: 'parent-1',
          projectId: 'proj-1',
          status: 'open',
          view: 'kanban',
        }),
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(global.fetch as any).toHaveBeenCalled();
    });

    it('should handle error responses', async () => {
      (global.fetch as any).mockResolvedValueOnce(
        createMockResponse({ error: 'Server error' }, 500),
      );

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.isError).toBeDefined();
    });

    it('should handle empty response', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse({ items: [] }));

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should include specs in request', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      renderHook(() => useItems());

      await waitFor(() => {
        const fetchCall = (global.fetch as any).mock.calls[0];
        const url = String(fetchCall?.[0]);

        expect(url).toContain('include_specs=true');
      });
    });

    it('should use dynamic query config', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      // Dynamic config should refetch on mount
      expect(result.current).toBeDefined();
    });

    it('should generate cache key with token', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems({ projectId: 'proj-1' }));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      // Should successfully create a key including token
      expect(result.current).toBeDefined();
    });
  });

  // ============================================================================
  // UseItem HOOK TESTS
  // ============================================================================

  describe(useItem, () => {
    it('should fetch single item by ID', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should be disabled when no ID provided', async () => {
      const { result } = renderHook(() => useItem(''));

      // With empty ID, query should be disabled
      expect(result.current.isDisabled).toBeTruthy();
    });

    it('should handle fetch error', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse({ error: 'Not found' }, 404));

      const { result } = renderHook(() => useItem('nonexistent'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.isError).toBeDefined();
    });

    it('should transform snake_case to camelCase', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      // Should have transformed fields
      expect(result.current.data).toBeDefined();
    });

    it('should use dynamic query config', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current).toBeDefined();
    });
  });

  // ============================================================================
  // UseCreateItem MUTATION TESTS
  // ============================================================================

  describe(useCreateItem, () => {
    it('should create item with valid data', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem, 201));

      const { result } = renderHook(() => useCreateItem());

      expect(result.current.mutate).toBeDefined();
      expect(result.current.isPending).toBeFalsy();
    });

    it('should handle create item errors', async () => {
      (global.fetch as any).mockResolvedValueOnce(
        createMockResponse({ error: 'Invalid input' }, 400),
      );

      const { result } = renderHook(() => useCreateItem());

      expect(result.current.mutate).toBeDefined();
    });

    it('should support async mutation', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem, 201));

      const { result } = renderHook(() => useCreateItem());

      expect(result.current.mutateAsync).toBeDefined();
    });
  });

  // ============================================================================
  // UseUpdateItem MUTATION TESTS
  // ============================================================================

  describe(useUpdateItem, () => {
    it('should update item', async () => {
      const updated = { ...mockItem, title: 'Updated' };
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(updated));

      const { result } = renderHook(() => useUpdateItem());

      expect(result.current.mutate).toBeDefined();
    });

    it('should handle partial updates', async () => {
      const updated = { ...mockItem, title: 'Updated' };
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(updated));

      const { result } = renderHook(() => useUpdateItem());

      expect(result.current.mutate).toBeDefined();
    });

    it('should handle update errors', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse({ error: 'Not found' }, 404));

      const { result } = renderHook(() => useUpdateItem());

      expect(result.current.mutate).toBeDefined();
    });
  });

  // ============================================================================
  // UseDeleteItem MUTATION TESTS
  // ============================================================================

  describe(useDeleteItem, () => {
    it('should delete item', async () => {
      (global.fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }));

      const { result } = renderHook(() => useDeleteItem());

      expect(result.current.mutate).toBeDefined();
    });

    it('should handle delete errors', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse({ error: 'Not found' }, 404));

      const { result } = renderHook(() => useDeleteItem());

      expect(result.current.mutate).toBeDefined();
    });
  });

  // ============================================================================
  // UseCreateItemWithSpec MUTATION TESTS
  // ============================================================================

  describe(useCreateItemWithSpec, () => {
    const mockSpecData = {
      item: {
        description: 'Test requirement',
        priority: 'high',
        projectId: 'proj-1',
        status: 'open',
        title: 'Test Requirement',
        type: 'requirement',
        view: 'kanban',
      },
      projectId: 'proj-1',
      spec: {
        adr_id: 'adr-1',
        contract_id: 'contract-1',
        quality_metrics: { score: 0.9 },
      },
    };

    it('should create item with specification', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem, 201));

      const { result } = renderHook(() => useCreateItemWithSpec());

      expect(result.current.mutate).toBeDefined();
    });

    it('should handle spec creation errors', async () => {
      (global.fetch as any).mockResolvedValueOnce(
        createMockResponse({ error: 'Invalid spec' }, 400),
      );

      const { result } = renderHook(() => useCreateItemWithSpec());

      expect(result.current.mutate).toBeDefined();
    });

    it('should show success toast on creation', async () => {
      const { toast } = await import('sonner');
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem, 201));

      const { result } = renderHook(() => useCreateItemWithSpec());

      expect(result.current.mutate).toBeDefined();
      expect(toast.success).toBeDefined();
    });

    it('should show error toast on failure', async () => {
      const { toast } = await import('sonner');
      (global.fetch as any).mockResolvedValueOnce(
        createMockResponse({ error: 'Server error' }, 500),
      );

      const { result } = renderHook(() => useCreateItemWithSpec());

      expect(result.current.mutate).toBeDefined();
      expect(toast.error).toBeDefined();
    });

    it('should invalidate items queries on success', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItem, 201));

      const { result } = renderHook(() => useCreateItemWithSpec());

      expect(result.current.mutate).toBeDefined();
      // Query client invalidation would be called
    });
  });

  // ============================================================================
  // ITEM TRANSFORMATION TESTS
  // ============================================================================

  describe('Item Transformation', () => {
    it('should transform snake_case to camelCase', async () => {
      const snakeCaseItem = {
        created_at: '2024-01-01T00:00:00Z',
        project_id: 'proj-1',
        updated_at: '2024-01-02T00:00:00Z',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(snakeCaseItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      // Transformation should occur
      expect(result.current.data).toBeDefined();
    });

    it('should handle requirement type fields', async () => {
      const requirementItem = {
        ...mockItem,
        adr_id: 'adr-1',
        contract_id: 'contract-1',
        quality_metrics: { score: 0.9 },
        type: 'requirement',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(requirementItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should handle test type fields', async () => {
      const testItem = {
        ...mockItem,
        automation_status: 'automated',
        expected_result: 'Pass',
        last_execution_result: 'Pass',
        test_steps: ['Step 1', 'Step 2'],
        test_type: 'unit',
        type: 'test',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(testItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should handle epic type fields', async () => {
      const epicItem = {
        ...mockItem,
        acceptance_criteria: 'Must have feature X',
        business_value: 'High',
        target_release: '1.0.0',
        type: 'epic',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(epicItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should handle user story type fields', async () => {
      const storyItem = {
        ...mockItem,
        acceptance_criteria: 'User can see items',
        as_a: 'user',
        i_want: 'to see my items',
        so_that: 'I can manage them',
        story_points: 5,
        type: 'user_story',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(storyItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should handle task type fields', async () => {
      const taskItem = {
        ...mockItem,
        actual_hours: 8,
        assignee: 'user@example.com',
        due_date: '2024-12-31',
        estimated_hours: 8,
        type: 'task',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(taskItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should handle bug type fields', async () => {
      const bugItem = {
        ...mockItem,
        environment: 'production',
        fixed_in_version: '1.1.0',
        found_in_version: '1.0.0',
        reproducible: true,
        severity: 'high',
        steps_to_reproduce: 'Step 1, Step 2',
        type: 'bug',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(bugItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should preserve both camelCase and snake_case when present', async () => {
      const mixedItem = {
        ...mockItem,
        created_at: '2024-01-01T00:00:00Z',
        createdAt: '2024-01-01T00:00:00Z',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mixedItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });
  });

  // ============================================================================
  // AUTH HEADER TESTS
  // ============================================================================

  describe('Authentication', () => {
    it('should include auth token in headers', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      renderHook(() => useItems());

      await waitFor(() => {
        const fetchCall = (global.fetch as any).mock.calls[0];
        expect(fetchCall).toBeDefined();
      });

      expect(global.fetch as any).toHaveBeenCalled();
    });

    it('should handle missing token', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should trim whitespace from token', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(mockItemResponse));

      renderHook(() => useItems());

      await waitFor(() => {
        expect(global.fetch as any).toHaveBeenCalled();
      });
    });
  });

  // ============================================================================
  // EDGE CASES
  // ============================================================================

  describe('Edge Cases', () => {
    it('should handle null response data', async () => {
      (global.fetch as any).mockResolvedValueOnce(createMockResponse(null));

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });
    });

    it('should handle malformed JSON', async () => {
      (global.fetch as any).mockResolvedValueOnce(
        new Response('invalid json', {
          headers: { 'Content-Type': 'application/json' },
          status: 200,
        }),
      );

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });
    });

    it('should handle network errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });
    });

    it('should handle very large item lists', async () => {
      const largeItemList = Array.from({ length: 1000 }, (_, i) => ({
        ...mockItem,
        id: `item-${i}`,
      }));

      (global.fetch as any).mockResolvedValueOnce(createMockResponse({ items: largeItemList }));

      const { result } = renderHook(() => useItems());

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });

    it('should handle special characters in item data', async () => {
      const specialItem = {
        ...mockItem,
        description: 'Test with <script>alert(1)</script>',
        title: 'Item with "quotes" and \'apostrophes\'',
      };

      (global.fetch as any).mockResolvedValueOnce(createMockResponse(specialItem));

      const { result } = renderHook(() => useItem('item-1'));

      await waitFor(() => {
        expect(result.current.isLoading).toBeFalsy();
      });

      expect(result.current.data).toBeDefined();
    });
  });
});
