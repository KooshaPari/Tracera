import type Graph from 'graphology';
import type { Node, Edge } from '@xyflow/react';

export interface GraphologyNodeAttributes {
  label: string;
  type: string;
  x?: number;
  y?: number;
  size?: number;
  color?: string;
  [key: string]: any;
}

export interface GraphologyEdgeAttributes {
  id: string;
  label?: string;
  weight?: number;
  color?: string;
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
