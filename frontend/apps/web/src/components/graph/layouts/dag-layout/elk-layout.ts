import type { Edge, Node } from '@xyflow/react';
import type { ElkExtendedEdge, ElkNode } from 'elkjs';

import ELK from 'elkjs/lib/elk.bundled.js';

import type { ElkOptions, LayoutType } from './types';

import { LAYOUT_WORKER_THRESHOLD, TREE_NODE_SEP_FACTOR, TREE_RANK_SEP_FACTOR } from './constants';

const DIRECTION_MAP: Record<ElkOptions['direction'], string> = {
  BT: 'UP',
  LR: 'RIGHT',
  RL: 'LEFT',
  TB: 'DOWN',
};

interface ElkInstance {
  layout: (graph: ElkNode) => Promise<ElkNode>;
}

const elk: ElkInstance = new ELK();

interface LayoutResponsePosition {
  id: string;
  x: number;
  y: number;
}

interface LayoutResponseResult {
  type: 'result';
  positions: LayoutResponsePosition[];
}

interface LayoutResponseError {
  type: 'error';
  error: string;
}

type WorkerMessage = LayoutResponseResult | LayoutResponseError;

interface PromiseWithResolvers<Value> {
  promise: Promise<Value>;
  resolve: (value: Value) => void;
  reject: (reason: unknown) => void;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isPromiseWithResolvers<Value>(value: unknown): value is PromiseWithResolvers<Value> {
  if (!isRecord(value)) {
    return false;
  }

  const candidate = value;
  return (
    typeof candidate['resolve'] === 'function' &&
    typeof candidate['reject'] === 'function' &&
    candidate['promise'] instanceof Promise
  );
}

function getPromiseWithResolvers<Value>(): PromiseWithResolvers<Value> | undefined {
  const withResolversCandidate = Reflect.get(Promise, 'withResolvers');
  if (typeof withResolversCandidate !== 'function') {
    return undefined;
  }

  const result: unknown = withResolversCandidate();
  if (!isPromiseWithResolvers<Value>(result)) {
    return undefined;
  }
  return result;
}

async function applyElkLayout<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: ElkOptions,
): Promise<Node<NodeData>[]> {
  if (nodes.length === 0) {
    return [];
  }

  const graph: ElkNode = {
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

  const result = await elk.layout(graph);

  const positionMap = new Map<string, { x: number; y: number }>();
  for (const child of result.children ?? []) {
    if (child.x !== undefined && child.y !== undefined) {
      positionMap.set(child.id, { x: child.x, y: child.y });
    }
  }

  return nodes.map((node) => {
    const pos = positionMap.get(node.id);
    if (!pos) {
      return node;
    }
    return { ...node, position: pos };
  });
}

async function runElkLayoutInWorker<NodeData extends Record<string, unknown>>(
  nodes: Node<NodeData>[],
  edges: Edge[],
  options: ElkOptions,
): Promise<Node<NodeData>[]> {
  if (typeof Worker === 'undefined') {
    return applyElkLayout(nodes, edges, options);
  }

  const resolvers = getPromiseWithResolvers<Node<NodeData>[]>();
  if (!resolvers) {
    return applyElkLayout(nodes, edges, options);
  }

  const { promise, resolve, reject } = resolvers;
  const worker = new Worker(new URL('../graphLayout.worker.ts', import.meta.url), {
    type: 'module',
  });

  const onMessage = (event: MessageEvent<WorkerMessage>): void => {
    worker.terminate();
    if (event.data.type === 'result') {
      const positionMap = new Map(
        event.data.positions.map((position) => [position.id, { x: position.x, y: position.y }]),
      );
      resolve(
        nodes.map((node) => {
          const pos = positionMap.get(node.id);
          if (!pos) {
            return node;
          }
          return { ...node, position: pos };
        }),
      );
      return;
    }
    reject(new Error(event.data.error ?? 'Layout worker error'));
  };

  worker.addEventListener('message', onMessage);
  worker.addEventListener('error', () => {
    worker.terminate();
    reject(new Error('Layout worker failed'));
  });

  worker.postMessage(
    {
      edges: edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
      })),
      nodes: nodes.map((node) => ({ id: node.id })),
      options: {
        direction: options.direction,
        marginX: options.marginX,
        marginY: options.marginY,
        nodeHeight: options.nodeHeight,
        nodeSep: options.nodeSep,
        nodeWidth: options.nodeWidth,
        rankSep: options.rankSep,
      },
      type: 'layout',
    },
    [],
  );

  const result = await promise;
  return result;
}

async function computeElkLayoutInternal<NodeData extends Record<string, unknown>>(
  inputNodes: Node<NodeData>[],
  inputEdges: Edge[],
  options: ElkOptions,
): Promise<Node<NodeData>[]> {
  if (inputNodes.length > LAYOUT_WORKER_THRESHOLD) {
    const result = await runElkLayoutInWorker(inputNodes, inputEdges, options);
    return result;
  }
  const result = await applyElkLayout(inputNodes, inputEdges, options);
  return result;
}

function getElkOptions(
  layout: LayoutType,
  options: {
    marginX: number;
    marginY: number;
    nodeHeight: number;
    nodeSep: number;
    nodeWidth: number;
    rankSep: number;
  },
): ElkOptions | undefined {
  const { marginX, marginY, nodeHeight, nodeSep, nodeWidth, rankSep } = options;

  if (layout === 'flow-chart') {
    return { direction: 'TB', marginX, marginY, nodeHeight, nodeSep, nodeWidth, rankSep };
  }
  if (layout === 'timeline') {
    return { direction: 'LR', marginX, marginY, nodeHeight, nodeSep, nodeWidth, rankSep };
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

export { applyElkLayout, computeElkLayoutInternal, getElkOptions, runElkLayoutInWorker };
