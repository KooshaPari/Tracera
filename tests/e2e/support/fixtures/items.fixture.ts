// tests/e2e/support/fixtures/items.fixture.ts
// Fixture: Items Setup
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, expect } from '@playwright/test';
import { DataHelper } from '../helpers/data.helper';

export class ItemsFixture {
  private dataHelper: DataHelper;
  private itemIds: string[] = [];

  constructor(private page: Page) {
    this.dataHelper = new DataHelper(page);
  }

  async createItem(title?: string, description?: string): Promise<string> {
    const itemTitle = title || this.dataHelper.generateRandomItemTitle();
    await this.page.goto('http://localhost:3000/items');
    await this.page.click('button:has-text("Create Item")');
    await this.page.fill('input[name="title"]', itemTitle);
    if (description) {
      await this.page.fill('textarea[name="description"]', description);
    }
    await this.page.click('button:has-text("Save")');
    await expect(this.page.locator(`text=${itemTitle}`)).toBeVisible();
    
    const itemId = await this.page.locator('[data-testid="item-id"]').textContent();
    if (itemId) {
      this.itemIds.push(itemId);
    }
    return itemId || '';
  }

  async deleteItem(itemId: string): Promise<void> {
    await this.page.goto(`http://localhost:3000/items/${itemId}`);
    await this.page.click('button:has-text("Delete")');
    await this.page.click('button:has-text("Confirm")');
    await expect(this.page.locator('text=Item deleted')).toBeVisible();
  }

  async cleanup(): Promise<void> {
    for (const itemId of this.itemIds) {
      try {
        await this.deleteItem(itemId);
      } catch (error) {
        // Ignore errors during cleanup
      }
    }
    this.itemIds = [];
  }

  async getItemId(): Promise<string | null> {
    return await this.page.locator('[data-testid="item-id"]').textContent();
  }

  async verifyItemExists(title: string): Promise<void> {
    await expect(this.page.locator(`text=${title}`)).toBeVisible();
  }

  async createMultipleItems(count: number): Promise<string[]> {
    const ids: string[] = [];
    for (let i = 0; i < count; i++) {
      const id = await this.createItem();
      ids.push(id);
    }
    return ids;
  }
}
