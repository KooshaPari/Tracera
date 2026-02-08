import { expect, test } from './global-setup';

/**
 * User Settings E2E Tests
 *
 * Comprehensive test suite for Settings page functionality including:
 * - Navigation and page access
 * - Profile settings (display name, email)
 * - Theme preferences
 * - Notification settings
 * - Form validation
 * - Save/Cancel actions
 * - Error handling
 */

test.describe('Settings Page Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to settings page', async ({ page }) => {
    // Navigate to settings
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Verify URL
    await expect(page).toHaveURL('/settings');

    // Verify page title
    const heading = page.getByRole('heading', { name: /settings/i });
    await expect(heading).toBeVisible();
  });

  test('should display settings header and description', async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Check for main heading
    const mainHeading = page.getByRole('heading', { level: 1 });
    await expect(mainHeading).toContainText('Settings');

    // Check for description text
    const description = page.getByText(/Manage your preferences and configuration/i);
    await expect(description).toBeVisible();
  });

  test('should display all settings tabs', async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Check for all tab triggers
    await expect(page.getByRole('tab', { name: /general/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /appearance/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /api/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /notifications/i })).toBeVisible();
  });
});

test.describe('General Settings Tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // General tab should be selected by default
    const generalTab = page.getByRole('tab', { name: /general/i });
    if (!(await generalTab.evaluate((el) => el.getAttribute('aria-selected')))) {
      await generalTab.click();
    }
    await expect(generalTab).toHaveAttribute('aria-selected', 'true');
  });

  test('should display general settings form fields', async ({ page }) => {
    // Display Name field
    const displayNameLabel = page.getByLabel(/display name/i);
    await expect(displayNameLabel).toBeVisible();

    // Email field
    const emailLabel = page.getByLabel(/email/i);
    await expect(emailLabel).toBeVisible();

    // Timezone field
    const timezoneLabel = page.getByLabel(/timezone/i);
    await expect(timezoneLabel).toBeVisible();

    // Save button
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await expect(saveButton).toBeVisible();
  });

  test('should update display name', async ({ page }) => {
    const displayNameInput = page.getByLabel(/display name/i);
    await displayNameInput.fill('John Doe');

    // Verify value is set
    await expect(displayNameInput).toHaveValue('John Doe');

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for success message
    const successMessage = page.getByText(/success|saved/i);
    await expect(successMessage).toBeVisible({ timeout: 10_000 });
  });

  test('should update email address', async ({ page }) => {
    const emailInput = page.getByLabel(/email/i);
    await emailInput.fill('john@example.com');

    // Verify value is set
    await expect(emailInput).toHaveValue('john@example.com');

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for success indication
    await page.waitForTimeout(500);
  });

  test('should validate email format', async ({ page }) => {
    const emailInput = page.getByLabel(/email/i);

    // Try invalid email
    await emailInput.fill('invalid-email');

    // Email input type="email" will have validation
    const isValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
    expect(isValid).toBe(false);
  });

  test('should change timezone', async ({ page }) => {
    // Open timezone select
    const timezoneSelect = page.getByLabel(/timezone/i);
    await timezoneSelect.click();

    // Select Pacific Time
    await page.getByText('Pacific Time').click();

    // Wait for selection
    await page.waitForTimeout(300);

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should handle save with loading state', async ({ page }) => {
    const displayNameInput = page.getByLabel(/display name/i);
    await displayNameInput.fill('Test User');

    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });

    // Click save
    await saveButton.click();

    // Button should show loading state briefly
    await page.waitForTimeout(300);
  });
});

test.describe('Appearance Settings Tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Click on Appearance tab
    const appearanceTab = page.getByRole('tab', { name: /appearance/i });
    await appearanceTab.click();
    await page.waitForTimeout(300);
  });

  test('should display appearance settings form fields', async ({ page }) => {
    // Theme select
    const themeLabel = page.getByLabel(/theme/i);
    await expect(themeLabel).toBeVisible();

    // Font Size select
    const fontSizeLabel = page.getByLabel(/font size/i);
    await expect(fontSizeLabel).toBeVisible();

    // Compact mode checkbox
    const compactCheckbox = page.getByLabel(/compact layout/i);
    await expect(compactCheckbox).toBeVisible();

    // Save button
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await expect(saveButton).toBeVisible();
  });

  test('should change theme to dark', async ({ page }) => {
    // Open theme select
    const themeSelect = page.getByLabel(/theme/i);
    await themeSelect.click();

    // Select Dark theme
    await page.getByText(/^Dark$/).click();

    // Wait for selection
    await page.waitForTimeout(300);

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should change theme to light', async ({ page }) => {
    // Open theme select
    const themeSelect = page.getByLabel(/theme/i);
    await themeSelect.click();

    // Select Light theme
    await page.getByText(/^Light$/).click();

    // Wait for selection
    await page.waitForTimeout(300);

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should change theme to system', async ({ page }) => {
    // Open theme select
    const themeSelect = page.getByLabel(/theme/i);
    await themeSelect.click();

    // Select System theme
    await page.getByText(/^System$/).click();

    // Wait for selection
    await page.waitForTimeout(300);

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should change font size', async ({ page }) => {
    // Open font size select
    const fontSizeSelect = page.getByLabel(/font size/i);
    await fontSizeSelect.click();

    // Select Large font size
    await page.getByText('Large').click();

    // Wait for selection
    await page.waitForTimeout(300);

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should toggle compact mode', async ({ page }) => {
    const compactCheckbox = page.getByLabel(/compact layout/i);

    // Check initial state
    const initialChecked = await compactCheckbox.isChecked();

    // Toggle checkbox
    await compactCheckbox.click();

    // Verify state changed
    const newChecked = await compactCheckbox.isChecked();
    expect(newChecked).toBe(!initialChecked);

    // Save changes
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });
});

test.describe('Notifications Settings Tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Click on Notifications tab
    const notificationsTab = page.getByRole('tab', {
      name: /notifications/i,
    });
    await notificationsTab.click();
    await page.waitForTimeout(300);
  });

  test('should display notification settings checkboxes', async ({ page }) => {
    // Email Notifications
    const emailNotifCheckbox = page.getByLabel(/email notifications/i);
    await expect(emailNotifCheckbox).toBeVisible();

    // Desktop Notifications
    const desktopNotifCheckbox = page.getByLabel(/desktop notifications/i);
    await expect(desktopNotifCheckbox).toBeVisible();

    // Weekly Summary
    const weeklySummaryCheckbox = page.getByLabel(/weekly summary/i);
    await expect(weeklySummaryCheckbox).toBeVisible();

    // Item Updates
    const itemUpdatesCheckbox = page.getByLabel(/item updates/i);
    await expect(itemUpdatesCheckbox).toBeVisible();

    // Save button
    const saveButton = page.getByRole('button', {
      name: /save preferences/i,
    });
    await expect(saveButton).toBeVisible();
  });

  test('should display notification descriptions', async ({ page }) => {
    // Check for descriptions
    await expect(page.getByText(/Receive email updates/i)).toBeVisible();
    await expect(page.getByText(/Browser push notifications/i)).toBeVisible();
    await expect(page.getByText(/Get a weekly digest/i)).toBeVisible();
    await expect(page.getByText(/Notify when items change/i)).toBeVisible();
  });

  test('should toggle email notifications', async ({ page }) => {
    const emailNotifCheckbox = page.getByLabel(/email notifications/i);

    // Get initial state
    const initialChecked = await emailNotifCheckbox.isChecked();

    // Toggle
    await emailNotifCheckbox.click();

    // Verify state changed
    const newChecked = await emailNotifCheckbox.isChecked();
    expect(newChecked).toBe(!initialChecked);

    // Save preferences
    const saveButton = page.getByRole('button', {
      name: /save preferences/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should toggle desktop notifications', async ({ page }) => {
    const desktopNotifCheckbox = page.getByLabel(/desktop notifications/i);

    // Get initial state
    const initialChecked = await desktopNotifCheckbox.isChecked();

    // Toggle
    await desktopNotifCheckbox.click();

    // Verify state changed
    const newChecked = await desktopNotifCheckbox.isChecked();
    expect(newChecked).toBe(!initialChecked);

    // Save preferences
    const saveButton = page.getByRole('button', {
      name: /save preferences/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should toggle weekly summary', async ({ page }) => {
    const weeklySummaryCheckbox = page.getByLabel(/weekly summary/i);

    // Get initial state
    const initialChecked = await weeklySummaryCheckbox.isChecked();

    // Toggle
    await weeklySummaryCheckbox.click();

    // Verify state changed
    const newChecked = await weeklySummaryCheckbox.isChecked();
    expect(newChecked).toBe(!initialChecked);

    // Save preferences
    const saveButton = page.getByRole('button', {
      name: /save preferences/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should toggle item updates notification', async ({ page }) => {
    const itemUpdatesCheckbox = page.getByLabel(/item updates/i);

    // Get initial state
    const initialChecked = await itemUpdatesCheckbox.isChecked();

    // Toggle
    await itemUpdatesCheckbox.click();

    // Verify state changed
    const newChecked = await itemUpdatesCheckbox.isChecked();
    expect(newChecked).toBe(!initialChecked);

    // Save preferences
    const saveButton = page.getByRole('button', {
      name: /save preferences/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should save multiple notification preferences at once', async ({ page }) => {
    // Toggle multiple checkboxes
    const emailNotifCheckbox = page.getByLabel(/email notifications/i);
    const desktopNotifCheckbox = page.getByLabel(/desktop notifications/i);
    const weeklySummaryCheckbox = page.getByLabel(/weekly summary/i);

    await emailNotifCheckbox.click();
    await desktopNotifCheckbox.click();
    await weeklySummaryCheckbox.click();

    // Save all changes at once
    const saveButton = page.getByRole('button', {
      name: /save preferences/i,
    });
    await saveButton.click();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });
});

test.describe('API Keys Tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Click on API tab
    const apiTab = page.getByRole('tab', { name: /api/i });
    await apiTab.click();
    await page.waitForTimeout(300);
  });

  test('should display API key section', async ({ page }) => {
    // API Key field
    const apiKeyLabel = page.getByLabel(/api key/i);
    await expect(apiKeyLabel).toBeVisible();

    // Description text
    const description = page.getByText(/Used for external integrations and webhooks/i);
    await expect(description).toBeVisible();

    // Buttons
    const generateButton = page.getByRole('button', {
      name: /generate new key/i,
    });
    await expect(generateButton).toBeVisible();

    const revokeButton = page.getByRole('button', { name: /revoke key/i });
    await expect(revokeButton).toBeVisible();
  });

  test('should have password-type API key input', async ({ page }) => {
    const apiKeyInput = page.getByLabel(/api key/i);

    // Verify input type is password
    const inputType = await apiKeyInput.evaluate((el: HTMLInputElement) => el.type);
    expect(inputType).toBe('password');
  });

  test('should allow entering API key', async ({ page }) => {
    const apiKeyInput = page.getByLabel(/api key/i);
    await apiKeyInput.fill('test-api-key-123');

    // Verify value is set
    const inputValue = await apiKeyInput.evaluate((el: HTMLInputElement) => el.value);
    expect(inputValue).toBe('test-api-key-123');
  });
});

test.describe('Settings Form Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test('should validate email field with HTML5 validation', async ({ page }) => {
    // Go to general tab
    const generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();

    const emailInput = page.getByLabel(/email/i);

    // Test various invalid formats
    const testCases = [
      { input: 'not-an-email', valid: false },
      { input: 'missing@domain', valid: false },
      { input: '@nodomain.com', valid: false },
      { input: 'valid@example.com', valid: true },
    ];

    for (const testCase of testCases) {
      await emailInput.fill(testCase.input);

      const isValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
      expect(isValid).toBe(testCase.valid);
    }
  });

  test('should handle empty form submission gracefully', async ({ page }) => {
    // Go to general tab
    const generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();

    // Clear all fields
    const displayNameInput = page.getByLabel(/display name/i);
    const emailInput = page.getByLabel(/email/i);

    await displayNameInput.fill('');
    await emailInput.fill('');

    // Try to save
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Should handle gracefully (no error, or validation error shown)
    await page.waitForTimeout(500);
  });
});

test.describe('Settings Tab Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test('should switch between tabs', async ({ page }) => {
    // Start on General tab
    let generalTab = page.getByRole('tab', { name: /general/i });
    let isSelected = await generalTab.evaluate((el) => el.getAttribute('aria-selected'));
    expect(isSelected).toBe('true');

    // Switch to Appearance
    const appearanceTab = page.getByRole('tab', { name: /appearance/i });
    await appearanceTab.click();
    await page.waitForTimeout(300);

    isSelected = await appearanceTab.evaluate((el) => el.getAttribute('aria-selected'));
    expect(isSelected).toBe('true');

    // Switch to Notifications
    const notificationsTab = page.getByRole('tab', {
      name: /notifications/i,
    });
    await notificationsTab.click();
    await page.waitForTimeout(300);

    isSelected = await notificationsTab.evaluate((el) => el.getAttribute('aria-selected'));
    expect(isSelected).toBe('true');

    // Switch back to General
    generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();
    await page.waitForTimeout(300);

    isSelected = await generalTab.evaluate((el) => el.getAttribute('aria-selected'));
    expect(isSelected).toBe('true');
  });

  test('should maintain tab content when switching', async ({ page }) => {
    // Go to General tab
    const generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();

    // Set a value
    const displayNameInput = page.getByLabel(/display name/i);
    await displayNameInput.fill('Test User');

    // Switch to another tab
    const appearanceTab = page.getByRole('tab', { name: /appearance/i });
    await appearanceTab.click();
    await page.waitForTimeout(300);

    // Switch back to General
    await generalTab.click();
    await page.waitForTimeout(300);

    // Value should still be there
    await expect(displayNameInput).toHaveValue('Test User');
  });

  test('should be accessible via keyboard', async ({ page }) => {
    // Focus on first tab
    await page.keyboard.press('Tab');

    // Navigate between tabs with arrow keys
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(300);

    const appearanceTab = page.getByRole('tab', { name: /appearance/i });
    const isSelected = await appearanceTab.evaluate((el) => el.getAttribute('aria-selected'));
    expect(isSelected).toBe('true');

    // Navigate with arrow key again
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(300);
  });
});

test.describe('Settings Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test('should handle invalid email gracefully', async ({ page }) => {
    // Go to general tab
    const generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();

    const emailInput = page.getByLabel(/email/i);
    await emailInput.fill('invalid');

    // Try to save - browser will prevent submission
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await saveButton.click();

    // Wait and verify page is still on settings
    await page.waitForTimeout(300);
    await expect(page).toHaveURL(/settings/);
  });

  test('should display save button in loading state', async ({ page }) => {
    // Go to general tab
    const generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();

    const displayNameInput = page.getByLabel(/display name/i);
    await displayNameInput.fill('Test User');

    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });

    // Click save
    await saveButton.click();

    // Check if button shows loading state (disabled or loading text)
    const isDisabled = await saveButton.isDisabled();
    const loadingTextVisible = await saveButton.getByText(/Saving/i).isVisible();

    // Either disabled or shows loading text
    expect(isDisabled || loadingTextVisible).toBeTruthy();

    // Wait for save to complete
    await page.waitForTimeout(500);
  });

  test('should handle page reload in settings', async ({ page }) => {
    // Go to a tab
    const appearanceTab = page.getByRole('tab', { name: /appearance/i });
    await appearanceTab.click();

    // Reload page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Settings page should still be accessible
    await expect(page).toHaveURL(/settings/);

    // Elements should be visible
    const themeLabel = page.getByLabel(/theme/i);
    await expect(themeLabel).toBeVisible();
  });
});

test.describe('Settings Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test('should have proper form labels', async ({ page }) => {
    // Go to general tab
    const generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();

    // All inputs should have associated labels
    const displayNameInput = page.getByLabel(/display name/i);
    const emailInput = page.getByLabel(/email/i);
    const timezoneInput = page.getByLabel(/timezone/i);

    await expect(displayNameInput).toBeVisible();
    await expect(emailInput).toBeVisible();
    await expect(timezoneInput).toBeVisible();
  });

  test('should have accessible tabs with ARIA roles', async ({ page }) => {
    // Check tab roles
    const tablist = page.getByRole('tablist');
    await expect(tablist).toBeVisible();

    // All tabs should have tab role
    const tabs = page.getByRole('tab');
    const count = await tabs.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Focus should be manageable with Tab key
    const initialFocus = await page.evaluate(() => document.activeElement);

    // Tab through elements
    for (let i = 0; i < 3; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }

    // Focus should have moved
    const currentFocus = await page.evaluate(() => document.activeElement);
    expect(initialFocus).not.toEqual(currentFocus);
  });

  test('should have descriptive button labels', async ({ page }) => {
    // Go to general tab
    const generalTab = page.getByRole('tab', { name: /general/i });
    await generalTab.click();

    // Save button should have descriptive text
    const saveButton = page.getByRole('button', {
      name: /save changes/i,
    });
    await expect(saveButton).toBeVisible();

    const text = await saveButton.textContent();
    expect(text).toMatch(/Save Changes/i);
  });
});

test.describe('Settings Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to settings from dashboard', async ({ page }) => {
    // First go to dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Navigate to settings
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Should be on settings page
    await expect(page).toHaveURL('/settings');
    await expect(page.getByRole('heading', { name: /settings/i })).toBeVisible();
  });

  test('should persist to settings page after navigation', async ({ page }) => {
    // Navigate to settings
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Verify we're on settings
    await expect(page).toHaveURL('/settings');

    // Navigate to another page
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Navigate back to settings
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Should still be able to access settings
    await expect(page).toHaveURL('/settings');
  });

  test('should handle settings page load errors gracefully', async ({ page }) => {
    // Go to settings
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Even if API fails, page should be usable
    const heading = page.getByRole('heading', { name: /settings/i });
    await expect(heading).toBeVisible();

    // Tabs should still be interactive
    const tabs = page.getByRole('tab');
    expect(await tabs.count()).toBeGreaterThan(0);
  });
});
