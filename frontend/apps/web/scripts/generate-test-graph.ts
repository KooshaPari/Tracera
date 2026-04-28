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
  // Generate nodes with realistic spatial distribution
  const nodes: TestNode[] = Array.from({ length: nodeCount }, (_, i) => {
    const nodeType = NODE_TYPES[i % NODE_TYPES.length];

    // Create clusters for more realistic graph structure
    const clusterId = Math.floor(i / 100);
    const clusterCenterX = (clusterId % 10) * 1000;
    const clusterCenterY = Math.floor(clusterId / 10) * 1000;

    return {
      data: {
        description: `Generated test ${nodeType} for performance testing`,
        priority: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
        status: ['open', 'in_progress', 'done', 'blocked'][Math.floor(Math.random() * 4)],
        title: `Test ${nodeType} ${i}`,
      },
      id: `test-node-${i}`,
      label: `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} ${i}`,
      position: {
        x: clusterCenterX + Math.random() * 800 - 400,
        y: clusterCenterY + Math.random() * 800 - 400,
      },
      type: nodeType,
    };
  });

  // Generate edges with realistic connections
  const edges: TestEdge[] = [];
  const edgesPerNode = Math.floor(edgeCount / nodeCount);
  const remainingEdges = edgeCount % nodeCount;

  for (let i = 0; i < nodeCount; i += 1) {
    const numEdges = edgesPerNode + (i < remainingEdges ? 1 : 0);

    for (let j = 0; j < numEdges; j += 1) {
      let targetIdx = Math.floor(Math.random() * nodeCount);

      // Prefer connections to nearby nodes (cluster locality)
      if (Math.random() < 0.7) {
        const maxDistance = 200; // Prefer nodes within 200 indices
        targetIdx = Math.max(
          0,
          Math.min(nodeCount - 1, i + Math.floor(Math.random() * maxDistance * 2) - maxDistance),
        );
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
    edges,
    metadata: {
      avgDegree: Math.round(avgDegree * 100) / 100,
      edgeCount,
      generated: new Date().toISOString(),
      nodeCount,
    },
    nodes,
  };
}

function main() {
  const args = process.argv.slice(2);

  const nodeCount = args[0] ? Number.parseInt(args[0], 10) : 10_000;
  const edgeCount = args[1] ? Number.parseInt(args[1], 10) : 15_000;

  if (isNaN(nodeCount) || isNaN(edgeCount)) {
    process.exit(1);
  }

  if (nodeCount < 1 || edgeCount < 1) {
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
}

main();
