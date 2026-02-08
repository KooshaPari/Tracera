import type { Edge, Node } from '@xyflow/react';
import type { ElkExtendedEdge, ElkNode } from 'elkjs';

import ELK from 'elkjs/lib/elk.bundled.js';

import type { ElkOptionsPayload, LayoutResponse } from './graphLayout.worker';

const ZERO = Number('0');
const ONE = Number('1');
const LAYOUT_WORKER_THRESHOLD = Number('150');
const GRID_COMPACT_PADDING_DIVISOR = Number('2');
const GRID_COLUMNS_DIVISOR = Number('1');
const RADIAL_RADIUS_MULTIPLIER = Number('1.5');
const RADIAL_ORPHAN_SEGMENTS = Number('8');
const FULL_CIRCLE_RADIANS = Math.PI * GRID_COMPACT_PADDING_DIVISOR;
const HALF_RADIANS = Math.PI / GRID_COMPACT_PADDING_DIVISOR;
const START_ANGLE_RADIANS = -HALF_RADIANS;
const DEFAULT_LAYOUT_CONFIG_INDEX = ZERO;
const LAYOUT_SIGNATURE_SEPARATOR = '|';
const CIRCULAR_MIN_RADIUS = Number('300');
const CIRCULAR_RADIUS_STEP = Number('20');
const FORCE_JITTER_RANGE = Number('50');
const FORCE_JITTER_MIDPOINT = Number('0.5');
const FORCE_ITERATIONS = Number('50');
const FORCE_REPULSION_STRENGTH = Number('5000');
const FORCE_ATTRACTION_STRENGTH = Number('0.1');
const FORCE_DAMPING = Number('0.9');
const FORCE_MIN_DISTANCE = GRID_COLUMNS_DIVISOR;
const FORCE_NORMALIZE_PADDING = Number('50');
const GRID_PADDING_MULTIPLIER = GRID_COMPACT_PADDING_DIVISOR;
const DEFAULT_NODE_WIDTH = Number('200');
const DEFAULT_NODE_HEIGHT = Number('80');
const DEFAULT_RANK_SEP = Number('100');
const DEFAULT_NODE_SEP = Number('60');
const DEFAULT_MARGIN_X = Number('40');
const DEFAULT_MARGIN_Y = Number('40');
const DEFAULT_CENTER_X = Number('500');
const DEFAULT_CENTER_Y = Number('400');
const TREE_NODE_SEP_FACTOR = Number('0.8');
const TREE_RANK_SEP_FACTOR = Number('1.5');

const DIRECTION_MAP: Record<string, string> = {
  BT: 'UP',
  LR: 'RIGHT',
  RL: 'LEFT',
  TB: 'DOWN',
};

interface ElkInstance {
  layout: (graph: ElkNode) => Promise<ElkNode>;
}

const elk: ElkInstance = new ELK();

interface LayoutTypeMap {
  'flow-chart': true;
  timeline: true;
  tree: true;
  'organic-network': true;
  'mind-map': true;
  gallery: true;
  wheel: true;
  compact: true;
}

type LayoutType = keyof LayoutTypeMap;

interface LayoutConfig {
  id: LayoutType;
  label: string;
  description: string;
  icon: string;
  algorithm: 'elk' | 'd3-force' | 'd3-radial' | 'grid' | 'circular';
  bestFor: string[];
}

const LAYOUT_CONFIGS: LayoutConfig[] = [
  {
    algorithm: 'elk',
    bestFor: ['Requirements traceability', 'Linear flows', 'Waterfall processes'],
    description: 'Top-to-bottom directed flow',
    icon: 'ArrowDown',
    id: 'flow-chart',
    label: 'Flow Chart',
  },
  {
    algorithm: 'elk',
    bestFor: ['Process flows', 'User journeys', 'Sequential tasks'],
    description: 'Left-to-right progression',
    icon: 'ArrowRight',
    id: 'timeline',
    label: 'Timeline',
  },
  {
    algorithm: 'elk',
    bestFor: ['Component trees', 'Org charts', 'File systems'],
    description: 'Hierarchical tree structure',
    icon: 'GitBranch',
    id: 'tree',
    label: 'Tree',
  },
  {
    algorithm: 'd3-force',
    bestFor: ['Exploratory analysis', 'Relationship discovery', 'Unknown structures'],
    description: 'Natural clustering by relationships',
    icon: 'Network',
    id: 'organic-network',
    label: 'Organic Network',
  },
  {
    algorithm: 'd3-radial',
    bestFor: ['Brainstorming', 'Centered exploration', 'Topic mapping'],
    description: 'Radial layout from center',
    icon: 'CircleDot',
    id: 'mind-map',
    label: 'Mind Map',
  },
  {
    algorithm: 'grid',
    bestFor: ['Quick overview', 'Many items', 'Visual scanning'],
    description: 'Grid for quick overview',
    icon: 'LayoutGrid',
    id: 'gallery',
    label: 'Gallery',
  },
  {
    algorithm: 'circular',
    bestFor: ['Cyclic processes', 'Stakeholder maps', 'Peer relationships'],
    description: 'Circular arrangement',
    icon: 'Circle',
    id: 'wheel',
    label: 'Wheel',
  },
  {
    algorithm: 'grid',
    bestFor: ['Large datasets', 'Dense views', 'Minimized space'],
    description: 'Dense space-efficient grid',
    icon: 'Minimize2',
    id: 'compact',
    label: 'Compact',
  },
];

interface ElkOptions {
  direction: 'TB' | 'LR' | 'BT' | 'RL';
  nodeWidth: number;
  nodeHeight: number;
  rankSep: number;
  nodeSep: number;
  marginX: number;
  marginY: number;
}

interface WorkerErrorMessage {
  type: 'error';
  error: string;
}

type WorkerMessage = LayoutResponse | WorkerErrorMessage;

interface Point {
  coordX: number;
  coordY: number;
}

interface ForcePosition {
  posX: number;
  posY: number;
  velX: number;
  velY: number;
}

interface LayoutSignatureParams<NodeData extends Record<string, unknown>> {
  edges: Edge[];
  layout: LayoutType;
  nodes: Node<NodeData>[];
}

interface SyncLayoutParams<NodeData extends Record<string, unknown>> {
  centerX: number;
  centerY: number;
  inputEdges: Edge[];
  inputNodes: Node<NodeData>[];
  layout: LayoutType;
  nodeHeight: number;
  nodeSep: number;
  nodeWidth: number;
}

interface SyncLayoutResult<NodeData extends Record<string, unknown>> {
  kind: 'sync' | 'async';
  nodes?: Node<NodeData>[];
}

interface ElkOptionsParams {
  layout: LayoutType;
  marginX: number;
  marginY: number;
  nodeHeight: number;
  nodeSep: number;
  nodeWidth: number;
  rankSep: number;
}

interface GridLayoutOptions {
  nodeWidth: number;
  nodeHeight: number;
  padding: number;
  compact?: boolean;
}

function getLayoutConfig({ layout }: { layout: LayoutType }): LayoutConfig {
  const match = LAYOUT_CONFIGS.find((config) => config.id === layout);
  if (match) {
    return match;
  }
  return LAYOUT_CONFIGS[DEFAULT_LAYOUT_CONFIG_INDEX];
}

function buildSignature<NodeData extends Record<string, unknown>>({
  edges,
  layout,
  nodes,
}: LayoutSignatureParams<NodeData>): string {
  const nodeIds = nodes.map((node) => node.id).join(LAYOUT_SIGNATURE_SEPARATOR);
  const edgeIds = edges
    .map((edge) => `${edge.id}:${edge.source}->${edge.target}`)
    .join(LAYOUT_SIGNATURE_SEPARATOR);
  return `${layout}${LAYOUT_SIGNATURE_SEPARATOR}${nodeIds}${LAYOUT_SIGNATURE_SEPARATOR}${edgeIds}`;
}

function getGridPadding({ compact, padding }: { compact?: boolean; padding: number }): number {
  if (compact === true) {
    return padding / GRID_COMPACT_PADDING_DIVISOR;
  }
  return padding;
}

function getGridColumnCount(nodeCount: number): number {
  const columnCount = Math.ceil(Math.sqrt(nodeCount));
  if (columnCount <= ZERO) {
    return GRID_COLUMNS_DIVISOR;
  }
  return columnCount;
}

function applyGridLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  options: GridLayoutOptions,
): Node<NodeData>[] {
  const { nodeWidth, nodeHeight, padding, compact } = options;
  const resolvedPadding = getGridPadding({ compact, padding });
  const safeColumnCount = getGridColumnCount(nodes.length);

  return nodes.map((node, index) => ({
    ...node,
    position: {
      x: (index % safeColumnCount) * (nodeWidth + resolvedPadding),
      y: Math.floor(index / safeColumnCount) * (nodeHeight + resolvedPadding),
    },
  }));
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
    if (!children.has(edge.source)) {
      children.set(edge.source, []);
    }
    const existing = children.get(edge.source);
    if (existing) {
      existing.push(edge.target);
    }
  }
  return children;
}

function computeDepths(rootIds: string[], children: Map<string, string[]>): Map<string, number> {
  const depths = new Map<string, number>();
  const queue: { id: string; depth: number }[] = rootIds.map((rootId) => ({
    depth: ZERO,
    id: rootId,
  }));

  while (queue.length > ZERO) {
    const next = queue.shift();
    if (next && !depths.has(next.id)) {
      depths.set(next.id, next.depth);
      const nodeChildren = children.get(next.id) ?? [];
      for (const childId of nodeChildren) {
        if (!depths.has(childId)) {
          queue.push({ depth: next.depth + ONE, id: childId });
        }
      }
    }
  }

  return depths;
}

function groupNodeIdsByDepth(depths: Map<string, number>): Map<number, string[]> {
  const byDepth = new Map<number, string[]>();
  for (const [nodeId, depth] of depths) {
    if (!byDepth.has(depth)) {
      byDepth.set(depth, []);
    }
    const existing = byDepth.get(depth);
    if (existing) {
      existing.push(nodeId);
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
    const radius = (depth + ONE) * baseRadius;
    const angleStep = FULL_CIRCLE_RADIANS / nodeIds.length;

    for (let index = ZERO; index < nodeIds.length; index += ONE) {
      const nodeId = nodeIds[index];
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
  let orphanIndex = ZERO;
  const baseRadius = Math.max(options.nodeWidth, options.nodeHeight) * RADIAL_RADIUS_MULTIPLIER;
  const halfNodeWidth = options.nodeWidth / GRID_COMPACT_PADDING_DIVISOR;
  const halfNodeHeight = options.nodeHeight / GRID_COMPACT_PADDING_DIVISOR;
  const orphanRadius = (depthCount + ONE) * baseRadius;
  const orphanAngleStep = FULL_CIRCLE_RADIANS / RADIAL_ORPHAN_SEGMENTS;

  return nodes.map((node) => {
    let position = positions.get(node.id);
    if (!position) {
      orphanIndex += ONE;
      const angle = orphanIndex * orphanAngleStep + START_ANGLE_RADIANS;
      position = {
        coordX: options.centerX + orphanRadius * Math.cos(angle) - halfNodeWidth,
        coordY: options.centerY + orphanRadius * Math.sin(angle) - halfNodeHeight,
      };
    }
    return {
      ...node,
      position: {
        x: position.coordX,
        y: position.coordY,
      },
    };
  });
}

function applyRadialLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: {
    nodeWidth: number;
    nodeHeight: number;
    centerX: number;
    centerY: number;
  },
): Node<NodeData>[] {
  const rootIds = getRootNodeIds(nodes, edges);
  const children = buildChildrenMap(edges);
  const depths = computeDepths(rootIds, children);
  const byDepth = groupNodeIdsByDepth(depths);
  const positions = buildRadialPositions(byDepth, options);

  return assignOrphanPositions(nodes, positions, options, byDepth.size);
}

function applyCircularLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  options: {
    nodeWidth: number;
    nodeHeight: number;
    centerX: number;
    centerY: number;
  },
): Node<NodeData>[] {
  const count = nodes.length;
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

function initializeForcePositions<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  options: { nodeWidth: number; nodeHeight: number; padding: number },
): Map<string, ForcePosition> {
  const positions = new Map<string, ForcePosition>();
  const columnCount = Math.ceil(Math.sqrt(nodes.length));
  let safeColumnCount = columnCount;
  if (safeColumnCount <= ZERO) {
    safeColumnCount = GRID_COLUMNS_DIVISOR;
  }

  for (let index = ZERO; index < nodes.length; index += ONE) {
    const node = nodes[index];
    const baseX =
      (index % safeColumnCount) * (options.nodeWidth + options.padding * GRID_PADDING_MULTIPLIER);
    const baseY =
      Math.floor(index / safeColumnCount) *
      (options.nodeHeight + options.padding * GRID_PADDING_MULTIPLIER);
    positions.set(node.id, {
      velX: ZERO,
      velY: ZERO,
      posX: baseX + (Math.random() - FORCE_JITTER_MIDPOINT) * FORCE_JITTER_RANGE,
      posY: baseY + (Math.random() - FORCE_JITTER_MIDPOINT) * FORCE_JITTER_RANGE,
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

      sourcePosition.velX += deltaX * FORCE_ATTRACTION_STRENGTH;
      sourcePosition.velY += deltaY * FORCE_ATTRACTION_STRENGTH;
      targetPosition.velX -= deltaX * FORCE_ATTRACTION_STRENGTH;
      targetPosition.velY -= deltaY * FORCE_ATTRACTION_STRENGTH;
    }
  }
}

function applyVelocity<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  positions: Map<string, ForcePosition>,
): void {
  for (const node of nodes) {
    const position = positions.get(node.id);
    if (position) {
      position.posX += position.velX;
      position.posY += position.velY;
      position.velX *= FORCE_DAMPING;
      position.velY *= FORCE_DAMPING;
    }
  }
}

function getMinPositionValues(positions: Map<string, ForcePosition>): {
  minX: number;
  minY: number;
} {
  let minX = Infinity;
  let minY = Infinity;
  for (const position of positions.values()) {
    minX = Math.min(minX, position.posX);
    minY = Math.min(minY, position.posY);
  }
  return { minX, minY };
}

function applyForceLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: { nodeWidth: number; nodeHeight: number; padding: number },
): Node<NodeData>[] {
  const positions = initializeForcePositions(nodes, options);
  for (let iteration = ZERO; iteration < FORCE_ITERATIONS; iteration += ONE) {
    applyRepulsion(nodes, positions);
    applyAttraction(edges, positions);
    applyVelocity(nodes, positions);
  }

  const { minX, minY } = getMinPositionValues(positions);

  return nodes.map((node) => {
    const position = positions.get(node.id);
    if (!position) {
      return node;
    }
    return {
      ...node,
      position: {
        x: position.posX - minX + FORCE_NORMALIZE_PADDING,
        y: position.posY - minY + FORCE_NORMALIZE_PADDING,
      },
    };
  });
}

function createElkGraph<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: ElkOptions,
): ElkNode {
  return {
    children: nodes.map((node) => ({
      height: options.nodeHeight,
      id: node.id,
      width: options.nodeWidth,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
    })) as ElkExtendedEdge[],
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': DIRECTION_MAP[options.direction] ?? 'DOWN',
      'elk.layered.spacing.nodeNodeBetweenLayers': String(options.rankSep),
      'elk.padding': `[left=${options.marginX}, top=${options.marginY}, right=${options.marginX}, bottom=${options.marginY}]`,
      'elk.spacing.nodeNode': String(options.nodeSep),
    },
  };
}

function mapElkPositions(children: ElkNode['children']): Map<string, Point> {
  const positionMap = new Map<string, Point>();
  const childNodes = children ?? [];
  for (const child of childNodes) {
    if (child.x !== undefined && child.y !== undefined) {
      positionMap.set(child.id, { coordX: child.x, coordY: child.y });
    }
  }
  return positionMap;
}

function buildNodePositions<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  positions: Map<string, Point>,
): Node<NodeData>[] {
  return nodes.map((node) => {
    const position = positions.get(node.id);
    if (!position) {
      return node;
    }

    return {
      ...node,
      position: {
        x: position.coordX,
        y: position.coordY,
      },
    };
  });
}

async function applyElkLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: ElkOptions,
): Promise<Node<NodeData>[]> {
  if (nodes.length === ZERO) {
    return [];
  }

  const graph = createElkGraph(nodes, edges, options);
  const result = await elk.layout(graph);
  const positionMap = mapElkPositions(result.children);

  return buildNodePositions(nodes, positionMap);
}

async function runElkLayoutInWorker<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: ElkOptions,
): Promise<Node<NodeData>[]> {
  if (typeof Worker === 'undefined') {
    return applyElkLayout(nodes, edges, options);
  }
  const worker = new Worker(new URL('./graphLayout.worker.ts', import.meta.url), {
    type: 'module',
  });
  const { promise, resolve, reject } = Promise.withResolvers<WorkerMessage>();

  const handleMessage = (event: MessageEvent<WorkerMessage>): void => {
    resolve(event.data);
  };
  const handleError = (): void => {
    reject(new Error('Layout worker failed'));
  };

  worker.addEventListener('message', handleMessage, { once: true });
  worker.addEventListener('error', handleError, { once: true });

  worker.postMessage(
    {
      edges: edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
      })),
      nodes: nodes.map((node) => ({ id: node.id })),
      options: options as ElkOptionsPayload,
      type: 'layout',
    },
    [],
  );

  try {
    const message: WorkerMessage = await promise;
    if (message.type === 'result') {
      const positionMap = new Map<string, Point>();
      for (const position of message.positions) {
        positionMap.set(position.id, { coordX: position.x, coordY: position.y });
      }
      return buildNodePositions(nodes, positionMap);
    }
    throw new Error(message.error ?? 'Layout worker error');
  } finally {
    worker.terminate();
  }
}

function resolveSyncLayout<NodeData extends Record<string, unknown>>({
  centerX,
  centerY,
  inputEdges,
  inputNodes,
  layout,
  nodeHeight,
  nodeSep,
  nodeWidth,
}: SyncLayoutParams<NodeData>): SyncLayoutResult<NodeData> {
  if (inputNodes.length === ZERO) {
    return { kind: 'sync', nodes: [] };
  }

  if (layout === 'organic-network') {
    return {
      kind: 'sync',
      nodes: applyForceLayout(inputNodes, inputEdges, {
        nodeHeight,
        nodeWidth,
        padding: nodeSep,
      }),
    };
  }

  if (layout === 'mind-map') {
    return {
      kind: 'sync',
      nodes: applyRadialLayout(inputNodes, inputEdges, {
        centerX,
        centerY,
        nodeHeight,
        nodeWidth,
      }),
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

  if (layout === 'wheel') {
    return {
      kind: 'sync',
      nodes: applyCircularLayout(inputNodes, {
        centerX,
        centerY,
        nodeHeight,
        nodeWidth,
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
        padding: nodeSep / GRID_COMPACT_PADDING_DIVISOR,
      }),
    };
  }

  return { kind: 'async' };
}

function getElkOptions({
  layout,
  marginX,
  marginY,
  nodeHeight,
  nodeSep,
  nodeWidth,
  rankSep,
}: ElkOptionsParams): ElkOptions | undefined {
  if (layout === 'flow-chart') {
    return {
      direction: 'TB',
      marginX,
      marginY,
      nodeHeight,
      nodeSep,
      nodeWidth,
      rankSep,
    };
  }

  if (layout === 'timeline') {
    return {
      direction: 'LR',
      marginX,
      marginY,
      nodeHeight,
      nodeSep,
      nodeWidth,
      rankSep,
    };
  }

  if (layout === 'tree') {
    return {
      direction: 'TB',
      marginX,
      marginY,
      nodeHeight,
      nodeSep: nodeSep * TREE_NODE_SEP_FACTOR,
      nodeWidth,
      rankSep: rankSep * TREE_RANK_SEP_FACTOR,
    };
  }

  return undefined;
}

async function computeElkLayoutInternal<NodeData extends Record<string, unknown>>(
  inputNodes: Node<NodeData>[],
  inputEdges: Edge[],
  options: ElkOptions,
): Promise<Node<NodeData>[]> {
  if (inputNodes.length > LAYOUT_WORKER_THRESHOLD) {
    return runElkLayoutInWorker(inputNodes, inputEdges, options);
  }
  return applyElkLayout(inputNodes, inputEdges, options);
}

export {
  DEFAULT_CENTER_X,
  DEFAULT_CENTER_Y,
  DEFAULT_MARGIN_X,
  DEFAULT_MARGIN_Y,
  DEFAULT_NODE_HEIGHT,
  DEFAULT_NODE_SEP,
  DEFAULT_NODE_WIDTH,
  DEFAULT_RANK_SEP,
  LAYOUT_CONFIGS,
  LAYOUT_SIGNATURE_SEPARATOR,
  ZERO,
  buildSignature,
  computeElkLayoutInternal,
  getElkOptions,
  getLayoutConfig,
  resolveSyncLayout,
};
export type { ElkOptions, LayoutConfig, LayoutType, SyncLayoutResult };
