/**
 * React Hook for GPU-Accelerated Force-Directed Layout
 *
 * Features:
 * - Automatic Web Worker execution for >1000 nodes
 * - Smooth spring animations for layout transitions
 * - Progress tracking
 * - Performance metrics
 */

import type { Edge, Node } from '@xyflow/react';

import { useCallback, useEffect, useRef, useState } from 'react';

import type { ForceSimulationConfig } from './gpuForceLayout';
import type {
  ForceLayoutError,
  ForceLayoutProgress,
  ForceLayoutRequest,
  ForceLayoutResponse,
} from './gpuForceLayout.worker';

import { getGPUForceLayout } from './gpuForceLayout';

// ============================================================================
// CONFIGURATION
// ============================================================================

const WORKER_THRESHOLD = 1000; // Use worker for graphs with >1000 nodes
const ANIMATION_DURATION = 800; // Ms for layout transition animation

// ============================================================================
// TYPES
// ============================================================================

export interface UseGPUForceLayoutOptions {
  enabled?: boolean;
  animateTransitions?: boolean;
  animationDuration?: number;
  config?: ForceSimulationConfig;
}

export interface GPUForceLayoutState {
  isComputing: boolean;
  progress: number;
  duration: number | null;
  error: string | null;
}

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

export function useGpuForceLayout<T extends Record<string, unknown>>(
  nodes: Node<T>[],
  edges: Edge[],
  options: UseGPUForceLayoutOptions = {},
) {
  const {
    enabled = true,
    animateTransitions = true,
    animationDuration = ANIMATION_DURATION,
    config = {},
  } = options;

  const [layoutedNodes, setLayoutedNodes] = useState<Node<T>[]>(nodes);
  const [state, setState] = useState<GPUForceLayoutState>({
    duration: null,
    error: null,
    isComputing: false,
    progress: 0,
  });

  const workerRef = useRef<Worker | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const prevSignatureRef = useRef<string>('');

  // Cleanup worker on unmount
  useEffect(
    () => () => {
      if (workerRef.current) {
        workerRef.current.terminate();
        workerRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    },
    [],
  );

  /**
   * Animate transition from old positions to new positions
   */
  const animateLayout = useCallback(
    async (oldNodes: Node<T>[], newNodes: Node<T>[], duration: number): Promise<void> =>
      new Promise((resolve) => {
        if (!animateTransitions) {
          setLayoutedNodes(newNodes);
          resolve();
          return;
        }

        const startTime = performance.now();
        const oldPosMap = new Map(oldNodes.map((n) => [n.id, n.position]));
        const newPosMap = new Map(newNodes.map((n) => [n.id, n.position]));

        const animate = (currentTime: number) => {
          const elapsed = currentTime - startTime;
          const progress = Math.min(elapsed / duration, 1);

          // Ease-out cubic
          const eased = 1 - (1 - progress) ** 3;

          const interpolatedNodes = newNodes.map((node) => {
            const oldPos = oldPosMap.get(node.id) ?? node.position;
            const newPos = newPosMap.get(node.id) ?? node.position;

            return {
              ...node,
              position: {
                x: oldPos.x + (newPos.x - oldPos.x) * eased,
                y: oldPos.y + (newPos.y - oldPos.y) * eased,
              },
            };
          });

          setLayoutedNodes(interpolatedNodes);

          if (progress < 1) {
            animationFrameRef.current = requestAnimationFrame(animate);
          } else {
            resolve();
          }
        };

        animationFrameRef.current = requestAnimationFrame(animate);
      }),
    [animateTransitions],
  );

  /**
   * Run layout in Web Worker
   */
  const runInWorker = useCallback(
    async (inputNodes: Node<T>[], inputEdges: Edge[]): Promise<Node<T>[]> =>
      new Promise((resolve, reject) => {
        if (typeof Worker === 'undefined') {
          reject(new Error('Web Workers not supported'));
          return;
        }

        // Create worker
        const worker = new Worker(new URL('./gpuForceLayout.worker.ts', import.meta.url), {
          type: 'module',
        });

        workerRef.current = worker;

        // Handle messages
        const onMessage = (
          ev: MessageEvent<ForceLayoutResponse | ForceLayoutProgress | ForceLayoutError>,
        ) => {
          const message = ev.data;
          switch (message.type) {
            case 'result': {
              worker.terminate();
              workerRef.current = null;

              const positionMap = new Map(message.positions.map((p) => [p.id, { x: p.x, y: p.y }]));

              const result = inputNodes.map((node) => {
                const pos = positionMap.get(node.id);
                if (!pos) {
                  return node;
                }
                return { ...node, position: pos };
              });

              setState((prev) => ({
                ...prev,
                duration: message.duration,
                isComputing: false,
              }));

              resolve(result);
              break;
            }
            case 'progress': {
              setState((prev) => ({
                ...prev,
                progress: message.progress,
              }));
              break;
            }
            case 'error': {
              worker.terminate();
              workerRef.current = null;

              setState((prev) => ({
                ...prev,
                error: message.error,
                isComputing: false,
              }));

              reject(new Error(message.error));
              break;
            }
          }
        };

        worker.addEventListener('message', onMessage);

        worker.addEventListener('error', (err) => {
          worker.terminate();
          workerRef.current = null;

          setState((prev) => ({
            ...prev,
            error: err.message || 'Worker error',
            isComputing: false,
          }));

          reject(new Error(err.message || 'Worker error'));
        });

        // Send request
        const request: ForceLayoutRequest = {
          config,
          edges: inputEdges.map((e) => ({
            id: e.id,
            source: e.source,
            target: e.target,
          })),
          nodes: inputNodes.map((n) => ({ id: n.id })),
          type: 'simulate',
        };

        worker.postMessage(request);
      }),
    [config],
  );

  /**
   * Run layout on main thread
   */
  const runOnMainThread = useCallback(
    async (inputNodes: Node<T>[], inputEdges: Edge[]): Promise<Node<T>[]> => {
      const startTime = performance.now();
      const layoutEngine = getGPUForceLayout();

      const result = await layoutEngine.simulate(inputNodes, inputEdges, config);

      const duration = performance.now() - startTime;

      setState((prev) => ({
        ...prev,
        duration,
        isComputing: false,
      }));

      return result;
    },
    [config],
  );

  /**
   * Calculate layout (main entry point)
   */
  const calculateLayout = useCallback(
    async (inputNodes: Node<T>[], inputEdges: Edge[]): Promise<Node<T>[]> => {
      if (!enabled || inputNodes.length === 0) {
        return inputNodes;
      }

      setState({
        duration: null,
        error: null,
        isComputing: true,
        progress: 0,
      });

      try {
        // Use worker for large graphs
        const result =
          inputNodes.length > WORKER_THRESHOLD
            ? await runInWorker(inputNodes, inputEdges)
            : await runOnMainThread(inputNodes, inputEdges);

        return result;
      } catch (error) {
        console.error('GPU force layout failed:', error);

        setState((prev) => ({
          ...prev,
          error: error instanceof Error ? error.message : String(error),
          isComputing: false,
        }));

        // Return original nodes on error
        return inputNodes;
      }
    },
    [enabled, runInWorker, runOnMainThread],
  );

  /**
   * Auto-calculate layout when inputs change
   */
  useEffect(() => {
    if (!enabled) {
      setLayoutedNodes(nodes);
      return;
    }

    // Create signature to detect changes
    const signature = `${nodes.length}|${edges.length}|${nodes.map((n) => n.id).join(',')}`;

    if (signature === prevSignatureRef.current) {
      return;
    }

    prevSignatureRef.current = signature;

    if (nodes.length === 0) {
      setLayoutedNodes([]);
      return;
    }

    // Calculate new layout
    const oldNodes = layoutedNodes.length > 0 ? layoutedNodes : nodes;
    let cancelled = false;

    const runLayout = async () => {
      const newNodes = await calculateLayout(nodes, edges);
      if (cancelled) {
        return;
      }

      if (animateTransitions) {
        await animateLayout(oldNodes, newNodes, animationDuration);
        return;
      }

      setLayoutedNodes(newNodes);
    };

    runLayout().catch((error) => {
      if (cancelled) {
        return;
      }

      setState((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : String(error),
        isComputing: false,
      }));
    });

    return () => {
      cancelled = true;
    };
  }, [
    enabled,
    nodes,
    edges,
    calculateLayout,
    animateLayout,
    animationDuration,
    animateTransitions,
  ]);

  return {
    nodes: layoutedNodes,
    ...state,
    calculateLayout,
  };
}

export default useGpuForceLayout;
