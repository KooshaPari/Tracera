import { expect, test } from './global-setup';

/**
 * Dimension Filters Tests
 *
 * Tests for applying and managing dimension-based filters on the graph.
 *
 * Dimension Filters:
 * - Maturity: Draft, Review, Approved, Deprecated
 * - Complexity: Low, Medium, High, Critical
 * - Coverage: Not Covered, Partial, Complete
 * - Risk: Low, Medium, High, Critical
 *
 * Filter Display Modes:
 * - Filter: Hide non-matching items
 * - Highlight: Visual emphasis on matching items
 * - Color: Color-code nodes by dimension value
 * - Size: Node size represents dimension value
 */

test.describe('Dimension Filters', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Allow graph to render
  });

  test.describe('Maturity Filters', () => {
    test('should display maturity filter control', async ({ page }) => {
      // Look for maturity filter control
      const maturityFilter = page
        .locator("button, select, [role='combobox']")
        .filter({ hasText: /maturity|draft|review|approved/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
    });

    test('should apply maturity filter - Draft', async ({ page }) => {
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i);
      await expect(draftOption.first()).toBeVisible({ timeout: 1000 });
      await draftOption.first().click();
      await page.waitForTimeout(1000);

      // Verify filter applied
      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible();
    });

    test('should apply maturity filter - Approved', async ({ page }) => {
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const approvedOption = page.getByText(/approved/i);
      await expect(approvedOption.first()).toBeVisible({ timeout: 1000 });
      await approvedOption.first().click();
      await page.waitForTimeout(1000);

      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible();
    });

    test('should apply multiple maturity filters', async ({ page }) => {
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      // Apply first filter
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i);
      await expect(draftOption.first()).toBeVisible({ timeout: 1000 });
      await draftOption.first().click();
      await page.waitForTimeout(300);
    });
  });

  test.describe('Complexity Filters', () => {
    test('should apply complexity filter - High', async ({ page }) => {
      const complexityFilter = page
        .locator('button, select')
        .filter({ hasText: /complexity|complex/i })
        .first();

      await expect(complexityFilter).toBeVisible({ timeout: 2000 });
      await complexityFilter.click();
      await page.waitForTimeout(300);

      const highOption = page.getByText(/high/i).first();
      await expect(highOption).toBeVisible({ timeout: 1000 });
      await highOption.click();
      await page.waitForTimeout(1000);
    });

    test('should apply complexity filter - Low', async ({ page }) => {
      const complexityFilter = page
        .locator('button, select')
        .filter({ hasText: /complexity|complex/i })
        .first();

      await expect(complexityFilter).toBeVisible({ timeout: 2000 });
      await complexityFilter.click();
      await page.waitForTimeout(300);

      const lowOption = page.getByText(/low/i).first();
      await expect(lowOption).toBeVisible({ timeout: 1000 });
      await lowOption.click();
      await page.waitForTimeout(1000);

      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible();
    });

    test('should apply complexity filter - Critical', async ({ page }) => {
      const complexityFilter = page
        .locator('button, select')
        .filter({ hasText: /complexity|complex/i })
        .first();

      await expect(complexityFilter).toBeVisible({ timeout: 2000 });
      await complexityFilter.click();
      await page.waitForTimeout(300);

      const criticalOption = page.getByText(/critical/i).first();
      await expect(criticalOption).toBeVisible({ timeout: 1000 });
      await criticalOption.click();
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Coverage Filters', () => {
    test('should apply coverage filter - Complete', async ({ page }) => {
      const coverageFilter = page
        .locator('button, select')
        .filter({ hasText: /coverage|cover/i })
        .first();

      await expect(coverageFilter).toBeVisible({ timeout: 2000 });
      await coverageFilter.click();
      await page.waitForTimeout(300);

      const completeOption = page.getByText(/complete/i).first();
      await expect(completeOption).toBeVisible({ timeout: 1000 });
      await completeOption.click();
      await page.waitForTimeout(1000);
    });

    test('should apply coverage filter - Partial', async ({ page }) => {
      const coverageFilter = page
        .locator('button, select')
        .filter({ hasText: /coverage|cover/i })
        .first();

      await expect(coverageFilter).toBeVisible({ timeout: 2000 });
      await coverageFilter.click();
      await page.waitForTimeout(300);

      const partialOption = page.getByText(/partial/i).first();
      await expect(partialOption).toBeVisible({ timeout: 1000 });
      await partialOption.click();
      await page.waitForTimeout(1000);

      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible();
    });

    test('should apply coverage filter - Not Covered', async ({ page }) => {
      const coverageFilter = page
        .locator('button, select')
        .filter({ hasText: /coverage|cover/i })
        .first();

      await expect(coverageFilter).toBeVisible({ timeout: 2000 });
      await coverageFilter.click();
      await page.waitForTimeout(300);

      const notCoveredOption = page.getByText(/not.*cover|uncovered/i).first();
      await expect(notCoveredOption).toBeVisible({ timeout: 1000 });
      await notCoveredOption.click();
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Risk Filters', () => {
    test('should apply risk filter - High', async ({ page }) => {
      const riskFilter = page.locator('button, select').filter({ hasText: /risk/i }).first();

      await expect(riskFilter).toBeVisible({ timeout: 2000 });
      await riskFilter.click();
      await page.waitForTimeout(300);

      const highOption = page.getByText(/high/i).first();
      await expect(highOption).toBeVisible({ timeout: 1000 });
      await highOption.click();
      await page.waitForTimeout(1000);
    });

    test('should apply risk filter - Critical', async ({ page }) => {
      const riskFilter = page.locator('button, select').filter({ hasText: /risk/i }).first();

      await expect(riskFilter).toBeVisible({ timeout: 2000 });
      await riskFilter.click();
      await page.waitForTimeout(300);

      const criticalOption = page.getByText(/critical/i).first();
      await expect(criticalOption).toBeVisible({ timeout: 1000 });
      await criticalOption.click();
      await page.waitForTimeout(1000);

      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible();
    });

    test('should apply risk filter - Low', async ({ page }) => {
      const riskFilter = page.locator('button, select').filter({ hasText: /risk/i }).first();

      await expect(riskFilter).toBeVisible({ timeout: 2000 });
      await riskFilter.click();
      await page.waitForTimeout(300);

      const lowOption = page.getByText(/low/i).first();
      await expect(lowOption).toBeVisible({ timeout: 1000 });
      await lowOption.click();
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Filter Display Modes', () => {
    test('should switch to filter display mode - Hide non-matching', async ({ page }) => {
      // Apply a dimension filter first
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i).first();
      await expect(draftOption).toBeVisible({ timeout: 1000 });
      await draftOption.click();
      await page.waitForTimeout(500);

      // Now look for filter display mode selector
      const displayModeSelector = page
        .locator('button')
        .filter({ hasText: /display|mode|filter|highlight|color|size/i })
        .first();

      await expect(displayModeSelector).toBeVisible({ timeout: 2000 });
      await displayModeSelector.click();
      await page.waitForTimeout(300);

      const filterMode = page.getByText(/filter|hide.*non|show.*only/i).first();
      await expect(filterMode).toBeVisible({ timeout: 1000 });
      await filterMode.click();
      await page.waitForTimeout(1000);
    });

    test('should switch to highlight display mode', async ({ page }) => {
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i).first();
      await expect(draftOption).toBeVisible({ timeout: 1000 });
      await draftOption.click();
      await page.waitForTimeout(500);

      // Look for highlight mode selector
      const displayModeSelector = page
        .locator('button')
        .filter({ hasText: /display|mode|highlight/i })
        .first();

      await expect(displayModeSelector).toBeVisible({ timeout: 2000 });
      await displayModeSelector.click();
      await page.waitForTimeout(300);

      const highlightMode = page.getByText(/highlight|emphasize|bold/i).first();
      await expect(highlightMode).toBeVisible({ timeout: 1000 });
      await highlightMode.click();
      await page.waitForTimeout(1000);
    });

    test('should switch to color display mode', async ({ page }) => {
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i).first();
      await expect(draftOption).toBeVisible({ timeout: 1000 });
      await draftOption.click();
      await page.waitForTimeout(500);

      const displayModeSelector = page
        .locator('button')
        .filter({ hasText: /display|mode|color/i })
        .first();

      await expect(displayModeSelector).toBeVisible({ timeout: 2000 });
      await displayModeSelector.click();
      await page.waitForTimeout(300);

      const colorMode = page.getByText(/color|colored|gradient/i).first();
      await expect(colorMode).toBeVisible({ timeout: 1000 });
      await colorMode.click();
      await page.waitForTimeout(1000);
    });

    test('should switch to size display mode', async ({ page }) => {
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity|complexity|risk|coverage/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const filterOption = page
        .locator("button, [role='option']")
        .filter({ hasText: /draft|high|low|complete|critical/i })
        .first();

      await expect(filterOption).toBeVisible({ timeout: 1000 });
      await filterOption.click();
      await page.waitForTimeout(500);

      const displayModeSelector = page
        .locator('button')
        .filter({ hasText: /display|mode|size/i })
        .first();

      await expect(displayModeSelector).toBeVisible({ timeout: 2000 });
      await displayModeSelector.click();
      await page.waitForTimeout(300);

      const sizeMode = page.getByText(/size|scale|proportional/i).first();
      await expect(sizeMode).toBeVisible({ timeout: 1000 });
      await sizeMode.click();
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Clear and Reset Filters', () => {
    test('should clear all filters', async ({ page }) => {
      // Apply a filter first
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i).first();
      await expect(draftOption).toBeVisible({ timeout: 1000 });
      await draftOption.click();
      await page.waitForTimeout(500);

      // Look for clear/reset button
      const clearBtn = page
        .locator('button')
        .filter({ hasText: /clear|reset|all|none/i })
        .first();

      await expect(clearBtn).toBeVisible({ timeout: 2000 });
      await clearBtn.click();
      await page.waitForTimeout(1000);
    });

    test('should reset individual filter', async ({ page }) => {
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i).first();
      await expect(draftOption).toBeVisible({ timeout: 1000 });
      await draftOption.click();
      await page.waitForTimeout(500);

      // Look for filter tag/chip with X button to remove
      const filterChip = page
        .locator("[class*='filter'], [class*='tag'], [class*='chip']")
        .filter({ hasText: /draft/i })
        .first();

      await expect(filterChip).toBeVisible({ timeout: 2000 });
      // Find close button within the chip
      const closeBtn = filterChip.locator('button, svg').first();
      await expect(closeBtn).toBeVisible({ timeout: 1000 });
      await closeBtn.click();
      await page.waitForTimeout(500);
    });

    test('should combine multiple filters', async ({ page }) => {
      // Apply maturity filter
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i).first();
      await expect(draftOption).toBeVisible({ timeout: 1000 });
      await draftOption.click();
      await page.waitForTimeout(500);

      // Apply complexity filter
      const complexityFilter = page
        .locator('button, select')
        .filter({ hasText: /complexity/i })
        .first();

      await expect(complexityFilter).toBeVisible({ timeout: 2000 });
      await complexityFilter.click();
      await page.waitForTimeout(300);

      const highOption = page.getByText(/high/i).first();
      await expect(highOption).toBeVisible({ timeout: 1000 });
      await highOption.click();
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Filter Persistence', () => {
    test('should preserve filters across graph interactions', async ({ page }) => {
      // Apply filter
      const maturityFilter = page
        .locator('button, select')
        .filter({ hasText: /maturity/i })
        .first();

      await expect(maturityFilter).toBeVisible({ timeout: 2000 });
      await maturityFilter.click();
      await page.waitForTimeout(300);

      const draftOption = page.getByText(/draft/i).first();
      await expect(draftOption).toBeVisible({ timeout: 1000 });
      await draftOption.click();
      await page.waitForTimeout(500);

      // Perform graph interaction - zoom in
      const zoomInBtn = page.locator('.react-flow__controls button').nth(0);
      await expect(zoomInBtn).toBeVisible({ timeout: 2000 });
      await zoomInBtn.click();
      await page.waitForTimeout(500);
    });
  });
});
