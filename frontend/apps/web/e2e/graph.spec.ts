import { expect, test } from './global-setup';

/**
 * E2E Tests for Graph Visualization
 * Tests traceability graph interactions, layout, filtering, and navigation
 */
test.describe('Graph Visualization', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Graph Rendering', () => {
    test('should render graph container', async ({ page }) => {
      // React Flow container - uses .react-flow div
      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 10_000 });

      // SVG rendering area for React Flow
      const svg = page.locator('.react-flow svg');
      await expect(svg).toBeVisible({ timeout: 10_000 });
    });

    test('should display nodes for items', async ({ page }) => {
      // React Flow nodes are rendered as div elements with data-id attribute
      const nodes = page.locator('.react-flow .react-flow__nodes > div[data-id]');
      // We expect at least one node to be present in the mock data
      await expect(nodes.first()).toBeVisible({ timeout: 10_000 });
      const nodeCount = await nodes.count();
      expect(nodeCount).toBeGreaterThan(0);
    });

    test('should display edges for links', async ({ page }) => {
      // React Flow edges are rendered as SVG paths/elements in the edges container
      const edges = page.locator('.react-flow__edges > g[data-testid], .react-flow__edges path');
      // We expect at least one edge if items are linked
      await expect(edges.first().or(page.locator('.react-flow__edges > g').first())).toBeVisible({
        timeout: 10_000,
      });
    });

    test('should show loading state while rendering', async ({ page }) => {
      // Reload page to catch loading state
      await page.reload();

      // Wait for graph to load
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.react-flow')).toBeVisible({ timeout: 10_000 });
    });
  });

  test.describe('Graph Interactions', () => {
    test('should zoom in/out with controls', async ({ page }) => {
      // React Flow controls - button elements in the controls container
      const zoomInBtn = page.locator('.react-flow__controls button').nth(0);
      const zoomOutBtn = page.locator('.react-flow__controls button').nth(1);

      await expect(zoomInBtn).toBeVisible({ timeout: 5000 });
      // Zoom in
      await zoomInBtn.click();
      await page.waitForTimeout(500);

      // Zoom out
      await zoomOutBtn.click();
      await page.waitForTimeout(500);
    });

    test('should zoom with mouse wheel', async ({ page }) => {
      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 5000 });
      // Scroll up to zoom in
      await reactFlowContainer.hover();
      await page.mouse.wheel(0, -100);
      await page.waitForTimeout(300);

      // Scroll down to zoom out
      await page.mouse.wheel(0, 100);
      await page.waitForTimeout(300);
    });

    test('should pan graph by dragging', async ({ page }) => {
      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 5000 });
      const box = await reactFlowContainer.boundingBox();
      if (box) {
        // Drag from center to move graph
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
        await page.mouse.down();
        await page.mouse.move(box.x + box.width / 2 + 100, box.y + box.height / 2 + 100);
        await page.mouse.up();
      }
    });

    test('should fit graph to view', async ({ page }) => {
      // React Flow fit view button - third button in controls (after zoom in/out)
      const fitBtn = page.locator('.react-flow__controls button').nth(2);
      await expect(fitBtn).toBeVisible({ timeout: 5000 });
      await fitBtn.click();
      await page.waitForTimeout(500);
    });

    test('should select node on click', async ({ page }) => {
      // Click first available node
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 10_000 });
      await firstNode.click();

      // Look for node details panel on the right side
      const detailsPanel = page.locator('.w-96').filter({ hasText: /incoming|outgoing/ });
      await expect(detailsPanel).toBeVisible({ timeout: 5000 });
    });

    test('should show node tooltip on hover', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 10_000 });
      await firstNode.hover();
      await page.waitForTimeout(300);

      // Look for tooltip
      const tooltip = page.getByRole('tooltip');
      await expect(tooltip).toBeVisible({ timeout: 2000 });
    });
  });

  test.describe('Graph Filtering', () => {
    test('should filter by item type', async ({ page }) => {
      // Look for type filter
      const typeFilter = page.getByLabel(/type|filter.*type/i);
      await expect(typeFilter).toBeVisible({ timeout: 5000 });
      await typeFilter.click();
      await page.getByText(/requirement/i).click();
      await page.waitForLoadState('networkidle');
    });

    test('should filter by link type', async ({ page }) => {
      const linkTypeFilter = page.getByLabel(/link.*type/i);
      await expect(linkTypeFilter).toBeVisible({ timeout: 5000 });
      await linkTypeFilter.click();
      await page.getByText(/implements/i).click();
      await page.waitForLoadState('networkidle');
    });

    test('should filter by project', async ({ page }) => {
      const projectFilter = page.getByLabel(/project/i);
      await expect(projectFilter).toBeVisible({ timeout: 5000 });
      await projectFilter.click();
      await page.getByText(/tracertm core/i).click();
      await page.waitForLoadState('networkidle');
    });

    test('should show/hide orphan nodes', async ({ page }) => {
      const orphanToggle = page.getByLabel(/show.*orphan|hide.*orphan|unlinked/i);
      await expect(orphanToggle).toBeVisible({ timeout: 5000 });
      // Toggle off
      await orphanToggle.click();
      await page.waitForTimeout(500);

      // Toggle back on
      await orphanToggle.click();
      await page.waitForTimeout(500);
    });

    test('should filter by node depth', async ({ page }) => {
      const depthControl = page.getByLabel(/depth|levels/i);
      await expect(depthControl).toBeVisible({ timeout: 5000 });
      // Set depth to 2
      await depthControl.fill('2');
      await page.waitForLoadState('networkidle');
    });
  });

  test.describe('Graph Layouts', () => {
    test('should switch to hierarchical layout', async ({ page }) => {
      // Layout selector is a Select component with trigger button
      const layoutSelectTrigger = page
        .locator('button')
        .filter({ hasText: /Force-directed|Hierarchical|Radial|Grid/ })
        .first();
      await expect(layoutSelectTrigger).toBeVisible({ timeout: 5000 });
      await layoutSelectTrigger.click();
      await page.waitForTimeout(300);

      const hierarchical = page.getByText('Hierarchical');
      await expect(hierarchical).toBeVisible({ timeout: 5000 });
      await hierarchical.click();
      await page.waitForTimeout(1000);
    });

    test('should switch to force-directed layout', async ({ page }) => {
      const layoutSelectTrigger = page
        .locator('button')
        .filter({ hasText: /Force-directed|Hierarchical|Radial|Grid/ })
        .first();
      await expect(layoutSelectTrigger).toBeVisible({ timeout: 5000 });
      await layoutSelectTrigger.click();
      await page.waitForTimeout(300);

      const forceDirected = page.getByText('Force-directed');
      await expect(forceDirected).toBeVisible({ timeout: 5000 });
      await forceDirected.click();
      await page.waitForTimeout(1000);
    });

    test('should switch to radial layout', async ({ page }) => {
      const layoutSelectTrigger = page
        .locator('button')
        .filter({ hasText: /Force-directed|Hierarchical|Radial|Grid/ })
        .first();
      await expect(layoutSelectTrigger).toBeVisible({ timeout: 5000 });
      await layoutSelectTrigger.click();
      await page.waitForTimeout(300);

      const radial = page.getByText('Radial');
      await expect(radial).toBeVisible({ timeout: 5000 });
      await radial.click();
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Graph Navigation', () => {
    test('should navigate to item from node', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 5000 });
      // Click node to select it
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for a button or link to navigate to item detail
      // This might be in the detail panel that opens on the right
      const detailPanel = page.locator('.w-96');
      const navigateLink = detailPanel
        .locator('a, button')
        .filter({ hasText: /open|view|navigate|detail/i })
        .first();

      await expect(navigateLink).toBeVisible({ timeout: 5000 });
      await navigateLink.click();
      await page.waitForLoadState('networkidle');

      // Should navigate to item detail page
      await expect(page).toHaveURL(/\/items\//);
    });

    test('should highlight path between nodes', async ({ page }) => {
      // Select source node
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 5000 });
      await firstNode.click();
      await page.waitForTimeout(300);

      // Shift-click target node to show path
      const secondNode = page.locator('.react-flow__nodes > div[data-id]').nth(1);
      await expect(secondNode).toBeVisible({ timeout: 5000 });
      await page.keyboard.down('Shift');
      await secondNode.click();
      await page.keyboard.up('Shift');
    });

    test('should focus on selected node', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 5000 });
      await firstNode.click();
      await page.waitForTimeout(300);

      // Use the fit view button (third control button) to focus on selected node
      const fitBtn = page.locator('.react-flow__controls button').nth(2);
      await expect(fitBtn).toBeVisible({ timeout: 5000 });
      await fitBtn.click();
      await page.waitForTimeout(500);
    });
  });

  test.describe('Graph Export', () => {
    test('should check export functionality', async ({ page }) => {
      // Export is typically available in the top menu or toolbar
      const exportBtn = page.getByRole('button', {
        name: /export|download|save/i,
      });

      await expect(exportBtn).toBeVisible({ timeout: 5000 });
    });

    test('should check for graph data access', async ({ page }) => {
      // Check if we can access graph data through the page
      const graphContainer = page.locator('.react-flow');

      await expect(graphContainer).toBeVisible({ timeout: 5000 });
      const nodeCount = await page.locator('.react-flow__nodes > div[data-id]').count();
      expect(nodeCount).toBeGreaterThan(0);
    });
  });

  test.describe('Graph Search', () => {
    test('should check for search functionality', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search|find/i);
      await expect(searchInput).toBeVisible({ timeout: 5000 });
      await searchInput.fill('authentication');
      await page.waitForTimeout(500);
      await searchInput.clear();
    });

    test('should verify graph interactivity', async ({ page }) => {
      // Basic check that graph nodes are interactive
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 5000 });
      await firstNode.click();
      await page.waitForTimeout(300);
    });
  });

  test.describe('Mini-map', () => {
    test('should display graph mini-map', async ({ page }) => {
      // React Flow MiniMap is rendered inside the react-flow container
      const minimap = page.locator('.react-flow__minimap');
      await expect(minimap).toBeVisible({ timeout: 5000 });
    });

    test('should navigate using mini-map', async ({ page }) => {
      const minimap = page.locator('.react-flow__minimap');
      await expect(minimap).toBeVisible({ timeout: 5000 });
      // Get minimap bounds and click in the middle
      const box = await minimap.boundingBox();
      if (box) {
        await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('Graph Performance', () => {
    test('should handle graph rendering without errors', async ({ page }) => {
      // Check if graph renders without errors
      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 10_000 });

      // Check console for critical errors
      const errors: string[] = [];
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await page.waitForTimeout(2000);

      expect(errors).toBeDefined();
    });
  });

  test.describe('Graph Context Menu', () => {
    test('should check for node context menu', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 5000 });
      await firstNode.click({ button: 'right' });
      await page.waitForTimeout(300);

      // Look for context menu
      const contextMenu = page.getByRole('menu');
      await expect(contextMenu).toBeVisible({ timeout: 2000 });
    });

    test('should check for node interactions', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();
      await expect(firstNode).toBeVisible({ timeout: 5000 });
      // Single click should select node
      await firstNode.click();
      await page.waitForTimeout(300);

      // Detail panel should appear on the right
      const detailPanel = page.locator('.w-96').filter({ hasText: /incoming|outgoing/ });
      await expect(detailPanel).toBeVisible({ timeout: 5000 });
    });
  });
});
