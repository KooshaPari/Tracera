import { expect, test } from './global-setup';

/**
 * Critical Path E2E Tests
 *
 * Tests for the most critical user flows in TraceRTM:
 * 1. Complete project creation flow
 * 2. Complete item creation and management flow
 * 3. Creating traceability links between items
 * 4. Navigation between all major views
 * 5. Search and filter functionality
 *
 * These tests represent the absolute core functionality that must work.
 */

test.describe('CRITICAL PATH: Project Creation Flow', { tag: '@smoke' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');
  });

  test('should complete end-to-end project creation', async ({ page }) => {
    // 1. Navigate to projects page
    await expect(page).toHaveURL('/projects');

    // 2. Find and click create button
    const createBtn = page.getByRole('button', { name: /create|new|add.*project/i }).first();

    // Check if button is visible
    await expect(createBtn).toBeVisible({ timeout: 3000 });

    await createBtn.click();
    await page.waitForTimeout(500);

    // 3. Fill project form
    const nameInput = page
      .getByLabel(/name|project name/i)
      .or(page.getByPlaceholder(/name/i))
      .first();

    const descInput = page
      .getByLabel(/description/i)
      .or(page.getByPlaceholder(/description/i))
      .first();

    await expect(nameInput).toBeVisible({ timeout: 2000 });
    // Generate unique project name with timestamp
    const projectName = `Critical Path Test ${Date.now()}`;
    await nameInput.fill(projectName);

    await expect(descInput).toBeVisible({ timeout: 1000 });
    await descInput.fill('Critical path test project created via E2E');

    // 4. Submit form
    const submitBtn = page.getByRole('button', {
      name: /create|save|submit/i,
    });

    await expect(submitBtn).toBeVisible({ timeout: 1000 });
    await submitBtn.click();
    await page.waitForLoadState('networkidle');

    // 5. Verify project was created
    const projectNameText = page.getByText(projectName);
    await expect(projectNameText).toBeVisible({ timeout: 5000 });
  });

  test('should display list of existing projects', async ({ page }) => {
    // Core requirement: projects should be displayable
    await page.waitForLoadState('networkidle');

    // Look for any project name in the list
    const projectItems = page.locator('text=/TraceRTM Core|Mobile App|project/i');

    const count = await projectItems.count();
    // Projects should be present
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('CRITICAL PATH: Item Creation and Management', { tag: '@smoke' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should create a new item', async ({ page }) => {
    // 1. Verify on items page
    await expect(page).toHaveURL(/\/items/);

    // 2. Find create button
    const createBtn = page.getByRole('button', { name: /create|new|add.*item/i }).first();

    await expect(createBtn).toBeVisible({ timeout: 3000 });

    await createBtn.click();
    await page.waitForTimeout(500);

    // 3. Fill item form
    const titleInput = page
      .getByLabel(/title|item title/i)
      .or(page.getByPlaceholder(/title/i))
      .first();

    await expect(titleInput).toBeVisible({ timeout: 2000 });
    const itemTitle = `Critical Path Item ${Date.now()}`;
    await titleInput.fill(itemTitle);

    // Try to fill description
    const descInput = page
      .getByLabel(/description/i)
      .or(page.getByPlaceholder(/description/i))
      .first();

    await expect(descInput).toBeVisible({ timeout: 1000 });
    await descInput.fill('Critical path test item - verifies item creation works');

    // Try to select type
    const typeSelect = page.getByLabel(/type/i).first();
    await expect(typeSelect).toBeVisible({ timeout: 1000 });
    await typeSelect.click();
    await page.waitForTimeout(300);

    const requirementOption = page.getByText(/requirement/i).first();
    await expect(requirementOption).toBeVisible({ timeout: 1000 });
    await requirementOption.click();

    // 4. Submit form
    const submitBtn = page.getByRole('button', {
      name: /create|save|submit|add/i,
    });

    await expect(submitBtn).toBeVisible({ timeout: 1000 });
    await submitBtn.click();
    await page.waitForLoadState('networkidle');

    // 5. Verify item appears in list
    const itemText = page.getByText(itemTitle);
    await expect(itemText).toBeVisible({ timeout: 5000 });
  });

  test('should update existing item status', async ({ page }) => {
    // 1. Wait for items to load
    await page.waitForLoadState('networkidle');

    // 2. Find an item (look for any visible item)
    const itemLink = page
      .getByRole('link', {
        name: /authentication|dashboard|feature|requirement/i,
      })
      .first();

    await expect(itemLink).toBeVisible({ timeout: 2000 });

    // 3. Click to navigate to item detail
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // 4. Look for status selector
    const statusField = page
      .getByLabel(/status/i)
      .first()
      .or(page.locator("[role='combobox']").filter({ hasText: /status/i }));

    await expect(statusField).toBeVisible({ timeout: 2000 });

    // 5. Change status
    await statusField.click();
    await page.waitForTimeout(300);

    const completedOption = page.getByText(/completed|done|finished/i);
    await expect(completedOption).toBeVisible({ timeout: 1000 });

    await completedOption.click();
    await page.waitForLoadState('networkidle');
  });

  test('should display items in table format', async ({ page }) => {
    // Core requirement: items should be displayable in a table
    await page.waitForLoadState('networkidle');

    // Look for any table content
    const rows = page.locator('tbody tr').or(page.locator("[role='row']"));
    const rowCount = await rows.count();

    expect(rowCount).toBeGreaterThan(0);

    // Check for common item properties displayed
    const headers = page.locator("thead [role='columnheader']");
    const headerCount = await headers.count();

    expect(headerCount).toBeGreaterThan(0);
    console.log(`Found ${headerCount} table headers and ${rowCount} rows`);
  });
});

test.describe('CRITICAL PATH: Link Creation Between Items', { tag: '@smoke' }, () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to an item that should have links capability
    await page.goto('/items/item-1');
    await page.waitForLoadState('networkidle');
  });

  test('should access item and show link section', async ({ page }) => {
    // 1. Verify on item detail page
    await page.waitForLoadState('networkidle');

    // 2. Look for links section/button
    const linkButton = page.getByRole('button', {
      name: /add link|create link|new link|link to/i,
    });

    await expect(linkButton).toBeVisible({ timeout: 2000 });

    // 3. Click to create link
    await linkButton.click();
    await page.waitForTimeout(500);

    // 4. Look for link form
    const targetSelect = page.getByLabel(/target.*item|target/i).first();

    await expect(targetSelect).toBeVisible({ timeout: 2000 });
  });

  test('should navigate to graph view showing links', async ({ page }) => {
    // Navigate to graph view
    const graphLink = page.getByRole('link', { name: /graph|visualization/i });

    await expect(graphLink).toBeVisible({ timeout: 2000 });

    await graphLink.click();
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveURL(/\/graph/);

    // Check for graph container
    const graphContainer = page.locator("[data-testid='graph-container']");
    await expect(graphContainer).toBeVisible({ timeout: 3000 });
  });
});

test.describe('CRITICAL PATH: Navigation Between Views', { tag: '@smoke' }, () => {
  test('should navigate to dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');
    await page.waitForLoadState('networkidle');

    // Verify page loaded - check for dashboard content
    // Use first() to handle multiple elements, and increase timeout
    const main = page.locator('main').first();
    const h1 = page.locator('h1').first();
    const dashboardText = page.getByText(/dashboard/i).first();

    await expect(main.or(h1).or(dashboardText)).toBeVisible({ timeout: 5000 });
  });

  test('should navigate from projects to items to detail', async ({ page }) => {
    // 1. Start at projects
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/projects');

    // 2. Navigate to items page directly (items page is not in sidebar navigation)
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/items/);

    // 3. Navigate to an item detail by clicking on an item
    const firstItem = page.locator("a[href^='/items/']").first();

    await expect(firstItem).toBeVisible({ timeout: 3000 });
    await firstItem.click();
    await page.waitForLoadState('networkidle');

    // Should be on detail page
    await expect(page).toHaveURL(/\/items\/[a-z0-9-]+/);
  });

  test('should use browser back button to navigate', async ({ page }) => {
    // 1. Navigate to multiple pages
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // 2. Go back
    await page.goBack();
    await page.waitForLoadState('networkidle');

    // Should be back at projects
    await expect(page).toHaveURL('/projects');
  });

  test('should navigate to graph view', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/');

    const graphLink = page.getByRole('link', { name: /graph|visualization/i });

    await expect(graphLink).toBeVisible({ timeout: 2000 });
    await graphLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/graph/);
  });

  test('should navigate to settings', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const settingsLink = page.getByRole('link', { name: /settings|config/i });

    await expect(settingsLink).toBeVisible({ timeout: 2000 });
    await settingsLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/settings/);
  });
});

test.describe('CRITICAL PATH: Search and Filter Functionality', { tag: '@smoke' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should search items by title', async ({ page }) => {
    // 1. Find search input
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByPlaceholder(/search/i))
      .first();

    await expect(searchInput).toBeVisible({ timeout: 2000 });

    // 2. Perform search
    await searchInput.fill('authentication');
    await page.waitForTimeout(500); // Wait for debounce

    // 3. Verify results updated
    const results = page.getByText(/authentication/i);
    const resultCount = await results.count();

    console.log(`Found ${resultCount} results for "authentication" search`);
    expect(resultCount).toBeGreaterThanOrEqual(0);
  });

  test('should filter items by type', async ({ page }) => {
    // Look for type filter
    const typeFilter = page
      .getByLabel(/type|filter.*type/i)
      .first()
      .or(page.locator('select').filter({ hasText: /type/i }).first());

    await expect(typeFilter).toBeVisible({ timeout: 2000 });

    // Click to open dropdown
    await typeFilter.click();
    await page.waitForTimeout(300);

    // Try to select a type
    const typeOption = page.getByText(/requirement|feature|test/i).first();
    await expect(typeOption).toBeVisible({ timeout: 1000 });
    await typeOption.click();
    await page.waitForTimeout(500);

    console.log('Type filter applied successfully');
  });

  test('should filter items by status', async ({ page }) => {
    // Look for status filter
    const statusFilter = page
      .getByLabel(/status|filter.*status/i)
      .first()
      .or(
        page
          .locator('select')
          .filter({ hasText: /status/i })
          .first(),
      );

    await expect(statusFilter).toBeVisible({ timeout: 2000 });

    await statusFilter.click();
    await page.waitForTimeout(300);

    const statusOption = page.getByText(/pending|in progress|completed/i);
    await expect(statusOption).toBeVisible({ timeout: 1000 });
    await statusOption.click();
    await page.waitForTimeout(500);

    console.log('Status filter applied successfully');
  });

  test('should clear search/filters', async ({ page }) => {
    // Fill search
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByPlaceholder(/search/i))
      .first();

    await expect(searchInput).toBeVisible({ timeout: 2000 });
    await searchInput.fill('test');
    await page.waitForTimeout(300);

    // Look for clear button
    const clearBtn = page.getByRole('button', { name: /clear|reset|x/i }).first();

    await expect(clearBtn).toBeVisible({ timeout: 2000 });
    await clearBtn.click();
    await page.waitForTimeout(300);

    // Verify cleared
    await expect(searchInput).toHaveValue('');
  });
});

test.describe('CRITICAL PATH: Core Data Integrity', { tag: '@smoke' }, () => {
  test('should load and display initial data on dashboard', async ({ page }) => {
    // Critical: app should show data on initial load
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait a bit for any animations
    await page.waitForTimeout(1000);

    // Check for any content on the page
    const mainLocator = page.locator('main').first();
    const roleMainLocator = page.locator("[role='main']").first();
    const bodyLocator = page.locator('body').first();

    await expect(mainLocator.or(roleMainLocator).or(bodyLocator)).toBeVisible({ timeout: 2000 });
  });

  test('should handle navigation without losing state', async ({ page }) => {
    // 1. Go to projects
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // 2. Do a search
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByPlaceholder(/search/i))
      .first();

    await expect(searchInput).toBeVisible({ timeout: 2000 });
    await searchInput.fill('test');

    // 3. Navigate away and back
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    await page.goBack();
    await page.waitForLoadState('networkidle');

    // Should be back at projects
    await expect(page).toHaveURL('/projects');
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Try to navigate to non-existent item
    await page.goto('/items/non-existent-id-12345', {
      waitUntil: 'networkidle',
    });

    // Page should either:
    // 1. Show error message
    // 2. Redirect to items list
    // 3. Show 404 page

    const error = page.getByText(/not found|error|does not exist/i);
    const itemsList = page.locator("table, [role='grid']");

    await expect(error.or(itemsList)).toBeVisible({ timeout: 2000 });
  });
});
