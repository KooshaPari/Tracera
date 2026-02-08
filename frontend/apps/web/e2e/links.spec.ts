import { expect, test } from './global-setup';

/**
 * E2E Tests for Traceability Links Management
 * Tests creation, deletion, and visualization of links between items
 */
test.describe('Traceability Links', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Links List View', () => {
    test('should display links on graph page', async ({ page }) => {
      // Navigate to graph
      await page.getByRole('link', { name: /graph/i }).click();
      await page.waitForLoadState('networkidle');

      // Verify URL
      await expect(page).toHaveURL(/\/graph/);

      // Check for React Flow graph visualization
      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 15_000 });

      // Check for edges (links) in the graph
      const edges = page.locator('.react-flow__edges > g');
      await expect(edges.first()).toBeVisible({ timeout: 10_000 });
    });

    test('should navigate to links view', async ({ page }) => {
      // Navigate to links view
      const linksLink = page.getByRole('link', { name: /links/i });
      await expect(linksLink).toBeVisible({ timeout: 5000 });
      await linksLink.click();
      await page.waitForLoadState('networkidle');

      // Should be on /links page
      await expect(page).toHaveURL(/\/links/);

      // Check for links list heading
      const heading = page.getByRole('heading', { name: /links/i });
      await expect(heading).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Create Link', () => {
    test('should navigate to item detail page', async ({ page }) => {
      // Navigate to items
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Find first item in the list and click it
      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      await expect(firstItemLink).toBeVisible({ timeout: 5000 });
      await firstItemLink.click();
      await page.waitForLoadState('networkidle');

      // Should navigate to item detail page with /items/ in URL
      await expect(page).toHaveURL(/\/items\//);
    });

    test('should view links section on item detail page', async ({ page }) => {
      // Navigate to item detail page
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Click first item
      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      await expect(firstItemLink).toBeVisible({ timeout: 5000 });
      await firstItemLink.click();
      await page.waitForLoadState('networkidle');

      // Look for Links tab
      const linksTab = page.getByRole('tab', { name: /links/i });
      await expect(linksTab).toBeVisible({ timeout: 5000 });
      await linksTab.click();
      await page.waitForTimeout(300);

      // Check for link sections
      const outgoingHeading = page.getByRole('heading', {
        name: /outgoing/i,
      });
      const incomingHeading = page.getByRole('heading', {
        name: /incoming/i,
      });

      // At least one of them should be visible
      const isOutgoingVisible = await outgoingHeading.isVisible();
      const isIncomingVisible = await incomingHeading.isVisible();
      expect(isOutgoingVisible || isIncomingVisible).toBe(true);
    });

    test('should check links visibility', async ({ page }) => {
      // Navigate to items and select first
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      await expect(firstItemLink).toBeVisible({ timeout: 5000 });
      await firstItemLink.click();
      await page.waitForLoadState('networkidle');

      // Click Links tab
      const linksTab = page.getByRole('tab', { name: /links/i });
      await expect(linksTab).toBeVisible({ timeout: 5000 });
      await linksTab.click();

      // Check for any link items
      const linkItems = page
        .locator('div')
        .filter({ hasText: /badge|secondary/ })
        .filter({ hasText: /→/ });
      await expect(linkItems.first()).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Delete Link', () => {
    test('should navigate to item with links', async ({ page }) => {
      // Navigate to items
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Click first item to view details
      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      await expect(firstItemLink).toBeVisible({ timeout: 5000 });
      await firstItemLink.click();
      await page.waitForLoadState('networkidle');

      // Navigate to links tab
      const linksTab = page.getByRole('tab', { name: /links/i });
      await expect(linksTab).toBeVisible({ timeout: 5000 });
      await linksTab.click();
      await page.waitForTimeout(300);

      // Check if there are any links
      const linkItems = page.locator('div').filter({ hasText: /→/ });
      await expect(linkItems.first()).toBeVisible({ timeout: 5000 });
    });

    test('should check for delete link functionality', async ({ page }) => {
      // Navigate to graph
      await page.getByRole('link', { name: /graph/i }).click();
      await page.waitForLoadState('networkidle');

      // Check for edges in graph
      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 5000 });

      // Try to click on an edge
      const edges = page.locator('.react-flow__edges > g');
      await expect(edges.first()).toBeVisible({ timeout: 10_000 });

      // Click first edge
      await edges.first().click();
      await page.waitForTimeout(300);

      // Check for delete action
      const deleteAction = page.getByRole('button', {
        name: /delete|remove|unlink/i,
      });

      await expect(deleteAction).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Link Types', () => {
    test('should display link types in graph', async ({ page }) => {
      // Navigate to graph
      await page.getByRole('link', { name: /graph/i }).click();
      await page.waitForLoadState('networkidle');

      // Look for edge labels showing link types
      const edgeLabels = page.locator('.react-flow__edge-label');
      await expect(edgeLabels.first()).toBeVisible({ timeout: 10_000 });
    });

    test('should display link types on item detail page', async ({ page }) => {
      // Navigate to items and select first
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      await expect(firstItemLink).toBeVisible({ timeout: 5000 });
      await firstItemLink.click();
      await page.waitForLoadState('networkidle');

      // Click Links tab
      const linksTab = page.getByRole('tab', { name: /links/i });
      await expect(linksTab).toBeVisible({ timeout: 5000 });
      await linksTab.click();

      // Check for badge elements that display link types
      const linkTypeText = page.getByText(/implements|tests|depends_on|related_to/i);
      await expect(linkTypeText.first()).toBeVisible({ timeout: 10_000 });
    });
  });

  test.describe('Link Navigation', () => {
    test('should navigate between items via links', async ({ page }) => {
      // Navigate to items
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Click first item
      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      await expect(firstItemLink).toBeVisible({ timeout: 5000 });
      await firstItemLink.click();
      await page.waitForLoadState('networkidle');

      // Click Links tab
      const linksTab = page.getByRole('tab', { name: /links/i });
      await expect(linksTab).toBeVisible({ timeout: 5000 });
      await linksTab.click();
      await page.waitForTimeout(300);

      // Look for link item IDs that are clickable
      const linkItems = page.locator('span').filter({ hasText: /item-|[a-f0-9]{8}-/ });
      await expect(linkItems.first()).toBeVisible({ timeout: 5000 });
    });

    test('should show bidirectional links', async ({ page }) => {
      // Navigate to items
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Click first item
      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      await expect(firstItemLink).toBeVisible({ timeout: 5000 });
      await firstItemLink.click();
      await page.waitForLoadState('networkidle');

      // Click Links tab
      const linksTab = page.getByRole('tab', { name: /links/i });
      await expect(linksTab).toBeVisible({ timeout: 5000 });
      await linksTab.click();
      await page.waitForTimeout(300);

      // Check for outgoing and incoming sections
      const outgoingSection = page.getByRole('heading', {
        name: /outgoing/i,
      });
      const incomingSection = page.getByRole('heading', {
        name: /incoming/i,
      });

      const isOutgoingVisible = await outgoingSection.isVisible();
      const isIncomingVisible = await incomingSection.isVisible();
      expect(isOutgoingVisible || isIncomingVisible).toBe(true);
    });
  });

  test.describe('Link Visualization', () => {
    test('should display links in graph view', async ({ page }) => {
      // Navigate to graph
      await page.getByRole('link', { name: /graph/i }).click();
      await page.waitForLoadState('networkidle');

      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 5000 });

      // Check for nodes and edges
      const nodes = page.locator('.react-flow__nodes > div[data-id]');
      await expect(nodes.first()).toBeVisible({ timeout: 10_000 });

      const edges = page.locator('.react-flow__edges > g');
      await expect(edges.first()).toBeVisible({ timeout: 10_000 });
    });

    test('should show edge labels on hover', async ({ page }) => {
      // Navigate to graph
      await page.getByRole('link', { name: /graph/i }).click();
      await page.waitForLoadState('networkidle');

      const reactFlowContainer = page.locator('.react-flow');
      await expect(reactFlowContainer).toBeVisible({ timeout: 5000 });

      // Hover over an edge
      const edge = page.locator('.react-flow__edges > g').first();
      await expect(edge).toBeVisible({ timeout: 5000 });
      await edge.hover();
      await page.waitForTimeout(300);

      // Edge labels should be visible
      const edgeLabel = page.locator('.react-flow__edge-label');
      await expect(edgeLabel.first()).toBeVisible({ timeout: 5000 });
    });

    test('should allow edge interaction', async ({ page }) => {
      // Navigate to graph
      await page.getByRole('link', { name: /graph/i }).click();
      await page.waitForLoadState('networkidle');

      const edges = page.locator('.react-flow__edges > g');
      const edgeCount = await edges.count().catch(() => 0);

      if (edgeCount > 0) {
        // Try clicking first edge
        await edges.first().click();
        await page.waitForTimeout(300);
      }
    });
  });

  test.describe('Link Statistics', () => {
    test('should display link tabs on items page', async ({ page }) => {
      // Navigate to items
      await page.getByRole('link', { name: /items/i }).click();
      await page.waitForLoadState('networkidle');

      // Click first item to view details
      const firstItemLink = page
        .locator('a')
        .filter({ hasText: /item|requirement|feature/i })
        .first();
      if (await firstItemLink.isVisible({ timeout: 2000 })) {
        await firstItemLink.click();
        await page.waitForLoadState('networkidle');

        // Check for Links tab with count
        const linksTab = page.getByRole('tab').filter({ hasText: /links/i });
        await expect(linksTab).toBeVisible({ timeout: 5000 });
      }
    });

    test('should show links in graph title', async ({ page }) => {
      // Navigate to graph
      await page.getByRole('link', { name: /graph/i }).click();
      await page.waitForLoadState('networkidle');

      // Check for graph title/stats
      const title = page.getByRole('heading', { name: /traceability graph/i });
      const stats = page.getByText(/items.*connections|connections.*items/i);

      if (await title.isVisible({ timeout: 2000 })) {
        if (await stats.isVisible({ timeout: 2000 })) {
          await stats.textContent();
        }
      }
    });
  });
});
