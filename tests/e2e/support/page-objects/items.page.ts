// tests/e2e/support/page-objects/items.page.ts
// Page Object: Items
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, Locator, expect } from '@playwright/test';

export class ItemsPage {
  readonly page: Page;
  readonly itemList: Locator;
  readonly createItemButton: Locator;
  readonly titleInput: Locator;
  readonly descriptionTextarea: Locator;
  readonly saveButton: Locator;
  readonly deleteButton: Locator;
  readonly filterInput: Locator;
  readonly searchInput: Locator;
  readonly tagsInput: Locator;
  readonly addTagButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.itemList = page.locator('[data-testid="item-list"]');
    this.createItemButton = page.locator('button:has-text("Create Item")');
    this.titleInput = page.locator('input[name="title"]');
    this.descriptionTextarea = page.locator('textarea[name="description"]');
    this.saveButton = page.locator('button:has-text("Save")');
    this.deleteButton = page.locator('button:has-text("Delete")');
    this.filterInput = page.locator('input[name="filter"]');
    this.searchInput = page.locator('input[name="search"]');
    this.tagsInput = page.locator('input[name="tags"]');
    this.addTagButton = page.locator('button:has-text("Add Tag")');
  }

  async navigate(): Promise<void> {
    await this.page.goto('http://localhost:3000/items');
    await this.page.waitForLoadState('networkidle');
  }

  async createItem(title: string, description?: string): Promise<string> {
    await this.createItemButton.click();
    await this.titleInput.fill(title);
    if (description) {
      await this.descriptionTextarea.fill(description);
    }
    await this.saveButton.click();
    await expect(this.page.locator(`text=${title}`)).toBeVisible();
    const itemId = await this.page.locator('[data-testid="item-id"]').textContent();
    return itemId || '';
  }

  async editItem(itemId: string, title: string): Promise<void> {
    await this.page.goto(`http://localhost:3000/items/${itemId}`);
    await this.titleInput.fill(title);
    await this.saveButton.click();
    await expect(this.page.locator(`text=${title}`)).toBeVisible();
  }

  async deleteItem(itemId: string): Promise<void> {
    await this.page.goto(`http://localhost:3000/items/${itemId}`);
    await this.deleteButton.click();
    await this.page.click('button:has-text("Confirm")');
    await expect(this.page.locator('text=Item deleted')).toBeVisible();
  }

  async filterItems(filter: string): Promise<void> {
    await this.filterInput.fill(filter);
    await this.page.press('input[name="filter"]', 'Enter');
    await this.page.waitForSelector('[data-testid="filtered-results"]');
  }

  async searchItems(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.press('input[name="search"]', 'Enter');
    await this.page.waitForSelector('[data-testid="search-results"]');
  }

  async addTag(itemId: string, tag: string): Promise<void> {
    await this.page.goto(`http://localhost:3000/items/${itemId}`);
    await this.tagsInput.fill(tag);
    await this.addTagButton.click();
    await expect(this.page.locator(`text=${tag}`)).toBeVisible();
  }

  async verifyItemExists(title: string): Promise<void> {
    await expect(this.page.locator(`text=${title}`)).toBeVisible();
  }

  async clickItem(title: string): Promise<void> {
    await this.page.click(`text=${title}`);
    await this.page.waitForURL('**/items/**');
  }
}
