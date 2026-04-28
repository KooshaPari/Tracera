import type { Edge, Node } from '@xyflow/react';

import type { ElkOptions, SyncLayoutResult } from './types';

const ZERO = Number('0');

interface ComputeLayoutParams<NodeData extends Record<string, unknown>> {
  applySyncLayout: (inputNodes: Node<NodeData>[], inputEdges: Edge[]) => SyncLayoutResult<NodeData>;
  computeElkLayout: (
    inputNodes: Node<NodeData>[],
    inputEdges: Edge[],
    options: ElkOptions,
  ) => Promise<Node<NodeData>[]>;
  elkOptions: ElkOptions | undefined;
  getGridFallback: (inputNodes: Node<NodeData>[]) => Node<NodeData>[];
  inputEdges: Edge[];
  inputNodes: Node<NodeData>[];
}

async function computeLayout<NodeData extends Record<string, unknown>>({
  applySyncLayout,
  computeElkLayout,
  elkOptions,
  getGridFallback,
  inputEdges,
  inputNodes,
}: ComputeLayoutParams<NodeData>): Promise<Node<NodeData>[]> {
  if (inputNodes.length === ZERO) {
    return [];
  }

  const syncResult = applySyncLayout(inputNodes, inputEdges);
  if (syncResult.kind === 'sync' && syncResult.nodes) {
    return syncResult.nodes;
  }

  if (!elkOptions) {
    return getGridFallback(inputNodes);
  }

  return computeElkLayout(inputNodes, inputEdges, elkOptions);
}

export { computeLayout };
