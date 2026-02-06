/**
 * Visual Regression Tests - Full Page Screenshots
 * Tests complete page layouts including Dashboard, Projects, Items, and Settings
 */

import { expect, test } from '@playwright/test';

import {
  LAYOUT_SCREENSHOT_OPTIONS,
  setTheme,
  setupVisualTest,
} from './helpers/visual-test-helpers';

test.describe('Dashboard Page Visual Tests', () => {
  test('dashboard page light theme', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <!-- Dashboard Header -->
          <header class="border-b bg-card px-6 py-4">
            <h1 class="text-3xl font-bold text-foreground">Dashboard</h1>
            <p class="text-muted-foreground">Welcome to TraceRTM</p>
          </header>

          <!-- Dashboard Content -->
          <main class="p-6 space-y-6">
            <!-- Stats Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Total Projects</p>
                <p class="text-3xl font-bold text-foreground">12</p>
                <p class="text-xs text-green-600">+2 this month</p>
              </div>
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Active Items</p>
                <p class="text-3xl font-bold text-foreground">248</p>
                <p class="text-xs text-blue-600">15 updated today</p>
              </div>
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Trace Links</p>
                <p class="text-3xl font-bold text-foreground">1,234</p>
                <p class="text-xs text-muted-foreground">Last 30 days</p>
              </div>
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Coverage</p>
                <p class="text-3xl font-bold text-foreground">94%</p>
                <p class="text-xs text-green-600">+3% this week</p>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="rounded-xl border bg-card">
                <div class="border-b p-6">
                  <h2 class="text-xl font-semibold">Recent Projects</h2>
                </div>
                <div class="p-6 space-y-3">
                  <div class="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors">
                    <div class="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
                      A
                    </div>
                    <div class="flex-1">
                      <p class="font-medium">Project Alpha</p>
                      <p class="text-xs text-muted-foreground">Updated 2 hours ago</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors">
                    <div class="h-10 w-10 rounded-full bg-secondary flex items-center justify-center text-secondary-foreground font-semibold">
                      B
                    </div>
                    <div class="flex-1">
                      <p class="font-medium">Project Beta</p>
                      <p class="text-xs text-muted-foreground">Updated 5 hours ago</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors">
                    <div class="h-10 w-10 rounded-full bg-accent flex items-center justify-center text-accent-foreground font-semibold">
                      C
                    </div>
                    <div class="flex-1">
                      <p class="font-medium">Project Charlie</p>
                      <p class="text-xs text-muted-foreground">Updated yesterday</p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border bg-card">
                <div class="border-b p-6">
                  <h2 class="text-xl font-semibold">Activity Timeline</h2>
                </div>
                <div class="p-6 space-y-4">
                  <div class="flex gap-3">
                    <div class="flex flex-col items-center">
                      <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs">
                        U
                      </div>
                      <div class="flex-1 w-0.5 bg-border mt-2"></div>
                    </div>
                    <div class="flex-1 pb-4">
                      <p class="font-medium text-sm">Item updated</p>
                      <p class="text-xs text-muted-foreground">REQ-001 modified by John Doe</p>
                      <p class="text-xs text-muted-foreground mt-1">2 hours ago</p>
                    </div>
                  </div>
                  <div class="flex gap-3">
                    <div class="flex flex-col items-center">
                      <div class="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white text-xs">
                        C
                      </div>
                      <div class="flex-1 w-0.5 bg-border mt-2"></div>
                    </div>
                    <div class="flex-1 pb-4">
                      <p class="font-medium text-sm">Link created</p>
                      <p class="text-xs text-muted-foreground">REQ-001 → TEST-042</p>
                      <p class="text-xs text-muted-foreground mt-1">5 hours ago</p>
                    </div>
                  </div>
                  <div class="flex gap-3">
                    <div class="flex flex-col items-center">
                      <div class="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center text-white text-xs">
                        N
                      </div>
                    </div>
                    <div class="flex-1">
                      <p class="font-medium text-sm">New project</p>
                      <p class="text-xs text-muted-foreground">Project Delta created</p>
                      <p class="text-xs text-muted-foreground mt-1">Yesterday</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('dashboard-light.png', LAYOUT_SCREENSHOT_OPTIONS);
  });

  test('dashboard page dark theme', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'dark');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <header class="border-b bg-card px-6 py-4">
            <h1 class="text-3xl font-bold text-foreground">Dashboard</h1>
            <p class="text-muted-foreground">Welcome to TraceRTM</p>
          </header>

          <main class="p-6 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Total Projects</p>
                <p class="text-3xl font-bold text-foreground">12</p>
                <p class="text-xs text-green-400">+2 this month</p>
              </div>
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Active Items</p>
                <p class="text-3xl font-bold text-foreground">248</p>
                <p class="text-xs text-blue-400">15 updated today</p>
              </div>
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Trace Links</p>
                <p class="text-3xl font-bold text-foreground">1,234</p>
                <p class="text-xs text-muted-foreground">Last 30 days</p>
              </div>
              <div class="rounded-xl border bg-card p-6 space-y-2">
                <p class="text-sm text-muted-foreground">Coverage</p>
                <p class="text-3xl font-bold text-foreground">94%</p>
                <p class="text-xs text-green-400">+3% this week</p>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('dashboard-dark.png', LAYOUT_SCREENSHOT_OPTIONS);
  });
});

test.describe('Projects List Page Visual Tests', () => {
  test('projects list with cards', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <header class="border-b bg-card px-6 py-4">
            <div class="flex items-center justify-between">
              <div>
                <h1 class="text-3xl font-bold text-foreground">Projects</h1>
                <p class="text-muted-foreground">Manage your traceability projects</p>
              </div>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-4">
                New Project
              </button>
            </div>
          </header>

          <main class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div class="rounded-xl border bg-card hover:shadow-lg transition-shadow">
                <div class="p-6 space-y-4">
                  <div class="flex items-start justify-between">
                    <div class="h-12 w-12 rounded-lg bg-primary flex items-center justify-center text-primary-foreground text-xl font-bold">
                      A
                    </div>
                    <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500 text-white">
                      Active
                    </span>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold">Project Alpha</h3>
                    <p class="text-sm text-muted-foreground mt-1">Enterprise requirements tracking system</p>
                  </div>
                  <div class="flex items-center gap-4 text-sm text-muted-foreground">
                    <div class="flex items-center gap-1">
                      <span>📝</span>
                      <span>42 items</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <span>🔗</span>
                      <span>128 links</span>
                    </div>
                  </div>
                  <div class="flex gap-2 pt-2">
                    <button class="flex-1 inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-3">
                      Open
                    </button>
                    <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-9 px-3">
                      Settings
                    </button>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border bg-card hover:shadow-lg transition-shadow">
                <div class="p-6 space-y-4">
                  <div class="flex items-start justify-between">
                    <div class="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center text-secondary-foreground text-xl font-bold">
                      B
                    </div>
                    <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-yellow-500 text-black">
                      In Progress
                    </span>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold">Project Beta</h3>
                    <p class="text-sm text-muted-foreground mt-1">Medical device compliance tracking</p>
                  </div>
                  <div class="flex items-center gap-4 text-sm text-muted-foreground">
                    <div class="flex items-center gap-1">
                      <span>📝</span>
                      <span>67 items</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <span>🔗</span>
                      <span>201 links</span>
                    </div>
                  </div>
                  <div class="flex gap-2 pt-2">
                    <button class="flex-1 inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-3">
                      Open
                    </button>
                    <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-9 px-3">
                      Settings
                    </button>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border bg-card hover:shadow-lg transition-shadow">
                <div class="p-6 space-y-4">
                  <div class="flex items-start justify-between">
                    <div class="h-12 w-12 rounded-lg bg-accent flex items-center justify-center text-accent-foreground text-xl font-bold">
                      C
                    </div>
                    <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold text-foreground">
                      Archived
                    </span>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold">Project Charlie</h3>
                    <p class="text-sm text-muted-foreground mt-1">Legacy system documentation</p>
                  </div>
                  <div class="flex items-center gap-4 text-sm text-muted-foreground">
                    <div class="flex items-center gap-1">
                      <span>📝</span>
                      <span>89 items</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <span>🔗</span>
                      <span>345 links</span>
                    </div>
                  </div>
                  <div class="flex gap-2 pt-2">
                    <button class="flex-1 inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-3">
                      Open
                    </button>
                    <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-9 px-3">
                      Settings
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('projects-list.png', LAYOUT_SCREENSHOT_OPTIONS);
  });
});

test.describe('Items Table Page Visual Tests', () => {
  test('items table view', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <header class="border-b bg-card px-6 py-4">
            <div class="flex items-center justify-between">
              <h1 class="text-3xl font-bold text-foreground">Items</h1>
              <div class="flex items-center gap-3">
                <input
                  type="text"
                  placeholder="Search items..."
                  class="flex h-10 w-64 rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-4">
                  New Item
                </button>
              </div>
            </div>
          </header>

          <main class="p-6">
            <div class="rounded-xl border bg-card">
              <table class="w-full">
                <thead class="border-b bg-muted/50">
                  <tr>
                    <th class="text-left p-4 font-medium text-sm">ID</th>
                    <th class="text-left p-4 font-medium text-sm">Title</th>
                    <th class="text-left p-4 font-medium text-sm">Type</th>
                    <th class="text-left p-4 font-medium text-sm">Status</th>
                    <th class="text-left p-4 font-medium text-sm">Updated</th>
                    <th class="text-right p-4 font-medium text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b hover:bg-muted/50 transition-colors">
                    <td class="p-4 font-mono text-sm">REQ-001</td>
                    <td class="p-4 text-sm">User authentication system</td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-blue-500 text-white">
                        Requirement
                      </span>
                    </td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500 text-white">
                        Approved
                      </span>
                    </td>
                    <td class="p-4 text-sm text-muted-foreground">2 hours ago</td>
                    <td class="p-4 text-right">
                      <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium hover:bg-accent h-8 w-8">
                        •••
                      </button>
                    </td>
                  </tr>
                  <tr class="border-b hover:bg-muted/50 transition-colors">
                    <td class="p-4 font-mono text-sm">TEST-042</td>
                    <td class="p-4 text-sm">Login flow validation test</td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-purple-500 text-white">
                        Test Case
                      </span>
                    </td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500 text-white">
                        Passing
                      </span>
                    </td>
                    <td class="p-4 text-sm text-muted-foreground">5 hours ago</td>
                    <td class="p-4 text-right">
                      <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium hover:bg-accent h-8 w-8">
                        •••
                      </button>
                    </td>
                  </tr>
                  <tr class="border-b hover:bg-muted/50 transition-colors">
                    <td class="p-4 font-mono text-sm">DOC-103</td>
                    <td class="p-4 text-sm">Authentication API documentation</td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-orange-500 text-white">
                        Documentation
                      </span>
                    </td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-yellow-500 text-black">
                        In Review
                      </span>
                    </td>
                    <td class="p-4 text-sm text-muted-foreground">Yesterday</td>
                    <td class="p-4 text-right">
                      <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium hover:bg-accent h-8 w-8">
                        •••
                      </button>
                    </td>
                  </tr>
                  <tr class="hover:bg-muted/50 transition-colors">
                    <td class="p-4 font-mono text-sm">CODE-087</td>
                    <td class="p-4 text-sm">JWT token validation module</td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-indigo-500 text-white">
                        Code
                      </span>
                    </td>
                    <td class="p-4 text-sm">
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500 text-white">
                        Implemented
                      </span>
                    </td>
                    <td class="p-4 text-sm text-muted-foreground">2 days ago</td>
                    <td class="p-4 text-right">
                      <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium hover:bg-accent h-8 w-8">
                        •••
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('items-table.png', LAYOUT_SCREENSHOT_OPTIONS);
  });
});

test.describe('Empty State Pages', () => {
  test('empty projects list', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <header class="border-b bg-card px-6 py-4">
            <h1 class="text-3xl font-bold text-foreground">Projects</h1>
          </header>

          <main class="p-6">
            <div class="rounded-xl border bg-card p-12">
              <div class="flex flex-col items-center justify-center text-center space-y-4 py-12">
                <div class="rounded-full bg-muted p-6">
                  <svg class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </div>
                <div class="space-y-2">
                  <h3 class="text-2xl font-semibold">No projects yet</h3>
                  <p class="text-muted-foreground max-w-md">
                    Get started by creating your first traceability project. Projects help organize your requirements, tests, and documentation.
                  </p>
                </div>
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-6 py-2">
                  Create First Project
                </button>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('empty-projects.png', LAYOUT_SCREENSHOT_OPTIONS);
  });

  test('empty items list', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <header class="border-b bg-card px-6 py-4">
            <h1 class="text-3xl font-bold text-foreground">Items</h1>
          </header>

          <main class="p-6">
            <div class="rounded-xl border bg-card p-12">
              <div class="flex flex-col items-center justify-center text-center space-y-4 py-12">
                <div class="rounded-full bg-muted p-6">
                  <svg class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="space-y-2">
                  <h3 class="text-2xl font-semibold">No items found</h3>
                  <p class="text-muted-foreground max-w-md">
                    Start tracking requirements, test cases, code, and documentation. Create your first item to begin building traceability.
                  </p>
                </div>
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-6 py-2">
                  Create Item
                </button>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('empty-items.png', LAYOUT_SCREENSHOT_OPTIONS);
  });
});

test.describe('Settings Page Visual Tests', () => {
  test('settings page layout', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <header class="border-b bg-card px-6 py-4">
            <h1 class="text-3xl font-bold text-foreground">Settings</h1>
            <p class="text-muted-foreground">Manage your account and preferences</p>
          </header>

          <main class="p-6">
            <div class="max-w-4xl mx-auto space-y-6">
              <!-- Profile Settings -->
              <div class="rounded-xl border bg-card">
                <div class="border-b p-6">
                  <h2 class="text-xl font-semibold">Profile</h2>
                  <p class="text-sm text-muted-foreground">Manage your personal information</p>
                </div>
                <div class="p-6 space-y-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <label class="text-sm font-medium">First Name</label>
                      <input type="text" value="John" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                    </div>
                    <div class="space-y-2">
                      <label class="text-sm font-medium">Last Name</label>
                      <input type="text" value="Doe" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                    </div>
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-medium">Email</label>
                    <input type="email" value="john.doe@example.com" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                  </div>
                  <div class="flex gap-2 pt-2">
                    <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-4">
                      Save Changes
                    </button>
                    <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-10 px-4">
                      Cancel
                    </button>
                  </div>
                </div>
              </div>

              <!-- Appearance Settings -->
              <div class="rounded-xl border bg-card">
                <div class="border-b p-6">
                  <h2 class="text-xl font-semibold">Appearance</h2>
                  <p class="text-sm text-muted-foreground">Customize how TraceRTM looks</p>
                </div>
                <div class="p-6 space-y-4">
                  <div class="space-y-2">
                    <label class="text-sm font-medium">Theme</label>
                    <div class="flex gap-4">
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="theme" checked class="h-4 w-4" />
                        <span class="text-sm">Light</span>
                      </label>
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="theme" class="h-4 w-4" />
                        <span class="text-sm">Dark</span>
                      </label>
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="theme" class="h-4 w-4" />
                        <span class="text-sm">System</span>
                      </label>
                    </div>
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-medium">Font Size</label>
                    <select class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                      <option>Small</option>
                      <option selected>Medium</option>
                      <option>Large</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Notifications Settings -->
              <div class="rounded-xl border bg-card">
                <div class="border-b p-6">
                  <h2 class="text-xl font-semibold">Notifications</h2>
                  <p class="text-sm text-muted-foreground">Configure notification preferences</p>
                </div>
                <div class="p-6 space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="font-medium text-sm">Email Notifications</p>
                      <p class="text-xs text-muted-foreground">Receive updates via email</p>
                    </div>
                    <input type="checkbox" checked class="h-4 w-4" />
                  </div>
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="font-medium text-sm">Desktop Notifications</p>
                      <p class="text-xs text-muted-foreground">Show browser notifications</p>
                    </div>
                    <input type="checkbox" class="h-4 w-4" />
                  </div>
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="font-medium text-sm">Link Updates</p>
                      <p class="text-xs text-muted-foreground">Notify when trace links change</p>
                    </div>
                    <input type="checkbox" checked class="h-4 w-4" />
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('settings-page.png', LAYOUT_SCREENSHOT_OPTIONS);
  });
});

test.describe('Error State Pages', () => {
  test('404 error page', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background flex items-center justify-center p-6">
          <div class="text-center space-y-4 max-w-md">
            <div class="text-8xl font-bold text-primary">404</div>
            <h1 class="text-3xl font-bold text-foreground">Page Not Found</h1>
            <p class="text-muted-foreground">
              The page you're looking for doesn't exist or has been moved.
            </p>
            <div class="flex gap-3 justify-center pt-4">
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-6">
                Go Home
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-10 px-6">
                Contact Support
              </button>
            </div>
          </div>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('error-404.png', LAYOUT_SCREENSHOT_OPTIONS);
  });

  test('general error state', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <header class="border-b bg-card px-6 py-4">
            <h1 class="text-3xl font-bold text-foreground">Dashboard</h1>
          </header>

          <main class="p-6">
            <div class="rounded-xl border-2 border-destructive bg-destructive/10 p-12">
              <div class="flex flex-col items-center justify-center text-center space-y-4">
                <div class="rounded-full bg-destructive/20 p-6">
                  <svg class="h-12 w-12 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div class="space-y-2">
                  <h3 class="text-2xl font-semibold text-destructive">Something went wrong</h3>
                  <p class="text-muted-foreground max-w-md">
                    We encountered an error while loading your data. Please try again or contact support if the problem persists.
                  </p>
                </div>
                <div class="flex gap-3">
                  <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-6">
                    Try Again
                  </button>
                  <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-10 px-6">
                    Go Back
                  </button>
                </div>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('error-general.png', LAYOUT_SCREENSHOT_OPTIONS);
  });
});

test.describe('Command Palette Visual Tests', () => {
  test('command palette open state', async ({ page }) => {
    await setupVisualTest(page);
    await setTheme(page, 'light');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background relative">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black/50 z-40"></div>

          <!-- Command Palette -->
          <div class="fixed inset-0 z-50 flex items-start justify-center pt-20">
            <div class="w-full max-w-2xl mx-4">
              <div class="rounded-xl border bg-card shadow-2xl">
                <!-- Search Input -->
                <div class="border-b p-4">
                  <input
                    type="text"
                    placeholder="Type a command or search..."
                    class="w-full bg-transparent text-lg outline-none"
                    value="proj"
                  />
                </div>

                <!-- Command List -->
                <div class="max-h-96 overflow-y-auto p-2">
                  <div class="space-y-1">
                    <!-- Selected -->
                    <div class="flex items-center gap-3 p-3 rounded-lg bg-primary text-primary-foreground">
                      <div class="flex items-center justify-center h-8 w-8 rounded bg-primary-foreground/20">
                        <span class="text-sm">📁</span>
                      </div>
                      <div class="flex-1">
                        <p class="font-medium text-sm">Go to Projects</p>
                        <p class="text-xs opacity-80">Navigate to projects list</p>
                      </div>
                      <kbd class="px-2 py-1 text-xs rounded bg-primary-foreground/20">⌘P</kbd>
                    </div>

                    <!-- Regular Items -->
                    <div class="flex items-center gap-3 p-3 rounded-lg hover:bg-accent">
                      <div class="flex items-center justify-center h-8 w-8 rounded bg-muted">
                        <span class="text-sm">➕</span>
                      </div>
                      <div class="flex-1">
                        <p class="font-medium text-sm">New Project</p>
                        <p class="text-xs text-muted-foreground">Create a new project</p>
                      </div>
                      <kbd class="px-2 py-1 text-xs rounded bg-muted">⌘N</kbd>
                    </div>

                    <div class="flex items-center gap-3 p-3 rounded-lg hover:bg-accent">
                      <div class="flex items-center justify-center h-8 w-8 rounded bg-muted">
                        <span class="text-sm">🔍</span>
                      </div>
                      <div class="flex-1">
                        <p class="font-medium text-sm">Search Projects</p>
                        <p class="text-xs text-muted-foreground">Find projects by name</p>
                      </div>
                      <kbd class="px-2 py-1 text-xs rounded bg-muted">⌘K</kbd>
                    </div>

                    <!-- Category Header -->
                    <div class="px-3 pt-4 pb-2">
                      <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Recent</p>
                    </div>

                    <div class="flex items-center gap-3 p-3 rounded-lg hover:bg-accent">
                      <div class="flex items-center justify-center h-8 w-8 rounded bg-muted">
                        <span class="text-sm">📄</span>
                      </div>
                      <div class="flex-1">
                        <p class="font-medium text-sm">Project Alpha</p>
                        <p class="text-xs text-muted-foreground">Opened 2 hours ago</p>
                      </div>
                    </div>

                    <div class="flex items-center gap-3 p-3 rounded-lg hover:bg-accent">
                      <div class="flex items-center justify-center h-8 w-8 rounded bg-muted">
                        <span class="text-sm">📄</span>
                      </div>
                      <div class="flex-1">
                        <p class="font-medium text-sm">Project Beta</p>
                        <p class="text-xs text-muted-foreground">Opened yesterday</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Footer -->
                <div class="border-t p-2 flex items-center justify-between text-xs text-muted-foreground bg-muted/30">
                  <div class="flex gap-4">
                    <span class="flex items-center gap-1">
                      <kbd class="px-1.5 py-0.5 rounded bg-background border">↑</kbd>
                      <kbd class="px-1.5 py-0.5 rounded bg-background border">↓</kbd>
                      Navigate
                    </span>
                    <span class="flex items-center gap-1">
                      <kbd class="px-1.5 py-0.5 rounded bg-background border">↵</kbd>
                      Select
                    </span>
                  </div>
                  <span class="flex items-center gap-1">
                    <kbd class="px-1.5 py-0.5 rounded bg-background border">Esc</kbd>
                    Close
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Page Content (blurred) -->
          <div class="blur-sm">
            <header class="border-b bg-card px-6 py-4">
              <h1 class="text-3xl font-bold">Dashboard</h1>
            </header>
          </div>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('command-palette-open.png', {
      ...LAYOUT_SCREENSHOT_OPTIONS,
      fullPage: false,
    });
  });
});
