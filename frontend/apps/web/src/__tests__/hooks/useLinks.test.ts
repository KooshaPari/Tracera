/**
 * Tests for useLinks hook
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import React from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useCreateLink, useLinks } from '../../hooks/useLinks'

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch as unknown as typeof fetch

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('useLinks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should fetch links', async () => {
    const mockLinks = [
      { id: '1', sourceId: 'item-1', targetId: 'item-2', type: 'depends_on' },
      { id: '2', sourceId: 'item-2', targetId: 'item-3', type: 'implements' },
    ]

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockLinks,
    })

    const { result } = renderHook(() => useLinks(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(result.current.data).toEqual(mockLinks)
    expect(mockFetch).toHaveBeenCalledTimes(1)
  })

  it('should fetch links with source filter', async () => {
    const mockLinks = [{ id: '1', sourceId: 'item-1', targetId: 'item-2', type: 'depends_on' }]

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockLinks,
    })

    const { result } = renderHook(() => useLinks({ sourceId: 'item-1' }), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(result.current.data).toEqual(mockLinks)
    expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('source_id=item-1'))
  })

  it('should fetch links with target filter', async () => {
    const mockLinks = [{ id: '1', sourceId: 'item-1', targetId: 'item-2', type: 'depends_on' }]

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockLinks,
    })

    const { result } = renderHook(() => useLinks({ targetId: 'item-2' }), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('target_id=item-2'))
  })

  it('should handle fetch error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    })

    const { result } = renderHook(() => useLinks(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isError).toBe(true))

    expect(result.current.error).toBeTruthy()
  })
})

describe('useCreateLink', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should create a link', async () => {
    const newLink = {
      sourceId: 'item-1',
      targetId: 'item-2',
      type: 'depends_on' as const,
      projectId: 'proj-1',
    }

    const createdLink = {
      id: '1',
      ...newLink,
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => createdLink,
    })

    const { result } = renderHook(() => useCreateLink(), {
      wrapper: createWrapper(),
    })

    result.current.mutate(newLink)

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(result.current.data).toEqual(createdLink)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/links'),
      expect.objectContaining({
        method: 'POST',
      })
    )
  })

  it('should handle create error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
    })

    const { result } = renderHook(() => useCreateLink(), {
      wrapper: createWrapper(),
    })

    result.current.mutate({
      sourceId: 'item-1',
      targetId: 'item-2',
      type: 'depends_on' as const,
      projectId: 'proj-1',
    })

    await waitFor(() => expect(result.current.isError).toBe(true))
  })
})
