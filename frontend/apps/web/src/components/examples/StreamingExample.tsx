/**
 * Example component demonstrating NDJSON streaming usage
 */

import type { ChangeEvent } from 'react';

import { useCallback, useMemo, useState } from 'react';

import type { StreamingStats } from '../../lib/ndjson-parser';

import { useStreamExport, useStreamGraph, useStreamItems } from '../../hooks/useStreaming';
import { StreamingProgress, StreamingProgressBar } from '../StreamingProgress';

const SLICE_SIZE = 10;
const PREVIEW_SIZE = 3;
const DATE_SPLIT_INDEX = 0;

const getItemKey = (item: { id?: string }, index: number) => `item-${item.id ?? index}`;

const getNodeKey = (node: { id?: string }, index: number) => `node-${node.id ?? index}`;

interface ErrorNoticeProps {
  error?: Error | undefined;
}

const ErrorNotice = ({ error }: ErrorNoticeProps) => {
  if (!error) {
    return null;
  }
  return (
    <div className='bg-destructive/10 text-destructive rounded p-3'>Error: {error.message}</div>
  );
};

interface ItemsListProps {
  items: unknown[];
}

const ItemsList = ({ items }: ItemsListProps) => (
  <div className='space-y-2'>
    <h4 className='font-medium'>Received Items ({items.length})</h4>
    <div className='max-h-64 space-y-1 overflow-y-auto'>
      {items.map((item, index) => (
        <div
          key={getItemKey(item as { id?: string }, index)}
          className='bg-muted rounded p-2 text-sm'
        >
          {JSON.stringify(item)}
        </div>
      ))}
    </div>
  </div>
);

interface ItemsControlsProps {
  isStreaming: boolean;
  onReset: () => void;
  onStart: () => void;
  onStop: () => void;
  projectId: string;
  onProjectIdChange: (value: string) => void;
}

const ItemsControls = ({
  isStreaming,
  onReset,
  onStart,
  onStop,
  projectId,
  onProjectIdChange,
}: ItemsControlsProps) => {
  const handleInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onProjectIdChange(event.target.value);
    },
    [onProjectIdChange],
  );

  return (
    <div className='flex gap-2'>
      <input
        type='text'
        placeholder='Project ID'
        value={projectId}
        onChange={handleInputChange}
        className='rounded border px-3 py-2'
        disabled={isStreaming}
      />
      <button
        onClick={onStart}
        disabled={isStreaming || !projectId}
        className='bg-primary rounded px-4 py-2 text-white disabled:opacity-50'
      >
        Start Streaming
      </button>
      <button
        onClick={onStop}
        disabled={!isStreaming}
        className='bg-destructive rounded px-4 py-2 text-white disabled:opacity-50'
      >
        Stop
      </button>
      <button
        onClick={onReset}
        disabled={isStreaming}
        className='bg-secondary rounded px-4 py-2 disabled:opacity-50'
      >
        Reset
      </button>
    </div>
  );
};

const StreamItemsExample = () => {
  const [projectId, setProjectId] = useState('');
  const { items, state, startStreaming, stopStreaming, reset } = useStreamItems();

  const handleStart = useCallback(() => {
    if (projectId) {
      startStreaming({ projectId });
    }
  }, [projectId, startStreaming]);

  const displayItems = useMemo(() => items.slice(-SLICE_SIZE), [items]);

  return (
    <div className='space-y-4 rounded-lg border p-4'>
      <h3 className='text-lg font-semibold'>Stream Items Example</h3>

      <ItemsControls
        isStreaming={state.isStreaming}
        onReset={reset}
        onStart={handleStart}
        onStop={stopStreaming}
        projectId={projectId}
        onProjectIdChange={setProjectId}
      />

      <StreamingProgress
        stats={state.stats}
        isStreaming={state.isStreaming}
        showThroughput
        showBytes
      />

      <ErrorNotice error={state.error ?? undefined} />

      <ItemsList items={displayItems} />
    </div>
  );
};

interface GraphControlsProps {
  graphId: string;
  isStreaming: boolean;
  onGraphIdChange: (value: string) => void;
  onReset: () => void;
  onStart: () => void;
  onStop: () => void;
}

const GraphControls = ({
  graphId,
  isStreaming,
  onGraphIdChange,
  onReset,
  onStart,
  onStop,
}: GraphControlsProps) => {
  const handleInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onGraphIdChange(event.target.value);
    },
    [onGraphIdChange],
  );

  return (
    <div className='flex gap-2'>
      <input
        type='text'
        placeholder='Graph ID'
        value={graphId}
        onChange={handleInputChange}
        className='rounded border px-3 py-2'
        disabled={isStreaming}
      />
      <button
        onClick={onStart}
        disabled={isStreaming || !graphId}
        className='bg-primary rounded px-4 py-2 text-white disabled:opacity-50'
      >
        Stream Graph
      </button>
      <button
        onClick={onStop}
        disabled={!isStreaming}
        className='bg-destructive rounded px-4 py-2 text-white disabled:opacity-50'
      >
        Stop
      </button>
      <button
        onClick={onReset}
        disabled={isStreaming}
        className='bg-secondary rounded px-4 py-2 disabled:opacity-50'
      >
        Reset
      </button>
    </div>
  );
};

interface GraphStatsProps {
  edgeCount: number;
  nodeCount: number;
}

const GraphStats = ({ edgeCount, nodeCount }: GraphStatsProps) => (
  <div className='grid grid-cols-2 gap-4'>
    <div className='bg-muted rounded p-3'>
      <div className='text-muted-foreground text-sm'>Nodes</div>
      <div className='text-2xl font-bold'>{nodeCount}</div>
    </div>
    <div className='bg-muted rounded p-3'>
      <div className='text-muted-foreground text-sm'>Edges</div>
      <div className='text-2xl font-bold'>{edgeCount}</div>
    </div>
  </div>
);

interface GraphPreviewProps {
  nodes: unknown[];
  previewNodes: unknown[];
  remainingCount: number;
}

const GraphPreview = ({ nodes, previewNodes, remainingCount }: GraphPreviewProps) => (
  <div className='bg-muted/50 rounded p-4'>
    <div className='text-muted-foreground mb-2 text-sm'>Graph Preview</div>
    <div className='space-y-1 text-xs'>
      {previewNodes.map((node, index) => (
        <div key={getNodeKey(node as { id?: string }, index)}>Node: {JSON.stringify(node)}</div>
      ))}
      {remainingCount > 0 && <div>... and {remainingCount} more</div>}
    </div>
    {nodes.length === 0 && <div className='text-muted-foreground text-xs'>No nodes yet</div>}
  </div>
);

const StreamGraphExample = () => {
  const [graphId, setGraphId] = useState('');
  const { nodes, edges, state, startStreaming, stopStreaming, reset } = useStreamGraph();

  const handleStart = useCallback(() => {
    if (graphId) {
      startStreaming(graphId);
    }
  }, [graphId, startStreaming]);

  const previewNodes = useMemo(() => nodes.slice(0, PREVIEW_SIZE), [nodes]);
  const remainingCount = Math.max(0, nodes.length - PREVIEW_SIZE);

  return (
    <div className='space-y-4 rounded-lg border p-4'>
      <h3 className='text-lg font-semibold'>Stream Graph Example</h3>

      <GraphControls
        graphId={graphId}
        isStreaming={state.isStreaming}
        onGraphIdChange={setGraphId}
        onReset={reset}
        onStart={handleStart}
        onStop={stopStreaming}
      />

      <StreamingProgress stats={state.stats} isStreaming={state.isStreaming} showThroughput />

      <GraphStats edgeCount={edges.length} nodeCount={nodes.length} />

      <GraphPreview nodes={nodes} previewNodes={previewNodes} remainingCount={remainingCount} />
    </div>
  );
};

interface ExportControlsProps {
  isStreaming: boolean;
  onExportTypeChange: (value: 'json' | 'csv') => void;
  onProjectIdChange: (value: string) => void;
  onStart: () => void;
  onStop: () => void;
  projectId: string;
  value: 'json' | 'csv';
}

const ExportControls = ({
  isStreaming,
  onExportTypeChange,
  onProjectIdChange,
  onStart,
  onStop,
  projectId,
  value,
}: ExportControlsProps) => {
  const handleProjectChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onProjectIdChange(event.target.value);
    },
    [onProjectIdChange],
  );

  const handleTypeChange = useCallback(
    (event: ChangeEvent<HTMLSelectElement>) => {
      const nextType = event.target.value === 'csv' ? 'csv' : 'json';
      onExportTypeChange(nextType);
    },
    [onExportTypeChange],
  );

  return (
    <div className='flex gap-2'>
      <input
        type='text'
        placeholder='Project ID'
        value={projectId}
        onChange={handleProjectChange}
        className='rounded border px-3 py-2'
        disabled={isStreaming}
      />
      <select
        value={value}
        onChange={handleTypeChange}
        className='rounded border px-3 py-2'
        disabled={isStreaming}
      >
        <option value='json'>JSON</option>
        <option value='csv'>CSV</option>
      </select>
      <button
        onClick={onStart}
        disabled={isStreaming || !projectId}
        className='bg-primary rounded px-4 py-2 text-white disabled:opacity-50'
      >
        Start Export
      </button>
      <button
        onClick={onStop}
        disabled={!isStreaming}
        className='bg-destructive rounded px-4 py-2 text-white disabled:opacity-50'
      >
        Stop
      </button>
    </div>
  );
};

interface ExportActionsProps {
  canDownload: boolean;
  isStreaming: boolean;
  onDownload: () => void;
  onReset: () => void;
}

interface ExportSizeProps {
  count: number;
}

const ExportSize = ({ count }: ExportSizeProps) => (
  <div className='bg-muted rounded p-3'>
    <div className='text-muted-foreground text-sm'>Export Size</div>
    <div className='text-2xl font-bold'>{count} items</div>
  </div>
);

const ExportActions = ({ canDownload, isStreaming, onDownload, onReset }: ExportActionsProps) => (
  <div className='space-y-2'>
    {canDownload && (
      <button onClick={onDownload} className='bg-primary rounded px-4 py-2 text-white'>
        Download Export
      </button>
    )}
    <button
      onClick={onReset}
      disabled={isStreaming}
      className='bg-secondary rounded px-4 py-2 disabled:opacity-50'
    >
      Reset
    </button>
  </div>
);

const StreamExportExample = () => {
  const [projectId, setProjectId] = useState('');
  const [exportType, setExportType] = useState<'json' | 'csv'>('json');
  const { data, state, startExport, stopExport, downloadAsFile, reset } = useStreamExport();

  const handleStart = useCallback(() => {
    if (projectId) {
      startExport({ projectId, type: exportType });
    }
  }, [exportType, projectId, startExport]);

  const handleDownload = useCallback(() => {
    const timestamp = new Date().toISOString().split('T')[DATE_SPLIT_INDEX];
    downloadAsFile(`export-${projectId}-${timestamp}.json`);
  }, [downloadAsFile, projectId]);

  const canDownload = data.length > 0 && !state.isStreaming;

  return (
    <div className='space-y-4 rounded-lg border p-4'>
      <h3 className='text-lg font-semibold'>Stream Export Example</h3>

      <ExportControls
        isStreaming={state.isStreaming}
        onExportTypeChange={setExportType}
        onProjectIdChange={setProjectId}
        onStart={handleStart}
        onStop={stopExport}
        projectId={projectId}
        value={exportType}
      />

      <div className='space-y-2'>
        <StreamingProgress
          stats={state.stats ?? null}
          isStreaming={state.isStreaming}
          showThroughput
          showBytes
        />
        {state.stats != null && (
          <StreamingProgressBar
            current={'itemsReceived' in state.stats ? state.stats.itemsReceived : 0}
            isStreaming={state.isStreaming}
          />
        )}
      </div>

      <ExportSize count={data.length} />

      <ExportActions
        canDownload={canDownload}
        isStreaming={state.isStreaming}
        onDownload={handleDownload}
        onReset={reset}
      />
    </div>
  );
};

const StreamingExamples = () => (
  <div className='space-y-8 p-6'>
    <h2 className='text-2xl font-bold'>NDJSON Streaming Examples</h2>
    <div className='grid gap-6'>
      <StreamItemsExample />
      <StreamGraphExample />
      <StreamExportExample />
    </div>
  </div>
);

export { StreamExportExample, StreamGraphExample, StreamItemsExample, StreamingExamples };
