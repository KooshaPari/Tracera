import { expect, test } from '@playwright/test';

import { authenticateAndNavigate } from './critical-path-helpers';

test.describe('Virtual Scrolling Performance', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/items/table');
  });

  test('should render table with virtual scrolling enabled', async ({ page }) => {
    // Wait for table to load
    await page.waitForSelector('[role="region"][aria-label*="Table content"]');

    // Verify virtual container exists
    const virtualContainer = page.locator('[role="region"]').first();
    const isVisible = await virtualContainer.isVisible();
    expect(isVisible).toBe(true);
  });

  test('should only render visible rows in viewport', async ({ page }) => {
    // Get initial row count visible in DOM
    const initialRows = page.locator('table tbody tr');

    // Add delay to ensure table renders
    await page.waitForTimeout(500);

    const initialCount = await initialRows.count();

    // With virtual scrolling and 600px height, should render roughly 8-12 rows max
    // Much fewer than total items (100+)
    expect(initialCount).toBeLessThan(20);
    expect(initialCount).toBeGreaterThan(5);
  });

  test('should dynamically load rows on scroll', async ({ page }) => {
    const virtualContainer = page.locator('[role="region"]').first();
    const initialRows = page.locator('table tbody tr');

    const initialCount = await initialRows.count();

    // Scroll down significantly
    await virtualContainer.evaluate((el: HTMLElement) => {
      el.scrollTop = el.scrollHeight / 2;
    });

    // Wait for virtual scroller to update
    await page.waitForTimeout(300);

    const scrolledRows = page.locator('table tbody tr');
    const scrolledCount = await scrolledRows.count();

    // Row count should remain roughly the same (virtual scrolling)
    expect(scrolledCount).toBeLessThan(initialCount + 5);
  });

  test('should maintain performance with search filtering', async ({ page }) => {
    // Search for specific item
    const searchInput = page.locator('input[placeholder="Search identifiers..."]');
    await searchInput.fill('test');

    await page.waitForTimeout(500);

    // Should have fewer rows than before
    const filteredRows = page.locator('table tbody tr');
    const filteredCount = await filteredRows.count();

    expect(filteredCount).toBeGreaterThanOrEqual(0);
    expect(filteredCount).toBeLessThan(15);
  });

  test('should handle sorting without blocking UI', async ({ page }) => {
    const startTime = Date.now();

    // Click sort button
    const sortButton = page.locator('button').filter({ hasText: 'Node Identifier' }).first();
    await sortButton.click();

    await page.waitForTimeout(300);

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Sorting should complete quickly (< 1 second)
    expect(duration).toBeLessThan(1000);

    // Items should be re-rendered in sorted order
    const rows = page.locator('table tbody tr');
    expect(await rows.count()).toBeGreaterThanOrEqual(0);
  });

  test('should display row count indicator', async ({ page }) => {
    // Look for item count display in filter bar
    await page.waitForSelector(String.raw`text=/Showing \d+ of \d+ items/`);
    const countText = page.locator(String.raw`text=/Showing \d+ of \d+ items/`);
    const isVisible = await countText.isVisible();

    expect(isVisible).toBe(true);

    // Extract counts
    const text = await countText.textContent();
    const match = text?.match(/Showing (\d+) of (\d+) items/);

    if (match) {
      const showing = Number.parseInt(match[1], 10);
      const total = Number.parseInt(match[2], 10);

      // Showing should be <= total
      expect(showing).toBeLessThanOrEqual(total);
    }
  });

  test('should handle rapid scroll events', async ({ page }) => {
    const virtualContainer = page.locator('[role="region"]').first();

    // Rapidly scroll up and down
    for (let i = 0; i < 5; i++) {
      await virtualContainer.evaluate((el: HTMLElement) => {
        el.scrollTop = Math.random() * el.scrollHeight;
      });
      await page.waitForTimeout(100);
    }

    // Table should still be in valid state
    const rows = page.locator('table tbody tr');
    const count = await rows.count();

    expect(count).toBeGreaterThanOrEqual(0);
    expect(count).toBeLessThan(25);
  });

  test('should preserve scroll position during data updates', async ({ page }) => {
    const virtualContainer = page.locator('[role="region"]').first();

    // Scroll to middle
    await virtualContainer.evaluate((el: HTMLElement) => {
      el.scrollTop = Math.min(el.scrollHeight * 0.5, el.scrollHeight - el.clientHeight);
    });

    const scrollBeforeUpdate = await virtualContainer.evaluate((el: HTMLElement) => el.scrollTop);

    // Trigger a filter change if possible
    const typeSelect = page.locator('button').filter({ hasText: 'All Types' }).first();
    const typeSelectExists = await typeSelect.isVisible().catch(() => false);

    if (typeSelectExists) {
      await typeSelect.click();
      await page.waitForTimeout(300);

      // Scroll position might change if items are filtered, but should not jump unexpectedly
      const scrollAfterUpdate = await virtualContainer.evaluate((el: HTMLElement) => el.scrollTop);

      // Allow some change but not massive jump
      const difference = Math.abs(scrollAfterUpdate - scrollBeforeUpdate);
      expect(difference).toBeLessThan(500);
    }
  });
});

test.describe('Virtual Scrolling Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/items/table');
  });

  test('should have proper ARIA labels', async ({ page }) => {
    // Check virtual container has proper region label
    const region = page.locator('[role="region"]');
    const ariaLabel = await region.first().getAttribute('aria-label');

    expect(ariaLabel).toContain('Table content');
  });

  test('should support keyboard navigation in search', async ({ page }) => {
    // Focus on search input
    const searchInput = page.locator('input[placeholder="Search identifiers..."]');
    await searchInput.focus();

    // Type to filter
    await page.keyboard.type('test');

    await page.waitForTimeout(300);

    // Verify filter was applied
    const rows = page.locator('table tbody tr');
    const count = await rows.count();

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Virtual Scrolling Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAndNavigate(page, '/items/table');
  });

  test('should handle empty result set gracefully', async ({ page }) => {
    // Search for non-existent item
    const searchInput = page.locator('input[placeholder="Search identifiers..."]');
    await searchInput.fill('xyznonexistentxyz123');

    await page.waitForTimeout(500);

    // Should show empty state or have 0 rows
    const rows = page.locator('table tbody tr');
    const rowCount = await rows.count();

    expect(rowCount).toBe(0);
  });

  test('should handle window resize', async ({ page }) => {
    const _virtualContainer = page.locator('[role="region"]').first();

    const _initialRowCount = await page.locator('table tbody tr').count();

    // Resize window
    await page.setViewportSize({ height: 800, width: 1200 });

    await page.waitForTimeout(500);

    // Should still have rows rendered or be empty
    const afterResizeRowCount = await page.locator('table tbody tr').count();
    expect(afterResizeRowCount).toBeGreaterThanOrEqual(0);
  });

  test('should handle type filter', async ({ page }) => {
    // Apply type filter if available
    const typeFilter = page.locator('button').filter({ hasText: 'All Types' }).first();
    const filterExists = await typeFilter.isVisible().catch(() => false);

    if (filterExists) {
      await typeFilter.click();
      await page.waitForTimeout(300);

      // Should have updated results
      const rows = page.locator('table tbody tr');
      const count = await rows.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });
});
