// ComponentUsageMatrix.stories.tsx - Storybook stories for ComponentUsageMatrix

import type { Meta, StoryObj } from '@storybook/react';

import type { ComponentUsage, LibraryComponent } from '@tracertm/types';

import { ComponentUsageMatrix } from '../ComponentUsageMatrix';

const meta = {
  component: ComponentUsageMatrix,
  parameters: {
    layout: 'fullscreen',
    test: {
      disable: true,
    },
  },
  tags: ['autodocs', 'skip-tests'],
  title: 'Graph/ComponentUsageMatrix',
} satisfies Meta<typeof ComponentUsageMatrix>;

export default meta;
type Story = StoryObj<typeof meta>;

// =============================================================================
// MOCK DATA
// =============================================================================

const mockComponents: LibraryComponent[] = [
  // Atoms
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Primary call-to-action button component',
    displayName: 'Primary Button',
    id: 'btn-primary',
    libraryId: 'ds-1',
    name: 'Button',
    projectId: 'proj-1',
    props: [
      {
        name: 'variant',
        required: false,
        type: '"primary" | "secondary" | "danger"',
      },
      { name: 'size', required: false, type: '"sm" | "md" | "lg"' },
      { name: 'disabled', required: false, type: 'boolean' },
      { name: 'loading', required: false, type: 'boolean' },
      {
        name: 'onClick',
        required: false,
        type: '(e: React.MouseEvent) => void',
      },
    ],
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 45,
    usageLocations: ['page-1', 'page-2', 'page-3'],
    variants: [
      { name: 'Primary', props: { variant: 'primary' } },
      { name: 'Secondary', props: { variant: 'secondary' } },
      { name: 'Danger', props: { variant: 'danger' } },
      { name: 'Small', props: { size: 'sm' } },
      { name: 'Large', props: { size: 'lg' } },
    ],
  },
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Basic text input field for forms',
    displayName: 'Text Input',
    id: 'input-text',
    libraryId: 'ds-1',
    name: 'Input',
    projectId: 'proj-1',
    props: [
      { name: 'type', required: false, type: 'string' },
      { name: 'placeholder', required: false, type: 'string' },
      { name: 'disabled', required: false, type: 'boolean' },
      { name: 'required', required: false, type: 'boolean' },
    ],
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 32,
    usageLocations: ['page-2', 'page-3'],
  },
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Small status indicator badge',
    displayName: 'Status Badge',
    id: 'badge-info',
    libraryId: 'ds-1',
    name: 'Badge',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 28,
    usageLocations: ['page-1'],
    variants: [
      { name: 'Success', props: { variant: 'success' } },
      { name: 'Error', props: { variant: 'error' } },
      { name: 'Warning', props: { variant: 'warning' } },
      { name: 'Info', props: { variant: 'info' } },
    ],
  },
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Lucide-based icon system',
    displayName: 'Icon Library',
    id: 'icon-star',
    libraryId: 'ds-1',
    name: 'Icon',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 89,
    usageLocations: ['page-1', 'page-2', 'page-3'],
  },

  // Molecules
  {
    category: 'molecule',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Search input with suggestions',
    displayName: 'Search Bar',
    id: 'search-bar',
    libraryId: 'ds-1',
    name: 'SearchBar',
    projectId: 'proj-1',
    props: [
      { name: 'onSearch', required: true, type: '(query: string) => void' },
      { name: 'suggestions', required: false, type: 'string[]' },
      { name: 'debounceMs', required: false, type: 'number' },
    ],
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 12,
    usageLocations: ['page-1'],
  },
  {
    category: 'molecule',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Labeled input with validation',
    displayName: 'Form Field',
    id: 'form-field',
    libraryId: 'ds-1',
    name: 'FormField',
    projectId: 'proj-1',
    props: [
      { name: 'label', required: true, type: 'string' },
      { name: 'error', required: false, type: 'string' },
      { name: 'required', required: false, type: 'boolean' },
    ],
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 24,
    usageLocations: ['page-2', 'page-3'],
  },

  // Organisms
  {
    category: 'organism',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Top navigation bar with menu',
    displayName: 'Navigation Bar',
    id: 'navbar',
    libraryId: 'ds-1',
    name: 'Navbar',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 3,
    usageLocations: ['page-1'],
  },
  {
    category: 'organism',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Left sidebar navigation',
    displayName: 'Side Navigation',
    id: 'sidebar',
    libraryId: 'ds-1',
    name: 'Sidebar',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 5,
    usageLocations: ['page-1', 'page-2'],
  },
  {
    category: 'organism',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Content card with header and body',
    displayName: 'Card Container',
    id: 'card-component',
    libraryId: 'ds-1',
    name: 'Card',
    projectId: 'proj-1',
    props: [
      { name: 'title', required: false, type: 'string' },
      { name: 'elevation', required: false, type: 'number' },
    ],
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 18,
    usageLocations: ['page-1', 'page-2', 'page-3'],
  },

  // Overlay
  {
    category: 'overlay',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Modal overlay for dialogs',
    displayName: 'Modal Dialog',
    id: 'modal-dialog',
    libraryId: 'ds-1',
    name: 'Modal',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 0,
  },
  {
    category: 'overlay',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'Hover tooltip popup',
    displayName: 'Tooltip',
    id: 'tooltip-popup',
    libraryId: 'ds-1',
    name: 'Tooltip',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 7,
    usageLocations: ['page-1'],
  },

  // Deprecated
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    deprecationMessage: 'Use Button component instead. This will be removed in v3.0',
    description: 'Old button component - do not use',
    displayName: 'Legacy Button (Deprecated)',
    id: 'old-btn',
    libraryId: 'ds-1',
    name: 'LegacyButton',
    projectId: 'proj-1',
    status: 'deprecated',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 4,
    usageLocations: ['page-4'],
  },
  {
    category: 'atom',
    createdAt: '2025-01-01T00:00:00Z',
    deprecationMessage: 'Use Input component instead',
    description: 'Legacy input - use Input instead',
    displayName: 'Old Input Field',
    id: 'old-input',
    libraryId: 'ds-1',
    name: 'OldInput',
    projectId: 'proj-1',
    status: 'deprecated',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 2,
  },

  // Experimental
  {
    category: 'data-display',
    createdAt: '2025-01-01T00:00:00Z',
    description: 'New advanced data table component',
    displayName: 'Data Table',
    id: 'new-table',
    libraryId: 'ds-1',
    name: 'DataTable',
    projectId: 'proj-1',
    props: [
      { name: 'columns', required: true, type: 'Column[]' },
      { name: 'data', required: true, type: 'Row[]' },
      { name: 'sortable', required: false, type: 'boolean' },
      { name: 'filterable', required: false, type: 'boolean' },
    ],
    status: 'experimental',
    updatedAt: '2025-01-29T00:00:00Z',
    usageCount: 1,
  },
];

const mockUsage: ComponentUsage[] = [
  // Button usage
  {
    componentId: 'btn-primary',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'u1',
    libraryId: 'ds-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/dashboard.tsx',
    usedInItemId: 'page-1',
    usedInLine: 45,
    variantUsed: 'Primary',
  },
  {
    componentId: 'btn-primary',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'u2',
    libraryId: 'ds-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/profile.tsx',
    usedInItemId: 'page-2',
    usedInLine: 120,
    variantUsed: 'Secondary',
  },
  {
    componentId: 'btn-primary',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'u3',
    libraryId: 'ds-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/settings.tsx',
    usedInItemId: 'page-3',
    usedInLine: 87,
    variantUsed: 'Primary',
  },

  // Input usage
  {
    componentId: 'input-text',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'u4',
    libraryId: 'ds-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/profile.tsx',
    usedInItemId: 'page-2',
    usedInLine: 95,
  },
  {
    componentId: 'input-text',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'u5',
    libraryId: 'ds-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/settings.tsx',
    usedInItemId: 'page-3',
    usedInLine: 112,
  },

  // Legacy button
  {
    componentId: 'old-btn',
    detectedAt: '2025-01-28T10:00:00Z',
    id: 'u6',
    libraryId: 'ds-1',
    projectId: 'proj-1',
    usedInFilePath: 'pages/legacy.tsx',
    usedInItemId: 'page-4',
    usedInLine: 30,
  },
];

const mockPages = [
  'pages/dashboard.tsx',
  'pages/profile.tsx',
  'pages/settings.tsx',
  'pages/legacy.tsx',
];

// =============================================================================
// STORIES
// =============================================================================

export const Default: Story = {
  args: {
    components: mockComponents,
    pages: mockPages,
    usage: mockUsage,
  },
};

export const WithSearch: Story = {
  args: {
    components: mockComponents,
    enableFiltering: true,
    pages: mockPages,
    usage: mockUsage,
  },
};

export const HighlightUnused: Story = {
  args: {
    components: mockComponents,
    highlightUnused: true,
    pages: mockPages,
    usage: mockUsage,
  },
  parameters: {
    docs: {
      description: {
        story: 'Unused and deprecated components are highlighted with special colors',
      },
    },
  },
};

export const WithVariantsAndProps: Story = {
  args: {
    components: mockComponents,
    pages: mockPages,
    showProps: true,
    showVariants: true,
    usage: mockUsage,
  },
  parameters: {
    docs: {
      description: {
        story: 'Component rows can be expanded to show variants and props',
      },
    },
  },
};

export const CustomPageLabels: Story = {
  args: {
    components: mockComponents,
    pageLabels: {
      'pages/dashboard.tsx': 'Dashboard',
      'pages/legacy.tsx': 'Legacy System',
      'pages/profile.tsx': 'User Profile',
      'pages/settings.tsx': 'Settings',
    },
    pages: mockPages,
    showProps: true,
    showVariants: true,
    usage: mockUsage,
  },
  parameters: {
    docs: {
      description: {
        story: 'Custom labels can be provided for page names',
      },
    },
  },
};

export const NoFiltering: Story = {
  args: {
    components: mockComponents,
    enableFiltering: false,
    pages: mockPages,
    usage: mockUsage,
  },
  parameters: {
    docs: {
      description: {
        story: 'Filtering controls can be disabled',
      },
    },
  },
};

export const LoadingState: Story = {
  args: {
    components: [],
    isLoading: true,
    pages: [],
    usage: [],
  },
};

export const Empty: Story = {
  args: {
    components: [],
    enableFiltering: true,
    pages: [],
    usage: [],
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows when no components are available',
      },
    },
  },
};

export const OnlyAtoms: Story = {
  args: {
    components: mockComponents.filter((c) => c.category === 'atom'),
    pages: mockPages,
    selectedCategory: 'atom',
    usage: mockUsage,
  },
  parameters: {
    docs: {
      description: {
        story: 'Filtered to show only atom components',
      },
    },
  },
};

export const WithCallbacks: Story = {
  args: {
    components: mockComponents,
    onCategoryChange: (category) => {
      alert(`Changed category to: ${category}`);
    },
    onSelectComponent: (componentId) => {
      alert(`Selected component: ${componentId}`);
    },
    onViewInCode: (componentId) => {
      alert(`View in code: ${componentId}`);
    },
    pages: mockPages,
    usage: mockUsage,
  },
  parameters: {
    docs: {
      description: {
        story: 'All callback props are functional',
      },
    },
  },
};
