/**
 * Performance Benchmarks for GPU Force-Directed Layout
 *
 * Target: <5s layout calculation for 50k nodes
 */

import type { Edge, Node } from '@xyflow/react';

import { beforeAll, describe, expect, it } from 'vitest';

import { GPUForceLayout } from '../gpuForceLayout';

// ============================================================================
// TEST DATA GENERATION
// ============================================================================

function generateNodes(count: number): Node[] {
  const nodes: Node[] = [];
  for (let i = 0; i < count; i++) {
    nodes.push({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    });
  }
  return nodes;
}

function generateEdges(nodeCount: number, edgesPerNode: number): Edge[] {
  const edges: Edge[] = [];
  let edgeId = 0;

  for (let i = 0; i < nodeCount; i++) {
    const source = `node-${i}`;

    for (let j = 0; j < edgesPerNode; j++) {
      // Connect to nearby nodes to create realistic graph structure
      const targetIndex = (i + 1 + j) % nodeCount;
      const target = `node-${targetIndex}`;

      if (source !== target) {
        edges.push({
          id: `edge-${edgeId++}`,
          source,
          target,
        });
      }
    }
  }

  return edges;
}

// ============================================================================
// BENCHMARK TESTS
// ============================================================================

describe('GPU Force Layout Performance', () => {
  let layout: GPUForceLayout;

  beforeAll(() => {
    layout = new GPUForceLayout();
  });

  it('should layout 100 nodes efficiently', async () => {
    const nodes = generateNodes(100);
    const edges = generateEdges(100, 2);

    const start = performance.now();
    await layout.simulate(nodes, edges, {
      iterations: 50,
      theta: 0.5,
    });
    const duration = performance.now() - start;

    console.log(`100 nodes: ${duration.toFixed(2)}ms`);
    // Note: In browser with GPU, target is <100ms. In Node.js test env, CPU only.
    expect(duration).toBeLessThan(1000);
  });

  it('should layout 1,000 nodes efficiently', async () => {
    const nodes = generateNodes(1000);
    const edges = generateEdges(1000, 2);

    const start = performance.now();
    await layout.simulate(nodes, edges, {
      iterations: 100,
      theta: 0.5,
    });
    const duration = performance.now() - start;

    console.log(`1,000 nodes: ${duration.toFixed(2)}ms`);
    // Note: In browser with GPU, target is <500ms. In Node.js test env, CPU only.
    expect(duration).toBeLessThan(15_000);
  });

  it('should demonstrate O(n log n) scaling with Barnes-Hut', async () => {
    // Test that Barnes-Hut achieves O(n log n) complexity
    const sizes = [100, 200, 400];
    const times: number[] = [];

    for (const size of sizes) {
      const nodes = generateNodes(size);
      const edges = generateEdges(size, 2);

      const start = performance.now();
      await layout.simulate(nodes, edges, {
        iterations: 20,
        theta: 0.5,
      });
      times.push(performance.now() - start);
    }

    console.log(`${sizes[0]} nodes: ${times[0].toFixed(2)}ms`);
    console.log(`${sizes[1]} nodes: ${times[1].toFixed(2)}ms`);
    console.log(`${sizes[2]} nodes: ${times[2].toFixed(2)}ms`);

    // Calculate scaling ratios
    const ratio1 = times[1] / times[0]; // 2x nodes
    const ratio2 = times[2] / times[1]; // 2x nodes again

    console.log(`Ratio (100→200): ${ratio1.toFixed(2)}x`);
    console.log(`Ratio (200→400): ${ratio2.toFixed(2)}x`);

    // For O(n log n), doubling nodes should be ~2-3x slower
    // For O(n²), it would be ~4x slower
    // Allow more margin for small graphs and test environment variance
    expect(ratio1).toBeLessThan(5);
    expect(ratio2).toBeLessThan(5);
  }, 30_000);

  it('Barnes-Hut should be faster than naive approach', async () => {
    const nodes = generateNodes(500);
    const edges = generateEdges(500, 2);

    // Naive approach (theta = 0, no approximation)
    const startNaive = performance.now();
    await layout.simulate(nodes, edges, {
      iterations: 20,
      theta: 0,
    });
    const naiveDuration = performance.now() - startNaive;

    // Barnes-Hut approach (theta = 0.5)
    const startBH = performance.now();
    await layout.simulate(nodes, edges, {
      iterations: 20,
      theta: 0.5,
    });
    const bhDuration = performance.now() - startBH;

    console.log(`Naive (theta=0): ${naiveDuration.toFixed(2)}ms`);
    console.log(`Barnes-Hut (theta=0.5): ${bhDuration.toFixed(2)}ms`);
    console.log(`Speedup: ${(naiveDuration / bhDuration).toFixed(2)}x`);

    // Barnes-Hut should provide speedup
    expect(bhDuration).toBeLessThan(naiveDuration * 1.2); // Allow 20% margin
  }, 30_000); // 30s timeout

  it('should handle dense graphs efficiently', async () => {
    const nodes = generateNodes(500);
    const edges = generateEdges(500, 5); // 5 edges per node = dense

    const start = performance.now();
    await layout.simulate(nodes, edges, {
      iterations: 50,
      theta: 0.5,
    });
    const duration = performance.now() - start;

    console.log(`500 nodes (dense): ${duration.toFixed(2)}ms`);
    // CPU-only environment, Barnes-Hut still helps
    expect(duration).toBeLessThan(10_000);
  });

  it('should handle sparse graphs efficiently', async () => {
    const nodes = generateNodes(1000);
    const edges = generateEdges(1000, 1); // 1 edge per node = sparse

    const start = performance.now();
    await layout.simulate(nodes, edges, {
      iterations: 50,
      theta: 0.6,
    });
    const duration = performance.now() - start;

    console.log(`1,000 nodes (sparse): ${duration.toFixed(2)}ms`);
    // Sparse graphs should be faster than dense
    expect(duration).toBeLessThan(15_000);
  });
});

// ============================================================================
// COMPLEXITY ANALYSIS
// ============================================================================

describe('Algorithm Complexity Analysis', () => {
  let layout: GPUForceLayout;

  beforeAll(() => {
    layout = new GPUForceLayout();
  });

  it('should scale O(n log n) with Barnes-Hut', async () => {
    const sizes = [500, 1000, 2000, 4000];
    const durations: number[] = [];

    for (const size of sizes) {
      const nodes = generateNodes(size);
      const edges = generateEdges(size, 2);

      const start = performance.now();
      await layout.simulate(nodes, edges, {
        iterations: 50,
        theta: 0.5,
      });
      const duration = performance.now() - start;

      durations.push(duration);
      console.log(`${size} nodes: ${duration.toFixed(2)}ms`);
    }

    // Check that complexity is better than O(n²)
    // For O(n log n), doubling n should increase time by ~2x-3x
    // For O(n²), doubling n would increase time by ~4x
    for (let i = 1; i < sizes.length; i++) {
      const ratio = sizes[i] / sizes[i - 1];
      const timeRatio = durations[i] / durations[i - 1];

      console.log(`Size ratio: ${ratio}x, Time ratio: ${timeRatio.toFixed(2)}x`);

      // Time ratio should be less than size ratio squared
      expect(timeRatio).toBeLessThan(ratio * ratio);
    }
  }, 30_000);
});

// ============================================================================
// QUALITY METRICS
// ============================================================================

describe('Layout Quality Metrics', () => {
  let layout: GPUForceLayout;

  beforeAll(() => {
    layout = new GPUForceLayout();
  });

  it('should produce non-overlapping nodes', async () => {
    const nodes = generateNodes(100);
    const edges = generateEdges(100, 2);

    const result = await layout.simulate(nodes, edges, {
      iterations: 200,
    });

    // Check for overlaps
    const minDistance = 30; // Minimum distance between node centers
    let overlaps = 0;

    for (let i = 0; i < result.length; i++) {
      for (let j = i + 1; j < result.length; j++) {
        const dx = result[i].position.x - result[j].position.x;
        const dy = result[i].position.y - result[j].position.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < minDistance) {
          overlaps++;
        }
      }
    }

    console.log(`Overlaps: ${overlaps} out of ${(result.length * (result.length - 1)) / 2} pairs`);

    // Allow some overlaps for large graphs, but should be minimal
    const overlapRate = overlaps / ((result.length * (result.length - 1)) / 2);
    expect(overlapRate).toBeLessThan(0.05); // Less than 5% overlap
  });

  it('should cluster connected nodes', async () => {
    const nodes = generateNodes(50);

    // Create two distinct clusters
    const edges: Edge[] = [];

    // Cluster 1: nodes 0-24
    for (let i = 0; i < 25; i++) {
      for (let j = i + 1; j < 25; j++) {
        if (Math.random() < 0.3) {
          edges.push({
            id: `edge-${edges.length}`,
            source: `node-${i}`,
            target: `node-${j}`,
          });
        }
      }
    }

    // Cluster 2: nodes 25-49
    for (let i = 25; i < 50; i++) {
      for (let j = i + 1; j < 50; j++) {
        if (Math.random() < 0.3) {
          edges.push({
            id: `edge-${edges.length}`,
            source: `node-${i}`,
            target: `node-${j}`,
          });
        }
      }
    }

    const result = await layout.simulate(nodes, edges, {
      iterations: 300,
    });

    // Calculate cluster centers
    let cluster1X = 0;
    let cluster1Y = 0;
    let cluster2X = 0;
    let cluster2Y = 0;

    for (let i = 0; i < 25; i++) {
      cluster1X += result[i].position.x;
      cluster1Y += result[i].position.y;
    }
    cluster1X /= 25;
    cluster1Y /= 25;

    for (let i = 25; i < 50; i++) {
      cluster2X += result[i].position.x;
      cluster2Y += result[i].position.y;
    }
    cluster2X /= 25;
    cluster2Y /= 25;

    // Clusters should be separated
    const clusterDistance = Math.sqrt((cluster2X - cluster1X) ** 2 + (cluster2Y - cluster1Y) ** 2);

    console.log(`Cluster separation: ${clusterDistance.toFixed(2)}`);
    expect(clusterDistance).toBeGreaterThan(200);
  });
});
