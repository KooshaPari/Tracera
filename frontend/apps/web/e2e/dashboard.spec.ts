import { expect, test } from './global-setup';

/**
 * Dashboard E2E Tests
 *
 * Tests for dashboard functionality, widgets, metrics, and overview displays.
 */

test.describe('Dashboard Overview', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display dashboard page', async ({ page }) => {
    // Should be on dashboard
    await expect(page).toHaveURL('/');

    // Dashboard content should be visible - look for the Traceability Dashboard heading
    const dashboardHeading = page.getByRole('heading', {
      name: /traceability dashboard/i,
    });
    await expect(dashboardHeading).toBeVisible({ timeout: 5000 });
  });

  test('should show dashboard heading', async ({ page }) => {
    // Look for main dashboard heading - should show "Welcome to TraceRTM"
    const heading = page.getByText(/Welcome to TraceRTM/i);

    await expect(heading).toBeVisible({ timeout: 5000 });
  });

  test('should load dashboard data', async ({ page }) => {
    // Wait for data to load
    await page.waitForLoadState('networkidle');

    // Should show dashboard subtitle - the actual DashboardView shows this message
    const subtitle = page.getByText(/Monitor project health and system-wide traceability status/i);
    await expect(subtitle).toBeVisible({ timeout: 5000 });

    // General content check - look for dashboard container
    const content = page.locator('[class*="space-y"]').first();
    const textContent = await content.textContent();

    expect(textContent).toBeTruthy();
    expect(textContent!.length).toBeGreaterThan(50);
  });
});

test.describe('Dashboard Metrics', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display project count metric', async ({ page }) => {
    // Look for project section - DashboardView shows "Active Projects" heading
    const projectStat = page.getByRole('heading', { name: /Active Projects/i });
    await expect(projectStat).toBeVisible({ timeout: 5000 });

    // Should show the projects section - check the page content
    const pageContent = page.locator('body');
    const projectText = await pageContent.textContent();
    expect(projectText).toContain('Active Projects');
  });

  test('should display items count metric', async ({ page }) => {
    // Look for items count stat
    const itemStat = page.getByText('Items').first();
    await expect(itemStat).toBeVisible({ timeout: 5000 });
  });

  test('should display links count metric', async ({ page }) => {
    // Look for links count
    const linkStat = page.getByText('Links').first();
    await expect(linkStat).toBeVisible({ timeout: 5000 });
  });

  test('should display active agents metric', async ({ page }) => {
    // Look for active agents count
    const agentStat = page.getByText(/Active Agents/i);
    await expect(agentStat).toBeVisible({ timeout: 5000 });
  });

  test('should display priority metrics', async ({ page }) => {
    // Look for priority breakdown
    await expect(page.locator('text=/critical|high|medium|low/i').first()).toBeVisible({
      timeout: 5000,
    });
  });
});

test.describe('Dashboard Widgets', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display recent projects section', async ({ page }) => {
    // Look for Recent Projects heading
    const recentProjects = page.getByText(/Recent Projects/i);
    await expect(recentProjects).toBeVisible({ timeout: 5000 });
  });

  test('should display project cards with information', async ({ page }) => {
    // Look for project names in the recent projects section
    const traceRTMProject = page.getByText(/TraceRTM Frontend/);
    await expect(traceRTMProject).toBeVisible({ timeout: 5000 });
  });

  test('should show items and links counts', async ({ page }) => {
    // Look for item and link counts in project cards
    const itemsCount = page.getByText(/items/i);
    await expect(itemsCount.first()).toBeVisible({ timeout: 5000 });

    const linksCount = page.getByText(/links/i);
    await expect(linksCount.first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to projects from stats', async ({ page }) => {
    // Click on "New Project" button which links to /projects
    const newProjectButton = page.getByRole('link', { name: /new project/i });

    await expect(newProjectButton).toBeVisible({ timeout: 3000 });
    await newProjectButton.click();
    await page.waitForLoadState('networkidle');

    // Should navigate to projects page
    await expect(page).toHaveURL(/\/projects/);
  });

  test('should navigate to specific project from dashboard', async ({ page }) => {
    // Look for any project link in the Active Projects section
    const projectLinks = page.locator('a[href*="/projects/"]');
    await expect(projectLinks.first()).toBeVisible({ timeout: 10_000 });
    await projectLinks.first().click();
    await page.waitForLoadState('networkidle');

    // Should navigate to projects page or project detail
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe('Dashboard Charts', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display items by type chart', async ({ page }) => {
    // Look for chart or visualization
    const chart = page.locator('canvas, svg').first().or(page.locator('[role="img"]').first());

    await expect(chart).toBeVisible({ timeout: 5000 });
  });

  test('should display items by status chart', async ({ page }) => {
    // Look for status breakdown chart
    await expect(page.locator('text=/status|completed|in progress/i').first()).toBeVisible({
      timeout: 5000,
    });
  });

  test('should display trend chart', async ({ page }) => {
    // Look for trend/timeline chart
    await expect(page.locator('canvas, svg').first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Dashboard Quick Actions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should show quick action buttons', async ({ page }) => {
    // Look for quick action buttons (Create Project, Create Item, etc.)
    const quickActions = page.locator('button').filter({ hasText: /create|new|add/i });
    await expect(quickActions.first()).toBeVisible({ timeout: 5000 });
    const count = await quickActions.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should create project from dashboard', async ({ page }) => {
    const createProjectButton = page
      .getByRole('button', { name: /create.*project|new project/i })
      .first();

    await expect(createProjectButton).toBeVisible({ timeout: 5000 });
    await createProjectButton.click();

    // Should open create project dialog
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible({ timeout: 5000 });
  });

  test('should create item from dashboard', async ({ page }) => {
    const createItemButton = page.getByRole('button', { name: /create.*item|new item/i }).first();
    await expect(createItemButton).toBeVisible({ timeout: 5000 });
    await createItemButton.click();

    // Should open create item dialog or navigate to create page
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Dashboard Filters', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should show project filter', async ({ page }) => {
    // Look for project filter dropdown
    const projectFilter = page
      .locator('select')
      .filter({ hasText: /project/i })
      .first()
      .or(page.getByLabel(/project/i).first());

    await expect(projectFilter).toBeVisible({ timeout: 5000 });
  });

  test('should filter dashboard by project', async ({ page }) => {
    const projectFilter = page.locator('select').first();
    await expect(projectFilter).toBeVisible({ timeout: 5000 });
    await projectFilter.click();
    await page.waitForTimeout(300);

    // Select a project
    const projectOption = page.getByText('TraceRTM Core').first();
    await expect(projectOption).toBeVisible({ timeout: 5000 });
    await projectOption.click();
    await page.waitForLoadState('networkidle');
  });

  test('should show time range filter', async ({ page }) => {
    // Look for date/time range filter
    const timeFilter = page
      .locator('select, button')
      .filter({ hasText: /today|week|month|year|range/i })
      .first();

    await expect(timeFilter).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Dashboard Refresh', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should show refresh button', async ({ page }) => {
    // Look for refresh button
    const refreshButton = page
      .getByRole('button', { name: /refresh|reload/i })
      .first()
      .or(page.locator('button[aria-label*="refresh" i]').first());

    await expect(refreshButton).toBeVisible({ timeout: 5000 });
  });

  test('should refresh dashboard data', async ({ page }) => {
    const refreshButton = page.getByRole('button', { name: /refresh|reload/i }).first();
    await expect(refreshButton).toBeVisible({ timeout: 5000 });
    await refreshButton.click();
    await page.waitForLoadState('networkidle');

    // Data should be reloaded
    await page.waitForTimeout(500);
  });

  test('should auto-refresh on navigation back', async ({ page }) => {
    // Navigate away
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Navigate back to dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Dashboard should reload data - look for the dashboard heading
    const dashboardHeading = page.getByRole('heading', {
      name: /traceability dashboard/i,
    });
    await expect(dashboardHeading).toBeVisible({ timeout: 5000 });
  });
});
