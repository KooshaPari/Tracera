import type { Node } from '@xyflow/react';

import {
  CIRCULAR_MIN_RADIUS,
  CIRCULAR_RADIUS_STEP,
  FULL_CIRCLE_RADIANS,
  GRID_COMPACT_PADDING_DIVISOR,
  START_ANGLE_RADIANS,
} from './constants';

export function applyCircularLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  options: { nodeWidth: number; nodeHeight: number; centerX: number; centerY: number },
): Node<NodeData>[] {
  const count = nodes.length;
  if (count <= 0) {
    return nodes;
  }
  const radius = Math.max(CIRCULAR_MIN_RADIUS, count * CIRCULAR_RADIUS_STEP);
  const angleStep = FULL_CIRCLE_RADIANS / count;
  const halfNodeWidth = options.nodeWidth / GRID_COMPACT_PADDING_DIVISOR;
  const halfNodeHeight = options.nodeHeight / GRID_COMPACT_PADDING_DIVISOR;

  return nodes.map((node, index) => {
    const angle = index * angleStep + START_ANGLE_RADIANS;
    return {
      ...node,
      position: {
        x: options.centerX + radius * Math.cos(angle) - halfNodeWidth,
        y: options.centerY + radius * Math.sin(angle) - halfNodeHeight,
      },
    };
  });
}
