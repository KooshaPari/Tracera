/**
 * GraphologyDataLayer Usage Examples
 *
 * Demonstrates how to use the GraphologyDataLayer in React components
 */

import type { Node, Edge } from '@xyflow/react';

import { ReactFlow, useNodesState, useEdgesState } from '@xyflow/react';
import React, { useEffect, useState } from 'react';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';

import { createGraphologyDataLayer } from './GraphologyDataLayer';

/**
 * Example 1: Basic Usage with ReactFlow
 */
export function BasicGraphologyExample() {
  const [nodes, setNodes] = useNodesState<Node>([]);
  const [edges, setEdges] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGraph() {
      // Create data layer
      const dataLayer = createGraphologyDataLayer();

      // Sample data (normally from API)
      const sampleNodes: Node[] = [
        {
          id: '1',
          type: 'default',
          position: { x: 0, y: 0 },
          data: { label: 'Node 1' },
        },
        {
          id: '2',
          type: 'default',
          position: { x: 100, y: 100 },
          data: { label: 'Node 2' },
        },
        {
          id: '3',
          type: 'default',
          position: { x: 200, y: 0 },
          data: { label: 'Node 3' },
        },
      ];

      const sampleEdges: Edge[] = [
        { id: 'e1-2', source: '1', target: '2' },
        { id: 'e2-3', source: '2', target: '3' },
      ];

      // Initialize with data
      await dataLayer.initialize(sampleNodes, sampleEdges);

      // Compute layout
      await dataLayer.computeLayout({
        algorithm: 'forceAtlas2',
        iterations: 200,
      });

      // Convert back to ReactFlow
      const { nodes: layoutNodes, edges: layoutEdges } = dataLayer.toReactFlow();

      setNodes(layoutNodes);
      setEdges(layoutEdges);
      setLoading(false);

      console.log('Performance:', dataLayer.getPerformanceMetrics());
    }

    loadGraph();
  }, [setNodes, setEdges]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '24px' }}>
        <LoadingSpinner size='sm' text='Loading graph...' />
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView />
    </div>
  );
}

/**
 * Example 2: Large Graph with Community Detection
 */
export function LargeGraphWithCommunities() {
  const [nodes, setNodes] = useNodesState<Node>([]);
  const [edges, setEdges] = useEdgesState<Edge>([]);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    async function loadLargeGraph() {
      const dataLayer = createGraphologyDataLayer();

      // Generate large graph (10k nodes)
      const largeNodes: Node[] = Array.from({ length: 10000 }, (_, i) => ({
        id: `node-${i}`,
        type: 'default',
        position: { x: 0, y: 0 },
        data: { label: `Node ${i}` },
      }));

      const largeEdges: Edge[] = [];
      for (let i = 0; i < 10000; i++) {
        const target = Math.floor(Math.random() * 10000);
        if (target !== i) {
          largeEdges.push({
            id: `edge-${i}`,
            source: `node-${i}`,
            target: `node-${target}`,
          });
        }
      }

      // Initialize
      console.time('Initialize 10k nodes');
      await dataLayer.initialize(largeNodes, largeEdges);
      console.timeEnd('Initialize 10k nodes');

      // Detect communities
      console.time('Detect communities');
      const communities = await dataLayer.detectCommunities();
      console.timeEnd('Detect communities');

      // Color nodes by community
      const communityColors = new Map<number, string>();
      communities.forEach((communityId, nodeId) => {
        if (!communityColors.has(communityId)) {
          const hue = (communityId * 137.5) % 360;
          communityColors.set(communityId, `hsl(${hue}, 70%, 60%)`);
        }
        dataLayer.updateNode(nodeId, {
          color: communityColors.get(communityId),
        });
      });

      // Compute layout (circular for speed)
      console.time('Compute layout');
      await dataLayer.computeLayout({ algorithm: 'circular' });
      console.timeEnd('Compute layout');

      // Get stats
      const graphStats = dataLayer.getStats();
      setStats(graphStats);

      // Convert to ReactFlow (take only first 1000 nodes for display)
      const { nodes: allNodes, edges: allEdges } = dataLayer.toReactFlow();
      setNodes(allNodes.slice(0, 1000));
      setEdges(allEdges.slice(0, 1000));

      console.log('Performance:', dataLayer.getPerformanceMetrics());
    }

    loadLargeGraph();
  }, [setNodes, setEdges]);

  return (
    <div>
      {stats && (
        <div style={{ padding: '10px', background: '#f5f5f5' }}>
          <h3>Graph Statistics</h3>
          <p>Nodes: {stats.nodeCount}</p>
          <p>Edges: {stats.edgeCount}</p>
          <p>Communities: {stats.communityCount}</p>
          <p>Density: {stats.density.toFixed(4)}</p>
          <p>Avg Degree: {stats.averageDegree.toFixed(2)}</p>
        </div>
      )}
      <div style={{ width: '100%', height: '800px' }}>
        <ReactFlow nodes={nodes} edges={edges} fitView />
      </div>
    </div>
  );
}

/**
 * Example 3: Incremental Updates
 */
export function IncrementalGraphExample() {
  const [nodes, setNodes] = useNodesState<Node>([]);
  const [edges, setEdges] = useEdgesState<Edge>([]);
  const dataLayerRef = React.useRef(createGraphologyDataLayer());

  const addRandomNode = () => {
    const dataLayer = dataLayerRef.current;
    const newId = `node-${Date.now()}`;

    dataLayer.addNode({
      id: newId,
      type: 'default',
      position: { x: Math.random() * 500, y: Math.random() * 500 },
      data: { label: `New ${newId}` },
    });

    // Connect to random existing node
    const existingNodes = dataLayer.toReactFlow().nodes;
    if (existingNodes.length > 1) {
      const randomNode = existingNodes[Math.floor(Math.random() * existingNodes.length)]!;
      dataLayer.addEdge({
        id: `edge-${Date.now()}`,
        source: newId,
        target: randomNode.id,
      });
    }

    // Update display
    const { nodes: updatedNodes, edges: updatedEdges } = dataLayer.toReactFlow();
    setNodes(updatedNodes);
    setEdges(updatedEdges);
  };

  return (
    <div>
      <button onClick={addRandomNode}>Add Random Node</button>
      <div style={{ width: '100%', height: '600px' }}>
        <ReactFlow nodes={nodes} edges={edges} fitView />
      </div>
    </div>
  );
}

/**
 * Example 4: Custom Hook for GraphologyDataLayer
 */
export function useGraphologyLayer(initialNodes: Node[] = [], initialEdges: Edge[] = []) {
  const [dataLayer] = useState(() => createGraphologyDataLayer());
  const [nodes, setNodes] = useNodesState(initialNodes);
  const [edges, setEdges] = useEdgesState(initialEdges);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);

  const initialize = async (newNodes: Node[], newEdges: Edge[]) => {
    setLoading(true);
    try {
      await dataLayer.initialize(newNodes, newEdges);
      const { nodes: layoutNodes, edges: layoutEdges } = dataLayer.toReactFlow();
      setNodes(layoutNodes);
      setEdges(layoutEdges);
      setStats(dataLayer.getStats());
    } finally {
      setLoading(false);
    }
  };

  const computeLayout = async (options = {}) => {
    setLoading(true);
    try {
      await dataLayer.computeLayout(options);
      const { nodes: layoutNodes, edges: layoutEdges } = dataLayer.toReactFlow();
      setNodes(layoutNodes);
      setEdges(layoutEdges);
    } finally {
      setLoading(false);
    }
  };

  const detectCommunities = async () => {
    setLoading(true);
    try {
      const communities = await dataLayer.detectCommunities();
      setStats({ ...dataLayer.getStats(), communities });
      return communities;
    } finally {
      setLoading(false);
    }
  };

  const addNode = (node: Node) => {
    dataLayer.addNode(node);
    const { nodes: updatedNodes, edges: updatedEdges } = dataLayer.toReactFlow();
    setNodes(updatedNodes);
    setEdges(updatedEdges);
  };

  const addEdge = (edge: Edge) => {
    dataLayer.addEdge(edge);
    const { nodes: updatedNodes, edges: updatedEdges } = dataLayer.toReactFlow();
    setNodes(updatedNodes);
    setEdges(updatedEdges);
  };

  const clear = () => {
    dataLayer.clear();
    setNodes([]);
    setEdges([]);
    setStats(null);
  };

  return {
    nodes,
    edges,
    loading,
    stats,
    dataLayer,
    initialize,
    computeLayout,
    detectCommunities,
    addNode,
    addEdge,
    clear,
  };
}

/**
 * Example 5: Using the Custom Hook
 */
export function GraphWithCustomHook() {
  const { nodes, edges, loading, stats, initialize, computeLayout, detectCommunities } =
    useGraphologyLayer();

  useEffect(() => {
    const sampleNodes: Node[] = Array.from({ length: 100 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: { label: `Node ${i}` },
    }));

    const sampleEdges: Edge[] = Array.from({ length: 150 }, (_, i) => ({
      id: `edge-${i}`,
      source: `node-${Math.floor(Math.random() * 100)}`,
      target: `node-${Math.floor(Math.random() * 100)}`,
    }));

    initialize(sampleNodes, sampleEdges);
  }, [initialize]);

  return (
    <div>
      <div style={{ padding: '10px', background: '#f5f5f5' }}>
        <button onClick={() => computeLayout({ algorithm: 'forceAtlas2' })} disabled={loading}>
          ForceAtlas2 Layout
        </button>
        <button onClick={() => computeLayout({ algorithm: 'circular' })} disabled={loading}>
          Circular Layout
        </button>
        <button onClick={detectCommunities} disabled={loading}>
          Detect Communities
        </button>

        {stats && (
          <div>
            <p>
              Nodes: {stats.nodeCount} | Edges: {stats.edgeCount}
            </p>
          </div>
        )}
      </div>

      <div style={{ width: '100%', height: '600px' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '24px' }}>
            <LoadingSpinner size='sm' text='Loading...' />
          </div>
        ) : (
          <ReactFlow nodes={nodes} edges={edges} fitView />
        )}
      </div>
    </div>
  );
}
