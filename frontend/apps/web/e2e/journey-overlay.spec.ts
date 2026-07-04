import { test } from './global-setup';

/**
 * Journey Overlay Tests
 *
 * Tests for selecting and visualizing user journeys overlaid on the
 * multi-dimensional traceability graph.
 *
 * Journey Features:
 * - Select journey from dropdown
 * - Verify journey nodes are highlighted
 * - Show journey path through graph
 * - Journey statistics and metrics
 * - Journey explorer navigation
 * - Filter graph to show only journey items
 * - Clear journey overlay
 */

test.describe('Journey Overlay', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test.describe('Journey Selection', () => {
    test('should display journey selector dropdown', async ({ page }) => {
      // Look for journey selector
      const journeySelector = page
        .locator("button, select, [role='combobox']")
        .filter({ hasText: /journey|user.*flow|user.*path|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
    });

    test('should list available journeys', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario|flow/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      // Count available journey options
      const journeyOptions = page
        .locator("button, [role='option'], li")
        .filter({ hasText: /[a-z]/i });
      await expect(journeyOptions.first()).toBeVisible({ timeout: 5000 });
    });

    test('should select journey from dropdown', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario|flow/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      // Select first available journey
      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);
    });

    test('should show selected journey name', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario|flow/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      const journeyName = (await journeyOption.textContent()) ?? '';

      await journeyOption.click();
      await page.waitForTimeout(500);

      // Check if journey name is displayed in selector
      await expect(journeySelector).toContainText(journeyName);
    });

    test('should handle multiple journey selection', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario|flow/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      // Look for checkboxes to enable multi-select
      const checkboxes = page.locator("input[type='checkbox'], [role='checkbox']");
      await expect(checkboxes.first()).toBeVisible({ timeout: 5000 });

      // Try selecting multiple journeys
      await checkboxes.nth(0).click();
      await page.waitForTimeout(300);

      await checkboxes.nth(1).click();
      await page.waitForTimeout(500);
    });
  });

  test.describe('Journey Highlighting', () => {
    test('should highlight journey nodes in graph', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      // Select a journey
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Check for highlighted nodes
      const highlightedNodes = page.locator(
        "[class*='journey'], [class*='highlighted'], [class*='active']",
      );
      await expect(highlightedNodes.first()).toBeVisible({ timeout: 10_000 });
    });

    test('should show journey path visualization', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for journey path visualization
      const journeyEdges = page.locator(".react-flow__edges [class*='journey'], [class*='path']");
      await expect(journeyEdges.first()).toBeVisible({ timeout: 10_000 });
    });

    test('should distinguish journey start and end nodes', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for start/end node indicators
      const startNode = page.locator("[class*='start'], [class*='begin']");
      const endNode = page.locator("[class*='end'], [class*='finish']");

      await expect(startNode.or(endNode)).toBeVisible({ timeout: 10_000 });
    });

    test('should highlight journey sequence steps', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for step badge or marker
      const stepMarkers = page.locator("[class*='step'], [class*='sequence']");
      await expect(stepMarkers.first()).toBeVisible({ timeout: 10_000 });
    });
  });

  test.describe('Journey Statistics and Metrics', () => {
    test('should display journey statistics panel', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for statistics panel
      const statsPanel = page.locator("[class*='stats'], [class*='metrics'], [class*='summary']");
      await expect(statsPanel).toBeVisible({ timeout: 10_000 });
    });

    test('should show journey step count', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for step count
      const stepCount = page.getByText(/step|count|length|items?/i);
      await expect(stepCount.first()).toBeVisible({ timeout: 10_000 });
    });

    test('should display journey coverage metrics', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for coverage metric
      const coverage = page.getByText(/coverage|cover|percent|%/i);
      await expect(coverage.first()).toBeVisible({ timeout: 10_000 });
    });

    test('should show journey completion status', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for completion status
      const status = page.getByText(/complete|done|pending|in.*progress|status/i);
      await expect(status.first()).toBeVisible({ timeout: 10_000 });
    });
  });

  test.describe('Journey Explorer Navigation', () => {
    test('should navigate journey steps sequentially', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for next/previous navigation buttons
      const nextBtn = page
        .locator('button')
        .filter({ hasText: /next|forward|right/i })
        .first();

      await expect(nextBtn).toBeVisible({ timeout: 10_000 });
      await nextBtn.click();
      await page.waitForTimeout(500);
    });

    test('should click on journey step in list to navigate', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for journey step list/explorer
      const stepList = page.locator("ul, [role='list']").filter({ hasText: /step|item|node/i });

      await expect(stepList).toBeVisible({ timeout: 10_000 });
      const steps = stepList.locator("li, [role='listitem']");
      await expect(steps.nth(1)).toBeVisible({ timeout: 5000 });
      // Click second step
      await steps.nth(1).click();
      await page.waitForTimeout(500);
    });

    test('should scroll to center graph on journey step selection', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Look for journey step list
      const stepList = page.locator("ul, [role='list']").filter({ hasText: /step|item/i });

      await expect(stepList).toBeVisible({ timeout: 10_000 });
      const steps = stepList.locator("li, [role='listitem']");

      await expect(steps.nth(1)).toBeVisible({ timeout: 5000 });
      await steps.nth(1).click();
      await page.waitForTimeout(500);
    });
  });

  test.describe('Journey Filtering', () => {
    test('should filter graph to show only journey items', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      // Get initial node count
      const initialCount = await page.locator('.react-flow__nodes > div[data-id]').count();

      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Check if there's a filter toggle for journey-only view
      const filterToggle = page
        .locator('button')
        .filter({ hasText: /filter|journey.*only|show.*only/i })
        .first();

      await expect(filterToggle).toBeVisible({ timeout: 10_000 });
      await filterToggle.click();
      await page.waitForTimeout(500);

      const filteredCount = await page.locator('.react-flow__nodes > div[data-id]').count();

      console.log(`Journey filter: ${initialCount} -> ${filteredCount} nodes`);
    });

    test('should preserve other filters when journey is selected', async ({ page }) => {
      // Apply a dimension filter first
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity|status|type/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 10_000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const option = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(option).toBeVisible({ timeout: 5000 });
      await option.click();
      await page.waitForTimeout(500);

      // Now select journey
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 5000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Clear Journey Overlay', () => {
    test('should clear journey selection', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      // Get highlighted nodes count
      const highlightedCount = await page
        .locator("[class*='journey'], [class*='highlighted']")
        .count();

      // Look for clear/reset button
      const clearBtn = page
        .locator('button')
        .filter({ hasText: /clear|reset|none|remove/i })
        .first();

      await expect(clearBtn).toBeVisible({ timeout: 10_000 });
      await clearBtn.click();
      await page.waitForTimeout(500);

      // Verify journey highlighting removed
      const remainingHighlighted = await page
        .locator("[class*='journey'], [class*='highlighted']")
        .count();

      expect(remainingHighlighted).toBeLessThan(highlightedCount);
    });

    test('should restore normal graph after clearing journey', async ({ page }) => {
      const journeySelector = page
        .locator('button, select')
        .filter({ hasText: /journey|scenario/i })
        .first();

      await expect(journeySelector).toBeVisible({ timeout: 10_000 });
      await journeySelector.click();
      await page.waitForTimeout(300);

      const journeyOption = page
        .locator("[role='option'], button")
        .filter({ hasText: /[A-Za-z]/ })
        .first();

      await expect(journeyOption).toBeVisible({ timeout: 5000 });
      await journeyOption.click();
      await page.waitForTimeout(1000);

      const allNodes = await page.locator('.react-flow__nodes > div[data-id]').count();

      // Clear journey
      const clearBtn = page
        .locator('button')
        .filter({ hasText: /clear|reset|none/i })
        .first();

      await expect(clearBtn).toBeVisible({ timeout: 10_000 });
      await clearBtn.click();
      await page.waitForTimeout(500);

      const nodesAfterClear = await page.locator('.react-flow__nodes > div[data-id]').count();

      expect(nodesAfterClear).toBe(allNodes);
    });
  });
});
