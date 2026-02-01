#!/usr/bin/env bun

/**
 * Generate Test Graph Data
 *
 * Creates synthetic graph data for performance testing
 * Usage: bun run scripts/generate-test-graph.ts <nodeCount> <edgeCount>
 * Example: bun run scripts/generate-test-graph.ts 10000 15000
 */

import fs from 'node:fs';
import path from 'node:path';

const NODE_TYPES = ['requirement', 'test', 'defect', 'epic', 'story', 'task'] as const;
const EDGE_TYPES = ['implements', 'tests', 'depends_on', 'related_to'] as const;

interface TestNode {
  id: string;
  type: string;
  label: string;
  position: { x: number; y: number };
  data?: {
    title?: string;
    description?: string;
    status?: string;
    priority?: string;
  };
}

interface TestEdge {
  id: string;
  sourceId: string;
  targetId: string;
  type: string;
}

interface TestGraph {
  nodes: TestNode[];
  edges: TestEdge[];
  metadata: {
    generated: string;
    nodeCount: number;
    edgeCount: number;
    avgDegree: number;
  };
}

function generateTestGraph(nodeCount: number, edgeCount: number): TestGraph {
  console.log(`Generating test graph with ${nodeCount} nodes and ${edgeCount} edges...`);

  // Generate nodes with realistic spatial distribution
  const nodes: TestNode[] = Array.from({ length: nodeCount }, (_, i) => {
    const nodeType = NODE_TYPES[i % NODE_TYPES.length];

    // Create clusters for more realistic graph structure
    const clusterId = Math.floor(i / 100);
    const clusterCenterX = (clusterId % 10) * 1000;
    const clusterCenterY = Math.floor(clusterId / 10) * 1000;

    return {
      id: `test-node-${i}`,
      type: nodeType,
      label: `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} ${i}`,
      position: {
        x: clusterCenterX + Math.random() * 800 - 400,
        y: clusterCenterY + Math.random() * 800 - 400,
      },
      data: {
        title: `Test ${nodeType} ${i}`,
        description: `Generated test ${nodeType} for performance testing`,
        status: ['open', 'in_progress', 'done', 'blocked'][Math.floor(Math.random() * 4)],
        priority: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
      },
    };
  });

  // Generate edges with realistic connections
  const edges: TestEdge[] = [];
  const edgesPerNode = Math.floor(edgeCount / nodeCount);
  const remainingEdges = edgeCount % nodeCount;

  for (let i = 0; i < nodeCount; i++) {
    const numEdges = edgesPerNode + (i < remainingEdges ? 1 : 0);

    for (let j = 0; j < numEdges; j++) {
      let targetIdx = Math.floor(Math.random() * nodeCount);

      // Prefer connections to nearby nodes (cluster locality)
      if (Math.random() < 0.7) {
        const maxDistance = 200; // Prefer nodes within 200 indices
        targetIdx = Math.max(0, Math.min(nodeCount - 1, i + Math.floor(Math.random() * maxDistance * 2) - maxDistance));
      }

      // Avoid self-loops
      if (targetIdx === i) {
        targetIdx = (i + 1) % nodeCount;
      }

      const edgeId = `test-edge-${edges.length}`;
      const edgeType = EDGE_TYPES[edges.length % EDGE_TYPES.length];

      edges.push({
        id: edgeId,
        sourceId: `test-node-${i}`,
        targetId: `test-node-${targetIdx}`,
        type: edgeType,
      });
    }
  }

  const avgDegree = edgeCount / nodeCount;

  return {
    nodes,
    edges,
    metadata: {
      generated: new Date().toISOString(),
      nodeCount,
      edgeCount,
      avgDegree: Math.round(avgDegree * 100) / 100,
    },
  };
}

function main() {
  const args = process.argv.slice(2);

  const nodeCount = args[0] ? parseInt(args[0], 10) : 10000;
  const edgeCount = args[1] ? parseInt(args[1], 10) : 15000;

  if (isNaN(nodeCount) || isNaN(edgeCount)) {
    console.error('Usage: bun run scripts/generate-test-graph.ts <nodeCount> <edgeCount>');
    process.exit(1);
  }

  if (nodeCount < 1 || edgeCount < 1) {
    console.error('Node count and edge count must be positive integers');
    process.exit(1);
  }

  const startTime = performance.now();
  const testGraph = generateTestGraph(nodeCount, edgeCount);
  const generationTime = performance.now() - startTime;

  // Write to file
  const outputDir = path.join(process.cwd(), 'test-data');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, `test-graph-${nodeCount}.json`);
  fs.writeFileSync(outputPath, JSON.stringify(testGraph, null, 2));

  console.log('\n✓ Test graph generated successfully!');
  console.log(`  Nodes: ${testGraph.metadata.nodeCount}`);
  console.log(`  Edges: ${testGraph.metadata.edgeCount}`);
  console.log(`  Average degree: ${testGraph.metadata.avgDegree}`);
  console.log(`  Generation time: ${Math.round(generationTime)}ms`);
  console.log(`  Output: ${outputPath}`);
  console.log(`  File size: ${(fs.statSync(outputPath).size / 1024 / 1024).toFixed(2)} MB`);
}

main();
