import { test } from './global-setup';

/**
 * Equivalence Panel Tests
 *
 * Tests for viewing, managing, and navigating equivalent items
 * across different dimensions in the traceability graph.
 *
 * Equivalence Features:
 * - View equivalence panel for selected node
 * - Confirm suggested equivalences
 * - Reject suggested equivalences
 * - Navigate via pivot targets
 * - Display equivalence strength/confidence
 * - Show equivalence relationships visually
 */

test.describe('Equivalence Panel', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test.describe('View Equivalence Panel', () => {
    test('should display equivalence panel when node is selected', async ({ page }) => {
      // Click on a node to select it
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for equivalence panel
      const equivalencePanel = page
        .locator("[class*='equivalence'], [class*='equivalent'], aside, .w-96")
        .filter({ hasText: /equivalent|maps to|corresponds|related/i })
        .first();

      await expect(equivalencePanel).toBeVisible({ timeout: 3000 });
    });

    test('should show equivalence list for selected item', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for equivalence section or tab
      const equivalenceTab = page
        .getByRole('tab', {
          name: /equivalent|equivalence/i,
        })
        .first();

      await expect(equivalenceTab).toBeVisible({ timeout: 5000 });
      await equivalenceTab.click();
      await page.waitForTimeout(500);

      // Look for list of equivalent items
      const equivalentList = page
        .locator("ul, [role='list']")
        .filter({ hasText: /equivalent|maps to/i })
        .first();

      await expect(equivalentList).toBeVisible({ timeout: 5000 });
    });

    test('should display equivalence strength/confidence', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for confidence/strength indicator
      const confidenceIndicators = page.getByText(/confidence|strength|match|score|%/i).first();
      await expect(confidenceIndicators).toBeVisible();

      // Look for progress bars or rating indicators
      const progressBars = page
        .locator("[role='progressbar'], [class*='progress'], [class*='strength']")
        .first();
      await expect(progressBars).toBeVisible();
    });

    test('should show equivalence metadata', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for equivalence metadata section
      const metadata = page.getByText(/dimension|view|perspective|type|status|version/i).first();
      await expect(metadata).toBeVisible();
    });
  });

  test.describe('Suggested Equivalences', () => {
    test('should display suggested equivalences', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for suggested equivalences section
      const suggestedSection = page.getByText(/suggested|recommended|potential|candidate/i).first();

      await expect(suggestedSection).toBeVisible({ timeout: 2000 });

      // Look for equivalence items marked as suggested
      const suggestedItems = page.locator("[class*='suggested'], [class*='recommended']").first();
      await expect(suggestedItems).toBeVisible();
    });

    test('should show confirmation actions for suggested equivalences', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for confirm/approve buttons
      const confirmBtn = page
        .locator('button')
        .filter({ hasText: /confirm|approve|accept|yes/i })
        .first();

      await expect(confirmBtn).toBeVisible({ timeout: 2000 });

      // Look for reject/deny buttons
      const rejectBtn = page
        .locator('button')
        .filter({ hasText: /reject|deny|no|dismiss/i })
        .first();

      await expect(rejectBtn).toBeVisible({ timeout: 2000 });
    });
  });

  test.describe('Confirm Equivalences', () => {
    test('should confirm suggested equivalence', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Find a suggested equivalence item with confirm button
      const firstSuggested = page.locator("[class*='suggested'], [class*='recommended']").first();
      await expect(firstSuggested).toBeVisible();

      // Look for confirm button within or near the item
      const confirmBtn = firstSuggested
        .locator('button')
        .filter({ hasText: /confirm|approve|accept/i })
        .first();

      await expect(confirmBtn).toBeVisible({ timeout: 2000 });
      await confirmBtn.click();
      await page.waitForTimeout(1000);

      // Verify equivalence is now in confirmed list
      const confirmedItems = page.locator("[class*='confirmed'], [class*='approved']").first();
      await expect(confirmedItems).toBeVisible();
    });

    test('should confirm multiple equivalences', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Find suggested items with confirm buttons
      const suggestedItems = page.locator("[class*='suggested'], [class*='recommended']");
      await expect(suggestedItems.nth(1)).toBeVisible();

      // Confirm first item
      const firstConfirmBtn = suggestedItems
        .nth(0)
        .locator('button')
        .filter({ hasText: /confirm|approve|accept/i })
        .first();

      await expect(firstConfirmBtn).toBeVisible({ timeout: 2000 });
      await firstConfirmBtn.click();
      await page.waitForTimeout(500);

      // Confirm second item
      const secondConfirmBtn = suggestedItems
        .nth(1)
        .locator('button')
        .filter({ hasText: /confirm|approve|accept/i })
        .first();

      await expect(secondConfirmBtn).toBeVisible({ timeout: 2000 });
      await secondConfirmBtn.click();
      await page.waitForTimeout(500);
    });

    test('should show confirmation feedback', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      const firstSuggested = page.locator("[class*='suggested'], [class*='recommended']").first();
      await expect(firstSuggested).toBeVisible({ timeout: 2000 });

      const confirmBtn = firstSuggested
        .locator('button')
        .filter({ hasText: /confirm|approve|accept/i })
        .first();

      await expect(confirmBtn).toBeVisible({ timeout: 2000 });
      await confirmBtn.click();
      await page.waitForTimeout(500);

      // Look for feedback message/toast
      const feedback = page.getByText(/confirmed|approved|success|added/i).first();
      await expect(feedback).toBeVisible({ timeout: 2000 });
    });
  });

  test.describe('Reject Equivalences', () => {
    test('should reject suggested equivalence', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      const firstSuggested = page.locator("[class*='suggested'], [class*='recommended']").first();
      await expect(firstSuggested).toBeVisible();

      const rejectBtn = firstSuggested
        .locator('button')
        .filter({ hasText: /reject|deny|no|dismiss/i })
        .first();

      await expect(rejectBtn).toBeVisible({ timeout: 2000 });
      const initialCount = await page
        .locator("[class*='suggested'], [class*='recommended']")
        .count();
      await rejectBtn.click();
      await page.waitForTimeout(1000);

      // Verify item is removed from suggested list
      const remainingCount = await page
        .locator("[class*='suggested'], [class*='recommended']")
        .count();
      expect(remainingCount).toBeLessThan(initialCount);
    });

    test('should show rejection feedback', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      const firstSuggested = page.locator("[class*='suggested'], [class*='recommended']").first();
      await expect(firstSuggested).toBeVisible({ timeout: 2000 });

      const rejectBtn = firstSuggested
        .locator('button')
        .filter({ hasText: /reject|deny|dismiss/i })
        .first();

      await expect(rejectBtn).toBeVisible({ timeout: 2000 });
      await rejectBtn.click();
      await page.waitForTimeout(500);

      // Look for feedback message
      const feedback = page.getByText(/rejected|dismissed|removed/i).first();
      await expect(feedback).toBeVisible({ timeout: 2000 });
    });
  });

  test.describe('Navigate via Pivot Targets', () => {
    test('should navigate to equivalent item', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for equivalence list
      const firstEquivalent = page
        .locator("[class*='equivalent'], li")
        .filter({ hasText: /equivalent|maps to|corresponds/i })
        .first();

      await expect(firstEquivalent).toBeVisible({ timeout: 5000 });

      const navLink = firstEquivalent.locator("a, button[class*='link']").first();

      await expect(navLink).toBeVisible({ timeout: 5000 });
      await navLink.click();
      await page.waitForTimeout(500);

      // Verify navigation occurred
      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible({ timeout: 5000 });
    });

    test('should highlight selected equivalent in graph', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      const firstEquivalent = page
        .locator("[class*='equivalent'], li")
        .filter({ hasText: /equivalent|maps to/i })
        .first();

      await expect(firstEquivalent).toBeVisible({ timeout: 2000 });
      // Click first equivalent
      await firstEquivalent.click();
      await page.waitForTimeout(500);

      // Look for highlighted node in graph
      const highlightedNodes = page
        .locator("[class*='selected'], [class*='highlighted'], [class*='active']")
        .first();
      await expect(highlightedNodes).toBeVisible();
    });

    test('should show pivot path to equivalent', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for equivalence with path information
      const pathInfo = page.getByText(/via|through|path|route|connection/i).first();
      await expect(pathInfo).toBeVisible({ timeout: 2000 });

      // Look for breadcrumb or path visualization
      const breadcrumb = page.locator("nav, [role='navigation'], [class*='breadcrumb']").first();
      await expect(breadcrumb).toBeVisible({ timeout: 2000 });
    });

    test('should navigate to pivot target and update panel', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Get initial panel content
      const detailPanel = page.locator("aside, [class*='panel'], .w-96").first();
      await expect(detailPanel).toBeVisible();
      const initialText = await detailPanel.textContent();

      const firstEquivalent = page
        .locator("[class*='equivalent'], li")
        .filter({ hasText: /equivalent|maps to/i })
        .first();

      await expect(firstEquivalent).toBeVisible({ timeout: 2000 });
      // Click to navigate to equivalent
      await firstEquivalent.click();
      await page.waitForTimeout(500);

      // Check if panel updated
      const updatedText = await detailPanel.textContent();
      expect(updatedText).not.toBe(initialText);
    });
  });

  test.describe('Equivalence Visual Relationships', () => {
    test('should show equivalence edges in graph', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      // Look for equivalence edges marked with special styling
      const equivalenceEdges = page
        .locator(".react-flow__edges [class*='equivalent'], [class*='maps-to']")
        .first();
      await expect(equivalenceEdges).toBeVisible();
    });

    test('should highlight equivalence relationships when hovering', async ({ page }) => {
      const firstNode = page.locator('.react-flow__nodes > div[data-id]').first();

      await expect(firstNode).toBeVisible({ timeout: 2000 });
      await firstNode.click();
      await page.waitForTimeout(500);

      const firstEquivalent = page
        .locator("[class*='equivalent'], li")
        .filter({ hasText: /equivalent|maps to/i })
        .first();

      await expect(firstEquivalent).toBeVisible({ timeout: 2000 });
      // Hover over equivalent item
      await firstEquivalent.hover();
      await page.waitForTimeout(300);

      // Look for highlighted edges or nodes
      const highlightedElements = page
        .locator("[class*='highlighted'], [style*='highlight']")
        .first();
      await expect(highlightedElements).toBeVisible();
    });
  });
});
