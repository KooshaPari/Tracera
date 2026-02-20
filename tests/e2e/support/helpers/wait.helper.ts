// tests/e2e/support/helpers/wait.helper.ts
// Helper: Wait Utilities
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, Locator } from '@playwright/test';

export class WaitHelper {
  constructor(private page: Page) {}

  async waitForElement(selector: string, timeout: number = 5000): Promise<void> {
    await this.page.waitForSelector(selector, { timeout });
  }

  async waitForText(text: string, timeout: number = 5000): Promise<void> {
    await this.page.waitForSelector(`text=${text}`, { timeout });
  }

  async waitForUrl(pattern: string | RegExp, timeout: number = 5000): Promise<void> {
    await this.page.waitForURL(pattern, { timeout });
  }

  async waitForNetworkIdle(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async waitForDomContentLoaded(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
  }

  async waitForTimeout(ms: number): Promise<void> {
    await this.page.waitForTimeout(ms);
  }

  async waitForApiResponse(urlPattern: string | RegExp, timeout: number = 10000): Promise<void> {
    await this.page.waitForResponse(
      (response) => {
        const url = response.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        }
        return urlPattern.test(url);
      },
      { timeout }
    );
  }

  async waitForElementToBeVisible(selector: string, timeout: number = 5000): Promise<void> {
    await this.page.waitForSelector(selector, { state: 'visible', timeout });
  }

  async waitForElementToBeHidden(selector: string, timeout: number = 5000): Promise<void> {
    await this.page.waitForSelector(selector, { state: 'hidden', timeout });
  }

  async waitForNavigation(): Promise<void> {
    await this.page.waitForNavigation();
  }

  async waitForDownload(): Promise<void> {
    await this.page.waitForEvent('download');
  }

  async waitForDialog(): Promise<void> {
    await this.page.waitForEvent('dialog');
  }

  async waitForApiRequest(urlPattern: string | RegExp, timeout: number = 10000): Promise<void> {
    await this.page.waitForRequest(
      (request) => {
        const url = request.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        }
        return urlPattern.test(url);
      },
      { timeout }
    );
  }
}
