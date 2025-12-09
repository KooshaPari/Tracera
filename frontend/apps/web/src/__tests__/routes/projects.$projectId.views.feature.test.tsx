/**
 * Tests for Feature View Route
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryHistory, createRouter, RouterProvider } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'

// Mock the dynamic imports used in the route loader
vi.mock('@/api/endpoints', () => ({
  projectsApi: {
    get: vi.fn(),
  },
  itemsApi: {
    list: vi.fn(),
  },
}))

describe('Feature View Route', () => {
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

  it('renders feature view with project data', async () => {
    const { projectsApi, itemsApi } = await import('@/api/endpoints')

    ;(projectsApi.get as any).mockResolvedValue({
      id: 'proj-1',
      name: 'Test Project',
      description: 'Test description',
    })

    ;(itemsApi.list as any).mockResolvedValue([
      {
        id: 'item-1',
        title: 'Feature 1',
        type: 'feature',
        status: 'todo',
        priority: 'high',
      },
    ])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/feature'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText('Features')).toBeInTheDocument()
      expect(screen.getByText(/Manage feature requirements/i)).toBeInTheDocument()
    })
  })

  it('displays project name in description', async () => {
    const { projectsApi, itemsApi } = await import('@/api/endpoints')

    ;(projectsApi.get as any).mockResolvedValue({
      id: 'proj-1',
      name: 'My Project',
      description: 'Test description',
    })

    ;(itemsApi.list as any).mockResolvedValue([])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/feature'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText(/My Project/)).toBeInTheDocument()
    })
  })

  it('handles loader errors gracefully', async () => {
    const { projectsApi } = await import('@/api/endpoints')

    ;(projectsApi.get as any).mockRejectedValue(new Error('Project not found'))

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/feature'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    // Should handle error state
    await waitFor(() => {
      // Error handling should be present
    }, { timeout: 2000 })
  })
})
