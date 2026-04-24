// tests/e2e/support/helpers/data.helper.ts
// Helper: Data Generation
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page } from '@playwright/test';

export class DataHelper {
  constructor(private page: Page) {}

  generateRandomString(length: number = 10): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  generateRandomEmail(): string {
    return `test-${this.generateRandomString(8)}@example.com`;
  }

  generateRandomItemTitle(): string {
    return `Item ${this.generateRandomString(6)}`;
  }

  generateRandomProjectName(): string {
    return `Project ${this.generateRandomString(6)}`;
  }

  generateRandomTag(): string {
    return `tag-${this.generateRandomString(4)}`;
  }

  generateTimestamp(): string {
    return Date.now().toString();
  }

  generateUniqueId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  generateTestData(type: 'item' | 'project' | 'user'): Record<string, string> {
    switch (type) {
      case 'item':
        return {
          title: this.generateRandomItemTitle(),
          description: `Description for ${this.generateRandomString(20)}`,
          tags: this.generateRandomTag(),
        };
      case 'project':
        return {
          name: this.generateRandomProjectName(),
          description: `Project description ${this.generateRandomString(30)}`,
        };
      case 'user':
        return {
          email: this.generateRandomEmail(),
          name: `User ${this.generateRandomString(8)}`,
          password: 'password123',
        };
      default:
        return {};
    }
  }

  async getItemIdFromPage(): Promise<string | null> {
    const itemIdElement = await this.page.locator('[data-testid="item-id"]').textContent();
    return itemIdElement;
  }

  async getProjectIdFromPage(): Promise<string | null> {
    const projectIdElement = await this.page.locator('[data-testid="project-id"]').textContent();
    return projectIdElement;
  }

  generateTestUsers(count: number): Array<{ email: string; password: string; name: string }> {
    return Array.from({ length: count }, () => ({
      email: this.generateRandomEmail(),
      password: 'password123',
      name: `User ${this.generateRandomString(6)}`,
    }));
  }
}
