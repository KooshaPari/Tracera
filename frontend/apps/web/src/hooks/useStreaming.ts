/**
 * React hooks for NDJSON streaming with progress tracking
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import type { StreamExportOptions, StreamGraphOptions, StreamItemsOptions } from '../api/streaming';
import type { Item } from '../api/types';
import type { NDJSONMetadata, StreamingStats } from '../lib/ndjson-parser';

import {
  createCancellableExportStream,
  createCancellableGraphStream,
  createCancellableItemStream,
  streamExport,
  streamGraph,
  streamItems,
} from '../api/streaming';

export interface StreamingState {
  isStreaming: boolean;
  stats: StreamingStats | null;
  error: Error | null;
  metadata: NDJSONMetadata[];
}

export interface UseStreamItemsResult {
  items: Item[];
  state: StreamingState;
  startStreaming: (options?: StreamItemsOptions) => Promise<void>;
  stopStreaming: () => void;
  reset: () => void;
}

/**
 * Hook for streaming items with progress tracking
 */
export function useStreamItems(): UseStreamItemsResult {
  const [items, setItems] = useState<Item[]>([]);
  const [state, setState] = useState<StreamingState>({
    error: null,
    isStreaming: false,
    metadata: [],
    stats: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const startStreaming = useCallback(async (options: StreamItemsOptions = {}) => {
    // Reset state
    setItems([]);
    setState({
      error: null,
      isStreaming: true,
      metadata: [],
      stats: null,
    });

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      const streamOptions: StreamItemsOptions = {
        ...options,
        onProgress: (stats) => {
          setState((prev) => ({
            ...prev,
            stats,
          }));
          options.onProgress?.(stats);
        },
        onMetadata: (metadata) => {
          setState((prev) => ({
            ...prev,
            metadata: [...prev.metadata, metadata],
          }));
          options.onMetadata?.(metadata);
        },
      };

      const receivedItems: Item[] = [];

      for await (const item of streamItems(streamOptions)) {
        // Check if streaming was cancelled
        if (abortControllerRef.current?.signal.aborted) {
          break;
        }

        receivedItems.push(item);

        // Update items in batches for better performance
        if (receivedItems.length % 10 === 0) {
          setItems([...receivedItems]);
        }
      }

      // Final update
      setItems(receivedItems);

      setState((prev) => ({
        ...prev,
        isStreaming: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isStreaming: false,
        error: error as Error,
      }));
    }
  }, []);

  const stopStreaming = useCallback(() => {
    abortControllerRef.current?.abort();
    setState((prev) => ({
      ...prev,
      isStreaming: false,
    }));
  }, []);

  const reset = useCallback(() => {
    stopStreaming();
    setItems([]);
    setState({
      error: null,
      isStreaming: false,
      metadata: [],
      stats: null,
    });
  }, [stopStreaming]);

  // Cleanup on unmount
  useEffect(
    () => () => {
      abortControllerRef.current?.abort();
    },
    [],
  );

  return {
    items,
    reset,
    startStreaming,
    state,
    stopStreaming,
  };
}

export interface UseStreamGraphResult {
  nodes: any[];
  edges: any[];
  state: StreamingState;
  startStreaming: (graphId: string, options?: StreamGraphOptions) => Promise<void>;
  stopStreaming: () => void;
  reset: () => void;
}

/**
 * Hook for streaming graph data with progress tracking
 */
export function useStreamGraph(): UseStreamGraphResult {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [state, setState] = useState<StreamingState>({
    error: null,
    isStreaming: false,
    metadata: [],
    stats: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const startStreaming = useCallback(async (graphId: string, options: StreamGraphOptions = {}) => {
    // Reset state
    setNodes([]);
    setEdges([]);
    setState({
      error: null,
      isStreaming: true,
      metadata: [],
      stats: null,
    });

    abortControllerRef.current = new AbortController();

    try {
      const streamOptions: StreamGraphOptions = {
        ...options,
        onProgress: (stats) => {
          setState((prev) => ({
            ...prev,
            stats,
          }));
          options.onProgress?.(stats);
        },
        onMetadata: (metadata) => {
          setState((prev) => ({
            ...prev,
            metadata: [...prev.metadata, metadata],
          }));
          options.onMetadata?.(metadata);
        },
      };

      const receivedNodes: Record<string, unknown>[] = [];
      const receivedEdges: Record<string, unknown>[] = [];

      for await (const item of streamGraph(graphId, streamOptions)) {
        if (abortControllerRef.current?.signal.aborted) {
          break;
        }

        if (item.type === 'node') {
          receivedNodes.push(item.data as Record<string, unknown>);
          if (receivedNodes.length % 10 === 0) {
            setNodes([...receivedNodes]);
          }
        } else if (item.type === 'edge') {
          receivedEdges.push(item.data as Record<string, unknown>);
          if (receivedEdges.length % 10 === 0) {
            setEdges([...receivedEdges]);
          }
        }
      }

      // Final updates
      setNodes(receivedNodes);
      setEdges(receivedEdges);

      setState((prev) => ({
        ...prev,
        isStreaming: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isStreaming: false,
        error: error as Error,
      }));
    }
  }, []);

  const stopStreaming = useCallback(() => {
    abortControllerRef.current?.abort();
    setState((prev) => ({
      ...prev,
      isStreaming: false,
    }));
  }, []);

  const reset = useCallback(() => {
    stopStreaming();
    setNodes([]);
    setEdges([]);
    setState({
      error: null,
      isStreaming: false,
      metadata: [],
      stats: null,
    });
  }, [stopStreaming]);

  useEffect(
    () => () => {
      abortControllerRef.current?.abort();
    },
    [],
  );

  return {
    edges,
    nodes,
    reset,
    startStreaming,
    state,
    stopStreaming,
  };
}

export interface UseStreamExportResult {
  data: any[];
  state: StreamingState;
  startExport: (options: StreamExportOptions) => Promise<void>;
  stopExport: () => void;
  downloadAsFile: (filename: string) => void;
  reset: () => void;
}

/**
 * Hook for streaming export data
 */
export function useStreamExport(): UseStreamExportResult {
  const [data, setData] = useState<any[]>([]);
  const [state, setState] = useState<StreamingState>({
    error: null,
    isStreaming: false,
    metadata: [],
    stats: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const startExport = useCallback(async (options: StreamExportOptions) => {
    setData([]);
    setState({
      error: null,
      isStreaming: true,
      metadata: [],
      stats: null,
    });

    abortControllerRef.current = new AbortController();

    try {
      const streamOptions: StreamExportOptions = {
        ...options,
        onProgress: (stats) => {
          setState((prev) => ({
            ...prev,
            stats,
          }));
          options.onProgress?.(stats);
        },
        onMetadata: (metadata) => {
          setState((prev) => ({
            ...prev,
            metadata: [...prev.metadata, metadata],
          }));
          options.onMetadata?.(metadata);
        },
      };

      const receivedData: Record<string, unknown>[] = [];

      for await (const item of streamExport(streamOptions)) {
        if (abortControllerRef.current?.signal.aborted) {
          break;
        }

        receivedData.push(item as Record<string, unknown>);

        if (receivedData.length % 10 === 0) {
          setData([...receivedData]);
        }
      }

      setData(receivedData);

      setState((prev) => ({
        ...prev,
        isStreaming: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isStreaming: false,
        error: error as Error,
      }));
    }
  }, []);

  const stopExport = useCallback(() => {
    abortControllerRef.current?.abort();
    setState((prev) => ({
      ...prev,
      isStreaming: false,
    }));
  }, []);

  const downloadAsFile = useCallback(
    (filename: string) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    },
    [data],
  );

  const reset = useCallback(() => {
    stopExport();
    setData([]);
    setState({
      error: null,
      isStreaming: false,
      metadata: [],
      stats: null,
    });
  }, [stopExport]);

  useEffect(
    () => () => {
      abortControllerRef.current?.abort();
    },
    [],
  );

  return {
    data,
    downloadAsFile,
    reset,
    startExport,
    state,
    stopExport,
  };
}
