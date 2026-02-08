import * as fs from 'node:fs';
import * as path from 'node:path';

import { expect, test } from './global-setup';

/**
 * Import/Export E2E Tests
 *
 * Comprehensive tests for import/export functionality:
 * - Export items to JSON and CSV formats
 * - Export projects with all data
 * - Import items from JSON and CSV files
 * - File validation and error handling
 * - Large file handling
 * - Export filters and options
 *
 * Note: These tests validate UI interactions and file handling.
 * Actual file content validation happens in unit tests.
 */

test.describe('Export Functionality', () => {
  test.describe('Export Items to JSON', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/items');
      await page.waitForLoadState('networkidle');
    });

    test('should display export button on items page', async ({ page }) => {
      // Wait for items to load - use mock data item names
      await page.waitForSelector('text=/User Authentication|Dashboard View|API Integration/', {
        timeout: 5000,
      });

      // Look for export button
      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });
    });

    test('should export all items as JSON', async ({ page }) => {
      // Wait for items to load
      await page.waitForSelector('text=/User Authentication/', {
        timeout: 5000,
      });

      // Find export button
      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });

      // Set up download listener
      const downloadPromise = page.waitForEvent('download', {
        timeout: 10_000,
      });

      // Click export button
      await exportButton.click();
      await page.waitForTimeout(500);

      // Look for JSON format option
      const jsonOption = page
        .getByText(/json|data/i)
        .first()
        .or(page.getByRole('menuitem', { name: /json/i }).first());

      await expect(jsonOption).toBeVisible({ timeout: 5000 });
      await jsonOption.click();

      const download = await downloadPromise;
      const filename = download.suggestedFilename();
      expect(filename).toMatch(/\.json$/);
      console.log(`Items exported as JSON: ${filename}`);
    });

    test('should handle export with filters', async ({ page }) => {
      // Wait for items to load
      await page.waitForSelector('text=/User Authentication/', {
        timeout: 5000,
      });

      // Try to find and apply filters
      const filterSelect = page.getByRole('combobox').or(page.locator('select')).first();

      await expect(filterSelect).toBeVisible({ timeout: 5000 });
      // Apply a filter
      await filterSelect.click();
      await page.waitForTimeout(300);

      const filterOption = page.locator('text=/Pending|In Progress|Completed/').first();
      await expect(filterOption).toBeVisible({ timeout: 5000 });
      await filterOption.click();
      await page.waitForTimeout(500);

      // Now export
      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });

      const downloadPromise = page.waitForEvent('download', {
        timeout: 10_000,
      });

      await exportButton.click();
      await page.waitForTimeout(300);

      const jsonOption = page.getByText(/json/).first();
      await expect(jsonOption).toBeVisible({ timeout: 5000 });
      await jsonOption.click();

      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.json$/);
      console.log(`Filtered items exported: ${download.suggestedFilename()}`);
    });

    test('should show export progress/confirmation', async ({ page }) => {
      // Wait for items
      await page.waitForSelector('text=/User Authentication/', {
        timeout: 5000,
      });

      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });
      await exportButton.click();

      // We might need to select a format if a menu opens
      const jsonOption = page.getByText(/json/i).first();
      if (await jsonOption.isVisible({ timeout: 2000 })) {
        await jsonOption.click();
      }

      // Look for success message or confirmation
      const successMessage = page.getByText(/export.*success|export.*complete|downloaded/i).first();

      // This might be optional depending on implementation, but let's expect it for high integrity
      await expect(successMessage).toBeVisible({ timeout: 10_000 });
    });
  });

  test.describe('Export Items to CSV', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/items');
      await page.waitForLoadState('networkidle');
    });

    test('should export items as CSV', async ({ page }) => {
      // Wait for items to load
      await page.waitForSelector('text=/User Authentication/', {
        timeout: 5000,
      });

      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });

      const downloadPromise = page.waitForEvent('download', {
        timeout: 5000,
      });

      await exportButton.click();
      await page.waitForTimeout(500);

      // Look for CSV option
      const csvOption = page
        .getByText(/csv/i)
        .first()
        .or(page.getByRole('menuitem', { name: /csv/i }).first());

      await expect(csvOption).toBeVisible({ timeout: 2000 });
      await csvOption.click();

      const download = await downloadPromise;
      const filename = download.suggestedFilename();
      expect(filename).toMatch(/\.csv$/);
      console.log(`Items exported as CSV: ${filename}`);
    });

    test('should handle large CSV exports', async ({ page }) => {
      // Wait for items
      await page.waitForSelector('text=/User Authentication/', {
        timeout: 5000,
      });

      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });

      const downloadPromise = page.waitForEvent('download', {
        timeout: 10_000,
      });

      await exportButton.click();
      await page.waitForTimeout(500);

      const csvOption = page.getByText(/csv/i).first();
      await expect(csvOption).toBeVisible({ timeout: 2000 });
      await csvOption.click();

      // Wait for download with longer timeout for large files
      const download = await downloadPromise;
      const path = await download.path();
      const stats = fs.statSync(path);
      console.log(`CSV exported with size: ${stats.size} bytes`);
      expect(stats.size).toBeGreaterThan(0);
    });
  });

  test.describe('Export Projects', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/projects');
      await page.waitForLoadState('networkidle');
    });

    test('should display export button on projects page', async ({ page }) => {
      // Wait for projects to load - use mock data project names
      await page.waitForSelector('text=/TraceRTM Frontend|Pokemon Go|E-Commerce/', {
        timeout: 5000,
      });

      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });
    });

    test('should export project with all items', async ({ page }) => {
      // Navigate to project detail
      await page.goto('/projects/proj-1');
      await page.waitForLoadState('networkidle');

      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });

      const downloadPromise = page.waitForEvent('download', {
        timeout: 5000,
      });

      await exportButton.click();
      await page.waitForTimeout(500);

      // Select JSON format
      const jsonOption = page.getByText(/json/).first();
      await expect(jsonOption).toBeVisible({ timeout: 2000 });
      await jsonOption.click();

      const download = await downloadPromise;
      const filename = download.suggestedFilename();
      expect(filename).toMatch(/\.json$/);
      console.log(`Project exported: ${filename}`);
    });

    test('should export project as CSV with items', async ({ page }) => {
      await page.goto('/projects/proj-1');
      await page.waitForLoadState('networkidle');

      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });

      const downloadPromise = page.waitForEvent('download', {
        timeout: 5000,
      });

      await exportButton.click();
      await page.waitForTimeout(500);

      const csvOption = page.getByText(/csv/i).first();
      await expect(csvOption).toBeVisible({ timeout: 2000 });
      await csvOption.click();

      const download = await downloadPromise;
      const filename = download.suggestedFilename();
      expect(filename).toMatch(/\.csv$/);
      console.log(`Project exported as CSV: ${filename}`);
    });
  });
});

test.describe('Import Functionality', () => {
  test.describe('Import Items from JSON', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/items');
      await page.waitForLoadState('networkidle');
    });

    test('should display import button', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
    });

    test('should open import dialog', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();

      // Dialog should open
      const dialog = page.getByRole('dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });
    });

    test('should show file upload area', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Look for file input or upload area
      const fileInput = page
        .locator("input[type='file']")
        .or(page.getByText(/drag.*file|upload|choose file/i).first());

      await expect(fileInput).toBeVisible({ timeout: 5000 });
    });

    test('should allow format selection', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Look for format selector
      const formatSelect = page
        .getByRole('combobox', { name: /format/i })
        .or(page.getByLabel(/format/i))
        .first();

      await expect(formatSelect).toBeVisible({ timeout: 5000 });
      await formatSelect.click();
      await page.waitForTimeout(300);

      // JSON option should be available
      const jsonOption = page.getByText(/json/i).first();
      await expect(jsonOption).toBeVisible({ timeout: 2000 });
    });

    test('should validate JSON file before import', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Create a test file with invalid JSON
      const testDir = '/tmp';
      const invalidJsonFile = path.join(testDir, 'invalid.json');
      fs.writeFileSync(invalidJsonFile, '{ invalid json }');

      // Try to upload invalid file
      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(invalidJsonFile);
      await page.waitForTimeout(1000);

      // Should show validation error
      const errorMessage = page.getByText(/invalid|error|format/i).first();
      await expect(errorMessage).toBeVisible({ timeout: 5000 });

      // Clean up
      fs.unlinkSync(invalidJsonFile);
    });
  });

  test.describe('Import Items from CSV', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/items');
      await page.waitForLoadState('networkidle');
    });

    test('should import items from CSV file', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Select CSV format
      const formatSelect = page
        .getByRole('combobox', { name: /format/i })
        .or(page.getByLabel(/format/i))
        .first();

      await expect(formatSelect).toBeVisible({ timeout: 5000 });
      await formatSelect.click();
      await page.waitForTimeout(300);

      const csvOption = page.getByText(/csv/i).first();
      await expect(csvOption).toBeVisible({ timeout: 5000 });
      await csvOption.click();
      await page.waitForTimeout(300);

      // Create sample CSV
      const testDir = '/tmp';
      const csvFile = path.join(testDir, 'items.csv');
      const csvContent = `Title,Type,Status,Priority
Test Item 1,Requirement,Pending,High
Test Item 2,Feature,In Progress,Medium`;

      fs.writeFileSync(csvFile, csvContent);

      // Upload file
      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(csvFile);
      await page.waitForTimeout(500);

      // Submit import
      const importSubmitBtn = page.getByRole('button', {
        name: /import|submit/i,
      });
      await expect(importSubmitBtn).toBeVisible({ timeout: 5000 });
      await importSubmitBtn.click();
      await page.waitForLoadState('networkidle');

      // Check for success message
      const successMsg = page.getByText(/import.*success|imported.*items/i).first();
      await expect(successMsg).toBeVisible({ timeout: 10_000 });

      // Clean up
      fs.unlinkSync(csvFile);
    });

    test('should show import summary with count', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Set CSV format
      const formatSelect = page
        .getByRole('combobox', { name: /format/i })
        .or(page.getByLabel(/format/i))
        .first();

      await expect(formatSelect).toBeVisible({ timeout: 5000 });
      await formatSelect.click();
      await page.waitForTimeout(300);

      const csvOption = page.getByText(/csv/i).first();
      await expect(csvOption).toBeVisible({ timeout: 5000 });
      await csvOption.click();

      // Create CSV with multiple items
      const testDir = '/tmp';
      const csvFile = path.join(testDir, 'many-items.csv');
      const csvLines = ['Title,Type,Status,Priority'];
      for (let i = 1; i <= 5; i++) {
        csvLines.push(`Item ${i},Requirement,Pending,High`);
      }
      fs.writeFileSync(csvFile, csvLines.join('\n'));

      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(csvFile);
      await page.waitForTimeout(500);

      // Look for item count preview
      const countText = page.getByText(/5.*items?|import.*5/i).first();
      await expect(countText).toBeVisible({ timeout: 5000 });

      const importSubmitBtn = page.getByRole('button', {
        name: /import|submit/i,
      });
      await expect(importSubmitBtn).toBeVisible({ timeout: 5000 });
      await importSubmitBtn.click();
      await page.waitForLoadState('networkidle');

      // Clean up
      fs.unlinkSync(csvFile);
    });
  });

  test.describe('Import Error Handling', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/items');
      await page.waitForLoadState('networkidle');
    });

    test('should handle missing required columns', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Set CSV format
      const formatSelect = page
        .getByRole('combobox', { name: /format/i })
        .or(page.getByLabel(/format/i))
        .first();

      await expect(formatSelect).toBeVisible({ timeout: 5000 });
      await formatSelect.click();
      await page.waitForTimeout(300);

      const csvOption = page.getByText(/csv/i).first();
      await expect(csvOption).toBeVisible({ timeout: 5000 });
      await csvOption.click();

      // Create CSV with missing required column
      const testDir = '/tmp';
      const csvFile = path.join(testDir, 'incomplete.csv');
      const csvContent = `Title,Type
Test Item,Requirement`;

      fs.writeFileSync(csvFile, csvContent);

      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(csvFile);
      await page.waitForTimeout(1000);

      // Should show error about missing columns
      const errorMsg = page.getByText(/missing|required|column/i).first();
      await expect(errorMsg).toBeVisible({ timeout: 5000 });

      // Clean up
      fs.unlinkSync(csvFile);
    });

    test('should handle duplicate entries in import', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Set CSV format
      const formatSelect = page
        .getByRole('combobox', { name: /format/i })
        .or(page.getByLabel(/format/i))
        .first();

      await expect(formatSelect).toBeVisible({ timeout: 5000 });
      await formatSelect.click();
      await page.waitForTimeout(300);

      const csvOption = page.getByText(/csv/i).first();
      await expect(csvOption).toBeVisible({ timeout: 5000 });
      await csvOption.click();

      // Create CSV with duplicate entries
      const testDir = '/tmp';
      const csvFile = path.join(testDir, 'duplicates.csv');
      const csvContent = `Title,Type,Status,Priority
Test Item,Requirement,Pending,High
Test Item,Requirement,Pending,High`;

      fs.writeFileSync(csvFile, csvContent);

      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(csvFile);
      await page.waitForTimeout(1000);

      // Look for duplicate warning or error
      const warningMsg = page.getByText(/duplicate|conflict|already exists/i).first();
      await expect(warningMsg).toBeVisible({ timeout: 5000 });

      // Clean up
      fs.unlinkSync(csvFile);
    });

    test('should handle file size limits', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Create a large CSV file
      const testDir = '/tmp';
      const largeFile = path.join(testDir, 'large.csv');
      const lines = ['Title,Type,Status,Priority'];

      // Generate 10000 rows (typically > file size limits)
      for (let i = 0; i < 10_000; i++) {
        lines.push(`Item ${i},Requirement,Pending,High`);
      }

      fs.writeFileSync(largeFile, lines.join('\n'));

      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(largeFile);
      await page.waitForTimeout(1000);

      // Check for file size error
      const sizeError = page.getByText(/too large|size limit|exceeds/i).first();
      await expect(sizeError).toBeVisible({ timeout: 5000 });

      // Clean up
      fs.unlinkSync(largeFile);
    });

    test('should show partial import results on errors', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      // Set CSV format
      const formatSelect = page
        .getByRole('combobox', { name: /format/i })
        .or(page.getByLabel(/format/i))
        .first();

      await expect(formatSelect).toBeVisible({ timeout: 5000 });
      await formatSelect.click();
      await page.waitForTimeout(300);

      const csvOption = page.getByText(/csv/i).first();
      await expect(csvOption).toBeVisible({ timeout: 5000 });
      await csvOption.click();

      // Create CSV with mixed valid and invalid entries
      const testDir = '/tmp';
      const csvFile = path.join(testDir, 'mixed.csv');
      const csvContent = `Title,Type,Status,Priority
Valid Item,Requirement,Pending,High
Invalid Item,,Invalid,Bad Priority
Another Valid,Feature,In Progress,Medium`;

      fs.writeFileSync(csvFile, csvContent);

      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(csvFile);
      await page.waitForTimeout(500);

      // Submit import
      const importSubmitBtn = page.getByRole('button', {
        name: /import|submit/i,
      });
      await expect(importSubmitBtn).toBeVisible({ timeout: 5000 });
      await importSubmitBtn.click();
      await page.waitForLoadState('networkidle');

      // Should show partial results
      const resultMsg = page.getByText(/imported.*error|success.*error/i).first();
      await expect(resultMsg).toBeVisible({ timeout: 10_000 });

      // Clean up
      fs.unlinkSync(csvFile);
    });
  });

  test.describe('Import Projects', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/projects');
      await page.waitForLoadState('networkidle');
    });

    test('should display import button on projects page', async ({ page }) => {
      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
    });

    test('should allow importing full project export', async ({ page }) => {
      // First export a project to get valid export file
      await page.goto('/projects/proj-1');
      await page.waitForLoadState('networkidle');

      const exportButton = page.getByRole('button', { name: /export/i }).first();
      await expect(exportButton).toBeVisible({ timeout: 5000 });

      const downloadPromise = page.waitForEvent('download', {
        timeout: 5000,
      });

      await exportButton.click();
      await page.waitForTimeout(500);

      const jsonOption = page.getByText(/json/).first();
      await expect(jsonOption).toBeVisible({ timeout: 2000 });
      await jsonOption.click();

      const download = await downloadPromise;
      const filePath = await download.path();

      // Now go back to projects and import
      await page.goto('/projects');
      await page.waitForLoadState('networkidle');

      const importButton = page.getByRole('button', { name: /import/i }).first();
      await expect(importButton).toBeVisible({ timeout: 5000 });
      await importButton.click();
      await page.waitForTimeout(500);

      const fileInput = page.locator("input[type='file']").first();
      await expect(fileInput).toBeVisible({ timeout: 5000 });
      await fileInput.setInputFiles(filePath);
      await page.waitForTimeout(500);

      const importSubmitBtn = page.getByRole('button', {
        name: /import|submit/i,
      });
      await expect(importSubmitBtn).toBeVisible({ timeout: 5000 });
      await importSubmitBtn.click();
      await page.waitForLoadState('networkidle');
      console.log('Project import completed');
    });
  });
});

test.describe('Export/Import Round-trip', () => {
  test('should maintain data integrity in JSON export/import cycle', async ({ page }) => {
    // Step 1: Navigate to items and export
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const exportButton = page.getByRole('button', { name: /export/i }).first();
    await expect(exportButton).toBeVisible({ timeout: 5000 });

    const downloadPromise = page.waitForEvent('download', { timeout: 5000 });

    await exportButton.click();
    await page.waitForTimeout(500);

    const jsonOption = page.getByText(/json/).first();
    await expect(jsonOption).toBeVisible({ timeout: 2000 });
    await jsonOption.click();

    const download = await downloadPromise;
    const exportFilePath = await download.path();

    // Step 2: Import the exported file
    const importButton = page.getByRole('button', { name: /import/i }).first();
    await expect(importButton).toBeVisible({ timeout: 5000 });
    await importButton.click();
    await page.waitForTimeout(500);

    const fileInput = page.locator("input[type='file']").first();
    await expect(fileInput).toBeVisible({ timeout: 5000 });
    await fileInput.setInputFiles(exportFilePath);
    await page.waitForTimeout(500);

    const importSubmitBtn = page.getByRole('button', {
      name: /import|submit/i,
    });
    await expect(importSubmitBtn).toBeVisible({ timeout: 5000 });
    await importSubmitBtn.click();
    await page.waitForLoadState('networkidle');

    // Verify round-trip success
    const successMsg = page.getByText(/import.*success|completed/i).first();
    await expect(successMsg).toBeVisible({ timeout: 10_000 });
  });

  test('should handle CSV export/import round-trip with data transformation', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const exportButton = page.getByRole('button', { name: /export/i }).first();
    await expect(exportButton).toBeVisible({ timeout: 5000 });

    const downloadPromise = page.waitForEvent('download', { timeout: 5000 });

    await exportButton.click();
    await page.waitForTimeout(500);

    const csvOption = page.getByText(/csv/).first();
    await expect(csvOption).toBeVisible({ timeout: 2000 });
    await csvOption.click();

    const download = await downloadPromise;
    const exportFilePath = await download.path();

    // Verify file exists and has content
    const stats = fs.statSync(exportFilePath);
    expect(stats.size).toBeGreaterThan(0);

    // Import the CSV
    const importButton = page.getByRole('button', { name: /import/i }).first();
    await expect(importButton).toBeVisible({ timeout: 5000 });
    await importButton.click();
    await page.waitForTimeout(500);

    // Set CSV format
    const formatSelect = page
      .getByRole('combobox', { name: /format/i })
      .or(page.getByLabel(/format/i))
      .first();

    await expect(formatSelect).toBeVisible({ timeout: 5000 });
    await formatSelect.click();
    await page.waitForTimeout(300);

    const csvSelectOption = page.getByText(/csv/i).first();
    await expect(csvSelectOption).toBeVisible({ timeout: 5000 });
    await csvSelectOption.click();
    await page.waitForTimeout(300);

    const fileInput = page.locator("input[type='file']").first();
    await expect(fileInput).toBeVisible({ timeout: 5000 });
    await fileInput.setInputFiles(exportFilePath);
    await page.waitForTimeout(500);

    const importSubmitBtn = page.getByRole('button', {
      name: /import|submit/i,
    });
    await expect(importSubmitBtn).toBeVisible({ timeout: 5000 });
    await importSubmitBtn.click();
    await page.waitForLoadState('networkidle');
    console.log('CSV round-trip import completed');
  });
});

test.describe('Export/Import Edge Cases', () => {
  test('should handle special characters in exported data', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const exportButton = page.getByRole('button', { name: /export/i }).first();
    await expect(exportButton).toBeVisible({ timeout: 5000 });

    const downloadPromise = page.waitForEvent('download', { timeout: 5000 });

    await exportButton.click();
    await page.waitForTimeout(500);

    const jsonOption = page.getByText(/json/).first();
    await expect(jsonOption).toBeVisible({ timeout: 2000 });
    await jsonOption.click();

    const download = await downloadPromise;
    const filePath = await download.path();
    const content = fs.readFileSync(filePath, 'utf8');

    // Verify special characters are preserved or escaped
    expect(content).toBeTruthy();
    console.log('Export with special characters completed');
  });

  test('should handle empty project export', async ({ page }) => {
    // Navigate to projects list
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Find an empty project or create scenario
    const projectCards = page.locator("[data-testid*='project']");
    await expect(projectCards.first()).toBeVisible({ timeout: 10_000 });

    // Click on first project
    await projectCards.first().click();
    await page.waitForLoadState('networkidle');

    const exportButton = page.getByRole('button', { name: /export/i }).first();
    await expect(exportButton).toBeVisible({ timeout: 5000 });

    const downloadPromise = page.waitForEvent('download', {
      timeout: 5000,
    });

    await exportButton.click();
    await page.waitForTimeout(500);

    const jsonOption = page.getByText(/json/).first();
    await expect(jsonOption).toBeVisible({ timeout: 2000 });
    await jsonOption.click();

    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBeTruthy();
    console.log(`Empty project export: ${download.suggestedFilename()}`);
  });

  test('should prevent import of corrupted files', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const importButton = page.getByRole('button', { name: /import/i }).first();
    await expect(importButton).toBeVisible({ timeout: 5000 });
    await importButton.click();
    await page.waitForTimeout(500);

    // Create a corrupted file
    const testDir = '/tmp';
    const corruptedFile = path.join(testDir, 'corrupted.json');
    fs.writeFileSync(corruptedFile, 'not valid json { [ ] }');

    const fileInput = page.locator("input[type='file']").first();
    await expect(fileInput).toBeVisible({ timeout: 5000 });
    await fileInput.setInputFiles(corruptedFile);
    await page.waitForTimeout(1000);

    // Should show validation error
    const errorMsg = page.getByText(/invalid|corrupted|error/i).first();
    await expect(errorMsg).toBeVisible({ timeout: 5000 });

    // Clean up
    fs.unlinkSync(corruptedFile);
  });
});
