/**
 * Graph Layout Benchmark Utilities
 *
 * Provides utilities for benchmarking graph layout performance,
 * both with and without Web Workers, to demonstrate the performance
 * improvements from off-main-thread computation.
 *
 * @module graphLayoutBenchmark
 */

import type { LayoutNode, LayoutEdge, LayoutOptions } from '@/workers/graphLayout.worker';

// ============================================================================
// TEST DATA GENERATION
// ============================================================================

/**
 * Generate synthetic graph data for benchmarking
 */
export function generateTestGraph(
  nodeCount: number,
  edgeDensity: number = 0.3,
): { nodes: LayoutNode[]; edges: LayoutEdge[] } {
  const nodes: LayoutNode[] = [];
  const edges: LayoutEdge[] = [];

  // Generate nodes
  for (let i = 0; i < nodeCount; i++) {
    nodes.push({
      id: `node-${i}`,
      width: 200,
      height: 120,
    });
  }

  // Generate edges (DAG structure with some randomness)
  const maxEdges = Math.floor(nodeCount * edgeDensity);
  let edgeCount = 0;

  for (let i = 0; i < nodeCount - 1 && edgeCount < maxEdges; i++) {
    // Connect to next level nodes (DAG)
    const targetCount = Math.min(Math.floor(Math.random() * 3) + 1, nodeCount - i - 1);

    for (let j = 0; j < targetCount && edgeCount < maxEdges; j++) {
      const targetIndex = i + Math.floor(Math.random() * (nodeCount - i - 1)) + 1;
      edges.push({
        id: `edge-${edgeCount}`,
        source: `node-${i}`,
        target: `node-${targetIndex}`,
      });
      edgeCount++;
    }
  }

  return { nodes, edges };
}

// ============================================================================
// PERFORMANCE MEASUREMENT
// ============================================================================

export interface BenchmarkResult {
  algorithm: string;
  nodeCount: number;
  edgeCount: number;
  duration: number;
  fps: number;
  mainThreadBlocked: boolean;
  memoryDelta?: number | undefined;
}

/**
 * Measure main thread responsiveness during layout computation
 */
export async function measureMainThreadResponsiveness(
  layoutFn: () => Promise<void>,
  sampleInterval: number = 16,
): Promise<{
  averageFPS: number;
  minFPS: number;
  maxFPS: number;
  blockedTime: number;
}> {
  const samples: number[] = [];
  let lastFrameTime = performance.now();
  let totalBlockedTime = 0;

  // Start frame monitoring
  const frameMonitor = setInterval(() => {
    const now = performance.now();
    const frameDuration = now - lastFrameTime;
    const fps = 1000 / frameDuration;
    samples.push(fps);

    // Count as blocked if FPS < 30
    if (fps < 30) {
      totalBlockedTime += frameDuration;
    }

    lastFrameTime = now;
  }, sampleInterval);

  // Run layout computation
  await layoutFn();

  // Stop monitoring
  clearInterval(frameMonitor);

  // Calculate statistics
  const averageFPS = samples.reduce((a, b) => a + b, 0) / samples.length;
  const minFPS = Math.min(...samples);
  const maxFPS = Math.max(...samples);

  return {
    averageFPS,
    minFPS,
    maxFPS,
    blockedTime: totalBlockedTime,
  };
}

/**
 * Benchmark layout computation with main thread monitoring
 */
export async function benchmarkLayoutWithMonitoring(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  layoutFn: (nodes: LayoutNode[], edges: LayoutEdge[]) => Promise<void>,
  algorithm: string,
): Promise<BenchmarkResult> {
  // Measure memory before
  const memoryBefore = (performance as any).memory?.usedJSHeapSize || 0;

  // Measure layout computation time
  const startTime = performance.now();

  const responsiveness = await measureMainThreadResponsiveness(async () => {
    await layoutFn(nodes, edges);
  });

  const duration = performance.now() - startTime;

  // Measure memory after
  const memoryAfter = (performance as any).memory?.usedJSHeapSize || 0;
  const memoryDelta = memoryAfter - memoryBefore;

  return {
    algorithm,
    nodeCount: nodes.length,
    edgeCount: edges.length,
    duration,
    fps: responsiveness.averageFPS,
    mainThreadBlocked: responsiveness.blockedTime > 100, // Blocked if >100ms
    memoryDelta: memoryDelta > 0 ? memoryDelta : undefined,
  };
}

// ============================================================================
// COMPARISON UTILITIES
// ============================================================================

export interface ComparisonResult {
  nodeCount: number;
  edgeCount: number;
  synchronous: BenchmarkResult;
  worker: BenchmarkResult;
  improvement: {
    durationImprovement: number; // Percentage
    fpsImprovement: number; // Percentage
    mainThreadBlockingRemoved: boolean;
  };
}

/**
 * Format benchmark results for display
 */
export function formatBenchmarkResult(result: BenchmarkResult): string {
  const lines = [
    `Algorithm: ${result.algorithm}`,
    `Nodes: ${result.nodeCount}, Edges: ${result.edgeCount}`,
    `Duration: ${result.duration.toFixed(2)}ms`,
    `Average FPS: ${result.fps.toFixed(1)}`,
    `Main Thread Blocked: ${result.mainThreadBlocked ? 'YES' : 'NO'}`,
  ];

  if (result.memoryDelta !== undefined) {
    lines.push(`Memory Delta: ${(result.memoryDelta / 1024 / 1024).toFixed(2)} MB`);
  }

  return lines.join('\n');
}

/**
 * Format comparison results for display
 */
export function formatComparisonResult(result: ComparisonResult): string {
  const lines = [
    `\n${'='.repeat(60)}`,
    `COMPARISON: ${result.nodeCount} nodes, ${result.edgeCount} edges`,
    `${'='.repeat(60)}`,
    '',
    'SYNCHRONOUS (Main Thread):',
    formatBenchmarkResult(result.synchronous),
    '',
    'WORKER (Off Main Thread):',
    formatBenchmarkResult(result.worker),
    '',
    'IMPROVEMENT:',
    `Duration: ${result.improvement.durationImprovement > 0 ? '+' : ''}${result.improvement.durationImprovement.toFixed(1)}% ${result.improvement.durationImprovement > 0 ? 'slower' : 'faster'}`,
    `FPS: ${result.improvement.fpsImprovement > 0 ? '+' : ''}${result.improvement.fpsImprovement.toFixed(1)}%`,
    `Main Thread Blocking: ${result.improvement.mainThreadBlockingRemoved ? 'REMOVED ✓' : 'Still present'}`,
    `${'='.repeat(60)}`,
  ];

  return lines.join('\n');
}

// ============================================================================
// EXPORT UTILITIES
// ============================================================================

/**
 * Export benchmark results to JSON
 */
export function exportBenchmarkResults(
  results: BenchmarkResult[],
  filename: string = 'graph-layout-benchmark.json',
): void {
  const data = {
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    results,
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Export comparison results to CSV
 */
export function exportComparisonToCSV(
  results: ComparisonResult[],
  filename: string = 'graph-layout-comparison.csv',
): void {
  const headers = [
    'Node Count',
    'Edge Count',
    'Sync Duration (ms)',
    'Worker Duration (ms)',
    'Sync FPS',
    'Worker FPS',
    'Sync Blocked',
    'Worker Blocked',
    'Duration Improvement (%)',
    'FPS Improvement (%)',
  ];

  const rows = results.map((r) => [
    r.nodeCount,
    r.edgeCount,
    r.synchronous.duration.toFixed(2),
    r.worker.duration.toFixed(2),
    r.synchronous.fps.toFixed(1),
    r.worker.fps.toFixed(1),
    r.synchronous.mainThreadBlocked ? 'YES' : 'NO',
    r.worker.mainThreadBlocked ? 'YES' : 'NO',
    r.improvement.durationImprovement.toFixed(1),
    r.improvement.fpsImprovement.toFixed(1),
  ]);

  const csv = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
