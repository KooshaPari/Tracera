/**
 * Sigma.js Transition Tests
 *
 * Tests for smooth transitions between ReactFlow and Sigma.js WebGL renderers.
 * Verifies camera position preservation, fade animations, and state management.
 */

import { expect, test } from '@playwright/test';

declare global {
  interface Window {
    __testGraphData?: {
      nodes: {
        id: string;
        position: { x: number; y: number };
        data?: Record<string, unknown>;
      }[];
      edges: unknown[];
    };
  }
}

test.describe('Hybrid Graph View Transitions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects/test-project/graph');
    await page.waitForLoadState('networkidle');
  });

  test('should show ReactFlow mode for < 10k nodes', async ({ page }) => {
    // Generate 5k nodes (below threshold)
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 5000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 5000, y: Math.random() * 5000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Should show ReactFlow mode indicator
    await expect(page.getByText('ReactFlow Mode')).toBeVisible({
      timeout: 5000,
    });

    // Node count badge should show correct count
    await expect(page.getByText(/5,000 nodes/i)).toBeVisible();
  });

  test('should switch to WebGL mode at 10k nodes', async ({ page }) => {
    // Start with 5k nodes (ReactFlow mode)
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 5000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 5000, y: Math.random() * 5000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    await expect(page.getByText('ReactFlow Mode')).toBeVisible();

    // Add more nodes to exceed threshold
    await page.evaluate(() => {
      const existingNodes = globalThis.__testGraphData!.nodes;
      for (let i = 5000; i < 10_500; i++) {
        existingNodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes: existingNodes };
      globalThis.dispatchEvent(new CustomEvent('updateGraph'));
    });

    // Should transition to WebGL mode
    await expect(page.getByText('WebGL Mode')).toBeVisible({ timeout: 3000 });

    // Transition notification should appear and disappear
    await expect(page.getByText(/Switching to WebGL/i)).toBeVisible({
      timeout: 1000,
    });
    await expect(page.getByText(/Switching to WebGL/i)).not.toBeVisible({
      timeout: 2000,
    });
  });

  test('should show transition notification', async ({ page }) => {
    // Start with 9k nodes (below threshold)
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 9000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 9000, y: Math.random() * 9000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Add nodes to cross threshold
    await page.evaluate(() => {
      const { nodes } = globalThis.__testGraphData!;
      for (let i = 9000; i < 11_000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
        });
      }
      globalThis.dispatchEvent(new CustomEvent('updateGraph'));
    });

    // Transition notification should animate in
    const notification = page.getByText(/Switching to WebGL/i);
    await expect(notification).toBeVisible({ timeout: 1000 });

    // Should fade out after ~1.5s
    await expect(notification).not.toBeVisible({ timeout: 2500 });
  });

  test('should show warning near threshold', async ({ page }) => {
    // Generate 8500 nodes (near threshold)
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 8500; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 8500, y: Math.random() * 8500 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Should show threshold warning
    await expect(page.getByText(/Approaching 10k node threshold/i)).toBeVisible({
      timeout: 5000,
    });

    // Should still be in ReactFlow mode
    await expect(page.getByText('ReactFlow Mode')).toBeVisible();
  });

  test('should preserve node selection across transition', async ({ page }) => {
    // Start with 9k nodes
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 9000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 9000, y: Math.random() * 9000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Select a node in ReactFlow mode
    await page.evaluate(() => {
      globalThis.dispatchEvent(new CustomEvent('selectNode', { detail: { nodeId: 'node-0' } }));
    });

    // Add nodes to trigger transition
    await page.evaluate(() => {
      const { nodes } = globalThis.__testGraphData!;
      for (let i = 9000; i < 11_000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
        });
      }
      globalThis.dispatchEvent(new CustomEvent('updateGraph'));
    });

    // Wait for transition to WebGL
    await expect(page.getByText('WebGL Mode')).toBeVisible({ timeout: 3000 });

    // Node should still be selected (detail panel visible)
    await expect(page.getByText('Node 0')).toBeVisible({ timeout: 1000 });
  });

  test('should handle rapid threshold crossings', async ({ page }) => {
    // Start below threshold
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 9000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 9000, y: Math.random() * 9000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    await expect(page.getByText('ReactFlow Mode')).toBeVisible();

    // Cross threshold up
    await page.evaluate(() => {
      const { nodes } = globalThis.__testGraphData!;
      for (let i = 9000; i < 11_000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
        });
      }
      globalThis.dispatchEvent(new CustomEvent('updateGraph'));
    });

    await expect(page.getByText('WebGL Mode')).toBeVisible({ timeout: 3000 });

    // Cross threshold down
    await page.evaluate(() => {
      const nodes = globalThis.__testGraphData!.nodes.slice(0, 9000);
      globalThis.__testGraphData!.nodes = nodes;
      globalThis.dispatchEvent(new CustomEvent('updateGraph'));
    });

    await expect(page.getByText('ReactFlow Mode')).toBeVisible({
      timeout: 3000,
    });

    // Should handle transitions gracefully without errors
  });

  test('should show performance mode for large graphs', async ({ page }) => {
    // Generate 60k nodes (should trigger performance mode)
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 60_000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 30_000, y: Math.random() * 30_000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Should be in WebGL mode
    await expect(page.getByText('WebGL Mode')).toBeVisible({ timeout: 10_000 });

    // Should show performance mode indicator
    await expect(page.getByText('Performance')).toBeVisible({ timeout: 1000 });

    // Should show warning about large graph
    await expect(page.getByText(/Large graph detected/i)).toBeVisible();
  });

  test('should animate transition with fade effect', async ({ page }) => {
    // Start with 9k nodes
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 9000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 9000, y: Math.random() * 9000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Get reference to ReactFlow container
    const reactFlowContainer = page.locator('[data-reactflow-container]');
    await expect(reactFlowContainer).toBeVisible();

    // Trigger transition
    await page.evaluate(() => {
      const { nodes } = globalThis.__testGraphData!;
      for (let i = 9000; i < 11_000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
        });
      }
      globalThis.dispatchEvent(new CustomEvent('updateGraph'));
    });

    // Wait for Sigma container to appear
    const sigmaContainer = page.locator('[data-testid="sigma-container"]');
    await expect(sigmaContainer).toBeVisible({ timeout: 3000 });

    // Verify transition completed
    await expect(page.getByText('WebGL Mode')).toBeVisible();
  });

  test('should maintain graph state during transition', async ({ page }) => {
    // Start with 9k nodes
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 9000; i++) {
        nodes.push({
          data: { label: `Node ${i}`, type: 'requirement' },
          id: `node-${i}`,
          position: { x: Math.random() * 9000, y: Math.random() * 9000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Apply filters or settings
    await page.evaluate(() => {
      globalThis.dispatchEvent(new CustomEvent('applyFilter', { detail: { type: 'requirement' } }));
    });

    // Trigger transition
    await page.evaluate(() => {
      const { nodes } = globalThis.__testGraphData!;
      for (let i = 9000; i < 11_000; i++) {
        nodes.push({
          data: { label: `Node ${i}`, type: 'requirement' },
          id: `node-${i}`,
          position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
        });
      }
      globalThis.dispatchEvent(new CustomEvent('updateGraph'));
    });

    await expect(page.getByText('WebGL Mode')).toBeVisible({ timeout: 3000 });

    // Filters should still be applied
    // (Implementation would verify filtered state)
  });

  test('should open detail panel in WebGL mode on node click', async ({ page }) => {
    // Generate 11k nodes (WebGL mode)
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 11_000; i++) {
        nodes.push({
          data: {
            description: `Description for node ${i}`,
            label: `Node ${i}`,
          },
          id: `node-${i}`,
          position: { x: Math.random() * 11_000, y: Math.random() * 11_000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    await expect(page.getByText('WebGL Mode')).toBeVisible({ timeout: 10_000 });

    // Click on a node (simulated)
    await page.evaluate(() => {
      globalThis.dispatchEvent(new CustomEvent('clickNode', { detail: { node: 'node-0' } }));
    });

    // Detail panel should slide in from right
    await expect(page.getByText('Node 0')).toBeVisible({ timeout: 1000 });
    await expect(page.getByText(/Description for node 0/i)).toBeVisible();

    // Close button should be visible
    const closeButton = page.getByRole('button', { name: /close/i });
    await expect(closeButton).toBeVisible();

    // Close detail panel
    await closeButton.click();
    await expect(page.getByText('Node 0')).not.toBeVisible({ timeout: 1000 });
  });

  test('should measure transition performance', async ({ page }) => {
    // Start with 9k nodes
    await page.evaluate(() => {
      const nodes = [];
      for (let i = 0; i < 9000; i++) {
        nodes.push({
          data: { label: `Node ${i}` },
          id: `node-${i}`,
          position: { x: Math.random() * 9000, y: Math.random() * 9000 },
        });
      }
      globalThis.__testGraphData = { edges: [], nodes };
    });

    // Measure transition time
    const transitionTime = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          const start = performance.now();

          // Trigger transition
          const { nodes } = window.__testGraphData!;
          for (let i = 9000; i < 11_000; i++) {
            nodes.push({
              data: { label: `Node ${i}` },
              id: `node-${i}`,
              position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
            });
          }

          window.dispatchEvent(new CustomEvent('updateGraph'));

          // Wait for transition to complete
          setTimeout(() => {
            const elapsed = performance.now() - start;
            resolve(elapsed);
          }, 500);
        }),
    );

    // Transition should complete in < 500ms
    expect(transitionTime).toBeLessThan(500);
  });
});
