// Professional Graph Toolbar - Comprehensive controls for graph visualization
// Provides zoom, layout, filter, export, and view options

import { useReactFlow } from '@xyflow/react';
import {
  Download,
  Filter,
  Maximize,
  Maximize2,
  Minimize,
  PanelRight,
  PanelRightClose,
  Settings2,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { useCallback, useState } from 'react';

import { Button } from '@tracertm/ui/components/Button';
import { Separator } from '@tracertm/ui/components/Separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import type { LayoutType } from './layouts/useDagLayout';
import type { GraphPerspective } from './types';

import { ExportControls } from './ExportControls';
import { FilterControls } from './FilterControls';
import { LayoutSelector } from './layouts/LayoutSelector';

interface GraphToolbarProps {
  // Layout
  layout: LayoutType;
  onLayoutChange: (layout: LayoutType) => void;

  // Filter state
  perspective?: GraphPerspective | undefined;
  onPerspectiveChange?: ((perspective: GraphPerspective) => void) | undefined;
  nodeTypes?: string[] | undefined;
  selectedNodeTypes?: string[] | undefined;
  onNodeTypeFilterChange?: ((types: string[]) => void) | undefined;

  // View state
  showDetailPanel: boolean;
  onToggleDetailPanel: () => void;
  isFullscreen: boolean;
  onToggleFullscreen: () => void;

  // Stats for display
  totalNodes?: number | undefined;
  visibleNodes?: number | undefined;
  totalEdges?: number | undefined;
  visibleEdges?: number | undefined;

  // Optional callbacks
  onReset?: (() => void) | undefined;
  onExport?: ((format: 'png' | 'svg' | 'json' | 'csv') => void) | undefined;

  // Variant
  variant?: 'full' | 'compact' | 'minimal' | undefined;
  className?: string | undefined;
}

export function GraphToolbar({
  layout,
  onLayoutChange,
  perspective,
  onPerspectiveChange,
  nodeTypes,
  selectedNodeTypes,
  onNodeTypeFilterChange,
  showDetailPanel,
  onToggleDetailPanel,
  isFullscreen,
  onToggleFullscreen,
  totalNodes = 0,
  visibleNodes = 0,
  totalEdges = 0,
  visibleEdges = 0,
  onExport,
  variant = 'full',
  onReset,
  className,
}: GraphToolbarProps) {
  const { fitView, zoomIn, zoomOut, getViewport } = useReactFlow();
  const [showFilters, setShowFilters] = useState(false);
  const [showExport, setShowExport] = useState(false);

  // Zoom controls
  const handleZoomIn = useCallback(() => {}, [zoomIn]);

  const handleZoomOut = useCallback(() => {}, [zoomOut]);

  const handleFitView = useCallback(() => {}, [fitView]);

  const handleActualSize = useCallback(() => {
    const viewport = getViewport();
    if (viewport) {
      // Reset zoom to 1:1
      undefined;
    }
  }, [fitView, getViewport]);

  // Export handler
  const handleExportClick = useCallback(
    (format: 'png' | 'svg' | 'json' | 'csv') => {
      onExport?.(format);
      setShowExport(false);
    },
    [onExport],
  );

  // Compact variant - minimal controls
  if (variant === 'minimal') {
    return (
      <div className='flex items-center gap-1 p-1' role='toolbar' aria-label='Graph view controls'>
        <div className='flex items-center gap-0.5 rounded-md border p-0.5'>
          <Button
            variant='ghost'
            size='sm'
            onClick={handleZoomIn}
            className='h-7 w-7 p-0'
            aria-label='Zoom in'
            title='Zoom in'
          >
            <ZoomIn className='h-3.5 w-3.5' aria-hidden='true' />
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={handleZoomOut}
            className='h-7 w-7 p-0'
            aria-label='Zoom out'
            title='Zoom out'
          >
            <ZoomOut className='h-3.5 w-3.5' aria-hidden='true' />
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={handleFitView}
            className='h-7 w-7 p-0'
            aria-label='Fit view to content'
            title='Fit view'
          >
            <Maximize2 className='h-3.5 w-3.5' aria-hidden='true' />
          </Button>
        </div>
      </div>
    );
  }

  // Compact variant - essential controls
  if (variant === 'compact') {
    return (
      <div
        className='flex items-center gap-2 p-1.5'
        role='toolbar'
        aria-label='Graph view controls'
      >
        <LayoutSelector value={layout} onChange={onLayoutChange} variant='compact' />

        <Separator orientation='vertical' className='h-6' aria-hidden='true' />

        <div
          className='flex items-center gap-0.5 rounded-md border p-0.5'
          role='group'
          aria-label='Zoom controls'
        >
          <Button
            variant='ghost'
            size='sm'
            onClick={handleZoomIn}
            className='h-7 w-7 p-0'
            aria-label='Zoom in (Cmd +)'
            title='Zoom in (Cmd +)'
          >
            <ZoomIn className='h-3.5 w-3.5' aria-hidden='true' />
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={handleZoomOut}
            className='h-7 w-7 p-0'
            aria-label='Zoom out (Cmd -)'
            title='Zoom out (Cmd -)'
          >
            <ZoomOut className='h-3.5 w-3.5' aria-hidden='true' />
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={handleFitView}
            className='h-7 w-7 p-0'
            aria-label='Fit view to content (Cmd 0)'
            title='Fit view (Cmd 0)'
          >
            <Maximize2 className='h-3.5 w-3.5' aria-hidden='true' />
          </Button>
        </div>

        <Button
          variant='ghost'
          size='sm'
          onClick={onToggleDetailPanel}
          className='h-7 w-7 p-0'
          aria-label={showDetailPanel ? 'Hide detail panel' : 'Show detail panel'}
          aria-pressed={showDetailPanel}
          title='Toggle detail panel'
        >
          {showDetailPanel ? (
            <PanelRightClose className='h-3.5 w-3.5' aria-hidden='true' />
          ) : (
            <PanelRight className='h-3.5 w-3.5' aria-hidden='true' />
          )}
        </Button>
      </div>
    );
  }

  // Full variant - all controls
  return (
    <TooltipProvider>
      <div
        className={`bg-card flex flex-wrap items-center justify-between gap-2 rounded-lg border p-2 sm:gap-3 sm:p-3 ${className ?? ''}`}
        role='toolbar'
        aria-label='Graph view controls'
      >
        {/* Left section: Layout and filters */}
        <div
          className='flex min-w-0 items-center gap-2'
          role='group'
          aria-label='Layout and filter controls'
        >
          {/* Layout selector */}
          <LayoutSelector
            value={layout}
            onChange={onLayoutChange}
            variant='select'
            className='w-full max-w-[160px] min-w-0 sm:max-w-[200px]'
          />

          <Separator orientation='vertical' className='hidden h-6 sm:block' aria-hidden='true' />

          {/* Filter controls */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={showFilters ? 'secondary' : 'ghost'}
                size='sm'
                onClick={() => {
                  setShowFilters(!showFilters);
                }}
                className='h-8 w-8 p-0'
                aria-label='Filter nodes and edges'
                aria-pressed={showFilters}
                aria-expanded={showFilters}
                aria-controls='filter-panel'
              >
                <Filter className='h-4 w-4' aria-hidden='true' />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Filter nodes and edges</p>
            </TooltipContent>
          </Tooltip>

          {/* Export controls */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={showExport ? 'secondary' : 'ghost'}
                size='sm'
                onClick={() => {
                  setShowExport(!showExport);
                }}
                className='h-8 w-8 p-0'
                aria-label='Export graph (Cmd E)'
                aria-pressed={showExport}
                aria-expanded={showExport}
                aria-controls='export-panel'
              >
                <Download className='h-4 w-4' aria-hidden='true' />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Export graph (Cmd E)</p>
            </TooltipContent>
          </Tooltip>

          {/* Stats badge (optional) */}
          {totalNodes > 0 && (
            <div className='bg-muted/50 hidden items-center gap-1.5 rounded-md px-2 py-1 text-xs md:flex'>
              <span className='text-muted-foreground'>Nodes:</span>
              <span className='font-medium'>
                {visibleNodes}/{totalNodes}
              </span>
              {totalEdges > 0 && (
                <>
                  <Separator orientation='vertical' className='mx-0.5 h-3' />
                  <span className='text-muted-foreground'>Edges:</span>
                  <span className='font-medium'>
                    {visibleEdges}/{totalEdges}
                  </span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Right section: View controls */}
        <div className='flex items-center gap-2' role='group' aria-label='View and zoom controls'>
          {/* Zoom controls */}
          <div
            className='flex items-center gap-0.5 rounded-md border p-0.5'
            role='group'
            aria-label='Zoom controls'
          >
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={handleZoomIn}
                  className='h-8 w-8 p-0'
                  aria-label='Zoom in (Cmd +)'
                >
                  <ZoomIn className='h-4 w-4' aria-hidden='true' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Zoom in (Cmd +)</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={handleZoomOut}
                  className='h-8 w-8 p-0'
                  aria-label='Zoom out (Cmd -)'
                >
                  <ZoomOut className='h-4 w-4' aria-hidden='true' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Zoom out (Cmd -)</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={handleFitView}
                  className='h-8 w-8 p-0'
                  aria-label='Fit view to content (Cmd 0)'
                >
                  <Maximize2 className='h-4 w-4' aria-hidden='true' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Fit view (Cmd 0)</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={handleActualSize}
                  className='h-8 w-8 p-0'
                  aria-label='Set actual size to 1:1'
                >
                  <Settings2 className='h-4 w-4' aria-hidden='true' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Actual size (1:1)</p>
              </TooltipContent>
            </Tooltip>
          </div>

          <Separator orientation='vertical' className='h-6' aria-hidden='true' />

          {/* Fullscreen toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant='ghost'
                size='sm'
                onClick={onToggleFullscreen}
                className='h-8 w-8 p-0'
                aria-label={isFullscreen ? 'Exit fullscreen (Esc)' : 'Enter fullscreen (F)'}
                aria-pressed={isFullscreen}
              >
                {isFullscreen ? (
                  <Minimize className='h-4 w-4' aria-hidden='true' />
                ) : (
                  <Maximize className='h-4 w-4' aria-hidden='true' />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>{isFullscreen ? 'Exit fullscreen (Esc)' : 'Fullscreen (F)'}</p>
            </TooltipContent>
          </Tooltip>

          {/* Detail panel toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant='ghost'
                size='sm'
                onClick={onToggleDetailPanel}
                className='h-8 w-8 p-0'
                aria-label={showDetailPanel ? 'Hide detail panel (P)' : 'Show detail panel (P)'}
                aria-pressed={showDetailPanel}
                aria-expanded={showDetailPanel}
                aria-controls='detail-panel'
              >
                {showDetailPanel ? (
                  <PanelRightClose className='h-4 w-4' aria-hidden='true' />
                ) : (
                  <PanelRight className='h-4 w-4' aria-hidden='true' />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Toggle detail panel (P)</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Filter panel (expandable) */}
        {showFilters && (
          <div
            id='filter-panel'
            className='mt-2 w-full border-t pt-2'
            role='region'
            aria-label='Graph filter options'
          >
            <FilterControls
              perspective={perspective}
              onPerspectiveChange={onPerspectiveChange}
              nodeTypes={nodeTypes}
              selectedNodeTypes={selectedNodeTypes}
              onNodeTypeFilterChange={onNodeTypeFilterChange}
              onClose={() => {
                setShowFilters(false);
              }}
            />
          </div>
        )}

        {/* Export panel (expandable) */}
        {showExport && (
          <div
            id='export-panel'
            className='mt-2 w-full border-t pt-2'
            role='region'
            aria-label='Graph export options'
          >
            <ExportControls
              onExport={handleExportClick}
              onClose={() => {
                setShowExport(false);
              }}
              disabled={totalNodes === 0}
            />
          </div>
        )}
      </div>
    </TooltipProvider>
  );
}
