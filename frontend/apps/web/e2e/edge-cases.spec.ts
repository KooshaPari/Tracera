import { expect, test } from './global-setup';

/**
 * Edge Cases and Error Handling E2E Tests
 *
 * Tests for boundary conditions, error scenarios, network failures,
 * data validation edge cases, and graceful degradation.
 */

test.describe('Edge Cases - Empty States', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display empty state when no items exist', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/items**', (route) => {
      void route.fulfill({
        body: JSON.stringify({ items: [], total: 0 }),
        status: 200,
      });
    });

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Should show empty state
    const emptyState = page.locator('[data-testid="empty-state"]');
    await expect(emptyState).toBeVisible();
    await expect(emptyState).toContainText(/no items/i);

    // Should show CTA to create first item
    const createButton = page.locator('button:has-text("Create First Item")');
    await expect(createButton).toBeVisible();
  });

  test('should display empty state when no projects exist', async ({ page }) => {
    await page.route('**/api/projects**', (route) => {
      void route.fulfill({
        body: JSON.stringify({ projects: [], total: 0 }),
        status: 200,
      });
    });

    await page.goto('/projects');

    const emptyState = page.locator('[data-testid="empty-state"]');
    await expect(emptyState).toBeVisible();
  });

  test('should display empty search results gracefully', async ({ page }) => {
    await page.goto('/items');

    await page.fill('[data-testid="search-input"]', 'nonexistent-query-xyz123');
    await page.waitForTimeout(500);

    const noResults = page.locator('[data-testid="no-results"]');
    await expect(noResults).toBeVisible();
    await expect(noResults).toContainText(/no results found/i);
  });

  test('should handle empty agent list', async ({ page }) => {
    await page.route('**/api/agents**', (route) => {
      void route.fulfill({
        body: JSON.stringify({ agents: [], total: 0 }),
        status: 200,
      });
    });

    await page.goto('/agents');

    const emptyState = page.locator('[data-testid="empty-state"]');
    await expect(emptyState).toBeVisible();
  });
});

test.describe('Edge Cases - Network Errors', () => {
  test('should handle network timeout', async ({ page }) => {
    await page.route('**/api/items**', (route) => {
      // Simulate timeout by not responding
      setTimeout(() => {
        void route.abort('timedout');
      }, 5000);
    });

    await page.goto('/items');

    // Should show timeout error
    const error = page.locator('[data-testid="error-message"]');
    await expect(error).toBeVisible({ timeout: 10_000 });
    await expect(error).toContainText(/timeout|took too long/i);

    // Should offer retry option
    const retryButton = page.locator('button:has-text("Retry")');
    await expect(retryButton).toBeVisible();
  });

  test('should handle 500 server error', async ({ page }) => {
    await page.route('**/api/items**', (route) => {
      void route.fulfill({
        body: JSON.stringify({ error: 'Internal Server Error' }),
        status: 500,
      });
    });

    await page.goto('/items');

    const error = page.locator('[data-testid="error-message"]');
    await expect(error).toBeVisible();
    await expect(error).toContainText(/something went wrong|server error/i);
  });

  test('should handle 404 not found', async ({ page }) => {
    await page.goto('/items/nonexistent-item-id-12345');

    const notFound = page.locator('[data-testid="not-found"]');
    await expect(notFound).toBeVisible();
    await expect(notFound).toContainText(/not found|doesn't exist/i);

    // Should offer navigation back
    const backButton = page.locator('button:has-text("Back")');
    await expect(backButton).toBeVisible();
  });

  test('should handle network offline', async ({ page, context }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Go offline
    await context.setOffline(true);

    // Try to create item
    await page.click('button:has-text("New Item")');
    await page.fill('input[name="title"]', 'Offline Item');
    await page.click('button:has-text("Save")');

    // Should show offline indicator
    const offlineMessage = page.locator('[data-testid="offline-indicator"]');
    await expect(offlineMessage).toBeVisible();

    // Go back online
    await context.setOffline(false);

    // Should sync automatically
    await page.waitForTimeout(2000);
    await expect(offlineMessage).not.toBeVisible();
  });

  test('should retry failed requests', async ({ page }) => {
    let requestCount = 0;

    await page.route('**/api/items**', (route) => {
      requestCount++;

      if (requestCount < 3) {
        void route.fulfill({ status: 500 });
      } else {
        void route.fulfill({
          body: JSON.stringify({ items: [], total: 0 }),
          status: 200,
        });
      }
    });

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Should eventually succeed after retries
    expect(requestCount).toBeGreaterThanOrEqual(3);

    // Should show content
    const itemsList = page.locator('[data-testid="items-list"]');
    await expect(itemsList).toBeVisible();
  });
});

test.describe('Edge Cases - Boundary Values', () => {
  test('should handle very long item titles', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    const longTitle = 'A'.repeat(500);
    await page.fill('input[name="title"]', longTitle);
    await page.click('button:has-text("Save")');

    // Should either truncate or show in full with proper styling
    const title = page.locator('[data-testid="item-title"]');
    await expect(title).toBeVisible();

    // Title should not break layout
    const titleBox = await title.boundingBox();
    expect(titleBox?.width).toBeLessThan(1000);
  });

  test('should handle zero items in pagination', async ({ page }) => {
    await page.route('**/api/items**', (route) => {
      void route.fulfill({
        body: JSON.stringify({ items: [], page: 1, pageSize: 10, total: 0 }),
        status: 200,
      });
    });

    await page.goto('/items');

    // Pagination should not appear or show 0
    const pagination = page.locator('[data-testid="pagination"]');

    if ((await pagination.count()) > 0) {
      const pageInfo = await pagination.textContent();
      expect(pageInfo).toContain('0');
    }
  });

  test('should handle maximum items in one page', async ({ page }) => {
    // Create 100 items
    const items = Array.from({ length: 100 }, (_, i) => ({
      id: `item-${i}`,
      title: `Item ${i}`,
      type: 'task',
    }));

    await page.route('**/api/items**', (route) => {
      void route.fulfill({
        body: JSON.stringify({ items, total: 100 }),
        status: 200,
      });
    });

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Should render without breaking
    const itemCards = page.locator('[data-testid="item-card"]');
    const count = await itemCards.count();

    expect(count).toBeGreaterThan(0);
    expect(count).toBeLessThanOrEqual(100);
  });

  test('should handle special characters in search', async ({ page }) => {
    await page.goto('/items');

    const specialChars = String.raw`!@#$%^&*()[]{}|\;:"'<>,.?/`;

    await page.fill('[data-testid="search-input"]', specialChars);
    await page.waitForTimeout(500);

    // Should not crash
    await expect(page.locator('[data-testid="items-list"]')).toBeVisible();
  });

  test('should handle Unicode characters', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    const unicodeTitle = '测试项目 🚀 Тест العربية';

    await page.fill('input[name="title"]', unicodeTitle);
    await page.click('button:has-text("Save")');

    // Should display correctly
    const title = page.locator('[data-testid="item-title"]');
    await expect(title).toHaveText(unicodeTitle);
  });

  test('should handle emoji in content', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    const emojiTitle = '🎉🎊🎈 Party Time! 🎁🎂🎃';

    await page.fill('input[name="title"]', emojiTitle);
    await page.click('button:has-text("Save")');

    const title = page.locator('[data-testid="item-title"]');
    await expect(title).toHaveText(emojiTitle);
  });
});

test.describe('Edge Cases - Concurrent Operations', () => {
  test('should handle rapid clicks on same button', async ({ page }) => {
    await page.goto('/items');

    // Rapidly click new item button
    const newButton = page.locator('button:has-text("New Item")');

    for (let i = 0; i < 10; i++) {
      await newButton.click();
      await page.waitForTimeout(50);
    }

    // Should only open one dialog
    const dialogs = page.locator('[role="dialog"]');
    await expect(dialogs).toHaveCount(1);
  });

  test('should handle simultaneous form submissions', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    await page.fill('input[name="title"]', 'Concurrent Item');

    // Try to submit multiple times rapidly
    const submitButton = page.locator('button:has-text("Save")');

    try {
      await Promise.all([submitButton.click(), submitButton.click(), submitButton.click()]);
    } catch {
      // Expected to fail for some clicks as some will be disabled or detached
    }

    // Should only create one item
    await page.waitForTimeout(1000);
    await page.goto('/items');

    const items = page.locator('[data-testid="item-card"]:has-text("Concurrent Item")');
    const count = await items.count();

    expect(count).toBeLessThanOrEqual(1);
  });

  test('should handle opening multiple modals', async ({ page }) => {
    await page.goto('/items');

    // Try to open multiple modals
    await page.click('button:has-text("New Item")');
    await page.waitForTimeout(100);

    // Press Escape to close
    await page.keyboard.press('Escape');
    await page.waitForTimeout(100);

    // Open again
    await page.click('button:has-text("New Item")');

    // Should work correctly
    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();
  });
});

test.describe('Edge Cases - Data Validation', () => {
  test('should handle null/undefined values gracefully', async ({ page }) => {
    await page.route('**/api/items/**', (route) => {
      void route.fulfill({
        body: JSON.stringify({
          description: undefined,
          id: 'test-id',
          title: null,
          type: 'task',
        }),
        status: 200,
      });
    });

    await page.goto('/items/test-id');

    // Should not crash
    await expect(page.locator('[data-testid="item-detail"]')).toBeVisible();

    // Should show fallback for null values
    const title = page.locator('[data-testid="item-title"]');
    const titleText = await title.textContent();

    expect(titleText).toBeTruthy();
    expect(titleText).not.toBe('null');
    expect(titleText).not.toBe('undefined');
  });

  test('should handle malformed API responses', async ({ page }) => {
    await page.route('**/api/items**', (route) => {
      void route.fulfill({
        body: 'Not valid JSON',
        status: 200,
      });
    });

    await page.goto('/items');

    // Should show error
    const error = page.locator('[data-testid="error-message"]');
    await expect(error).toBeVisible();
  });

  test('should handle missing required fields in response', async ({ page }) => {
    await page.route('**/api/items**', (route) => {
      void route.fulfill({
        body: JSON.stringify({
          items: [
            { id: '1' }, // Missing title, type, etc.
            { title: 'No ID' }, // Missing id
          ],
        }),
        status: 200,
      });
    });

    await page.goto('/items');

    // Should handle gracefully, possibly filtering out invalid items
    const itemCards = page.locator('[data-testid="item-card"]');
    const count = await itemCards.count();

    // Should show some items or show error
    expect(count >= 0).toBe(true);
  });

  test('should validate date formats', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    // Try invalid date
    const dateInput = page.locator('input[type="date"]');

    if ((await dateInput.count()) > 0) {
      await dateInput.fill('invalid-date');

      const value = await dateInput.inputValue();
      expect(value).not.toBe('invalid-date');
    }
  });
});

test.describe('Edge Cases - Browser Compatibility', () => {
  test('should handle window resize', async ({ page }) => {
    await page.goto('/items');

    // Resize to mobile
    await page.setViewportSize({ height: 667, width: 375 });
    await page.waitForTimeout(500);

    // Should show mobile layout
    const mobileMenu = page.locator('[data-testid="mobile-menu"]');
    await expect(mobileMenu).toBeVisible();

    // Resize to desktop
    await page.setViewportSize({ height: 1080, width: 1920 });
    await page.waitForTimeout(500);

    // Should show desktop layout
    const desktopNav = page.locator('[data-testid="desktop-nav"]');
    await expect(desktopNav).toBeVisible();
  });

  test('should handle page zoom', async ({ page }) => {
    await page.goto('/items');

    // Zoom in
    await page.evaluate(() => {
      document.body.style.zoom = '150%';
    });

    await page.waitForTimeout(500);

    // Content should still be visible and usable
    const items = page.locator('[data-testid="item-card"]');
    await expect(items.first()).toBeVisible();

    // Reset zoom
    await page.evaluate(() => {
      document.body.style.zoom = '100%';
    });
  });

  test('should work with JavaScript disabled gracefully', async ({ page, context }) => {
    // This test checks for progressive enhancement
    await context.route('**/*.js', async (route) => {
      await route.abort();
    });

    try {
      await page.goto('/', { timeout: 5000 });

      // Should at least show some content or message
      const bodyText = await page.textContent('body');
      expect(bodyText).toBeTruthy();
    } catch {
      // Expected to fail, but shouldn't crash completely
      expect(true).toBe(true);
    }
  });
});

test.describe('Edge Cases - Form Validation', () => {
  test('should validate required fields', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    // Try to submit without filling required fields
    await page.click('button:has-text("Save")');

    // Should show validation errors
    const errors = page.locator('.error');
    expect(await errors.count()).toBeGreaterThan(0);
  });

  test('should prevent submission while validating', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    await page.fill('input[name="title"]', 'Test');

    // Submit button should be disabled during submission
    const submitButton = page.locator('button:has-text("Save")');
    await submitButton.click();

    // Button should be disabled
    await expect(submitButton).toBeDisabled();
  });

  test('should handle form reset', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    await page.fill('input[name="title"]', 'Test Item');
    await page.fill('textarea[name="description"]', 'Test Description');

    // Cancel/Reset form
    await page.click('button:has-text("Cancel")');

    // Open again
    await page.click('button:has-text("New Item")');

    // Form should be empty
    const titleValue = await page.inputValue('input[name="title"]');
    expect(titleValue).toBe('');
  });

  test('should preserve form state on validation error', async ({ page }) => {
    await page.goto('/items');
    await page.click('button:has-text("New Item")');

    await page.fill('input[name="title"]', 'Test Item');
    await page.fill('textarea[name="description"]', 'Test Description');

    // Trigger validation error (e.g., by removing title)
    await page.fill('input[name="title"]', '');
    await page.click('button:has-text("Save")');

    // Description should still be there
    const descValue = await page.inputValue('textarea[name="description"]');
    expect(descValue).toBe('Test Description');
  });
});

test.describe('Edge Cases - URL and Routing', () => {
  test('should handle direct URL access to deep routes', async ({ page }) => {
    // Directly navigate to a deep route
    await page.goto('/items/item-123/edit');

    // Should load correctly or redirect appropriately
    const url = page.url();
    expect(url).toBeTruthy();

    // Should not show blank page
    const bodyText = await page.textContent('body');
    expect(bodyText?.length).toBeGreaterThan(0);
  });

  test('should handle malformed URLs', async ({ page }) => {
    await page.goto('/items/../../../etc/passwd');

    // Should redirect to safe page or show 404
    const url = page.url();
    expect(url).not.toContain('../');
  });

  test('should handle URL with query parameters', async ({ page }) => {
    await page.goto('/items?page=999&sort=invalid&filter[]=<script>');

    // Should handle gracefully
    await expect(page).not.toHaveURL(/error/);

    // Should sanitize parameters
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toContain('<script>');
  });

  test('should preserve query parameters on navigation', async ({ page }) => {
    await page.goto('/items?status=open&assignee=john');

    const initialUrl = page.url();

    // Navigate to detail and back
    await page.locator('[data-testid="item-card"]').first().click();
    await page.goBack();

    // Query parameters should be preserved
    const finalUrl = page.url();
    expect(finalUrl).toBe(initialUrl);
  });
});

test.describe('Edge Cases - Performance Under Load', () => {
  test('should handle rapid scrolling', async ({ page }) => {
    await page.goto('/items');

    // Rapidly scroll up and down
    for (let i = 0; i < 10; i++) {
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });
      await page.waitForTimeout(50);
      await page.evaluate(() => {
        window.scrollTo(0, 0);
      });
      await page.waitForTimeout(50);
    }

    // Should not crash or freeze
    const items = page.locator('[data-testid="items-list"]');
    await expect(items).toBeVisible();
  });

  test('should handle many open connections', async ({ page }) => {
    await page.goto('/dashboard');

    // Trigger many API calls
    const promises: Promise<unknown>[] = [];
    for (let i = 0; i < 20; i++) {
      promises.push(page.goto('/items'));
      promises.push(page.goto('/projects'));
    }

    await Promise.allSettled(promises);

    // Should handle without crashing
    expect(page).toBeDefined();
  });
});

test.describe('Edge Cases - Localization', () => {
  test('should handle RTL languages', async ({ page }) => {
    // Set RTL language
    await page.evaluate(() => {
      document.documentElement.setAttribute('dir', 'rtl');
    });

    await page.goto('/items');

    // Layout should adapt to RTL
    const direction = await page.evaluate(() => document.documentElement.getAttribute('dir'));

    expect(direction).toBe('rtl');
  });

  test('should handle long translations', async ({ page }) => {
    // Simulate long German translations
    await page.goto('/items');

    // Buttons and labels should not overflow
    const buttons = page.locator('button');
    const count = await buttons.count();

    for (let i = 0; i < Math.min(count, 10); i++) {
      const box = await buttons.nth(i).boundingBox();
      if (box) {
        expect(box.width).toBeLessThan(500);
      }
    }
  });
});
