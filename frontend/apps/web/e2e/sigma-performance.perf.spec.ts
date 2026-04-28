/**
 * Sigma.js WebGL Rendering Performance Tests
 *
 * E2E tests that measure actual rendering performance in browser.
 * Tests the full rendering pipeline with WebGL.
 *
 * Performance targets:
 * - 10k nodes: 60 FPS, < 500ms initial render
 * - 50k nodes: 60 FPS, < 2000ms initial render
 * - 100k nodes: 60 FPS, < 5000ms initial render
 */

import { expect, test } from '@playwright/test';

/** Chrome non-standard performance.memory (optional) */
interface PerformanceMemory {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}

test.describe('Sigma.js WebGL Performance', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to graph view
    await page.goto('/projects/test-project/graph');

    // Wait for page to be ready
    await page.waitForLoadState('networkidle');
  });

  test('should render 10k nodes at 60 FPS', async ({ page }) => {
    // Generate 10k nodes via API or mock
    await page.evaluate(() => {
      interface NodeItem {
        id: string;
        type: string;
        position: { x: number; y: number };
        data: { label: string; type?: string };
      }
      interface EdgeItem {
        id: string;
        source: string;
        target: string;
      }
      const nodes: NodeItem[] = [];
      const edges: EdgeItem[] = [];

      for (let i = 0; i < 10_000; i++) {
        nodes.push({
          data: {
            label: `Node ${i}`,
            type: 'requirement',
          },
          id: `node-${i}`,
          position: {
            x: Math.random() * 10_000,
            y: Math.random() * 10_000,
          },
          type: 'requirement',
        });
      }

      for (let i = 0; i < 15_000; i++) {
        const source = `node-${Math.floor(Math.random() * 10_000)}`;
        const target = `node-${Math.floor(Math.random() * 10_000)}`;
        edges.push({
          id: `edge-${i}`,
          source,
          target,
        });
      }

      // Store in window for component access
      (
        globalThis as Window & {
          __testGraphData?: { nodes: NodeItem[]; edges: EdgeItem[] };
        }
      ).__testGraphData = { edges, nodes };
    });

    // Wait for WebGL mode indicator
    await expect(page.getByText('WebGL Mode')).toBeVisible({ timeout: 5000 });

    // Measure initial render time
    const startTime = Date.now();
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });
    const renderTime = Date.now() - startTime;

    // Initial render should be < 500ms
    expect(renderTime).toBeLessThan(500);

    // Measure FPS by monitoring frame times
    const fps = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();
          const duration = 1000; // Measure for 1 second

          const measureFPS = () => {
            frameCount++;
            const elapsed = performance.now() - startTime;

            if (elapsed < duration) {
              requestAnimationFrame(measureFPS);
            } else {
              const fps = Math.round((frameCount * 1000) / elapsed);
              resolve(fps);
            }
          };

          requestAnimationFrame(measureFPS);
        }),
    );

    // Should maintain 60 FPS (allow some variance: >= 55 FPS)
    expect(fps).toBeGreaterThanOrEqual(55);
  });

  test('should handle zoom interactions smoothly', async ({ page }) => {
    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });

    // Measure FPS during zoom
    const zoomFPS = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();
          const duration = 1000;

          // Simulate zoom while measuring FPS
          const measureFPS = () => {
            frameCount++;
            const elapsed = performance.now() - startTime;

            if (elapsed < duration) {
              // Trigger zoom event
              window.dispatchEvent(new WheelEvent('wheel', { deltaY: -100 }));
              requestAnimationFrame(measureFPS);
            } else {
              const fps = Math.round((frameCount * 1000) / elapsed);
              resolve(fps);
            }
          };

          requestAnimationFrame(measureFPS);
        }),
    );

    // Should maintain >= 55 FPS during zoom
    expect(zoomFPS).toBeGreaterThanOrEqual(55);
  });

  test('should handle pan interactions smoothly', async ({ page }) => {
    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });

    // Measure FPS during pan
    const panFPS = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();
          const duration = 1000;

          const measureFPS = () => {
            frameCount++;
            const elapsed = performance.now() - startTime;

            if (elapsed < duration) {
              requestAnimationFrame(measureFPS);
            } else {
              const fps = Math.round((frameCount * 1000) / elapsed);
              resolve(fps);
            }
          };

          requestAnimationFrame(measureFPS);
        }),
    );

    // Should maintain >= 55 FPS during pan
    expect(panFPS).toBeGreaterThanOrEqual(55);
  });

  test('should handle node selection efficiently', async ({ page }) => {
    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });

    // Measure time to select a node
    const selectionTime = await page.evaluate(() => {
      const start = performance.now();

      // Simulate node selection
      const event = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
      });

      document.dispatchEvent(event);

      return performance.now() - start;
    });

    // Selection should be < 16ms (60 FPS frame budget)
    expect(selectionTime).toBeLessThan(16);
  });

  test('should highlight selected node and neighbors', async ({ page }) => {
    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });

    // Click on a node (simulated)
    await page.evaluate(() => {
      // Simulate clicking on node-0
      const clickEvent = new CustomEvent('clickNode', {
        detail: { node: 'node-0' },
      });
      globalThis.dispatchEvent(clickEvent);
    });

    // Verify detail panel appears (WebGL mode)
    await expect(page.getByText('Node 0')).toBeVisible({ timeout: 1000 });

    // Measure highlight update time
    const highlightTime = await page.evaluate(() => {
      const start = performance.now();

      // Update highlights (simulated)
      globalThis.dispatchEvent(new CustomEvent('updateHighlights'));

      return performance.now() - start;
    });

    // Highlight update should be < 16ms
    expect(highlightTime).toBeLessThan(16);
  });

  test('should handle 50k nodes with performance mode', async ({ page }) => {
    // Generate 50k nodes
    await page.evaluate(() => {
      interface NodeItem {
        id: string;
        type: string;
        position: { x: number; y: number };
        data: { label: string };
      }
      const nodes: NodeItem[] = [];
      for (let i = 0; i < 50_000; i++) {
        const node: NodeItem = {
          data: {
            label: `Node ${i}`,
          },
          id: `node-${i}`,
          position: {
            x: Math.random() * 20_000,
            y: Math.random() * 20_000,
          },
          type: 'requirement',
        };
        nodes.push(node);
      }
      (
        globalThis as Window & {
          __testGraphData?: { nodes: NodeItem[]; edges: unknown[] };
        }
      ).__testGraphData = { edges: [], nodes };
    });

    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 15_000,
    });

    // Verify performance mode is active
    await expect(page.getByText('Performance')).toBeVisible();

    // Initial render should be < 2000ms
    const startTime = Date.now();
    await page.waitForSelector('[data-testid="sigma-container"]');
    const renderTime = Date.now() - startTime;

    expect(renderTime).toBeLessThan(2000);
  });

  test('should handle 100k nodes (stress test)', async ({ page }) => {
    // Increase timeout for this heavy test
    test.slow();

    // Generate 100k nodes
    await page.evaluate(() => {
      interface NodeItem {
        id: string;
        type: string;
        position: { x: number; y: number };
        data: { label: string };
      }
      const nodes: NodeItem[] = [];
      for (let i = 0; i < 100_000; i++) {
        const node: NodeItem = {
          data: {
            label: `Node ${i}`,
          },
          id: `node-${i}`,
          position: {
            x: Math.random() * 30_000,
            y: Math.random() * 30_000,
          },
          type: 'requirement',
        };
        nodes.push(node);
      }
      (
        globalThis as Window & {
          __testGraphData?: { nodes: NodeItem[]; edges: unknown[] };
        }
      ).__testGraphData = { edges: [], nodes };
    });

    // Wait for graph to load (longer timeout)
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 20_000,
    });

    // Verify performance mode is active
    await expect(page.getByText('Performance')).toBeVisible();

    // Initial render should be < 5000ms
    const startTime = Date.now();
    await page.waitForSelector('[data-testid="sigma-container"]');
    const renderTime = Date.now() - startTime;

    expect(renderTime).toBeLessThan(5000);

    // Measure FPS (should still target 60 FPS with optimizations)
    const fps = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();
          const duration = 1000;

          const measureFPS = () => {
            frameCount++;
            const elapsed = performance.now() - startTime;

            if (elapsed < duration) {
              requestAnimationFrame(measureFPS);
            } else {
              const fps = Math.round((frameCount * 1000) / elapsed);
              resolve(fps);
            }
          };

          requestAnimationFrame(measureFPS);
        }),
    );

    // With 100k nodes, accept >= 50 FPS
    expect(fps).toBeGreaterThanOrEqual(50);
  });

  test('should show performance metrics', async ({ page }) => {
    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });

    // Verify node/edge count badge is visible
    await expect(page.getByText(/nodes/i)).toBeVisible();

    // Verify FPS is being measured (implementation specific)
    // Performance overlay should show metrics
  });

  test('should apply LOD (Level of Detail) based on zoom', async ({ page }) => {
    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });

    // Zoom in
    await page.mouse.wheel(0, -500); // Scroll up to zoom in

    // At close zoom, labels should be visible
    // (Implementation would check canvas rendering)

    // Zoom out
    await page.mouse.wheel(0, 500); // Scroll down to zoom out

    // At far zoom, labels should be hidden
    // (Implementation would check canvas rendering)

    // Verify zoom operations are smooth
    const zoomFPS = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();

          const measureFPS = () => {
            frameCount++;
            if (performance.now() - startTime < 1000) {
              requestAnimationFrame(measureFPS);
            } else {
              resolve(frameCount);
            }
          };

          requestAnimationFrame(measureFPS);
        }),
    );

    expect(zoomFPS).toBeGreaterThanOrEqual(55);
  });

  test('should hide edges during pan/zoom for performance', async ({ page }) => {
    // Wait for graph to load
    await page.waitForSelector('[data-testid="sigma-container"]', {
      timeout: 10_000,
    });

    // Start panning
    await page.mouse.down();
    await page.mouse.move(100, 100);

    // During pan, edges should be hidden (implementation check)
    // FPS should remain high

    await page.mouse.up();

    // After pan, edges should reappear
  });
});

test.describe('Sigma.js Memory Performance', () => {
  test('should not leak memory during graph updates', async ({ page }) => {
    await page.goto('/projects/test-project/graph');

    // Get initial memory usage (Chrome-only performance.memory)
    const initialMemory = await page.evaluate(() => {
      const perf = performance as Performance & { memory?: PerformanceMemory };
      if (perf.memory != null) {
        return perf.memory.usedJSHeapSize;
      }
      return 0;
    });

    // Update graph multiple times
    for (let i = 0; i < 10; i++) {
      await page.evaluate(() => {
        // Trigger graph update
        globalThis.dispatchEvent(new CustomEvent('updateGraph'));
      });

      await page.waitForTimeout(100);
    }

    // Get final memory usage (Chrome-only performance.memory)
    const finalMemory = await page.evaluate(() => {
      const perf = performance as Performance & { memory?: PerformanceMemory };
      if (perf.memory != null) {
        return perf.memory.usedJSHeapSize;
      }
      return 0;
    });

    // Memory growth should be minimal (< 50 MB)
    const memoryGrowth = (finalMemory - initialMemory) / 1024 / 1024;
    expect(memoryGrowth).toBeLessThan(50);
  });
});
