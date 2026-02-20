/**
 * HybridGraphView - Integration Example
 *
 * Demonstrates automatic threshold switching between ReactFlow and Sigma.js WebGL
 *
 * Features:
 * - Automatic mode switching at 10k nodes
 * - Performance mode indicator
 * - Threshold warning near limit
 * - Force override options
 * - Rich node detail panel in WebGL mode
 */

import type { Edge, Node } from '@xyflow/react';

import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { logger } from '@/lib/logger';

import { HybridGraphView } from './HybridGraphView';

export function HybridGraphViewExample() {
  const [nodeCount, setNodeCount] = useState(5000);

  // Generate test data
  const nodes: Node[] = Array.from({ length: nodeCount }, (_, i) => ({
    data: {
      description: `Test node ${i}`,
      label: `Node ${i}`,
      status: i % 3 === 0 ? 'active' : 'inactive',
    },
    id: `node-${i}`,
    position: { x: Math.random() * 1000, y: Math.random() * 1000 },
    type: 'default',
  }));

  const edges: Edge[] = Array.from({ length: Math.min(nodeCount * 2, 20_000) }, (_, i) => ({
    id: `edge-${i}`,
    source: `node-${Math.floor(Math.random() * nodeCount)}`,
    target: `node-${Math.floor(Math.random() * nodeCount)}`,
  }));

  return (
    <div className='flex h-screen w-screen flex-col'>
      {/* Controls */}
      <div className='bg-card flex items-center gap-4 border-b p-4'>
        <div className='text-sm font-medium'>Test Hybrid Graph Switching:</div>
        <Button
          size='sm'
          variant={nodeCount === 5000 ? 'default' : 'outline'}
          onClick={() => {
            setNodeCount(5000);
          }}
        >
          5k nodes (ReactFlow)
        </Button>
        <Button
          size='sm'
          variant={nodeCount === 9500 ? 'default' : 'outline'}
          onClick={() => {
            setNodeCount(9500);
          }}
        >
          9.5k nodes (Near threshold)
        </Button>
        <Button
          size='sm'
          variant={nodeCount === 15_000 ? 'default' : 'outline'}
          onClick={() => {
            setNodeCount(15_000);
          }}
        >
          15k nodes (WebGL)
        </Button>
        <Button
          size='sm'
          variant={nodeCount === 50_000 ? 'default' : 'outline'}
          onClick={() => {
            setNodeCount(50_000);
          }}
        >
          50k nodes (WebGL)
        </Button>
      </div>

      {/* Hybrid Graph View */}
      <div className='flex-1'>
        <HybridGraphView
          nodes={nodes}
          edges={edges}
          onNodeClick={(nodeId) => {
            logger.info('Node clicked:', nodeId);
          }}
          onNodeExpand={(nodeId) => {
            logger.info('Node expand:', nodeId);
          }}
          onNodeNavigate={(nodeId) => {
            logger.info('Node navigate:', nodeId);
          }}
        />
      </div>
    </div>
  );
}

/**
 * Force Override Example
 *
 * Demonstrates manual override of automatic switching
 */
export function ForceOverrideExample() {
  const [mode, setMode] = useState<'auto' | 'reactflow' | 'webgl'>('auto');
  const nodeCount = 12_000; // Above threshold

  const nodes: Node[] = Array.from({ length: nodeCount }, (_, i) => ({
    data: { label: `Node ${i}` },
    id: `node-${i}`,
    position: { x: Math.random() * 1000, y: Math.random() * 1000 },
    type: 'default',
  }));

  return (
    <div className='flex h-screen w-screen flex-col'>
      <div className='bg-card flex items-center gap-4 border-b p-4'>
        <div className='text-sm font-medium'>Force Mode (12k nodes):</div>
        <Button
          size='sm'
          variant={mode === 'auto' ? 'default' : 'outline'}
          onClick={() => {
            setMode('auto');
          }}
        >
          Auto (WebGL)
        </Button>
        <Button
          size='sm'
          variant={mode === 'reactflow' ? 'default' : 'outline'}
          onClick={() => {
            setMode('reactflow');
          }}
        >
          Force ReactFlow
        </Button>
        <Button
          size='sm'
          variant={mode === 'webgl' ? 'default' : 'outline'}
          onClick={() => {
            setMode('webgl');
          }}
        >
          Force WebGL
        </Button>
      </div>

      <div className='flex-1'>
        <HybridGraphView
          nodes={nodes}
          edges={[]}
          config={{
            forceReactFlow: mode === 'reactflow',
            forceWebGL: mode === 'webgl',
          }}
        />
      </div>
    </div>
  );
}

/**
 * Custom Threshold Example
 *
 * Demonstrates custom threshold configuration
 */
export function CustomThresholdExample() {
  const [threshold, setThreshold] = useState(10_000);
  const nodeCount = 7500;

  const nodes: Node[] = Array.from({ length: nodeCount }, (_, i) => ({
    data: { label: `Node ${i}` },
    id: `node-${i}`,
    position: { x: Math.random() * 1000, y: Math.random() * 1000 },
    type: 'default',
  }));

  return (
    <div className='flex h-screen w-screen flex-col'>
      <div className='bg-card flex items-center gap-4 border-b p-4'>
        <div className='text-sm font-medium'>Custom Threshold (7.5k nodes):</div>
        <Button
          size='sm'
          variant={threshold === 5000 ? 'default' : 'outline'}
          onClick={() => {
            setThreshold(5000);
          }}
        >
          Threshold: 5k (→ WebGL)
        </Button>
        <Button
          size='sm'
          variant={threshold === 10_000 ? 'default' : 'outline'}
          onClick={() => {
            setThreshold(10_000);
          }}
        >
          Threshold: 10k (→ ReactFlow)
        </Button>
        <Button
          size='sm'
          variant={threshold === 20_000 ? 'default' : 'outline'}
          onClick={() => {
            setThreshold(20_000);
          }}
        >
          Threshold: 20k (→ ReactFlow)
        </Button>
      </div>

      <div className='flex-1'>
        <HybridGraphView nodes={nodes} edges={[]} config={{ nodeThreshold: threshold }} />
      </div>
    </div>
  );
}
