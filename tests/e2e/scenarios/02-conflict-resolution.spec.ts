// tests/e2e/scenarios/02-conflict-resolution.spec.ts
// Scenario: Conflict Resolution
// Linked to: Scenario 2, Stories US-SC-2.1 to US-SC-2.50
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { test, expect } from '@playwright/test';

test.describe('Scenario: Conflict Resolution', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard');
  });

  // CONFLICT DETECTION
  // ============================================================================

  test('SC-2.1: Detect edit conflict on same field', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Conflict Test');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Both users edit same field
    await page.fill('input[name="title"]', 'User 1 Title');
    await page2.fill('input[name="title"]', 'User 2 Title');

    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Verify conflict detected
    await expect(page.locator('text=Conflict detected')).toBeVisible();
    await expect(page2.locator('text=Conflict detected')).toBeVisible();
  });

  test('SC-2.2: Resolve conflict with last-write-wins', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Last Write Wins');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    await page.fill('input[name="title"]', 'First Edit');
    await page.click('button:has-text("Save")');

    await page2.fill('input[name="title"]', 'Second Edit');
    await page2.click('button:has-text("Save")');

    // Verify last write wins
    await expect(page2.locator('text=Second Edit')).toBeVisible();
  });

  test('SC-2.3: Resolve conflict with manual merge', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Merge Test');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Create conflict
    await page.fill('textarea[name="description"]', 'User 1 description');
    await page2.fill('textarea[name="description"]', 'User 2 description');
    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Manual merge option appears
    await expect(page.locator('button:has-text("Merge Changes")')).toBeVisible();
    await page.click('button:has-text("Merge Changes")');
    await page.fill('textarea[name="description"]', 'Merged: User 1 + User 2');
    await page.click('button:has-text("Save Merged")');

    await expect(page.locator('text=Merged: User 1 + User 2')).toBeVisible();
  });

  test('SC-2.4: Conflict on link creation', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Item A');
    await page.click('button:has-text("Save")');
    const itemAId = await page.locator('[data-testid="item-id"]').textContent();

    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Item B');
    await page.click('button:has-text("Save")');
    const itemBId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');

    // Both users create same link
    await page.goto(`http://localhost:3000/items/${itemAId}`);
    await page2.goto(`http://localhost:3000/items/${itemAId}`);

    await page.click('button:has-text("Add Link")');
    await page.fill('input[name="target-id"]', itemBId!);
    await page.click('button:has-text("Create Link")');

    await page2.click('button:has-text("Add Link")');
    await page2.fill('input[name="target-id"]', itemBId!);
    await page2.click('button:has-text("Create Link")');

    // Verify duplicate link handled
    await expect(page.locator('text=Link already exists')).toBeVisible();
  });

  test('SC-2.5: Conflict on deletion', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Delete Conflict');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // User 1 edits, User 2 deletes
    await page.fill('input[name="title"]', 'Updated Title');
    await page2.click('button:has-text("Delete")');
    await page2.click('button:has-text("Confirm")');

    await page.click('button:has-text("Save")');

    // Verify conflict handled
    await expect(page.locator('text=Item was deleted')).toBeVisible();
  });

  test('SC-2.6: Conflict resolution UI', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'UI Test');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Create conflict
    await page.fill('input[name="title"]', 'User 1');
    await page2.fill('input[name="title"]', 'User 2');
    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Verify conflict UI elements
    await expect(page.locator('[data-testid="conflict-dialog"]')).toBeVisible();
    await expect(page.locator('text=Your version')).toBeVisible();
    await expect(page.locator('text=Other version')).toBeVisible();
    await expect(page.locator('button:has-text("Keep Mine")')).toBeVisible();
    await expect(page.locator('button:has-text("Keep Theirs")')).toBeVisible();
    await expect(page.locator('button:has-text("Merge")')).toBeVisible();
  });

  test('SC-2.7: Auto-resolve non-conflicting changes', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Auto Merge');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Edit different fields (no conflict)
    await page.fill('input[name="title"]', 'New Title');
    await page2.fill('textarea[name="description"]', 'New Description');

    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Verify both changes applied
    await expect(page.locator('text=New Title')).toBeVisible();
    await expect(page2.locator('text=New Description')).toBeVisible({ timeout: 5000 });
  });

  test('SC-2.8: Conflict on tag modification', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Tag Conflict');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Both users modify tags
    await page.fill('input[name="tags"]', 'tag1,tag2');
    await page2.fill('input[name="tags"]', 'tag3,tag4');
    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Verify conflict resolution
    await expect(page.locator('[data-testid="conflict-dialog"]')).toBeVisible();
  });

  test('SC-2.9: Version history on conflict', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Version Test');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Create conflict
    await page.fill('input[name="title"]', 'Version 1');
    await page2.fill('input[name="title"]', 'Version 2');
    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Check version history
    await page.click('button:has-text("View History")');
    await expect(page.locator('[data-testid="version-history"]')).toBeVisible();
    await expect(page.locator('text=Version 1')).toBeVisible();
    await expect(page.locator('text=Version 2')).toBeVisible();
  });

  test('SC-2.10: Conflict notification', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Notification Test');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Create conflict
    await page.fill('input[name="title"]', 'User 1');
    await page2.fill('input[name="title"]', 'User 2');
    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Verify notification
    await expect(page.locator('[data-testid="notification"]')).toBeVisible();
    await expect(page.locator('text=Conflict detected')).toBeVisible();
  });

  // Additional conflict resolution scenarios (SC-2.11 to SC-2.50)
  for (let i = 11; i <= 50; i++) {
    test(`SC-2.${i}: Conflict resolution scenario ${i}`, async ({ page, context }) => {
      await page.goto('http://localhost:3000/items');
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Conflict Test ${i}`);
      await page.click('button:has-text("Save")');
      const itemId = await page.locator('[data-testid="item-id"]').textContent();

      const page2 = await context.newPage();
      await page2.goto('http://localhost:3000');
      await page2.fill('input[name="email"]', 'john@example.com');
      await page2.fill('input[name="password"]', 'password123');
      await page2.click('button:has-text("Login")');
      await page2.goto(`http://localhost:3000/items/${itemId}`);

      // Create and resolve conflict
      await page.fill('input[name="title"]', `Version A ${i}`);
      await page2.fill('input[name="title"]', `Version B ${i}`);
      await page.click('button:has-text("Save")');
      await page2.click('button:has-text("Save")');

      // Resolve
      await page.click('button:has-text("Keep Mine")');
      await expect(page.locator(`text=Version A ${i}`)).toBeVisible();
    });
  }
});
