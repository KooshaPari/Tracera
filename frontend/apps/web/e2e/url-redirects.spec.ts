import { expect, test } from '@playwright/test';

/**
 * E2E tests for backward compatibility URL redirects
 * Ensures old bookmarks and links continue to work with new URL structure
 */

test.describe('URL Redirects - Backward Compatibility', () => {
  test.beforeEach(async ({ page }) => {
    // Intercept API calls to provide mock data
    await page.route('**/api/v1/items/*', async (route) => {
      const url = route.request().url();
      const itemId = url.split('/').pop();

      if (itemId === 'valid-item-123') {
        await route.fulfill({
          body: JSON.stringify({
            created_at: '2024-01-01T00:00:00Z',
            description: 'Test description',
            id: 'valid-item-123',
            priority: 'high',
            project_id: 'project-456',
            status: 'todo',
            title: 'Test Item',
            type: 'epic',
            updated_at: '2024-01-01T00:00:00Z',
            version: 1,
            view: 'FEATURE',
          }),
          contentType: 'application/json',
          status: 200,
        });
      } else if (itemId === 'invalid-item-999') {
        await route.fulfill({
          body: JSON.stringify({ error: 'Item not found' }),
          contentType: 'application/json',
          status: 404,
        });
      } else {
        await route.continue();
      }
    });

    // Mock projects API
    await page.route('**/api/v1/projects', async (route) => {
      await route.fulfill({
        body: JSON.stringify({
          items: [
            {
              created_at: '2024-01-01T00:00:00Z',
              description: 'Test project description',
              id: 'project-456',
              name: 'Test Project',
              updated_at: '2024-01-01T00:00:00Z',
            },
          ],
          total: 1,
        }),
        contentType: 'application/json',
        status: 200,
      });
    });
  });

  test('should redirect /items/:itemId to new URL format', async ({ page }) => {
    // Navigate to old URL format
    await page.goto('http://localhost:5173/items/valid-item-123');

    // Wait for redirect
    await page.waitForURL('**/projects/project-456/views/feature/valid-item-123', {
      timeout: 5000,
    });

    // Verify we're on the correct page
    expect(page.url()).toContain('/projects/project-456/views/feature/valid-item-123');

    // Verify the page loaded correctly (not showing error)
    await expect(page.locator('text=Item Not Found')).not.toBeVisible();
  });

  test('should show loading state during redirect', async ({ page }) => {
    // Navigate to old URL format
    const navigationPromise = page.goto('http://localhost:5173/items/valid-item-123');

    // Should show loading spinner
    await expect(page.locator('text=Redirecting')).toBeVisible();

    await navigationPromise;
  });

  test('should handle item not found gracefully', async ({ page }) => {
    // Navigate to old URL with invalid item
    await page.goto('http://localhost:5173/items/invalid-item-999');

    // Wait for error message
    await expect(page.locator('text=Item Not Found')).toBeVisible();
    await expect(page.locator('text=Back to Projects')).toBeVisible();
  });

  test('should convert uppercase view type to lowercase in URL', async ({ page }) => {
    // Mock item with uppercase view type
    await page.route('**/api/v1/items/test-item', async (route) => {
      await route.fulfill({
        body: JSON.stringify({
          id: 'test-item',
          project_id: 'project-123',
          view: 'TEST', // Uppercase
          type: 'test_case',
          title: 'Test Case',
          status: 'todo',
          priority: 'high',
          version: 1,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        }),
        contentType: 'application/json',
        status: 200,
      });
    });

    await page.goto('http://localhost:5173/items/test-item');

    // Should convert to lowercase
    await page.waitForURL('**/projects/project-123/views/test/test-item', {
      timeout: 5000,
    });

    expect(page.url()).toContain('/views/test/');
    expect(page.url()).not.toContain('/views/TEST/');
  });

  test('should redirect /items to /projects', async ({ page }) => {
    await page.goto('http://localhost:5173/items');

    // Wait for redirect
    await page.waitForURL('**/projects', { timeout: 5000 });

    expect(page.url()).toMatch(/\/projects\/?$/);
  });

  test('should redirect /graph to /projects with hint', async ({ page }) => {
    await page.goto('http://localhost:5173/graph');

    // Should show redirect message
    await expect(page.locator('text=Redirecting to projects')).toBeVisible();
    await expect(page.locator('text=Please select a project to view its graph')).toBeVisible();

    // Wait for redirect
    await page.waitForURL('**/projects', { timeout: 5000 });

    expect(page.url()).toMatch(/\/projects\/?$/);
  });

  test('should redirect /search to /projects with search hint', async ({ page }) => {
    await page.goto('http://localhost:5173/search');

    // Should show redirect message and hint
    await expect(page.locator('text=Redirecting to projects')).toBeVisible();
    await expect(page.locator('text=Use Cmd+K or Ctrl+K to open global search')).toBeVisible();

    // Wait for redirect
    await page.waitForURL('**/projects', { timeout: 5000 });

    expect(page.url()).toMatch(/\/projects\/?$/);
  });

  test('should not allow back navigation to old URL after redirect', async ({ page }) => {
    // Start from home
    await page.goto('http://localhost:5173/');

    // Navigate to old URL
    await page.goto('http://localhost:5173/items/valid-item-123');

    // Wait for redirect
    await page.waitForURL('**/projects/project-456/views/feature/valid-item-123', {
      timeout: 5000,
    });

    // Go back
    await page.goBack();

    // Should go back to home, not to /items/valid-item-123
    expect(page.url()).toMatch(/\/(projects)?\/?$/);
    expect(page.url()).not.toContain('/items/');
  });

  test('should preserve item context after redirect', async ({ page }) => {
    await page.goto('http://localhost:5173/items/valid-item-123');

    // Wait for redirect
    await page.waitForURL('**/projects/project-456/views/feature/valid-item-123', {
      timeout: 5000,
    });

    // Verify URL parameters are correct
    const url = new URL(page.url());
    expect(url.pathname).toContain('/projects/project-456');
    expect(url.pathname).toContain('/views/feature');
    expect(url.pathname).toContain('/valid-item-123');
  });
});

test.describe('Accessibility - Redirect Pages', () => {
  test('should have accessible loading state', async ({ page }) => {
    await page.goto('http://localhost:5173/items');

    // Loading message should be accessible
    const loadingMessage = page.locator('text=Redirecting to projects');
    await expect(loadingMessage).toBeVisible();

    // Should have proper ARIA attributes or semantic HTML
    const parent = loadingMessage.locator('..');
    await expect(parent).toBeVisible();
  });

  test('should have accessible error state', async ({ page }) => {
    await page.route('**/api/v1/items/error-item', async (route) => {
      await route.fulfill({
        body: JSON.stringify({ error: 'Not found' }),
        contentType: 'application/json',
        status: 404,
      });
    });

    await page.goto('http://localhost:5173/items/error-item');

    // Error heading should be semantic
    const errorHeading = page.locator("h1:has-text('Item Not Found')");
    await expect(errorHeading).toBeVisible();

    // Link should be keyboard accessible
    const backLink = page.locator("a:has-text('Back to Projects')");
    await expect(backLink).toBeVisible();

    // Test keyboard navigation
    await backLink.focus();
    await expect(backLink).toBeFocused();
  });
});
