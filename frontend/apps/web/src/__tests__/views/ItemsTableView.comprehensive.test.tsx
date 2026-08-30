/**
 * Comprehensive Tests for ItemsTableView
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useCreateItem, useDeleteItem, useItems, useUpdateItem } from '../../hooks/useItems';
import { useProjects } from '../../hooks/useProjects';
import { ItemsTableView } from '../../views/ItemsTableView';

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
  useCreateItem: vi.fn(),
  useDeleteItem: vi.fn(),
  useItems: vi.fn(),
  useUpdateItem: vi.fn(),
}));

vi.mock('../../hooks/useProjects', () => ({
  useProjects: vi.fn(),
}));

describe(ItemsTableView, () => {
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
    vi.mocked(useCreateItem).mockReturnValue({ isPending: false, mutate: vi.fn() } as any);
  });

  it('renders table with items', () => {
    const mockItems = [
      {
        created_at: new Date().toISOString(),
        id: 'item-1',
        owner: 'user1',
        priority: 'high',
        status: 'todo',
        title: 'Item 1',
        type: 'feature',
      },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: { items: mockItems },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useUpdateItem).mockReturnValue({
      mutate: vi.fn(),
    } as any);

    vi.mocked(useDeleteItem).mockReturnValue({
      mutate: vi.fn(),
    } as any);

    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTableView projectId='proj-1' type='feature' />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId('item-title')).toHaveTextContent('Item 1');
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
        <ItemsTableView projectId='proj-1' type='feature' />
      </QueryClientProvider>,
    );

    // Should show loading skeleton
  });

  it('handles sorting', async () => {
    const mockItems = [
      {
        created_at: new Date('2024-01-01').toISOString(),
        id: 'item-1',
        priority: 'low',
        status: 'todo',
        title: 'Item A',
        type: 'feature',
      },
      {
        created_at: new Date('2024-01-02').toISOString(),
        id: 'item-2',
        priority: 'high',
        status: 'done',
        title: 'Item B',
        type: 'feature',
      },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: { items: mockItems },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useUpdateItem).mockReturnValue({
      mutate: vi.fn(),
    } as any);

    vi.mocked(useDeleteItem).mockReturnValue({
      mutate: vi.fn(),
    } as any);

    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTableView projectId='proj-1' />
      </QueryClientProvider>,
    );

    // Both items should be visible initially
    expect(screen.getAllByTestId('item-title').map((title) => title.textContent)).toEqual([
      'Item A',
      'Item B',
    ]);

    // Click on sortable column header
    const titleHeader = screen.getByText('Title');
    await user.click(titleHeader);
    await user.click(titleHeader);

    // Items should still be visible after sort (sorting is handled by table component)
    expect(screen.getAllByTestId('item-title').map((title) => title.textContent)).toEqual([
      'Item B',
      'Item A',
    ]);
  });

  it('handles filtering', async () => {
    const mockItems = [
      {
        id: 'item-1',
        priority: 'high',
        status: 'todo',
        title: 'Item 1',
        type: 'feature',
      },
      {
        id: 'item-2',
        priority: 'low',
        status: 'done',
        title: 'Item 2',
        type: 'feature',
      },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: { items: mockItems },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useUpdateItem).mockReturnValue({
      mutate: vi.fn(),
    } as any);

    vi.mocked(useDeleteItem).mockReturnValue({
      mutate: vi.fn(),
    } as any);

    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTableView projectId='proj-1' />
      </QueryClientProvider>,
    );

    // Filter input should be present
    const filterInput = screen.getByPlaceholderText(/Search/i);
    expect(filterInput).toBeInTheDocument();

    // Both items visible initially
    expect(screen.getAllByTestId('item-title').map((title) => title.textContent)).toEqual([
      'Item 1',
      'Item 2',
    ]);

    // Type in the client-side filter.
    await user.type(filterInput, 'Item 1');

    await waitFor(() => {
      expect(screen.getAllByTestId('item-title').map((title) => title.textContent)).toEqual([
        'Item 1',
      ]);
    });
  });

  it('exposes item actions', () => {
    const mockItems = [
      {
        id: 'item-1',
        status: 'todo',
        title: 'Item 1',
        type: 'feature',
      },
      {
        id: 'item-2',
        status: 'done',
        title: 'Item 2',
        type: 'feature',
      },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: { items: mockItems },
      error: null,
      isError: false,
      isLoading: false,
    } as any);
    vi.mocked(useUpdateItem).mockReturnValue({ mutate: vi.fn() } as any);
    vi.mocked(useDeleteItem).mockReturnValue({ mutate: vi.fn() } as any);
    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ItemsTableView projectId='proj-1' type='feature' />
      </QueryClientProvider>,
    );

    expect(screen.getAllByRole('button', { name: /Open item Item [12]/ })).toHaveLength(4);
    expect(screen.getAllByRole('button', { name: /Delete item Item [12]/ })).toHaveLength(4);
  });
});
