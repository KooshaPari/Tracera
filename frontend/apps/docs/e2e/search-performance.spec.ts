/**
 * Search Performance E2E Tests
 *
 * Tests the instant search functionality and performance.
 */

import { expect, test } from '@playwright/test';

test.describe('Instant Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('search index loads successfully', async ({ page }) => {
    // Check that search index file exists and is accessible
    const response = await page.goto('/search-index.json');
    expect(response?.status()).toBe(200);

    const index = await response?.json();
    expect(index).toBeTruthy();
    expect(index.documents).toBeTruthy();
    expect(index.documents.length).toBeGreaterThan(0);
  });

  test('opens search with Cmd+K', async ({ page }) => {
    // Press Cmd+K (or Ctrl+K on Windows/Linux)
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Search dialog should be visible
    const searchInput = page.getByPlaceholder(/search/i);
    await expect(searchInput).toBeVisible();
    await expect(searchInput).toBeFocused();
  });

  test('performs search and displays results', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Type search query
    const searchInput = page.getByPlaceholder(/search/i);
    await searchInput.fill('getting started');

    // Wait for results (should be fast)
    await page.waitForSelector('[role="listbox"]', { timeout: 500 });

    // Should have results
    const results = page.locator('[role="option"]');
    await expect(results.first()).toBeVisible();

    // Should display search performance metric
    const perfMetric = page.locator(String.raw`text=/\d+ms/`);
    await expect(perfMetric).toBeVisible();

    // Performance should be <100ms
    const perfText = await perfMetric.textContent();
    const perfValue = Number.parseInt(perfText || '0');
    expect(perfValue).toBeLessThan(100);
  });

  test('keyboard navigation works', async ({ page }) => {
    // Open search and enter query
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');
    await page.getByPlaceholder(/search/i).fill('api');

    // Wait for results
    await page.waitForSelector('[role="option"]', { timeout: 500 });

    // First result should be selected
    const firstResult = page.locator('[role="option"]').first();
    await expect(firstResult).toHaveAttribute('aria-selected', 'true');

    // Press down arrow
    await page.keyboard.press('ArrowDown');

    // Second result should now be selected
    const secondResult = page.locator('[role="option"]').nth(1);
    await expect(secondResult).toHaveAttribute('aria-selected', 'true');

    // Press up arrow
    await page.keyboard.press('ArrowUp');

    // First result should be selected again
    await expect(firstResult).toHaveAttribute('aria-selected', 'true');
  });

  test('closes search with Escape', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    const searchInput = page.getByPlaceholder(/search/i);
    await expect(searchInput).toBeVisible();

    // Press Escape
    await page.keyboard.press('Escape');

    // Search should be closed
    await expect(searchInput).not.toBeVisible();
  });

  test('navigates to page on Enter', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Search for specific page
    await page.getByPlaceholder(/search/i).fill('quick start');
    await page.waitForSelector('[role="option"]', { timeout: 500 });

    // Press Enter
    await page.keyboard.press('Enter');

    // Should navigate to the page
    await expect(page).toHaveURL(/\/docs\/.*quick-start/, { timeout: 3000 });
  });

  test('highlights matched text', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Search
    await page.getByPlaceholder(/search/i).fill('architecture');
    await page.waitForSelector('[role="option"]', { timeout: 500 });

    // Should have highlighted text
    const highlighted = page.locator('mark');
    await expect(highlighted.first()).toBeVisible();
  });

  test('shows "no results" message for invalid query', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Search for something that doesn't exist
    await page.getByPlaceholder(/search/i).fill('xyzabc123notfound');

    // Wait a moment for search to complete
    await page.waitForTimeout(200);

    // Should show no results message
    await expect(page.locator('text=/no results/i')).toBeVisible();
  });

  test('requires minimum 2 characters', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Type single character
    await page.getByPlaceholder(/search/i).fill('a');

    // Should show message about minimum characters
    await expect(page.locator('text=/at least 2 characters/i')).toBeVisible();
  });

  test('virtual scrolling handles many results', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Search for common term that will return many results
    await page.getByPlaceholder(/search/i).fill('get');
    await page.waitForSelector('[role="option"]', { timeout: 500 });

    // Get results container
    const resultsContainer = page.locator('[role="listbox"]');

    // Scroll within results
    await resultsContainer.evaluate((el) => {
      el.scrollTop = el.scrollHeight / 2;
    });

    // Wait for virtual scroll to update
    await page.waitForTimeout(100);

    // Results should still be visible (virtual scrolling working)
    await expect(page.locator('[role="option"]').first()).toBeVisible();
  });

  test('search performance metrics are accurate', async ({ page }) => {
    // Open search
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Measure search time
    const startTime = Date.now();

    await page.getByPlaceholder(/search/i).fill('configuration');
    await page.waitForSelector('[role="option"]', { timeout: 500 });

    const endTime = Date.now();
    const actualDuration = endTime - startTime;

    // Get displayed performance metric
    const perfText = await page.locator(String.raw`text=/\d+ms/`).textContent();
    const displayedDuration = Number.parseInt(perfText || '0');

    // Displayed metric should be reasonable (within 100ms of actual)
    expect(Math.abs(displayedDuration - actualDuration)).toBeLessThan(100);

    // Both should be under 100ms target
    expect(displayedDuration).toBeLessThan(100);
    expect(actualDuration).toBeLessThan(500); // More lenient for E2E
  });

  test('search works across different page types', async ({ page }) => {
    // Test searching for different sections
    const queries = ['getting started', 'architecture', 'api', 'guides'];

    for (const query of queries) {
      // Open search (or reuse if already open)
      if (!(await page.getByPlaceholder(/search/i).isVisible())) {
        await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');
      }

      // Clear and search
      await page.getByPlaceholder(/search/i).fill('');
      await page.getByPlaceholder(/search/i).fill(query);

      // Should have results
      await page.waitForSelector('[role="option"]', { timeout: 500 });
      const results = page.locator('[role="option"]');
      await expect(results.first()).toBeVisible();

      // Results should contain the query term
      const firstResultText = await results.first().textContent();
      expect(firstResultText?.toLowerCase()).toContain(query.toLowerCase().split(' ')[0]);
    }
  });

  test('web worker initializes correctly', async ({ page }) => {
    // Check console for worker initialization message
    const logs: string[] = [];

    page.on('console', (msg) => {
      logs.push(msg.text());
    });

    // Open search to trigger worker initialization
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');

    // Wait for worker to initialize
    await page.waitForTimeout(500);

    // Should have initialization log
    const hasInitLog = logs.some(
      (log) => log.includes('Search worker initialized') || log.includes('init'),
    );
    expect(hasInitLog).toBeTruthy();
  });
});
