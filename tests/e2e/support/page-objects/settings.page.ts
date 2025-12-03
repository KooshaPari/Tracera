// tests/e2e/support/page-objects/settings.page.ts
// Page Object: Settings
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, Locator, expect } from '@playwright/test';

export class SettingsPage {
  readonly page: Page;
  readonly profileTab: Locator;
  readonly preferencesTab: Locator;
  readonly notificationsTab: Locator;
  readonly securityTab: Locator;
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly saveButton: Locator;
  readonly themeSelect: Locator;
  readonly languageSelect: Locator;
  readonly notificationToggle: Locator;
  readonly changePasswordButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.profileTab = page.locator('button:has-text("Profile")');
    this.preferencesTab = page.locator('button:has-text("Preferences")');
    this.notificationsTab = page.locator('button:has-text("Notifications")');
    this.securityTab = page.locator('button:has-text("Security")');
    this.nameInput = page.locator('input[name="name"]');
    this.emailInput = page.locator('input[name="email"]');
    this.saveButton = page.locator('button:has-text("Save")');
    this.themeSelect = page.locator('select[name="theme"]');
    this.languageSelect = page.locator('select[name="language"]');
    this.notificationToggle = page.locator('[data-testid="notification-toggle"]');
    this.changePasswordButton = page.locator('button:has-text("Change Password")');
  }

  async navigate(): Promise<void> {
    await this.page.goto('http://localhost:3000/settings');
    await this.page.waitForLoadState('networkidle');
  }

  async updateProfile(name: string, email: string): Promise<void> {
    await this.profileTab.click();
    await this.nameInput.fill(name);
    await this.emailInput.fill(email);
    await this.saveButton.click();
    await expect(this.page.locator('text=Profile updated')).toBeVisible();
  }

  async changeTheme(theme: string): Promise<void> {
    await this.preferencesTab.click();
    await this.themeSelect.selectOption(theme);
    await this.saveButton.click();
    await expect(this.page.locator('text=Theme updated')).toBeVisible();
  }

  async changeLanguage(language: string): Promise<void> {
    await this.preferencesTab.click();
    await this.languageSelect.selectOption(language);
    await this.saveButton.click();
    await expect(this.page.locator('text=Language updated')).toBeVisible();
  }

  async toggleNotifications(enabled: boolean): Promise<void> {
    await this.notificationsTab.click();
    const currentState = await this.notificationToggle.isChecked();
    if (currentState !== enabled) {
      await this.notificationToggle.click();
    }
    await this.saveButton.click();
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await this.securityTab.click();
    await this.changePasswordButton.click();
    await this.page.fill('input[name="old-password"]', oldPassword);
    await this.page.fill('input[name="new-password"]', newPassword);
    await this.page.fill('input[name="confirm-password"]', newPassword);
    await this.page.click('button:has-text("Update Password")');
    await expect(this.page.locator('text=Password updated')).toBeVisible();
  }

  async verifySettingsSaved(): Promise<void> {
    await expect(this.page.locator('text=Settings saved')).toBeVisible();
  }
}
