/**
 * Comprehensive Projects List Page Tests
 * Tests: Project listing, filtering, sorting, pagination, search
 */

import { QueryClient } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory, createRouter } from '@tanstack/react-router';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { routeTree } from '@/routeTree.gen';

vi.mock('@/api/projects', () => ({
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  fetchProjects: vi.fn(),
  updateProject: vi.fn(),
}));

describe('Projects List Page', () => {
  let queryClient: QueryClient;
  let router: any;
  let history: any;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { gcTime: 0, retry: false },
      },
    });

    history = createMemoryHistory({
      initialEntries: ['/projects'],
    });

    router = createRouter({
      context: { queryClient },
      history,
      routeTree,
    });

    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe('Page Rendering', () => {
    it('renders projects list page with header', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          {
            description: 'First project',
            id: '1',
            name: 'Project Alpha',
            status: 'active',
          },
          {
            description: 'Second project',
            id: '2',
            name: 'Project Beta',
            status: 'active',
          },
        ],
        page: 1,
        pageSize: 50,
        total: 2,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /projects/i })).toBeInTheDocument();
      });

      expect(screen.getByText(/Project Alpha/i)).toBeInTheDocument();
      expect(screen.getByText(/Project Beta/i)).toBeInTheDocument();
    });

    it('displays project cards with correct information', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          {
            created_at: '2024-01-15T10:00:00Z',
            description: 'Online shopping system',
            id: 'proj-1',
            itemCount: 45,
            linkCount: 120,
            name: 'E-Commerce Platform',
            status: 'active',
            updated_at: '2024-02-20T14:30:00Z',
          },
        ],
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/E-Commerce Platform/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Online shopping system/i)).toBeInTheDocument();
      expect(screen.getByText(/45/)).toBeInTheDocument(); // Item count
      expect(screen.getByText(/120/)).toBeInTheDocument(); // Link count
      expect(screen.getByText(/active/i)).toBeInTheDocument();
    });

    it('renders grid view by default', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Project 1' },
          { id: '2', name: 'Project 2' },
          { id: '3', name: 'Project 3' },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        const grid = screen.getByTestId('projects-grid');
        expect(grid).toHaveClass('grid');
      });
    });

    it('switches to list view when toggled', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: '1', name: 'Project 1' }],
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByTestId('projects-grid')).toBeInTheDocument();
      });

      const listViewButton = screen.getByRole('button', { name: /list view/i });
      await userEvent.click(listViewButton);

      await waitFor(() => {
        expect(screen.getByTestId('projects-list')).toBeInTheDocument();
      });
    });

    it('displays create project button', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /create project/i })).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading skeleton while fetching projects', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockImplementation(
        async () =>
          new Promise((resolve) =>
            setTimeout(() => {
              resolve({ data: [], total: 0 });
            }, 100),
          ),
      );

      render(<RouterProvider router={router} />);

      expect(screen.getAllByRole('status', { name: /loading/i }).length).toBeGreaterThan(0);

      await waitFor(() => {
        expect(screen.queryByRole('status', { name: /loading/i })).not.toBeInTheDocument();
      });
    });

    it('shows loading state when refetching', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: '1', name: 'Project 1' }],
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
      });

      vi.mocked(fetchProjects).mockImplementation(
        async () =>
          new Promise((resolve) =>
            setTimeout(() => {
              resolve({
                data: [{ id: '1', name: 'Project 1 Updated' }],
                total: 1,
              });
            }, 50),
          ),
      );

      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      await userEvent.click(refreshButton);

      expect(screen.getByTestId('refetching-indicator')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText(/Project 1 Updated/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message when fetch fails', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockRejectedValue(new Error('Network error'));

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });

      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('shows retry button that refetches data', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects)
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValueOnce({
          data: [{ id: '1', name: 'Recovered Project' }],
          total: 1,
        });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/failed/i)).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /retry/i });
      await userEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText(/Recovered Project/i)).toBeInTheDocument();
      });
    });

    it('handles partial data load gracefully', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: '1', name: 'Project 1' }],
        error: 'Some items could not be loaded',
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/some items could not be loaded/i)).toBeInTheDocument();
    });
  });

  describe('Filtering', () => {
    it('filters projects by status', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Active Project', status: 'active' },
          { id: '2', name: 'Archived Project', status: 'archived' },
          { id: '3', name: 'Draft Project', status: 'draft' },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Active Project/i)).toBeInTheDocument();
      });

      const statusFilter = screen.getByRole('combobox', {
        name: /filter by status/i,
      });
      await userEvent.click(statusFilter);
      await userEvent.click(screen.getByRole('option', { name: /^active$/i }));

      await waitFor(() => {
        expect(screen.getByText(/Active Project/i)).toBeInTheDocument();
        expect(screen.queryByText(/Archived Project/i)).not.toBeInTheDocument();
        expect(screen.queryByText(/Draft Project/i)).not.toBeInTheDocument();
      });
    });

    it('filters projects by date range', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { created_at: '2023-01-01', id: '1', name: 'Old Project' },
          { created_at: '2024-06-01', id: '2', name: 'New Project' },
        ],
        total: 2,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Old Project/i)).toBeInTheDocument();
      });

      const dateFilter = screen.getByRole('button', {
        name: /filter by date/i,
      });
      await userEvent.click(dateFilter);

      const startDate = screen.getByLabelText(/start date/i);
      await userEvent.type(startDate, '2024-01-01');

      await waitFor(() => {
        expect(screen.getByText(/New Project/i)).toBeInTheDocument();
        expect(screen.queryByText(/Old Project/i)).not.toBeInTheDocument();
      });
    });

    it('combines multiple filters', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          {
            created_at: '2024-06-01',
            id: '1',
            name: 'Active New',
            status: 'active',
          },
          {
            created_at: '2023-01-01',
            id: '2',
            name: 'Active Old',
            status: 'active',
          },
          {
            created_at: '2024-06-01',
            id: '3',
            name: 'Archived New',
            status: 'archived',
          },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Active New/i)).toBeInTheDocument();
      });

      // Apply status filter
      const statusFilter = screen.getByRole('combobox', {
        name: /filter by status/i,
      });
      await userEvent.click(statusFilter);
      await userEvent.click(screen.getByRole('option', { name: /^active$/i }));

      // Apply date filter
      const dateFilter = screen.getByRole('button', {
        name: /filter by date/i,
      });
      await userEvent.click(dateFilter);
      const startDate = screen.getByLabelText(/start date/i);
      await userEvent.type(startDate, '2024-01-01');

      await waitFor(() => {
        expect(screen.getByText(/Active New/i)).toBeInTheDocument();
        expect(screen.queryByText(/Active Old/i)).not.toBeInTheDocument();
        expect(screen.queryByText(/Archived New/i)).not.toBeInTheDocument();
      });
    });

    it('clears all filters when clear button clicked', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Active Project', status: 'active' },
          { id: '2', name: 'Archived Project', status: 'archived' },
        ],
        total: 2,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Active Project/i)).toBeInTheDocument();
      });

      // Apply filter
      const statusFilter = screen.getByRole('combobox', {
        name: /filter by status/i,
      });
      await userEvent.click(statusFilter);
      await userEvent.click(screen.getByRole('option', { name: /^active$/i }));

      await waitFor(() => {
        expect(screen.queryByText(/Archived Project/i)).not.toBeInTheDocument();
      });

      // Clear filters
      const clearButton = screen.getByRole('button', {
        name: /clear filters/i,
      });
      await userEvent.click(clearButton);

      await waitFor(() => {
        expect(screen.getByText(/Active Project/i)).toBeInTheDocument();
        expect(screen.getByText(/Archived Project/i)).toBeInTheDocument();
      });
    });
  });

  describe('Sorting', () => {
    it('sorts projects by name ascending', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Zebra Project' },
          { id: '2', name: 'Alpha Project' },
          { id: '3', name: 'Beta Project' },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Zebra Project/i)).toBeInTheDocument();
      });

      const sortSelect = screen.getByRole('combobox', { name: /sort by/i });
      await userEvent.click(sortSelect);
      await userEvent.click(screen.getByRole('option', { name: /name \(a-z\)/i }));

      await waitFor(() => {
        const projects = screen.getAllByTestId(/project-card/);
        expect(projects[0]).toHaveTextContent(/Alpha Project/i);
        expect(projects[1]).toHaveTextContent(/Beta Project/i);
        expect(projects[2]).toHaveTextContent(/Zebra Project/i);
      });
    });

    it('sorts projects by date newest first', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { created_at: '2024-01-01', id: '1', name: 'Oldest' },
          { created_at: '2024-03-01', id: '2', name: 'Newest' },
          { created_at: '2024-02-01', id: '3', name: 'Middle' },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Oldest/i)).toBeInTheDocument();
      });

      const sortSelect = screen.getByRole('combobox', { name: /sort by/i });
      await userEvent.click(sortSelect);
      await userEvent.click(screen.getByRole('option', { name: /newest first/i }));

      await waitFor(() => {
        const projects = screen.getAllByTestId(/project-card/);
        expect(projects[0]).toHaveTextContent(/Newest/i);
        expect(projects[1]).toHaveTextContent(/Middle/i);
        expect(projects[2]).toHaveTextContent(/Oldest/i);
      });
    });

    it('sorts by item count', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', itemCount: 10, name: 'Small' },
          { id: '2', itemCount: 100, name: 'Large' },
          { id: '3', itemCount: 50, name: 'Medium' },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Small/i)).toBeInTheDocument();
      });

      const sortSelect = screen.getByRole('combobox', { name: /sort by/i });
      await userEvent.click(sortSelect);
      await userEvent.click(screen.getByRole('option', { name: /most items/i }));

      await waitFor(() => {
        const projects = screen.getAllByTestId(/project-card/);
        expect(projects[0]).toHaveTextContent(/Large/i);
        expect(projects[1]).toHaveTextContent(/Medium/i);
        expect(projects[2]).toHaveTextContent(/Small/i);
      });
    });
  });

  describe('Pagination', () => {
    it('displays pagination controls when needed', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: Array.from({ length: 50 }, (_, i) => ({
          id: `${i}`,
          name: `Project ${i}`,
        })),
        page: 1,
        pageSize: 50,
        total: 150,
        totalPages: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/page 1 of 3/i)).toBeInTheDocument();
      });

      expect(screen.getByRole('button', { name: /next page/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /previous page/i })).toBeDisabled();
    });

    it('navigates to next page', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValueOnce({
        data: [{ id: '1', name: 'Page 1 Project' }],
        page: 1,
        pageSize: 50,
        total: 100,
        totalPages: 2,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Page 1 Project/i)).toBeInTheDocument();
      });

      vi.mocked(fetchProjects).mockResolvedValueOnce({
        data: [{ id: '51', name: 'Page 2 Project' }],
        page: 2,
        pageSize: 50,
        total: 100,
        totalPages: 2,
      });

      const nextButton = screen.getByRole('button', { name: /next page/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText(/Page 2 Project/i)).toBeInTheDocument();
      });
    });

    it('changes page size', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: Array.from({ length: 50 }, (_, i) => ({
          id: `${i}`,
          name: `Project ${i}`,
        })),
        page: 1,
        pageSize: 50,
        total: 150,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Project 0/i)).toBeInTheDocument();
      });

      const pageSizeSelect = screen.getByRole('combobox', {
        name: /items per page/i,
      });
      await userEvent.click(pageSizeSelect);
      await userEvent.click(screen.getByRole('option', { name: /100/i }));

      await waitFor(() => {
        expect(fetchProjects).toHaveBeenCalledWith(expect.objectContaining({ pageSize: 100 }));
      });
    });
  });

  describe('Search', () => {
    it('searches projects by name', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'E-Commerce Platform' },
          { id: '2', name: 'Mobile App' },
          { id: '3', name: 'E-Learning System' },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/E-Commerce Platform/i)).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search projects/i);
      await userEvent.type(searchInput, 'e-');

      await waitFor(() => {
        expect(screen.getByText(/E-Commerce Platform/i)).toBeInTheDocument();
        expect(screen.getByText(/E-Learning System/i)).toBeInTheDocument();
        expect(screen.queryByText(/Mobile App/i)).not.toBeInTheDocument();
      });
    });

    it('debounces search input', async () => {
      vi.useFakeTimers();

      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search projects/i)).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search projects/i);
      await userEvent.type(searchInput, 'test');

      // Search should not trigger immediately
      expect(fetchProjects).toHaveBeenCalledTimes(1); // Initial load only

      vi.advanceTimersByTime(300); // Debounce delay

      await waitFor(() => {
        expect(fetchProjects).toHaveBeenCalledTimes(2); // Now with search
      });

      vi.useRealTimers();
    });

    it('clears search with clear button', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: '1', name: 'Found Project' }],
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search projects/i)).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search projects/i);
      await userEvent.type(searchInput, 'found');

      await waitFor(() => {
        expect(screen.getByText(/Found Project/i)).toBeInTheDocument();
      });

      const clearButton = screen.getByRole('button', { name: /clear search/i });
      await userEvent.click(clearButton);

      await waitFor(() => {
        expect(searchInput).toHaveValue('');
      });
    });
  });

  describe('Project Creation', () => {
    it('opens create project dialog', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /create project/i })).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', {
        name: /create project/i,
      });
      await userEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByRole('dialog', { name: /create project/i })).toBeInTheDocument();
      });
    });

    it('creates new project successfully', async () => {
      const { fetchProjects, createProject } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
      vi.mocked(createProject).mockResolvedValue({
        description: 'Test description',
        id: 'new-proj',
        name: 'New Project',
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /create project/i })).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', {
        name: /create project/i,
      });
      await userEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
      });

      await userEvent.type(screen.getByLabelText(/project name/i), 'New Project');
      await userEvent.type(screen.getByLabelText(/description/i), 'Test description');

      const submitButton = screen.getByRole('button', { name: /create$/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/project created successfully/i)).toBeInTheDocument();
      });
    });

    it('shows validation errors on invalid input', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /create project/i })).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', {
        name: /create project/i,
      });
      await userEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
      });

      const submitButton = screen.getByRole('button', { name: /create$/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/project name is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Project Actions', () => {
    it('navigates to project detail on card click', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: 'proj-123', name: 'Test Project' }],
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Test Project/i)).toBeInTheDocument();
      });

      const projectCard = screen.getByTestId('project-card-proj-123');
      await userEvent.click(projectCard);

      await waitFor(() => {
        expect(history.location.pathname).toBe('/projects/proj-123');
      });
    });

    it('opens context menu on right click', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: 'proj-123', name: 'Test Project' }],
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Test Project/i)).toBeInTheDocument();
      });

      const projectCard = screen.getByTestId('project-card-proj-123');
      await userEvent.pointer({ keys: '[MouseRight]', target: projectCard });

      await waitFor(() => {
        expect(screen.getByRole('menu')).toBeInTheDocument();
      });

      expect(screen.getByRole('menuitem', { name: /edit/i })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: /delete/i })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: /duplicate/i })).toBeInTheDocument();
    });

    it('deletes project with confirmation', async () => {
      const { fetchProjects, deleteProject } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: 'proj-123', name: 'Test Project' }],
        total: 1,
      });
      vi.mocked(deleteProject).mockResolvedValue({ success: true });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Test Project/i)).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole('button', {
        name: /delete project proj-123/i,
      });
      await userEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', {
        name: /confirm delete/i,
      });
      await userEvent.click(confirmButton);

      await waitFor(() => {
        expect(screen.getByText(/project deleted successfully/i)).toBeInTheDocument();
      });
    });
  });

  describe('Empty States', () => {
    it('shows empty state when no projects exist', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/no projects yet/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/create your first project/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create project/i })).toBeInTheDocument();
    });

    it('shows empty state for search with no results', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [{ id: '1', name: 'Existing Project' }],
        total: 1,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Existing Project/i)).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search projects/i);
      await userEvent.type(searchInput, 'nonexistent');

      await waitFor(() => {
        expect(screen.getByText(/no projects found/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/try different search terms/i)).toBeInTheDocument();
    });
  });

  describe('Bulk Operations', () => {
    it('selects multiple projects', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Project 1' },
          { id: '2', name: 'Project 2' },
          { id: '3', name: 'Project 3' },
        ],
        total: 3,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
      });

      const checkbox1 = screen.getByRole('checkbox', {
        name: /select project 1/i,
      });
      const checkbox2 = screen.getByRole('checkbox', {
        name: /select project 2/i,
      });

      await userEvent.click(checkbox1);
      await userEvent.click(checkbox2);

      await waitFor(() => {
        expect(screen.getByText(/2 selected/i)).toBeInTheDocument();
      });
    });

    it('selects all projects', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Project 1' },
          { id: '2', name: 'Project 2' },
        ],
        total: 2,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
      });

      const selectAllCheckbox = screen.getByRole('checkbox', {
        name: /select all/i,
      });
      await userEvent.click(selectAllCheckbox);

      await waitFor(() => {
        expect(screen.getByText(/2 selected/i)).toBeInTheDocument();
      });
    });

    it('bulk deletes selected projects', async () => {
      const { fetchProjects, deleteProject } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Project 1' },
          { id: '2', name: 'Project 2' },
        ],
        total: 2,
      });
      vi.mocked(deleteProject).mockResolvedValue({ success: true });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
      });

      // Select projects
      await userEvent.click(screen.getByRole('checkbox', { name: /select project 1/i }));
      await userEvent.click(screen.getByRole('checkbox', { name: /select project 2/i }));

      const bulkDeleteButton = screen.getByRole('button', {
        name: /delete selected/i,
      });
      await userEvent.click(bulkDeleteButton);

      await waitFor(() => {
        expect(screen.getByText(/delete 2 projects/i)).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      await userEvent.click(confirmButton);

      await waitFor(() => {
        expect(screen.getByText(/2 projects deleted/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper heading hierarchy', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        const headings = screen.getAllByRole('heading');
        expect(headings[0].tagName).toBe('H1');
      });
    });

    it('supports keyboard navigation through projects', async () => {
      const { fetchProjects } = await import('@/api/projects');

      vi.mocked(fetchProjects).mockResolvedValue({
        data: [
          { id: '1', name: 'Project 1' },
          { id: '2', name: 'Project 2' },
        ],
        total: 2,
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
      });

      await userEvent.tab();
      expect(screen.getByTestId('project-card-1')).toHaveFocus();

      await userEvent.tab();
      expect(screen.getByTestId('project-card-2')).toHaveFocus();
    });
  });
});
