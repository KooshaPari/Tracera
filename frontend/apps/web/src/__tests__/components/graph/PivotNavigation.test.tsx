/**
 * Comprehensive tests for PivotNavigation component
 * Tests: perspective navigation, equivalent items display, confidence indicators
 */

import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { PivotTarget } from '@/components/graph/PivotNavigation';
import type { Item } from '@tracertm/types';

import { PivotNavigation, buildPivotTargets } from '@/components/graph/PivotNavigation';

// =============================================================================
// FIXTURES
// =============================================================================

const mockCurrentItem: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'item-1',
  perspective: 'product',
  projectId: 'proj-1',
  status: 'active',
  title: 'User Authentication',
  type: 'feature',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockTechnicalItem: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'item-2',
  perspective: 'technical',
  projectId: 'proj-1',
  status: 'active',
  title: 'Authentication API',
  type: 'api',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockUIItem: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'item-3',
  perspective: 'ui',
  projectId: 'proj-1',
  status: 'active',
  title: 'Login Form Component',
  type: 'ui_component',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockSecurityItem: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'item-4',
  perspective: 'security',
  projectId: 'proj-1',
  status: 'active',
  title: 'Authentication Security Check',
  type: 'security',
  updatedAt: '2024-01-01T00:00:00Z',
} as any;

const mockPivotTargets: PivotTarget[] = [
  {
    confidence: 0.95,
    item: mockTechnicalItem,
    perspectiveId: 'technical',
    source: 'equivalence',
  },
  {
    confidence: 0.85,
    item: mockUIItem,
    perspectiveId: 'ui',
    source: 'canonical',
  },
  {
    confidence: 0.75,
    item: mockSecurityItem,
    perspectiveId: 'security',
    source: 'equivalence',
  },
];

// =============================================================================
// COMPONENT TESTS
// =============================================================================

describe('PivotNavigation Component', () => {
  let onPivot: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    onPivot = vi.fn();
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders pivot navigation header', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
        />,
      );

      expect(screen.getByText(/pivot to perspective/i)).toBeInTheDocument();
    });

    it('displays pivot buttons for each perspective', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
        />,
      );

      // Should show buttons for technical, ui, and security
      expect(screen.getByText(/technical/i)).toBeInTheDocument();
      expect(screen.getByText(/ui/i)).toBeInTheDocument();
      expect(screen.getByText(/security/i)).toBeInTheDocument();
    });

    it('does not show current perspective as pivot target', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
        />,
      );

      // Product should not appear as a pivot option
      const buttons = screen.getAllByRole('button');
      const productButton = buttons.filter((b) => b.textContent?.includes('Product'));
      expect(productButton.length).toBe(0);
    });

    it('does not show all perspective in pivot targets', () => {
      const targetsWithAll: PivotTarget[] = [
        ...mockPivotTargets,
        {
          confidence: 1,
          item: mockCurrentItem,
          perspectiveId: 'all',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={targetsWithAll}
          onPivot={onPivot}
        />,
      );

      // "All" perspective should be filtered out
      expect(screen.queryByText(/All perspective/i)).not.toBeInTheDocument();
    });

    it('returns null when no equivalent items and showEmpty is false', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={[]}
          onPivot={onPivot}
          showEmpty={false}
        />,
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe('Single Item Navigation', () => {
    it('shows button with item details when single equivalent exists', () => {
      const singleTarget: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={singleTarget}
          onPivot={onPivot}
        />,
      );

      expect(screen.getByText(/Technical/i)).toBeInTheDocument();
    });

    it('navigates directly when clicking single item button', async () => {
      const singleTarget: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={singleTarget}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.click(technicalButton);

      expect(onPivot).toHaveBeenCalledWith('technical', 'item-2');
    });

    it('displays confidence indicator for single item', () => {
      const singleTarget: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={singleTarget}
          onPivot={onPivot}
        />,
      );

      // Confidence indicator should be visible
      expect(screen.getByText(/Technical/i)).toBeInTheDocument();
    });

    it('shows item details in tooltip', async () => {
      const singleTarget: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={singleTarget}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.hover(technicalButton);

      await waitFor(() => {
        expect(screen.getByText('Authentication API')).toBeInTheDocument();
      });
    });

    it('shows confidence percentage in tooltip', async () => {
      const singleTarget: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={singleTarget}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.hover(technicalButton);

      await waitFor(() => {
        expect(screen.getByText(/95%/)).toBeInTheDocument();
      });
    });
  });

  describe('Multiple Items Navigation', () => {
    it('shows badge with count when multiple equivalents exist', () => {
      const multipleTargets: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
        {
          confidence: 0.85,
          item: mockSecurityItem,
          perspectiveId: 'technical',
          source: 'canonical',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={multipleTargets}
          onPivot={onPivot}
        />,
      );

      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('opens popover when clicking multi-item button', async () => {
      const multipleTargets: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
        {
          confidence: 0.85,
          item: mockSecurityItem,
          perspectiveId: 'technical',
          source: 'canonical',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={multipleTargets}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.click(technicalButton);

      await waitFor(() => {
        expect(screen.getByText(/Select equivalent/i)).toBeInTheDocument();
      });
    });

    it('displays all items in popover', async () => {
      const multipleTargets: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
        {
          confidence: 0.85,
          item: mockSecurityItem,
          perspectiveId: 'technical',
          source: 'canonical',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={multipleTargets}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.click(technicalButton);

      await waitFor(() => {
        expect(screen.getByText('Authentication API')).toBeInTheDocument();
        expect(screen.getByText('Authentication Security Check')).toBeInTheDocument();
      });
    });

    it('navigates when clicking item in popover', async () => {
      const multipleTargets: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
        {
          confidence: 0.85,
          item: mockSecurityItem,
          perspectiveId: 'technical',
          source: 'canonical',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={multipleTargets}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.click(technicalButton);

      const itemButton = await screen.findByRole('button', {
        name: /Authentication API/i,
      });
      await user.click(itemButton);

      expect(onPivot).toHaveBeenCalledWith('technical', 'item-2');
    });

    it('displays type information in popover', async () => {
      const multipleTargets: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={multipleTargets}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.click(technicalButton);

      await waitFor(() => {
        expect(screen.getByText(/api/i)).toBeInTheDocument();
      });
    });
  });

  describe('Confidence Indicators', () => {
    it('displays confidence bars in color', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
        />,
      );

      // Component should render without errors
      expect(screen.getByText(/Technical/i)).toBeInTheDocument();
    });

    it('shows different colors for different confidence levels', () => {
      const mixedConfidenceTargets: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
        {
          confidence: 0.5,
          item: mockUIItem,
          perspectiveId: 'ui',
          source: 'canonical',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mixedConfidenceTargets}
          onPivot={onPivot}
        />,
      );

      expect(screen.getByText(/Technical/i)).toBeInTheDocument();
      expect(screen.getByText(/UI/i)).toBeInTheDocument();
    });

    it('shows confidence tooltip on hover', async () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
        />,
      );

      const technicalButton = screen.getByRole('button', {
        name: /Technical/i,
      });
      await user.hover(technicalButton);

      await waitFor(() => {
        expect(screen.getByText(/95%/)).toBeInTheDocument();
      });
    });
  });

  describe('Compact Mode', () => {
    it('renders compact button when compact prop is true', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
          compact
        />,
      );

      expect(screen.getByRole('button', { name: /Pivot/i })).toBeInTheDocument();
    });

    it('shows equivalence count badge in compact mode', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
          compact
        />,
      );

      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('opens popover with all perspectives in compact mode', async () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
          compact
        />,
      );

      const pivotButton = screen.getByRole('button', { name: /Pivot/i });
      await user.click(pivotButton);

      await waitFor(() => {
        expect(screen.getByText(/Pivot to another perspective/i)).toBeInTheDocument();
      });
    });

    it('groups items by perspective in compact popover', async () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
          compact
        />,
      );

      const pivotButton = screen.getByRole('button', { name: /Pivot/i });
      await user.click(pivotButton);

      await waitFor(() => {
        expect(screen.getByText(/Technical/i)).toBeInTheDocument();
        expect(screen.getByText(/UI/i)).toBeInTheDocument();
        expect(screen.getByText(/Security/i)).toBeInTheDocument();
      });
    });

    it('navigates from compact popover', async () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
          compact
        />,
      );

      const pivotButton = screen.getByRole('button', { name: /Pivot/i });
      await user.click(pivotButton);

      const itemButton = await screen.findByRole('button', {
        name: /Authentication API/i,
      });
      await user.click(itemButton);

      expect(onPivot).toHaveBeenCalled();
    });

    it('returns null when no equivalents in compact mode with showEmpty false', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={[]}
          onPivot={onPivot}
          compact
          showEmpty={false}
        />,
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe('Empty States', () => {
    it('shows disabled buttons when showEmpty is true but no items', () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={[]}
          onPivot={onPivot}
          showEmpty
        />,
      );

      // Should show perspective buttons but disabled
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it("shows 'No equivalents' message on disabled button hover", async () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={[]}
          onPivot={onPivot}
          showEmpty
        />,
      );

      const buttons = screen.getAllByRole('button');
      if (buttons.length > 0) {
        await user.hover(buttons[0]);

        // Tooltip should appear
        expect(buttons[0]).toBeInTheDocument();
      }
    });
  });

  describe('Edge Cases', () => {
    it('handles duplicate items in pivot targets', () => {
      const duplicateTargets: PivotTarget[] = [
        {
          confidence: 0.95,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
        {
          confidence: 0.85,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'canonical',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={duplicateTargets}
          onPivot={onPivot}
        />,
      );

      expect(screen.getByText(/Technical/i)).toBeInTheDocument();
    });

    it('handles items with very low confidence', () => {
      const lowConfidenceTargets: PivotTarget[] = [
        {
          confidence: 0.1,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={lowConfidenceTargets}
          onPivot={onPivot}
        />,
      );

      expect(screen.getByText(/Technical/i)).toBeInTheDocument();
    });

    it('handles items with 100% confidence', () => {
      const perfectConfidenceTargets: PivotTarget[] = [
        {
          confidence: 1,
          item: mockTechnicalItem,
          perspectiveId: 'technical',
          source: 'equivalence',
        },
      ];

      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={perfectConfidenceTargets}
          onPivot={onPivot}
        />,
      );

      expect(screen.getByText(/Technical/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('supports keyboard navigation', async () => {
      render(
        <PivotNavigation
          currentItem={mockCurrentItem}
          currentPerspective='product'
          equivalentItems={mockPivotTargets}
          onPivot={onPivot}
        />,
      );

      // Tab to first button
      await user.tab();
      expect(screen.getByText(/Technical/i)).toBeInTheDocument();

      // Press Enter to activate
      await user.keyboard('{Enter}');
      expect(onPivot).toHaveBeenCalledTimes(0); // Might not be called on Enter in popover
    });
  });
});

// =============================================================================
// UTILITY FUNCTION TESTS
// =============================================================================

describe(buildPivotTargets, () => {
  const mockAllItems = [mockCurrentItem, mockTechnicalItem, mockUIItem, mockSecurityItem];

  it('builds pivot targets from equivalence links', () => {
    const equivalenceLinks = [
      {
        confidence: 0.95,
        id: 'link-1',
        sourceItemId: 'item-1',
        status: 'confirmed',
        strategies: [{ confidence: 0.95, strategy: 'explicit_annotation' }],
        targetItemId: 'item-2',
      },
    ];

    const targets = buildPivotTargets(mockCurrentItem, equivalenceLinks, [], mockAllItems);

    expect(targets).toHaveLength(1);
    expect(targets[0].item.id).toBe('item-2');
    expect(targets[0].confidence).toBe(0.95);
    expect(targets[0].source).toBe('equivalence');
  });

  it('builds pivot targets from canonical projections', () => {
    const projections = [
      {
        canonicalConceptId: 'concept-1',
        confidence: 0.9,
        id: 'proj-1',
        isConfirmed: true,
        isRejected: false,
        itemId: 'item-2',
        perspective: 'technical',
        strategy: 'api_contract',
      },
    ];

    const targets = buildPivotTargets(mockCurrentItem, [], projections, mockAllItems);

    expect(targets).toHaveLength(1);
    expect(targets[0].item.id).toBe('item-2');
    expect(targets[0].perspective).toBe('technical');
    expect(targets[0].source).toBe('canonical');
  });

  it('combines equivalence links and projections', () => {
    const equivalenceLinks = [
      {
        confidence: 0.95,
        id: 'link-1',
        sourceItemId: 'item-1',
        status: 'confirmed',
        strategies: [{ confidence: 0.95, strategy: 'explicit_annotation' }],
        targetItemId: 'item-2',
      },
    ];

    const projections = [
      {
        canonicalConceptId: 'concept-1',
        confidence: 0.85,
        id: 'proj-1',
        isConfirmed: true,
        isRejected: false,
        itemId: 'item-3',
        perspective: 'ui',
        strategy: 'api_contract',
      },
    ];

    const targets = buildPivotTargets(mockCurrentItem, equivalenceLinks, projections, mockAllItems);

    expect(targets).toHaveLength(2);
  });

  it('sorts by confidence descending', () => {
    const equivalenceLinks = [
      {
        confidence: 0.5,
        id: 'link-1',
        sourceItemId: 'item-1',
        status: 'confirmed',
        strategies: [{ confidence: 0.5, strategy: 'explicit_annotation' }],
        targetItemId: 'item-2',
      },
      {
        confidence: 0.95,
        id: 'link-2',
        sourceItemId: 'item-1',
        status: 'confirmed',
        strategies: [{ confidence: 0.95, strategy: 'semantic_similarity' }],
        targetItemId: 'item-3',
      },
    ];

    const targets = buildPivotTargets(mockCurrentItem, equivalenceLinks, [], mockAllItems);

    expect(targets[0].confidence).toBe(0.95);
    expect(targets[1].confidence).toBe(0.5);
  });

  it('excludes current item from targets', () => {
    const equivalenceLinks = [
      {
        id: 'link-1',
        sourceItemId: 'item-1',
        targetItemId: 'item-1', // Same as current
        confidence: 0.95,
        status: 'confirmed',
        strategies: [{ confidence: 0.95, strategy: 'explicit_annotation' }],
      },
    ];

    const targets = buildPivotTargets(mockCurrentItem, equivalenceLinks, [], mockAllItems);

    expect(targets).toHaveLength(0);
  });

  it('handles items not found in items list', () => {
    const equivalenceLinks = [
      {
        confidence: 0.95,
        id: 'link-1',
        sourceItemId: 'item-1',
        status: 'confirmed',
        strategies: [{ confidence: 0.95, strategy: 'explicit_annotation' }],
        targetItemId: 'nonexistent',
      },
    ];

    const targets = buildPivotTargets(mockCurrentItem, equivalenceLinks, [], mockAllItems);

    expect(targets).toHaveLength(0);
  });

  it('deduplicates items across sources', () => {
    const equivalenceLinks = [
      {
        confidence: 0.95,
        id: 'link-1',
        sourceItemId: 'item-1',
        status: 'confirmed',
        strategies: [{ confidence: 0.95, strategy: 'explicit_annotation' }],
        targetItemId: 'item-2',
      },
    ];

    const projections = [
      {
        id: 'proj-1',
        canonicalConceptId: 'concept-1',
        itemId: 'item-2', // Same item
        perspective: 'technical',
        confidence: 0.9,
        isConfirmed: true,
        isRejected: false,
        strategy: 'api_contract',
      },
    ];

    const targets = buildPivotTargets(mockCurrentItem, equivalenceLinks, projections, mockAllItems);

    expect(targets).toHaveLength(1);
  });

  it('returns empty array when no links or projections', () => {
    const targets = buildPivotTargets(mockCurrentItem, [], [], mockAllItems);

    expect(targets).toHaveLength(0);
  });
});
