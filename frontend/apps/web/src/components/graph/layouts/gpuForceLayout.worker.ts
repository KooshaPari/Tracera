/**
 * Web Worker for GPU Force-Directed Layout
 *
 * Runs force simulation off the main thread to keep UI responsive.
 * Uses Barnes-Hut optimization for O(n log n) complexity.
 */

import type { Edge, Node } from '@xyflow/react';

import type { ForceSimulationConfig } from './gpuForceLayout';

import { GPUForceLayout } from './gpuForceLayout';

// ============================================================================
// MESSAGE TYPES
// ============================================================================

export interface ForceLayoutRequest {
  type: 'simulate';
  nodes: { id: string }[];
  edges: { id: string; source: string; target: string }[];
  config: ForceSimulationConfig;
}

export interface ForceLayoutResponse {
  type: 'result';
  positions: { id: string; x: number; y: number }[];
  duration: number;
}

export interface ForceLayoutProgress {
  type: 'progress';
  iteration: number;
  totalIterations: number;
  progress: number;
}

export interface ForceLayoutError {
  type: 'error';
  error: string;
}

// ============================================================================
// WORKER IMPLEMENTATION
// ============================================================================

const layoutEngine = new GPUForceLayout();

self.addEventListener('message', async (ev: MessageEvent<ForceLayoutRequest>) => {
  const msg = ev.data;

  if (msg.type !== 'simulate') {
    return;
  }

  const startTime = performance.now();

  try {
    // Convert minimal node data back to full Node objects
    const nodes: Node[] = msg.nodes.map((n) => ({
      data: {},
      id: n.id,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const edges: Edge[] = msg.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
    }));

    // Run simulation
    const result = await layoutEngine.simulate(nodes, edges, msg.config);

    // Extract positions
    const positions = result.map((node) => ({
      id: node.id,
      x: node.position.x,
      y: node.position.y,
    }));

    const duration = performance.now() - startTime;

    // Send result back to main thread
    const response: ForceLayoutResponse = {
      duration,
      positions,
      type: 'result',
    };

    (globalThis as unknown as Worker).postMessage(response);
  } catch (error) {
    const errorResponse: ForceLayoutError = {
      error: error instanceof Error ? error.message : String(error),
      type: 'error',
    };

    (globalThis as unknown as Worker).postMessage(errorResponse);
  }
});

// Handle cleanup
self.addEventListener('error', (err) => {
  const errorResponse: ForceLayoutError = {
    error: err.message || 'Worker error occurred',
    type: 'error',
  };

  (globalThis as unknown as Worker).postMessage(errorResponse);
});
