// Example: Integrating GraphToolbar into FlowGraphViewInner
// This shows how to use the new toolbar with all features

import { ReactFlowProvider } from '@xyflow/react';
import { useCallback, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import { logger } from '@/lib/logger';

import type { LayoutType } from './layouts/useDagLayout';
import type { GraphPerspective } from './types';

import { FlowGraphViewInner } from './FlowGraphViewInner';
import { GraphToolbar } from './GraphToolbar';

interface EnhancedGraphViewProps {
  items: Item[];
  links: Link[];
  onNavigateToItem?: (itemId: string) => void;
}

export function EnhancedGraphView({ items, links, onNavigateToItem }: EnhancedGraphViewProps) {
  // State management
  const [layout, setLayout] = useState<LayoutType>('flow-chart');
  const [perspective, setPerspective] = useState<GraphPerspective>('all');
  const [showDetailPanel, setShowDetailPanel] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>([]);

  // Derive unique node types from items
  const nodeTypes = [
    ...new Set(items.map((item) => item.type || 'item').map((t) => t.toLowerCase())),
  ];

  // Fullscreen toggle
  const handleFullscreenToggle = useCallback(async () => {
    const container = document.querySelector('.graph-container');
    if (!container) {
      return;
    }

    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
        setIsFullscreen(false);
      } else {
        await (container as HTMLElement).requestFullscreen();
        setIsFullscreen(true);
      }
    } catch {
      // Fullscreen not supported or denied
    }
  }, []);

  // Reset all filters and view
  const handleReset = useCallback(() => {
    setPerspective('all');
    setLayout('flow-chart');
    setSelectedNodeTypes([]);
  }, []);

  // Export handler
  const handleExport = useCallback((format: 'png' | 'svg' | 'json' | 'csv') => {
    logger.info(`Exporting graph as ${format}`);
    // Export logic is handled by ExportControls internally
  }, []);

  // Filter items by selected types
  const filteredItems =
    selectedNodeTypes.length > 0
      ? items.filter((item) => selectedNodeTypes.includes((item.type || 'item').toLowerCase()))
      : items;

  return (
    <ReactFlowProvider>
      <div className='graph-container flex h-full flex-col'>
        {/* Professional Toolbar */}
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
          onToggleFullscreen={handleFullscreenToggle}
          totalNodes={items.length}
          visibleNodes={filteredItems.length}
          totalEdges={links.length}
          visibleEdges={links.length}
          onReset={handleReset}
          onExport={handleExport}
          variant='full' // Or "compact" or "minimal"
        />

        {/* Graph View */}
        <div className='mt-3 flex-1'>
          <FlowGraphViewInner
            items={filteredItems}
            links={links}
            perspective={perspective}
            defaultLayout={layout}
            onNavigateToItem={onNavigateToItem}
            showControls={false} // Toolbar provides controls
            autoFit
          />
        </div>
      </div>
    </ReactFlowProvider>
  );
}

// Compact variant example
export function CompactGraphView({ items, links }: { items: Item[]; links: Link[] }) {
  const [layout, setLayout] = useState<LayoutType>('flow-chart');
  const [showDetailPanel, setShowDetailPanel] = useState(true);

  return (
    <ReactFlowProvider>
      <div className='flex h-full flex-col'>
        <GraphToolbar
          layout={layout}
          onLayoutChange={setLayout}
          showDetailPanel={showDetailPanel}
          onToggleDetailPanel={() => {
            setShowDetailPanel(!showDetailPanel);
          }}
          isFullscreen={false}
          onToggleFullscreen={() => {}}
          variant='compact'
        />

        <div className='mt-2 flex-1'>
          <FlowGraphViewInner
            items={items}
            links={links}
            defaultLayout={layout}
            showControls={false}
          />
        </div>
      </div>
    </ReactFlowProvider>
  );
}

// Minimal variant example
export function MinimalGraphView({ items, links }: { items: Item[]; links: Link[] }) {
  return (
    <ReactFlowProvider>
      <div className='flex h-full flex-col'>
        <GraphToolbar
          layout='flow-chart'
          onLayoutChange={() => {}}
          showDetailPanel={false}
          onToggleDetailPanel={() => {}}
          isFullscreen={false}
          onToggleFullscreen={() => {}}
          variant='minimal'
        />

        <div className='mt-1 flex-1'>
          <FlowGraphViewInner items={items} links={links} showControls={false} />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
