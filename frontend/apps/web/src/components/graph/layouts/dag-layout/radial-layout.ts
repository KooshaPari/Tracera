import type { Edge, Node } from '@xyflow/react';

import {
  FULL_CIRCLE_RADIANS,
  GRID_COMPACT_PADDING_DIVISOR,
  RADIAL_ORPHAN_SEGMENTS,
  RADIAL_RADIUS_MULTIPLIER,
  START_ANGLE_RADIANS,
} from './constants';

interface Point {
  coordX: number;
  coordY: number;
}

function getRootNodeIds<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
): string[] {
  const hasIncoming = new Set(edges.map((edge) => edge.target));
  const rootIds: string[] = [];
  for (const node of nodes) {
    if (!hasIncoming.has(node.id)) {
      rootIds.push(node.id);
    }
  }
  return rootIds;
}

function buildChildrenMap(edges: Edge[]): Map<string, string[]> {
  const children = new Map<string, string[]>();
  for (const edge of edges) {
    const existing = children.get(edge.source);
    if (existing) {
      existing.push(edge.target);
    } else {
      children.set(edge.source, [edge.target]);
    }
  }
  return children;
}

function computeDepths(rootIds: string[], children: Map<string, string[]>): Map<string, number> {
  const depths = new Map<string, number>();
  const queue: { id: string; depth: number }[] = rootIds.map((rootId) => ({
    depth: 0,
    id: rootId,
  }));

  while (queue.length > 0) {
    const next = queue.shift();
    if (next && !depths.has(next.id)) {
      depths.set(next.id, next.depth);
      const nodeChildren = children.get(next.id);
      if (nodeChildren) {
        for (const childId of nodeChildren) {
          if (!depths.has(childId)) {
            queue.push({ depth: next.depth + 1, id: childId });
          }
        }
      }
    }
  }
  return depths;
}

function groupNodeIdsByDepth(depths: Map<string, number>): Map<number, string[]> {
  const byDepth = new Map<number, string[]>();
  for (const [nodeId, depth] of depths) {
    const existing = byDepth.get(depth);
    if (existing) {
      existing.push(nodeId);
    } else {
      byDepth.set(depth, [nodeId]);
    }
  }
  return byDepth;
}

function buildRadialPositions(
  byDepth: Map<number, string[]>,
  options: { nodeWidth: number; nodeHeight: number; centerX: number; centerY: number },
): Map<string, Point> {
  const positions = new Map<string, Point>();
  const baseRadius = Math.max(options.nodeWidth, options.nodeHeight) * RADIAL_RADIUS_MULTIPLIER;
  const halfNodeWidth = options.nodeWidth / GRID_COMPACT_PADDING_DIVISOR;
  const halfNodeHeight = options.nodeHeight / GRID_COMPACT_PADDING_DIVISOR;

  for (const [depth, nodeIds] of byDepth) {
    const radius = (depth + 1) * baseRadius;
    const angleStep = FULL_CIRCLE_RADIANS / nodeIds.length;
    for (let index = 0; index < nodeIds.length; index += 1) {
      const nodeId = nodeIds[index]!;
      const angle = index * angleStep + START_ANGLE_RADIANS;
      positions.set(nodeId, {
        coordX: options.centerX + radius * Math.cos(angle) - halfNodeWidth,
        coordY: options.centerY + radius * Math.sin(angle) - halfNodeHeight,
      });
    }
  }
  return positions;
}

function assignOrphanPositions<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  positions: Map<string, Point>,
  options: { nodeWidth: number; nodeHeight: number; centerX: number; centerY: number },
  depthCount: number,
): Node<NodeData>[] {
  let orphanIndex = 0;
  const baseRadius = Math.max(options.nodeWidth, options.nodeHeight) * RADIAL_RADIUS_MULTIPLIER;
  const halfNodeWidth = options.nodeWidth / GRID_COMPACT_PADDING_DIVISOR;
  const halfNodeHeight = options.nodeHeight / GRID_COMPACT_PADDING_DIVISOR;
  const orphanRadius = (depthCount + 1) * baseRadius;
  const orphanAngleStep = FULL_CIRCLE_RADIANS / RADIAL_ORPHAN_SEGMENTS;

  return nodes.map((node) => {
    const existing = positions.get(node.id);
    if (existing) {
      return { ...node, position: { x: existing.coordX, y: existing.coordY } };
    }

    orphanIndex += 1;
    const angle = orphanIndex * orphanAngleStep + START_ANGLE_RADIANS;
    const coordX = options.centerX + orphanRadius * Math.cos(angle) - halfNodeWidth;
    const coordY = options.centerY + orphanRadius * Math.sin(angle) - halfNodeHeight;
    return { ...node, position: { x: coordX, y: coordY } };
  });
}

export function applyRadialLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: { nodeWidth: number; nodeHeight: number; centerX: number; centerY: number },
): Node<NodeData>[] {
  const rootIds = getRootNodeIds(nodes, edges);
  const children = buildChildrenMap(edges);
  const depths = computeDepths(rootIds, children);
  const byDepth = groupNodeIdsByDepth(depths);
  const positions = buildRadialPositions(byDepth, options);
  return assignOrphanPositions(nodes, positions, options, byDepth.size);
}
