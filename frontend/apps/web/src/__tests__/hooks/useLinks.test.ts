/**
 * Tests for useLinks hook
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useCreateLink, useLinks } from '../../hooks/useLinks';

// Mock fetch at module level
const mockFetch = vi.fn();
globalThis.fetch = mockFetch as unknown as typeof fetch;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      mutations: { retry: false },
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe(useLinks, () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('should fetch links', async () => {
    const mockLinksArray = [
      { id: '1', sourceId: 'item-1', targetId: 'item-2', type: 'depends_on' },
      { id: '2', sourceId: 'item-2', targetId: 'item-3', type: 'implements' },
    ];

    const mockResponse = {
      links: mockLinksArray,
      total: mockLinksArray.length,
    };

    mockFetch.mockResolvedValueOnce({
      json: async () => mockResponse,
      ok: true,
    });

    const { result } = renderHook(() => useLinks(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBeTruthy();
    });

    expect(result.current.data).toEqual(mockResponse);
    expect(mockFetch).toHaveBeenCalledOnce();
  });

  it('should fetch links with source filter', async () => {
    const mockLinksArray = [
      { id: '1', sourceId: 'item-1', targetId: 'item-2', type: 'depends_on' },
    ];

    const mockResponse = {
      links: mockLinksArray,
      total: mockLinksArray.length,
    };

    mockFetch.mockResolvedValueOnce({
      json: async () => mockResponse,
      ok: true,
    });

    const { result } = renderHook(() => useLinks({ sourceId: 'item-1' }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBeTruthy();
    });

    expect(result.current.data).toEqual(mockResponse);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('source_id=item-1'),
      expect.any(Object),
    );
  });

  it('should fetch links with target filter', async () => {
    const mockLinksArray = [
      { id: '1', sourceId: 'item-1', targetId: 'item-2', type: 'depends_on' },
    ];

    const mockResponse = {
      links: mockLinksArray,
      total: mockLinksArray.length,
    };

    mockFetch.mockResolvedValueOnce({
      json: async () => mockResponse,
      ok: true,
    });

    const { result } = renderHook(() => useLinks({ targetId: 'item-2' }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBeTruthy();
    });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('target_id=item-2'),
      expect.any(Object),
    );
  });

  it('should handle fetch error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useLinks(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBeTruthy();
    });

    expect(result.current.error).toBeTruthy();
  });
});

describe(useCreateLink, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should create a link', async () => {
    const newLink = {
      projectId: 'proj-1',
      sourceId: 'item-1',
      targetId: 'item-2',
      type: 'depends_on' as const,
    };

    const createdLink = {
      id: '1',
      ...newLink,
    };

    mockFetch.mockResolvedValueOnce({
      json: async () => createdLink,
      ok: true,
    });

    const { result } = renderHook(() => useCreateLink(), {
      wrapper: createWrapper(),
    });

    result.current.mutate(newLink);

    await waitFor(() => {
      expect(result.current.isSuccess).toBeTruthy();
    });

    expect(result.current.data).toEqual(createdLink);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/links'),
      expect.objectContaining({
        method: 'POST',
      }),
    );
  });

  it('should handle create error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
    });

    const { result } = renderHook(() => useCreateLink(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      projectId: 'proj-1',
      sourceId: 'item-1',
      targetId: 'item-2',
      type: 'depends_on' as const,
    });

    await waitFor(() => {
      expect(result.current.isError).toBeTruthy();
    });
  });
});
