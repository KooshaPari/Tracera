/**
 * Tests for API View Route
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

describe('API View Route', () => {
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

  it('renders API view with project data', async () => {
    const { projectsApi, itemsApi } = await import('@/api/endpoints')

    ;(projectsApi.get as any).mockResolvedValue({
      id: 'proj-1',
      name: 'Test Project',
      description: 'Test description',
    })

    ;(itemsApi.list as any).mockResolvedValue([
      {
        id: 'item-1',
        title: 'GET /api/users',
        type: 'api',
        status: 'done',
        method: 'GET',
      },
    ])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/api'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText('API Endpoints')).toBeInTheDocument()
      expect(screen.getByText(/REST API contracts/i)).toBeInTheDocument()
    })
  })

  it('displays project name in description', async () => {
    const { projectsApi, itemsApi } = await import('@/api/endpoints')

    ;(projectsApi.get as any).mockResolvedValue({
      id: 'proj-1',
      name: 'API Project',
      description: 'Test description',
    })

    ;(itemsApi.list as any).mockResolvedValue([])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/api'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText(/API Project/)).toBeInTheDocument()
    })
  })
})
