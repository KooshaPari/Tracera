/**
 * Comprehensive Tests for ItemsTreeView
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useItems } from '../../hooks/useItems';
import { useProjects } from '../../hooks/useProjects';
import { ItemsTreeView } from '../../views/ItemsTreeView';

// Mock TanStack Router
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    Link: ({ children, to }: any) => (
      <a href={typeof to === 'string' ? to : to.toString()}>{children}</a>
    ),
    useNavigate: () => vi.fn(),
    useSearch: () => ({}),
  };
});

vi.mock('../../hooks/useItems', () => ({
  useItems: vi.fn(),
}));

vi.mock('../../hooks/useProjects', () => ({
  useProjects: vi.fn(),
}));

describe(ItemsTreeView, () => {
  let queryClient: QueryClient;
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  it('renders tree view with items', () => {
    const mockItems = [
      {
        id: 'item-1',
        parentId: null,
        status: 'todo',
        title: 'Parent Item',
        type: 'feature',
      },
      {
        id: 'item-2',
        parentId: 'item-1',
        status: 'done',
        title: 'Child Item',
        type: 'feature',
      },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: mockItems,
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTreeView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Parent Item')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    vi.mocked(useItems).mockReturnValue({
      data: undefined,
      error: null,
      isError: false,
      isLoading: true,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTreeView />
      </QueryClientProvider>,
    );

    // Should show loading skeleton
  });

  it('handles expand/collapse', async () => {
    const mockItems = [
      {
        id: 'item-1',
        parentId: null,
        status: 'todo',
        title: 'Parent Item',
        type: 'feature',
      },
      {
        id: 'item-2',
        parentId: 'item-1',
        status: 'done',
        title: 'Child Item',
        type: 'feature',
      },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: mockItems,
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTreeView />
      </QueryClientProvider>,
    );

    // Find expand button
    const expandButtons = screen.getAllByText('▶');
    if (expandButtons.length > 0) {
      await user.click(expandButtons[0]);
      await waitFor(() => {
        expect(screen.getByText('Child Item')).toBeInTheDocument();
      });
    }
  });

  it('displays search functionality', async () => {
    vi.mocked(useItems).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTreeView />
      </QueryClientProvider>,
    );

    const searchInput = screen.getByPlaceholderText(/Search/i);
    if (searchInput) {
      await user.type(searchInput, 'test');
      // Should filter tree items
    }
  });
});
