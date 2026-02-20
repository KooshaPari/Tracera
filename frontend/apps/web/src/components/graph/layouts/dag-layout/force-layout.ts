import type { Edge, Node } from '@xyflow/react';

import {
  FORCE_ATTRACTION_STRENGTH,
  FORCE_DAMPING,
  FORCE_ITERATIONS,
  FORCE_JITTER_MIDPOINT,
  FORCE_JITTER_RANGE,
  FORCE_MIN_DISTANCE,
  FORCE_NORMALIZE_PADDING,
  FORCE_REPULSION_STRENGTH,
  GRID_FALLBACK_PADDING_MULTIPLIER,
  GRID_MIN_COLUMNS,
} from './constants';

interface ForcePosition {
  posX: number;
  posY: number;
  velX: number;
  velY: number;
}

function initializeForcePositions<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  options: { nodeWidth: number; nodeHeight: number; padding: number },
): Map<string, ForcePosition> {
  const positions = new Map<string, ForcePosition>();
  const columnCount = Math.ceil(Math.sqrt(nodes.length));
  let safeColumnCount = columnCount;
  if (safeColumnCount <= 0) {
    safeColumnCount = GRID_MIN_COLUMNS;
  }

  for (let index = 0; index < nodes.length; index += 1) {
    const node = nodes[index];
    if (!node) continue;
    const baseX =
      (index % safeColumnCount) *
      (options.nodeWidth + options.padding * GRID_FALLBACK_PADDING_MULTIPLIER);
    const baseY =
      Math.floor(index / safeColumnCount) *
      (options.nodeHeight + options.padding * GRID_FALLBACK_PADDING_MULTIPLIER);
    positions.set(node.id, {
      posX: baseX + (Math.random() - FORCE_JITTER_MIDPOINT) * FORCE_JITTER_RANGE,
      posY: baseY + (Math.random() - FORCE_JITTER_MIDPOINT) * FORCE_JITTER_RANGE,
      velX: 0,
      velY: 0,
    });
  }

  return positions;
}

function applyRepulsion<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  positions: Map<string, ForcePosition>,
): void {
  for (const sourceNode of nodes) {
    const sourcePosition = positions.get(sourceNode.id);
    if (sourcePosition) {
      for (const targetNode of nodes) {
        if (sourceNode.id !== targetNode.id) {
          const targetPosition = positions.get(targetNode.id);
          if (targetPosition) {
            const deltaX = sourcePosition.posX - targetPosition.posX;
            const deltaY = sourcePosition.posY - targetPosition.posY;
            const distance = Math.hypot(deltaX, deltaY) || FORCE_MIN_DISTANCE;
            const force = FORCE_REPULSION_STRENGTH / (distance * distance);
            sourcePosition.velX += (deltaX / distance) * force;
            sourcePosition.velY += (deltaY / distance) * force;
          }
        }
      }
    }
  }
}

function applyAttraction(edges: Edge[], positions: Map<string, ForcePosition>): void {
  for (const edge of edges) {
    const sourcePosition = positions.get(edge.source);
    const targetPosition = positions.get(edge.target);
    if (sourcePosition && targetPosition) {
      const deltaX = targetPosition.posX - sourcePosition.posX;
      const deltaY = targetPosition.posY - sourcePosition.posY;
      const distance = Math.hypot(deltaX, deltaY) || FORCE_MIN_DISTANCE;
      const force = FORCE_ATTRACTION_STRENGTH * distance;
      const forceX = (deltaX / distance) * force;
      const forceY = (deltaY / distance) * force;
      sourcePosition.velX += forceX;
      sourcePosition.velY += forceY;
      targetPosition.velX -= forceX;
      targetPosition.velY -= forceY;
    }
  }
}

function updatePositions(positions: Map<string, ForcePosition>): void {
  for (const position of positions.values()) {
    position.velX *= FORCE_DAMPING;
    position.velY *= FORCE_DAMPING;
    position.posX += position.velX;
    position.posY += position.velY;
  }
}

function normalizePositions<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  positions: Map<string, ForcePosition>,
): Map<string, { x: number; y: number }> {
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;

  for (const node of nodes) {
    const position = positions.get(node.id);
    if (position) {
      if (position.posX < minX) {
        minX = position.posX;
      }
      if (position.posY < minY) {
        minY = position.posY;
      }
    }
  }

  const adjusted = new Map<string, { x: number; y: number }>();
  for (const node of nodes) {
    const position = positions.get(node.id);
    if (position) {
      adjusted.set(node.id, {
        x: position.posX - minX + FORCE_NORMALIZE_PADDING,
        y: position.posY - minY + FORCE_NORMALIZE_PADDING,
      });
    }
  }
  return adjusted;
}

export function applyForceLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: { nodeWidth: number; nodeHeight: number; padding: number },
): Node<NodeData>[] {
  const positions = initializeForcePositions(nodes, options);

  for (let iter = 0; iter < FORCE_ITERATIONS; iter += 1) {
    applyRepulsion(nodes, positions);
    applyAttraction(edges, positions);
    updatePositions(positions);
  }

  const normalized = normalizePositions(nodes, positions);
  return nodes.map((node) => {
    const pos = normalized.get(node.id);
    if (!pos) {
      return node;
    }
    return { ...node, position: pos };
  });
}
