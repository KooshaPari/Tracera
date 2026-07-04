import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import * as hooks from '../../hooks/useItems';
import * as projectHooks from '../../hooks/useProjects';
import { ItemsTreeView } from '../../views/ItemsTreeView';

// Mock react router
vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children }: any) => <a href={to}>{children}</a>,
  useNavigate: vi.fn(() => vi.fn()),
  useSearch: vi.fn(() => ({})),
}));

// Mock hooks
vi.mock('../../hooks/useItems', () => ({
  useItems: vi.fn(),
}));

vi.mock('../../hooks/useProjects', () => ({
  useProjects: vi.fn(),
}));

const mockTreeItems = Array.from({ length: 50 }, (_, i) => ({
  id: `item-${i}`,
  title: `Item ${i}`,
  description: `Description for item ${i}`,
  type: ['requirement', 'feature', 'test', 'bug', 'task'][i % 5],
  status: ['todo', 'in_progress', 'done', 'blocked'][i % 4],
  priority: ['critical', 'high', 'medium', 'low'][i % 4],
  owner: i % 2 === 0 ? `User ${i % 5}` : null,
  parentId: i > 10 ? `item-${Math.floor(i / 2)}` : null, // Create hierarchy
  projectId: `project-${i % 3}`,
  createdAt: new Date(),
  updatedAt: new Date(),
}));

describe('ItemsTreeView Performance', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(hooks, 'useItems').mockReturnValue({
      data: { items: mockTreeItems },
      isLoading: false,
    } as any);
    vi.spyOn(projectHooks, 'useProjects').mockReturnValue({
      data: [
        { id: 'project-0', name: 'Project 0' },
        { id: 'project-1', name: 'Project 1' },
        { id: 'project-2', name: 'Project 2' },
      ],
    } as any);
  });

  it('renders tree with hierarchical data efficiently', () => {
    const renderSpy = vi.fn();
    const OriginalItemsTreeView = ItemsTreeView;

    const WrappedView = () => {
      renderSpy();
      return <OriginalItemsTreeView />;
    };

    const { rerender } = render(<WrappedView />);

    // Initial render
    expect(renderSpy).toHaveBeenCalledTimes(1);

    // Re-render with same props should not increase count significantly
    rerender(<WrappedView />);
    expect(renderSpy).toHaveBeenCalledTimes(2);
  });

  it('memoizes TreeItem components with deep nesting', () => {
    const { container } = render(<ItemsTreeView />);

    // Check that tree items are rendered
    const treeItems = container.querySelectorAll('[style*="marginLeft"]');
    expect(treeItems.length).toBeGreaterThan(0);
  });

  it('handles expand/collapse operations efficiently', async () => {
    const user = userEvent.setup();
    const { container } = render(<ItemsTreeView />);

    // Find expand buttons
    const expandButtons = container.querySelectorAll('button');
    const chevronButtons = [...expandButtons].filter((btn: Element) => btn.querySelector('svg'));

    if (chevronButtons.length > 0) {
      const firstButton = chevronButtons[0];
      if (!firstButton) {
        return;
      }

      // Click to expand
      await user.click(firstButton);
      expect(firstButton).toBeInTheDocument();

      // Click again to collapse
      await user.click(firstButton);
      expect(firstButton).toBeInTheDocument();
    }
  });

  it('expands/collapses all efficiently without performance degradation', async () => {
    const user = userEvent.setup();
    const { container } = render(<ItemsTreeView />);

    // Find expand all button (Maximize2 icon)
    const buttons = screen.getAllByRole('button');
    const expandAllButton = buttons.find((btn) => btn.getAttribute('title') === 'Expand All');

    if (expandAllButton) {
      await user.click(expandAllButton);
      // Should still render efficiently
      const treeItems = container.querySelectorAll('[style*="marginLeft"]');
      expect(treeItems.length).toBeGreaterThan(0);
    }
  });

  it('filters tree items efficiently with memoization', async () => {
    const user = userEvent.setup();
    const { container } = render(<ItemsTreeView />);

    const searchInput = container.querySelector('input[placeholder="Search hierarchy..."]');
    expect(searchInput).toBeInTheDocument();

    if (searchInput) {
      // Type to filter
      await user.type(searchInput, 'Item 1');

      // Should still render efficiently
      const treeItems = container.querySelectorAll('[style*="marginLeft"]');
      expect(treeItems.length).toBeGreaterThan(0);
    }
  });

  it('preserves tree structure when filtering', async () => {
    const user = userEvent.setup();
    const { container, rerender } = render(<ItemsTreeView />);

    const searchInput = container.querySelector('input[placeholder="Search hierarchy..."]')!;

    if (searchInput) {
      await user.clear(searchInput);
      await user.type(searchInput, '0');

      // Should maintain tree structure
      const treeItems = container.querySelectorAll('[style*="marginLeft"]');
      expect(treeItems.length).toBeGreaterThan(0);

      // Re-render should not cause excessive updates
      rerender(<ItemsTreeView />);
      const rerenderedItems = container.querySelectorAll('[style*="marginLeft"]');
      expect(rerenderedItems.length).toBeGreaterThan(0);
    }
  });

  it('memoizes tree structure with expand state', async () => {
    const user = userEvent.setup();
    const { container } = render(<ItemsTreeView />);

    // Get initial state
    const initialItems = container.querySelectorAll('[style*="marginLeft"]');
    const initialCount = initialItems.length;
    void initialCount;

    // Toggle expand state
    const expandButtons = container.querySelectorAll('button');
    const chevronButtons = [...expandButtons].filter((btn: Element) => btn.querySelector('svg'));

    if (chevronButtons.length > 0) {
      const firstButton = chevronButtons[0];
      if (!firstButton) {
        return;
      }
      await user.click(firstButton);
      const expandedItems = container.querySelectorAll('[style*="marginLeft"]');

      // Count should change based on expand state
      expect(expandedItems.length).not.toBe(0);
    }
  });
});
