import type { Edge, Node } from '@xyflow/react';
import type Graph from 'graphology';

import { useMemo, useState } from 'react';

import { createGraphologyAdapter } from '@/lib/graphology/adapter';

const NODE_THRESHOLD = 10_000; // Switch to WebGL at 10k nodes

export interface HybridGraphConfig {
  nodeThreshold?: number;
  forceReactFlow?: boolean; // Emergency override
  forceWebGL?: boolean;
}

export interface HybridGraphState {
  useWebGL: boolean;
  nodeCount: number;
  edgeCount: number;
  graphologyGraph: Graph | null;
  performanceMode: 'reactflow' | 'webgl';
}

export const useHybridGraph = (nodes: Node[], edges: Edge[], config: HybridGraphConfig = {}) => {
  const { nodeThreshold = NODE_THRESHOLD, forceReactFlow = false, forceWebGL = false } = config;

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Determine rendering mode
  const useWebGL = useMemo(() => {
    if (forceReactFlow) {
      return false;
    }
    if (forceWebGL) {
      return true;
    }
    return nodes.length >= nodeThreshold;
  }, [nodes.length, nodeThreshold, forceReactFlow, forceWebGL]);

  // Convert to Graphology if using WebGL
  const graphologyGraph = useMemo(() => {
    if (!useWebGL) {
      return null;
    }

    const adapter = createGraphologyAdapter();
    adapter.syncFromReactFlow(nodes, edges);
    return adapter.getGraph();
  }, [nodes, edges, useWebGL]);

  // State for UI
  const state: HybridGraphState = {
    edgeCount: edges.length,
    graphologyGraph,
    nodeCount: nodes.length,
    performanceMode: useWebGL ? 'webgl' : 'reactflow',
    useWebGL,
  };

  return {
    ...state,
    selectedNodeId,
    setSelectedNodeId,
  };
};
