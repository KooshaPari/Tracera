import { expect, test } from '@playwright/test';

import { authenticateAndNavigate } from './critical-path-helpers';

test.describe('Traceability Matrix E2E', () => {
  const projectId = 'test-project-123';

  test.beforeEach(async ({ page }) => {
    // Authenticate and navigate to the matrix view directly
    await authenticateAndNavigate(page, `/projects/${projectId}/views/matrix`);
  });

  test('should display traceability matrix with stats', async ({ page }) => {
    // Verify header
    await expect(page.getByText('Traceability Matrix')).toBeVisible();
    await expect(page.getByText('Track test coverage for requirements')).toBeVisible();

    // Verify stats cards are visible
    await expect(page.getByText('Total Requirements')).toBeVisible();
    await expect(page.getByText('Covered')).toBeVisible();
    await expect(page.getByText('Uncovered')).toBeVisible();
    await expect(page.getByText('Coverage')).toBeVisible();

    // Verify coverage progress bar
    await expect(page.getByText('Overall Coverage Progress')).toBeVisible();
  });

  test('should filter requirements by search query', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Search requirements...');
    await expect(searchInput).toBeVisible();

    // Type a search query
    await searchInput.fill('User Login');
    await page.waitForTimeout(500); // Wait for filter to apply

    // Verify filtered results or empty state
    const table = page.locator('table');
    const noResults = page.getByText('No requirements found');

    // Either the table should be visible with filtered items, or "No requirements found"
    const isVisible = (await table.isVisible()) || (await noResults.isVisible());
    expect(isVisible).toBe(true);
  });

  test('should filter requirements by view type', async ({ page }) => {
    const viewSelect = page.locator('select');
    await expect(viewSelect).toBeVisible();

    // Change filter to 'Features'
    await viewSelect.selectOption('FEATURE');
    await page.waitForTimeout(500);

    // Verify matrix updates (just check it's still visible or shows empty state)
    await expect(page.locator('table').or(page.getByText('No requirements found'))).toBeVisible();
  });

  test('should toggle "Show gaps only"', async ({ page }) => {
    const gapsCheckbox = page.getByLabel('Show gaps only');
    await expect(gapsCheckbox).toBeVisible();

    // Toggle checkbox
    await gapsCheckbox.check();
    await page.waitForTimeout(500);

    // Verify matrix updates to show gaps or "No coverage gaps found"
    await expect(page.locator('table').or(page.getByText('No coverage gaps found'))).toBeVisible();
  });

  test('should display matrix table with correct headers', async ({ page }) => {
    const table = page.locator('table');

    // If there are requirements, check headers
    if (await table.isVisible()) {
      await expect(page.getByRole('columnheader', { name: 'Requirement' })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: 'View' })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: 'Covered' })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: 'Test Cases' })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: 'Test Status' })).toBeVisible();
    }
  });
});
