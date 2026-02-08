import type { Edge, Node } from '@xyflow/react';

import { useCallback, useMemo, useRef, useState } from 'react';

import { logger } from '@/lib/logger';

import type { ElkOptions, LayoutConfig, LayoutType, SyncLayoutResult } from './types';

import { computeLayout } from './compute-layout';
import {
  DEFAULT_CENTER_X,
  DEFAULT_CENTER_Y,
  DEFAULT_MARGIN_X,
  DEFAULT_MARGIN_Y,
  DEFAULT_NODE_HEIGHT,
  DEFAULT_NODE_SEP,
  DEFAULT_NODE_WIDTH,
  DEFAULT_RANK_SEP,
} from './constants';
import { computeElkLayoutInternal, getElkOptions } from './elk-layout';
import { applyGridLayout } from './grid-layout';
import { getLayoutConfig } from './layout-config';
import { buildSignature } from './signature';
import { resolveSyncLayout } from './sync-layout';
import { useApplyLayoutEffect } from './use-apply-layout-effect';

interface UseDagLayoutOptions {
  nodeWidth?: number;
  nodeHeight?: number;
  rankSep?: number;
  nodeSep?: number;
  marginX?: number;
  marginY?: number;
  centerX?: number;
  centerY?: number;
}

interface DagLayoutResult<NodeData extends Record<string, unknown>> {
  calculateLayout: (inputNodes: Node<NodeData>[], inputEdges: Edge[]) => Promise<Node<NodeData>[]>;
  isLayouting: boolean;
  layoutConfig: LayoutConfig;
  nodes: Node<NodeData>[];
}

function useDagLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  layout: LayoutType,
  options: UseDagLayoutOptions = {},
): DagLayoutResult<NodeData> {
  const {
    nodeWidth = DEFAULT_NODE_WIDTH,
    nodeHeight = DEFAULT_NODE_HEIGHT,
    rankSep = DEFAULT_RANK_SEP,
    nodeSep = DEFAULT_NODE_SEP,
    marginX = DEFAULT_MARGIN_X,
    marginY = DEFAULT_MARGIN_Y,
    centerX = DEFAULT_CENTER_X,
    centerY = DEFAULT_CENTER_Y,
  } = options;

  const [layoutedNodes, setLayoutedNodes] = useState<Node<NodeData>[]>(nodes);
  const [isLayouting, setIsLayouting] = useState(false);

  const layoutConfig = useMemo(() => getLayoutConfig(layout), [layout]);
  const signature = useMemo(() => buildSignature({ edges, layout, nodes }), [edges, layout, nodes]);

  const applySyncLayout = useCallback(
    (inputNodes: Node<NodeData>[], inputEdges: Edge[]): SyncLayoutResult<NodeData> =>
      resolveSyncLayout({
        centerX,
        centerY,
        inputEdges,
        inputNodes,
        layout,
        nodeHeight,
        nodeSep,
        nodeWidth,
      }),
    [centerX, centerY, layout, nodeHeight, nodeSep, nodeWidth],
  );

  const elkOptions = useMemo(
    () =>
      getElkOptions(layout, {
        marginX,
        marginY,
        nodeHeight,
        nodeSep,
        nodeWidth,
        rankSep,
      }),
    [layout, marginX, marginY, nodeHeight, nodeSep, nodeWidth, rankSep],
  );

  const getGridFallback = useCallback(
    (inputNodes: Node<NodeData>[]) =>
      applyGridLayout(inputNodes, { compact: false, nodeHeight, nodeWidth, padding: nodeSep }),
    [nodeHeight, nodeSep, nodeWidth],
  );

  const computeElkLayout = useCallback(
    async (
      inputNodes: Node<NodeData>[],
      inputEdges: Edge[],
      resolvedElkOptions: ElkOptions,
    ): Promise<Node<NodeData>[]> => {
      const result = await computeElkLayoutInternal(inputNodes, inputEdges, resolvedElkOptions);
      return result;
    },
    [],
  );

  const calculateLayout = useCallback(
    async (inputNodes: Node<NodeData>[], inputEdges: Edge[]): Promise<Node<NodeData>[]> => {
      try {
        return await computeLayout({
          applySyncLayout,
          computeElkLayout,
          elkOptions,
          getGridFallback,
          inputEdges,
          inputNodes,
        });
      } catch (error: unknown) {
        logger.error('Layout calculation failed:', error);
        return getGridFallback(inputNodes);
      }
    },
    [applySyncLayout, computeElkLayout, elkOptions, getGridFallback],
  );

  const prevSignatureRef = useRef<string>('');

  useApplyLayoutEffect({
    applySyncLayout,
    computeElkLayout,
    edges,
    elkOptions,
    getGridFallback,
    nodes,
    prevSignatureRef,
    setIsLayouting,
    setLayoutedNodes,
    signature,
  });

  return { calculateLayout, isLayouting, layoutConfig, nodes: layoutedNodes };
}

export { useDagLayout };
export type { DagLayoutResult, UseDagLayoutOptions };
