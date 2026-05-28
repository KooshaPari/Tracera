/**
 * UICodeTracePanel Live Integration
 *
 * Wires UICodeTracePanel to the real backend endpoint:
 *   GET /api/v1/analysis/code-trace/{component_id}
 *
 * Closes: https://github.com/KooshaPari/trace/issues/226
 */

import React, { useCallback, useEffect, useState } from 'react';

import type { CodeReference } from '@tracertm/types';

import { codeTraceApi } from '@/api/endpoints';
import { logger } from '@/lib/logger';

import type { UICodeTraceChain } from './UICodeTracePanel';

import { UICodeTracePanel } from './UICodeTracePanel';

// =============================================================================
// HOOK: useUICodeTrace
// Fetches and manages live trace-chain state for a given component ID.
// =============================================================================

interface UseUICodeTraceResult {
  traceChain: UICodeTraceChain | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useUICodeTrace(
  componentId: string | null | undefined,
  projectId?: string,
): UseUICodeTraceResult {
  const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChain = useCallback(async () => {
    if (!componentId) {
      setTraceChain(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const raw = await codeTraceApi.getChain(componentId, projectId);

      // Adapt backend response to UICodeTraceChain shape expected by the panel
      const chain: UICodeTraceChain = {
        id: raw.id,
        name: raw.name,
        description: raw.description,
        overallConfidence: raw.overallConfidence,
        lastUpdated: raw.lastUpdated,
        levels: raw.levels.map((lvl) => ({
          id: lvl.id,
          type: lvl.type,
          title: lvl.title,
          description: lvl.description,
          confidence: lvl.confidence,
          strategy: lvl.strategy as UICodeTraceChain['levels'][number]['strategy'],
          isConfirmed: lvl.isConfirmed,
          componentName: lvl.componentName,
          componentPath: lvl.componentPath,
          screenshot: lvl.screenshot,
          codeRef: lvl.codeRef
            ? ({
                id: lvl.id,
                symbolName: lvl.codeRef.symbolName,
                symbolType: (lvl.codeRef.symbolType ?? 'function') as CodeReference['symbolType'],
                filePath: lvl.codeRef.filePath ?? '',
                startLine: lvl.codeRef.startLine,
                endLine: lvl.codeRef.endLine,
                signature: lvl.codeRef.signature,
                language: 'unknown',
              } satisfies CodeReference)
            : undefined,
          requirementId: lvl.requirementId,
          businessValue: lvl.businessValue,
        })),
      };

      setTraceChain(chain);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load trace chain';
      logger.error('[UICodeTracePanel] fetch error:', err);
      setError(message);
      setTraceChain(null);
    } finally {
      setIsLoading(false);
    }
  }, [componentId, projectId]);

  useEffect(() => {
    void fetchChain();
  }, [fetchChain]);

  return { traceChain, isLoading, error, refresh: fetchChain };
}

// =============================================================================
// LiveUICodeTracePanel
// Drop-in replacement for the panel — accepts a componentId and handles all
// API concerns internally.  All interaction callbacks are optional overrides.
// =============================================================================

export interface LiveUICodeTracePanelProps {
  /** UUID of the item to trace (UI component, code symbol, or requirement). */
  componentId: string | null | undefined;
  /** Optional project scope for the query. */
  projectId?: string;
  /** Called when the user clicks "Open in Editor" on a code level. */
  onOpenCode?: (codeRef: CodeReference) => void;
  /** Called when the user clicks "View Requirement". */
  onOpenRequirement?: (requirementId: string) => void;
  /** Called when the user navigates to a UI component. */
  onNavigateToUI?: (componentPath: string) => void;
}

export function LiveUICodeTracePanel({
  componentId,
  projectId,
  onOpenCode,
  onOpenRequirement,
  onNavigateToUI,
}: LiveUICodeTracePanelProps) {
  const { traceChain, isLoading, error, refresh } = useUICodeTrace(componentId, projectId);

  const handleOpenCode = useCallback(
    (codeRef: CodeReference) => {
      if (onOpenCode) {
        onOpenCode(codeRef);
        return;
      }
      // Default: open in VS Code
      if (codeRef.filePath) {
        const line = codeRef.startLine ? `:${codeRef.startLine}` : '';
        window.open(`vscode://file/${codeRef.filePath}${line}`);
      }
    },
    [onOpenCode],
  );

  const handleOpenRequirement = useCallback(
    (requirementId: string) => {
      if (onOpenRequirement) {
        onOpenRequirement(requirementId);
        return;
      }
      globalThis.location.href = `/items/${requirementId}`;
    },
    [onOpenRequirement],
  );

  const handleNavigateToUI = useCallback(
    (componentPath: string) => {
      if (onNavigateToUI) {
        onNavigateToUI(componentPath);
        return;
      }
      globalThis.location.href = `/components/${componentPath}`;
    },
    [onNavigateToUI],
  );

  return (
    <div className='space-y-2'>
      {/* Error banner */}
      {error && !isLoading && (
        <div className='rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800'>
          <span className='font-semibold'>Error: </span>
          {error}
          <button
            onClick={() => void refresh()}
            className='ml-2 text-red-700 underline hover:text-red-900'
          >
            Retry
          </button>
        </div>
      )}

      <UICodeTracePanel
        traceChain={traceChain}
        isLoading={isLoading}
        onOpenCode={handleOpenCode}
        onOpenRequirement={handleOpenRequirement}
        onNavigateToUI={handleNavigateToUI}
        onRefreshTrace={() => void refresh()}
      />
    </div>
  );
}

// =============================================================================
// EXAMPLE: BasicUICodeTracePanelExample (updated — uses live hook)
// =============================================================================

export function BasicUICodeTracePanelExample() {
  const [componentId, setComponentId] = React.useState<string>('');
  const [submittedId, setSubmittedId] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittedId(componentId.trim() || null);
  };

  return (
    <div className='space-y-4 p-4'>
      <form onSubmit={handleSubmit} className='flex gap-2'>
        <input
          type='text'
          placeholder='Enter component UUID'
          value={componentId}
          onChange={(e) => {
            setComponentId(e.target.value);
          }}
          className='flex-1 rounded border px-3 py-2 text-sm'
        />
        <button
          type='submit'
          className='rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700'
        >
          Load Trace
        </button>
      </form>

      <LiveUICodeTracePanel componentId={submittedId} />
    </div>
  );
}

// =============================================================================
// EXAMPLE: SidePanelLayoutExample (updated — uses live hook)
// =============================================================================

const DEMO_COMPONENTS = ['LoginForm', 'NavBar', 'Dashboard'] as const;

export function SidePanelLayoutExample({
  componentIdMap = {},
}: {
  componentIdMap?: Record<string, string>;
}) {
  const [selectedName, setSelectedName] = React.useState<string | null>(null);
  const selectedId = selectedName ? (componentIdMap[selectedName] ?? null) : null;

  return (
    <div className='flex h-screen gap-4'>
      {/* Component list */}
      <div className='flex-1 overflow-auto border-r p-4'>
        <h2 className='mb-4 text-lg font-semibold'>Components</h2>
        <div className='space-y-2'>
          {DEMO_COMPONENTS.map((name) => (
            <button
              key={name}
              onClick={() => {
                setSelectedName(name);
              }}
              className={`block w-full rounded px-4 py-2 text-left ${
                selectedName === name ? 'bg-blue-100 text-blue-900' : 'hover:bg-gray-100'
              }`}
            >
              {name}
            </button>
          ))}
        </div>
      </div>

      {/* Side panel */}
      <div className='w-96 overflow-auto border-l bg-gray-50 p-4'>
        {selectedId ? (
          <LiveUICodeTracePanel componentId={selectedId} />
        ) : (
          <p className='text-sm text-gray-500'>Select a component to view its trace chain.</p>
        )}
      </div>
    </div>
  );
}
