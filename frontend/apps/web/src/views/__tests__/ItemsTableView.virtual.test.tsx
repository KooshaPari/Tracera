import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createRootRoute, createRouter } from '@tanstack/react-router';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ItemsTableView } from '../ItemsTableView';

// Mock hooks
vi.mock('../../hooks/useItems', () => ({
  useCreateItem: vi.fn(() => ({
    isPending: false,
    mutateAsync: vi.fn(),
  })),
  useDeleteItem: vi.fn(() => ({
    isPending: false,
    mutateAsync: vi.fn(),
  })),
  useItems: vi.fn(() => ({
    data: {
      items: Array.from({ length: 1000 }, (_, i) => ({
        createdAt: new Date(2024, 0, (i % 30) + 1).toISOString(),
        id: `item-${i}`,
        owner: `Owner ${i % 5}`,
        priority: 'medium' as const,
        status: 'todo' as const,
        title: `Item ${i}`,
        type: 'feature',
      })),
    },
    isLoading: false,
  })),
}));

vi.mock('../../hooks/useProjects', () => ({
  useProjects: vi.fn(() => ({
    data: [],
  })),
}));

// Setup router
const rootRoute = createRootRoute({
  component: () => <ItemsTableView />,
});

const router = createRouter({
  routeTree: rootRoute,
});

describe.skip('ItemsTableView - Virtual Scrolling', () => {
  let queryClient: QueryClient;
  let user: ReturnType<typeof userEvent.setup>;
  let container: HTMLElement;

  beforeEach(() => {
    queryClient = new QueryClient();
    user = userEvent.setup();
  });

  it('should render virtual table with 1000 items', async () => {
    const { container: renderContainer } = render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router}>
          <ItemsTableView />
        </RouterProvider>
      </QueryClientProvider>,
    );
    container = renderContainer;

    // Wait for items to load
    await screen.findByText(/Item 0/i);

    // Verify that the virtual container exists
    const virtualContainer = container.querySelector('[style*="height"]');
    expect(virtualContainer).toBeInTheDocument();
  });

  it('should only render visible rows (not all 1000)', async () => {
    const { container: renderContainer } = render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router}>
          <ItemsTableView />
        </RouterProvider>
      </QueryClientProvider>,
    );
    container = renderContainer;

    await screen.findByText(/Item 0/i);

    // Count rendered TableRow elements
    const rows = container.querySelectorAll('tbody tr');

    // Should be much less than 1000 (typically 10-20 visible + overscan)
    expect(rows.length).toBeLessThan(50);
    expect(rows.length).toBeGreaterThan(0);
  });

  it('should handle search filtering with virtual scrolling', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router}>
          <ItemsTableView />
        </RouterProvider>
      </QueryClientProvider>,
    );

    await screen.findByText(/Item 0/i);

    // Search for a specific item
    const searchInput = screen.getByPlaceholderText(/Search identifiers/i);
    await user.type(searchInput, 'Item 42');

    // Wait for filtered results
    await screen.findByText(/Item 42/i);

    // Verify only filtered items are in DOM
    const rows = container.querySelectorAll('tbody tr');
    expect(rows.length).toBeLessThan(10);
  });

  it('should handle sorting with virtual scrolling', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router}>
          <ItemsTableView />
        </RouterProvider>
      </QueryClientProvider>,
    );

    await screen.findByText(/Item 0/i);

    // Click sort button
    const sortButton = screen.getByRole('button', { name: /Node Identifier/i });
    await user.click(sortButton);

    // Verify results are still rendered
    await screen.findByText(/Item/i);
  });

  it('should display empty state when no items match filter', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router}>
          <ItemsTableView />
        </RouterProvider>
      </QueryClientProvider>,
    );

    await screen.findByText(/Item 0/i);

    // Search for non-existent item
    const searchInput = screen.getByPlaceholderText(/Search identifiers/i);
    await user.type(searchInput, 'nonexistent-item-xyz');

    // Wait for empty state
    await screen.findByText(/Registry Vacant/i);
  });
});
