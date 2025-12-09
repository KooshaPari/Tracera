/**
 * Comprehensive Project Detail Page Tests
 * Tests: Project detail rendering, tabs, items/links management, views
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryHistory, createRouter, RouterProvider } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'

vi.mock('@/api/projects', () => ({
  fetchProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
}))

vi.mock('@/api/items', () => ({
  fetchProjectItems: vi.fn(),
  createItem: vi.fn(),
  updateItem: vi.fn(),
  deleteItem: vi.fn(),
}))

vi.mock('@/api/links', () => ({
  fetchProjectLinks: vi.fn(),
  createLink: vi.fn(),
  deleteLink: vi.fn(),
}))

describe('Project Detail Page', () => {
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

    history = createMemoryHistory({
      initialEntries: ['/projects/proj-123'],
    })

    router = createRouter({
      routeTree,
      history,
      context: { queryClient },
    })

    vi.clearAllMocks()
  })

  afterEach(() => {
    queryClient.clear()
  })

  describe('Page Rendering', () => {
    it('renders project detail page with header', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'E-Commerce Platform',
        description: 'Complete online shopping solution',
        status: 'active',
        created_at: '2024-01-15',
        updated_at: '2024-02-20',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /E-Commerce Platform/i })).toBeInTheDocument()
      })

      expect(screen.getByText(/Complete online shopping solution/i)).toBeInTheDocument()
      expect(screen.getByText(/active/i)).toBeInTheDocument()
    })

    it('displays project metadata', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-02-20T14:30:00Z',
        owner: 'John Doe',
        tags: ['critical', 'backend'],
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/John Doe/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/critical/i)).toBeInTheDocument()
      expect(screen.getByText(/backend/i)).toBeInTheDocument()
      expect(screen.getByText(/Created:/i)).toBeInTheDocument()
      expect(screen.getByText(/Last Updated:/i)).toBeInTheDocument()
    })

    it('renders tab navigation', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument()
      })

      expect(screen.getByRole('tab', { name: /items/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /links/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /graph/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /reports/i })).toBeInTheDocument()
    })

    it('displays project statistics', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
        stats: {
          totalItems: 156,
          totalLinks: 342,
          completionRate: 67.5,
          coverage: 89.2,
        },
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/156/)).toBeInTheDocument()
      })

      expect(screen.getByText(/342/)).toBeInTheDocument()
      expect(screen.getByText(/67.5%/)).toBeInTheDocument()
      expect(screen.getByText(/89.2%/)).toBeInTheDocument()
    })
  })

  describe('Loading States', () => {
    it('shows loading skeleton while fetching project', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ id: 'proj-123', name: 'Test' }), 100)
          )
      )
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      expect(screen.getAllByRole('status', { name: /loading/i }).length).toBeGreaterThan(0)

      await waitFor(() => {
        expect(screen.queryByRole('status', { name: /loading/i })).not.toBeInTheDocument()
      })
    })

    it('shows partial loading for different sections', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ data: [], total: 0 }), 100))
      )
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/Test Project/i)).toBeInTheDocument()
      })

      const itemsSection = screen.getByTestId('items-section')
      expect(within(itemsSection).getByRole('status')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('displays 404 error for non-existent project', async () => {
      const { fetchProject } = await import('@/api/projects')

      vi.mocked(fetchProject).mockRejectedValue(new Error('Project not found'))

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/Project Not Found/i)).toBeInTheDocument()
      })

      expect(screen.getByRole('button', { name: /Go Back/i })).toBeInTheDocument()
    })

    it('shows error when items fail to load', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockRejectedValue(new Error('Failed to load items'))
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/Test Project/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Failed to load items/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
    })

    it('handles unauthorized access gracefully', async () => {
      const { fetchProject } = await import('@/api/projects')

      vi.mocked(fetchProject).mockRejectedValue(new Error('Unauthorized'))

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/Access Denied/i)).toBeInTheDocument()
      })

      expect(
        screen.getByText(/You don't have permission to view this project/i)
      ).toBeInTheDocument()
    })
  })

  describe('Tab Navigation', () => {
    it('switches to items tab', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({
        data: [
          { id: 'item-1', title: 'Feature A', type: 'feature' },
          { id: 'item-2', title: 'Bug B', type: 'bug' },
        ],
        total: 2,
      })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /items/i })).toBeInTheDocument()
      })

      const itemsTab = screen.getByRole('tab', { name: /items/i })
      await userEvent.click(itemsTab)

      await waitFor(() => {
        expect(screen.getByText(/Feature A/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Bug B/i)).toBeInTheDocument()
    })

    it('switches to links tab', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({
        data: [
          { id: 'link-1', sourceId: 'item-1', targetId: 'item-2', type: 'depends' },
          { id: 'link-2', sourceId: 'item-2', targetId: 'item-3', type: 'blocks' },
        ],
        total: 2,
      })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /links/i })).toBeInTheDocument()
      })

      const linksTab = screen.getByRole('tab', { name: /links/i })
      await userEvent.click(linksTab)

      await waitFor(() => {
        expect(screen.getByText(/depends/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/blocks/i)).toBeInTheDocument()
    })

    it('maintains tab state in URL', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /items/i })).toBeInTheDocument()
      })

      const itemsTab = screen.getByRole('tab', { name: /items/i })
      await userEvent.click(itemsTab)

      await waitFor(() => {
        expect(history.location.search).toContain('tab=items')
      })
    })
  })

  describe('Items Management', () => {
    it('displays items list', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({
        data: [
          {
            id: 'item-1',
            title: 'User Authentication',
            type: 'feature',
            status: 'in-progress',
            priority: 'high',
          },
          {
            id: 'item-2',
            title: 'Login Bug Fix',
            type: 'bug',
            status: 'done',
            priority: 'critical',
          },
        ],
        total: 2,
      })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/Test Project/i)).toBeInTheDocument()
      })

      // Navigate to items tab
      await userEvent.click(screen.getByRole('tab', { name: /items/i }))

      await waitFor(() => {
        expect(screen.getByText(/User Authentication/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Login Bug Fix/i)).toBeInTheDocument()
      expect(screen.getByText(/high/i)).toBeInTheDocument()
      expect(screen.getByText(/critical/i)).toBeInTheDocument()
    })

    it('creates new item', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems, createItem } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(createItem).mockResolvedValue({
        id: 'new-item',
        title: 'New Feature',
        type: 'feature',
      })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /items/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /items/i }))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /create item/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('button', { name: /create item/i }))

      await waitFor(() => {
        expect(screen.getByRole('dialog', { name: /create item/i })).toBeInTheDocument()
      })

      await userEvent.type(screen.getByLabelText(/title/i), 'New Feature')
      await userEvent.click(screen.getByLabelText(/type/i))
      await userEvent.click(screen.getByRole('option', { name: /feature/i }))

      await userEvent.click(screen.getByRole('button', { name: /create$/i }))

      await waitFor(() => {
        expect(screen.getByText(/item created successfully/i)).toBeInTheDocument()
      })
    })

    it('filters items by type', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({
        data: [
          { id: 'item-1', title: 'Feature 1', type: 'feature' },
          { id: 'item-2', title: 'Bug 1', type: 'bug' },
          { id: 'item-3', title: 'Feature 2', type: 'feature' },
        ],
        total: 3,
      })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /items/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /items/i }))

      await waitFor(() => {
        expect(screen.getByText(/Feature 1/i)).toBeInTheDocument()
      })

      const typeFilter = screen.getByRole('combobox', { name: /filter by type/i })
      await userEvent.click(typeFilter)
      await userEvent.click(screen.getByRole('option', { name: /^feature$/i }))

      await waitFor(() => {
        expect(screen.getByText(/Feature 1/i)).toBeInTheDocument()
        expect(screen.getByText(/Feature 2/i)).toBeInTheDocument()
        expect(screen.queryByText(/Bug 1/i)).not.toBeInTheDocument()
      })
    })

    it('sorts items by priority', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({
        data: [
          { id: 'item-1', title: 'Low Priority', priority: 'low' },
          { id: 'item-2', title: 'Critical Priority', priority: 'critical' },
          { id: 'item-3', title: 'High Priority', priority: 'high' },
        ],
        total: 3,
      })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /items/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /items/i }))

      await waitFor(() => {
        expect(screen.getByText(/Low Priority/i)).toBeInTheDocument()
      })

      const sortSelect = screen.getByRole('combobox', { name: /sort by/i })
      await userEvent.click(sortSelect)
      await userEvent.click(screen.getByRole('option', { name: /priority/i }))

      await waitFor(() => {
        const items = screen.getAllByTestId(/item-card/)
        expect(items[0]).toHaveTextContent(/Critical Priority/i)
        expect(items[1]).toHaveTextContent(/High Priority/i)
        expect(items[2]).toHaveTextContent(/Low Priority/i)
      })
    })

    it('deletes item with confirmation', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems, deleteItem } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({
        data: [{ id: 'item-1', title: 'Item to Delete' }],
        total: 1,
      })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(deleteItem).mockResolvedValue({ success: true })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /items/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /items/i }))

      await waitFor(() => {
        expect(screen.getByText(/Item to Delete/i)).toBeInTheDocument()
      })

      const deleteButton = screen.getByRole('button', { name: /delete item-1/i })
      await userEvent.click(deleteButton)

      await waitFor(() => {
        expect(screen.getByText(/confirm delete/i)).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('button', { name: /confirm/i }))

      await waitFor(() => {
        expect(screen.getByText(/item deleted/i)).toBeInTheDocument()
      })
    })
  })

  describe('Links Management', () => {
    it('displays links with source and target', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({
        data: [
          { id: 'item-1', title: 'Feature A' },
          { id: 'item-2', title: 'Feature B' },
        ],
        total: 2,
      })
      vi.mocked(fetchProjectLinks).mockResolvedValue({
        data: [
          {
            id: 'link-1',
            sourceId: 'item-1',
            targetId: 'item-2',
            type: 'depends',
            sourceTitle: 'Feature A',
            targetTitle: 'Feature B',
          },
        ],
        total: 1,
      })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /links/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /links/i }))

      await waitFor(() => {
        expect(screen.getByText(/Feature A/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Feature B/i)).toBeInTheDocument()
      expect(screen.getByText(/depends/i)).toBeInTheDocument()
    })

    it('creates new link between items', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks, createLink } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({
        data: [
          { id: 'item-1', title: 'Item 1' },
          { id: 'item-2', title: 'Item 2' },
        ],
        total: 2,
      })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(createLink).mockResolvedValue({
        id: 'new-link',
        sourceId: 'item-1',
        targetId: 'item-2',
        type: 'blocks',
      })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /links/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /links/i }))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /create link/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('button', { name: /create link/i }))

      await waitFor(() => {
        expect(screen.getByRole('dialog', { name: /create link/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByLabelText(/source item/i))
      await userEvent.click(screen.getByRole('option', { name: /Item 1/i }))

      await userEvent.click(screen.getByLabelText(/target item/i))
      await userEvent.click(screen.getByRole('option', { name: /Item 2/i }))

      await userEvent.click(screen.getByLabelText(/link type/i))
      await userEvent.click(screen.getByRole('option', { name: /blocks/i }))

      await userEvent.click(screen.getByRole('button', { name: /create$/i }))

      await waitFor(() => {
        expect(screen.getByText(/link created successfully/i)).toBeInTheDocument()
      })
    })

    it('filters links by type', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({
        data: [
          { id: 'link-1', type: 'depends', sourceId: '1', targetId: '2' },
          { id: 'link-2', type: 'blocks', sourceId: '2', targetId: '3' },
          { id: 'link-3', type: 'depends', sourceId: '3', targetId: '4' },
        ],
        total: 3,
      })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /links/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /links/i }))

      await waitFor(() => {
        expect(screen.getAllByText(/depends/i)).toHaveLength(2)
      })

      const typeFilter = screen.getByRole('combobox', { name: /filter by type/i })
      await userEvent.click(typeFilter)
      await userEvent.click(screen.getByRole('option', { name: /^depends$/i }))

      await waitFor(() => {
        expect(screen.getAllByText(/depends/i)).toHaveLength(2)
        expect(screen.queryByText(/blocks/i)).not.toBeInTheDocument()
      })
    })

    it('deletes link', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks, deleteLink } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({
        data: [{ id: 'link-1', type: 'depends', sourceId: '1', targetId: '2' }],
        total: 1,
      })
      vi.mocked(deleteLink).mockResolvedValue({ success: true })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /links/i })).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('tab', { name: /links/i }))

      await waitFor(() => {
        expect(screen.getByText(/depends/i)).toBeInTheDocument()
      })

      const deleteButton = screen.getByRole('button', { name: /delete link-1/i })
      await userEvent.click(deleteButton)

      await waitFor(() => {
        expect(screen.getByText(/link deleted/i)).toBeInTheDocument()
      })
    })
  })

  describe('Project Actions', () => {
    it('edits project details', async () => {
      const { fetchProject, updateProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Old Name',
        description: 'Old description',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(updateProject).mockResolvedValue({
        id: 'proj-123',
        name: 'New Name',
        description: 'New description',
      })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/Old Name/i)).toBeInTheDocument()
      })

      const editButton = screen.getByRole('button', { name: /edit project/i })
      await userEvent.click(editButton)

      await waitFor(() => {
        expect(screen.getByRole('dialog', { name: /edit project/i })).toBeInTheDocument()
      })

      const nameInput = screen.getByLabelText(/project name/i)
      await userEvent.clear(nameInput)
      await userEvent.type(nameInput, 'New Name')

      const descInput = screen.getByLabelText(/description/i)
      await userEvent.clear(descInput)
      await userEvent.type(descInput, 'New description')

      await userEvent.click(screen.getByRole('button', { name: /save/i }))

      await waitFor(() => {
        expect(screen.getByText(/New Name/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/New description/i)).toBeInTheDocument()
    })

    it('archives project', async () => {
      const { fetchProject, updateProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
        status: 'active',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(updateProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
        status: 'archived',
      })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/active/i)).toBeInTheDocument()
      })

      const archiveButton = screen.getByRole('button', { name: /archive/i })
      await userEvent.click(archiveButton)

      await waitFor(() => {
        expect(screen.getByText(/confirm archive/i)).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('button', { name: /confirm/i }))

      await waitFor(() => {
        expect(screen.getByText(/archived/i)).toBeInTheDocument()
      })
    })

    it('deletes project', async () => {
      const { fetchProject, deleteProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(deleteProject).mockResolvedValue({ success: true })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByText(/Test Project/i)).toBeInTheDocument()
      })

      const deleteButton = screen.getByRole('button', { name: /delete project/i })
      await userEvent.click(deleteButton)

      await waitFor(() => {
        expect(screen.getByText(/permanently delete/i)).toBeInTheDocument()
      })

      await userEvent.click(screen.getByRole('button', { name: /confirm delete/i }))

      await waitFor(() => {
        expect(history.location.pathname).toBe('/projects')
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('navigation', { name: /tabs/i })).toBeInTheDocument()
      })

      expect(screen.getByRole('button', { name: /edit project/i })).toHaveAttribute('aria-label')
    })

    it('supports keyboard navigation', async () => {
      const { fetchProject } = await import('@/api/projects')
      const { fetchProjectItems } = await import('@/api/items')
      const { fetchProjectLinks } = await import('@/api/links')

      vi.mocked(fetchProject).mockResolvedValue({
        id: 'proj-123',
        name: 'Test Project',
      })
      vi.mocked(fetchProjectItems).mockResolvedValue({ data: [], total: 0 })
      vi.mocked(fetchProjectLinks).mockResolvedValue({ data: [], total: 0 })

      render(<RouterProvider router={router} />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument()
      })

      await userEvent.tab()
      expect(screen.getByRole('tab', { name: /overview/i })).toHaveFocus()

      await userEvent.keyboard('{ArrowRight}')
      expect(screen.getByRole('tab', { name: /items/i })).toHaveFocus()
    })
  })
})
