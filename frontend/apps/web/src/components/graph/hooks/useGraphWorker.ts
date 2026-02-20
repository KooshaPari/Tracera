import { useCallback, useEffect, useRef, useState } from 'react';

export interface LayoutMessage {
  type: 'layout-request' | 'layout-response' | 'error';
  id?: string;
  data?: unknown;
  error?: string;
}

export interface LayoutNode {
  id: string;
  width: number;
  height: number;
}

export interface LayoutEdge {
  id: string;
  source: string;
  target: string;
}

export interface LayoutOptions {
  type: 'dagre' | 'elk' | 'fcose';
  direction?: 'TB' | 'LR' | 'BT' | 'RL';
  nodeSep?: number;
  rankSep?: number;
  marginX?: number;
  marginY?: number;
  nodeWidth?: number;
  nodeHeight?: number;
}

export interface LayoutResult {
  positions: Record<string, { x: number; y: number }>;
  size: { width: number; height: number };
}

interface PendingRequest {
  id: string;
  resolve: (value: LayoutResult) => void;
  reject: (reason: Error) => void;
  // Store timeout as NodeJS.Timeout | number to support both browser and Node.js environments
  timeout: NodeJS.Timeout | number;
}

/**
 * Hook for running heavy layout calculations in a Web Worker
 * Prevents main thread blocking with large graphs
 */
export function useGraphWorker() {
  const workerRef = useRef<Worker | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const pendingRequestsRef = useRef<Map<string, PendingRequest>>(new Map());

  // Initialize worker
  useEffect(() => {
    if (typeof globalThis.window === 'undefined') {
      return;
    }

    try {
      // Create worker from inline code or separate file
      const workerCode = `
        // Simple DAG layout implementation
        function layoutDAG(nodes, edges, options) {
          const nodeMap = new Map(nodes.map(n => [n.id, n]));
          const graph = new Map();

          // Build adjacency
          for (const node of nodes) {
            graph.set(node.id, []);
          }
          for (const edge of edges) {
            if (graph.has(edge.source)) {
              graph.get(edge.source).push(edge.target);
            }
          }

          // Topological sort with levels
          const levels = new Map();
          const visited = new Set();

          function assignLevel(nodeId, currentLevel = 0) {
            if (visited.has(nodeId)) return levels.get(nodeId) || 0;
            visited.add(nodeId);

            let maxIncomingLevel = -1;
            for (const [source, targets] of graph) {
              if (targets.includes(nodeId)) {
                const srcLevel = assignLevel(source, currentLevel + 1);
                maxIncomingLevel = Math.max(maxIncomingLevel, srcLevel);
              }
            }

            const nodeLevel = maxIncomingLevel + 1;
            levels.set(nodeId, nodeLevel);
            return nodeLevel;
          }

          for (const nodeId of nodeMap.keys()) {
            assignLevel(nodeId);
          }

          // Group nodes by level
          const levelGroups = new Map();
          for (const [nodeId, level] of levels) {
            if (!levelGroups.has(level)) levelGroups.set(level, []);
            levelGroups.get(level).push(nodeId);
          }

          // Calculate positions
          const positions = {};
          let maxWidth = 0;
          let maxHeight = 0;

          const nodeWidth = options.nodeWidth || 200;
          const nodeHeight = options.nodeHeight || 120;
          const nodeSep = options.nodeSep || 60;
          const rankSep = options.rankSep || 100;
          const marginX = options.marginX || 40;
          const marginY = options.marginY || 40;

          const maxLevel = Math.max(...Array.from(levelGroups.keys()));
          for (const [level, nodeIds] of levelGroups) {
            const y = marginY + level * (nodeHeight + rankSep);
            const levelWidth = nodeIds.length * (nodeWidth + nodeSep);
            const startX = marginX + (maxLevel > 5 ? -levelWidth / 2 : 0);

            nodeIds.forEach((nodeId, index) => {
              const x = startX + index * (nodeWidth + nodeSep);
              positions[nodeId] = { x: Math.max(marginX, x), y };
              maxWidth = Math.max(maxWidth, x + nodeWidth + marginX);
              maxHeight = Math.max(maxHeight, y + nodeHeight + marginY);
            });
          }

          return {
            positions,
            size: { width: maxWidth, height: maxHeight }
          };
        }

        self.onmessage = function(event) {
          const { id, type, nodes, edges, options } = event.data;

          try {
            if (type === 'layout-request') {
              let result;

              if (options.type === 'dagre' || options.type === 'elk') {
                result = layoutDAG(nodes, edges, options);
              } else {
                // Fallback to simple grid layout
                const positions = {};
                const perRow = Math.ceil(Math.sqrt(nodes.length));
                const nodeWidth = options.nodeWidth || 200;
                const nodeHeight = options.nodeHeight || 120;
                const sep = 60;

                nodes.forEach((node, i) => {
                  const x = (i % perRow) * (nodeWidth + sep) + 40;
                  const y = Math.floor(i / perRow) * (nodeHeight + sep) + 40;
                  positions[node.id] = { x, y };
                });

                const width = perRow * (nodeWidth + sep) + 40;
                const height = Math.ceil(nodes.length / perRow) * (nodeHeight + sep) + 40;
                result = { positions, size: { width, height } };
              }

              self.postMessage({
                id,
                type: 'layout-response',
                data: result
              });
            }
          } catch (error) {
            self.postMessage({
              id,
              type: 'error',
              error: error instanceof Error ? error.message : String(error)
            });
          }
        };
      `;

      const blob = new Blob([workerCode], { type: 'application/javascript' });
      const workerUrl = URL.createObjectURL(blob);
      const worker = new Worker(workerUrl);

      worker.onmessage = (event: MessageEvent<LayoutMessage>) => {
        const { id, type, data, error: errorMsg } = event.data;

        if (!id) {
          return;
        }

        const pending = pendingRequestsRef.current.get(id);
        if (!pending) {
          return;
        }

        pendingRequestsRef.current.delete(id);
        clearTimeout(pending.timeout);

        if (type === 'layout-response' && data) {
          pending.resolve(data as LayoutResult);
        } else if (type === 'error') {
          pending.reject(new Error(errorMsg ?? 'Layout computation failed'));
        }
      };

      worker.onerror = (error: ErrorEvent) => {
        const errorMessage = error.message || 'Unknown worker error';
        setError(new Error(`Worker error: ${errorMessage}`));
        pendingRequestsRef.current.forEach((pending) => {
          pending.reject(new Error(errorMessage));
        });
        pendingRequestsRef.current.clear();
      };

      workerRef.current = worker;
      setIsReady(true);

      return () => {
        worker.terminate();
        URL.revokeObjectURL(workerUrl);
      };
    } catch (error) {
      setError(error instanceof Error ? error : new Error(String(error)));
    }
    return;
  }, []);

  // Layout computation function
  const computeLayout = useCallback(
    async (
      nodes: LayoutNode[],
      edges: LayoutEdge[],
      options: LayoutOptions,
    ): Promise<LayoutResult> =>
      new Promise((resolve, reject) => {
        if (!workerRef.current) {
          reject(new Error('Worker not initialized'));
          return;
        }

        const id = `layout-${Date.now()}-${Math.random()}`;

        const timeoutId = setTimeout(() => {
          pendingRequestsRef.current.delete(id);
          reject(new Error('Layout computation timeout'));
        }, 30_000); // 30 second timeout

        pendingRequestsRef.current.set(id, {
          id,
          reject,
          resolve,
          timeout: timeoutId,
        });

        workerRef.current.postMessage({
          edges,
          id,
          nodes,
          options,
          type: 'layout-request',
        } as LayoutMessage & {
          nodes: LayoutNode[];
          edges: LayoutEdge[];
          options: LayoutOptions;
        });
      }),
    [],
  );

  // Cancel pending requests
  const cancelRequests = useCallback(() => {
    for (const [, pending] of pendingRequestsRef.current) {
      clearTimeout(pending.timeout);
      pending.reject(new Error('Cancelled'));
    }
    pendingRequestsRef.current.clear();
  }, []);

  return {
    cancelRequests,
    computeLayout,
    error,
    isReady,
  };
}

/**
 * Hook for grouping and clustering nodes
 */
export function useNodeClustering(
  nodes: {
    id: string;
    x: number;
    y: number;
    width: number;
    height: number;
  }[],
  clusterDistance = 300,
) {
  const [clusters, setClusters] = useState<Map<string, string[]>>(new Map());

  useEffect(() => {
    if (nodes.length === 0) {
      setClusters(new Map());
      return;
    }

    // Simple clustering using distance
    const clusterMap = new Map<string, string[]>();
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const visited = new Set<string>();

    function clusterFromNode(startId: string): string[] {
      if (visited.has(startId)) {
        return [];
      }

      const cluster: string[] = [startId];
      visited.add(startId);
      const queue = [startId];

      while (queue.length > 0) {
        const currentId = queue.shift()!;
        const current = nodeMap.get(currentId)!;

        for (const other of nodeMap.values()) {
          if (visited.has(other.id)) {
            continue;
          }

          const dx = other.x - current.x;
          const dy = other.y - current.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < clusterDistance) {
            cluster.push(other.id);
            visited.add(other.id);
            queue.push(other.id);
          }
        }
      }

      return cluster;
    }

    for (const node of nodes) {
      if (!visited.has(node.id)) {
        const cluster = clusterFromNode(node.id);
        const clusterId = `cluster-${cluster[0]}`;
        clusterMap.set(clusterId, cluster);
      }
    }

    setClusters(clusterMap);
  }, [nodes, clusterDistance]);

  return { clusters };
}
