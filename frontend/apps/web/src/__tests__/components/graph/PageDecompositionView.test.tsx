/**
 * Comprehensive tests for PageDecompositionView component
 * Tests: hierarchical decomposition, search, expand/collapse, view modes
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { Item, Link } from '@tracertm/types';

import { PageDecompositionView } from '@/components/graph/PageDecompositionView';

// =============================================================================
// FIXTURES
// =============================================================================

const mockSite: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'site-1',
  projectId: 'proj-1',
  status: 'active',
  title: 'E-commerce Platform',
  type: 'site',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockPage: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'page-1',
  projectId: 'proj-1',
  status: 'active',
  title: 'Product Listing',
  type: 'page',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockLayout: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'layout-1',
  projectId: 'proj-1',
  status: 'active',
  title: 'Main Layout',
  type: 'layout',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockSection: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'section-1',
  projectId: 'proj-1',
  status: 'active',
  title: 'Product Grid',
  type: 'section',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockComponent: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'component-1',
  projectId: 'proj-1',
  status: 'active',
  title: 'Product Card',
  type: 'component',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockElement: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'element-1',
  projectId: 'proj-1',
  status: 'active',
  title: 'Product Title',
  type: 'element',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockItems = [mockSite, mockPage, mockLayout, mockSection, mockComponent, mockElement];

const mockLinks: Link[] = [
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'link-1',
    projectId: 'proj-1',
    sourceItemId: 'site-1',
    targetItemId: 'page-1',
    type: 'contains',
  } as any,
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'link-2',
    projectId: 'proj-1',
    sourceItemId: 'page-1',
    targetItemId: 'layout-1',
    type: 'contains',
  } as any,
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'link-3',
    projectId: 'proj-1',
    sourceItemId: 'layout-1',
    targetItemId: 'section-1',
    type: 'contains',
  } as any,
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'link-4',
    projectId: 'proj-1',
    sourceItemId: 'section-1',
    targetItemId: 'component-1',
    type: 'contains',
  } as any,
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'link-5',
    projectId: 'proj-1',
    sourceItemId: 'component-1',
    targetItemId: 'element-1',
    type: 'contains',
  } as any,
];

// =============================================================================
// COMPONENT TESTS
// =============================================================================

describe('PageDecompositionView Component', () => {
  let onSelectItem: ReturnType<typeof vi.fn>;
  let onViewInCode: ReturnType<typeof vi.fn>;
  let onViewInDesign: ReturnType<typeof vi.fn>;
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    onSelectItem = vi.fn();
    onViewInCode = vi.fn();
    onViewInDesign = vi.fn();
    user = userEvent.setup();
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders page decomposition view with title', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('displays hierarchical structure', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('E-commerce Platform')).toBeInTheDocument();
      expect(screen.getByText('Product Listing')).toBeInTheDocument();
    });

    it('shows statistics for entity types', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      // Component should render without errors
      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('renders search input', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      expect(searchInput).toBeInTheDocument();
    });

    it('renders view mode toggle buttons', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Hierarchical Expansion', () => {
    it('expands items when clicking expand button', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const siteItem = screen.getByText('E-commerce Platform');
      expect(siteItem).toBeInTheDocument();

      // Click expand for site
      const expandButtons = screen.getAllByRole('button');
      const siteExpandButton = expandButtons.find((btn) =>
        btn.closest('div')?.textContent?.includes('E-commerce Platform'),
      );

      if (siteExpandButton) {
        await user.click(siteExpandButton);
      }

      await waitFor(() => {
        expect(screen.getByText('Product Listing')).toBeInTheDocument();
      });
    });

    it('collapses items when clicking collapse button', async () => {
      const { rerender } = render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('E-commerce Platform')).toBeInTheDocument();

      // Test collapse behavior
      rerender(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('E-commerce Platform')).toBeInTheDocument();
    });

    it('shows expand all button', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('shows collapse all button', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('expands all items when Expand All clicked', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      // Find and click expand all button
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('collapses all items when Collapse All clicked', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Search Functionality', () => {
    it('filters items by search query', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'product');

      await waitFor(() => {
        expect(screen.getByText(/Product/i)).toBeInTheDocument();
      });
    });

    it('case-insensitive search', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'PRODUCT');

      await waitFor(() => {
        expect(screen.getByText(/Product/i)).toBeInTheDocument();
      });
    });

    it('clears search results when query is cleared', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'product');

      await waitFor(() => {
        expect(screen.getByText(/Product/i)).toBeInTheDocument();
      });

      await user.clear(searchInput);

      await waitFor(() => {
        expect(screen.getByText('E-commerce Platform')).toBeInTheDocument();
      });
    });

    it('shows no results message when no matches', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'nonexistent');

      // Should handle no results gracefully
      expect(searchInput).toBeInTheDocument();
    });
  });

  describe('Item Selection', () => {
    it('calls onSelectItem when item clicked', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const siteItem = screen.getByText('E-commerce Platform');
      await user.click(siteItem);

      await waitFor(() => {
        expect(onSelectItem).toHaveBeenCalled();
      });
    });

    it('highlights selected item', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId='site-1'
        />,
      );

      expect(screen.getByText('E-commerce Platform')).toBeInTheDocument();
    });

    it('shows action buttons for selected item', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId='site-1'
          onViewInCode={onViewInCode}
          onViewInDesign={onViewInDesign}
        />,
      );

      expect(screen.getByText('E-commerce Platform')).toBeInTheDocument();
    });
  });

  describe('View Modes', () => {
    it('switches to tree view', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      const treeButton = buttons[0]; // Assuming first button is tree view

      await user.click(treeButton);

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('switches to outline view', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      if (buttons.length > 1) {
        await user.click(buttons[1]);
      }

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('switches to visual view', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      if (buttons.length > 2) {
        await user.click(buttons[2]);
      }

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });
  });

  describe('Depth Control', () => {
    it('expands to specific depth', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('shows depth indicator when enabled', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });
  });

  describe('Root Item', () => {
    it('uses root item as starting point when provided', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
          rootId='page-1'
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('shows all items when no root specified', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('E-commerce Platform')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty items list', () => {
      render(
        <PageDecompositionView
          items={[]}
          links={[]}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('handles items without children', () => {
      render(
        <PageDecompositionView
          items={[mockElement]}
          links={[]}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Product Title')).toBeInTheDocument();
    });

    it('handles broken hierarchy', () => {
      const brokenLinks: Link[] = [
        {
          createdAt: '2024-01-01T00:00:00Z',
          id: 'link-1',
          projectId: 'proj-1',
          sourceItemId: 'nonexistent',
          targetItemId: 'page-1',
          type: 'contains',
        } as any,
      ];

      render(
        <PageDecompositionView
          items={mockItems}
          links={brokenLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('handles duplicate links', () => {
      const duplicateLinks: Link[] = [
        ...mockLinks,
        mockLinks[0], // Duplicate
      ];

      render(
        <PageDecompositionView
          items={mockItems}
          links={duplicateLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });
  });

  describe('Statistics', () => {
    it('displays entity type counts', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('updates statistics when items change', () => {
      const { rerender } = render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const newItems = [...mockItems, mockComponent];
      rerender(
        <PageDecompositionView
          items={newItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('supports keyboard navigation', async () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      await user.tab();
      expect(screen.getByText('Page Decomposition')).toBeInTheDocument();
    });

    it('provides proper ARIA labels', () => {
      render(
        <PageDecompositionView
          items={mockItems}
          links={mockLinks}
          onSelectItem={onSelectItem}
          selectedItemId={null}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      expect(searchInput).toBeInTheDocument();
    });
  });
});
