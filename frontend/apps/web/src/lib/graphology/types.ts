import type { Edge, Node } from '@xyflow/react';
import type Graph from 'graphology';

export interface GraphologyNodeAttributes {
  label: string;
  type: string;
  x?: number | undefined;
  y?: number | undefined;
  size?: number | undefined;
  color?: string | undefined;
  [key: string]: any;
}

export interface GraphologyEdgeAttributes {
  id: string;
  label?: string | undefined;
  weight?: number | undefined;
  color?: string | undefined;
  [key: string]: any;
}

export interface GraphologyAdapter {
  getGraph(): Graph;
  syncFromReactFlow(nodes: Node[], edges: Edge[]): void;
  toReactFlow(): { nodes: Node[]; edges: Edge[] };
  cluster(): Promise<Map<string, number>>;
  computeLayout(iterations?: number): Promise<void>;
  clear(): void;
}
