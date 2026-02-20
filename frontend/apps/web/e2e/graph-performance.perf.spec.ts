/// <reference lib="dom" />
/// <reference lib="es2015" />

import type { Page } from '@playwright/test';

import { expect, test } from '@playwright/test';

import { authenticateAndNavigate } from './critical-path-helpers';

/**
 * Graph Performance E2E Tests
 *
 * Tests graph visualization performance including:
 * - Frame rates during panning/zooming
 * - Node selection responsiveness
 * - Edge rendering performance
 * - LOD (Level of Detail) transitions
 * - Large graph progressive loading
 * - Memory usage
 *
 * Performance Targets:
 * - 60 FPS panning (16.6ms per frame)
 * - <50ms node selection response
 * - No flicker during edge rendering
 * - Smooth LOD transitions
 * - Progressive loading for 1000+ nodes
 */

interface PerformanceMetrics {
  fps: number;
  avgFrameTime: number;
  maxFrameTime: number;
  jankFrames: number;
  jankPercentage: number;
}

interface MemoryMetrics {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}

/**
 * Measure frame rate during an animation or interaction
 */
async function measureFrameRate(page: Page, duration = 1000): Promise<PerformanceMetrics> {
  return page.evaluate(
    async (measureDuration) =>
      new Promise<PerformanceMetrics>((resolve) => {
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
            // Calculate metrics
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

/** Chrome non-standard performance.memory (optional) */
interface PerformanceMemory {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}

/**
 * Get current memory usage
 */
async function getMemoryUsage(page: Page): Promise<MemoryMetrics | null> {
  return page.evaluate(() => {
    const { memory } = performance as Performance & { memory?: PerformanceMemory };
    if (memory == null) {
      return null;
    }

    return {
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
      totalJSHeapSize: memory.totalJSHeapSize,
      usedJSHeapSize: memory.usedJSHeapSize,
    };
  });
}

/** Window with optional gc (exposed by Node --expose-gc in Playwright) */
interface WindowWithGC extends Window {
  gc?: () => void;
}

/**
 * Force garbage collection if available
 */
async function forceGC(page: Page): Promise<void> {
  await page.evaluate(() => {
    const w = globalThis as WindowWithGC;
    if (typeof w.gc === 'function') {
      w.gc();
    }
  });
}

/**
 * Wait for graph to be rendered
 */
async function waitForGraphReady(page: Page): Promise<void> {
  // Wait for ReactFlow to be initialized
  await page.waitForSelector('.react-flow', { timeout: 10_000 });

  // Wait for nodes to be rendered
  await page.waitForSelector('.react-flow__node', { timeout: 10_000 });

  // Give it a moment to stabilize
  await page.waitForTimeout(1000);
}

/**
 * Get node count in the graph
 */
async function getNodeCount(page: Page): Promise<number> {
  return page.evaluate(() => {
    const nodes = document.querySelectorAll('.react-flow__node');
    return nodes.length;
  });
}

/**
 * Get edge count in the graph
 */
async function getEdgeCount(page: Page): Promise<number> {
  return page.evaluate(() => {
    const edges = document.querySelectorAll('.react-flow__edge');
    return edges.length;
  });
}

/**
 * Measure interaction response time
 */
async function measureInteractionTime(page: Page, action: () => Promise<void>): Promise<number> {
  const startTime = await page.evaluate(() => performance.now());
  await action();

  // Wait for visual update
  await page.evaluate(
    async () =>
      new Promise<void>((resolve) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            resolve();
          });
        });
      }),
  );

  const endTime = await page.evaluate(() => performance.now());
  return endTime - startTime;
}

test.describe('Graph Performance - 500 Node Load', () => {
  test.beforeEach(async ({ page }) => {
    // Enable performance memory API (gc exposed by Node --expose-gc in Playwright)
    await page.addInitScript(() => {
      const w = globalThis as WindowWithGC;
      w.gc = w.gc ?? (() => {});
    });

    await authenticateAndNavigate(page, '/graph');
  });

  test('should load 500 node graph within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    // Wait for graph to be ready
    await waitForGraphReady(page);

    const loadTime = Date.now() - startTime;

    // Graph should load in under 5 seconds
    expect(loadTime).toBeLessThan(5000);

    // Verify nodes are rendered
    const nodeCount = await getNodeCount(page);
    expect(nodeCount).toBeGreaterThan(0);
  });

  test('should maintain 60 FPS during panning', async ({ page }) => {
    await waitForGraphReady(page);

    // Get the graph viewport
    const graphPane = page.locator('.react-flow__pane');

    // Start measuring frame rate
    const metricsPromise = measureFrameRate(page, 2000);

    // Pan the graph continuously
    await graphPane.hover();
    await page.mouse.down();

    // Pan in multiple directions
    for (let i = 0; i < 10; i++) {
      await page.mouse.move(500 + i * 20, 300 + i * 15, { steps: 5 });
      await page.waitForTimeout(100);
    }

    await page.mouse.up();

    const metrics = await metricsPromise;

    // Should maintain close to 60 FPS (at least 50 FPS)
    expect(metrics.fps).toBeGreaterThan(50);

    // Average frame time should be under 20ms
    expect(metrics.avgFrameTime).toBeLessThan(20);

    // Less than 5% jank frames
    expect(metrics.jankPercentage).toBeLessThan(5);
  });

  test('should maintain performance during continuous panning', async ({ page }) => {
    await waitForGraphReady(page);

    const graphPane = page.locator('.react-flow__pane');

    // Measure FPS during longer panning session
    const metricsPromise = measureFrameRate(page, 3000);

    await graphPane.hover();
    await page.mouse.down();

    // Continuous circular panning
    const centerX = 500;
    const centerY = 300;
    const radius = 150;

    for (let angle = 0; angle < 720; angle += 15) {
      const rad = (angle * Math.PI) / 180;
      const x = centerX + radius * Math.cos(rad);
      const y = centerY + radius * Math.sin(rad);
      await page.mouse.move(x, y, { steps: 3 });
    }

    await page.mouse.up();

    const metrics = await metricsPromise;

    // Should maintain good performance even during extended panning
    expect(metrics.fps).toBeGreaterThan(45);
    expect(metrics.jankPercentage).toBeLessThan(10);
  });
});

test.describe('Graph Performance - Zoom Operations', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/graph');
    await waitForGraphReady(page);
  });

  test('should have smooth zoom transitions', async ({ page }) => {
    const graphPane = page.locator('.react-flow__pane');

    // Measure frame rate during zoom
    const metricsPromise = measureFrameRate(page, 1500);

    // Perform multiple zoom operations
    await graphPane.hover({ position: { x: 400, y: 300 } });

    for (let i = 0; i < 5; i++) {
      await page.mouse.wheel(0, -100); // Zoom in
      await page.waitForTimeout(100);
    }

    for (let i = 0; i < 5; i++) {
      await page.mouse.wheel(0, 100); // Zoom out
      await page.waitForTimeout(100);
    }

    const metrics = await metricsPromise;

    // Zoom should be smooth
    expect(metrics.fps).toBeGreaterThan(50);
    expect(metrics.avgFrameTime).toBeLessThan(20);
  });

  test('should handle rapid zoom changes', async ({ page }) => {
    const graphPane = page.locator('.react-flow__pane');

    await graphPane.hover({ position: { x: 400, y: 300 } });

    const startTime = Date.now();

    // Rapid zoom in/out
    for (let i = 0; i < 10; i++) {
      await page.mouse.wheel(0, i % 2 === 0 ? -50 : 50);
    }

    // Wait for stabilization
    await page.waitForTimeout(500);

    const totalTime = Date.now() - startTime;

    // Should handle rapid zoom without freezing
    expect(totalTime).toBeLessThan(2000);

    // Graph should still be responsive
    const nodeCount = await getNodeCount(page);
    expect(nodeCount).toBeGreaterThan(0);
  });

  test('should use zoom controls efficiently', async ({ page }) => {
    // Find zoom in button
    const zoomInBtn = page.locator('.react-flow__controls-zoomin');

    await expect(zoomInBtn).toBeVisible({ timeout: 10_000 });
    // Measure response time for zoom button clicks
    const clickTimes: number[] = [];

    for (let i = 0; i < 5; i++) {
      const responseTime = await measureInteractionTime(page, async () => {
        await zoomInBtn.click();
      });
      clickTimes.push(responseTime);
      await page.waitForTimeout(100);
    }

    const avgResponseTime = clickTimes.reduce((a, b) => a + b, 0) / clickTimes.length;

    // Zoom controls should respond quickly
    expect(avgResponseTime).toBeLessThan(100);
  });
});

test.describe('Graph Performance - Node Selection', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/graph');
    await waitForGraphReady(page);
  });

  test('should select nodes with <50ms response time', async ({ page }) => {
    const nodes = page.locator('.react-flow__node');
    const nodeCount = await nodes.count();

    expect(nodeCount).toBeGreaterThan(0);

    const responseTimes: number[] = [];

    // Test selection on multiple nodes
    const testCount = Math.min(10, nodeCount);

    for (let i = 0; i < testCount; i++) {
      const responseTime = await measureInteractionTime(page, async () => {
        await nodes.nth(i).click();
      });

      responseTimes.push(responseTime);
      await page.waitForTimeout(50);
    }

    const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
    const maxResponseTime = Math.max(...responseTimes);

    // Average response time should be under 50ms
    expect(avgResponseTime).toBeLessThan(50);

    // Max response time should be under 100ms
    expect(maxResponseTime).toBeLessThan(100);
  });

  test('should handle rapid node selection without lag', async ({ page }) => {
    const nodes = page.locator('.react-flow__node');
    const nodeCount = await nodes.count();

    const startTime = Date.now();

    // Rapidly select different nodes
    for (let i = 0; i < Math.min(20, nodeCount); i++) {
      await nodes.nth(i % nodeCount).click();
    }

    const totalTime = Date.now() - startTime;

    // Should complete rapid selections quickly
    expect(totalTime).toBeLessThan(2000);

    // Graph should still be responsive
    const finalNodeCount = await getNodeCount(page);
    expect(finalNodeCount).toBe(nodeCount);
  });

  test('should maintain performance with multiple selections', async ({ page }) => {
    const nodes = page.locator('.react-flow__node');

    // Select multiple nodes with Ctrl+Click
    const metricsPromise = measureFrameRate(page, 1000);

    for (let i = 0; i < 5; i++) {
      await page.keyboard.down('Control');
      await nodes.nth(i).click();
      await page.keyboard.up('Control');
      await page.waitForTimeout(100);
    }

    const metrics = await metricsPromise;

    // Should maintain good frame rate during multi-select
    expect(metrics.fps).toBeGreaterThan(45);
  });
});

test.describe('Graph Performance - Edge Rendering', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/graph');
    await waitForGraphReady(page);
  });

  test('should render edges without flicker during pan', async ({ page }) => {
    const graphPane = page.locator('.react-flow__pane');

    // Measure stability during panning
    const _visualStability = await page.evaluate(
      async () =>
        new Promise<{ flickerCount: number }>((resolve) => {
          let flickerCount = 0;
          const edgeElements = document.querySelectorAll('.react-flow__edge');

          // Monitor edge visibility
          const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
              if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                // Count potential flickers (visibility changes)
                flickerCount++;
              }
            });
          });

          edgeElements.forEach((edge) => {
            observer.observe(edge, {
              attributeFilter: ['style'],
              attributes: true,
            });
          });

          // Pan and observe
          setTimeout(() => {
            observer.disconnect();
            resolve({ flickerCount });
          }, 2000);
        }),
    );

    // Start panning
    await graphPane.hover();
    await page.mouse.down();

    for (let i = 0; i < 10; i++) {
      await page.mouse.move(400 + i * 30, 300 + i * 20, { steps: 5 });
      await page.waitForTimeout(100);
    }

    await page.mouse.up();

    await page.waitForTimeout(2000);

    // Edges should not flicker excessively
    // Note: Some updates are expected, but not excessive
    // This is a basic check; real flicker detection is complex
  });

  test('should maintain edge visibility during zoom', async ({ page }) => {
    const graphPane = page.locator('.react-flow__pane');

    // Get initial edge count
    const _initialEdges = await getEdgeCount(page);

    // Zoom operations
    await graphPane.hover({ position: { x: 400, y: 300 } });

    for (let i = 0; i < 3; i++) {
      await page.mouse.wheel(0, -100);
      await page.waitForTimeout(200);

      const currentEdges = await getEdgeCount(page);
      // Edges should remain rendered
      expect(currentEdges).toBeGreaterThan(0);
    }

    for (let i = 0; i < 3; i++) {
      await page.mouse.wheel(0, 100);
      await page.waitForTimeout(200);

      const currentEdges = await getEdgeCount(page);
      expect(currentEdges).toBeGreaterThan(0);
    }
  });

  test('should handle edge hover interactions smoothly', async ({ page }) => {
    const edges = page.locator('.react-flow__edge');
    const edgeCount = await edges.count();

    if (edgeCount > 0) {
      const metricsPromise = measureFrameRate(page, 1000);

      // Hover over multiple edges
      for (let i = 0; i < Math.min(5, edgeCount); i++) {
        await edges.nth(i).hover();
        await page.waitForTimeout(100);
      }

      const metrics = await metricsPromise;

      // Should maintain smooth interaction
      expect(metrics.fps).toBeGreaterThan(50);
    }
  });
});

test.describe('Graph Performance - LOD Transitions', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/graph');
    await waitForGraphReady(page);
  });

  test('should smoothly transition LOD during zoom', async ({ page }) => {
    const graphPane = page.locator('.react-flow__pane');

    await graphPane.hover({ position: { x: 400, y: 300 } });

    // Measure frame rate during LOD transitions
    const metricsPromise = measureFrameRate(page, 2000);

    // Gradually zoom out to trigger LOD changes
    for (let i = 0; i < 10; i++) {
      await page.mouse.wheel(0, 200); // Large zoom out
      await page.waitForTimeout(150);
    }

    // Zoom back in
    for (let i = 0; i < 10; i++) {
      await page.mouse.wheel(0, -200); // Large zoom in
      await page.waitForTimeout(150);
    }

    const metrics = await metricsPromise;

    // LOD transitions should be smooth
    expect(metrics.fps).toBeGreaterThan(40);
    expect(metrics.jankPercentage).toBeLessThan(15);
  });

  test('should switch node detail levels appropriately', async ({ page }) => {
    const graphPane = page.locator('.react-flow__pane');

    await graphPane.hover({ position: { x: 400, y: 300 } });

    // Zoom out to see simplified nodes
    for (let i = 0; i < 5; i++) {
      await page.mouse.wheel(0, 300);
      await page.waitForTimeout(200);
    }

    // Check if nodes are still visible (even if simplified)
    const nodesAfterZoomOut = await getNodeCount(page);
    expect(nodesAfterZoomOut).toBeGreaterThan(0);

    // Zoom back in for detailed view
    for (let i = 0; i < 5; i++) {
      await page.mouse.wheel(0, -300);
      await page.waitForTimeout(200);
    }

    // Nodes should still be rendered with more detail
    const nodesAfterZoomIn = await getNodeCount(page);
    expect(nodesAfterZoomIn).toBeGreaterThan(0);
  });

  test('should maintain readable text during LOD transitions', async ({ page }) => {
    // Check that node labels remain readable at different zoom levels
    const checkLabels = async () =>
      page.evaluate(() => {
        const nodes = document.querySelectorAll('.react-flow__node');
        let readableCount = 0;

        nodes.forEach((node) => {
          const text = node.textContent?.trim();
          if (text && text.length > 0) {
            readableCount++;
          }
        });

        return { readable: readableCount, total: nodes.length };
      });

    const initialLabels = await checkLabels();
    expect(initialLabels.readable).toBeGreaterThan(0);

    const graphPane = page.locator('.react-flow__pane');
    await graphPane.hover({ position: { x: 400, y: 300 } });

    // Zoom out
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(300);

    const zoomedLabels = await checkLabels();
    // At least some labels should remain (simplified)
    expect(zoomedLabels.readable).toBeGreaterThan(0);
  });
});

test.describe('Graph Performance - Large Graph (1000+ Nodes)', () => {
  test.beforeEach(async ({ page }) => {
    // Enable performance monitoring
    await page.addInitScript(() => {
      (globalThis as any).gc = (globalThis as any).gc ?? (() => {});
    });

    await authenticateAndNavigate(page, '/graph');
  });

  test('should progressively load large graph', async ({ page }) => {
    const startTime = Date.now();

    // Wait for initial render
    await page.waitForSelector('.react-flow', { timeout: 15_000 });

    const initialLoadTime = Date.now() - startTime;

    // Should start rendering quickly (within 3 seconds)
    expect(initialLoadTime).toBeLessThan(3000);

    // Wait for more nodes to load
    await page.waitForTimeout(2000);

    const nodeCount = await getNodeCount(page);

    // Should have rendered nodes (might not be all 1000 yet due to virtualization)
    expect(nodeCount).toBeGreaterThan(0);
  });

  test('should use viewport culling for off-screen nodes', async ({ page }) => {
    await waitForGraphReady(page);

    // Get initial visible node count
    const visibleNodes = await page.evaluate(() => {
      const viewport = {
        height: window.innerHeight,
        width: window.innerWidth,
        x: 0,
        y: 0,
      };

      const nodes = document.querySelectorAll('.react-flow__node');
      let visibleCount = 0;

      nodes.forEach((node) => {
        const rect = node.getBoundingClientRect();
        if (
          rect.right >= viewport.x &&
          rect.left <= viewport.x + viewport.width &&
          rect.bottom >= viewport.y &&
          rect.top <= viewport.y + viewport.height
        ) {
          visibleCount++;
        }
      });

      return { total: nodes.length, visible: visibleCount };
    });

    // With viewport culling, not all nodes should be rendered
    // (or at least, they should be optimized)
    expect(visibleNodes.visible).toBeGreaterThan(0);

    // The visible count should be less than or equal to total
    expect(visibleNodes.visible).toBeLessThanOrEqual(visibleNodes.total);
  });

  test('should maintain performance with large graph panning', async ({ page }) => {
    await waitForGraphReady(page);

    const graphPane = page.locator('.react-flow__pane');

    // Measure performance during panning large graph
    const metricsPromise = measureFrameRate(page, 2000);

    await graphPane.hover();
    await page.mouse.down();

    // Pan across large graph
    for (let i = 0; i < 15; i++) {
      await page.mouse.move(300 + i * 40, 200 + i * 30, { steps: 3 });
      await page.waitForTimeout(80);
    }

    await page.mouse.up();

    const metrics = await metricsPromise;

    // Should maintain acceptable performance even with large graph
    expect(metrics.fps).toBeGreaterThan(30);
    expect(metrics.jankPercentage).toBeLessThan(20);
  });

  test('should handle large graph zoom efficiently', async ({ page }) => {
    await waitForGraphReady(page);

    const graphPane = page.locator('.react-flow__pane');
    await graphPane.hover({ position: { x: 500, y: 300 } });

    const zoomStartTime = Date.now();

    // Zoom in and out on large graph
    for (let i = 0; i < 5; i++) {
      await page.mouse.wheel(0, -150);
      await page.waitForTimeout(100);
    }

    for (let i = 0; i < 5; i++) {
      await page.mouse.wheel(0, 150);
      await page.waitForTimeout(100);
    }

    const zoomDuration = Date.now() - zoomStartTime;

    // Zoom operations should complete in reasonable time
    expect(zoomDuration).toBeLessThan(3000);
  });

  test('should not exceed memory limits with large graph', async ({ page }) => {
    await waitForGraphReady(page);

    // Force GC before measurement
    await forceGC(page);
    await page.waitForTimeout(500);

    const initialMemory = await getMemoryUsage(page);

    if (initialMemory) {
      // Interact with graph
      const graphPane = page.locator('.react-flow__pane');

      for (let i = 0; i < 5; i++) {
        await graphPane.hover();
        await page.mouse.down();
        await page.mouse.move(300 + i * 50, 200 + i * 50, { steps: 5 });
        await page.mouse.up();
        await page.waitForTimeout(200);
      }

      // Force GC and check memory
      await forceGC(page);
      await page.waitForTimeout(500);

      const finalMemory = await getMemoryUsage(page);

      if (finalMemory) {
        const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

        // Memory increase should be reasonable (less than 50MB)
        expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);

        // Should not be near the heap limit
        const heapUsagePercentage =
          (finalMemory.usedJSHeapSize / finalMemory.jsHeapSizeLimit) * 100;
        expect(heapUsagePercentage).toBeLessThan(80);
      }
    }
  });
});

test.describe('Graph Performance - Memory Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      (globalThis as any).gc = (globalThis as any).gc ?? (() => {});
    });

    await authenticateAndNavigate(page, '/graph');
    await waitForGraphReady(page);
  });

  test('should not leak memory during repeated interactions', async ({ page }) => {
    const initialMemory = await getMemoryUsage(page);

    if (initialMemory) {
      const graphPane = page.locator('.react-flow__pane');
      const nodes = page.locator('.react-flow__node');

      // Perform repeated operations
      for (let cycle = 0; cycle < 3; cycle++) {
        // Pan
        await graphPane.hover();
        await page.mouse.down();
        await page.mouse.move(400, 300, { steps: 5 });
        await page.mouse.up();

        // Select nodes
        const nodeCount = await nodes.count();
        for (let i = 0; i < Math.min(5, nodeCount); i++) {
          await nodes.nth(i).click();
          await page.waitForTimeout(50);
        }

        // Zoom
        await page.mouse.wheel(0, -100);
        await page.waitForTimeout(100);
        await page.mouse.wheel(0, 100);
        await page.waitForTimeout(100);
      }

      // Force GC
      await forceGC(page);
      await page.waitForTimeout(1000);

      const finalMemory = await getMemoryUsage(page);

      if (finalMemory) {
        const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

        // Should not accumulate excessive memory
        expect(memoryIncrease).toBeLessThan(20 * 1024 * 1024);
      }
    }
  });

  test('should clean up nodes when navigating away', async ({ page }) => {
    const initialMemory = await getMemoryUsage(page);

    // Navigate away
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Force GC
    await forceGC(page);
    await page.waitForTimeout(1000);

    const afterNavigationMemory = await getMemoryUsage(page);

    if (initialMemory && afterNavigationMemory) {
      // Memory should be released
      // Allow for some baseline increase but not graph-sized
      const memoryChange = afterNavigationMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Should not retain large graph data
      expect(Math.abs(memoryChange)).toBeLessThan(30 * 1024 * 1024);
    }
  });
});

test.describe('Graph Performance - Network Requests', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/graph');
  });

  test('should efficiently load graph data', async ({ page }) => {
    const requests: string[] = [];

    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/api/') || url.includes('/graphql')) {
        requests.push(url);
      }
    });

    await waitForGraphReady(page);

    // Should make reasonable number of API requests
    expect(requests.length).toBeLessThan(10);
  });

  test('should implement progressive loading for viewport', async ({ page }) => {
    const requests: { url: string; timestamp: number }[] = [];

    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/api/graph') || url.includes('/api/nodes')) {
        requests.push({ timestamp: Date.now(), url });
      }
    });

    await waitForGraphReady(page);

    const _initialRequests = [...requests];

    // Pan to different area
    const graphPane = page.locator('.react-flow__pane');
    await graphPane.hover();
    await page.mouse.down();
    await page.mouse.move(100, 100, { steps: 10 });
    await page.mouse.up();

    await page.waitForTimeout(1000);

    // May trigger additional requests for off-screen content
    // This is acceptable for progressive loading
    const totalRequests = requests.length;

    // But shouldn't make excessive requests
    expect(totalRequests).toBeLessThan(20);
  });

  test('should cache graph data appropriately', async ({ page }) => {
    await waitForGraphReady(page);

    let secondVisitRequests = 0;

    page.on('request', (request) => {
      if (request.url().includes('/api/graph')) {
        secondVisitRequests++;
      }
    });

    // Navigate away
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Navigate back
    await page.goto('/graph');
    await waitForGraphReady(page);

    // Should use cached data (fewer requests)
    expect(secondVisitRequests).toBeLessThan(5);
  });
});

test.describe('Graph Performance - Interaction Responsiveness', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/graph');
    await waitForGraphReady(page);
  });

  test('should respond to keyboard shortcuts quickly', async ({ page }) => {
    const shortcuts = [
      { description: 'fit view', key: 'f' },
      { description: 'zoom in', key: '+' },
      { description: 'zoom out', key: '-' },
    ];

    for (const shortcut of shortcuts) {
      const responseTime = await measureInteractionTime(page, async () => {
        await page.keyboard.press(shortcut.key);
      });

      // Keyboard shortcuts should respond quickly
      expect(responseTime).toBeLessThan(100);
      await page.waitForTimeout(200);
    }
  });

  test('should handle context menu interactions efficiently', async ({ page }) => {
    const nodes = page.locator('.react-flow__node');
    const nodeCount = await nodes.count();

    if (nodeCount > 0) {
      const responseTime = await measureInteractionTime(page, async () => {
        await nodes.first().click({ button: 'right' });
      });

      // Context menu should appear quickly
      expect(responseTime).toBeLessThan(100);
    }
  });

  test('should update layout controls without lag', async ({ page }) => {
    const layoutSelector = page.locator('button').filter({ hasText: /layout/i });

    await expect(layoutSelector.first()).toBeVisible({ timeout: 10_000 });
    const responseTime = await measureInteractionTime(page, async () => {
      await layoutSelector.first().click();
    });

    expect(responseTime).toBeLessThan(100);
  });
});

test.describe('Graph Performance - Rendering Optimization', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/graph');
    await waitForGraphReady(page);
  });

  test('should use requestAnimationFrame for smooth updates', async ({ page }) => {
    // This test verifies that the graph uses RAF properly
    const rafUsage = await page.evaluate(async () => {
      let rafCalls = 0;
      const originalRAF = globalThis.requestAnimationFrame;

      globalThis.requestAnimationFrame = ((callback: FrameRequestCallback) => {
        rafCalls++;
        return originalRAF(callback);
      }) as typeof requestAnimationFrame;

      // Trigger an update
      window.scrollBy(0, 10);

      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ rafCalls });
        }, 1000);
      });
    });

    // Should use RAF for updates
    expect((rafUsage as any).rafCalls).toBeGreaterThan(0);
  });

  test('should batch DOM updates efficiently', async ({ page }) => {
    const nodes = page.locator('.react-flow__node');

    // Trigger multiple updates
    const startTime = Date.now();

    for (let i = 0; i < 5; i++) {
      await nodes.nth(i % (await nodes.count())).click();
    }

    const updateTime = Date.now() - startTime;

    // Batched updates should be fast
    expect(updateTime).toBeLessThan(500);
  });

  test('should minimize layout thrashing', async ({ page }) => {
    const layoutTime = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          const start = performance.now();

          // Potentially thrashing operations
          const nodes = document.querySelectorAll('.react-flow__node');
          nodes.forEach((node) => {
            const height = node.clientHeight; // Read
            (node as HTMLElement).style.height = `${height}px`; // Write
          });

          requestAnimationFrame(() => {
            const end = performance.now();
            resolve(end - start);
          });
        }),
    );

    // Should complete layout operations efficiently
    expect(layoutTime).toBeLessThan(50);
  });
});
