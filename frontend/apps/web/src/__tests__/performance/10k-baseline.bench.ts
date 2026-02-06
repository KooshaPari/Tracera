/**
 * 10k Node Graph Performance Baseline Benchmark
 *
 * Establishes baseline performance metrics for graph rendering at 10,000 node scale.
 * This benchmark measures current implementation performance and sets targets for future optimization.
 *
 * Test Scenarios:
 * - Load 10k nodes, 50k edges
 * - Pan across entire graph
 * - Zoom from 0.1x to 2x
 * - Node selection operations
 * - LOD transitions
 * - Memory usage tracking
 * - Edge culling performance
 *
 * Performance Targets (Phase 5-8 improvements):
 * - Initial render: < 3s (current baseline TBD)
 * - Pan FPS: > 30 FPS (target: 60 FPS by Phase 8)
 * - Zoom FPS: > 30 FPS (target: 60 FPS by Phase 8)
 * - Memory: < 500MB heap (target: < 300MB by Phase 8)
 * - Node selection: < 100ms (target: < 50ms by Phase 8)
 *
 * @module Performance/10kBaseline
 */

import type { Page } from '@playwright/test';

import { expect, test } from '@playwright/test';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';

const logger = {
  info: (msg: string) => {
    console.log(msg);
  },
};

/**
 * Performance metrics captured during benchmarking
 */
interface PerformanceMetrics {
  // Render performance
  initialRenderTime: number;
  layoutComputationTime: number;
  firstPaintTime: number;

  // Frame rates
  panFPS: number;
  zoomFPS: number;
  continuousPanFPS: number;

  // Interaction performance
  nodeSelectionTime: number;
  avgNodeSelectionTime: number;
  lodTransitionTime: number;

  // Memory metrics
  initialMemoryMB: number;
  peakMemoryMB: number;
  finalMemoryMB: number;
  heapUsagePercent: number;

  // Culling performance
  edgeCullingTimePerFrame: number;
  nodeLODComputationTime: number;
  visibleNodeCount: number;
  culledNodeCount: number;

  // Graph stats
  totalNodes: number;
  totalEdges: number;

  // Jank metrics
  jankFrameCount: number;
  jankPercentage: number;
  avgFrameTime: number;
  maxFrameTime: number;
}

/**
 * Benchmark results for comparison and reporting
 */
interface BenchmarkResults {
  timestamp: string;
  testEnvironment: {
    userAgent: string;
    viewport: { width: number; height: number };
    devicePixelRatio: number;
  };
  scenarios: {
    load10kGraph: PerformanceMetrics;
    continuousPan: PerformanceMetrics;
    zoomOperations: PerformanceMetrics;
    nodeSelection: PerformanceMetrics;
    lodTransitions: PerformanceMetrics;
  };
  summary: {
    overallScore: number;
    performanceGrade: 'A' | 'B' | 'C' | 'D' | 'F';
    readyForProduction: boolean;
    blockers: string[];
    recommendations: string[];
  };
}

/**
 * Generate mock 10k node graph data
 */
async function generate10kGraphData(page: Page): Promise<void> {
  await page.evaluate(() => {
    const nodes: any[] = [];
    const edges: any[] = [];

    const types = [
      'requirement',
      'epic',
      'user_story',
      'task',
      'bug',
      'test_case',
      'code',
      'ui_component',
    ];
    const statuses = ['todo', 'in_progress', 'done', 'blocked'];

    // Generate 10,000 nodes
    for (let i = 0; i < 10_000; i++) {
      const type = types[i % types.length];
      const status = statuses[Math.floor(Math.random() * statuses.length)];

      nodes.push({
        description: `Description for node ${i}`,
        id: `node-${i}`,
        metadata: {
          createdAt: new Date().toISOString(),
          priority: Math.floor(Math.random() * 5) + 1,
        },
        status,
        title: `Node ${i}`,
        type,
        view: type,
      });
    }

    // Generate ~50,000 edges (5 edges per node on average)
    const linkTypes = ['traces_to', 'depends_on', 'blocks', 'implements', 'tests'] as const;

    for (let i = 0; i < 50_000; i++) {
      const sourceIdx = Math.floor(Math.random() * nodes.length);
      const targetIdx = Math.floor(Math.random() * nodes.length);

      if (sourceIdx !== targetIdx) {
        edges.push({
          id: `edge-${i}`,
          sourceId: nodes[sourceIdx].id,
          targetId: nodes[targetIdx].id,
          type: linkTypes[i % linkTypes.length],
        });
      }
    }

    // Store in window for access
    (globalThis as any).__benchmarkGraphData = { edges, nodes };
  });
}

/**
 * Load graph data into the graph view
 */
async function loadGraphData(page: Page): Promise<void> {
  // Inject data into the graph component
  await page.evaluate(() => {
    const data = (globalThis as any).__benchmarkGraphData;
    const event = new CustomEvent('loadGraphData', { detail: data });
    globalThis.dispatchEvent(event);
  });
}

/**
 * Get current memory usage from browser
 */
async function getMemoryUsage(page: Page): Promise<{
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
} | null> {
  return page.evaluate(() => {
    const { memory } = performance as any;
    if (!memory) {
      return null;
    }

    return {
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
      totalJSHeapSize: memory.totalJSHeapSize,
      usedJSHeapSize: memory.usedJSHeapSize,
    };
  });
}

/**
 * Force garbage collection (Chrome only)
 */
async function forceGC(page: Page): Promise<void> {
  await page.evaluate(() => {
    if ((globalThis as any).gc) {
      (globalThis as any).gc();
    }
  });
}

/**
 * Measure frame rate during an operation
 */
async function measureFrameRate(
  page: Page,
  duration = 2000,
): Promise<{
  fps: number;
  avgFrameTime: number;
  maxFrameTime: number;
  jankFrames: number;
  jankPercentage: number;
}> {
  return page.evaluate(
    async (measureDuration) =>
      new Promise((resolve) => {
        const frameTimings: number[] = [];
        let lastFrameTime = performance.now();
        const startTime = performance.now();

        const measureFrames = () => {
          const now = performance.now();
          const frameTime = now - lastFrameTime;
          frameTimings.push(frameTime);
          lastFrameTime = now;

          if (now - startTime < measureDuration) {
            requestAnimationFrame(measureFrames);
          } else {
            const avgFrameTime = frameTimings.reduce((a, b) => a + b, 0) / frameTimings.length;
            const maxFrameTime = Math.max(...frameTimings);
            const jankFrames = frameTimings.filter((t) => t > 50).length;
            const fps = 1000 / avgFrameTime;

            resolve({
              avgFrameTime,
              fps,
              jankFrames,
              jankPercentage: (jankFrames / frameTimings.length) * 100,
              maxFrameTime,
            });
          }
        };

        requestAnimationFrame(measureFrames);
      }),
    duration,
  );
}

/**
 * Wait for graph to be fully rendered
 */
async function waitForGraphReady(page: Page): Promise<void> {
  await page.waitForSelector('.react-flow', { timeout: 30_000 });
  await page.waitForSelector('.react-flow__node', { timeout: 30_000 });
  await page.waitForTimeout(2000); // Allow for layout stabilization
}

/**
 * Get graph metrics from the page
 */
async function getGraphMetrics(page: Page): Promise<{
  nodeCount: number;
  edgeCount: number;
  visibleNodeCount: number;
  lodLevel: string;
}> {
  return page.evaluate(() => {
    const nodes = document.querySelectorAll('.react-flow__node');
    const edges = document.querySelectorAll('.react-flow__edge');

    // Try to get metrics from the performance panel if available
    const metricsPanel = document.querySelector('[data-testid="graph-metrics"]');
    let lodLevel = 'unknown';

    if (metricsPanel) {
      const lodText = metricsPanel.textContent || '';
      const lodMatch = lodText.match(/LOD:\s*(\w+)/);
      if (lodMatch) {
        lodLevel = lodMatch[1];
      }
    }

    return {
      edgeCount: edges.length,
      lodLevel,
      nodeCount: nodes.length,
      visibleNodeCount: nodes.length,
    };
  });
}

test.describe('10k Node Baseline Performance', () => {
  let benchmarkResults: BenchmarkResults;

  test.beforeAll(async () => {
    benchmarkResults = {
      scenarios: {} as any,
      summary: {
        blockers: [],
        overallScore: 0,
        performanceGrade: 'F',
        readyForProduction: false,
        recommendations: [],
      },
      testEnvironment: {
        devicePixelRatio: 1,
        userAgent: '',
        viewport: { height: 1080, width: 1920 },
      },
      timestamp: new Date().toISOString(),
    };
  });

  test.beforeEach(async ({ page }) => {
    // Enable performance memory API (Chrome)
    await page.addInitScript(() => {
      (globalThis as any).gc = (globalThis as any).gc ?? (() => {});
    });

    // Set viewport
    await page.setViewportSize({ height: 1080, width: 1920 });

    // Capture environment
    const userAgent = await page.evaluate(() => navigator.userAgent);
    const dpr = await page.evaluate(() => window.devicePixelRatio);
    benchmarkResults.testEnvironment.userAgent = userAgent;
    benchmarkResults.testEnvironment.devicePixelRatio = dpr;
  });

  test('Scenario 1: Load 10k nodes with 50k edges', async ({ page }) => {
    logger.info('📊 Scenario 1: Loading 10k node graph...');

    // Navigate to graph page
    await page.goto('/graph', { waitUntil: 'networkidle' });

    // Generate test data
    await generate10kGraphData(page);

    // Measure initial memory
    await forceGC(page);
    await page.waitForTimeout(500);
    const initialMemory = await getMemoryUsage(page);

    // Start timing
    const startTime = Date.now();
    const layoutStart = performance.now();

    // Load the graph
    await loadGraphData(page);

    // Wait for rendering
    await waitForGraphReady(page);

    const layoutEnd = performance.now();
    const totalLoadTime = Date.now() - startTime;

    // Get graph metrics
    const graphMetrics = await getGraphMetrics(page);

    // Measure final memory
    const finalMemory = await getMemoryUsage(page);

    // Measure first paint
    const firstPaintTime = await page.evaluate(() => {
      const paintEntries = performance.getEntriesByType('paint') as PerformanceEntry[];
      const fcp = paintEntries.find((e) => e.name === 'first-contentful-paint');
      return fcp ? fcp.startTime : 0;
    });

    const metrics: PerformanceMetrics = {
      avgFrameTime: 0,
      avgNodeSelectionTime: 0,
      continuousPanFPS: 0,
      culledNodeCount: 10_000 - graphMetrics.visibleNodeCount,
      edgeCullingTimePerFrame: 0,
      finalMemoryMB: finalMemory ? finalMemory.usedJSHeapSize / 1_048_576 : 0,
      firstPaintTime,
      heapUsagePercent: finalMemory
        ? (finalMemory.usedJSHeapSize / finalMemory.jsHeapSizeLimit) * 100
        : 0,
      initialMemoryMB: initialMemory ? initialMemory.usedJSHeapSize / 1_048_576 : 0,
      initialRenderTime: totalLoadTime,
      jankFrameCount: 0,
      jankPercentage: 0,
      layoutComputationTime: layoutEnd - layoutStart,
      lodTransitionTime: 0,
      maxFrameTime: 0,
      nodeLODComputationTime: 0,
      nodeSelectionTime: 0,
      panFPS: 0,
      peakMemoryMB: finalMemory ? finalMemory.usedJSHeapSize / 1_048_576 : 0,
      totalEdges: 50_000,
      totalNodes: 10_000,
      visibleNodeCount: graphMetrics.visibleNodeCount,
      zoomFPS: 0,
    };

    benchmarkResults.scenarios.load10kGraph = metrics;

    // Assertions
    logger.info(`  ✓ Initial render time: ${metrics.initialRenderTime}ms (target: <3000ms)`);
    logger.info(`  ✓ Layout computation: ${metrics.layoutComputationTime.toFixed(2)}ms`);
    logger.info(`  ✓ Memory usage: ${metrics.finalMemoryMB.toFixed(2)}MB (target: <500MB)`);
    logger.info(
      `  ✓ Visible nodes: ${metrics.visibleNodeCount} (culled: ${metrics.culledNodeCount})`,
    );

    // Target: < 3s for initial render
    expect(metrics.initialRenderTime).toBeLessThan(10_000); // Relaxed for baseline
  });

  test('Scenario 2: Continuous panning performance', async ({ page }) => {
    logger.info('📊 Scenario 2: Measuring continuous pan FPS...');

    await page.goto('/graph', { waitUntil: 'networkidle' });
    await generate10kGraphData(page);
    await loadGraphData(page);
    await waitForGraphReady(page);

    const graphPane = page.locator('.react-flow__pane');

    // Start frame rate measurement
    const metricsPromise = measureFrameRate(page, 3000);

    // Perform continuous panning
    await graphPane.hover();
    await page.mouse.down();

    // Pan in a large circular pattern
    const centerX = 960;
    const centerY = 540;
    const radius = 300;

    for (let angle = 0; angle < 720; angle += 10) {
      const rad = (angle * Math.PI) / 180;
      const x = centerX + radius * Math.cos(rad);
      const y = centerY + radius * Math.sin(rad);
      await page.mouse.move(x, y, { steps: 2 });
    }

    await page.mouse.up();

    const frameMetrics = await metricsPromise;

    const metrics: PerformanceMetrics = {
      ...benchmarkResults.scenarios.load10kGraph,
      continuousPanFPS: frameMetrics.fps,
      avgFrameTime: frameMetrics.avgFrameTime,
      maxFrameTime: frameMetrics.maxFrameTime,
      jankFrameCount: frameMetrics.jankFrames,
      jankPercentage: frameMetrics.jankPercentage,
    };

    benchmarkResults.scenarios.continuousPan = metrics;

    logger.info(`  ✓ Pan FPS: ${frameMetrics.fps.toFixed(2)} (target: >30fps)`);
    logger.info(`  ✓ Avg frame time: ${frameMetrics.avgFrameTime.toFixed(2)}ms`);
    logger.info(`  ✓ Jank percentage: ${frameMetrics.jankPercentage.toFixed(2)}%`);

    // Target: > 30 FPS during panning
    expect(frameMetrics.fps).toBeGreaterThan(20); // Relaxed for baseline
  });

  test('Scenario 3: Zoom performance (0.1x to 2x)', async ({ page }) => {
    logger.info('📊 Scenario 3: Measuring zoom performance...');

    await page.goto('/graph', { waitUntil: 'networkidle' });
    await generate10kGraphData(page);
    await loadGraphData(page);
    await waitForGraphReady(page);

    const graphPane = page.locator('.react-flow__pane');
    await graphPane.hover({ position: { x: 960, y: 540 } });

    // Start frame rate measurement
    const metricsPromise = measureFrameRate(page, 3000);

    // Zoom out to 0.1x
    for (let i = 0; i < 15; i++) {
      await page.mouse.wheel(0, 200);
      await page.waitForTimeout(100);
    }

    // Zoom in to 2x
    for (let i = 0; i < 30; i++) {
      await page.mouse.wheel(0, -200);
      await page.waitForTimeout(100);
    }

    // Back to 1x
    for (let i = 0; i < 15; i++) {
      await page.mouse.wheel(0, 100);
      await page.waitForTimeout(100);
    }

    const frameMetrics = await metricsPromise;

    const metrics: PerformanceMetrics = {
      ...benchmarkResults.scenarios.load10kGraph,
      zoomFPS: frameMetrics.fps,
      avgFrameTime: frameMetrics.avgFrameTime,
      maxFrameTime: frameMetrics.maxFrameTime,
      jankFrameCount: frameMetrics.jankFrames,
      jankPercentage: frameMetrics.jankPercentage,
    };

    benchmarkResults.scenarios.zoomOperations = metrics;

    logger.info(`  ✓ Zoom FPS: ${frameMetrics.fps.toFixed(2)} (target: >30fps)`);
    logger.info(`  ✓ Avg frame time: ${frameMetrics.avgFrameTime.toFixed(2)}ms`);

    expect(frameMetrics.fps).toBeGreaterThan(20); // Relaxed for baseline
  });

  test('Scenario 4: Node selection performance', async ({ page }) => {
    logger.info('📊 Scenario 4: Measuring node selection time...');

    await page.goto('/graph', { waitUntil: 'networkidle' });
    await generate10kGraphData(page);
    await loadGraphData(page);
    await waitForGraphReady(page);

    const nodes = page.locator('.react-flow__node');
    const nodeCount = await nodes.count();

    const selectionTimes: number[] = [];
    const testCount = Math.min(20, nodeCount);

    for (let i = 0; i < testCount; i++) {
      const startTime = performance.now();

      await nodes.nth(i).click();

      await page.evaluate(
        async () =>
          new Promise((resolve) => {
            requestAnimationFrame(() => {
              requestAnimationFrame(resolve);
            });
          }),
      );

      const endTime = performance.now();
      selectionTimes.push(endTime - startTime);
    }

    const avgSelectionTime = selectionTimes.reduce((a, b) => a + b, 0) / selectionTimes.length;
    const maxSelectionTime = Math.max(...selectionTimes);

    const metrics: PerformanceMetrics = {
      ...benchmarkResults.scenarios.load10kGraph,
      nodeSelectionTime: maxSelectionTime,
      avgNodeSelectionTime: avgSelectionTime,
    };

    benchmarkResults.scenarios.nodeSelection = metrics;

    logger.info(`  ✓ Avg selection time: ${avgSelectionTime.toFixed(2)}ms (target: <100ms)`);
    logger.info(`  ✓ Max selection time: ${maxSelectionTime.toFixed(2)}ms`);

    expect(avgSelectionTime).toBeLessThan(200); // Relaxed for baseline
  });

  test('Scenario 5: LOD transition performance', async ({ page }) => {
    logger.info('📊 Scenario 5: Measuring LOD transitions...');

    await page.goto('/graph', { waitUntil: 'networkidle' });
    await generate10kGraphData(page);
    await loadGraphData(page);
    await waitForGraphReady(page);

    const graphPane = page.locator('.react-flow__pane');
    await graphPane.hover({ position: { x: 960, y: 540 } });

    // Measure LOD transition times
    const transitionTimes: number[] = [];

    // Zoom out to trigger LOD changes
    for (let i = 0; i < 5; i++) {
      const startTime = performance.now();

      await page.mouse.wheel(0, 300);
      await page.waitForTimeout(150);

      await page.evaluate(
        async () =>
          new Promise((resolve) => {
            requestAnimationFrame(() => {
              requestAnimationFrame(resolve);
            });
          }),
      );

      const endTime = performance.now();
      transitionTimes.push(endTime - startTime);
    }

    const avgTransitionTime = transitionTimes.reduce((a, b) => a + b, 0) / transitionTimes.length;

    const metrics: PerformanceMetrics = {
      ...benchmarkResults.scenarios.load10kGraph,
      lodTransitionTime: avgTransitionTime,
    };

    benchmarkResults.scenarios.lodTransitions = metrics;

    logger.info(`  ✓ Avg LOD transition: ${avgTransitionTime.toFixed(2)}ms (target: <100ms)`);

    expect(avgTransitionTime).toBeLessThan(300); // Relaxed for baseline
  });

  test.afterAll(async () => {
    // Calculate overall performance score
    const { scenarios } = benchmarkResults;

    // Scoring weights
    const scores = {
      load: scenarios.load10kGraph.initialRenderTime < 3000 ? 20 : 0,
      lod: scenarios.lodTransitions.lodTransitionTime < 100 ? 20 : 0,
      pan: scenarios.continuousPan.continuousPanFPS > 30 ? 20 : 0,
      selection: scenarios.nodeSelection.avgNodeSelectionTime < 100 ? 20 : 0,
      zoom: scenarios.zoomOperations.zoomFPS > 30 ? 20 : 0,
    };

    const overallScore = Object.values(scores).reduce((a, b) => a + b, 0);
    benchmarkResults.summary.overallScore = overallScore;

    // Determine grade
    if (overallScore >= 90) {
      benchmarkResults.summary.performanceGrade = 'A';
    } else if (overallScore >= 70) {
      benchmarkResults.summary.performanceGrade = 'B';
    } else if (overallScore >= 50) {
      benchmarkResults.summary.performanceGrade = 'C';
    } else if (overallScore >= 30) {
      benchmarkResults.summary.performanceGrade = 'D';
    } else {
      benchmarkResults.summary.performanceGrade = 'F';
    }

    // Blockers
    if (scenarios.load10kGraph.initialRenderTime > 10_000) {
      benchmarkResults.summary.blockers.push('Initial render time exceeds 10 seconds');
    }
    if (scenarios.continuousPan.continuousPanFPS < 15) {
      benchmarkResults.summary.blockers.push('Pan FPS below 15fps');
    }
    if (scenarios.load10kGraph.finalMemoryMB > 1000) {
      benchmarkResults.summary.blockers.push('Memory usage exceeds 1GB');
    }

    // Recommendations
    if (scenarios.continuousPan.continuousPanFPS < 30) {
      benchmarkResults.summary.recommendations.push('Optimize viewport culling and edge rendering');
    }
    if (scenarios.nodeSelection.avgNodeSelectionTime > 100) {
      benchmarkResults.summary.recommendations.push(
        'Improve node selection response time with better event handling',
      );
    }
    if (scenarios.load10kGraph.culledNodeCount < 8000) {
      benchmarkResults.summary.recommendations.push('Increase viewport culling aggressiveness');
    }

    benchmarkResults.summary.readyForProduction =
      benchmarkResults.summary.blockers.length === 0 && overallScore >= 70;

    // Save results to file
    const resultsDir = path.join(__dirname, '../../..', 'performance-results');
    await fs.mkdir(resultsDir, { recursive: true });

    const resultsFile = path.join(resultsDir, `10k-baseline-${Date.now()}.json`);
    await fs.writeFile(resultsFile, JSON.stringify(benchmarkResults, null, 2));

    logger.info('\n' + '='.repeat(80));
    logger.info('📊 10K NODE BASELINE BENCHMARK RESULTS');
    logger.info('='.repeat(80));
    logger.info(
      `Overall Score: ${overallScore}/100 (Grade: ${benchmarkResults.summary.performanceGrade})`,
    );
    logger.info(
      `Production Ready: ${benchmarkResults.summary.readyForProduction ? '✅ YES' : '❌ NO'}`,
    );
    logger.info('\nScenario Results:');
    logger.info(`  Load Time: ${scenarios.load10kGraph.initialRenderTime}ms (target: <3000ms)`);
    logger.info(
      `  Pan FPS: ${scenarios.continuousPan.continuousPanFPS.toFixed(2)} (target: >30fps)`,
    );
    logger.info(`  Zoom FPS: ${scenarios.zoomOperations.zoomFPS.toFixed(2)} (target: >30fps)`);
    logger.info(
      `  Selection: ${scenarios.nodeSelection.avgNodeSelectionTime.toFixed(2)}ms (target: <100ms)`,
    );
    logger.info(
      `  LOD Transition: ${scenarios.lodTransitions.lodTransitionTime.toFixed(2)}ms (target: <100ms)`,
    );
    logger.info(`  Memory: ${scenarios.load10kGraph.finalMemoryMB.toFixed(2)}MB (target: <500MB)`);

    if (benchmarkResults.summary.blockers.length > 0) {
      logger.info('\n⚠️  Blockers:');
      benchmarkResults.summary.blockers.forEach((b) => {
        logger.info(`    - ${b}`);
      });
    }

    if (benchmarkResults.summary.recommendations.length > 0) {
      logger.info('\n💡 Recommendations:');
      benchmarkResults.summary.recommendations.forEach((r) => {
        logger.info(`    - ${r}`);
      });
    }

    logger.info(`\n📄 Results saved to: ${resultsFile}`);
    logger.info('='.repeat(80) + '\n');
  });
});
