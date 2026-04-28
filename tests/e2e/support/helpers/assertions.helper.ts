// tests/e2e/support/helpers/assertions.helper.ts
// Helper: Assertions
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, Locator, expect } from '@playwright/test';

export class AssertionsHelper {
  constructor(private page: Page) {}

  async assertElementVisible(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeVisible();
  }

  async assertElementNotVisible(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).not.toBeVisible();
  }

  async assertTextVisible(text: string): Promise<void> {
    await expect(this.page.locator(`text=${text}`)).toBeVisible();
  }

  async assertTextNotVisible(text: string): Promise<void> {
    await expect(this.page.locator(`text=${text}`)).not.toBeVisible();
  }

  async assertElementContainsText(selector: string, text: string): Promise<void> {
    await expect(this.page.locator(selector)).toContainText(text);
  }

  async assertInputValue(selector: string, value: string): Promise<void> {
    await expect(this.page.locator(selector)).toHaveValue(value);
  }

  async assertUrlContains(pattern: string): Promise<void> {
    await expect(this.page).toHaveURL(new RegExp(pattern));
  }

  async assertElementCount(selector: string, count: number): Promise<void> {
    const elements = await this.page.locator(selector).count();
    expect(elements).toBe(count);
  }

  async assertElementCountGreaterThan(selector: string, count: number): Promise<void> {
    const elements = await this.page.locator(selector).count();
    expect(elements).toBeGreaterThan(count);
  }

  async assertElementEnabled(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeEnabled();
  }

  async assertElementDisabled(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeDisabled();
  }

  async assertCheckboxChecked(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeChecked();
  }

  async assertCheckboxNotChecked(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).not.toBeChecked();
  }

  async assertSuccessMessage(message: string): Promise<void> {
    await expect(this.page.locator(`text=${message}`)).toBeVisible();
  }

  async assertErrorMessage(message: string): Promise<void> {
    await expect(this.page.locator(`text=${message}`)).toBeVisible();
  }

  async assertLoadingComplete(): Promise<void> {
    await expect(this.page.locator('[data-testid="loading"]')).not.toBeVisible();
  }
}
