/**
 * Safe Graph Components - Graph components wrapped with error boundaries
 *
 * This file provides error-boundary-wrapped versions of critical graph components
 * to prevent entire page crashes when a graph rendering error occurs.
 */

import { ErrorBoundary } from '@/components/ErrorBoundary';
import { LoadingSpinner } from '@/components/layout/LoadingSpinner';

import { EnhancedGraphView } from './EnhancedGraphView';
import { FlowGraphView } from './FlowGraphView';
import { GraphViewContainer } from './GraphViewContainer';
import { UnifiedGraphView } from './UnifiedGraphView';
import { VirtualizedGraphView } from './VirtualizedGraphView';

// Loading fallback for graph components
const GraphLoadingFallback = () => (
  <div className='bg-muted/5 flex h-full min-h-[400px] items-center justify-center'>
    <div className='text-muted-foreground'>
      <LoadingSpinner text='Loading graph...' />
    </div>
  </div>
);

// Error fallback for graph components
const GraphErrorFallback = (error: Error, reset: () => void) => (
  <div className='border-destructive/50 bg-destructive/5 flex h-full min-h-[400px] items-center justify-center rounded-lg border-2 border-dashed p-8'>
    <div className='max-w-md space-y-4 text-center'>
      <h3 className='text-destructive text-lg font-semibold'>Graph Rendering Error</h3>
      <p className='text-muted-foreground text-sm'>
        {error.message || 'Unable to render graph visualization'}
      </p>
      <button
        onClick={reset}
        className='bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2 transition-colors'
      >
        Retry
      </button>
    </div>
  </div>
);

/**
 * Safe wrapper for GraphViewContainer with error boundary and lazy loading
 */
export const SafeGraphViewContainer = (props: React.ComponentProps<typeof GraphViewContainer>) => (
  <ErrorBoundary name='GraphViewContainer' fallback={GraphErrorFallback}>
    <GraphViewContainer {...props} />
  </ErrorBoundary>
);

/**
 * Safe wrapper for FlowGraphView with error boundary and lazy loading
 */
export const SafeFlowGraphView = (props: React.ComponentProps<typeof FlowGraphView>) => (
  <ErrorBoundary name='FlowGraphView' fallback={GraphErrorFallback}>
    <FlowGraphView {...props} />
  </ErrorBoundary>
);

/**
 * Safe wrapper for EnhancedGraphView with error boundary and lazy loading
 */
export const SafeEnhancedGraphView = (props: React.ComponentProps<typeof EnhancedGraphView>) => (
  <ErrorBoundary name='EnhancedGraphView' fallback={GraphErrorFallback}>
    <EnhancedGraphView {...props} />
  </ErrorBoundary>
);

/**
 * Safe wrapper for VirtualizedGraphView with error boundary and lazy loading
 */
export const SafeVirtualizedGraphView = (
  props: React.ComponentProps<typeof VirtualizedGraphView>,
) => (
  <ErrorBoundary name='VirtualizedGraphView' fallback={GraphErrorFallback}>
    <VirtualizedGraphView {...props} />
  </ErrorBoundary>
);

/**
 * Safe wrapper for UnifiedGraphView with error boundary and lazy loading
 */
export const SafeUnifiedGraphView = (props: React.ComponentProps<typeof UnifiedGraphView>) => (
  <ErrorBoundary name='UnifiedGraphView' fallback={GraphErrorFallback}>
    <UnifiedGraphView {...props} />
  </ErrorBoundary>
);
