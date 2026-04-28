// Graph View Container - Project views in sidebar; graph type (mind map, flow chart, etc.) in combobox

import { useCallback, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import type { GraphViewMode } from './GraphViewConfig';
import type { LayoutType } from './layouts/useDagLayout';
import type { GraphPerspective } from './types';

import { GraphViewLoadingState } from './GraphViewLoadingState';
import { GraphViewSidebar } from './GraphViewSidebar';
import { GraphViewTopBar } from './GraphViewTopBar';
import { useGraphViewState } from './useGraphViewState';

interface GraphViewContainerProps {
  items: Item[];
  links: Link[];
  isLoading?: boolean | undefined;
  projectId?: string | undefined;
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  defaultView?: GraphViewMode | undefined;
  canLoadMore?: boolean | undefined;
  visibleEdges?: number | undefined;
  totalEdges?: number | undefined;
  onLoadMore?: (() => void) | undefined;
  children: (props: {
    viewMode: GraphViewMode;
    perspective: GraphPerspective | undefined;
    layoutPreference: LayoutType | undefined;
    items: Item[];
    links: Link[];
    onNavigateToItem?: ((itemId: string) => void) | undefined;
  }) => React.ReactNode;
}

interface SelectPointerEvent {
  stopPropagation: () => void;
}

const stopSelectPointerDown = (event: SelectPointerEvent): void => {
  event.stopPropagation();
};

const GraphViewContainer = ({
  items,
  links,
  projectId,
  isLoading = false,
  onNavigateToItem,
  defaultView = 'traceability',
  canLoadMore: _canLoadMore = false,
  visibleEdges: _visibleEdges,
  totalEdges: _totalEdges,
  onLoadMore: _onLoadMore,
  children,
}: GraphViewContainerProps): JSX.Element => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const {
    currentConfig,
    filteredDiagramViews,
    filteredGraphViews,
    filteredPerspectiveViews,
    getPerspective,
    handleSelectChange,
    handleViewTypeSearchChange,
    perspectiveColor,
    viewMode,
    viewTypeSearch,
  } = useGraphViewState({
    defaultView,
  });

  const handleSidebarToggle = useCallback((): void => {
    setSidebarCollapsed((collapsed) => !collapsed);
  }, []);

  const { length: itemCount } = items;
  const { length: linkCount } = links;

  // Loading state
  if (isLoading) {
    return <GraphViewLoadingState />;
  }

  return (
    <div className='flex h-full'>
      {/* Sidebar */}
      <GraphViewSidebar
        collapsed={sidebarCollapsed}
        onToggle={handleSidebarToggle}
        projectId={projectId}
        itemsCount={itemCount}
        linksCount={linkCount}
      />

      {/* Main content area */}
      <div className='flex flex-1 flex-col overflow-hidden'>
        <GraphViewTopBar
          viewMode={viewMode}
          viewTypeSearch={viewTypeSearch}
          currentConfig={currentConfig}
          filteredGraphViews={filteredGraphViews}
          filteredDiagramViews={filteredDiagramViews}
          filteredPerspectiveViews={filteredPerspectiveViews}
          onSelectChange={handleSelectChange}
          onSearchChange={handleViewTypeSearchChange}
          onSearchPointerDown={stopSelectPointerDown}
          perspectiveColor={perspectiveColor}
        />

        {/* View content */}
        <div className='relative flex-1 overflow-hidden'>
          {children({
            items,
            layoutPreference: currentConfig?.layoutPreference,
            links,
            onNavigateToItem,
            perspective: getPerspective(viewMode),
            viewMode,
          })}
        </div>
      </div>
    </div>
  );
};

export { GraphViewContainer };
