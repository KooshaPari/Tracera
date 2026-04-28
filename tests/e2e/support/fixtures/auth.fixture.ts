// tests/e2e/support/fixtures/auth.fixture.ts
// Fixture: Authentication
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, expect } from '@playwright/test';
import { testConfig } from '../config/test.config';

export class AuthFixture {
  constructor(private page: Page) {}

  async login(email: string = testConfig.users.projectManager.email, password: string = testConfig.users.projectManager.password): Promise<void> {
    await this.page.goto(testConfig.baseUrl);
    await this.page.fill('input[name="email"]', email);
    await this.page.fill('input[name="password"]', password);
    await this.page.click('button:has-text("Login")');
    await this.page.waitForURL('**/dashboard');
    await expect(this.page).toHaveURL(/.*dashboard/);
  }

  async loginAsProjectManager(): Promise<void> {
    await this.login(testConfig.users.projectManager.email, testConfig.users.projectManager.password);
  }

  async loginAsDeveloper(): Promise<void> {
    await this.login(testConfig.users.developer.email, testConfig.users.developer.password);
  }

  async loginAsDesigner(): Promise<void> {
    await this.login(testConfig.users.designer.email, testConfig.users.designer.password);
  }

  async loginAsQAEngineer(): Promise<void> {
    await this.login(testConfig.users.qaEngineer.email, testConfig.users.qaEngineer.password);
  }

  async logout(): Promise<void> {
    await this.page.click('button:has-text("Logout")');
    await this.page.waitForURL('**/login');
    await expect(this.page).toHaveURL(/.*login/);
  }

  async verifyLoggedIn(): Promise<void> {
    await expect(this.page.locator('[data-testid="user-menu"]')).toBeVisible();
  }

  async verifyLoggedOut(): Promise<void> {
    await expect(this.page.locator('input[name="email"]')).toBeVisible();
  }

  async getAuthToken(): Promise<string | null> {
    const token = await this.page.evaluate(() => {
      return localStorage.getItem('authToken');
    });
    return token;
  }

  async setAuthToken(token: string): Promise<void> {
    await this.page.evaluate((t) => {
      localStorage.setItem('authToken', t);
    }, token);
  }
}
