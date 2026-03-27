/**
 * UICodeTracePanel Integration Examples
 * Demonstrates how to integrate the UICodeTracePanel component with your application
 */

import React, { useCallback, useState } from 'react';

import type { CodeReference } from '@tracertm/types';

import { logger } from '@/lib/logger';

import type { UICodeTraceChain } from './UICodeTracePanel';

import { UICodeTracePanel } from './UICodeTracePanel';

// =============================================================================
// EXAMPLE 1: Basic Integration with State Management
// =============================================================================

/**
 * Basic example showing how to manage trace chain state
 * and handle user interactions
 */
export function BasicUICodeTracePanelExample() {
  const [traceChain, _setTraceChain] = useState<UICodeTraceChain | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Simulate fetching trace chain from API
  /*
	Const handleFetchTraceChain = useCallback(async (componentId: string) => {
		setIsLoading(true);
		try {
			// In real app, call your tRPC endpoint
			// const trace = await trpc.traces.getUICodeTrace.query({ componentId });
			// setTraceChain(trace);

			// Mock delay
			await new Promise((resolve) => setTimeout(resolve, 1000));
			// Mock data would be set here
		} finally {
			setIsLoading(false);
		}
	}, []);
	*/

  const handleOpenCode = useCallback((codeRef: CodeReference) => {
    // Option 1: VS Code Extension
    if (codeRef.filePath) {
      const lineParam = codeRef.startLine ? `:${codeRef.startLine}` : '';
      window.open(`vscode://open?${codeRef.filePath}${lineParam}`);
    }
  }, []);

  const handleOpenRequirement = useCallback((requirementId: string) => {
    // Navigate to requirement detail page
    globalThis.location.href = `/items/${requirementId}`;
  }, []);

  const handleNavigateToUI = useCallback((componentPath: string) => {
    // Navigate to component file or preview
    globalThis.location.href = `/components/${componentPath}`;
  }, []);

  const handleRefreshTrace = useCallback(async () => {
    if (traceChain) {
      setIsLoading(true);
      try {
        // Refetch the trace chain
        // Const fresh = await trpc.traces.getUICodeTrace.query({
        //   ComponentId: traceChain.id
        // });
        // SetTraceChain(fresh);
      } finally {
        setIsLoading(false);
      }
    }
  }, [traceChain]);

  return (
    <UICodeTracePanel
      traceChain={traceChain}
      isLoading={isLoading}
      onOpenCode={handleOpenCode}
      onOpenRequirement={handleOpenRequirement}
      onNavigateToUI={handleNavigateToUI}
      onRefreshTrace={handleRefreshTrace}
    />
  );
}

// =============================================================================
// EXAMPLE 2: Integration with tRPC Query
// =============================================================================

/**
 * Example using tRPC with React Query for data fetching
 * Requires: trpc client and React Query setup
 */
export function TRPCIntegrationExample() {
  const [selectedComponentId, setSelectedComponentId] = useState<string | null>(null);

  // Example tRPC query (you need to set this up in your router)
  // Const { data: traceChain, isLoading, refetch } = trpc.traces.getUICodeTrace.useQuery(
  //   { componentId: selectedComponentId! },
  //   { enabled: !!selectedComponentId }
  // );

  // For now, using mock data
  const traceChain: UICodeTraceChain | null = null;
  const isLoading = false;

  const handleOpenCode = useCallback((codeRef: CodeReference) => {
    // Open code in editor
    logger.info('Open code:', codeRef);
  }, []);

  const handleRefresh = useCallback(async () => {
    // Refetch(); // If using tRPC
  }, []);

  return (
    <div className='space-y-4'>
      {/* Component selector */}
      <div>
        <label className='mb-2 block text-sm font-medium'>Select Component:</label>
        <input
          type='text'
          placeholder='Enter component ID'
          value={selectedComponentId ?? ''}
          onChange={(e) => {
            setSelectedComponentId(e.target.value);
          }}
          className='w-full rounded border px-3 py-2'
        />
      </div>

      {/* Trace panel */}
      <UICodeTracePanel
        traceChain={traceChain}
        isLoading={isLoading}
        onOpenCode={handleOpenCode}
        onRefreshTrace={handleRefresh}
      />
    </div>
  );
}

// =============================================================================
// EXAMPLE 3: Integration with Atoms/State Atom
// =============================================================================

/**
 * Example using Jotai atoms for state management
 * Requires: jotai setup
 */
export function AtomStateIntegrationExample() {
  // In real app:
  // Const [selectedTrace, setSelectedTrace] = useAtom(selectedTraceAtom);
  // Const [traceHistory, setTraceHistory] = useAtom(traceHistoryAtom);

  // Mock state
  const [selectedTrace, _setSelectedTrace] = useState<UICodeTraceChain | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefreshTrace = useCallback(async () => {
    setIsRefreshing(true);
    try {
      // Fetch fresh trace data
      // Const fresh = await api.traces.getUICodeTrace(selectedTrace?.id);
      // SetSelectedTrace(fresh);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  return (
    <UICodeTracePanel
      traceChain={selectedTrace}
      isLoading={isRefreshing}
      onRefreshTrace={handleRefreshTrace}
    />
  );
}

// =============================================================================
// EXAMPLE 4: Integration with Side Panel Layout
// =============================================================================

/**
 * Example showing UICodeTracePanel in a side panel layout
 * Common pattern for detailed views
 */
export function SidePanelLayoutExample() {
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [traceChain, _setTraceChain] = useState<UICodeTraceChain | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSelectItem = useCallback(async (itemId: string) => {
    setSelectedItemId(itemId);
    setIsLoading(true);
    try {
      // Fetch trace chain for selected item
      // Const trace = await api.traces.getUICodeTrace({ componentId: itemId });
      // SetTraceChain(trace);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className='flex h-screen gap-4'>
      {/* Main content area */}
      <div className='flex-1 overflow-auto border-r p-4'>
        <h2 className='mb-4 text-lg font-semibold'>Components</h2>
        {/* List of components */}
        <div className='space-y-2'>
          {['LoginForm', 'NavBar', 'Dashboard'].map((name) => (
            <button
              key={name}
              onClick={async () => handleSelectItem(name)}
              className={`block w-full rounded px-4 py-2 text-left ${
                selectedItemId === name ? 'bg-blue-100 text-blue-900' : 'hover:bg-gray-100'
              }`}
            >
              {name}
            </button>
          ))}
        </div>
      </div>

      {/* Side panel with trace */}
      <div className='w-96 overflow-auto border-l bg-gray-50 p-4'>
        <UICodeTracePanel
          traceChain={traceChain}
          isLoading={isLoading}
          onOpenCode={(codeRef) => {
            logger.info('Open code:', codeRef);
          }}
          onRefreshTrace={async () => {
            if (traceChain) {
              setIsLoading(true);
              try {
                // Refetch trace
              } finally {
                setIsLoading(false);
              }
            }
          }}
        />
      </div>
    </div>
  );
}

// =============================================================================
// EXAMPLE 5: Integration with Modal Dialog
// =============================================================================

/**
 * Example showing UICodeTracePanel in a modal dialog
 * Good for detailed trace inspection
 */
export function ModalDialogExample() {
  const [isOpen, setIsOpen] = useState(false);
  const [traceChain, _setTraceChain] = useState<UICodeTraceChain | null>(null);

  const handleOpenTraceModal = useCallback(async (_componentId: string) => {
    // Fetch trace data
    // Const trace = await api.traces.getUICodeTrace({ componentId });
    // SetTraceChain(trace);
    setIsOpen(true);
  }, []);

  return (
    <div>
      {/* Open modal button */}
      <button
        onClick={async () => handleOpenTraceModal('component-1')}
        className='rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700'
      >
        View Trace
      </button>

      {/* Modal dialog */}
      {isOpen && (
        <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/50'>
          <div className='flex max-h-[90vh] w-full max-w-2xl flex-col rounded-lg bg-white shadow-xl'>
            {/* Modal header */}
            <div className='flex items-center justify-between border-b p-4'>
              <h2 className='text-lg font-semibold'>Traceability Chain</h2>
              <button
                onClick={() => {
                  setIsOpen(false);
                }}
                className='text-gray-500 hover:text-gray-700'
              >
                ✕
              </button>
            </div>

            {/* Modal content */}
            <div className='flex-1 overflow-auto p-4'>
              <UICodeTracePanel
                traceChain={traceChain}
                onOpenCode={(codeRef) => {
                  window.open(`vscode://open?${codeRef.filePath}:${codeRef.startLine}`);
                }}
              />
            </div>

            {/* Modal footer */}
            <div className='flex justify-end gap-2 border-t p-4'>
              <button
                onClick={() => {
                  setIsOpen(false);
                }}
                className='rounded px-4 py-2 text-gray-600 hover:bg-gray-100'
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// EXAMPLE 6: Integration with Error Handling
// =============================================================================

/**
 * Example showing how to handle errors when fetching trace data
 */
export function ErrorHandlingExample() {
  const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetchTrace = useCallback(async (componentId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // tracked: https://github.com/KooshaPari/trace/issues/225
      // Const trace = await api.traces.getUICodeTrace({ componentId });
      // SetTraceChain(trace);
      undefined;
      setTraceChain(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch trace chain';
      setError(message);
      setTraceChain(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className='space-y-4'>
      {/* Error message */}
      {error && (
        <div className='rounded border border-red-200 bg-red-50 p-4 text-red-800'>
          <p className='font-semibold'>Error</p>
          <p className='mt-1 text-sm'>{error}</p>
          <button
            onClick={async () => handleFetchTrace('component-1')}
            className='mt-2 text-sm text-red-700 underline hover:text-red-900'
          >
            Try again
          </button>
        </div>
      )}

      {/* Trace panel */}
      <UICodeTracePanel traceChain={traceChain} isLoading={isLoading} />
    </div>
  );
}

// =============================================================================
// EXAMPLE 7: Integration with URL Search Params
// =============================================================================

/**
 * Example showing integration with URL query parameters
 * Good for bookmarkable trace chains
 */
export function URLSearchParamsExample() {
  const [traceChain, _setTraceChain] = useState<UICodeTraceChain | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Get componentId from URL
  const searchParams = new URLSearchParams(globalThis.location.search);
  const componentId = searchParams.get('component');

  // Fetch trace when component changes
  const fetchTrace = useCallback(async () => {
    if (!componentId) {
      return;
    }

    setIsLoading(true);
    try {
      // Const trace = await api.traces.getUICodeTrace({ componentId });
      // SetTraceChain(trace);
    } finally {
      setIsLoading(false);
    }
  }, [componentId]);

  // Effect to fetch when component ID changes
  React.useEffect(() => {}, [fetchTrace]);

  return (
    <UICodeTracePanel traceChain={traceChain} isLoading={isLoading} onRefreshTrace={fetchTrace} />
  );
}

// =============================================================================
// EXAMPLE 8: Integration with Breadcrumb Navigation
// =============================================================================

/**
 * Example showing UICodeTracePanel with breadcrumb navigation
 * Helps users understand context in the trace hierarchy
 */
export function BreadcrumbNavigationExample() {
  const [traceChain, _setTraceChain] = useState<UICodeTraceChain | null>(null);
  const [selectedLevelIndex, setSelectedLevelIndex] = useState(0);

  const selectedLevel = traceChain?.levels[selectedLevelIndex];

  return (
    <div className='space-y-4'>
      {/* Breadcrumb navigation */}
      {traceChain && (
        <div className='flex items-center gap-2 text-sm text-gray-600'>
          {traceChain.levels.map((level, index) => (
            <React.Fragment key={level.id}>
              <button
                onClick={() => {
                  setSelectedLevelIndex(index);
                }}
                className={`rounded px-2 py-1 ${
                  index === selectedLevelIndex ? 'bg-blue-100 text-blue-900' : 'hover:bg-gray-100'
                }`}
              >
                {level.title}
              </button>
              {index < traceChain.levels.length - 1 && <span>→</span>}
            </React.Fragment>
          ))}
        </div>
      )}

      {/* Trace panel */}
      <UICodeTracePanel
        traceChain={traceChain}
        onOpenCode={(codeRef) => {
          logger.info('Open code:', codeRef);
        }}
      />

      {/* Selected level details */}
      {selectedLevel && (
        <div className='rounded border border-blue-200 bg-blue-50 p-4'>
          <h3 className='font-semibold text-blue-900'>{selectedLevel.title}</h3>
          <p className='mt-2 text-sm text-blue-800'>{selectedLevel.description}</p>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// EXAMPLE 9: Integration with Analytics/Telemetry
// =============================================================================

/**
 * Example showing how to track user interactions for analytics
 */
export function AnalyticsIntegrationExample() {
  const [traceChain, _setTraceChain] = useState<UICodeTraceChain | null>(null);

  const trackEvent = (eventName: string, data: Record<string, unknown>) => {
    // Send to analytics service
    logger.info('Analytics:', eventName, data);
    // In real app: analytics.track(eventName, data);
  };

  const handleOpenCode = (codeRef: CodeReference) => {
    trackEvent('trace:open_code', {
      filePath: codeRef.filePath,
      symbol: codeRef.symbolName,
    });
  };

  const handleOpenRequirement = (requirementId: string) => {
    trackEvent('trace:open_requirement', {
      requirementId,
    });
  };

  return (
    <UICodeTracePanel
      traceChain={traceChain}
      onOpenCode={handleOpenCode}
      onOpenRequirement={handleOpenRequirement}
      onRefreshTrace={() => {
        trackEvent('trace:refresh', {
          traceId: traceChain?.id,
        });
      }}
    />
  );
}

// =============================================================================
// EXAMPLE 10: Integration with Export/Share
// =============================================================================

/**
 * Example showing how to export trace chain as JSON or PDF
 */
export function ExportShareExample() {
  const [traceChain, _setTraceChain] = useState<UICodeTraceChain | null>(null);

  const handleExportJSON = () => {
    if (!traceChain) {
      return;
    }

    const json = JSON.stringify(traceChain, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trace-${traceChain.id}.json`;
    a.click();
  };

  const handleCopyShareLink = () => {};

  return (
    <div className='space-y-4'>
      <UICodeTracePanel traceChain={traceChain} />

      {/* Export controls */}
      {traceChain && (
        <div className='flex gap-2'>
          <button
            onClick={handleExportJSON}
            className='rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700'
          >
            Export JSON
          </button>
          <button
            onClick={handleCopyShareLink}
            className='rounded bg-purple-600 px-4 py-2 text-white hover:bg-purple-700'
          >
            Copy Share Link
          </button>
        </div>
      )}
    </div>
  );
}
