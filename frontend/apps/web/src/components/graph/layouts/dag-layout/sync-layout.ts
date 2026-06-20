import type { Edge, Node } from '@xyflow/react';

import type { LayoutType, SyncLayoutResult } from './types';

import { applyCircularLayout } from './circular-layout';
import { applyForceLayout } from './force-layout';
import { applyGridLayout } from './grid-layout';
import { applyRadialLayout } from './radial-layout';

export interface SyncLayoutParams<NodeData extends Record<string, unknown>> {
  centerX: number;
  centerY: number;
  inputEdges: Edge[];
  inputNodes: Node<NodeData>[];
  layout: LayoutType;
  nodeHeight: number;
  nodeSep: number;
  nodeWidth: number;
}

export function resolveSyncLayout<NodeData extends Record<string, unknown>>(
  params: SyncLayoutParams<NodeData>,
): SyncLayoutResult<NodeData> {
  const { inputNodes, inputEdges, layout, nodeHeight, nodeSep, nodeWidth, centerX, centerY } =
    params;

  if (layout === 'organic-network') {
    return {
      kind: 'sync',
      nodes: applyForceLayout(inputNodes, inputEdges, { nodeHeight, nodeWidth, padding: nodeSep }),
    };
  }

  if (layout === 'mind-map') {
    return {
      kind: 'sync',
      nodes: applyRadialLayout(inputNodes, inputEdges, { centerX, centerY, nodeHeight, nodeWidth }),
    };
  }

  if (layout === 'gallery') {
    return {
      kind: 'sync',
      nodes: applyGridLayout(inputNodes, {
        compact: false,
        nodeHeight,
        nodeWidth,
        padding: nodeSep,
      }),
    };
  }

  if (layout === 'compact') {
    return {
      kind: 'sync',
      nodes: applyGridLayout(inputNodes, {
        compact: true,
        nodeHeight,
        nodeWidth,
        padding: nodeSep,
      }),
    };
  }

  if (layout === 'wheel') {
    return {
      kind: 'sync',
      nodes: applyCircularLayout(inputNodes, { centerX, centerY, nodeHeight, nodeWidth }),
    };
  }

  return { kind: 'async' };
}
