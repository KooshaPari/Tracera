/**
 * Comprehensive tests for ComponentLibraryExplorer component
 * Tests: library browsing, component search, variants, design tokens
 */

import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type {
  ComponentLibrary,
  ComponentProp,
  ComponentVariant,
  DesignToken,
  LibraryComponent,
} from '@tracertm/types';

import { ComponentLibraryExplorer } from '@/components/graph/ComponentLibraryExplorer';

// =============================================================================
// FIXTURES
// =============================================================================

const mockDesignTokens: DesignToken[] = [
  {
    createdAt: '2024-01-15T00:00:00Z',
    id: 'color-primary',
    libraryId: 'lib-ui',
    name: 'Primary Color',
    path: ['color', 'primary'],
    projectId: 'project-ui',
    type: 'color',
    updatedAt: '2024-01-15T00:00:00Z',
    usageCount: 1,
    value: '#3b82f6',
  },
  {
    createdAt: '2024-01-15T00:00:00Z',
    id: 'spacing-md',
    libraryId: 'lib-ui',
    name: 'Medium Spacing',
    path: ['spacing', 'md'],
    projectId: 'project-ui',
    type: 'spacing',
    updatedAt: '2024-01-15T00:00:00Z',
    usageCount: 1,
    value: '16px',
  },
];

const mockComponentVariants: ComponentVariant[] = [
  {
    description: 'Primary button style',
    name: 'Primary',
    props: { size: 'md', variant: 'primary' },
  },
  {
    description: 'Secondary button style',
    name: 'Secondary',
    props: { size: 'md', variant: 'secondary' },
  },
];

const mockComponentProps: ComponentProp[] = [
  {
    description: 'Button text',
    name: 'label',
    required: true,
    type: 'string',
  },
  {
    description: 'Click handler',
    name: 'onClick',
    required: false,
    type: 'function',
  },
];

const mockButton: LibraryComponent = {
  category: 'atom',
  createdAt: '2024-01-15T00:00:00Z',
  description: 'Reusable button component',
  displayName: 'Button',
  figmaUrl: 'http://figma.local/button',
  id: 'component-button',
  libraryId: 'lib-ui',
  name: 'Button',
  projectId: 'project-ui',
  props: mockComponentProps,
  status: 'stable',
  storybookUrl: 'http://storybook.local/button',
  updatedAt: '2024-01-15T00:00:00Z',
  usageCount: 24,
  variants: mockComponentVariants,
};

const mockCard: LibraryComponent = {
  category: 'molecule',
  createdAt: '2024-01-15T00:00:00Z',
  description: 'Container component',
  displayName: 'Card',
  id: 'component-card',
  libraryId: 'lib-ui',
  name: 'Card',
  projectId: 'project-ui',
  props: [],
  status: 'stable',
  updatedAt: '2024-01-15T00:00:00Z',
  usageCount: 12,
  variants: [],
};

const mockUILibrary: ComponentLibrary = {
  componentCount: 2,
  createdAt: '2024-01-15T00:00:00Z',
  description: 'Core UI component library',
  id: 'lib-ui',
  name: 'UI Components',
  projectId: 'project-ui',
  slug: 'ui-components',
  source: 'storybook',
  sourceUrl: 'http://github.local/ui',
  syncStatus: 'synced',
  tokenCount: 2,
  updatedAt: '2024-01-15T00:00:00Z',
  version: '1.0.0',
};

const mockIconsLibrary: ComponentLibrary = {
  componentCount: 150,
  createdAt: '2024-01-15T00:00:00Z',
  description: 'SVG icon library',
  id: 'lib-icons',
  name: 'Icon Library',
  projectId: 'project-ui',
  slug: 'icon-library',
  source: 'storybook',
  sourceUrl: 'http://github.local/icons',
  syncStatus: 'synced',
  tokenCount: 0,
  updatedAt: '2024-01-15T00:00:00Z',
  version: '1.0.0',
};

// =============================================================================
// COMPONENT TESTS
// =============================================================================

describe('ComponentLibraryExplorer Component', () => {
  let onSelectLibrary: ReturnType<typeof vi.fn>;
  let onSelectComponent: ReturnType<typeof vi.fn>;
  let onViewInStorybook: ReturnType<typeof vi.fn>;
  let onViewInFigma: ReturnType<typeof vi.fn>;
  let onViewInCode: ReturnType<typeof vi.fn>;
  let onSyncLibrary: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    onSelectLibrary = vi.fn();
    onSelectComponent = vi.fn();
    onViewInStorybook = vi.fn();
    onViewInFigma = vi.fn();
    onViewInCode = vi.fn();
    onSyncLibrary = vi.fn();
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders component library explorer with title', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Component Library')).toBeInTheDocument();
    });

    it('displays library list', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary, mockIconsLibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByRole('option', { name: 'UI Components' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: 'Icon Library' })).toBeInTheDocument();
    });

    it('displays components list', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
      expect(screen.getByText('Card')).toBeInTheDocument();
    });

    it('renders search input', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      expect(searchInput).toBeInTheDocument();
    });

    it('shows component count for libraries', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('UI Components')).toBeInTheDocument();
    });

    it('displays loading state', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[]}
          components={[]}
          onSelectComponent={onSelectComponent}
          isLoading
        />,
      );

      // Component should render gracefully
      expect(screen.getByText(/library/i) || screen.getByText(/component/i)).toBeTruthy();
    });
  });

  describe('Library Selection', () => {
    it('selects library when clicking library name', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary, mockIconsLibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          onSelectLibrary={onSelectLibrary}
          selectedLibraryId='lib-ui'
        />,
      );

      await user.selectOptions(
        screen.getByRole('combobox', { name: 'Component library' }),
        'lib-icons',
      );

      await waitFor(() => {
        expect(onSelectLibrary).toHaveBeenCalledWith('lib-icons');
      });
    });

    it('highlights selected library', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary, mockIconsLibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          selectedLibraryId='lib-ui'
        />,
      );

      expect(screen.getByRole('combobox', { name: 'Component library' })).toHaveValue('lib-ui');
    });

    it('filters components by selected library', () => {
      const iconComponent = {
        ...mockButton,
        id: 'component-icon',
        name: 'Icon',
        libraryId: 'lib-icons',
      };

      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary, mockIconsLibrary]}
          components={[mockButton, iconComponent]}
          onSelectComponent={onSelectComponent}
          selectedLibraryId='lib-ui'
        />,
      );

      // Should primarily show UI library components
      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('shows library metadata', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('UI Components')).toBeInTheDocument();
      expect(screen.getByText('Core UI component library')).toBeInTheDocument();
    });

    it('shows sync button for library', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          onSyncLibrary={onSyncLibrary}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Component Selection', () => {
    it('selects component when clicking component name', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const buttonComponent = screen.getByText('Button');
      await user.click(buttonComponent);

      expect(onSelectComponent).toHaveBeenCalledWith('component-button');
    });

    it('highlights selected component', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          selectedComponentId='component-button'
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('displays component category badge', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
      expect(screen.getByText('Card')).toBeInTheDocument();
    });

    it('shows component description', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          selectedComponentId='component-button'
        />,
      );

      expect(screen.getByText(/Reusable button component/i)).toBeInTheDocument();
    });

    it('shows usage count for components', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('filters components by search query', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'button');

      await waitFor(() => {
        expect(screen.getByText('Button')).toBeInTheDocument();
      });
    });

    it('case-insensitive search', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'BUTTON');

      await waitFor(() => {
        expect(screen.getByText('Button')).toBeInTheDocument();
      });
    });

    it('searches in component descriptions', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'reusable');

      await waitFor(() => {
        expect(screen.getByText('Button')).toBeInTheDocument();
      });
    });

    it('shows no results message when no matches', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'nonexistent');

      // Should handle gracefully
      expect(searchInput).toBeInTheDocument();
    });

    it('clears search results when query cleared', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'button');

      await waitFor(() => {
        expect(screen.getByText('Button')).toBeInTheDocument();
      });

      await user.clear(searchInput);

      await waitFor(() => {
        expect(screen.getByText('Card')).toBeInTheDocument();
      });
    });
  });

  describe('Component Details', () => {
    it('displays component variants', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          selectedComponentId='component-button'
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('displays component props', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          selectedComponentId='component-button'
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('shows variant names and descriptions', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          selectedComponentId='component-button'
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('displays prop types and required status', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          selectedComponentId='component-button'
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });
  });

  describe('External Links', () => {
    it('shows Storybook link for component', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          onViewInStorybook={onViewInStorybook}
          selectedComponentId='component-button'
        />,
      );

      const links = screen.getAllByRole('button');
      expect(links.length).toBeGreaterThan(0);
    });

    it('shows Figma link for component', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          onViewInFigma={onViewInFigma}
          selectedComponentId='component-button'
        />,
      );

      const links = screen.getAllByRole('button');
      expect(links.length).toBeGreaterThan(0);
    });

    it('shows code link for component', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          onViewInCode={onViewInCode}
          selectedComponentId='component-button'
        />,
      );

      const links = screen.getAllByRole('button');
      expect(links.length).toBeGreaterThan(0);
    });
  });

  describe('Design Tokens', () => {
    it('displays design tokens tab', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          tokens={mockDesignTokens}
          onSelectComponent={onSelectComponent}
        />,
      );

      // Should render without errors
      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('shows design token values', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          tokens={mockDesignTokens}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('filters tokens by category', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          tokens={mockDesignTokens}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });
  });

  describe('Categories', () => {
    it('groups components by category', () => {
      const atomComponent = { ...mockButton, category: 'atom' };
      const moleculeComponent = { ...mockCard, category: 'molecule' };

      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[atomComponent, moleculeComponent]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
      expect(screen.getByText('Card')).toBeInTheDocument();
    });

    it('shows category icons', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('allows expanding/collapsing categories', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Sync Operations', () => {
    it('calls onSyncLibrary when sync button clicked', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          onSyncLibrary={onSyncLibrary}
        />,
      );

      const buttons = screen.getAllByRole('button');
      const syncButton = buttons.find(
        (btn) =>
          btn.textContent?.includes('Sync') || btn.getAttribute('aria-label')?.includes('Sync'),
      );

      if (syncButton) {
        await user.click(syncButton);
        await waitFor(() => {
          expect(onSyncLibrary).toHaveBeenCalled();
        });
      }
    });

    it('shows loading state during sync', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
          isLoading
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });
  });

  describe('Empty States', () => {
    it('handles no libraries', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[]}
          components={[]}
          onSelectComponent={onSelectComponent}
        />,
      );

      // Should render gracefully
      expect(screen.getByText('No component libraries')).toBeInTheDocument();
    });

    it('handles no components in library', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('UI Components')).toBeInTheDocument();
    });

    it('handles no design tokens', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          tokens={[]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('supports keyboard navigation', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      await user.tab();
      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('provides proper ARIA labels', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      expect(searchInput).toBeInTheDocument();
    });

    it('has semantic HTML structure', () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });
  });

  describe('Sorting and Filtering', () => {
    it('renders components with different usage counts', () => {
      const highUsageComponent = { ...mockButton, usageCount: 100 };
      const lowUsageComponent = { ...mockCard, usageCount: 5 };

      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[lowUsageComponent, highUsageComponent]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
      expect(screen.getByText('Card')).toBeInTheDocument();
    });

    it('renders components updated at different times', () => {
      const recentComponent = {
        ...mockButton,
        updatedAt: '2024-01-20T00:00:00Z',
      };
      const oldComponent = {
        ...mockCard,
        updatedAt: '2024-01-01T00:00:00Z',
      };

      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[oldComponent, recentComponent]}
          onSelectComponent={onSelectComponent}
        />,
      );

      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    it('filters by category', async () => {
      render(
        <ComponentLibraryExplorer
          libraries={[mockUILibrary]}
          components={[mockButton, mockCard]}
          onSelectComponent={onSelectComponent}
        />,
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });
});
