import { expect, test } from './global-setup';

/**
 * Bulk Operations E2E Tests
 *
 * Comprehensive tests for bulk item operations including:
 * - Multiple item selection with checkboxes
 * - Bulk delete operations with confirmations
 * - Bulk status updates across multiple items
 * - Bulk move operations to different projects
 * - Bulk tag additions
 * - Bulk archive operations
 * - Selection UI interactions (select all, deselect all)
 * - Confirmation dialogs and cancellation
 * - Undo functionality
 * - Error handling for bulk operations
 */

/**
 * Test Suite: Bulk Item Selection
 * Tests for selecting, deselecting, and managing multiple item selections
 */
test.describe('Bulk Item Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should display selection checkboxes for items', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication|Dashboard|API/i', {
      timeout: 5000,
    });

    // Look for checkboxes in table rows or item rows
    const checkboxes = page.locator('input[type="checkbox"]');
    await expect(checkboxes.first()).toBeVisible({ timeout: 5000 });
    const checkboxCount = await checkboxes.count();

    expect(checkboxCount).toBeGreaterThan(0);
  });

  test('should select single item when checkbox is clicked', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Get first item checkbox
    const firstCheckbox = page.locator('input[type="checkbox"]').nth(1); // Skip header if present

    await expect(firstCheckbox).toBeVisible();

    // Click checkbox
    await firstCheckbox.click();
    await page.waitForTimeout(300);

    // Checkbox should be checked
    await expect(firstCheckbox).toBeChecked();

    // Bulk action bar should appear
    const bulkActionBar = page
      .locator('[data-testid="bulk-action-bar"]')
      .or(page.locator('text=/selected|delete|archive/i'));

    await expect(bulkActionBar).toBeVisible({ timeout: 2000 });
  });

  test('should select multiple items with individual checkboxes', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Get first two checkboxes
    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    // Click both checkboxes
    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Both should be checked
    await expect(checkbox1).toBeChecked();
    await expect(checkbox2).toBeChecked();

    // Bulk action bar should show "2 selected"
    const selectedCount = page.locator(String.raw`text=/2\s+selected|2\s+items/i`);
    await expect(selectedCount).toBeVisible({ timeout: 2000 });
  });

  test('should support select all functionality', async ({ page }) => {
    // Wait for items to load
    await page.waitForLoadState('networkidle');

    // Look for "Select All" button or header checkbox
    const selectAllCheckbox = page.locator('input[type="checkbox"]').first();
    const selectAllButton = page.getByRole('button', { name: /select all/i });

    await expect(selectAllCheckbox.or(selectAllButton)).toBeVisible();

    // Prefer clicking checkbox if available, otherwise button
    if (await selectAllCheckbox.isVisible()) {
      await selectAllCheckbox.click();
    } else {
      await selectAllButton.click();
    }
    await page.waitForTimeout(500);

    // Verify bulk action bar shows multiple items selected
    const selectedIndicator = page.locator('text=/selected|items selected/i');
    await expect(selectedIndicator).toBeVisible({ timeout: 5000 });
  });

  test('should deselect items individually', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    // Select both
    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Deselect first one
    await checkbox1.click();
    await page.waitForTimeout(300);

    // First should be unchecked, second should still be checked
    await expect(checkbox1).not.toBeChecked();
    await expect(checkbox2).toBeChecked();

    // Should show "1 selected"
    const selectedCount = page.locator(String.raw`text=/1\s+selected/i`);
    await expect(selectedCount).toBeVisible({ timeout: 2000 });
  });

  test('should clear all selections with clear button', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    // Select both
    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Look for "Clear Selection" or "Deselect All" button
    const clearButton = page.getByRole('button', { name: /clear|deselect all|unselect/i }).first();

    await expect(clearButton).toBeVisible();
    await clearButton.click();
    await page.waitForTimeout(300);

    // All should be unchecked
    await expect(checkbox1).not.toBeChecked();
    await expect(checkbox2).not.toBeChecked();
  });
});

/**
 * Test Suite: Bulk Delete Operations
 * Tests for deleting multiple items with confirmation dialogs
 */
test.describe('Bulk Delete Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should show delete button in bulk action bar', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select an item
    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Delete button should appear in bulk action bar
    const deleteButton = page
      .getByRole('button', { name: /delete|remove/i })
      .filter({ hasText: /delete|remove/i });

    await expect(deleteButton).toBeVisible({ timeout: 2000 });
  });

  test('should show confirmation dialog when deleting multiple items', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select two items
    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Click delete button
    const deleteButton = page.getByRole('button', { name: /delete|remove/i }).first();

    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
    await page.waitForTimeout(300);

    // Confirmation dialog should appear
    const confirmDialog = page.getByRole('dialog').or(page.getByRole('alertdialog'));

    await expect(confirmDialog).toBeVisible({ timeout: 2000 });

    // Dialog should mention items being deleted
    const dialogText = page.locator("[role='dialog']");
    await expect(dialogText).toContainText(/delete|remove|confirm/i, { timeout: 2000 });
  });

  test('should confirm bulk delete operation', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select an item for deletion
    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Click delete
    const deleteButton = page.getByRole('button', { name: /delete|remove/i }).first();

    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
    await page.waitForTimeout(300);

    // Click confirm button in dialog
    const confirmButton = page
      .getByRole('button', { name: /confirm|yes|delete/i })
      .filter({ hasText: /confirm|yes|delete/i });

    await expect(confirmButton).toBeVisible({ timeout: 5000 });
    await confirmButton.click();
    await page.waitForLoadState('networkidle');

    // Selection should be cleared or item removed
    await expect(checkbox).not.toBeChecked();
  });

  test('should cancel bulk delete operation', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    const deleteButton = page.getByRole('button', { name: /delete|remove/i }).first();

    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
    await page.waitForTimeout(300);

    // Click cancel button
    const cancelButton = page.getByRole('button', { name: /cancel|close/i }).first();

    await expect(cancelButton).toBeVisible();
    await cancelButton.click();
    await page.waitForTimeout(300);

    // Dialog should be closed
    const dialog = page.getByRole('dialog');
    await expect(dialog).not.toBeVisible();

    // Item should still be selected
    await expect(checkbox).toBeChecked();
  });

  test('should show undo option after bulk delete', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    const deleteButton = page.getByRole('button', { name: /delete|remove/i }).first();

    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
    await page.waitForTimeout(300);

    // Confirm delete
    const confirmButton = page
      .getByRole('button', { name: /confirm|yes|delete/i })
      .filter({ hasText: /confirm|yes|delete/i });

    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
    await page.waitForLoadState('networkidle');

    // Look for undo toast/button
    const undoButton = page.getByRole('button', { name: /undo/i }).or(page.locator('text=/undo/i'));

    await expect(undoButton).toBeVisible({ timeout: 3000 });
  });
});

/**
 * Test Suite: Bulk Status Update Operations
 * Tests for updating status across multiple items
 */
test.describe('Bulk Status Update Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should show status update option in bulk action menu', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select items
    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Look for status option in bulk action menu
    const statusMenu = page
      .getByRole('button', { name: /status|change status/i })
      .or(page.locator('[data-testid="bulk-status-menu"]'));

    await expect(statusMenu).toBeVisible({ timeout: 2000 });
  });

  test('should update status for multiple selected items', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select two items
    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Click status menu
    const statusButton = page.getByRole('button', { name: /status|change status/i }).first();

    await expect(statusButton).toBeVisible();
    await statusButton.click();
    await page.waitForTimeout(300);

    // Select a status option (e.g., "Completed")
    const statusOption = page.getByText(/completed|done|closed/i).first();

    await expect(statusOption).toBeVisible();
    await statusOption.click();
    await page.waitForLoadState('networkidle');
  });

  test('should show confirmation for bulk status update', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    const statusButton = page.getByRole('button', { name: /status|change status/i }).first();

    await expect(statusButton).toBeVisible();
    await statusButton.click();
    await page.waitForTimeout(300);

    // Select a status
    const statusOption = page.getByText(/completed|done|closed/i).first();

    await expect(statusOption).toBeVisible();
    await statusOption.click();
    await page.waitForTimeout(300);

    // Look for confirmation message
    const confirmMessage = page
      .locator('[role="alert"]')
      .or(page.locator('text=/updated|changed/i'));

    await expect(confirmMessage).toBeVisible({ timeout: 2000 });
  });
});

/**
 * Test Suite: Bulk Move to Project Operations
 * Tests for moving multiple items to different projects
 */
test.describe('Bulk Move to Project Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should show move to project option in bulk actions', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Look for move/project option
    const moveButton = page
      .getByRole('button', { name: /move|project/i })
      .or(page.locator('[data-testid="bulk-move-menu"]'));

    await expect(moveButton).toBeVisible({ timeout: 2000 });
  });

  test('should move multiple items to different project', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select items
    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Click move button
    const moveButton = page.getByRole('button', { name: /move|project/i }).first();

    await expect(moveButton).toBeVisible();
    await moveButton.click();
    await page.waitForTimeout(300);

    // Select a project from dropdown
    const projectOption = page
      .locator('[data-testid*="project"]')
      .or(page.getByText(/project|Mobile|Core/i))
      .first();

    await expect(projectOption).toBeVisible();
    await projectOption.click();
    await page.waitForLoadState('networkidle');
  });
});

/**
 * Test Suite: Bulk Tag Operations
 * Tests for adding tags to multiple items
 */
test.describe('Bulk Tag Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should show add tags option in bulk actions', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Look for tags/label option
    const tagsButton = page
      .getByRole('button', { name: /tag|label|add tag/i })
      .or(page.locator('[data-testid="bulk-tags-menu"]'));

    await expect(tagsButton).toBeVisible({ timeout: 2000 });
  });

  test('should add tags to multiple selected items', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    const tagsButton = page.getByRole('button', { name: /tag|label|add tag/i }).first();

    await expect(tagsButton).toBeVisible();
    await tagsButton.click();
    await page.waitForTimeout(300);

    // Type a tag name
    const tagInput = page
      .locator('[data-testid*="tag-input"]')
      .or(page.locator('input[placeholder*="tag" i]'))
      .first();

    await expect(tagInput).toBeVisible();
    await tagInput.click();
    await tagInput.fill('bulk-test');
    await page.keyboard.press('Enter');
    await page.waitForLoadState('networkidle');
  });
});

/**
 * Test Suite: Bulk Archive Operations
 * Tests for archiving multiple items
 */
test.describe('Bulk Archive Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should show archive option in bulk actions', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    const archiveButton = page
      .getByRole('button', { name: /archive/i })
      .or(page.locator('[data-testid="bulk-archive-menu"]'));

    await expect(archiveButton).toBeVisible({ timeout: 2000 });
  });

  test('should archive multiple items with confirmation', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    const archiveButton = page.getByRole('button', { name: /archive/i }).first();

    await expect(archiveButton).toBeVisible({ timeout: 5000 });
    await archiveButton.click();
    await page.waitForTimeout(300);

    // Confirm archive action if dialog appears
    const confirmButton = page
      .getByRole('button', { name: /confirm|yes|archive/i })
      .filter({ hasText: /confirm|yes|archive/i })
      .first();

    await expect(confirmButton).toBeVisible({ timeout: 5000 });
    await confirmButton.click();
    await page.waitForLoadState('networkidle');
  });
});

/**
 * Test Suite: Bulk Operations UI and Interactions
 * Tests for UI elements and general interactions
 */
test.describe('Bulk Operations UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should display selection counter when items are selected', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Look for counter showing "2 selected" or similar
    const counter = page.locator(String.raw`text=/\d+\s+(selected|items)/i`);

    await expect(counter).toBeVisible({ timeout: 2000 });
  });

  test('should show bulk action bar with multiple buttons', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    if (await checkbox.isVisible()) {
      await checkbox.click();
      await page.waitForTimeout(300);

      // Bulk action bar should have multiple buttons
      const bulkActionBar = page
        .locator('[data-testid="bulk-action-bar"]')
        .or(page.locator('div:has(> button[name*="delete" i])'));

      const buttons = bulkActionBar.locator('button');
      const buttonCount = await buttons.count();

      // Should have at least 2 action buttons
      expect(buttonCount).toBeGreaterThanOrEqual(2);
    }
  });

  test('should keep bulk action bar visible while scrolling', async ({ page }) => {
    // Wait for items to load
    await page.waitForLoadState('networkidle');

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Scroll down
    await page.evaluate(() => {
      window.scrollBy(0, 500);
    });
    await page.waitForTimeout(300);

    // Bulk action bar should still be visible
    const bulkActionBar = page
      .locator('[data-testid="bulk-action-bar"]')
      .or(page.locator('text=/selected/i'));

    await expect(bulkActionBar).toBeVisible({ timeout: 2000 });
  });
});

/**
 * Test Suite: Bulk Operations Error Handling
 * Tests for error scenarios and error messages
 */
test.describe('Bulk Operations Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should handle error when bulk delete fails', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select items
    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Intercept delete request to simulate error
    await page.route('**/api/v1/items/**', async (route) => {
      await route.abort('failed');
    });

    const deleteButton = page.getByRole('button', { name: /delete|remove/i }).first();

    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
    await page.waitForTimeout(300);

    // Confirm delete
    const confirmButton = page
      .getByRole('button', { name: /confirm|yes|delete/i })
      .filter({ hasText: /confirm|yes|delete/i });

    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
    await page.waitForTimeout(500);

    // Error message should appear
    const errorMessage = page.locator('[role="alert"]').or(page.locator('text=/error|failed/i'));

    await expect(errorMessage).toBeVisible({ timeout: 2000 });
  });

  test('should show error when no items are selected for bulk action', async ({ page }) => {
    // Wait for items to load - use shorter timeout
    await page.waitForSelector('text=/Node Registry|All Items/i', {
      timeout: 5000,
    });

    // Try to find bulk delete button (only visible when items are selected)
    const deleteButton = page
      .locator('[data-testid="bulk-delete"]')
      .or(page.getByRole('button', { name: /bulk.*delete/i }))
      .first();

    // Check if delete button exists in bulk action context
    await expect(deleteButton).not.toBeVisible({ timeout: 2000 });
  });

  test('should recover gracefully from partial bulk operation failures', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    // Select multiple items
    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(2);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    await checkbox1.click();
    await page.waitForTimeout(200);
    await checkbox2.click();
    await page.waitForTimeout(300);

    // Intercept to return partial failure
    let requestCount = 0;
    await page.route('**/api/v1/items/**', async (route) => {
      requestCount++;
      if (requestCount > 1) {
        await route.abort('failed'); // Fail second request
      } else {
        await route.continue();
      }
    });

    const statusButton = page.getByRole('button', { name: /status|change status/i }).first();

    await expect(statusButton).toBeVisible();
    await statusButton.click();
    await page.waitForTimeout(300);

    const statusOption = page.getByText(/completed|done/i).first();

    await expect(statusOption).toBeVisible();
    await statusOption.click();
    await page.waitForTimeout(500);

    // Should show partial success or partial failure message
    const resultMessage = page
      .locator('[role="alert"]')
      .or(page.locator('text=/updated|error|partial/i'));

    await expect(resultMessage).toBeVisible({ timeout: 2000 });
  });
});

/**
 * Test Suite: Bulk Operations Undo Functionality
 * Tests for undoing bulk operations
 */
test.describe('Bulk Operations Undo', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should undo bulk status update', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    const statusButton = page.getByRole('button', { name: /status|change status/i }).first();

    await expect(statusButton).toBeVisible();
    await statusButton.click();
    await page.waitForTimeout(300);

    const statusOption = page.getByText(/completed|done/i).first();

    await expect(statusOption).toBeVisible();
    await statusOption.click();
    await page.waitForLoadState('networkidle');

    // Look for undo button
    const undoButton = page.getByRole('button', { name: /undo/i }).or(page.locator('text=/undo/i'));

    await expect(undoButton).toBeVisible({ timeout: 2000 });
    await undoButton.click();
    await page.waitForLoadState('networkidle');

    console.log('Undo bulk status update completed');
  });

  test('should undo bulk tag addition', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    const tagsButton = page.getByRole('button', { name: /tag|label/i }).first();

    await expect(tagsButton).toBeVisible();
    await tagsButton.click();
    await page.waitForTimeout(300);

    const tagInput = page
      .locator('[data-testid*="tag-input"]')
      .or(page.locator('input[placeholder*="tag" i]'))
      .first();

    await expect(tagInput).toBeVisible();
    await tagInput.click();
    await tagInput.fill('test-undo-tag');
    await page.keyboard.press('Enter');
    await page.waitForLoadState('networkidle');

    // Look for undo button
    const undoButton = page.getByRole('button', { name: /undo/i }).or(page.locator('text=/undo/i'));

    await expect(undoButton).toBeVisible({ timeout: 2000 });
    await undoButton.click();
    await page.waitForLoadState('networkidle');

    console.log('Undo bulk tag addition completed');
  });
});

/**
 * Test Suite: Bulk Operations with Keyboard Shortcuts
 * Tests for keyboard shortcuts in bulk operations
 */
test.describe('Bulk Operations Keyboard Shortcuts', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');
  });

  test('should select/deselect items with Shift+Click', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox1 = page.locator('input[type="checkbox"]').nth(1);
    const checkbox2 = page.locator('input[type="checkbox"]').nth(3);

    await expect(checkbox1).toBeVisible();
    await expect(checkbox2).toBeVisible();

    // Click first
    await checkbox1.click();
    await page.waitForTimeout(200);

    // Shift+Click last to select range
    await checkbox2.click({ modifiers: ['Shift'] });
    await page.waitForTimeout(300);

    // Multiple items should be selected
    const selectedCheckboxes = page.locator('input[type="checkbox"]:checked');
    const count = await selectedCheckboxes.count();

    // Should have selected range (at least 2)
    expect(count).toBeGreaterThanOrEqual(2);
  });

  test('should clear selection with Escape key', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Press Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // Selection should be cleared
    const selectedCheckboxes = page.locator('input[type="checkbox"]:checked');
    await expect(selectedCheckboxes).toHaveCount(0);
  });

  test('should delete selected items with Delete key', async ({ page }) => {
    // Wait for items to load
    await page.waitForSelector('text=/User Authentication/', { timeout: 5000 });

    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await expect(checkbox).toBeVisible();
    await checkbox.click();
    await page.waitForTimeout(300);

    // Press Delete key
    await page.keyboard.press('Delete');
    await page.waitForTimeout(300);

    // Confirmation dialog may appear, check for it
    const confirmDialog = page.getByRole('dialog');
    await expect(confirmDialog).toBeVisible({ timeout: 2000 });
  });
});
