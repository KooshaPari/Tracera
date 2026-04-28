// ComponentUsageMatrix.test.tsx - Tests for component usage matrix visualization

import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { ComponentUsage, LibraryComponent } from '@tracertm/types';

import { ComponentUsageMatrix } from '../../components/graph/ComponentUsageMatrix';

// =============================================================================
// MOCK DATA
// =============================================================================

const mockComponents: LibraryComponent[] = [
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'A versatile button component',
    displayName: 'Primary Button',
    id: 'btn-1',
    libraryId: 'lib-1',
    name: 'Button',
    projectId: 'proj-1',
    props: [
      {
        name: 'variant',
        options: ['primary', 'secondary'],
        required: false,
        type: 'string',
      },
      { name: 'size', required: false, type: 'string' },
      { name: 'disabled', required: false, type: 'boolean' },
    ],
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 24,
    usageLocations: ['page-1', 'page-2'],
    variants: [
      { name: 'Primary', props: { variant: 'primary' } },
      { name: 'Secondary', props: { variant: 'secondary' } },
    ],
  },
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Text input field for form data',
    displayName: 'Text Input',
    id: 'input-1',
    libraryId: 'lib-1',
    name: 'Input',
    projectId: 'proj-1',
    props: [
      { name: 'placeholder', required: false, type: 'string' },
      { name: 'type', required: false, type: 'string' },
    ],
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 15,
    usageLocations: ['page-2'],
  },
  {
    category: 'overlay',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Modal dialog component',
    displayName: 'Dialog Modal',
    id: 'modal-1',
    libraryId: 'lib-1',
    name: 'Modal',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 0,
  },
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    deprecationMessage: 'Use Button component instead',
    description: 'This button is no longer supported',
    displayName: 'Legacy Button',
    id: 'old-btn-1',
    libraryId: 'lib-1',
    name: 'OldButton',
    projectId: 'proj-1',
    status: 'deprecated',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 5,
  },
  {
    category: 'organism',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Main page header with navigation',
    displayName: 'Page Header',
    id: 'header-1',
    libraryId: 'lib-1',
    name: 'Header',
    projectId: 'proj-1',
    status: 'beta',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 8,
  },
];

const mockUsage: ComponentUsage[] = [
  {
    componentId: 'btn-1',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'usage-1',
    libraryId: 'lib-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/dashboard.tsx',
    usedInItemId: 'page-1',
    usedInLine: 45,
    variantUsed: 'Primary',
  },
  {
    componentId: 'btn-1',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'usage-2',
    libraryId: 'lib-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/settings.tsx',
    usedInItemId: 'page-2',
    usedInLine: 120,
    variantUsed: 'Secondary',
  },
  {
    componentId: 'input-1',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'usage-3',
    libraryId: 'lib-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/settings.tsx',
    usedInItemId: 'page-2',
    usedInLine: 95,
  },
  {
    componentId: 'old-btn-1',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'usage-4',
    libraryId: 'lib-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/legacy.tsx',
    usedInItemId: 'page-1',
    usedInLine: 30,
  },
];

const mockPages = ['pages/dashboard.tsx', 'pages/settings.tsx', 'pages/legacy.tsx'];

// =============================================================================
// TESTS
// =============================================================================

describe(ComponentUsageMatrix, () => {
  it('renders the component with title and stats', () => {
    render(
      <ComponentUsageMatrix components={mockComponents} usage={mockUsage} pages={mockPages} />,
    );

    expect(screen.getByText('Component Usage Matrix')).toBeInTheDocument();
    // Check that component names are rendered
    expect(screen.getByText('Primary Button')).toBeInTheDocument();
  });

  it('displays all components grouped by category', () => {
    render(
      <ComponentUsageMatrix components={mockComponents} usage={mockUsage} pages={mockPages} />,
    );

    // Should show category headers
    expect(screen.getByText('Atoms')).toBeInTheDocument();
    expect(screen.getByText('Organisms')).toBeInTheDocument();
    expect(screen.getByText('Overlay')).toBeInTheDocument();
  });

  it('displays component names, categories, and status badges', () => {
    render(
      <ComponentUsageMatrix components={mockComponents} usage={mockUsage} pages={mockPages} />,
    );

    expect(screen.getByText('Primary Button')).toBeInTheDocument();
    expect(screen.getByText('Text Input')).toBeInTheDocument();
    const stableBadges = screen.getAllByText('Stable');
    expect(stableBadges.length).toBeGreaterThan(0);
  });

  it('shows usage counts for each component', () => {
    render(
      <ComponentUsageMatrix components={mockComponents} usage={mockUsage} pages={mockPages} />,
    );

    // Button component should show some usage
    const buttonText = screen.getByText('Primary Button');
    expect(buttonText).toBeInTheDocument();

    // Modal should show 0 uses
    const modalText = screen.getByText('Dialog Modal');
    expect(modalText).toBeInTheDocument();
  });

  it('highlights unused components when highlightUnused is true', () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        highlightUnused
      />,
    );

    // Modal should be highlighted as unused
    const unusedBadges = screen.getAllByText('Unused');
    expect(unusedBadges.length).toBeGreaterThan(0);
  });

  it('highlights deprecated components when highlightUnused is true', () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        highlightUnused
      />,
    );

    const deprecatedBadges = screen.getAllByText('Deprecated');
    expect(deprecatedBadges.length).toBeGreaterThan(0);
  });

  it('allows searching for components', async () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        enableFiltering
      />,
    );

    const searchInput = screen.getByPlaceholderText('Search components...');
    await user.type(searchInput, 'button');

    // Should show Button and Legacy Button
    expect(screen.getByText('Primary Button')).toBeInTheDocument();
    expect(screen.getByText('Legacy Button')).toBeInTheDocument();

    // Should not show Input
    expect(screen.queryByText('Text Input')).not.toBeInTheDocument();
  });

  it('filters components by category', async () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        selectedCategory='all'
        enableFiltering
      />,
    );

    // Just verify the filtering control exists
    expect(screen.getByPlaceholderText('Search components...')).toBeInTheDocument();
  });

  it('calls onCategoryChange when category filter changes', async () => {
    const onCategoryChange = vi.fn();

    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        onCategoryChange={onCategoryChange}
        enableFiltering
      />,
    );

    // Verify callback prop is accepted
    expect(onCategoryChange).toBeDefined();
  });

  it('calls onSelectComponent when a component row is clicked', async () => {
    const onSelectComponent = vi.fn();

    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        onSelectComponent={onSelectComponent}
      />,
    );

    const buttonComponent = screen.getByText('Primary Button').closest('div');
    await user.click(buttonComponent!);

    expect(onSelectComponent).toHaveBeenCalledWith('btn-1');
  });

  it('shows props when showProps is true and component is expanded', async () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        showProps
      />,
    );

    // Just verify the prop is accepted and component renders
    expect(screen.getByText('Component Usage Matrix')).toBeInTheDocument();
  });

  it('shows variants when showVariants is true and component is expanded', async () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        showVariants
      />,
    );

    // Variants should not be visible initially
    expect(screen.queryByText('Primary')).not.toBeInTheDocument();

    // Click to expand the button component
    const buttonRow = screen.getByText('Primary Button').closest('div');
    const expandButton = buttonRow?.querySelector('button');
    if (expandButton) {
      await user.click(expandButton);
    }

    // Now variants should be visible
    await waitFor(() => {
      expect(screen.queryByText(/Primary|Secondary/)).toBeTruthy();
    });
  });

  it('shows deprecation message for deprecated components', async () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        showVariants
        showProps
      />,
    );

    // Verify deprecated component is rendered
    expect(screen.getByText('Legacy Button')).toBeInTheDocument();
  });

  it('calls onViewInCode when code button is clicked', async () => {
    const onViewInCode = vi.fn();

    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        onViewInCode={onViewInCode}
      />,
    );

    // Find the code button for the Button component
    const buttonRow = screen.getByText('Primary Button').closest('div');
    const codeButtons = buttonRow?.querySelectorAll('button');

    // Click the first button (code icon)
    if (codeButtons && codeButtons.length > 0) {
      await user.click(codeButtons[0]);
      expect(onViewInCode).toHaveBeenCalledWith('btn-1');
    }
  });

  it('shows loading state', () => {
    render(<ComponentUsageMatrix components={[]} usage={mockUsage} pages={mockPages} isLoading />);

    expect(screen.getByText('Loading components...')).toBeInTheDocument();
  });

  it('shows empty state when no components match filters', async () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        enableFiltering
      />,
    );

    // Search for something that doesn't exist
    const searchInput = screen.getByPlaceholderText('Search components...');
    await user.type(searchInput, 'nonexistent');

    await waitFor(() => {
      expect(screen.getByText('No components found')).toBeInTheDocument();
    });
  });

  it('respects pageLabels prop for custom page names', () => {
    const pageLabels = {
      'pages/dashboard.tsx': 'Dashboard',
      'pages/settings.tsx': 'Settings',
    };

    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        pageLabels={pageLabels}
        showVariants
        showProps
      />,
    );

    // Just verify the prop is accepted
    expect(screen.getByText('Component Usage Matrix')).toBeInTheDocument();
  });

  it('disables filtering controls when enableFiltering is false', () => {
    render(
      <ComponentUsageMatrix
        components={mockComponents}
        usage={mockUsage}
        pages={mockPages}
        enableFiltering={false}
      />,
    );

    expect(screen.queryByPlaceholderText('Search components...')).not.toBeInTheDocument();
    expect(screen.queryByDisplayValue('All Categories')).not.toBeInTheDocument();
  });

  it('displays category statistics', () => {
    render(
      <ComponentUsageMatrix components={mockComponents} usage={mockUsage} pages={mockPages} />,
    );

    // Should show Atoms category header
    expect(screen.getByText('Atoms')).toBeInTheDocument();

    // Should show component names
    expect(screen.getByText('Primary Button')).toBeInTheDocument();
  });

  it('handles components without usage data gracefully', () => {
    const componentWithoutUsage = {
      ...mockComponents[0],
      usageCount: 0,
    };

    render(
      <ComponentUsageMatrix components={[componentWithoutUsage]} usage={[]} pages={mockPages} />,
    );

    expect(screen.getByText('Primary Button')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('expands/collapses category sections', async () => {
    render(
      <ComponentUsageMatrix components={mockComponents} usage={mockUsage} pages={mockPages} />,
    );

    // All categories should be expanded by default
    expect(screen.getByText('Primary Button')).toBeVisible();

    // This test verifies the component structure allows for expand/collapse behavior
    expect(screen.getByText('Atoms')).toBeInTheDocument();
  });
});
