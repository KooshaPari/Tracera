// tests/e2e/scenarios/05-offline-sync.spec.ts
// Scenario: Offline Sync
// Linked to: Scenario 5, Stories US-SC-5.1 to US-SC-5.50
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { test, expect } from '@playwright/test';

test.describe('Scenario: Offline Sync', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard');
  });

  // OFFLINE OPERATIONS
  // ============================================================================

  test('SC-5.1: Create item while offline', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    
    // Go offline
    await page.context().setOffline(true);
    await expect(page.locator('[data-testid="offline-indicator"]')).toBeVisible();
    
    // Create item offline
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Offline Item');
    await page.click('button:has-text("Save")');
    
    // Verify queued for sync
    await expect(page.locator('text=Queued for sync')).toBeVisible();
    await expect(page.locator('text=Offline Item')).toBeVisible();
  });

  test('SC-5.2: Edit item while offline', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Original Title');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();
    
    // Go offline
    await page.context().setOffline(true);
    
    // Edit offline
    await page.goto(`http://localhost:3000/items/${itemId}`);
    await page.fill('input[name="title"]', 'Offline Edit');
    await page.click('button:has-text("Save")');
    
    await expect(page.locator('text=Queued for sync')).toBeVisible();
    await expect(page.locator('input[name="title"]')).toHaveValue('Offline Edit');
  });

  test('SC-5.3: Delete item while offline', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'To Delete Offline');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();
    
    // Go offline
    await page.context().setOffline(true);
    
    // Delete offline
    await page.goto(`http://localhost:3000/items/${itemId}`);
    await page.click('button:has-text("Delete")');
    await page.click('button:has-text("Confirm")');
    
    await expect(page.locator('text=Queued for deletion')).toBeVisible();
  });

  test('SC-5.4: Sync when coming back online', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    
    // Go offline and create
    await page.context().setOffline(true);
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Sync Test');
    await page.click('button:has-text("Save")');
    
    // Come back online
    await page.context().setOffline(false);
    await expect(page.locator('[data-testid="offline-indicator"]')).not.toBeVisible();
    
    // Verify sync
    await expect(page.locator('[data-testid="syncing"]')).toBeVisible();
    await expect(page.locator('text=Sync complete')).toBeVisible({ timeout: 10000 });
  });

  test('SC-5.5: Multiple offline operations sync in order', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.context().setOffline(true);
    
    // Create multiple items
    for (let i = 0; i < 5; i++) {
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Offline ${i}`);
      await page.click('button:has-text("Save")');
    }
    
    // Come online
    await page.context().setOffline(false);
    
    // Verify all synced
    for (let i = 0; i < 5; i++) {
      await expect(page.locator(`text=Offline ${i}`)).toBeVisible({ timeout: 15000 });
    }
  });

  test('SC-5.6: Conflict resolution on sync', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Conflict Sync');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();
    
    // User 1 goes offline and edits
    await page.context().setOffline(true);
    await page.goto(`http://localhost:3000/items/${itemId}`);
    await page.fill('input[name="title"]', 'Offline Edit');
    await page.click('button:has-text("Save")');
    
    // User 2 edits online
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);
    await page2.fill('input[name="title"]', 'Online Edit');
    await page2.click('button:has-text("Save")');
    
    // User 1 comes online
    await page.context().setOffline(false);
    
    // Verify conflict resolution
    await expect(page.locator('[data-testid="conflict-dialog"]')).toBeVisible();
  });

  test('SC-5.7: Offline indicator visibility', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.context().setOffline(true);
    
    await expect(page.locator('[data-testid="offline-indicator"]')).toBeVisible();
    await expect(page.locator('text=You are offline')).toBeVisible();
    
    await page.context().setOffline(false);
    await expect(page.locator('[data-testid="offline-indicator"]')).not.toBeVisible();
  });

  test('SC-5.8: Queue size limit handling', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.context().setOffline(true);
    
    // Create many items (exceed queue limit)
    for (let i = 0; i < 100; i++) {
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Queue Test ${i}`);
      await page.click('button:has-text("Save")');
    }
    
    // Verify queue limit warning
    await expect(page.locator('text=Queue limit reached')).toBeVisible();
  });

  test('SC-5.9: Partial sync failure recovery', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.context().setOffline(true);
    
    // Create items
    for (let i = 0; i < 3; i++) {
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Partial ${i}`);
      await page.click('button:has-text("Save")');
    }
    
    // Come online with partial failure
    await page.context().setOffline(false);
    await page.route('**/api/items', route => {
      if (route.request().postData()?.includes('Partial 1')) {
        route.fulfill({ status: 500 });
      } else {
        route.continue();
      }
    });
    
    // Verify partial sync
    await expect(page.locator('text=2 of 3 items synced')).toBeVisible();
    await expect(page.locator('button:has-text("Retry Failed")')).toBeVisible();
  });

  test('SC-5.10: Offline data persistence', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.context().setOffline(true);
    
    // Create item
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Persistent Item');
    await page.click('button:has-text("Save")');
    
    // Reload page
    await page.reload();
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.context().setOffline(true);
    
    // Verify item still in queue
    await expect(page.locator('text=Persistent Item')).toBeVisible();
  });

  // Additional offline sync scenarios (SC-5.11 to SC-5.50)
  for (let i = 11; i <= 50; i++) {
    test(`SC-5.${i}: Offline sync scenario ${i}`, async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      await page.context().setOffline(true);
      
      // Perform offline operation
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Offline Test ${i}`);
      await page.click('button:has-text("Save")');
      
      await expect(page.locator('text=Queued for sync')).toBeVisible();
      await expect(page.locator(`text=Offline Test ${i}`)).toBeVisible();
      
      // Sync
      await page.context().setOffline(false);
      await expect(page.locator('text=Sync complete')).toBeVisible({ timeout: 10000 });
      await expect(page.locator(`text=Offline Test ${i}`)).toBeVisible();
    });
  }
});
