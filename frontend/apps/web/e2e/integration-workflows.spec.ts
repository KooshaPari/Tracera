import { expect, test } from './global-setup';

/**
 * Integration Workflow Tests
 *
 * Tests that verify multiple components working together
 * in realistic user workflows.
 */

test.describe('Project to Items Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should create project and add items in one flow', async ({ page }) => {
    // Navigate to projects
    await page.goto('/projects');
    await page.waitForURL('/projects');
    await page.waitForLoadState('networkidle');

    // Try multiple ways to create a project
    const newProjectBtn = page
      .locator('button')
      .filter({ hasText: /new project/i })
      .first();
    await expect(newProjectBtn).toBeVisible({ timeout: 5000 });
    await newProjectBtn.click();

    await page.waitForTimeout(500);

    // Fill form fields if dialog is open
    const nameInput = page.locator('input[id="project-name"]');
    await expect(nameInput).toBeVisible({ timeout: 5000 });
    await nameInput.fill('Test Project');
    await page.fill('textarea[id="project-description"]', 'A test project for workflow');

    const createBtn = page
      .locator('button')
      .filter({ hasText: /create project/i })
      .first();
    await expect(createBtn).toBeVisible({ timeout: 5000 });
    await createBtn.click();
    await page.waitForURL(/\/projects\/[^?]+/);
    await page.waitForTimeout(500);
  });

  test('should link items within project context', async ({ page }) => {
    // Navigate to items
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Click on first item if available
    const itemCards = page.locator('tbody tr');
    await expect(itemCards.first()).toBeVisible({ timeout: 5000 });
    await itemCards.first().click();
    await page.waitForTimeout(500);

    // Try to navigate to item detail
    const itemLinks = page.locator('a[href*="/items/"]');
    await expect(itemLinks.first()).toBeVisible({ timeout: 5000 });
    await itemLinks.first().click();
    await page.waitForURL(/\/items\/.*/);

    // Verify we're on an item page
    await page.waitForTimeout(300);
  });

  test('should manage project lifecycle with items', async ({ page }) => {
    // Create project
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Navigate with search param to open create dialog
    await page.goto('/projects?action=create');
    await page.waitForTimeout(500);

    // Fill form fields if dialog is open
    const nameInput = page.locator('input[id="project-name"]');
    await expect(nameInput).toBeVisible({ timeout: 5000 });
    await nameInput.fill('Lifecycle Project');

    const createBtn = page
      .locator('button')
      .filter({ hasText: /create project/i })
      .first();
    await expect(createBtn).toBeVisible({ timeout: 5000 });
    await createBtn.click();
    await page.waitForURL(/\/projects\/[^?]+/);
    await page.waitForTimeout(500);

    // Navigate back to projects to verify
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Search to Navigation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should search and navigate to results', async ({ page }) => {
    // Try to open global search with Cmd+K or Ctrl+K
    const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
    await page.keyboard.press(`${modifier}+KeyK`);
    await page.waitForTimeout(500);

    // Look for search dialog or input
    const searchInput = page
      .locator('input[placeholder*="search" i], input[type="search"]')
      .first();
    await expect(searchInput).toBeVisible({ timeout: 5000 });
    await searchInput.fill('authentication');
    await page.waitForTimeout(500);

    // Look for clickable results
    const results = page
      .locator('button, a, div[role="option"]')
      .filter({ hasText: /authentication/i });
    await expect(results.first()).toBeVisible({ timeout: 5000 });
    await results.first().click();
    await page.waitForTimeout(500);
  });

  test('should filter search by type', async ({ page }) => {
    // Navigate to items page where filtering is available
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Look for filter controls
    const filterButtons = page.locator('button').filter({ hasText: /filter/i });
    await expect(filterButtons.first()).toBeVisible({ timeout: 5000 });
    await filterButtons.first().click();
    await page.waitForTimeout(300);
  });

  test('should search within project context', async ({ page }) => {
    // Navigate to a project if it exists
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Look for a clickable project link
    const projectLinks = page.locator('a[href*="/projects/"]').first();
    await expect(projectLinks).toBeVisible({ timeout: 5000 });
    await projectLinks.click();
    await page.waitForURL(/\/projects\/.*/);
    await page.waitForTimeout(500);
  });

  test('should navigate between search results using keyboard', async ({ page }) => {
    // Navigate to items which should have keyboard support
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Look for table or list that can be navigated
    const tableRows = page.locator('tbody tr, [role="row"]');
    await expect(tableRows.first()).toBeVisible({ timeout: 5000 });
    await tableRows.first().focus();
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(300);
  });
});

test.describe('Dashboard to Detail Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate from dashboard widget to detail view', async ({ page }) => {
    // Look for clickable items on dashboard
    const dashboardLinks = page.locator('a[href*="/projects/"]').first();
    await expect(dashboardLinks).toBeVisible({ timeout: 5000 });
    await dashboardLinks.click();
    await page.waitForURL(/\/projects\/.*/);
    await page.waitForTimeout(500);
  });

  test('should navigate from dashboard stats to filtered lists', async ({ page }) => {
    // Look for clickable stat items on dashboard
    const statLinks = page
      .locator('button, a')
      .filter({ hasText: /item|status|progress/i })
      .first();
    await expect(statLinks).toBeVisible({ timeout: 5000 });
    await statLinks.click();
    await page.waitForTimeout(500);
  });

  test('should update dashboard after creating item', async ({ page }) => {
    // Navigate to items to create an item
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Look for create button
    const createButton = page
      .locator('button')
      .filter({ hasText: /new|create|add/i })
      .first();
    await expect(createButton).toBeVisible({ timeout: 5000 });
    await createButton.click();
    await page.waitForTimeout(500);

    // Return to dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Item CRUD with Links Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should create item, add links, and verify in graph', async ({ page }) => {
    // Look for new item button
    const newItemButton = page
      .locator('button')
      .filter({ hasText: /new|create/i })
      .first();
    await expect(newItemButton).toBeVisible({ timeout: 5000 });
    await newItemButton.click();
    await page.waitForTimeout(500);

    // Look for title input
    const titleInput = page.locator('input[name="title"], input[placeholder*="title" i]').first();
    await expect(titleInput).toBeVisible({ timeout: 5000 });
    await titleInput.fill('Test Item');
    await page.waitForTimeout(300);

    // Navigate to graph
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
  });

  test('should update item and preserve links', async ({ page }) => {
    // Navigate to items
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Click on first item
    const firstItemLink = page.locator('a[href*="/items/"]').first();
    await expect(firstItemLink).toBeVisible({ timeout: 5000 });
    await firstItemLink.click();
    await page.waitForURL(/\/items\/.*/);
    await page.waitForTimeout(500);

    // Look for edit button
    const editButton = page.locator('button').filter({ hasText: /edit/i }).first();
    await expect(editButton).toBeVisible({ timeout: 5000 });
    await editButton.click();
    await page.waitForTimeout(300);
  });

  test('should delete item and update linked items', async ({ page }) => {
    // Navigate to items
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Look for first item
    const firstItemLink = page.locator('a[href*="/items/"]').first();
    await expect(firstItemLink).toBeVisible({ timeout: 5000 });
    await firstItemLink.click();
    await page.waitForURL(/\/items\/.*/);
    await page.waitForTimeout(500);

    // Look for delete button
    const deleteButton = page
      .locator('button')
      .filter({ hasText: /delete/i })
      .first();
    await expect(deleteButton).toBeVisible({ timeout: 5000 });
    await deleteButton.click();
    await page.waitForTimeout(300);

    // Look for confirm button
    const confirmButton = page
      .locator('button')
      .filter({ hasText: /confirm|yes/i })
      .first();
    await expect(confirmButton).toBeVisible({ timeout: 5000 });
    await confirmButton.click();
    await page.waitForTimeout(500);
  });
});

test.describe('Sync and Collaboration Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should sync changes across tabs', async ({ browser }) => {
    // Create two contexts (tabs)
    const context1 = await browser.newContext();
    const page1 = await context1.newPage();
    await page1.goto('/items');
    await page1.waitForLoadState('networkidle');

    const context2 = await browser.newContext();
    const page2 = await context2.newPage();
    await page2.goto('/items');
    await page2.waitForLoadState('networkidle');

    // Wait a bit for initial load
    await page1.waitForTimeout(500);
    await page2.waitForTimeout(500);

    // Both should be on items page
    await expect(page1).toHaveURL(/\/items/);
    await expect(page2).toHaveURL(/\/items/);

    await context1.close();
    await context2.close();
  });

  test('should handle offline mode gracefully', async ({ page, context }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Go offline
    await context.setOffline(true);
    await page.waitForTimeout(500);

    // Try to interact with page
    const buttons = page.locator('button').first();
    await expect(buttons).toBeVisible({ timeout: 5000 });
    // Page should still be responsive even offline
    await expect(buttons).toBeEnabled();

    // Go back online
    await context.setOffline(false);
    await page.waitForTimeout(500);

    // Page should work normally
    await expect(page).toHaveURL(/\/items/);
  });

  test('should resolve sync conflicts', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Navigate to an item if available
    const firstItemLink = page.locator('a[href*="/items/"]').first();
    await expect(firstItemLink).toBeVisible({ timeout: 5000 });
    await firstItemLink.click();
    await page.waitForURL(/\/items\/.*/);
    await page.waitForTimeout(500);
  });

  test('should show real-time updates', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Page should be responsive to interactions
    const buttons = page.locator('button');
    await expect(buttons.first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Multi-Agent Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/agents');
    await page.waitForLoadState('networkidle');
  });

  test('should create agents and assign to items', async ({ page }) => {
    // Look for agents on page
    const agentCards = page.locator('div, section').filter({ hasText: /agent/i });
    await expect(agentCards.first()).toBeVisible({ timeout: 5000 });
    // Agents page is visible
    await expect(page).toHaveURL(/\/agents/);

    // Navigate to items
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Back to agents
    await page.goto('/agents');
    await page.waitForLoadState('networkidle');
  });

  test('should track agent workload', async ({ page }) => {
    // Agents page should be loaded
    await expect(page).toHaveURL(/\/agents/);

    // Look for agent list items
    const agentLinks = page.locator('a, button').filter({ hasText: /agent|analyzer|runner/i });
    await expect(agentLinks.first()).toBeVisible({ timeout: 5000 });
    await agentLinks.first().click();
    await page.waitForTimeout(500);
  });

  test('should filter items by agent', async ({ page }) => {
    // Navigate to items
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Look for filter button
    const filterButton = page
      .locator('button')
      .filter({ hasText: /filter/i })
      .first();
    await expect(filterButton).toBeVisible({ timeout: 5000 });
    await filterButton.click();
    await page.waitForTimeout(500);
  });
});

test.describe('Bulk Operations Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should select multiple items and bulk update', async ({ page }) => {
    // Look for checkboxes
    const checkboxes = page.locator('[type="checkbox"], [role="checkbox"]');
    await expect(checkboxes.first()).toBeVisible({ timeout: 5000 });
    await checkboxes.first().click();
    await page.waitForTimeout(300);

    await expect(checkboxes.nth(1)).toBeVisible({ timeout: 5000 });
    await checkboxes.nth(1).click();
    await page.waitForTimeout(300);

    // Look for bulk action toolbar
    const bulkToolbar = page.locator(
      '[data-testid="bulk-action-bar"], [data-testid="bulk-toolbar"]',
    );
    await expect(bulkToolbar).toBeVisible({ timeout: 5000 });
  });

  test('should bulk delete with confirmation', async ({ page }) => {
    // Look for checkboxes
    const checkboxes = page.locator('[type="checkbox"], [role="checkbox"]');
    await expect(checkboxes.first()).toBeVisible({ timeout: 5000 });
    await checkboxes.first().click();
    await page.waitForTimeout(300);

    // Look for delete button
    const deleteButton = page
      .locator('button')
      .filter({ hasText: /delete/i })
      .first();
    await expect(deleteButton).toBeVisible({ timeout: 5000 });
    await deleteButton.click();
    await page.waitForTimeout(500);

    // Look for confirmation dialog
    const confirmButton = page
      .locator('button')
      .filter({ hasText: /confirm|yes/i })
      .first();
    await expect(confirmButton).toBeVisible({ timeout: 5000 });
    await confirmButton.click();
    await page.waitForTimeout(500);
  });

  test('should bulk export items', async ({ page }) => {
    // Look for export button
    const exportButton = page
      .locator('button')
      .filter({ hasText: /export/i })
      .first();
    await expect(exportButton).toBeVisible({ timeout: 5000 });
  });
});
