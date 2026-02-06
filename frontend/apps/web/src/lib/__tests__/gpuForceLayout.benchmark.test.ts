/**
 * GPU Force Layout Benchmarks
 *
 * Measures performance of GPU vs CPU force-directed layout
 * Targets: 100k nodes in <5 seconds (vs 30+ seconds CPU)
 */

import type { Edge, Node } from '@xyflow/react';

import { describe, it, expect, beforeAll } from 'vitest';

import {
  GPUForceLayout,
  applyGPUForceLayout,
  getGPUBackendInfo,
  type GPUBackend,
} from '../gpuForceLayout';

// ============================================================================
// TEST DATA GENERATORS
// ============================================================================

/**
 * Generate random graph for benchmarking
 */
function generateRandomGraph(
  nodeCount: number,
  edgeDensity = 0.01,
): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = Array.from({ length: nodeCount }, (_, i) => ({
    id: `node-${i}`,
    type: 'default',
    position: { x: 0, y: 0 },
    data: { label: `Node ${i}` },
  }));

  const edges: Edge[] = [];
  const maxEdges = Math.floor((nodeCount * (nodeCount - 1)) / 2);
  const edgeCount = Math.floor(maxEdges * edgeDensity);

  for (let i = 0; i < edgeCount; i++) {
    const source = Math.floor(Math.random() * nodeCount);
    const target = Math.floor(Math.random() * nodeCount);
    if (source !== target) {
      edges.push({
        id: `edge-${i}`,
        source: `node-${source}`,
        target: `node-${target}`,
      });
    }
  }

  return { nodes, edges };
}

/**
 * Generate scale-free graph (more realistic)
 * Uses Barabási–Albert model
 */
function generateScaleFreeGraph(
  nodeCount: number,
  m = 2,
): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = Array.from({ length: nodeCount }, (_, i) => ({
    id: `node-${i}`,
    type: 'default',
    position: { x: 0, y: 0 },
    data: { label: `Node ${i}` },
  }));

  const edges: Edge[] = [];
  const degrees = new Map<string, number>();

  // Initial complete graph with m nodes
  for (let i = 0; i < m; i++) {
    degrees.set(`node-${i}`, 0);
    for (let j = i + 1; j < m; j++) {
      edges.push({
        id: `edge-${edges.length}`,
        source: `node-${i}`,
        target: `node-${j}`,
      });
      degrees.set(`node-${i}`, (degrees.get(`node-${i}`) || 0) + 1);
      degrees.set(`node-${j}`, (degrees.get(`node-${j}`) || 0) + 1);
    }
  }

  // Add nodes with preferential attachment
  for (let i = m; i < nodeCount; i++) {
    const newNodeId = `node-${i}`;
    degrees.set(newNodeId, 0);

    // Calculate total degree
    let totalDegree = 0;
    for (const deg of degrees.values()) {
      totalDegree += deg;
    }

    // Add m edges
    const targets = new Set<string>();
    while (targets.size < m) {
      const rand = Math.random() * totalDegree;
      let cumulative = 0;
      for (const [nodeId, degree] of degrees) {
        if (nodeId === newNodeId) continue;
        cumulative += degree;
        if (rand <= cumulative && !targets.has(nodeId)) {
          targets.add(nodeId);
          break;
        }
      }
    }

    // Create edges
    for (const targetId of targets) {
      edges.push({
        id: `edge-${edges.length}`,
        source: newNodeId,
        target: targetId,
      });
      degrees.set(newNodeId, (degrees.get(newNodeId) || 0) + 1);
      degrees.set(targetId, (degrees.get(targetId) || 0) + 1);
    }
  }

  return { nodes, edges };
}

// ============================================================================
// BENCHMARK HELPERS
// ============================================================================

interface BenchmarkResult {
  nodeCount: number;
  edgeCount: number;
  backend: GPUBackend;
  duration: number;
  iterationsPerSecond: number;
}

async function runBenchmark(nodeCount: number, backend?: GPUBackend): Promise<BenchmarkResult> {
  const { nodes, edges } = generateScaleFreeGraph(nodeCount);

  const layout = new GPUForceLayout(nodes, edges, {
    iterations: 100,
    forceBackend: backend,
  });

  const result = await layout.compute();

  return {
    nodeCount,
    edgeCount: edges.length,
    backend: result.backend,
    duration: result.duration,
    iterationsPerSecond: (100 / result.duration) * 1000,
  };
}

function formatBenchmarkResult(result: BenchmarkResult): string {
  return `${result.nodeCount} nodes, ${result.edgeCount} edges: ${result.duration.toFixed(2)}ms (${result.iterationsPerSecond.toFixed(2)} iter/s) [${result.backend}]`;
}

// ============================================================================
// TESTS
// ============================================================================

describe('GPU Force Layout Benchmarks', () => {
  let backendInfo: Awaited<ReturnType<typeof getGPUBackendInfo>>;

  beforeAll(async () => {
    backendInfo = await getGPUBackendInfo();
    logger.info('\n=== GPU Backend Info ===');
    logger.info(`Default backend: ${backendInfo.backend}`);
    logger.info(`WebGPU available: ${backendInfo.available.webgpu}`);
    logger.info(`WebGL available: ${backendInfo.available.webgl}`);
    logger.info(`CPU available: ${backendInfo.available.cpu}`);
    logger.info('========================\n');
  });

  describe('Backend Detection', () => {
    it('should detect available GPU backend', async () => {
      expect(backendInfo.backend).toMatch(/^(webgpu|webgl|cpu)$/);
      expect(backendInfo.available.cpu).toBe(true);
    });

    it('should provide backend info', async () => {
      const info = await getGPUBackendInfo();
      expect(info).toHaveProperty('backend');
      expect(info).toHaveProperty('available');
    });
  });

  describe('Small Graphs (1k nodes)', () => {
    it('should layout 1k nodes quickly', async () => {
      const result = await runBenchmark(1000);
      logger.info(`1k nodes: ${formatBenchmarkResult(result)}`);
      expect(result.duration).toBeLessThan(5000); // <5s
    });
  });

  describe('Medium Graphs (5k nodes)', () => {
    it('should layout 5k nodes', async () => {
      const result = await runBenchmark(5000);
      logger.info(`5k nodes: ${formatBenchmarkResult(result)}`);
      expect(result.duration).toBeLessThan(30000); // <30s
    });
  });

  describe('Large Graphs (10k nodes)', () => {
    it('should layout 10k nodes', async () => {
      const result = await runBenchmark(10000);
      logger.info(`10k nodes: ${formatBenchmarkResult(result)}`);
      expect(result.duration).toBeLessThan(60000); // <60s
    }, 120000); // 2 minute timeout
  });

  // Only run very large tests in CI or when explicitly requested
  describe.skip('Very Large Graphs (100k nodes)', () => {
    it('should layout 100k nodes in target time', async () => {
      const result = await runBenchmark(100000);
      logger.info(`100k nodes: ${formatBenchmarkResult(result)}`);
      // Target: <5s with GPU, accept <60s for CPU fallback
      const target = backendInfo.backend === 'cpu' ? 60000 : 5000;
      expect(result.duration).toBeLessThan(target);
    }, 300000); // 5 minute timeout
  });

  describe('Backend Comparison', () => {
    it('should compare CPU vs available GPU backend', async () => {
      const cpuResult = await runBenchmark(1000, 'cpu');
      logger.info(`CPU:  ${formatBenchmarkResult(cpuResult)}`);

      if (backendInfo.available.webgpu || backendInfo.available.webgl) {
        const gpuBackend = backendInfo.available.webgpu ? 'webgpu' : 'webgl';
        const gpuResult = await runBenchmark(1000, gpuBackend);
        logger.info(`GPU:  ${formatBenchmarkResult(gpuResult)}`);

        // GPU should be faster (but currently not implemented)
        // When implemented, uncomment:
        // expect(gpuResult.duration).toBeLessThan(cpuResult.duration);
      } else {
        logger.info('GPU backends not available, skipping comparison');
      }
    });
  });

  describe('API Tests', () => {
    it('should compute layout with default options', async () => {
      const { nodes, edges } = generateRandomGraph(100);
      const result = await applyGPUForceLayout(nodes, edges);
      expect(result).toHaveLength(100);
      expect(result[0]).toHaveProperty('position');
    });

    it('should call progress callback', async () => {
      const { nodes, edges } = generateRandomGraph(100);
      const progressUpdates: number[] = [];

      const layout = new GPUForceLayout(nodes, edges, {
        iterations: 50,
        onProgress: (progress) => {
          progressUpdates.push(progress);
        },
      });

      await layout.compute();
      expect(progressUpdates.length).toBeGreaterThan(0);
      expect(Math.max(...progressUpdates)).toBe(1);
    });

    it('should handle empty graph', async () => {
      const result = await applyGPUForceLayout([], []);
      expect(result).toHaveLength(0);
    });

    it('should normalize positions to positive quadrant', async () => {
      const { nodes, edges } = generateRandomGraph(50);
      const result = await applyGPUForceLayout(nodes, edges);

      for (const node of result) {
        expect(node.position.x).toBeGreaterThanOrEqual(0);
        expect(node.position.y).toBeGreaterThanOrEqual(0);
      }
    });
  });
});

// ============================================================================
// PERFORMANCE COMPARISON TABLE
// ============================================================================

describe.skip('Performance Comparison (Manual Run)', () => {
  it('should generate performance comparison table', async () => {
    logger.info('\n=== Performance Comparison Table ===\n');
    logger.info('| Nodes | CPU     | WebGL   | WebGPU  | Speedup |');
    logger.info('|-------|---------|---------|---------|---------|');

    const testSizes = [1000, 5000, 10000];

    for (const size of testSizes) {
      const cpuResult = await runBenchmark(size, 'cpu');

      let webglDuration = 'N/A';
      let webgpuDuration = 'N/A';
      let speedup = 'N/A';

      if (backendInfo.available.webgl) {
        const webglResult = await runBenchmark(size, 'webgl');
        webglDuration = `${webglResult.duration.toFixed(0)}ms`;
      }

      if (backendInfo.available.webgpu) {
        const webgpuResult = await runBenchmark(size, 'webgpu');
        webgpuDuration = `${webgpuResult.duration.toFixed(0)}ms`;
        speedup = `${(cpuResult.duration / webgpuResult.duration).toFixed(1)}x`;
      }

      logger.info(
        `| ${size.toLocaleString().padEnd(5)} | ${`${cpuResult.duration.toFixed(0)}ms`.padEnd(7)} | ${webglDuration.padEnd(7)} | ${webgpuDuration.padEnd(7)} | ${speedup.padEnd(7)} |`,
      );
    }

    logger.info('\n====================================\n');
  }, 600000); // 10 minute timeout
});
