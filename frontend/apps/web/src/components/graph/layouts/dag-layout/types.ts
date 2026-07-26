import type { Edge, Node } from '@xyflow/react';

type LayoutType =
  | 'flow-chart'
  | 'timeline'
  | 'tree'
  | 'organic-network'
  | 'mind-map'
  | 'gallery'
  | 'wheel'
  | 'compact';

interface LayoutConfig {
  id: LayoutType;
  label: string;
  description: string;
  icon: string;
  algorithm: 'elk' | 'd3-force' | 'd3-radial' | 'grid' | 'circular';
  bestFor: string[];
}

interface ElkOptions {
  direction: 'TB' | 'LR' | 'BT' | 'RL';
  nodeWidth: number;
  nodeHeight: number;
  rankSep: number;
  nodeSep: number;
  marginX: number;
  marginY: number;
}

interface SyncLayoutResult<NodeData extends Record<string, unknown>> {
  kind: 'sync' | 'async';
  nodes?: Node<NodeData>[] | undefined;
}

interface LayoutSignatureParams<NodeData extends Record<string, unknown>> {
  edges: Edge[];
  layout: LayoutType;
  nodes: Node<NodeData>[];
}

export type { ElkOptions, LayoutConfig, LayoutSignatureParams, LayoutType, SyncLayoutResult };
