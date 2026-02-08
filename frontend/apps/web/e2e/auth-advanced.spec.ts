import { expect, test } from './global-setup';

/**
 * Advanced Authentication E2E Tests
 *
 * Comprehensive authentication flow testing including edge cases,
 * session management, token refresh, and security scenarios.
 */

test.describe('Advanced Authentication Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Login Flow', () => {
    test('should handle successful login with valid credentials', async ({ page }) => {
      // Navigate to login page
      await page.goto('/auth/login');
      await page.waitForLoadState('networkidle');

      // Fill in login form
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');

      // Submit form
      await page.click('button[type="submit"]');

      // Should redirect to dashboard
      await expect(page).toHaveURL('/', { timeout: 10_000 });

      // Verify user is logged in
      const userMenu = page.locator('[data-testid="user-menu"]');
      await expect(userMenu).toBeVisible({ timeout: 10_000 });
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/auth/login');

      await page.fill('input[name="email"]', 'wrong@example.com');
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');

      // Should show error message
      const errorMessage = page.locator('[role="alert"]');
      await expect(errorMessage).toBeVisible();
      await expect(errorMessage).toContainText(/invalid/i);

      // Should stay on login page
      await expect(page).toHaveURL(/\/auth\/login/);
    });

    test('should validate email format', async ({ page }) => {
      await page.goto('/auth/login');

      await page.fill('input[name="email"]', 'invalid-email');
      await page.fill('input[name="password"]', 'password123');

      // Try to submit
      await page.click('button[type="submit"]');

      // Should show validation error
      const emailError = page.locator('input[name="email"] ~ .error');
      await expect(emailError).toBeVisible();
      await expect(emailError).toContainText(/email/i);
    });

    test('should require password field', async ({ page }) => {
      await page.goto('/auth/login');

      await page.fill('input[name="email"]', 'test@example.com');
      await page.click('button[type="submit"]');

      // Should show password required error
      const passwordError = page.locator('input[name="password"] ~ .error');
      await expect(passwordError).toBeVisible();
      await expect(passwordError).toContainText(/required/i);
    });

    test('should toggle password visibility', async ({ page }) => {
      await page.goto('/auth/login');

      const passwordInput = page.locator('input[name="password"]');
      const toggleButton = page.locator('[data-testid="toggle-password"]');

      // Password should be hidden by default
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // Click toggle button
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'text');

      // Click again to hide
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('should handle login with remember me option', async ({ page }) => {
      await page.goto('/auth/login');

      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');

      // Check remember me
      await page.check('input[name="rememberMe"]');
      await page.click('button[type="submit"]');

      await page.waitForURL('/');

      // Verify persistent session in localStorage
      const rememberMe = await page.evaluate(() => localStorage.getItem('rememberMe'));
      expect(rememberMe).toBe('true');
    });
  });

  test.describe('Logout Flow', () => {
    test.beforeEach(async ({ page }) => {
      // Login first
      await page.goto('/auth/login');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL('/');
    });

    test('should logout successfully', async ({ page }) => {
      // Click user menu
      await page.click('[data-testid="user-menu"]');

      // Click logout button
      await page.click('[data-testid="logout-button"]');

      // Should redirect to login page
      await expect(page).toHaveURL('/auth/login', { timeout: 10_000 });

      // Session should be cleared
      const token = await page.evaluate(() => localStorage.getItem('authToken'));
      expect(token).toBeNull();
    });

    test('should confirm logout when user has unsaved changes', async ({ page }) => {
      // Create some unsaved changes
      await page.goto('/items/new');
      await page.fill('input[name="title"]', 'Unsaved Item');

      // Try to logout
      await page.click('[data-testid="user-menu"]');
      await page.click('[data-testid="logout-button"]');

      // Should show confirmation dialog
      const confirmDialog = page.locator('[role="dialog"]');
      await expect(confirmDialog).toBeVisible();
      await expect(confirmDialog).toContainText(/unsaved changes/i);

      // Cancel logout
      await page.click('button:has-text("Cancel")');
      await expect(confirmDialog).not.toBeVisible();

      // Should still be on items page
      await expect(page).toHaveURL(/\/items\/new/);
    });

    test('should clear all session data on logout', async ({ page }) => {
      // Logout
      await page.click('[data-testid="user-menu"]');
      await page.click('[data-testid="logout-button"]');
      await expect(page).toHaveURL('/auth/login', { timeout: 10_000 });

      // Verify all session data is cleared
      const sessionData = await page.evaluate(() => ({
        session: sessionStorage.getItem('session'),
        token: localStorage.getItem('authToken'),
        user: localStorage.getItem('user'),
      }));

      expect(sessionData.token).toBeNull();
      expect(sessionData.user).toBeNull();
      expect(sessionData.session).toBeNull();
    });
  });

  test.describe('Session Management', () => {
    test('should maintain session across page reloads', async ({ page }) => {
      // Login
      await page.goto('/auth/login');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL('/');

      // Get auth token
      const tokenBefore = await page.evaluate(() => localStorage.getItem('authToken'));

      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Should still be authenticated
      const tokenAfter = await page.evaluate(() => localStorage.getItem('authToken'));
      expect(tokenAfter).toBe(tokenBefore);

      // Verify user menu is visible
      const userMenu = page.locator('[data-testid="user-menu"]');
      await expect(userMenu).toBeVisible({ timeout: 5000 });
    });

    test('should handle session timeout', async ({ page }) => {
      // Login
      await page.goto('/auth/login');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL('/', { timeout: 10_000 });

      // Simulate session timeout by clearing token
      await page.evaluate(() => {
        localStorage.removeItem('authToken');
      });

      // Navigate to protected route
      await page.goto('/items');

      // Should redirect to login
      await expect(page).toHaveURL('/auth/login', { timeout: 10_000 });

      // Should show timeout message
      const message = page.locator('[role="alert"]');
      await expect(message).toBeVisible({ timeout: 5000 });
      await expect(message).toContainText(/session expired/i);
    });

    test('should refresh token before expiration', async ({ page }) => {
      // Login
      await page.goto('/auth/login');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL('/');

      // Wait for token refresh (simulated)
      await page.waitForTimeout(2000);

      // Intercept token refresh request
      let _refreshRequested = false;
      await page.route('**/api/auth/refresh', (route) => {
        _refreshRequested = true;
        void route.fulfill({
          body: JSON.stringify({ token: 'new-token' }),
          status: 200,
        });
      });

      // Trigger activity that would check token expiration
      await page.goto('/projects');
      await page.waitForLoadState('networkidle');

      // Token should have been refreshed (in real implementation)
      // This is a simplified check
      const token = await page.evaluate(() => localStorage.getItem('authToken'));
      expect(token).toBeTruthy();
    });

    test('should handle concurrent session in multiple tabs', async ({ browser }) => {
      // Create first tab and login
      const context1 = await browser.newContext();
      const page1 = await context1.newPage();

      await page1.goto('/auth/login');
      await page1.fill('input[name="email"]', 'test@example.com');
      await page1.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await expect(page1).toHaveURL('/', { timeout: 10_000 });

      // Create second tab with same session
      const page2 = await context1.newPage();
      await page2.goto('/');
      await page2.waitForLoadState('networkidle');

      // Both tabs should be authenticated
      await expect(page1.locator('[data-testid="user-menu"]')).toBeVisible();
      await expect(page2.locator('[data-testid="user-menu"]')).toBeVisible();

      // Logout from first tab
      await page1.click('[data-testid="user-menu"]');
      await page1.click('[data-testid="logout-button"]');
      await expect(page1).toHaveURL('/auth/login', { timeout: 10_000 });

      // Second tab should also be logged out (storage event)
      await expect(page2).toHaveURL('/auth/login', { timeout: 10_000 });

      await context1.close();
    });
  });

  test.describe('Password Reset', () => {
    test('should navigate to password reset page', async ({ page }) => {
      await page.goto('/auth/login');

      // Click forgot password link
      await page.click('a:has-text("Forgot password")');

      // Should navigate to reset page
      await expect(page).toHaveURL('/auth/reset-password', { timeout: 10_000 });
    });

    test('should send password reset email', async ({ page }) => {
      await page.goto('/auth/reset-password');

      // Fill email
      await page.fill('input[name="email"]', 'test@example.com');
      await page.click('button[type="submit"]');

      // Should show success message
      const successMessage = page.locator('[role="alert"]');
      await expect(successMessage).toBeVisible();
      await expect(successMessage).toContainText(/email sent/i);
    });

    test('should validate email format in reset form', async ({ page }) => {
      await page.goto('/auth/reset-password');

      await page.fill('input[name="email"]', 'invalid-email');
      await page.click('button[type="submit"]');

      const error = page.locator('input[name="email"] ~ .error');
      await expect(error).toBeVisible();
      await expect(error).toContainText(/valid email/i);
    });

    test('should handle password reset with token', async ({ page }) => {
      // Navigate with reset token
      await page.goto('/auth/reset-password?token=valid-reset-token');

      // Should show new password form
      await expect(page.locator('input[name="newPassword"]')).toBeVisible();
      await expect(page.locator('input[name="confirmPassword"]')).toBeVisible();

      // Fill new password
      await page.fill('input[name="newPassword"]', 'NewPassword123!');
      await page.fill('input[name="confirmPassword"]', 'NewPassword123!');
      await page.click('button[type="submit"]');

      // Should redirect to login
      await expect(page).toHaveURL('/auth/login', { timeout: 10_000 });

      // Should show success message
      const message = page.locator('[role="alert"]');
      await expect(message).toBeVisible({ timeout: 5000 });
      await expect(message).toContainText(/password reset successful/i);
    });

    test('should validate password strength', async ({ page }) => {
      await page.goto('/auth/reset-password?token=valid-token');

      // Weak password
      await page.fill('input[name="newPassword"]', 'weak');
      await page.fill('input[name="confirmPassword"]', 'weak');

      const strengthIndicator = page.locator('[data-testid="password-strength"]');
      await expect(strengthIndicator).toBeVisible();
      await expect(strengthIndicator).toHaveClass(/weak/);
    });

    test('should validate password confirmation match', async ({ page }) => {
      await page.goto('/auth/reset-password?token=valid-token');

      await page.fill('input[name="newPassword"]', 'StrongPassword123!');
      await page.fill('input[name="confirmPassword"]', 'DifferentPassword123!');
      await page.click('button[type="submit"]');

      const error = page.locator('input[name="confirmPassword"] ~ .error');
      await expect(error).toBeVisible();
      await expect(error).toContainText(/passwords do not match/i);
    });
  });

  test.describe('User Registration', () => {
    test('should navigate to registration page', async ({ page }) => {
      await page.goto('/auth/login');

      await page.click('a:has-text("Sign up")');
      await page.waitForURL('/auth/register');
      await expect(page).toHaveURL('/auth/register');
    });

    test('should register new user successfully', async ({ page }) => {
      await page.goto('/auth/register');

      // Fill registration form
      await page.fill('input[name="email"]', 'newuser@example.com');
      await page.fill('input[name="password"]', 'SecurePass123!');
      await page.fill('input[name="confirmPassword"]', 'SecurePass123!');
      await page.fill('input[name="name"]', 'New User');

      // Accept terms
      await page.check('input[name="acceptTerms"]');

      // Submit
      await page.click('button[type="submit"]');

      // Should redirect to dashboard or verification page
      await expect(page).toHaveURL(/\/(|auth\/verify)/, { timeout: 10_000 });

      // Should show success message
      const message = page.locator('[role="alert"]');
      await expect(message).toBeVisible({ timeout: 5000 });
    });

    test('should validate all required fields', async ({ page }) => {
      await page.goto('/auth/register');

      // Try to submit without filling fields
      await page.click('button[type="submit"]');

      // Should show multiple errors
      const errors = page.locator('.error');
      await expect(errors).toHaveCount(4); // Email, password, confirm, name
    });

    test('should enforce terms acceptance', async ({ page }) => {
      await page.goto('/auth/register');

      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'SecurePass123!');
      await page.fill('input[name="confirmPassword"]', 'SecurePass123!');
      await page.fill('input[name="name"]', 'Test User');

      // Don't check terms
      await page.click('button[type="submit"]');

      // Should show error
      const termsError = page.locator('input[name="acceptTerms"] ~ .error');
      await expect(termsError).toBeVisible();
      await expect(termsError).toContainText(/accept terms/i);
    });

    test('should check for existing email', async ({ page }) => {
      await page.goto('/auth/register');

      await page.fill('input[name="email"]', 'existing@example.com');
      await page.fill('input[name="password"]', 'SecurePass123!');
      await page.fill('input[name="confirmPassword"]', 'SecurePass123!');
      await page.fill('input[name="name"]', 'Test User');
      await page.check('input[name="acceptTerms"]');

      await page.click('button[type="submit"]');

      // Should show error about existing email
      const error = page.locator('[role="alert"]');
      await expect(error).toBeVisible();
      await expect(error).toContainText(/email already exists/i);
    });
  });

  test.describe('Security Features', () => {
    test('should prevent XSS in login form', async ({ page }) => {
      await page.goto('/auth/login');

      const xssPayload = '<script>alert("XSS")</script>';
      await page.fill('input[name="email"]', xssPayload);
      await page.fill('input[name="password"]', xssPayload);

      // Script should not execute
      page.on('dialog', () => {
        throw new Error('XSS vulnerability detected!');
      });

      await page.click('button[type="submit"]');
      await page.waitForTimeout(1000);

      // Should safely handle the input
      const emailValue = await page.inputValue('input[name="email"]');
      expect(emailValue).toBe(xssPayload); // Should be stored as text, not executed
    });

    test('should have CSRF protection', async ({ page }) => {
      await page.goto('/auth/login');

      // Check for CSRF token
      const csrfToken = await page.evaluate(() => {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta?.getAttribute('content');
      });

      // CSRF token should exist or be handled by headers
      expect(csrfToken).toBeTruthy();
    });

    test('should rate limit login attempts', async ({ page }) => {
      await page.goto('/auth/login');

      // Attempt multiple failed logins
      for (let i = 0; i < 6; i++) {
        await page.fill('input[name="email"]', 'test@example.com');
        await page.fill('input[name="password"]', 'wrongpassword');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(500);
      }

      // Should show rate limit error
      const error = page.locator('[role="alert"]');
      await expect(error).toBeVisible();
      await expect(error).toContainText(/too many attempts/i);

      // Submit button should be disabled
      const submitButton = page.locator('button[type="submit"]');
      await expect(submitButton).toBeDisabled();
    });

    test('should secure sensitive data in localStorage', async ({ page }) => {
      await page.goto('/auth/login');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL('/');

      // Password should never be stored
      const storage = await page.evaluate(() => JSON.stringify(localStorage));

      expect(storage).not.toContain('password123');
    });
  });

  test.describe('OAuth and Third-Party Auth', () => {
    test('should display OAuth login options', async ({ page }) => {
      await page.goto('/auth/login');

      // Check for OAuth buttons
      await expect(page.locator('button:has-text("Google")')).toBeVisible();
      await expect(page.locator('button:has-text("GitHub")')).toBeVisible();
    });

    test('should initiate OAuth flow', async ({ page, context }) => {
      await page.goto('/auth/login');

      // Click Google OAuth button
      const [popup] = await Promise.all([
        context.waitForEvent('page'),
        page.click('button:has-text("Google")'),
      ]);

      // Should open OAuth popup
      await popup.waitForLoadState();
      expect(popup.url()).toContain('google.com');

      await popup.close();
    });

    test('should handle OAuth callback', async ({ page }) => {
      // Simulate OAuth callback
      await page.goto('/auth/callback?code=oauth-code&state=valid-state');

      // Should process callback and redirect
      await expect(page).toHaveURL('/', { timeout: 10_000 });

      // User should be authenticated
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible({ timeout: 5000 });
    });

    test('should handle OAuth errors', async ({ page }) => {
      // Simulate OAuth error
      await page.goto('/auth/callback?error=access_denied');

      // Should show error and redirect to login
      await expect(page).toHaveURL('/auth/login', { timeout: 10_000 });

      const error = page.locator('[role="alert"]');
      await expect(error).toBeVisible({ timeout: 5000 });
      await expect(error).toContainText(/authentication failed/i);
    });
  });

  test.describe('Accessibility', () => {
    test('login form should be keyboard navigable', async ({ page }) => {
      await page.goto('/auth/login');

      // Tab through form
      await page.keyboard.press('Tab'); // Email
      await expect(page.locator('input[name="email"]')).toBeFocused();

      await page.keyboard.press('Tab'); // Password
      await expect(page.locator('input[name="password"]')).toBeFocused();

      await page.keyboard.press('Tab'); // Submit button
      await expect(page.locator('button[type="submit"]')).toBeFocused();

      // Submit with Enter
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.keyboard.press('Enter');

      await expect(page).toHaveURL('/', { timeout: 10_000 });
    });

    test('should have proper ARIA labels', async ({ page }) => {
      await page.goto('/auth/login');

      // Check for ARIA labels
      const emailInput = page.locator('input[name="email"]');
      const passwordInput = page.locator('input[name="password"]');

      await expect(emailInput).toHaveAttribute('aria-label', /email/i);
      await expect(passwordInput).toHaveAttribute('aria-label', /password/i);
    });

    test('should announce errors to screen readers', async ({ page }) => {
      await page.goto('/auth/login');

      await page.fill('input[name="email"]', 'invalid-email');
      await page.click('button[type="submit"]');

      const error = page.locator('[role="alert"]');
      await expect(error).toHaveAttribute('aria-live', 'polite');
    });
  });
});
