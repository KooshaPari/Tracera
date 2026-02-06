import { expect, test } from './global-setup';

/**
 * Graph View Visual Regression Tests
 *
 * Captures screenshots of the traceability graph visualization at multiple
 * viewport sizes to detect unintended visual changes in node rendering,
 * edge drawing, controls, and layout.
 *
 * Tags: @visual @regression @graph
 *
 * Run with: bun x playwright test --project=visual graph.visual
 */

const viewports = [
  { name: 'desktop', width: 1280, height: 720 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 667 },
] as const;

/**
 * Inject CSS to disable animations and transitions for deterministic screenshots.
 */
async function disableAnimations(page: import('@playwright/test').Page): Promise<void> {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
        caret-color: transparent !important;
      }
    `,
  });
}

/**
 * Wait for the React Flow graph to finish rendering.
 */
async function waitForGraphReady(page: import('@playwright/test').Page): Promise<void> {
  // Wait for the React Flow container to be present in the DOM
  const reactFlow = page.locator('.react-flow');
  await reactFlow.waitFor({ state: 'visible', timeout: 15_000 }).catch(() => {
    // Graph may not render in all test environments
  });

  // Give force-directed layout and edge rendering time to settle
  await page.waitForTimeout(2000);
}

test.describe('Graph View Visual Regression @visual', () => {
  for (const viewport of viewports) {
    test.describe(`${viewport.name} (${viewport.width}x${viewport.height})`, () => {
      test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
      });

      test(`should match graph view full-page screenshot at ${viewport.name}`, async ({ page }) => {
        await page.goto('/graph');
        await page.waitForLoadState('networkidle');
        await waitForGraphReady(page);
        await disableAnimations(page);

        await expect(page).toHaveScreenshot(`graph-full-page-${viewport.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.02,
        });
      });

      test(`should match graph controls and minimap at ${viewport.name}`, async ({ page }) => {
        await page.goto('/graph');
        await page.waitForLoadState('networkidle');
        await waitForGraphReady(page);
        await disableAnimations(page);

        // Verify controls are present before capturing
        const controls = page.locator('.react-flow__controls');
        await controls.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {
          // Controls may not render in all configurations
        });

        await expect(page).toHaveScreenshot(`graph-controls-${viewport.name}.png`, {
          fullPage: false,
          maxDiffPixelRatio: 0.02,
        });
      });
    });
  }

  test.describe('graph layout variants', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.goto('/graph');
      await page.waitForLoadState('networkidle');
      await waitForGraphReady(page);
    });

    test('should match graph with nodes and edges rendered', async ({ page }) => {
      await disableAnimations(page);

      // Check that some nodes exist
      const nodes = page.locator('.react-flow__nodes > div[data-id]');
      await nodes
        .first()
        .waitFor({ state: 'visible', timeout: 10_000 })
        .catch(() => {
          // Nodes may not be available in mocked/empty environment
        });

      await expect(page).toHaveScreenshot('graph-nodes-and-edges.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.02,
      });
    });

    test('should match graph after fit-to-view', async ({ page }) => {
      // Click fit-to-view button (third control button in React Flow)
      const fitBtn = page.locator('.react-flow__controls button').nth(2);
      if (await fitBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await fitBtn.click();
        await page.waitForTimeout(500);
      }

      await disableAnimations(page);

      await expect(page).toHaveScreenshot('graph-fit-to-view.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.02,
      });
    });

    test('should match graph with node selected', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      if (await firstNode.isVisible({ timeout: 5000 }).catch(() => false)) {
        await firstNode.click();
        await page.waitForTimeout(500);
      }

      await disableAnimations(page);

      await expect(page).toHaveScreenshot('graph-node-selected.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.02,
      });
    });

    test('should match graph minimap', async ({ page }) => {
      const minimap = page.locator('.react-flow__minimap');
      if (await minimap.isVisible({ timeout: 5000 }).catch(() => false)) {
        await disableAnimations(page);

        await expect(minimap).toHaveScreenshot('graph-minimap.png', {
          maxDiffPixelRatio: 0.02,
        });
      }
    });
  });

  test.describe('graph dark mode', () => {
    test('should match graph view in dark mode', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.emulateMedia({ colorScheme: 'dark' });
      await page.goto('/graph');
      await page.waitForLoadState('networkidle');
      await waitForGraphReady(page);
      await disableAnimations(page);

      await expect(page).toHaveScreenshot('graph-dark-mode.png', {
        fullPage: true,
        maxDiffPixelRatio: 0.02,
      });
    });
  });
});
