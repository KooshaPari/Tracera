// Storybook Stories for GraphToolbar
// Demonstrates all toolbar variants and configurations

import type { Meta, StoryObj } from '@storybook/react';

import { ReactFlowProvider } from '@xyflow/react';
import { useState } from 'react';

import { logger } from '@/lib/logger';

import type { LayoutType } from '../layouts/useDagLayout';
import type { GraphPerspective } from '../types';

import { GraphToolbar } from '../GraphToolbar';

const meta: Meta<typeof GraphToolbar> = {
  component: GraphToolbar,
  decorators: [
    (Story) => (
      <ReactFlowProvider>
        <div className='bg-background h-screen p-4'>
          <Story />
        </div>
      </ReactFlowProvider>
    ),
  ],
  parameters: {
    layout: 'fullscreen',
    test: {
      disable: true,
    },
  },
  tags: ['autodocs', 'skip-tests'],
  title: 'Graph/GraphToolbar',
};

export default meta;
type Story = StoryObj<typeof GraphToolbar>;

// Interactive wrapper for stateful toolbar
function ToolbarWrapper({ variant }: { variant?: 'full' | 'compact' | 'minimal' }) {
  const [layout, setLayout] = useState<LayoutType>('flow-chart');
  const [perspective, setPerspective] = useState<GraphPerspective>('all');
  const [showDetailPanel, setShowDetailPanel] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>([]);

  const nodeTypes = [
    'requirement',
    'feature',
    'user_story',
    'epic',
    'task',
    'test_case',
    'bug',
    'api',
    'database',
    'ui_component',
  ];

  return (
    <GraphToolbar
      layout={layout}
      onLayoutChange={setLayout}
      perspective={perspective}
      onPerspectiveChange={setPerspective}
      nodeTypes={nodeTypes}
      selectedNodeTypes={selectedNodeTypes}
      onNodeTypeFilterChange={setSelectedNodeTypes}
      showDetailPanel={showDetailPanel}
      onToggleDetailPanel={() => {
        setShowDetailPanel(!showDetailPanel);
      }}
      isFullscreen={isFullscreen}
      onToggleFullscreen={() => {
        setIsFullscreen(!isFullscreen);
      }}
      totalNodes={150}
      visibleNodes={120}
      totalEdges={300}
      visibleEdges={250}
      onExport={(format) => logger.info('Export:', format)}
      variant={variant}
    />
  );
}

// Full variant with all features
export const Full: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Complete toolbar with layout selector, filters, export controls, zoom, and view options. Best for desktop graph views.',
      },
    },
  },
  render: () => <ToolbarWrapper variant='full' />,
};

// Compact variant
export const Compact: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Compact toolbar with essential controls - layout selector and zoom controls. Good for tablet views.',
      },
    },
  },
  render: () => <ToolbarWrapper variant='compact' />,
};

// Minimal variant
export const Minimal: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Minimal toolbar with only zoom controls. Ideal for mobile views or embedded graphs.',
      },
    },
  },
  render: () => <ToolbarWrapper variant='minimal' />,
};

// With active filters
export const WithFilters: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Toolbar with active filters showing how it displays selected perspectives and node types.',
      },
    },
  },
  render: () => {
    const [layout, setLayout] = useState<LayoutType>('flow-chart');
    const [perspective, setPerspective] = useState<GraphPerspective>('technical');
    const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>([
      'api',
      'database',
      'code',
    ]);
    const [showDetailPanel, setShowDetailPanel] = useState(true);

    return (
      <GraphToolbar
        layout={layout}
        onLayoutChange={setLayout}
        perspective={perspective}
        onPerspectiveChange={setPerspective}
        nodeTypes={['requirement', 'feature', 'api', 'database', 'code', 'test_case']}
        selectedNodeTypes={selectedNodeTypes}
        onNodeTypeFilterChange={setSelectedNodeTypes}
        showDetailPanel={showDetailPanel}
        onToggleDetailPanel={() => {
          setShowDetailPanel(!showDetailPanel);
        }}
        isFullscreen={false}
        onToggleFullscreen={() => {}}
        totalNodes={150}
        visibleNodes={45}
        totalEdges={300}
        visibleEdges={90}
        variant='full'
      />
    );
  },
};

// Large dataset
export const LargeDataset: Story = {
  args: {
    totalEdges: 12_000,
    totalNodes: 5000,
    visibleEdges: 1200,
    visibleNodes: 500,
  },
  parameters: {
    docs: {
      description: {
        story: 'Toolbar with large dataset statistics showing culling information.',
      },
    },
  },
  render: () => <ToolbarWrapper variant='full' />,
};

// Disabled state
export const Disabled: Story = {
  parameters: {
    docs: {
      description: {
        story: 'Toolbar with no data (disabled state).',
      },
    },
  },
  render: () => (
    <GraphToolbar
      layout='flow-chart'
      onLayoutChange={() => {}}
      showDetailPanel={false}
      onToggleDetailPanel={() => {}}
      isFullscreen={false}
      onToggleFullscreen={() => {}}
      totalNodes={0}
      visibleNodes={0}
      variant='full'
    />
  ),
};

// Fullscreen mode
export const Fullscreen: Story = {
  parameters: {
    docs: {
      description: {
        story: 'Toolbar in fullscreen mode showing exit fullscreen button.',
      },
    },
  },
  render: () => {
    const [isFullscreen, setIsFullscreen] = useState(true);

    return (
      <GraphToolbar
        layout='flow-chart'
        onLayoutChange={() => {}}
        showDetailPanel
        onToggleDetailPanel={() => {}}
        isFullscreen={isFullscreen}
        onToggleFullscreen={() => {
          setIsFullscreen(!isFullscreen);
        }}
        totalNodes={100}
        visibleNodes={100}
        variant='full'
      />
    );
  },
};

// Keyboard shortcuts documentation
export const KeyboardShortcuts: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Complete keyboard shortcuts reference for the graph toolbar. All shortcuts work when the graph has focus.',
      },
    },
  },
  render: () => (
    <div className='space-y-4'>
      <h2 className='text-2xl font-bold'>Keyboard Shortcuts</h2>

      <div className='grid grid-cols-2 gap-4'>
        <div className='space-y-2'>
          <h3 className='text-lg font-semibold'>Zoom Controls</h3>
          <div className='space-y-1 text-sm'>
            <div className='flex justify-between'>
              <span>Zoom In</span>
              <kbd className='bg-muted rounded px-2 py-1'>Cmd/Ctrl + Plus</kbd>
            </div>
            <div className='flex justify-between'>
              <span>Zoom Out</span>
              <kbd className='bg-muted rounded px-2 py-1'>Cmd/Ctrl + Minus</kbd>
            </div>
            <div className='flex justify-between'>
              <span>Fit View</span>
              <kbd className='bg-muted rounded px-2 py-1'>Cmd/Ctrl + 0</kbd>
            </div>
            <div className='flex justify-between'>
              <span>Actual Size</span>
              <kbd className='bg-muted rounded px-2 py-1'>Cmd/Ctrl + 1</kbd>
            </div>
          </div>
        </div>

        <div className='space-y-2'>
          <h3 className='text-lg font-semibold'>View Controls</h3>
          <div className='space-y-1 text-sm'>
            <div className='flex justify-between'>
              <span>Fullscreen</span>
              <kbd className='bg-muted rounded px-2 py-1'>F</kbd>
            </div>
            <div className='flex justify-between'>
              <span>Toggle Detail Panel</span>
              <kbd className='bg-muted rounded px-2 py-1'>P</kbd>
            </div>
            <div className='flex justify-between'>
              <span>Toggle Mini-map</span>
              <kbd className='bg-muted rounded px-2 py-1'>M</kbd>
            </div>
          </div>
        </div>

        <div className='space-y-2'>
          <h3 className='text-lg font-semibold'>Actions</h3>
          <div className='space-y-1 text-sm'>
            <div className='flex justify-between'>
              <span>Export</span>
              <kbd className='bg-muted rounded px-2 py-1'>Cmd/Ctrl + E</kbd>
            </div>
            <div className='flex justify-between'>
              <span>Toggle Filters</span>
              <kbd className='bg-muted rounded px-2 py-1'>Cmd/Ctrl + F</kbd>
            </div>
            <div className='flex justify-between'>
              <span>Reset View</span>
              <kbd className='bg-muted rounded px-2 py-1'>Cmd/Ctrl + Shift + R</kbd>
            </div>
          </div>
        </div>
      </div>

      <div className='mt-8'>
        <ToolbarWrapper variant='full' />
      </div>
    </div>
  ),
};
