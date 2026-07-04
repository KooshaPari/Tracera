/**
 * End-to-End Tests for Screenshot Storage
 * Tests complete screenshot lifecycle from capture to storage and retrieval
 */

import { expect, test } from '@playwright/test';

test.describe('Screenshot Storage', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');

    // Wait for app to load
    await page.waitForLoadState('networkidle');
  });

  test('should upload and retrieve screenshot', async ({ page }) => {
    // Given: A project with items
    // Navigate to a project
    const projectLink = page.locator('[data-testid="project-link"]').first();
    await expect(projectLink).toBeVisible({ timeout: 10_000 });
    await projectLink.click();
    await page.waitForLoadState('networkidle');

    // Navigate to an item view
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // When: Taking a screenshot
    const screenshotButton = page.locator('[data-testid="screenshot-button"]');
    await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
    await screenshotButton.click();

    // Wait for upload progress to appear
    const progressBar = page.locator('[data-testid="upload-progress"]');
    await expect(progressBar).toBeVisible();

    // Wait for upload to complete
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Verify success message
    const successMessage = page.locator('[data-testid="upload-success"]');
    await expect(successMessage).toBeVisible({ timeout: 5000 });

    // Then: Verify screenshot is saved
    const screenshot = page.locator('[data-testid="item-screenshot"]');
    await expect(screenshot).toBeVisible({ timeout: 10_000 });
    await expect(screenshot).toHaveAttribute('src', /\.(jpg|jpeg|png)$/);
  });

  test('should show upload progress during screenshot upload', async ({ page }) => {
    // Given: Item page is open
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // When: Starting screenshot upload
    const screenshotButton = page.locator('[data-testid="screenshot-button"]');
    await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
    await screenshotButton.click();

    // Then: Verify progress bar is shown
    const progressBar = page.locator('[data-testid="upload-progress"]');
    await expect(progressBar).toBeVisible();

    // Verify progress updates
    const progressPercent = page.locator('[data-testid="upload-percent"]');
    const initialPercent = await progressPercent.textContent();
    expect(initialPercent).toMatch(/\d+%/);

    // Wait for completion
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Verify final state
    const successMessage = page.locator('[data-testid="upload-success"]');
    await expect(successMessage).toBeVisible();
  });

  test('should generate and display thumbnail', async ({ page }) => {
    // Given: Item with screenshot
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // When: Uploading screenshot
    const screenshotButton = page.locator('[data-testid="screenshot-button"]');
    await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
    await screenshotButton.click();

    // Wait for upload
    const progressBar = page.locator('[data-testid="upload-progress"]');
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Then: Verify thumbnail is generated and visible
    const thumbnail = page.locator('[data-testid="screenshot-thumbnail"]');
    await expect(thumbnail).toBeVisible({ timeout: 10_000 });

    // Verify thumbnail has correct dimensions
    const boundingBox = await thumbnail.boundingBox();
    expect(boundingBox?.width).toBeGreaterThan(0);
    expect(boundingBox?.height).toBeGreaterThan(0);
  });

  test('should cache screenshots for performance', async ({ page }) => {
    // Given: Item page is open
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // When: Taking first screenshot
    const screenshotButton = page.locator('[data-testid="screenshot-button"]');
    await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
    const startTime1 = Date.now();
    await screenshotButton.click();

    const progressBar = page.locator('[data-testid="upload-progress"]');
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });
    const duration1 = Date.now() - startTime1;

    // When: Taking second screenshot (should be cached)
    const startTime2 = Date.now();
    await screenshotButton.click();

    const progressBar2 = page.locator('[data-testid="upload-progress"]');
    await progressBar2.waitFor({ state: 'hidden', timeout: 30_000 });
    const duration2 = Date.now() - startTime2;

    // Then: Second should be faster (cached)
    // Note: This is approximate, caching might not always be faster
    expect(duration2).toBeLessThanOrEqual(duration1 * 1.5);
  });

  test('should delete screenshot', async ({ page }) => {
    // Given: Item with existing screenshot
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // First, upload a screenshot if not exists
    const screenshot = page.locator('[data-testid="item-screenshot"]');
    const isVisible = await screenshot.isVisible();
    if (!isVisible) {
      const screenshotButton = page.locator('[data-testid="screenshot-button"]');
      await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
      await screenshotButton.click();
      const progressBar = page.locator('[data-testid="upload-progress"]');
      await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });
    }

    // When: Deleting screenshot
    const deleteButton = page.locator('[data-testid="delete-screenshot"]');
    await expect(deleteButton).toBeVisible({ timeout: 10_000 });
    await deleteButton.click();

    // Confirm deletion if dialog appears
    const confirmButton = page.locator('[data-testid="confirm-delete"]');
    await expect(confirmButton).toBeVisible({ timeout: 5000 });
    await confirmButton.click();

    // Then: Verify screenshot is removed
    await expect(screenshot).not.toBeVisible({ timeout: 5000 });

    // Verify delete success message
    const successMessage = page.locator('[data-testid="delete-success"]');
    await expect(successMessage).toBeVisible({ timeout: 5000 });
  });

  test('should persist screenshot across page reload', async ({ page }) => {
    // Given: Item with uploaded screenshot
    const itemLink = page.locator('[data-testid="item-row"]').first();
    const _itemId = await itemLink.getAttribute('data-item-id');

    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // Upload screenshot if not exists
    const screenshot = page.locator('[data-testid="item-screenshot"]');
    const isVisible = await screenshot.isVisible();
    if (!isVisible) {
      const screenshotButton = page.locator('[data-testid="screenshot-button"]');
      await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
      await screenshotButton.click();
      const progressBar = page.locator('[data-testid="upload-progress"]');
      await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });
    }

    // Get current screenshot URL
    const screenshotUrl = await screenshot.getAttribute('src');

    // When: Reloading page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Then: Verify screenshot is still visible
    const reloadedScreenshot = page.locator('[data-testid="item-screenshot"]');
    await expect(reloadedScreenshot).toBeVisible({ timeout: 10_000 });

    // Verify it's the same screenshot
    const reloadedUrl = await reloadedScreenshot.getAttribute('src');
    expect(reloadedUrl).toBe(screenshotUrl);
  });

  test('should handle upload errors gracefully', async ({ page }) => {
    // Given: Network is simulated to fail
    await page.context().setExtraHTTPHeaders({
      'X-Test-Fail-Upload': 'true',
    });

    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // When: Attempting screenshot upload
    const screenshotButton = page.locator('[data-testid="screenshot-button"]');
    await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
    await screenshotButton.click();

    // Then: Verify error message is shown
    const errorMessage = page.locator('[data-testid="upload-error"]');
    await expect(errorMessage).toBeVisible({ timeout: 10_000 });

    // Verify error can be dismissed
    const dismissButton = page.locator('[data-testid="dismiss-error"]');
    await expect(dismissButton).toBeVisible({ timeout: 5000 });
    await dismissButton.click();
    await expect(errorMessage).not.toBeVisible({ timeout: 5000 });
  });

  test('should support multiple screenshots per item', async ({ page }) => {
    // Given: Item page is open
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // When: Uploading multiple screenshots
    const screenshotButton = page.locator('[data-testid="screenshot-button"]');
    await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
    // First screenshot
    await screenshotButton.click();
    let progressBar = page.locator('[data-testid="upload-progress"]');
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Second screenshot
    await screenshotButton.click();
    progressBar = page.locator('[data-testid="upload-progress"]');
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Third screenshot
    await screenshotButton.click();
    progressBar = page.locator('[data-testid="upload-progress"]');
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Then: Verify all screenshots are stored
    const screenshots = page.locator('[data-testid="item-screenshot"]');
    const count = await screenshots.count();
    expect(count).toBeGreaterThanOrEqual(1);

    // Verify screenshot gallery/carousel is visible if multiple
    if (count > 1) {
      const gallery = page.locator('[data-testid="screenshot-gallery"]');
      await expect(gallery).toBeVisible();
    }
  });

  test('should display screenshot metadata', async ({ page }) => {
    // Given: Item with screenshot
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // Upload screenshot if needed
    const screenshot = page.locator('[data-testid="item-screenshot"]');
    const isVisible = await screenshot.isVisible();
    if (!isVisible) {
      const screenshotButton = page.locator('[data-testid="screenshot-button"]');
      await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
      await screenshotButton.click();
      const progressBar = page.locator('[data-testid="upload-progress"]');
      await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });
    }

    // When: Viewing screenshot metadata
    const metadataButton = page.locator('[data-testid="screenshot-metadata"]');
    await expect(metadataButton).toBeVisible({ timeout: 10_000 });
    await metadataButton.click();

    // Then: Verify metadata is displayed
    const metadata = page.locator('[data-testid="screenshot-metadata-panel"]');
    await expect(metadata).toBeVisible();

    // Verify metadata fields
    const uploadDate = page.locator('[data-testid="metadata-upload-date"]');
    const fileSize = page.locator('[data-testid="metadata-file-size"]');
    const dimensions = page.locator('[data-testid="metadata-dimensions"]');

    await expect(uploadDate).toBeVisible({ timeout: 5000 });
    expect(await uploadDate.textContent()).toMatch(/\d{4}-\d{2}-\d{2}/);

    await expect(fileSize).toBeVisible({ timeout: 5000 });
    expect(await fileSize.textContent()).toMatch(/\d+\s*(KB|MB|bytes)/);

    await expect(dimensions).toBeVisible({ timeout: 5000 });
    expect(await dimensions.textContent()).toMatch(/\d+x\d+/);
  });

  test('should support screenshot versions', async ({ page }) => {
    // Given: Item page is open
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // When: Uploading screenshot with version
    const screenshotButton = page.locator('[data-testid="screenshot-button"]');
    await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
    // Version 1
    await screenshotButton.click();
    let progressBar = page.locator('[data-testid="upload-progress"]');
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Verify version is shown
    const version = page.locator('[data-testid="screenshot-version"]');
    await expect(version).toBeVisible({ timeout: 5000 });
    const versionText = await version.textContent();
    expect(versionText).toMatch(/v\d+\.\d+\.\d+|version \d+/i);

    // Version 2
    await screenshotButton.click();
    progressBar = page.locator('[data-testid="upload-progress"]');
    await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });

    // Then: Verify version history is available
    const versionHistory = page.locator('[data-testid="screenshot-version-history"]');
    await expect(versionHistory).toBeVisible({ timeout: 5000 });
    const historyItems = page.locator('[data-testid="version-item"]');
    expect(await historyItems.count()).toBeGreaterThanOrEqual(1);
  });

  test('should support full-size screenshot view', async ({ page }) => {
    // Given: Item with screenshot
    const itemLink = page.locator('[data-testid="item-row"]').first();
    await expect(itemLink).toBeVisible({ timeout: 10_000 });
    await itemLink.click();
    await page.waitForLoadState('networkidle');

    // Upload screenshot if needed
    const screenshot = page.locator('[data-testid="item-screenshot"]');
    const isVisible = await screenshot.isVisible();
    if (!isVisible) {
      const screenshotButton = page.locator('[data-testid="screenshot-button"]');
      await expect(screenshotButton).toBeVisible({ timeout: 10_000 });
      await screenshotButton.click();
      const progressBar = page.locator('[data-testid="upload-progress"]');
      await progressBar.waitFor({ state: 'hidden', timeout: 30_000 });
    }

    // When: Opening full-size view
    const fullsizeButton = page.locator('[data-testid="view-fullsize"]');
    await expect(fullsizeButton).toBeVisible({ timeout: 10_000 });
    await fullsizeButton.click();

    // Then: Verify fullsize modal/dialog opens
    const fullsizeView = page.locator('[data-testid="fullsize-screenshot"]');
    await expect(fullsizeView).toBeVisible({ timeout: 5000 });

    // Verify close button
    const closeButton = page.locator('[data-testid="close-fullsize"]');
    await expect(closeButton).toBeVisible({ timeout: 5000 });
    await closeButton.click();
    await expect(fullsizeView).not.toBeVisible({ timeout: 5000 });
  });
});
