/**
 * StreamingGraphView - Example component demonstrating incremental graph loading
 *
 * Features:
 * - Real-time streaming data loading
 * - Progressive rendering
 * - Loading progress UI
 * - Viewport-based data fetching
 * - Predictive prefetch
 */

import { RefreshCw, ZoomIn, ZoomOut } from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';

import type { ViewportBounds } from '../../lib/graph/IncrementalGraphBuilder';

import {
  calculatePanDirection,
  calculatePanVelocity,
  useIncrementalGraph,
} from '../../hooks/useIncrementalGraph';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { GraphLoadingProgress, GraphLoadingProgressCompact } from './GraphLoadingProgress';

export interface StreamingGraphViewProps {
  projectId: string;
  initialViewport?: ViewportBounds | undefined;
  onViewportChange?: ((viewport: ViewportBounds) => void) | undefined;
  showProgress?: boolean | undefined;
  enablePrefetch?: boolean | undefined;
  className?: string | undefined;
}

export function StreamingGraphView({
  projectId,
  initialViewport = { maxX: 1000, maxY: 1000, minX: 0, minY: 0 },
  onViewportChange,
  showProgress = true,
  enablePrefetch = true,
  className = '',
}: StreamingGraphViewProps) {
  const [viewport, setViewport] = useState<ViewportBounds>(initialViewport);
  const [zoom, setZoom] = useState(1);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState<{ x: number; y: number } | null>(null);

  const previousViewportRef = useRef<ViewportBounds>(viewport);
  const lastMoveTimeRef = useRef<number>(Date.now());

  // Calculate pan direction and velocity
  const panDirection = calculatePanDirection(previousViewportRef.current, viewport);
  const panVelocity = calculatePanVelocity(
    previousViewportRef.current,
    viewport,
    Date.now() - lastMoveTimeRef.current,
  );

  // Use incremental graph hook
  const { state, loadGraph, loadViewport, abort, reset } = useIncrementalGraph({
    enablePrefetch,
    prefetchDirection: panDirection ?? undefined,
    prefetchVelocity: panVelocity,
    projectId,
    viewport,
    zoom,
  });

  // Load graph on mount and viewport change
  useEffect(() => {}, [loadGraph]);

  // Update previous viewport reference
  useEffect(() => {
    previousViewportRef.current = viewport;
    lastMoveTimeRef.current = Date.now();
  }, [viewport]);

  // Handle viewport changes
  const handleViewportChange = useCallback(
    (newViewport: ViewportBounds) => {},
    [onViewportChange, loadViewport],
  );

  // Pan handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsPanning(true);
    setPanStart({ x: e.clientX, y: e.clientY });
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isPanning || !panStart) {
        return;
      }

      const dx = (e.clientX - panStart.x) / zoom;
      const dy = (e.clientY - panStart.y) / zoom;

      const newViewport = {
        maxX: viewport.maxX - dx,
        maxY: viewport.maxY - dy,
        minX: viewport.minX - dx,
        minY: viewport.minY - dy,
      };

      handleViewportChange(newViewport);
      setPanStart({ x: e.clientX, y: e.clientY });
    },
    [isPanning, panStart, viewport, zoom, handleViewportChange],
  );

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
    setPanStart(null);
  }, []);

  // Zoom handlers
  const handleZoomIn = useCallback(() => {
    setZoom((z) => Math.min(z * 1.5, 10));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom((z) => Math.max(z / 1.5, 0.1));
  }, []);

  // Reset handler
  const handleReset = useCallback(() => {}, [reset, initialViewport, loadGraph]);

  return (
    <div className={`relative ${className}`}>
      {/* Progress UI */}
      {showProgress && state.isLoading && (
        <div className='absolute top-4 right-4 z-10 w-80'>
          <GraphLoadingProgress
            progress={state.progress}
            metadata={state.metadata}
            isLoading={state.isLoading}
            onCancel={abort}
          />
        </div>
      )}

      {/* Controls */}
      <div className='absolute top-4 left-4 z-10 flex gap-2'>
        <Button variant='outline' size='sm' onClick={handleZoomIn} title='Zoom In'>
          <ZoomIn className='h-4 w-4' />
        </Button>
        <Button variant='outline' size='sm' onClick={handleZoomOut} title='Zoom Out'>
          <ZoomOut className='h-4 w-4' />
        </Button>
        <Button variant='outline' size='sm' onClick={handleReset} title='Reset View'>
          <RefreshCw className='h-4 w-4' />
        </Button>
      </div>

      {/* Compact progress at bottom */}
      {showProgress && state.isLoading && (
        <div className='absolute bottom-4 left-1/2 z-10 -translate-x-1/2 transform'>
          <GraphLoadingProgressCompact
            progress={state.progress}
            isLoading={state.isLoading}
            onCancel={abort}
          />
        </div>
      )}

      {/* Graph Canvas */}
      <Card
        className={`h-full min-h-[600px] w-full cursor-${isPanning ? 'grabbing' : 'grab'} overflow-hidden`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg
          className='h-full w-full'
          viewBox={`${viewport.minX} ${viewport.minY} ${viewport.maxX - viewport.minX} ${viewport.maxY - viewport.minY}`}
        >
          {/* Render edges */}
          <g className='edges'>
            {state.edges.map((edge) => {
              const source = state.nodes.find((n) => n.id === edge.sourceId);
              const target = state.nodes.find((n) => n.id === edge.targetId);

              if (!source || !target) {
                return null;
              }

              return (
                <line
                  key={edge.id}
                  x1={source.position.x}
                  y1={source.position.y}
                  x2={target.position.x}
                  y2={target.position.y}
                  stroke='currentColor'
                  strokeWidth={2 / zoom}
                  className='text-muted-foreground/30'
                />
              );
            })}
          </g>

          {/* Render nodes */}
          <g className='nodes'>
            {state.nodes.map((node) => (
              <g key={node.id} transform={`translate(${node.position.x}, ${node.position.y})`}>
                <circle
                  r={20 / zoom}
                  fill='currentColor'
                  className='text-primary'
                  stroke='white'
                  strokeWidth={2 / zoom}
                />
                <text
                  y={30 / zoom}
                  textAnchor='middle'
                  fontSize={12 / zoom}
                  fill='currentColor'
                  className='text-foreground select-none'
                >
                  {node.label}
                </text>
              </g>
            ))}
          </g>
        </svg>
      </Card>

      {/* Stats */}
      <div className='text-muted-foreground mt-4 flex justify-between text-xs'>
        <div>
          Nodes: <span className='font-mono'>{state.nodes.length}</span> | Edges:{' '}
          <span className='font-mono'>{state.edges.length}</span>
        </div>
        <div>
          Zoom: <span className='font-mono'>{zoom.toFixed(2)}x</span>
        </div>
        {state.metadata && (
          <div>
            Total: <span className='font-mono'>{state.metadata.totalNodes}</span> nodes,{' '}
            <span className='font-mono'>{state.metadata.totalEdges}</span> edges
          </div>
        )}
      </div>

      {/* Error display */}
      {state.error && (
        <div className='bg-destructive/10 text-destructive mt-4 rounded-lg p-4 text-sm'>
          <strong>Error loading graph:</strong> {state.error.message}
        </div>
      )}
    </div>
  );
}

/**
 * Example usage in a page component
 */
export function StreamingGraphViewExample() {
  const [projectId] = useState('example-project-id');

  return (
    <div className='container mx-auto p-6'>
      <div className='mb-6'>
        <h1 className='mb-2 text-2xl font-bold'>Streaming Graph View</h1>
        <p className='text-muted-foreground'>
          Real-time incremental loading with predictive prefetch
        </p>
      </div>

      <StreamingGraphView
        projectId={projectId}
        showProgress
        enablePrefetch
        onViewportChange={(_viewport) => {}}
      />
    </div>
  );
}

export default StreamingGraphView;
