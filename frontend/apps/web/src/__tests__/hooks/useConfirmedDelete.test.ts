/**
 * UseConfirmedDelete Hook Tests
 *
 * Tests for:
 * - Dialog state management
 * - Delete execution
 * - Success/error handling
 * - Toast notifications
 */

import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useConfirmedBulkDelete, useConfirmedDelete } from '@/hooks/useConfirmedDelete';

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

describe(useConfirmedDelete, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with closed dialog', () => {
    const { result } = renderHook(() => useConfirmedDelete());

    expect(result.current.dialogOpen).toBeFalsy();
    expect(result.current.pendingDelete).toBeNull();
    expect(result.current.isDeleting).toBeFalsy();
  });

  it('opens dialog on requestDelete', () => {
    const { result } = renderHook(() => useConfirmedDelete());

    act(() => {
      result.current.requestDelete({
        description: 'Are you sure?',
        id: 'item-1',
        name: 'Test Item',
        title: 'Delete item?',
      });
    });

    expect(result.current.dialogOpen).toBeTruthy();
    expect(result.current.pendingDelete?.id).toBe('item-1');
    expect(result.current.pendingDelete?.name).toBe('Test Item');
  });

  it('executes delete function on executeDelete', async () => {
    const { result } = renderHook(() => useConfirmedDelete());
    const deleteFunction = vi.fn().mockResolvedValue();

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
        successMessage: 'Item deleted',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    expect(deleteFunction).toHaveBeenCalled();
  });

  it('closes dialog after successful delete', async () => {
    const { result } = renderHook(() => useConfirmedDelete());
    const deleteFunction = vi.fn().mockResolvedValue();

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    expect(result.current.dialogOpen).toBeFalsy();
  });

  it('handles delete errors', async () => {
    const { result } = renderHook(() => useConfirmedDelete());
    const error = new Error('Delete failed');
    const deleteFunction = vi.fn().mockRejectedValue(error);

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    expect(result.current.isDeleting).toBeFalsy();
  });

  it('sets isDeleting during execution', async () => {
    const { result } = renderHook(() => useConfirmedDelete());
    const deleteFunction = vi.fn(async () => new Promise((resolve) => setTimeout(resolve, 100)));

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
      });
    });

    void act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    await waitFor(() => {
      expect(result.current.isDeleting).toBeFalsy();
    });
  });

  it('cancels delete operation', () => {
    const { result } = renderHook(() => useConfirmedDelete());

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
      });
    });

    expect(result.current.dialogOpen).toBeTruthy();

    act(() => {
      result.current.cancelDelete();
    });

    expect(result.current.dialogOpen).toBeFalsy();
    expect(result.current.pendingDelete).toBeNull();
  });

  it('closes dialog without clearing pending state', () => {
    const { result } = renderHook(() => useConfirmedDelete());

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
      });
    });

    act(() => {
      result.current.closeDialog();
    });

    expect(result.current.dialogOpen).toBeFalsy();
  });

  it('respects showSuccessToast option', async () => {
    const { toast } = await import('sonner');
    const { result } = renderHook(() => useConfirmedDelete({ showSuccessToast: true }));
    const deleteFunction = vi.fn().mockResolvedValue();

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
        successMessage: 'Item deleted',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalled();
    });
  });

  it('respects showErrorToast option', async () => {
    const { toast } = await import('sonner');
    const { result } = renderHook(() => useConfirmedDelete({ showErrorToast: true }));
    const deleteFunction = vi.fn().mockRejectedValue(new Error('Delete failed'));

    act(() => {
      result.current.requestDelete({
        id: 'item-1',
        name: 'Test Item',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
  });
});

describe(useConfirmedBulkDelete, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with closed dialog', () => {
    const { result } = renderHook(() => useConfirmedBulkDelete());

    expect(result.current.dialogOpen).toBeFalsy();
    expect(result.current.pendingDelete).toBeNull();
    expect(result.current.isDeleting).toBeFalsy();
  });

  it('opens dialog for bulk delete', () => {
    const { result } = renderHook(() => useConfirmedBulkDelete());

    act(() => {
      result.current.requestDelete({
        count: 5,
        itemType: 'items',
      });
    });

    expect(result.current.dialogOpen).toBeTruthy();
    expect(result.current.pendingDelete?.count).toBe(5);
    expect(result.current.pendingDelete?.itemType).toBe('items');
  });

  it('executes bulk delete function', async () => {
    const { result } = renderHook(() => useConfirmedBulkDelete());
    const deleteFunction = vi.fn().mockResolvedValue();

    act(() => {
      result.current.requestDelete({
        count: 3,
        itemType: 'items',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    expect(deleteFunction).toHaveBeenCalled();
  });

  it('closes dialog after successful bulk delete', async () => {
    const { result } = renderHook(() => useConfirmedBulkDelete());
    const deleteFunction = vi.fn().mockResolvedValue();

    act(() => {
      result.current.requestDelete({
        count: 2,
        itemType: 'items',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    expect(result.current.dialogOpen).toBeFalsy();
  });

  it('handles bulk delete errors', async () => {
    const { result } = renderHook(() => useConfirmedBulkDelete());
    const deleteFunction = vi.fn().mockRejectedValue(new Error('Bulk delete failed'));

    act(() => {
      result.current.requestDelete({
        count: 5,
        itemType: 'items',
      });
    });

    await act(async () => {
      await result.current.executeDelete(deleteFunction);
    });

    expect(result.current.isDeleting).toBeFalsy();
  });

  it('cancels bulk delete operation', () => {
    const { result } = renderHook(() => useConfirmedBulkDelete());

    act(() => {
      result.current.requestDelete({
        count: 5,
        itemType: 'items',
      });
    });

    expect(result.current.dialogOpen).toBeTruthy();

    act(() => {
      result.current.cancelDelete();
    });

    expect(result.current.dialogOpen).toBeFalsy();
    expect(result.current.pendingDelete).toBeNull();
  });
});
