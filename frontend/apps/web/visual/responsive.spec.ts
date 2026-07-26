/**
 * Visual Regression Tests - Responsive Layouts
 * Tests mobile, tablet, and desktop viewport consistency
 */

import { devices, expect, test } from '@playwright/test';

test.describe('Mobile Responsive Tests', () => {
  test.use({ ...devices['iPhone 12'] });

  test('mobile navigation and layout', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <!-- Mobile Header -->
          <header class="sticky top-0 z-50 w-full border-b bg-card">
            <div class="flex h-14 items-center justify-between px-4">
              <button class="inline-flex items-center justify-center rounded-lg hover:bg-accent h-9 w-9">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h1 class="text-lg font-semibold">TraceRTM</h1>
              <button class="inline-flex items-center justify-center rounded-lg hover:bg-accent h-9 w-9">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </button>
            </div>
          </header>

          <!-- Mobile Content -->
          <main class="p-4 space-y-4">
            <div class="rounded-xl border bg-card p-4 space-y-3">
              <h2 class="text-xl font-semibold">Project Overview</h2>
              <p class="text-sm text-muted-foreground">
                Mobile-optimized card layout with responsive spacing and typography.
              </p>
              <div class="flex gap-2">
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-4 flex-1">
                  View
                </button>
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-9 px-4 flex-1">
                  Edit
                </button>
              </div>
            </div>

            <div class="rounded-xl border bg-card p-4 space-y-3">
              <h2 class="text-xl font-semibold">Recent Items</h2>
              <div class="space-y-2">
                <div class="flex items-center gap-3 p-3 rounded-lg border bg-background">
                  <div class="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
                    A
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium truncate">Item Alpha</p>
                    <p class="text-xs text-muted-foreground">2 hours ago</p>
                  </div>
                </div>
                <div class="flex items-center gap-3 p-3 rounded-lg border bg-background">
                  <div class="h-10 w-10 rounded-full bg-secondary flex items-center justify-center text-secondary-foreground font-semibold">
                    B
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium truncate">Item Beta</p>
                    <p class="text-xs text-muted-foreground">5 hours ago</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-xl border bg-card p-4 space-y-3">
              <h2 class="text-xl font-semibold">Quick Actions</h2>
              <div class="grid grid-cols-2 gap-2">
                <button class="flex flex-col items-center gap-2 p-4 rounded-lg border bg-background hover:bg-accent">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span class="text-xs font-medium">New Item</span>
                </button>
                <button class="flex flex-col items-center gap-2 p-4 rounded-lg border bg-background hover:bg-accent">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span class="text-xs font-medium">Search</span>
                </button>
                <button class="flex flex-col items-center gap-2 p-4 rounded-lg border bg-background hover:bg-accent">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span class="text-xs font-medium">Reports</span>
                </button>
                <button class="flex flex-col items-center gap-2 p-4 rounded-lg border bg-background hover:bg-accent">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span class="text-xs font-medium">Settings</span>
                </button>
              </div>
            </div>
          </main>

          <!-- Mobile Bottom Navigation -->
          <nav class="fixed bottom-0 left-0 right-0 border-t bg-card">
            <div class="flex justify-around items-center h-16 px-2">
              <button class="flex flex-col items-center gap-1 px-3 py-2 text-primary">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span class="text-xs font-medium">Home</span>
              </button>
              <button class="flex flex-col items-center gap-1 px-3 py-2 text-muted-foreground">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span class="text-xs font-medium">Projects</span>
              </button>
              <button class="flex flex-col items-center gap-1 px-3 py-2 text-muted-foreground">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span class="text-xs font-medium">Alerts</span>
              </button>
              <button class="flex flex-col items-center gap-1 px-3 py-2 text-muted-foreground">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span class="text-xs font-medium">Profile</span>
              </button>
            </div>
          </nav>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('mobile-layout.png', {
      fullPage: true,
      maxDiffPixels: 200,
    });
  });

  test('mobile form layout', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background p-4">
          <div class="rounded-xl border bg-card p-4 space-y-4">
            <h2 class="text-2xl font-semibold">Create Item</h2>

            <div class="space-y-4">
              <div class="space-y-2">
                <label class="text-sm font-medium">Title</label>
                <input type="text" placeholder="Enter title" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium">Category</label>
                <select class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                  <option>Requirements</option>
                  <option>Design</option>
                  <option>Development</option>
                  <option>Testing</option>
                </select>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium">Priority</label>
                <div class="flex gap-2">
                  <button class="flex-1 h-10 rounded-md border border-input bg-background hover:bg-accent text-sm font-medium">
                    Low
                  </button>
                  <button class="flex-1 h-10 rounded-md border-2 border-primary bg-primary/10 text-primary text-sm font-medium">
                    Medium
                  </button>
                  <button class="flex-1 h-10 rounded-md border border-input bg-background hover:bg-accent text-sm font-medium">
                    High
                  </button>
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium">Description</label>
                <textarea placeholder="Enter description..." rows="4" class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"></textarea>
              </div>

              <div class="flex gap-2 pt-4">
                <button class="flex-1 inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-4">
                  Create
                </button>
                <button class="flex-1 inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-10 px-4">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('mobile-form.png', {
      fullPage: true,
      maxDiffPixels: 200,
    });
  });
});

test.describe('Tablet Responsive Tests', () => {
  test.use({ ...devices['iPad Pro'] });

  test('tablet layout', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background">
          <!-- Tablet Header -->
          <header class="border-b bg-card">
            <div class="flex h-16 items-center justify-between px-6">
              <div class="flex items-center gap-4">
                <h1 class="text-xl font-bold">TraceRTM</h1>
                <nav class="flex gap-2">
                  <button class="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium">
                    Dashboard
                  </button>
                  <button class="px-4 py-2 rounded-lg hover:bg-accent text-sm font-medium">
                    Projects
                  </button>
                  <button class="px-4 py-2 rounded-lg hover:bg-accent text-sm font-medium">
                    Reports
                  </button>
                </nav>
              </div>
              <div class="flex items-center gap-2">
                <button class="h-9 w-9 rounded-lg hover:bg-accent flex items-center justify-center">
                  🔍
                </button>
                <button class="h-9 w-9 rounded-lg hover:bg-accent flex items-center justify-center">
                  🔔
                </button>
                <div class="h-9 w-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold text-sm">
                  JD
                </div>
              </div>
            </div>
          </header>

          <!-- Tablet Content -->
          <main class="p-6">
            <div class="grid grid-cols-2 gap-6">
              <div class="rounded-xl border bg-card p-6 space-y-4">
                <h2 class="text-2xl font-semibold">Active Projects</h2>
                <div class="space-y-3">
                  <div class="flex items-center justify-between p-4 rounded-lg border bg-background">
                    <div class="flex items-center gap-3">
                      <div class="h-12 w-12 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold">
                        A
                      </div>
                      <div>
                        <p class="font-medium">Project Alpha</p>
                        <p class="text-sm text-muted-foreground">12 items</p>
                      </div>
                    </div>
                    <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500 text-white">
                      Active
                    </span>
                  </div>
                  <div class="flex items-center justify-between p-4 rounded-lg border bg-background">
                    <div class="flex items-center gap-3">
                      <div class="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center text-secondary-foreground font-bold">
                        B
                      </div>
                      <div>
                        <p class="font-medium">Project Beta</p>
                        <p class="text-sm text-muted-foreground">8 items</p>
                      </div>
                    </div>
                    <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-yellow-500 text-black">
                      Review
                    </span>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border bg-card p-6 space-y-4">
                <h2 class="text-2xl font-semibold">Statistics</h2>
                <div class="grid grid-cols-2 gap-4">
                  <div class="p-4 rounded-lg bg-primary/10 border border-primary/20">
                    <p class="text-sm text-muted-foreground">Total Items</p>
                    <p class="text-3xl font-bold text-primary">142</p>
                  </div>
                  <div class="p-4 rounded-lg bg-secondary/10 border border-secondary/20">
                    <p class="text-sm text-muted-foreground">Completed</p>
                    <p class="text-3xl font-bold text-secondary">89</p>
                  </div>
                  <div class="p-4 rounded-lg bg-accent border">
                    <p class="text-sm text-muted-foreground">In Progress</p>
                    <p class="text-3xl font-bold">32</p>
                  </div>
                  <div class="p-4 rounded-lg bg-destructive/10 border border-destructive/20">
                    <p class="text-sm text-muted-foreground">Blocked</p>
                    <p class="text-3xl font-bold text-destructive">21</p>
                  </div>
                </div>
              </div>

              <div class="col-span-2 rounded-xl border bg-card p-6 space-y-4">
                <h2 class="text-2xl font-semibold">Recent Activity</h2>
                <div class="space-y-2">
                  <div class="flex items-center gap-4 p-3 rounded-lg hover:bg-accent">
                    <div class="h-2 w-2 rounded-full bg-green-500"></div>
                    <p class="flex-1 text-sm">Item REQ-001 was completed</p>
                    <p class="text-xs text-muted-foreground">2 min ago</p>
                  </div>
                  <div class="flex items-center gap-4 p-3 rounded-lg hover:bg-accent">
                    <div class="h-2 w-2 rounded-full bg-blue-500"></div>
                    <p class="flex-1 text-sm">New comment on DES-042</p>
                    <p class="text-xs text-muted-foreground">15 min ago</p>
                  </div>
                  <div class="flex items-center gap-4 p-3 rounded-lg hover:bg-accent">
                    <div class="h-2 w-2 rounded-full bg-yellow-500"></div>
                    <p class="flex-1 text-sm">Item DEV-123 needs review</p>
                    <p class="text-xs text-muted-foreground">1 hour ago</p>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('tablet-layout.png', {
      fullPage: true,
      maxDiffPixels: 200,
    });
  });
});

test.describe('Desktop Responsive Tests', () => {
  test.use({ ...devices['Desktop Chrome'] });

  test('desktop layout with sidebar', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="flex min-h-screen bg-background">
          <!-- Sidebar -->
          <aside class="w-64 border-r bg-card">
            <div class="flex h-16 items-center px-6 border-b">
              <h1 class="text-xl font-bold">TraceRTM</h1>
            </div>
            <nav class="p-4 space-y-2">
              <button class="w-full flex items-center gap-3 px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Dashboard
              </button>
              <button class="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Projects
              </button>
              <button class="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Items
              </button>
              <button class="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Reports
              </button>
              <button class="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Settings
              </button>
            </nav>
          </aside>

          <!-- Main Content -->
          <div class="flex-1 flex flex-col">
            <!-- Header -->
            <header class="h-16 border-b bg-card flex items-center justify-between px-6">
              <div class="flex items-center gap-4">
                <input type="search" placeholder="Search..." class="w-96 h-10 rounded-md border border-input bg-background px-4 text-sm" />
              </div>
              <div class="flex items-center gap-3">
                <button class="h-10 px-4 rounded-lg hover:bg-accent flex items-center gap-2 text-sm font-medium">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  New Item
                </button>
                <button class="h-10 w-10 rounded-lg hover:bg-accent flex items-center justify-center">
                  🔔
                </button>
                <div class="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
                  JD
                </div>
              </div>
            </header>

            <!-- Content -->
            <main class="flex-1 p-6">
              <div class="grid grid-cols-3 gap-6 mb-6">
                <div class="rounded-xl border bg-card p-6">
                  <p class="text-sm text-muted-foreground mb-2">Total Items</p>
                  <p class="text-4xl font-bold">1,423</p>
                  <p class="text-sm text-green-500 mt-2">↑ 12% from last month</p>
                </div>
                <div class="rounded-xl border bg-card p-6">
                  <p class="text-sm text-muted-foreground mb-2">Completed</p>
                  <p class="text-4xl font-bold">892</p>
                  <p class="text-sm text-green-500 mt-2">↑ 8% from last month</p>
                </div>
                <div class="rounded-xl border bg-card p-6">
                  <p class="text-sm text-muted-foreground mb-2">In Progress</p>
                  <p class="text-4xl font-bold">531</p>
                  <p class="text-sm text-yellow-500 mt-2">→ 2% from last month</p>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-6">
                <div class="rounded-xl border bg-card p-6 space-y-4">
                  <h2 class="text-xl font-semibold">Recent Projects</h2>
                  <div class="space-y-3">
                    <div class="flex items-center justify-between p-4 rounded-lg border bg-background hover:bg-accent cursor-pointer">
                      <div class="flex items-center gap-3">
                        <div class="h-10 w-10 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
                          A
                        </div>
                        <div>
                          <p class="font-medium">Project Alpha</p>
                          <p class="text-sm text-muted-foreground">24 items • Updated 2h ago</p>
                        </div>
                      </div>
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500 text-white">
                        Active
                      </span>
                    </div>
                    <div class="flex items-center justify-between p-4 rounded-lg border bg-background hover:bg-accent cursor-pointer">
                      <div class="flex items-center gap-3">
                        <div class="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center text-secondary-foreground font-bold text-sm">
                          B
                        </div>
                        <div>
                          <p class="font-medium">Project Beta</p>
                          <p class="text-sm text-muted-foreground">18 items • Updated 5h ago</p>
                        </div>
                      </div>
                      <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-yellow-500 text-black">
                        Review
                      </span>
                    </div>
                  </div>
                </div>

                <div class="rounded-xl border bg-card p-6 space-y-4">
                  <h2 class="text-xl font-semibold">Activity Feed</h2>
                  <div class="space-y-3">
                    <div class="flex gap-3">
                      <div class="h-2 w-2 mt-2 rounded-full bg-green-500"></div>
                      <div class="flex-1">
                        <p class="text-sm font-medium">Item REQ-001 completed</p>
                        <p class="text-xs text-muted-foreground">John Doe • 5 minutes ago</p>
                      </div>
                    </div>
                    <div class="flex gap-3">
                      <div class="h-2 w-2 mt-2 rounded-full bg-blue-500"></div>
                      <div class="flex-1">
                        <p class="text-sm font-medium">New comment on DES-042</p>
                        <p class="text-xs text-muted-foreground">Jane Smith • 15 minutes ago</p>
                      </div>
                    </div>
                    <div class="flex gap-3">
                      <div class="h-2 w-2 mt-2 rounded-full bg-yellow-500"></div>
                      <div class="flex-1">
                        <p class="text-sm font-medium">Item DEV-123 needs review</p>
                        <p class="text-xs text-muted-foreground">Bob Johnson • 1 hour ago</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('desktop-layout.png', {
      fullPage: true,
      maxDiffPixels: 200,
    });
  });
});

test.describe('Responsive Breakpoint Tests', () => {
  const viewports = [
    { height: 667, name: 'mobile-sm', width: 375 },
    { height: 926, name: 'mobile-lg', width: 428 },
    { height: 1024, name: 'tablet', width: 768 },
    { height: 800, name: 'desktop-sm', width: 1280 },
    { height: 1080, name: 'desktop-lg', width: 1920 },
  ];

  for (const viewport of viewports) {
    test(`grid layout at ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({
        height: viewport.height,
        width: viewport.width,
      });
      await page.goto('http://localhost:5173');

      await page.evaluate(() => {
        const root = document.querySelector('#root')!;
        root.innerHTML = `
          <div class="p-4 md:p-6 lg:p-8 bg-background min-h-screen">
            <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold mb-6">Responsive Grid</h1>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
              <div class="rounded-xl border bg-card p-4 md:p-6">
                <h3 class="font-semibold text-lg mb-2">Card 1</h3>
                <p class="text-sm text-muted-foreground">Responsive card layout</p>
              </div>
              <div class="rounded-xl border bg-card p-4 md:p-6">
                <h3 class="font-semibold text-lg mb-2">Card 2</h3>
                <p class="text-sm text-muted-foreground">Adapts to screen size</p>
              </div>
              <div class="rounded-xl border bg-card p-4 md:p-6">
                <h3 class="font-semibold text-lg mb-2">Card 3</h3>
                <p class="text-sm text-muted-foreground">Mobile-first design</p>
              </div>
              <div class="rounded-xl border bg-card p-4 md:p-6">
                <h3 class="font-semibold text-lg mb-2">Card 4</h3>
                <p class="text-sm text-muted-foreground">Tailwind breakpoints</p>
              </div>
              <div class="rounded-xl border bg-card p-4 md:p-6">
                <h3 class="font-semibold text-lg mb-2">Card 5</h3>
                <p class="text-sm text-muted-foreground">Grid auto-layout</p>
              </div>
              <div class="rounded-xl border bg-card p-4 md:p-6">
                <h3 class="font-semibold text-lg mb-2">Card 6</h3>
                <p class="text-sm text-muted-foreground">Flexible spacing</p>
              </div>
            </div>
          </div>
        `;
      });

      await expect(page).toHaveScreenshot(`responsive-${viewport.name}.png`, {
        fullPage: true,
        maxDiffPixels: 200,
      });
    });
  }
});
