// Enhanced Graph View - Multi-perspective traceability visualization
// Features: Multiple views, rich node pills, Storybook-like UI view

import { Network } from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type { GraphPerspective } from '@/components/graph/types';
import type { Item, LayoutType, Link } from '@tracertm/types';

import { NodeDetailPanel } from '@/components/graph/NodeDetailPanel';
import { PerspectiveSelector } from '@/components/graph/PerspectiveSelector';
import { PERSPECTIVE_CONFIGS } from '@/components/graph/types';
import { UIComponentTree } from '@/components/graph/UIComponentTree';
import { Card } from '@tracertm/ui/components/Card';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

import { GraphControls } from './GraphControls';
import { GraphHeader } from './GraphHeader';
import { GraphLegend } from './GraphLegend';
import { useCytoscapeEnhancedGraph } from './useCytoscapeEnhancedGraph';
import { useEnhancedGraphData } from './useEnhancedGraphData';

interface EnhancedGraphViewProps {
  items: Item[];
  links: Link[];
  isLoading?: boolean;
  projectId?: string;
  onNavigateToItem?: (itemId: string) => void;
}

function EnhancedGraphViewComponent({
  items,
  links,
  isLoading = false,
  onNavigateToItem,
}: EnhancedGraphViewProps): JSX.Element {
  const [perspective, setPerspective] = useState<GraphPerspective>('all');
  const [layout, setLayout] = useState<LayoutType>('cose');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showDetailPanel, setShowDetailPanel] = useState(true);
  const [showUITree, setShowUITree] = useState(false);

  const {
    filteredNodes,
    filteredLinks,
    perspectiveCounts,
    selectedNode,
    incomingLinks,
    outgoingLinks,
    relatedItems,
  } = useEnhancedGraphData({
    items,
    links,
    perspective,
    selectedNodeId,
  });

  const handleClearSelection = useCallback(() => {
    setSelectedNodeId(null);
  }, []);

  const { containerRef, exportPng, fit, focusNode, zoomIn, zoomOut, clearHighlights } =
    useCytoscapeEnhancedGraph({
      filteredLinks,
      filteredNodes,
      layout,
      onClearSelection: handleClearSelection,
      onSelectNodeId: setSelectedNodeId,
      onShowDetailPanel: setShowDetailPanel,
      perspective,
    });

  const handleLayoutChange = useCallback((newLayout: LayoutType) => {
    setLayout(newLayout);
  }, []);

  const handlePerspectiveChange = useCallback((newPerspective: GraphPerspective) => {
    setPerspective(newPerspective);
    setSelectedNodeId(null);

    // Auto-show UI tree for UI perspective
    setShowUITree(newPerspective === 'ui');

    // Update layout preference
    const config = PERSPECTIVE_CONFIGS.find((c) => c.id === newPerspective);
    if (config?.layoutPreference) {
      setLayout(config.layoutPreference);
    }
  }, []);

  const handleReset = useCallback(() => {
    setPerspective('all');
    setLayout('cose');
    setSelectedNodeId(null);
    setShowUITree(false);
    clearHighlights();
  }, [clearHighlights]);

  const handleCloseDetail = useCallback(() => {
    setSelectedNodeId(null);
    clearHighlights();
  }, [clearHighlights]);

  const handleNavigateToItem = useCallback(
    (itemId: string) => {
      onNavigateToItem?.(itemId);
    },
    [onNavigateToItem],
  );

  if (isLoading) {
    return (
      <div className='space-y-6'>
        <Skeleton className='h-12 w-full' />
        <Skeleton className='h-14 w-full' />
        <Skeleton className='h-[calc(100vh-300px)]' />
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className='space-y-6'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Traceability Graph</h1>
          <p className='text-muted-foreground mt-2'>
            Multi-perspective visualization of item relationships
          </p>
        </div>
        <Card className='p-12'>
          <div className='text-center'>
            <Network className='text-muted-foreground mx-auto mb-4 h-16 w-16' />
            <p className='text-muted-foreground'>No items to visualize</p>
            <p className='text-muted-foreground mt-1 text-sm'>
              Create items and links to see the traceability graph
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      <GraphHeader
        perspective={perspective}
        itemsCount={filteredNodes.length}
        connectionsCount={filteredLinks.length}
      />

      <PerspectiveSelector
        currentPerspective={perspective}
        onPerspectiveChange={handlePerspectiveChange}
        itemCounts={perspectiveCounts}
      />

      <GraphControls
        layout={layout}
        showUITree={showUITree}
        showDetailPanel={showDetailPanel}
        onLayoutChange={handleLayoutChange}
        onToggleUITree={() => {
          setShowUITree((prev) => !prev);
        }}
        onToggleDetailPanel={() => {
          setShowDetailPanel((prev) => !prev);
        }}
        onZoomIn={zoomIn}
        onZoomOut={zoomOut}
        onFit={fit}
        onReset={handleReset}
        onExport={exportPng}
      />

      <div className='flex gap-4' style={{ height: 'calc(100vh - 340px)' }}>
        {showUITree && (
          <div className='w-80 shrink-0'>
            <UIComponentTree
              items={items}
              links={links}
              onSelectItem={focusNode}
              selectedItemId={selectedNodeId}
            />
          </div>
        )}

        <Card className='flex-1 overflow-hidden p-0'>
          <div ref={containerRef} className='bg-background h-full w-full' />
        </Card>

        {showDetailPanel && selectedNode && (
          <NodeDetailPanel
            node={selectedNode}
            relatedItems={relatedItems}
            incomingLinks={incomingLinks}
            outgoingLinks={outgoingLinks}
            onClose={handleCloseDetail}
            onNavigateToItem={handleNavigateToItem}
            onFocusNode={focusNode}
          />
        )}
      </div>

      <GraphLegend filteredNodes={filteredNodes} />
    </div>
  );
}

export const EnhancedGraphView = memo(EnhancedGraphViewComponent);
