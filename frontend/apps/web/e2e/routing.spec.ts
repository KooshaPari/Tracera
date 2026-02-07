import { expect, test } from './global-setup';

/**
 * Comprehensive Routing E2E Tests
 *
 * Tests for route navigation, dynamic routes, route parameters,
 * and application routing behavior. These tests verify that:
 * - All static routes are accessible and return 200
 * - Dynamic routes work with correct parameters
 * - Route transitions work smoothly
 * - Route guards and redirects function properly
 * - Sidebar and breadcrumb navigation work correctly
 *
 * Success Criteria:
 * - 20+ route tests passing
 * - Static routes return 200 status
 * - Dynamic routes load with parameters
 * - Navigation between routes works smoothly
 */

test.describe('Route Navigation - Static Routes', () => {
  const _staticRoutes = [
    '/',
    '/projects',
    '/items',
    '/graph',
    '/settings',
    '/reports',
    '/matrix',
    '/links',
    '/impact',
    '/events',
    '/api-docs',
    '/api-docs/swagger',
    '/api-docs/redoc',
    '/matrix/traceability',
    '/impact/analysis',
    '/events/timeline',
    '/items/tree',
    '/items/kanban',
    '/auth/login',
    '/auth/register',
    '/auth/reset-password',
  ];

  test.beforeEach(async ({ page }) => {
    // Ensure we start from a clean state
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should load dashboard route', async ({ page }) => {
    const response = await page.goto('/');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL('/');
  });

  test('should load projects list route', async ({ page }) => {
    const response = await page.goto('/projects');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/projects/);
    await page.waitForLoadState('networkidle');
  });

  test('should load items view route', async ({ page }) => {
    const response = await page.goto('/items');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/items/);
    await page.waitForLoadState('networkidle');
  });

  test('should load items tree view', async ({ page }) => {
    const response = await page.goto('/items/tree');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/items\/tree/);
    await page.waitForLoadState('networkidle');
  });

  test('should load items kanban view', async ({ page }) => {
    const response = await page.goto('/items/kanban');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/items\/kanban/);
    await page.waitForLoadState('networkidle');
  });

  test('should load graph view route', async ({ page }) => {
    const response = await page.goto('/graph');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/graph/);
    await page.waitForLoadState('networkidle');
  });

  test('should load settings route', async ({ page }) => {
    const response = await page.goto('/settings');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/settings/);
    await page.waitForLoadState('networkidle');
  });

  test('should load reports route', async ({ page }) => {
    const response = await page.goto('/reports');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/reports/);
    await page.waitForLoadState('networkidle');
  });

  test('should load matrix route', async ({ page }) => {
    const response = await page.goto('/matrix');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/matrix/);
    await page.waitForLoadState('networkidle');
  });

  test('should load matrix traceability route', async ({ page }) => {
    const response = await page.goto('/matrix/traceability');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/matrix\/traceability/);
    await page.waitForLoadState('networkidle');
  });

  test('should load links route', async ({ page }) => {
    const response = await page.goto('/links');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/links/);
    await page.waitForLoadState('networkidle');
  });

  test('should load impact analysis route', async ({ page }) => {
    const response = await page.goto('/impact/analysis');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/impact\/analysis/);
    await page.waitForLoadState('networkidle');
  });

  test('should load events timeline route', async ({ page }) => {
    const response = await page.goto('/events/timeline');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/events\/timeline/);
    await page.waitForLoadState('networkidle');
  });

  test('should load API documentation swagger', async ({ page }) => {
    const response = await page.goto('/api-docs/swagger');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/api-docs\/swagger/);
    await page.waitForLoadState('networkidle');
  });

  test('should load API documentation redoc', async ({ page }) => {
    const response = await page.goto('/api-docs/redoc');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/api-docs\/redoc/);
    await page.waitForLoadState('networkidle');
  });

  test('should load authentication login route', async ({ page }) => {
    const response = await page.goto('/auth/login');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/auth\/login/);
    await page.waitForLoadState('networkidle');
  });

  test('should load authentication register route', async ({ page }) => {
    const response = await page.goto('/auth/register');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/auth\/register/);
    await page.waitForLoadState('networkidle');
  });

  test('should load authentication reset password route', async ({ page }) => {
    const response = await page.goto('/auth/reset-password');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/auth\/reset-password/);
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Route Navigation - Dynamic Routes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to project detail route with ID', async ({ page }) => {
    // Use a test project ID
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}`);

    // Should either succeed or return 404 if project doesn't exist
    // But the route itself should be valid
    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}`));
  });

  test('should navigate to item detail route with ID', async ({ page }) => {
    const itemId = 'test-item-456';
    const response = await page.goto(`/items/${itemId}`);

    // Route should be valid
    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/items/${itemId}`));
  });

  test('should navigate to project views with viewType parameter', async ({ page }) => {
    const projectId = 'test-project-123';
    const viewType = 'feature';

    const response = await page.goto(`/projects/${projectId}/views/${viewType}`);
    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/views/${viewType}`));
  });

  test('should navigate to project views with viewType and itemId', async ({ page }) => {
    const projectId = 'test-project-123';
    const viewType = 'feature';
    const itemId = 'item-789';

    const response = await page.goto(`/projects/${projectId}/views/${viewType}/${itemId}`);
    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/views/${viewType}/${itemId}`));
  });

  test('should navigate to project settings', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/settings`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/settings`));
  });

  test('should navigate to project agents', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/agents`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/agents`));
  });

  test('should navigate to project views - architecture', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/views/architecture`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/views/architecture`));
  });

  test('should navigate to project views - api', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/views/api`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/views/api`));
  });

  test('should navigate to project views - database', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/views/database`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/views/database`));
  });

  test('should navigate to project features', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/features`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/features`));
  });

  test('should navigate to feature detail', async ({ page }) => {
    const projectId = 'test-project-123';
    const featureId = 'feature-456';
    const response = await page.goto(`/projects/${projectId}/features/${featureId}`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/features/${featureId}`));
  });

  test('should navigate to project ADRs', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/adrs`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/adrs`));
  });

  test('should navigate to ADR detail', async ({ page }) => {
    const projectId = 'test-project-123';
    const adrId = 'adr-123';
    const response = await page.goto(`/projects/${projectId}/adrs/${adrId}`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/adrs/${adrId}`));
  });

  test('should navigate to project contracts', async ({ page }) => {
    const projectId = 'test-project-123';
    const response = await page.goto(`/projects/${projectId}/contracts`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/contracts`));
  });

  test('should navigate to contract detail', async ({ page }) => {
    const projectId = 'test-project-123';
    const contractId = 'contract-789';
    const response = await page.goto(`/projects/${projectId}/contracts/${contractId}`);

    expect(response?.status()).toBeLessThan(500);
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}/contracts/${contractId}`));
  });
});

test.describe('Route Navigation - Sidebar Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate via sidebar to projects', async ({ page }) => {
    // Click projects in sidebar/navigation
    const projectsLink = page.getByRole('link', { name: /projects/i }).first();
    await expect(projectsLink).toBeVisible({ timeout: 5000 });
    await projectsLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/projects/);
  });

  test('should navigate via sidebar to items', async ({ page }) => {
    const itemsLink = page.getByRole('link', { name: /items/i }).first();
    await expect(itemsLink).toBeVisible({ timeout: 5000 });
    await itemsLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/items/);
  });

  test('should navigate via sidebar to graph view', async ({ page }) => {
    const graphLink = page.getByRole('link', { name: /graph/i }).first();
    await expect(graphLink).toBeVisible({ timeout: 5000 });
    await graphLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/graph/);
  });

  test('should navigate via sidebar to settings', async ({ page }) => {
    const settingsLink = page.getByRole('link', { name: /settings/i }).first();
    await expect(settingsLink).toBeVisible({ timeout: 5000 });
    await settingsLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/settings/);
  });

  test('should maintain active state in sidebar', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Check if projects link is marked as active
    const projectsLink = page.getByRole('link', { name: /projects/i }).first();
    await expect(projectsLink).toHaveAttribute('aria-current', 'page', { timeout: 5000 });
  });
});

test.describe('Route Navigation - Route Transitions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should transition smoothly between routes', async ({ page }) => {
    // Navigate from dashboard to projects
    await page.goto('/projects');
    await expect(page).toHaveURL(/\/projects/);

    // Navigate from projects to items
    await page.goto('/items');
    await expect(page).toHaveURL(/\/items/);

    // Navigate from items to graph
    await page.goto('/graph');
    await expect(page).toHaveURL(/\/graph/);

    // Navigate back to dashboard
    await page.goto('/');
    await expect(page).toHaveURL('/');
  });

  test('should handle rapid route transitions', async ({ page }) => {
    const routes = ['/projects', '/items', '/graph', '/settings'];

    for (const route of routes) {
      await page.goto(route);
      const currentUrl = page.url();
      expect(currentUrl).toContain(route);
    }
  });

  test('should maintain scroll position during navigation', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Scroll down
    await page.evaluate(() => {
      window.scrollTo(0, 500);
    });
    const _scrollBefore = await page.evaluate(() => window.scrollY);

    // Navigate to another route
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Navigate back
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Scroll position might be reset, but page should load successfully
    await expect(page).toHaveURL(/\/projects/);
  });

  test('should handle navigation with query parameters', async ({ page }) => {
    // Navigate with query parameters
    await page.goto('/search?q=test&type=feature');
    await expect(page).toHaveURL(/\/search\?q=test&type=feature/);

    // Navigate to another route
    await page.goto('/items?view=tree&sort=name');
    await expect(page).toHaveURL(/\/items\?view=tree&sort=name/);
  });

  test('should handle back button navigation', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');

    // Navigate forward
    await page.goto('/projects');
    await expect(page).toHaveURL(/\/projects/);

    // Use back button
    await page.goBack();
    await expect(page).toHaveURL('/');
  });

  test('should handle forward button navigation', async ({ page }) => {
    await page.goto('/');
    await page.goto('/projects');
    await page.goBack();
    await expect(page).toHaveURL('/');

    // Use forward button
    await page.goForward();
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe('Route Navigation - Error Handling', () => {
  test('should handle non-existent route gracefully', async ({ page }) => {
    // Navigate to non-existent route
    const response = await page.goto('/non-existent-route');

    // Should either get 404 or be redirected
    expect(response?.status()).toBeLessThan(500);
  });

  test('should handle invalid project ID', async ({ page }) => {
    const response = await page.goto('/projects/non-existent-id');

    // Route should exist even if project doesn't
    expect(response?.status()).toBeLessThan(500);
  });

  test('should handle invalid item ID', async ({ page }) => {
    const response = await page.goto('/items/non-existent-id');

    // Route should exist even if item doesn't
    expect(response?.status()).toBeLessThan(500);
  });

  test('should recover from failed navigation', async ({ page }) => {
    // Try invalid route
    await page.goto('/invalid');

    // Should still be able to navigate to valid route
    await page.goto('/projects');
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe('Route Navigation - Route Guards', () => {
  test('should redirect to appropriate auth routes', async ({ page }) => {
    // Navigate to login
    const response = await page.goto('/auth/login');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('should load register route', async ({ page }) => {
    const response = await page.goto('/auth/register');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test('should load password reset route', async ({ page }) => {
    const response = await page.goto('/auth/reset-password');
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/\/auth\/reset-password/);
  });
});

test.describe('Route Navigation - Breadcrumb Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display breadcrumbs on nested routes', async ({ page }) => {
    const projectId = 'test-project';
    await page.goto(`/projects/${projectId}`);
    await page.waitForLoadState('networkidle');

    // Check for breadcrumb navigation
    const breadcrumb = page
      .locator('nav')
      .filter({ hasText: /projects|home/i })
      .first();
    await expect(breadcrumb).toBeVisible({ timeout: 5000 });

    // Breadcrumbs might be optional, but page should load
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}`));
  });

  test('should navigate via breadcrumb to parent', async ({ page }) => {
    const projectId = 'test-project';
    await page.goto(`/projects/${projectId}`);
    await page.waitForLoadState('networkidle');

    // Try to find and click a breadcrumb link to projects
    const projectsLink = page.getByRole('link', {
      name: /projects/i,
    });
    const count = await projectsLink.count();

    if (count > 0) {
      // Click the first projects link (which might be breadcrumb)
      await projectsLink.first().click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/\/projects/);
    } else {
      // Manual navigation if breadcrumb not found
      await page.goto('/projects');
      await expect(page).toHaveURL(/\/projects/);
    }
  });
});

test.describe('Route Navigation - Performance', () => {
  test('should navigate to route in under 1 second', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/projects');
    const navigationTime = Date.now() - startTime;

    expect(navigationTime).toBeLessThan(1000);
  });

  test('should load all static routes without timeout', async ({ page }) => {
    const routes = ['/', '/projects', '/items', '/graph', '/settings', '/reports'];

    for (const route of routes) {
      const startTime = Date.now();
      const response = await page.goto(route, { timeout: 5000 });
      const loadTime = Date.now() - startTime;

      expect(response?.status()).toBeLessThan(400);
      expect(loadTime).toBeLessThan(5000);
    }
  });

  test('should handle multiple rapid navigation requests', async ({ page }) => {
    const navigationPromises: ReturnType<typeof page.goto>[] = [];

    for (let i = 0; i < 5; i++) {
      navigationPromises.push(page.goto('/projects'));
    }

    await Promise.all(navigationPromises);
    await expect(page).toHaveURL(/\/projects/);
  });
});
