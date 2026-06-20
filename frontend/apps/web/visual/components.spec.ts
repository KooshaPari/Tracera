/**
 * Visual Regression Tests - Core UI Components
 * Tests visual consistency of buttons, inputs, cards, badges, and other UI primitives
 */

import { expect, test } from '@playwright/test';

test.describe('Button Component Visual Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Create a test page with all button variants
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <link href="http://localhost:5173/src/index.css" rel="stylesheet">
          <script type="module">
            import { Button } from 'http://localhost:5173/@fs${process.cwd()}/packages/ui/src/components/Button.tsx'
          </script>
        </head>
        <body class="p-8 space-y-8 bg-background">
          <div id="root"></div>
        </body>
      </html>
    `);
  });

  test('button variants in light theme', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="space-y-8">
          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Button Variants</h2>
            <div class="flex gap-4 items-center flex-wrap">
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
                Default
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-10 px-4 py-2">
                Destructive
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                Outline
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-secondary text-secondary-foreground hover:bg-secondary/80 h-10 px-4 py-2">
                Secondary
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                Ghost
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 text-primary underline-offset-4 hover:underline h-10 px-4 py-2">
                Link
              </button>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Button Sizes</h2>
            <div class="flex gap-4 items-center flex-wrap">
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-9 rounded-md px-3">
                Small
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
                Default
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-11 rounded-md px-8">
                Large
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 w-10">
                🔍
              </button>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Button States</h2>
            <div class="flex gap-4 items-center flex-wrap">
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
                Normal
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 ring-2 ring-ring">
                Focused
              </button>
              <button disabled class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground pointer-events-none opacity-50 h-10 px-4 py-2">
                Disabled
              </button>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
                <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Loading
              </button>
            </div>
          </section>
        </div>
      `;
    });

    // Take screenshot of all button variants
    await expect(page.locator('#root')).toHaveScreenshot('buttons-variants.png', {
      maxDiffPixels: 100,
    });
  });

  test('button hover states', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="space-y-4">
          <button id="default-btn" class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
            Default Hover
          </button>
          <button id="outline-btn" class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
            Outline Hover
          </button>
        </div>
      `;
    });

    // Hover over button
    await page.locator('#default-btn').hover();
    await expect(page.locator('#default-btn')).toHaveScreenshot('button-default-hover.png');

    await page.locator('#outline-btn').hover();
    await expect(page.locator('#outline-btn')).toHaveScreenshot('button-outline-hover.png');
  });
});

test.describe('Input Component Visual Tests', () => {
  test('input variants and states', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8 space-y-6 max-w-md">
          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Input States</h2>

            <div class="space-y-2">
              <label class="text-sm font-medium">Default Input</label>
              <input type="text" placeholder="Enter text..." class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" />
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium">Filled Input</label>
              <input type="text" value="Sample text content" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" />
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium">Disabled Input</label>
              <input disabled type="text" placeholder="Disabled..." class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background cursor-not-allowed opacity-50" />
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium">Error Input</label>
              <input type="text" placeholder="Invalid input" class="flex h-10 w-full rounded-md border-2 border-destructive bg-background px-3 py-2 text-sm" />
              <p class="text-sm text-destructive">This field is required</p>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium">Textarea</label>
              <textarea placeholder="Enter description..." rows="4" class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"></textarea>
            </div>
          </section>
        </div>
      `;
    });

    await expect(page.locator('#root')).toHaveScreenshot('inputs-variants.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Card Component Visual Tests', () => {
  test('card layouts', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8 space-y-6">
          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Card Variants</h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="rounded-xl border bg-card text-card-foreground shadow">
                <div class="flex flex-col space-y-1.5 p-6">
                  <h3 class="font-semibold leading-none tracking-tight">Simple Card</h3>
                  <p class="text-sm text-muted-foreground">Card description goes here</p>
                </div>
                <div class="p-6 pt-0">
                  <p class="text-sm">This is the card content area with some sample text to demonstrate the layout and styling.</p>
                </div>
              </div>

              <div class="rounded-xl border bg-card text-card-foreground shadow">
                <div class="flex flex-col space-y-1.5 p-6">
                  <h3 class="font-semibold leading-none tracking-tight">Card with Actions</h3>
                  <p class="text-sm text-muted-foreground">Interactive card example</p>
                </div>
                <div class="p-6 pt-0 space-y-4">
                  <p class="text-sm">Card content with action buttons below.</p>
                  <div class="flex gap-2">
                    <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-3">
                      Confirm
                    </button>
                    <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-9 px-3">
                      Cancel
                    </button>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border bg-card text-card-foreground shadow hover:shadow-lg transition-shadow">
                <div class="flex flex-col space-y-1.5 p-6">
                  <h3 class="font-semibold leading-none tracking-tight">Hoverable Card</h3>
                  <p class="text-sm text-muted-foreground">Hover to see shadow effect</p>
                </div>
                <div class="p-6 pt-0">
                  <p class="text-sm">This card has an elevated shadow on hover.</p>
                </div>
              </div>

              <div class="rounded-xl border-2 border-primary bg-card text-card-foreground shadow">
                <div class="flex flex-col space-y-1.5 p-6">
                  <h3 class="font-semibold leading-none tracking-tight">Selected Card</h3>
                  <p class="text-sm text-muted-foreground">Active selection state</p>
                </div>
                <div class="p-6 pt-0">
                  <p class="text-sm">This card shows a selected/active state with a colored border.</p>
                </div>
              </div>
            </div>
          </section>
        </div>
      `;
    });

    await expect(page.locator('#root')).toHaveScreenshot('cards-variants.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Badge Component Visual Tests', () => {
  test('badge variants', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8 space-y-6">
          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Badge Variants</h2>
            <div class="flex gap-3 items-center flex-wrap">
              <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground hover:bg-primary/80">
                Default
              </span>
              <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                Secondary
              </span>
              <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80">
                Destructive
              </span>
              <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground">
                Outline
              </span>
              <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500 text-white">
                Success
              </span>
              <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-yellow-500 text-black">
                Warning
              </span>
              <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-blue-500 text-white">
                Info
              </span>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Badge with Icons</h2>
            <div class="flex gap-3 items-center flex-wrap">
              <span class="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-primary text-primary-foreground">
                <span class="h-2 w-2 rounded-full bg-white"></span>
                Online
              </span>
              <span class="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">
                <span class="h-2 w-2 rounded-full bg-yellow-500"></span>
                Away
              </span>
              <span class="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold text-foreground">
                <span class="h-2 w-2 rounded-full bg-gray-500"></span>
                Offline
              </span>
            </div>
          </section>
        </div>
      `;
    });

    await expect(page.locator('#root')).toHaveScreenshot('badges-variants.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Form Components Visual Tests', () => {
  test('complete form layout', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8 max-w-2xl mx-auto">
          <div class="rounded-xl border bg-card text-card-foreground shadow">
            <div class="flex flex-col space-y-1.5 p-6">
              <h3 class="font-semibold leading-none tracking-tight text-2xl">Create Account</h3>
              <p class="text-sm text-muted-foreground">Enter your information to create an account</p>
            </div>
            <div class="p-6 pt-0 space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="text-sm font-medium">First Name</label>
                  <input type="text" placeholder="John" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                </div>
                <div class="space-y-2">
                  <label class="text-sm font-medium">Last Name</label>
                  <input type="text" placeholder="Doe" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium">Email</label>
                <input type="email" placeholder="john.doe@example.com" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium">Password</label>
                <input type="password" placeholder="••••••••" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium">Role</label>
                <select class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                  <option>Developer</option>
                  <option>Designer</option>
                  <option>Product Manager</option>
                  <option>Other</option>
                </select>
              </div>

              <div class="flex items-center space-x-2">
                <input type="checkbox" id="terms" class="h-4 w-4 rounded border-input" />
                <label for="terms" class="text-sm font-medium">
                  I agree to the terms and conditions
                </label>
              </div>

              <div class="flex gap-3 pt-4">
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 flex-1">
                  Create Account
                </button>
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-10 px-4 py-2">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      `;
    });

    await expect(page.locator('#root')).toHaveScreenshot('form-complete.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Loading and Empty States', () => {
  test('loading states', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8 space-y-8">
          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Loading Spinners</h2>
            <div class="flex gap-6 items-center">
              <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg class="animate-spin h-6 w-6 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg class="animate-spin h-4 w-4 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Skeleton Loaders</h2>
            <div class="space-y-3 max-w-md">
              <div class="h-4 bg-muted rounded animate-pulse"></div>
              <div class="h-4 bg-muted rounded animate-pulse w-5/6"></div>
              <div class="h-4 bg-muted rounded animate-pulse w-4/6"></div>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Card Skeleton</h2>
            <div class="rounded-xl border bg-card p-6 max-w-md">
              <div class="space-y-3">
                <div class="h-6 bg-muted rounded animate-pulse w-3/4"></div>
                <div class="h-4 bg-muted rounded animate-pulse"></div>
                <div class="h-4 bg-muted rounded animate-pulse w-5/6"></div>
                <div class="h-4 bg-muted rounded animate-pulse w-4/6"></div>
              </div>
            </div>
          </section>
        </div>
      `;
    });

    // Disable animations for consistent screenshots
    await page.addStyleTag({
      content: '*, *::before, *::after { animation: none !important; }',
    });

    await expect(page.locator('#root')).toHaveScreenshot('loading-states.png', {
      maxDiffPixels: 100,
    });
  });

  test('empty states', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8">
          <div class="rounded-xl border bg-card p-12">
            <div class="flex flex-col items-center justify-center text-center space-y-4">
              <div class="rounded-full bg-muted p-6">
                <svg class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
              </div>
              <div class="space-y-2">
                <h3 class="text-2xl font-semibold">No items found</h3>
                <p class="text-muted-foreground max-w-md">
                  Get started by creating your first item. Click the button below to begin.
                </p>
              </div>
              <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 py-2">
                Create Item
              </button>
            </div>
          </div>
        </div>
      `;
    });

    await expect(page.locator('#root')).toHaveScreenshot('empty-state.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Alert Component Visual Tests', () => {
  test('alert variants', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8 space-y-6 bg-background max-w-3xl">
          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Alert Variants</h2>

            <!-- Info Alert -->
            <div class="rounded-lg border border-blue-200 bg-blue-50 dark:bg-blue-950 dark:border-blue-800 p-4">
              <div class="flex gap-3">
                <svg class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <h4 class="font-semibold text-blue-900 dark:text-blue-100">Information</h4>
                  <p class="text-sm text-blue-800 dark:text-blue-200 mt-1">
                    This is an informational alert with helpful details.
                  </p>
                </div>
              </div>
            </div>

            <!-- Success Alert -->
            <div class="rounded-lg border border-green-200 bg-green-50 dark:bg-green-950 dark:border-green-800 p-4">
              <div class="flex gap-3">
                <svg class="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <h4 class="font-semibold text-green-900 dark:text-green-100">Success</h4>
                  <p class="text-sm text-green-800 dark:text-green-200 mt-1">
                    Your changes have been saved successfully.
                  </p>
                </div>
              </div>
            </div>

            <!-- Warning Alert -->
            <div class="rounded-lg border border-yellow-200 bg-yellow-50 dark:bg-yellow-950 dark:border-yellow-800 p-4">
              <div class="flex gap-3">
                <svg class="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div class="flex-1">
                  <h4 class="font-semibold text-yellow-900 dark:text-yellow-100">Warning</h4>
                  <p class="text-sm text-yellow-800 dark:text-yellow-200 mt-1">
                    Please review your changes before proceeding.
                  </p>
                </div>
              </div>
            </div>

            <!-- Error Alert -->
            <div class="rounded-lg border border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800 p-4">
              <div class="flex gap-3">
                <svg class="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <h4 class="font-semibold text-red-900 dark:text-red-100">Error</h4>
                  <p class="text-sm text-red-800 dark:text-red-200 mt-1">
                    There was an error processing your request. Please try again.
                  </p>
                </div>
                <button class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Alert with Actions -->
            <div class="rounded-lg border border-purple-200 bg-purple-50 dark:bg-purple-950 dark:border-purple-800 p-4">
              <div class="flex gap-3">
                <svg class="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <div class="flex-1">
                  <h4 class="font-semibold text-purple-900 dark:text-purple-100">New Update Available</h4>
                  <p class="text-sm text-purple-800 dark:text-purple-200 mt-1">
                    A new version of TraceRTM is available. Update now to get the latest features.
                  </p>
                  <div class="flex gap-2 mt-3">
                    <button class="inline-flex items-center justify-center rounded-lg text-xs font-medium bg-purple-600 text-white hover:bg-purple-700 h-8 px-3">
                      Update Now
                    </button>
                    <button class="inline-flex items-center justify-center rounded-lg text-xs font-medium border border-purple-300 bg-white dark:bg-purple-900 text-purple-900 dark:text-purple-100 h-8 px-3">
                      Later
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      `;
    });

    await expect(page.locator('#root')).toHaveScreenshot('alerts-variants.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Select and Dropdown Visual Tests', () => {
  test('select and dropdown states', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="p-8 space-y-6 bg-background max-w-2xl">
          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Select Components</h2>

            <div class="space-y-2">
              <label class="text-sm font-medium">Default Select</label>
              <select class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option>Select an option...</option>
                <option>Option 1</option>
                <option>Option 2</option>
                <option>Option 3</option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium">Selected Value</label>
              <select class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option>Option 1</option>
                <option selected>Option 2</option>
                <option>Option 3</option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium">Disabled Select</label>
              <select disabled class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm opacity-50 cursor-not-allowed">
                <option>Option 1</option>
                <option>Option 2</option>
              </select>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Checkbox and Radio</h2>

            <div class="space-y-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" class="h-4 w-4 rounded border-input" />
                <span class="text-sm">Unchecked checkbox</span>
              </label>

              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked class="h-4 w-4 rounded border-input" />
                <span class="text-sm">Checked checkbox</span>
              </label>

              <label class="flex items-center gap-2 cursor-not-allowed opacity-50">
                <input type="checkbox" disabled class="h-4 w-4 rounded border-input" />
                <span class="text-sm">Disabled checkbox</span>
              </label>
            </div>

            <div class="space-y-3 pt-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="radio-group" class="h-4 w-4" />
                <span class="text-sm">Radio option 1</span>
              </label>

              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="radio-group" checked class="h-4 w-4" />
                <span class="text-sm">Radio option 2 (selected)</span>
              </label>

              <label class="flex items-center gap-2 cursor-not-allowed opacity-50">
                <input type="radio" name="radio-group" disabled class="h-4 w-4" />
                <span class="text-sm">Radio option 3 (disabled)</span>
              </label>
            </div>
          </section>
        </div>
      `;
    });

    await expect(page.locator('#root')).toHaveScreenshot('select-checkbox-radio.png', {
      maxDiffPixels: 100,
    });
  });
});
