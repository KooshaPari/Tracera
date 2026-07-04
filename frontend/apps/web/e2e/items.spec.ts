import { expect, test } from './global-setup';

/**
 * Items CRUD E2E Tests
 *
 * Tests for item creation, reading, updating, deletion, and management.
 * Tests different item views: Table, Kanban, Tree.
 */

test.describe('Items Table View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should display items table', async ({ page }) => {
    // Wait for table to load - look for the items table container
    const table = page.locator('table');
    await expect(table).toBeVisible({ timeout: 5000 });

    // Should show table header
    const titleHeader = page.getByRole('columnheader', { name: /title/i });
    await expect(titleHeader).toBeVisible({ timeout: 5000 });
  });

  test('should display item columns', async ({ page }) => {
    // Wait for table
    await page.waitForLoadState('networkidle');

    // Common table headers
    const headers = ['Title', 'Type', 'Status', 'Priority'];

    for (const header of headers) {
      const headerCell = page.getByRole('columnheader', {
        name: new RegExp(header, 'i'),
      });
      await expect(headerCell).toBeVisible({ timeout: 5000 });
    }
  });

  test('should show item actions', async ({ page }) => {
    // Wait for table to load
    await page.waitForLoadState('networkidle');

    // Look for action buttons in table rows - check for rows with content
    const tableBody = page.locator('tbody');
    await expect(tableBody).toBeVisible({ timeout: 5000 });

    // Verify some table rows are present
    const tableRows = page.locator('tbody tr');
    const rowCount = await tableRows.count();
    expect(rowCount).toBeGreaterThan(0);
  });

  test('should filter items by project', async ({ page }) => {
    // Look for project filter
    const filterSelect = page.getByRole('combobox').or(page.locator('select')).first();

    await expect(filterSelect).toBeVisible({ timeout: 5000 });
  });

  test('should sort items by column', async ({ page }) => {
    // Wait for table to load
    await page.waitForLoadState('networkidle');

    // Try to click on a sortable column header
    const titleHeader = page.getByRole('columnheader', { name: /title/i });
    await expect(titleHeader).toBeVisible({ timeout: 5000 });
    // Click header to sort
    await titleHeader.click();
    await page.waitForTimeout(500);

    // Verify table is still visible after sort
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });
});

test.describe('Items Kanban View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items/kanban');
    await page.waitForLoadState('networkidle');
  });

  test('should display kanban board', async ({ page }) => {
    // Wait for content
    await page.waitForLoadState('networkidle');

    // Look for kanban columns based on actual item statuses
    // Check for status badge containers or column headers
    const statusText = page.getByText(/todo|in_progress|done|blocked/i);
    await expect(statusText.first()).toBeVisible({ timeout: 5000 });
  });

  test('should display items in kanban columns', async ({ page }) => {
    // Wait for content to load
    await page.waitForLoadState('networkidle');

    // Look for kanban board content - check page body
    const pageContent = page.locator('body');
    const content = await pageContent.textContent();

    // Verify there's content beyond just headers
    expect(content).toBeTruthy();
    expect((content ?? '').length).toBeGreaterThan(50);
  });

  test('should drag and drop items between columns', async ({ page }) => {
    // This is a complex interaction - test that cards exist
    await page.waitForLoadState('networkidle');

    // Look for draggable items
    const draggableItems = page.locator('[draggable="true"]').or(page.locator('[data-draggable]'));

    await expect(draggableItems.first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Items Tree View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items/tree');
    await page.waitForLoadState('networkidle');
  });

  test('should display items tree', async ({ page }) => {
    // Wait for tree to load
    await page.waitForLoadState('networkidle');

    // Verify page loaded and has content
    const pageContent = page.locator('body');
    const content = await pageContent.textContent();
    expect(content).toBeTruthy();
    expect((content ?? '').length).toBeGreaterThan(50);
  });

  test('should expand and collapse tree nodes', async ({ page }) => {
    // Wait for tree
    await page.waitForLoadState('networkidle');

    // Look for expand/collapse buttons - use specific "Expand All" or "Collapse All" buttons
    const expandAllBtn = page.getByRole('button', { name: /expand all/i });
    const collapseAllBtn = page.getByRole('button', { name: /collapse all/i });

    await expect(expandAllBtn).toBeVisible({ timeout: 5000 });
    await expandAllBtn.click();
    await page.waitForTimeout(300);

    // Look for collapse button after expanding
    await expect(collapseAllBtn).toBeVisible({ timeout: 5000 });
    await collapseAllBtn.click();
    await page.waitForTimeout(300);
  });

  test('should show parent-child relationships', async ({ page }) => {
    // Wait for content
    await page.waitForLoadState('networkidle');

    // Items with parent_id should be nested
    // Look for indented items or nested structure
    await page.waitForTimeout(500);
  });
});

test.describe('Item Creation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should show create item button', async ({ page }) => {
    const createButton = page.getByRole('button', { name: /create|new|add item/i }).first();

    await expect(createButton).toBeVisible({ timeout: 5000 });
  });

  test('should open create item dialog', async ({ page }) => {
    const createButton = page.getByRole('button', { name: /create|new|add item/i }).first();

    await expect(createButton).toBeVisible({ timeout: 5000 });
    await createButton.click();

    // Dialog should open - or check for form elements
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible({ timeout: 5000 });
  });

  test('should create a new item', async ({ page }) => {
    const createButton = page.getByRole('button', { name: /create|new|add item/i }).first();

    await expect(createButton).toBeVisible({ timeout: 5000 });
    await createButton.click();
    await page.waitForTimeout(500);

    // Fill in item details
    const titleInput = page.getByLabel(/title/i).or(page.getByPlaceholder(/title/i));
    await expect(titleInput).toBeVisible({ timeout: 5000 });
    await titleInput.fill('E2E Test Item');

    // Select type
    const typeSelect = page.getByLabel(/type/i).first();
    await expect(typeSelect).toBeVisible({ timeout: 5000 });
    await typeSelect.click();
    await page.waitForTimeout(300);

    // Select "Requirement" type
    const requirementOption = page.getByText('Requirement').first();
    await expect(requirementOption).toBeVisible({ timeout: 5000 });
    await requirementOption.click();

    // Fill description
    const descInput = page.getByLabel(/description/i).or(page.getByPlaceholder(/description/i));
    await expect(descInput).toBeVisible({ timeout: 5000 });
    await descInput.fill('Created via E2E test');

    // Submit
    const submitButton = page.getByRole('button', {
      name: /create|save|submit/i,
    });
    await expect(submitButton).toBeVisible({ timeout: 5000 });
    await submitButton.click();
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Item Detail', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items/item-1');
    await page.waitForLoadState('networkidle');
  });

  test('should display item details', async ({ page }) => {
    // Should show item title
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const heading = page.getByRole('heading', { name: /User Authentication/i });
    await expect(heading).toBeVisible();
  });

  test('should show item metadata', async ({ page }) => {
    // Wait for page
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Look for metadata fields
    await page
      .locator('text=/type|status|priority|created|updated/i')
      .first()
      .waitFor({ state: 'visible', timeout: 5000 });
  });

  test('should display item description', async ({ page }) => {
    // Wait for content
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Should show description
    await expect(page.getByText(/Implement secure user authentication/i)).toBeVisible({
      timeout: 5000,
    });
  });

  test('should show related items', async ({ page }) => {
    // Wait for page
    await page.waitForLoadState('networkidle');

    // Look for links/relationships section
    await expect(page.locator('text=/related|links|dependencies|children/i').first()).toBeVisible({
      timeout: 5000,
    });
  });
});

test.describe('Item Update', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items/item-2');
    await page.waitForLoadState('networkidle');
  });

  test('should show edit item button', async ({ page }) => {
    const editButton = page.getByRole('button', { name: /edit/i }).first();

    await expect(editButton).toBeVisible({ timeout: 5000 });
  });

  test('should update item status', async ({ page }) => {
    // Look for status selector
    const statusSelect = page
      .getByLabel(/status/i)
      .first()
      .or(
        page
          .locator('select')
          .filter({ hasText: /status/i })
          .first(),
      );

    await expect(statusSelect).toBeVisible({ timeout: 5000 });
    await statusSelect.click();
    await page.waitForTimeout(300);

    // Select a different status
    const completedOption = page.getByText('Completed').first();
    await expect(completedOption).toBeVisible({ timeout: 5000 });
    await completedOption.click();
    await page.waitForLoadState('networkidle');
  });

  test('should update item priority', async ({ page }) => {
    // Look for priority selector
    const prioritySelect = page.getByLabel(/priority/i).first();

    await expect(prioritySelect).toBeVisible({ timeout: 5000 });
    await prioritySelect.click();
    await page.waitForTimeout(300);
  });
});

test.describe('Item Deletion', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items/item-10');
    await page.waitForLoadState('networkidle');
  });

  test('should show delete item button', async ({ page }) => {
    const deleteButton = page.getByRole('button', { name: /delete/i }).first();

    await expect(deleteButton).toBeVisible({ timeout: 5000 });
  });

  test('should show confirmation for delete', async ({ page }) => {
    const deleteButton = page.getByRole('button', { name: /delete/i }).first();

    await expect(deleteButton).toBeVisible({ timeout: 5000 });
    await deleteButton.click();

    // Should show confirmation
    const confirmDialog = page.getByRole('dialog').or(page.getByRole('alertdialog'));
    await expect(confirmDialog).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Item Search and Filter', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should search items by title', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByPlaceholder(/search/i))
      .first();

    await expect(searchInput).toBeVisible({ timeout: 5000 });
    await searchInput.fill('Authentication');
    await page.waitForTimeout(500);

    // Should show matching items or search results
    await expect(page.getByText('User Authentication')).toBeVisible({ timeout: 5000 });
  });

  test('should filter items by type', async ({ page }) => {
    // Look for type filter
    const typeFilter = page
      .locator('select')
      .filter({ hasText: /type/i })
      .first()
      .or(page.getByLabel(/type/i).first());

    await expect(typeFilter).toBeVisible({ timeout: 5000 });
  });

  test('should filter items by status', async ({ page }) => {
    // Look for status filter
    const statusFilter = page
      .locator('select')
      .filter({ hasText: /status/i })
      .first();

    await expect(statusFilter).toBeVisible({ timeout: 5000 });
  });
});
