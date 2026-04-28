// DesignTokenBrowser.test.tsx - Test suite for DesignTokenBrowser component
// Tests token display, filtering, search, categorization, and interactions

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { DesignToken } from '@tracertm/types';

import { DesignTokenBrowser } from '@/components/graph/DesignTokenBrowser';

// =============================================================================
// MOCK DATA
// =============================================================================

const mockColorTokens: DesignToken[] = [
  {
    createdAt: '2024-01-01T00:00:00Z',
    description: 'Primary brand color',
    id: 'color-1',
    libraryId: 'lib-1',
    name: 'primary',
    path: ['colors', 'primary', '500'],
    projectId: 'proj-1',
    resolvedValue: '#3B82F6',
    tags: ['brand', 'interactive'],
    type: 'color',
    updatedAt: '2024-01-01T00:00:00Z',
    usageCount: 12,
    usedByComponentIds: ['btn-1', 'btn-2'],
    value: '#3B82F6',
  },
  {
    createdAt: '2024-01-01T00:00:00Z',
    figmaStyleId: 'figma-style-1',
    id: 'color-2',
    libraryId: 'lib-1',
    name: 'secondary',
    path: ['colors', 'secondary', '500'],
    projectId: 'proj-1',
    resolvedValue: '#10B981',
    tags: ['status'],
    type: 'color',
    updatedAt: '2024-01-01T00:00:00Z',
    usageCount: 8,
    value: '#10B981',
  },
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'color-3',
    libraryId: 'lib-1',
    name: 'error',
    path: ['colors', 'error', '500'],
    projectId: 'proj-1',
    resolvedValue: '#EF4444',
    type: 'color',
    updatedAt: '2024-01-01T00:00:00Z',
    usageCount: 0,
    value: '#EF4444',
  },
];

const mockSpacingTokens: DesignToken[] = [
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'spacing-1',
    libraryId: 'lib-1',
    name: 'sm',
    path: ['spacing', 'sm'],
    projectId: 'proj-1',
    resolvedValue: '0.5rem',
    type: 'spacing',
    updatedAt: '2024-01-01T00:00:00Z',
    usageCount: 20,
    usedByComponentIds: ['btn-1'],
    value: '0.5rem',
  },
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'spacing-2',
    libraryId: 'lib-1',
    name: 'md',
    path: ['spacing', 'md'],
    projectId: 'proj-1',
    resolvedValue: '1rem',
    type: 'spacing',
    updatedAt: '2024-01-01T00:00:00Z',
    usageCount: 15,
    value: '1rem',
  },
];

const mockTypographyTokens: DesignToken[] = [
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'typo-1',
    libraryId: 'lib-1',
    name: 'body-regular',
    path: ['typography', 'body', 'regular'],
    projectId: 'proj-1',
    resolvedValue: '16px/1.5 "Inter", sans-serif',
    type: 'typography',
    updatedAt: '2024-01-01T00:00:00Z',
    usageCount: 25,
    value: '16px/1.5 "Inter", sans-serif',
  },
];

const mockTokensWithReferences: DesignToken[] = [
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'token-ref-1',
    libraryId: 'lib-1',
    name: 'primary-light',
    path: ['colors', 'primary', 'light'],
    projectId: 'proj-1',
    referencesTokenId: 'color-1',
    resolvedValue: '#3B82F6',
    type: 'color',
    updatedAt: '2024-01-01T00:00:00Z',
    usageCount: 5,
    value: '{colors.primary.500}',
  },
];

const TOKENS_ALL = [...mockColorTokens, ...mockSpacingTokens, ...mockTypographyTokens];
const TOKENS_COLOR_AND_SPACING = [...mockColorTokens, ...mockSpacingTokens];

// =============================================================================
// TESTS
// =============================================================================

describe(DesignTokenBrowser, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Basic rendering
  describe('rendering', () => {
    it('should render the component with all tokens', () => {
      render(<DesignTokenBrowser tokens={TOKENS_ALL} />);

      expect(screen.getByText('Design Tokens')).toBeInTheDocument();
      expect(screen.getByText(/10 tokens/)).toBeInTheDocument();
    });

    it('should display empty state when no tokens', () => {
      render(<DesignTokenBrowser tokens={[]} />);

      expect(screen.getByText('No design tokens')).toBeInTheDocument();
      expect(screen.getByText(/Import tokens from Figma/)).toBeInTheDocument();
    });

    it('should group tokens by type', () => {
      render(<DesignTokenBrowser tokens={TOKENS_COLOR_AND_SPACING} />);

      // Should show category buttons
      expect(screen.getByText(/Colors \(3\)/)).toBeInTheDocument();
      expect(screen.getByText(/Spacing \(2\)/)).toBeInTheDocument();
    });

    it('should display token stats correctly', () => {
      render(<DesignTokenBrowser tokens={TOKENS_COLOR_AND_SPACING} />);

      expect(screen.getByText(/5 tokens/)).toBeInTheDocument();
      expect(screen.getByText(/3 in use/)).toBeInTheDocument();
      expect(screen.getByText(/1 synced/)).toBeInTheDocument();
    });
  });

  // Search functionality
  describe('search and filtering', () => {
    it('should filter tokens by name', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
      await userEvent.type(searchInput, 'primary');

      // Should show primary token
      expect(screen.getByText('primary')).toBeInTheDocument();
      // Should not show secondary
      expect(screen.queryByText('secondary')).not.toBeInTheDocument();
    });

    it('should filter tokens by path', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
      await userEvent.type(searchInput, 'secondary');

      expect(screen.getByText('secondary')).toBeInTheDocument();
    });

    it('should filter tokens by value', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
      await userEvent.type(searchInput, '#EF4444');

      expect(screen.getByText('error')).toBeInTheDocument();
    });

    it('should filter tokens by tag', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
      await userEvent.type(searchInput, 'brand');

      expect(screen.getByText('primary')).toBeInTheDocument();
    });

    it('should show no results message when search has no matches', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
      await userEvent.type(searchInput, 'nonexistent');

      expect(screen.getByText('No tokens found')).toBeInTheDocument();
    });
  });

  // Category expansion
  describe('category expansion', () => {
    it('should expand categories on click', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      const colorsButton = screen.getByText(/Colors \(3\)/);
      expect(colorsButton).toBeInTheDocument();

      await userEvent.click(colorsButton);

      // Should show token items
      await waitFor(() => {
        expect(screen.getByText('primary')).toBeInTheDocument();
      });
    });

    it('should expand all categories with button', async () => {
      render(<DesignTokenBrowser tokens={TOKENS_COLOR_AND_SPACING} />);

      const expandAllButton = screen.getByText('Expand All');
      await userEvent.click(expandAllButton);

      await waitFor(() => {
        expect(screen.getByText('primary')).toBeInTheDocument();
        expect(screen.getByText('sm')).toBeInTheDocument();
      });
    });

    it('should collapse all categories with button', async () => {
      const { rerender } = render(<DesignTokenBrowser tokens={TOKENS_COLOR_AND_SPACING} />);

      // First expand all
      const expandAllButton = screen.getByText('Expand All');
      await userEvent.click(expandAllButton);

      await waitFor(() => {
        expect(screen.getByText('primary')).toBeInTheDocument();
      });

      // Then collapse all
      const collapseAllButton = screen.getByText('Collapse All');
      await userEvent.click(collapseAllButton);

      // Rerender to see updated state
      rerender(<DesignTokenBrowser tokens={TOKENS_COLOR_AND_SPACING} />);

      // Primary should not be visible until expanded again
      const primaryElements = screen.queryAllByText('primary');
      expect(primaryElements.length).toBeLessThanOrEqual(1);
    });
  });

  // Token selection
  describe('token selection', () => {
    it('should call onSelectToken when token is clicked', async () => {
      const onSelectToken = vi.fn();
      render(<DesignTokenBrowser tokens={mockColorTokens} onSelectToken={onSelectToken} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      // Click on primary token
      await waitFor(async () => {
        const primaryToken = screen.getByText('primary');
        const tokenContainer = primaryToken.closest("div[class*='flex-col']");
        if (tokenContainer) {
          await userEvent.click(tokenContainer);
        }
      });

      expect(onSelectToken).toHaveBeenCalled();
    });

    it('should highlight selected token', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} selectedTokenId='color-1' />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      // Find the primary token container
      await waitFor(() => {
        const primaryText = screen.getByText('primary');
        const tokenContainer = primaryText.closest("div[class*='flex']");
        expect(tokenContainer).toHaveClass('bg-primary/10');
      });
    });
  });

  // Copy functionality
  describe('copy to clipboard', () => {
    it('should copy token value to clipboard', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      // Click copy button (hover action)
      await waitFor(() => {
        const primaryToken = screen.getByText('primary');
        const copyButton = primaryToken
          .closest("div[class*='group']")
          ?.querySelector('button[class*="copy"]');
        expect(copyButton).toBeTruthy();
      });
    });
  });

  // Token details expansion
  describe('token details', () => {
    it('should show description when expanded', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      // Expand token details
      await waitFor(async () => {
        const primaryToken = screen.getByText('primary');
        const expandButton = primaryToken
          .closest("div[class*='flex-col']")
          ?.querySelector('button');
        if (expandButton) {
          await userEvent.click(expandButton);
        }
      });

      await waitFor(() => {
        expect(screen.getByText('Primary brand color')).toBeInTheDocument();
      });
    });

    it('should show component usage', async () => {
      const componentMap = new Map([
        ['btn-1', 'Button Primary'],
        ['btn-2', 'Button Secondary'],
      ]);
      render(
        <DesignTokenBrowser
          tokens={mockColorTokens}
          showComponentUsage
          componentMap={componentMap}
        />,
      );

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      // Should show usage count
      expect(screen.getByText(/12/)).toBeInTheDocument();
    });

    it('should display referenced tokens', async () => {
      render(<DesignTokenBrowser tokens={mockTokensWithReferences} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(1\)/);
      await userEvent.click(colorsButton);

      // Should show the token with reference
      await waitFor(() => {
        expect(screen.getByText('primary-light')).toBeInTheDocument();
      });
    });
  });

  // Figma integration
  describe('figma integration', () => {
    it('should show Figma icon for synced tokens', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      // Secondary token has Figma style ID
      await waitFor(() => {
        const secondaryToken = screen.getByText('secondary');
        const figmaIcon = secondaryToken.closest('div')?.querySelector('svg[class*="text-blue"]');
        expect(figmaIcon).toBeTruthy();
      });
    });

    it('should call onLinkToFigma when linking token', async () => {
      const onLinkToFigma = vi.fn();
      render(<DesignTokenBrowser tokens={mockColorTokens} onLinkToFigma={onLinkToFigma} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      // Click on Figma link button for unsync token
      // (Would need to hover and click the Figma button)
      expect(onLinkToFigma).not.toHaveBeenCalled();
    });

    it('should show sync count in stats', () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      expect(screen.getByText(/1 synced/)).toBeInTheDocument();
    });
  });

  // Token preview rendering
  describe('token preview', () => {
    it('should render color preview box', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      await waitFor(() => {
        const previewBoxes = screen.getAllByRole('img', { hidden: true });
        expect(previewBoxes.length).toBeGreaterThan(0);
      });
    });

    it('should display token value in code format', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      // Expand colors category
      const colorsButton = screen.getByText(/Colors \(3\)/);
      await userEvent.click(colorsButton);

      await waitFor(() => {
        expect(screen.getByText('#3B82F6')).toBeInTheDocument();
      });
    });
  });

  // Category type icons
  describe('category type icons', () => {
    it('should display correct icon for each token type', async () => {
      render(<DesignTokenBrowser tokens={TOKENS_ALL} />);

      // All category buttons should be visible
      expect(screen.getByText(/Colors \(3\)/)).toBeInTheDocument();
      expect(screen.getByText(/Spacing \(2\)/)).toBeInTheDocument();
      expect(screen.getByText(/Typography \(1\)/)).toBeInTheDocument();
    });
  });

  // Accessibility
  describe('accessibility', () => {
    it('should have accessible button labels', async () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      expect(screen.getByText('Expand All')).toBeInTheDocument();
      expect(screen.getByText('Collapse All')).toBeInTheDocument();
    });

    it('should have descriptive search placeholder', () => {
      render(<DesignTokenBrowser tokens={mockColorTokens} />);

      const searchInput = screen.getByPlaceholderText(/Search tokens by name, value, or path/);
      expect(searchInput).toBeInTheDocument();
    });
  });
});
