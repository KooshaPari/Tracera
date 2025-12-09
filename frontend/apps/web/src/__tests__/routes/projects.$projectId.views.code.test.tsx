/**
 * Tests for Code View Route
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryHistory, createRouter, RouterProvider } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'

vi.mock('@/api/endpoints', () => ({
  projectsApi: {
    get: vi.fn(),
  },
  itemsApi: {
    list: vi.fn(),
  },
}))

describe('Code View Route', () => {
  let queryClient: QueryClient
  let router: any
  let history: any

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, gcTime: 0 },
        mutations: { retry: false },
      },
    })

    vi.clearAllMocks()
  })

  it('renders code view with project data', async () => {
    const { projectsApi, itemsApi } = await import('@/api/endpoints')

    ;(projectsApi.get as any).mockResolvedValue({
      id: 'proj-1',
      name: 'Test Project',
      description: 'Test description',
    })

    ;(itemsApi.list as any).mockResolvedValue([
      {
        id: 'item-1',
        title: 'Code Implementation 1',
        type: 'code',
        status: 'done',
      },
    ])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/code'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText('Code Implementation')).toBeInTheDocument()
      expect(screen.getByText(/Source code implementations/i)).toBeInTheDocument()
    })
  })

  it('displays project name in description', async () => {
    const { projectsApi, itemsApi } = await import('@/api/endpoints')

    ;(projectsApi.get as any).mockResolvedValue({
      id: 'proj-1',
      name: 'Codebase Project',
      description: 'Test description',
    })

    ;(itemsApi.list as any).mockResolvedValue([])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/code'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText(/Codebase Project/)).toBeInTheDocument()
    })
  })
})
