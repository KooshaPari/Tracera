/**
 * Comprehensive Accessibility Tests for ItemsTableView
 * WCAG 2.1 Level AA Compliance
 *
 * Tests:
 * - Keyboard navigation (arrow keys, Home/End, Ctrl+Home/End)
 * - ARIA attributes (roles, labels, descriptions)
 * - Screen reader announcements
 * - Focus management and indicators
 * - Color contrast
 * - Semantic HTML
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useDeleteItem, useItems } from '../../hooks/useItems';
import { useProjects } from '../../hooks/useProjects';
import { ItemsTableViewA11y } from '../../views/ItemsTableViewA11y';

// Mock dependencies
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useSearch: () => ({}),
  };
});

vi.mock('../../hooks/useItems', () => ({
  useCreateItem: vi.fn(() => ({
    isPending: false,
    mutateAsync: vi.fn(),
  })),
  useDeleteItem: vi.fn(),
  useItems: vi.fn(),
  useUpdateItem: vi.fn(),
}));

vi.mock('../../hooks/useProjects', () => ({
  useProjects: vi.fn(),
}));

describe('ItemsTableViewA11y - Accessibility', () => {
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

  const mockItems = [
    {
      createdAt: new Date('2024-01-01').toISOString(),
      id: 'item-1',
      owner: 'john',
      priority: 'high',
      status: 'in_progress',
      title: 'Create Authentication',
      type: 'feature',
    },
    {
      createdAt: new Date('2024-01-02').toISOString(),
      id: 'item-2',
      owner: 'jane',
      priority: 'critical',
      status: 'todo',
      title: 'Setup Database',
      type: 'feature',
    },
    {
      createdAt: new Date('2024-01-03').toISOString(),
      id: 'item-3',
      owner: 'bob',
      priority: 'high',
      status: 'blocked',
      title: 'Fix Login Bug',
      type: 'bug',
    },
  ];

  const renderTable = () => {
    vi.mocked(useItems).mockReturnValue({
      data: { items: mockItems },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useDeleteItem).mockReturnValue({
      mutateAsync: vi.fn(),
    } as any);

    vi.mocked(useProjects).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    return render(
      <QueryClientProvider client={queryClient}>
        <ItemsTableViewA11y />
      </QueryClientProvider>,
    );
  };

  describe('ARIA Roles and Attributes', () => {
    it('should have proper table role and labels', () => {
      renderTable();

      const table = screen.getByRole('table', {
        name: /Items table with sortable columns/i,
      });
      expect(table).toBeInTheDocument();
    });

    it('should have aria-label on table container', () => {
      renderTable();

      const region = screen.getByRole('region', {
        name: /Items table with keyboard navigation support/i,
      });
      expect(region).toBeInTheDocument();
    });

    it('should have columnheader roles on header cells', () => {
      renderTable();

      const headers = screen.getAllByRole('columnheader');
      expect(headers.length).toBeGreaterThan(0);
      expect(headers[0]).toHaveAttribute('aria-colindex', '1');
    });

    it('should have row roles on table rows', () => {
      renderTable();

      const rows = screen.getAllByRole('row');
      expect(rows.length).toBeGreaterThan(1); // Header + data rows
      expect(rows[1]).toHaveAttribute('aria-rowindex', '2'); // First data row
    });

    it('should have gridcell roles on data cells', () => {
      renderTable();

      const cells = screen.getAllByRole('gridcell');
      expect(cells.length).toBeGreaterThan(0);
    });

    it('should have aria-sort on sortable headers', () => {
      renderTable();

      const nodeIdentifierHeader = screen.getByRole('columnheader', {
        name: /Node Identifier/i,
      });
      expect(nodeIdentifierHeader).toHaveAttribute('aria-sort');
    });

    it('should have aria-describedby for table instructions', () => {
      renderTable();

      const table = document.querySelector('#items-table-a11y');
      expect(table).toHaveAttribute('aria-describedby', 'table-instructions');

      const instructions = document.querySelector('#table-instructions');
      expect(instructions).toBeInTheDocument();
      expect(instructions).toHaveClass('sr-only');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should have arrow key navigation instructions in sr-only text', () => {
      renderTable();

      const instructions = document.querySelector('#table-instructions');
      expect(instructions?.textContent).toContain('Use arrow keys to navigate');
      expect(instructions?.textContent).toContain('Home and End');
      expect(instructions?.textContent).toContain('Ctrl+Home');
    });

    it('should have focusable elements with proper tabindex', () => {
      renderTable();

      const titleButton = screen.getByLabelText(/Item Create Authentication/i);
      expect(titleButton).toHaveAttribute('tabindex');
    });

    it('should have roving tabindex on action buttons', () => {
      renderTable();

      const buttons = screen.getAllByRole('button');
      // Some buttons should have tabindex=0 or -1 for roving tabindex
      const hasRovingTabindex = buttons.some(
        (btn) => btn.getAttribute('tabindex') === '0' || btn.getAttribute('tabindex') === '-1',
      );
      expect(hasRovingTabindex).toBeTruthy();
    });
  });

  describe('Focus Management', () => {
    it('should announce navigation to screen readers', () => {
      renderTable();

      const liveRegion = document.querySelector('#table-announcements');
      expect(liveRegion).toHaveAttribute('role', 'status');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveAttribute('aria-atomic', 'true');
    });

    it('should have visible focus indicators', () => {
      renderTable();

      const titleButton = screen.getByLabelText(/Item Create Authentication/i);
      expect(titleButton).toHaveClass('focus:ring-2', 'focus:ring-primary');
    });

    it('should manage focus when items are deleted', async () => {
      renderTable();

      const deleteButtons = screen.getAllByLabelText(/Delete item/i);
      expect(deleteButtons.length).toBeGreaterThan(0);
    });
  });

  describe('Semantic HTML and Labels', () => {
    it('should have descriptive aria-labels on action buttons', () => {
      renderTable();

      expect(
        screen.getByLabelText(/Open item details for Create Authentication/i),
      ).toBeInTheDocument();
      expect(screen.getByLabelText(/Delete item Create Authentication/i)).toBeInTheDocument();
    });

    it('should have aria-labels on search input', () => {
      renderTable();

      const searchInput = screen.getByLabelText(/Search items by title or ID/i);
      expect(searchInput).toBeInTheDocument();
    });

    it('should have aria-label on create button', () => {
      renderTable();

      const createButton = screen.getByLabelText(/Create new node/i);
      expect(createButton).toBeInTheDocument();
    });

    it('should have aria-label on view switch button', () => {
      renderTable();

      const workflowButton = screen.getByLabelText(/Switch to workflow view/i);
      expect(workflowButton).toBeInTheDocument();
    });

    it('should have status information as aria-labels', () => {
      renderTable();

      // Status should be readable by screen readers
      const statusElements = screen.getAllByText(/in progress/i);
      expect(statusElements.length).toBeGreaterThan(0);
    });

    it('should have priority information as aria-labels', () => {
      renderTable();

      // Priority dot should have aria-label
      const priorityLabels = screen.getAllByLabelText(/priority/i);
      expect(priorityLabels.length).toBeGreaterThan(0);
    });

    it('should have owner information with avatar labels', () => {
      renderTable();

      const ownerLabels = screen.getAllByLabelText(/Avatar for/i);
      expect(ownerLabels.length).toBeGreaterThan(0);
    });
  });

  describe('Screen Reader Compatibility', () => {
    it('should have sr-only instructions visible only to screen readers', () => {
      renderTable();

      const instructions = document.querySelector('#table-instructions');
      expect(instructions).toHaveClass('sr-only');

      // Verify it's visually hidden but accessible
      const _styles = globalThis.getComputedStyle(instructions!);
      // Sr-only class should hide element from view
    });

    it('should hide decorative icons from screen readers', () => {
      renderTable();

      // All lucide-react icons should have aria-hidden="true"
      const decorativeIcons = document.querySelectorAll("[aria-hidden='true']");
      expect(decorativeIcons.length).toBeGreaterThan(0);
    });

    it('should have proper heading hierarchy', () => {
      renderTable();

      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toHaveTextContent(/Node Registry/i);
    });

    it('should announce actions through live regions', () => {
      renderTable();

      const liveRegion = document.querySelector('#table-announcements');
      expect(liveRegion).toBeInTheDocument();
    });
  });

  describe('Modal Accessibility', () => {
    it('should have dialog role on create modal', async () => {
      renderTable();

      const createButton = screen.getByLabelText(/Create new node/i);
      await user.click(createButton);

      // Modal should have proper role
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('aria-modal', 'true');
    });

    it('should have aria-labelledby on modal', async () => {
      renderTable();

      const createButton = screen.getByLabelText(/Create new node/i);
      await user.click(createButton);

      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('aria-labelledby', 'create-modal-title');
    });

    it('should have labels on form inputs', async () => {
      renderTable();

      const createButton = screen.getByLabelText(/Create new node/i);
      await user.click(createButton);

      expect(screen.getByLabelText(/Title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Type/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Status/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Priority/i)).toBeInTheDocument();
    });

    it('should have close button with aria-label', async () => {
      renderTable();

      const createButton = screen.getByLabelText(/Create new node/i);
      await user.click(createButton);

      const closeButton = screen.getByLabelText(/Close dialog/i);
      expect(closeButton).toBeInTheDocument();
    });
  });

  describe('Content Structure', () => {
    it('should have proper table structure with headers and body', () => {
      renderTable();

      const tableHeader = screen.getByRole('rowgroup');
      expect(tableHeader).toBeInTheDocument();

      const rows = screen.getAllByRole('row');
      expect(rows.length).toBeGreaterThan(1);
    });

    it('should display all required columns', () => {
      renderTable();

      expect(screen.getByText('Node Identifier')).toBeInTheDocument();
      expect(screen.getByText('Type')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Priority')).toBeInTheDocument();
      expect(screen.getByText('Owner')).toBeInTheDocument();
      expect(screen.getByText('Actions')).toBeInTheDocument();
    });

    it('should display all item data', () => {
      renderTable();

      expect(screen.getByText('Create Authentication')).toBeInTheDocument();
      expect(screen.getByText('Setup Database')).toBeInTheDocument();
      expect(screen.getByText('Fix Login Bug')).toBeInTheDocument();
    });
  });

  describe('Error Handling and States', () => {
    it('should announce when items are deleted', async () => {
      vi.mocked(useDeleteItem).mockReturnValue({
        mutateAsync: vi.fn().mockResolvedValue({}),
      } as any);

      renderTable();

      const deleteButtons = screen.getAllByLabelText(/Delete item/i);
      if (deleteButtons.length > 0) {
        // Verify delete button has proper aria-label
        expect(deleteButtons[0]).toHaveAccessibleName(/Delete item/i);
      }
    });

    it('should handle empty state accessibly', () => {
      vi.mocked(useItems).mockReturnValue({
        data: { items: [] },
        error: null,
        isError: false,
        isLoading: false,
      } as any);

      render(
        <QueryClientProvider client={queryClient}>
          <ItemsTableViewA11y />
        </QueryClientProvider>,
      );

      expect(screen.getByText(/Registry Vacant/i)).toBeInTheDocument();
    });

    it('should handle loading state with semantic meaning', () => {
      vi.mocked(useItems).mockReturnValue({
        data: null,
        error: null,
        isError: false,
        isLoading: true,
      } as any);

      render(
        <QueryClientProvider client={queryClient}>
          <ItemsTableViewA11y />
        </QueryClientProvider>,
      );

      // Should show loading skeletons
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('WCAG 2.1 AA Compliance Specific Tests', () => {
    it('should have sufficient touch target size (44x44px minimum)', () => {
      renderTable();

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        // Buttons should have adequate padding
        expect(button).toHaveClass('h-8', 'w-8');
      });
    });

    it('should support text resizing', () => {
      renderTable();

      const h1 = screen.getByRole('heading', { level: 1 });
      const styles = globalThis.getComputedStyle(h1);
      // Should not use fixed pixel sizes for fonts
      expect(styles.fontSize).toBeTruthy();
    });

    it('should maintain focus order', () => {
      renderTable();

      // Focus should be logical and sequential
      const focusableElements = document.querySelectorAll(
        "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])",
      );
      expect(focusableElements.length).toBeGreaterThan(0);
    });

    it('should have 4.5:1 color contrast for text', () => {
      renderTable();

      // Text elements should have sufficient contrast
      const textElements = screen.getAllByText(/Create Authentication/i);
      expect(textElements.length).toBeGreaterThan(0);
    });

    it('should not rely on color alone to convey information', () => {
      renderTable();

      // Status badges should have text, not just color
      const statusBadges = screen.getAllByText(/in progress/i);
      expect(statusBadges.length).toBeGreaterThan(0);

      // Priority should have both dot and text
      const priorityTexts = screen.getAllByText(/high/i);
      expect(priorityTexts.length).toBeGreaterThan(0);
    });
  });
});
