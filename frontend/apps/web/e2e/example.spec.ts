/**
 * Basic E2E Test Example
 *
 * Demonstrates:
 * - Page navigation
 * - Element interaction
 * - Assertions
 * - Screenshots
 * - Network requests
 *
 * Tags: @smoke @e2e
 */
import { expect, test } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load and display title @smoke', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for page to be ready
    await page.waitForLoadState('networkidle');

    // Check title
    await expect(page).toHaveTitle(/TraceRTM/);

    // Take screenshot for visual reference
    await page.screenshot({
      fullPage: true,
      path: 'test-results/homepage.png',
    });
  });

  test('should navigate to login page', async ({ page }) => {
    await page.goto('/');

    // Find and click login button
    const loginButton = page.getByRole('link', { name: /login/i });
    await expect(loginButton).toBeVisible();
    await loginButton.click();

    // Verify navigation
    await expect(page).toHaveURL(/\/login/);
  });

  test('should handle API requests', async ({ page }) => {
    // Listen for API requests
    const apiRequests: string[] = [];
    page.on('request', (request) => {
      if (request.url().includes('/api/')) {
        apiRequests.push(request.url());
      }
    });

    await page.goto('/dashboard');

    // Wait for API calls to complete
    await page.waitForLoadState('networkidle');

    // Verify API was called
    expect(apiRequests.length).toBeGreaterThan(0);
  });
});

test.describe('Authentication Flow', () => {
  test('should show validation errors on invalid input', async ({ page }) => {
    await page.goto('/login');

    // Submit empty form
    await page.getByRole('button', { name: /submit|login/i }).click();

    // Check for validation errors
    const errorMessage = page.getByText(/required|invalid/i).first();
    await expect(errorMessage).toBeVisible();
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill form
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('password123');

    // Submit
    await page.getByRole('button', { name: /submit|login/i }).click();

    // Verify redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);

    // Verify user is logged in
    const userMenu = page.getByRole('button', { name: /profile|account/i });
    await expect(userMenu).toBeVisible();
  });
});
