/**
 * DesignTokenBrowser Component Example
 * Demonstrates usage patterns for the Design Token Browser component
 */

import { useState } from 'react';

import type { DesignToken } from '@tracertm/types';

import { logger } from '@/lib/logger';

import { DesignTokenBrowser } from './DesignTokenBrowser';

/**
 * Example 1: Basic Usage
 * Shows the component with minimal configuration
 */
export function BasicExample() {
  const tokens: DesignToken[] = [
    {
      createdAt: '2024-01-01T00:00:00Z',
      description: 'Primary brand color',
      id: 'color-primary',
      libraryId: 'lib-1',
      name: 'primary',
      path: ['colors', 'primary', '500'],
      projectId: 'proj-1',
      resolvedValue: '#3B82F6',
      tags: ['brand'],
      type: 'color',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 12,
      usedByComponentIds: ['btn-1'],
      value: '#3B82F6',
    },
  ];

  return <DesignTokenBrowser tokens={tokens} />;
}

/**
 * Example 2: With Selection Handling
 * Demonstrates token selection callbacks
 */
export function SelectionExample() {
  const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null);

  const tokens: DesignToken[] = [
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: 'color-1',
      libraryId: 'lib-1',
      name: 'primary',
      path: ['colors', 'primary', '500'],
      projectId: 'proj-1',
      resolvedValue: '#3B82F6',
      type: 'color',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 12,
      value: '#3B82F6',
    },
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: 'color-2',
      libraryId: 'lib-1',
      name: 'secondary',
      path: ['colors', 'secondary', '500'],
      projectId: 'proj-1',
      resolvedValue: '#10B981',
      type: 'color',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 8,
      value: '#10B981',
    },
  ];

  return (
    <div className='space-y-4'>
      <div>
        <h3 className='text-sm font-medium'>Selected Token:</h3>
        <p className='text-muted-foreground text-xs'>
          {selectedTokenId ? `ID: ${selectedTokenId}` : 'None selected'}
        </p>
      </div>
      <DesignTokenBrowser
        tokens={tokens}
        selectedTokenId={selectedTokenId}
        onSelectToken={setSelectedTokenId}
      />
    </div>
  );
}

/**
 * Example 3: With Component Usage Tracking
 * Shows which components use each token
 */
export function ComponentUsageExample() {
  // Map component IDs to human-readable names
  const componentMap = new Map([
    ['btn-primary', 'Button Primary'],
    ['btn-secondary', 'Button Secondary'],
    ['link-default', 'Link Default'],
    ['card-header', 'Card Header'],
  ]);

  const tokens: DesignToken[] = [
    {
      createdAt: '2024-01-01T00:00:00Z',
      description: 'Primary brand color',
      id: 'color-primary',
      libraryId: 'lib-1',
      name: 'primary',
      path: ['colors', 'primary', '500'],
      projectId: 'proj-1',
      resolvedValue: '#3B82F6',
      tags: ['brand', 'interactive'],
      type: 'color',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 12,
      usedByComponentIds: ['btn-primary', 'link-default', 'card-header'],
      value: '#3B82F6',
    },
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: 'spacing-md',
      libraryId: 'lib-1',
      name: 'md',
      path: ['spacing', 'md'],
      projectId: 'proj-1',
      resolvedValue: '1rem',
      type: 'spacing',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 25,
      usedByComponentIds: ['btn-primary', 'btn-secondary', 'card-header'],
      value: '1rem',
    },
  ];

  return <DesignTokenBrowser tokens={tokens} showComponentUsage componentMap={componentMap} />;
}

/**
 * Example 4: With Figma Integration
 * Shows synced Figma tokens and linking capability
 */
export function FigmaIntegrationExample() {
  const handleLinkToFigma = async (tokenId: string) => {
    logger.info(`Linking token ${tokenId} to Figma...`);
    // In a real app, this would call your API
  };

  const tokens: DesignToken[] = [
    {
      id: 'color-primary',
      libraryId: 'lib-1',
      projectId: 'proj-1',
      name: 'primary',
      path: ['colors', 'primary', '500'],
      type: 'color',
      value: '#3B82F6',
      resolvedValue: '#3B82F6',
      usageCount: 12,
      figmaStyleId: 'figma-style-abc123', // Already synced
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
    {
      id: 'color-secondary',
      libraryId: 'lib-1',
      projectId: 'proj-1',
      name: 'secondary',
      path: ['colors', 'secondary', '500'],
      type: 'color',
      value: '#10B981',
      resolvedValue: '#10B981',
      usageCount: 8,
      // Not synced - user can link it
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
  ];

  return <DesignTokenBrowser tokens={tokens} onLinkToFigma={handleLinkToFigma} />;
}

/**
 * Example 5: With Token References
 * Shows tokens that reference other tokens
 */
export function TokenReferencesExample() {
  const tokens: DesignToken[] = [
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: 'color-primary-500',
      libraryId: 'lib-1',
      name: 'primary.500',
      path: ['colors', 'primary', '500'],
      projectId: 'proj-1',
      resolvedValue: '#3B82F6',
      type: 'color',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 5,
      value: '#3B82F6',
    },
    {
      id: 'color-primary-light',
      libraryId: 'lib-1',
      projectId: 'proj-1',
      name: 'primary.light',
      path: ['colors', 'primary', 'light'],
      description: 'Lighter shade of primary color',
      type: 'color',
      value: '{colors.primary.500}',
      resolvedValue: '#3B82F6',
      referencesTokenId: 'color-primary-500', // References primary.500
      usageCount: 8,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
    {
      createdAt: '2024-01-01T00:00:00Z',
      description: 'Darker shade of primary color',
      id: 'color-primary-dark',
      libraryId: 'lib-1',
      name: 'primary.dark',
      path: ['colors', 'primary', 'dark'],
      projectId: 'proj-1',
      referencesTokenId: 'color-primary-500',
      resolvedValue: '#3B82F6',
      type: 'color',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 6,
      value: '{colors.primary.500}',
    },
  ];

  return <DesignTokenBrowser tokens={tokens} />;
}

/**
 * Example 6: Full Featured Example
 * Demonstrates all features combined
 */
export function FullFeaturedExample() {
  const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null);

  const componentMap = new Map([
    ['btn-1', 'Button Primary'],
    ['btn-2', 'Button Secondary'],
    ['link-1', 'Link Text'],
  ]);

  const handleLinkToFigma = async (tokenId: string) => {
    logger.info(`Linking token ${tokenId} to Figma...`);
    // Call your API
  };

  const tokens: DesignToken[] = [
    // Colors
    {
      createdAt: '2024-01-01T00:00:00Z',
      description: 'Primary brand color',
      figmaStyleId: 'figma-1',
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
      usedByComponentIds: ['btn-1', 'link-1'],
      value: '#3B82F6',
    },
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: 'color-2',
      libraryId: 'lib-1',
      name: 'secondary',
      path: ['colors', 'secondary', '500'],
      projectId: 'proj-1',
      resolvedValue: '#10B981',
      type: 'color',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 8,
      usedByComponentIds: ['btn-2'],
      value: '#10B981',
    },
    // Spacing
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
      usedByComponentIds: ['btn-1', 'btn-2'],
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
      usedByComponentIds: ['btn-1'],
      value: '1rem',
    },
    // Typography
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: 'typo-1',
      libraryId: 'lib-1',
      name: 'body',
      path: ['typography', 'body'],
      projectId: 'proj-1',
      resolvedValue: '16px/1.5 "Inter", sans-serif',
      type: 'typography',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 25,
      value: '16px/1.5 "Inter", sans-serif',
    },
    // Shadows
    {
      createdAt: '2024-01-01T00:00:00Z',
      id: 'shadow-1',
      libraryId: 'lib-1',
      name: 'lg',
      path: ['shadows', 'lg'],
      projectId: 'proj-1',
      resolvedValue: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      type: 'shadow',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 5,
      value: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    },
  ];

  return (
    <div className='space-y-4'>
      <div>
        <h2 className='text-sm font-semibold'>Selected Token</h2>
        <p className='text-muted-foreground text-xs'>
          {selectedTokenId ? `ID: ${selectedTokenId}` : 'None selected'}
        </p>
      </div>
      <DesignTokenBrowser
        tokens={tokens}
        selectedTokenId={selectedTokenId}
        onSelectToken={setSelectedTokenId}
        onLinkToFigma={handleLinkToFigma}
        showComponentUsage
        componentMap={componentMap}
      />
    </div>
  );
}

/**
 * Example Usage Index
 * Demonstrates all examples in a tabbed interface
 */
export function ExamplesShowcase() {
  const [activeExample, setActiveExample] = useState<
    'basic' | 'selection' | 'usage' | 'figma' | 'references' | 'full'
  >('full');

  const examples = {
    basic: {
      component: <BasicExample />,
      description: 'Minimal configuration example',
      title: 'Basic Usage',
    },
    figma: {
      component: <FigmaIntegrationExample />,
      description: 'Sync tokens with Figma styles',
      title: 'Figma Integration',
    },
    full: {
      component: <FullFeaturedExample />,
      description: 'All features combined',
      title: 'Full Featured',
    },
    references: {
      component: <TokenReferencesExample />,
      description: 'Display token-to-token references',
      title: 'Token References',
    },
    selection: {
      component: <SelectionExample />,
      description: 'Handle token selection events',
      title: 'Token Selection',
    },
    usage: {
      component: <ComponentUsageExample />,
      description: 'Track component usage of tokens',
      title: 'Component Usage',
    },
  };

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold'>DesignTokenBrowser Examples</h1>
        <p className='text-muted-foreground mt-1 text-sm'>
          Browse through different usage patterns
        </p>
      </div>

      {/* Tab buttons */}
      <div className='flex flex-wrap gap-2'>
        {(Object.keys(examples) as (keyof typeof examples)[]).map((key) => (
          <button
            key={key}
            onClick={() => {
              setActiveExample(key);
            }}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              activeExample === key
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-foreground hover:bg-muted/80'
            }`}
          >
            {examples[key].title}
          </button>
        ))}
      </div>

      {/* Description */}
      <div className='text-muted-foreground text-sm'>{examples[activeExample].description}</div>

      {/* Example content */}
      <div className='h-[600px] overflow-hidden rounded-lg border p-4'>
        {examples[activeExample].component}
      </div>
    </div>
  );
}
