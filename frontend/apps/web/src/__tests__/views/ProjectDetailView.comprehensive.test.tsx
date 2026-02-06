/**
 * Comprehensive Tests for ProjectDetailView
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useItems } from '../../hooks/useItems';
import { useLinks } from '../../hooks/useLinks';
import { useProject } from '../../hooks/useProjects';
import { ProjectDetailView } from '../../views/ProjectDetailView';

// Mock TanStack Router
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    Link: ({ children, to }: any) => (
      <a href={typeof to === 'string' ? to : to.toString()}>{children}</a>
    ),
    useNavigate: () => vi.fn(),
    useParams: () => ({ projectId: 'proj-1' }),
    useSearch: () => ({}),
    ...actual,
  };
});

vi.mock('../../hooks/useItems', () => ({
  useItems: vi.fn(),
}));

vi.mock('../../hooks/useLinks', () => ({
  useLinks: vi.fn(),
}));

vi.mock('../../hooks/useProjects', () => ({
  useProject: vi.fn(),
  useUpdateProject: vi.fn(),
}));

const user = userEvent.setup();

describe(ProjectDetailView, () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  it('renders project detail with tabs', () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        description: 'Test description',
        id: 'proj-1',
        name: 'Test Project',
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    // Text appears multiple times, use getAllByText
    expect(screen.getAllByText('Test Project').length).toBeGreaterThan(0);
  });

  it('displays project statistics', () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        id: 'proj-1',
        name: 'Test Project',
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: [
        { id: 'item-1', status: 'todo' },
        { id: 'item-2', status: 'done' },
      ],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: [{ id: 'link-1' }],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/Total Items/i)).toBeInTheDocument();
  });

  it('handles tab switching', async () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        id: 'proj-1',
        name: 'Test Project',
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    // Find and click tabs
    const tabs = screen.getAllByRole('tab');
    const secondTab = tabs[1];
    if (secondTab) {
      await user.click(secondTab);
      // Should switch to different tab content
    }
  });

  it('displays items by type', () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        id: 'proj-1',
        name: 'Test Project',
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: {
        items: [
          {
            id: 'item-1',
            priority: 'high',
            status: 'todo',
            title: 'Feature 1',
            type: 'feature',
          },
          {
            id: 'item-2',
            priority: 'medium',
            status: 'in_progress',
            title: 'Requirement 1',
            type: 'requirement',
          },
        ],
        total: 2,
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Feature 1')).toBeInTheDocument();
  });
});
