import type { Node } from '@xyflow/react';

import { GRID_COMPACT_PADDING_DIVISOR, GRID_MIN_COLUMNS } from './constants';

interface GridLayoutOptions {
  nodeWidth: number;
  nodeHeight: number;
  padding: number;
  compact?: boolean;
}

function getGridPadding(padding: number, compact: boolean | undefined): number {
  if (compact === true) {
    return padding / GRID_COMPACT_PADDING_DIVISOR;
  }
  return padding;
}

function getGridColumnCount(nodeCount: number): number {
  const columnCount = Math.ceil(Math.sqrt(nodeCount));
  if (columnCount <= 0) {
    return GRID_MIN_COLUMNS;
  }
  return columnCount;
}

function applyGridLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  options: GridLayoutOptions,
): Node<NodeData>[] {
  const { nodeWidth, nodeHeight, padding, compact } = options;
  const resolvedPadding = getGridPadding(padding, compact);
  const safeColumnCount = getGridColumnCount(nodes.length);

  return nodes.map((node, index) => ({
    ...node,
    position: {
      x: (index % safeColumnCount) * (nodeWidth + resolvedPadding),
      y: Math.floor(index / safeColumnCount) * (nodeHeight + resolvedPadding),
    },
  }));
}

export { applyGridLayout, type GridLayoutOptions };
