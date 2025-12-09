/**
 * Tests for Wireframe View Route
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryHistory, createRouter, RouterProvider } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'

vi.mock('@/api/projects', () => ({
  fetchProject: vi.fn(),
}), { virtual: true })

vi.mock('@/api/items', () => ({
  fetchProjectWireframes: vi.fn(),
}), { virtual: true })

describe('Wireframe View Route', () => {
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

  it('renders wireframe view with project data', async () => {
    const { fetchProject } = await import('@/api/projects')
    const { fetchProjectWireframes } = await import('@/api/items')

    ;(fetchProject as any).mockResolvedValue({
      id: 'proj-1',
      name: 'Test Project',
      description: 'Test description',
    })

    ;(fetchProjectWireframes as any).mockResolvedValue([
      {
        id: 'item-1',
        title: 'Homepage Wireframe',
        type: 'wireframe',
        status: 'done',
      },
    ])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/wireframe'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText('Wireframes & UI')).toBeInTheDocument()
      expect(screen.getByText(/UI\/UX designs/i)).toBeInTheDocument()
    })
  })

  it('displays project name in description', async () => {
    const { fetchProject } = await import('@/api/projects')
    const { fetchProjectWireframes } = await import('@/api/items')

    ;(fetchProject as any).mockResolvedValue({
      id: 'proj-1',
      name: 'Design Project',
      description: 'Test description',
    })

    ;(fetchProjectWireframes as any).mockResolvedValue([])

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-1/views/wireframe'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText(/Design Project/)).toBeInTheDocument()
    })
  })
})
