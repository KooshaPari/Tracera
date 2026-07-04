/**
 * Visual Regression Tests - Theme Consistency
 * Tests light/dark mode switching and theme variable consistency
 */

import { expect, test } from '@playwright/test';

test.describe('Theme Switching Visual Tests', () => {
  test('light theme components', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Set light theme
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background p-8 space-y-8">
          <header class="border-b pb-4">
            <h1 class="text-4xl font-bold text-foreground">Light Theme</h1>
            <p class="text-muted-foreground">Component showcase in light mode</p>
          </header>

          <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-4">
              <h2 class="text-2xl font-semibold">Primary Card</h2>
              <p class="text-sm text-muted-foreground">
                This card demonstrates the primary color scheme in light mode.
              </p>
              <div class="flex gap-2">
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-4">
                  Primary
                </button>
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-secondary text-secondary-foreground h-9 px-4">
                  Secondary
                </button>
              </div>
            </div>

            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-4">
              <h2 class="text-2xl font-semibold">Form Elements</h2>
              <input type="text" placeholder="Sample input" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
              <select class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option>Option 1</option>
                <option>Option 2</option>
              </select>
            </div>

            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-3">
              <h2 class="text-2xl font-semibold">Status Badges</h2>
              <div class="flex gap-2 flex-wrap">
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-primary text-primary-foreground">Active</span>
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">Pending</span>
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-destructive text-destructive-foreground">Error</span>
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold text-foreground">Inactive</span>
              </div>
            </div>

            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-3">
              <h2 class="text-2xl font-semibold">Alerts</h2>
              <div class="rounded-lg border border-blue-200 bg-blue-50 p-4 text-blue-900">
                <p class="text-sm font-medium">Info: System update available</p>
              </div>
              <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-yellow-900">
                <p class="text-sm font-medium">Warning: Disk space low</p>
              </div>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Typography Scale</h2>
            <div class="rounded-xl border bg-card p-6 space-y-2">
              <h1 class="text-4xl font-bold text-foreground">Heading 1</h1>
              <h2 class="text-3xl font-bold text-foreground">Heading 2</h2>
              <h3 class="text-2xl font-bold text-foreground">Heading 3</h3>
              <h4 class="text-xl font-bold text-foreground">Heading 4</h4>
              <p class="text-base text-foreground">Body text - regular paragraph content</p>
              <p class="text-sm text-muted-foreground">Small text - secondary information</p>
              <p class="text-xs text-muted-foreground">Extra small text - captions and labels</p>
            </div>
          </section>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('theme-light-full.png', {
      fullPage: true,
      maxDiffPixels: 200,
    });
  });

  test('dark theme components', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Set dark theme
    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
    });

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background p-8 space-y-8">
          <header class="border-b pb-4">
            <h1 class="text-4xl font-bold text-foreground">Dark Theme</h1>
            <p class="text-muted-foreground">Component showcase in dark mode</p>
          </header>

          <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-4">
              <h2 class="text-2xl font-semibold">Primary Card</h2>
              <p class="text-sm text-muted-foreground">
                This card demonstrates the primary color scheme in dark mode.
              </p>
              <div class="flex gap-2">
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-4">
                  Primary
                </button>
                <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-secondary text-secondary-foreground h-9 px-4">
                  Secondary
                </button>
              </div>
            </div>

            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-4">
              <h2 class="text-2xl font-semibold">Form Elements</h2>
              <input type="text" placeholder="Sample input" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
              <select class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option>Option 1</option>
                <option>Option 2</option>
              </select>
            </div>

            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-3">
              <h2 class="text-2xl font-semibold">Status Badges</h2>
              <div class="flex gap-2 flex-wrap">
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-primary text-primary-foreground">Active</span>
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">Pending</span>
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-destructive text-destructive-foreground">Error</span>
                <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold text-foreground">Inactive</span>
              </div>
            </div>

            <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-3">
              <h2 class="text-2xl font-semibold">Alerts</h2>
              <div class="rounded-lg border border-blue-800 bg-blue-950 p-4 text-blue-100">
                <p class="text-sm font-medium">Info: System update available</p>
              </div>
              <div class="rounded-lg border border-yellow-800 bg-yellow-950 p-4 text-yellow-100">
                <p class="text-sm font-medium">Warning: Disk space low</p>
              </div>
            </div>
          </section>

          <section class="space-y-4">
            <h2 class="text-2xl font-bold">Typography Scale</h2>
            <div class="rounded-xl border bg-card p-6 space-y-2">
              <h1 class="text-4xl font-bold text-foreground">Heading 1</h1>
              <h2 class="text-3xl font-bold text-foreground">Heading 2</h2>
              <h3 class="text-2xl font-bold text-foreground">Heading 3</h3>
              <h4 class="text-xl font-bold text-foreground">Heading 4</h4>
              <p class="text-base text-foreground">Body text - regular paragraph content</p>
              <p class="text-sm text-muted-foreground">Small text - secondary information</p>
              <p class="text-xs text-muted-foreground">Extra small text - captions and labels</p>
            </div>
          </section>
        </div>
      `;
    });

    await expect(page).toHaveScreenshot('theme-dark-full.png', {
      fullPage: true,
      maxDiffPixels: 200,
    });
  });

  test('theme toggle animation', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="min-h-screen bg-background p-8 flex items-center justify-center">
          <div class="rounded-xl border bg-card text-card-foreground shadow-lg p-8 space-y-6 max-w-md">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-2xl font-bold">Theme Settings</h2>
                <p class="text-sm text-muted-foreground">Choose your preferred theme</p>
              </div>
              <button id="theme-toggle" class="inline-flex items-center justify-center rounded-lg bg-secondary text-secondary-foreground h-10 w-10">
                🌙
              </button>
            </div>

            <div class="space-y-4">
              <div class="p-4 rounded-lg bg-accent">
                <p class="text-sm font-medium">Current theme: <span id="theme-name">Light</span></p>
              </div>

              <div class="grid grid-cols-3 gap-2">
                <div class="h-20 rounded bg-primary"></div>
                <div class="h-20 rounded bg-secondary"></div>
                <div class="h-20 rounded bg-accent"></div>
              </div>
            </div>
          </div>
        </div>
      `;

      // Add theme toggle functionality
      const toggleBtn = document.querySelector('#theme-toggle')!;
      const themeName = document.querySelector('#theme-name')!;

      toggleBtn.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark');
        toggleBtn.textContent = isDark ? '☀️' : '🌙';
        themeName.textContent = isDark ? 'Dark' : 'Light';
      });
    });

    // Light theme
    await expect(page.locator('.min-h-screen')).toHaveScreenshot('theme-toggle-light.png');

    // Click toggle
    await page.click('#theme-toggle');
    await page.waitForTimeout(300); // Wait for transition

    // Dark theme
    await expect(page.locator('.min-h-screen')).toHaveScreenshot('theme-toggle-dark.png');
  });

  test('color palette consistency', async ({ page }) => {
    await page.goto('http://localhost:5173');

    for (const theme of ['light', 'dark']) {
      await page.evaluate((t) => {
        document.documentElement.classList.toggle('dark', t === 'dark');
      }, theme);

      await page.evaluate(() => {
        const root = document.querySelector('#root')!;
        root.innerHTML = `
          <div class="bg-background p-8 space-y-8">
            <h1 class="text-3xl font-bold text-foreground">Color Palette</h1>

            <section class="space-y-4">
              <h2 class="text-xl font-semibold">Semantic Colors</h2>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="space-y-2">
                  <div class="h-24 rounded-lg bg-primary"></div>
                  <p class="text-sm font-medium">Primary</p>
                </div>
                <div class="space-y-2">
                  <div class="h-24 rounded-lg bg-secondary"></div>
                  <p class="text-sm font-medium">Secondary</p>
                </div>
                <div class="space-y-2">
                  <div class="h-24 rounded-lg bg-accent"></div>
                  <p class="text-sm font-medium">Accent</p>
                </div>
                <div class="space-y-2">
                  <div class="h-24 rounded-lg bg-destructive"></div>
                  <p class="text-sm font-medium">Destructive</p>
                </div>
              </div>
            </section>

            <section class="space-y-4">
              <h2 class="text-xl font-semibold">Background Colors</h2>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div class="space-y-2">
                  <div class="h-24 rounded-lg border bg-background"></div>
                  <p class="text-sm font-medium">Background</p>
                </div>
                <div class="space-y-2">
                  <div class="h-24 rounded-lg border bg-card"></div>
                  <p class="text-sm font-medium">Card</p>
                </div>
                <div class="space-y-2">
                  <div class="h-24 rounded-lg border bg-muted"></div>
                  <p class="text-sm font-medium">Muted</p>
                </div>
              </div>
            </section>

            <section class="space-y-4">
              <h2 class="text-xl font-semibold">Text Colors</h2>
              <div class="rounded-lg border bg-card p-6 space-y-4">
                <p class="text-foreground text-lg">Foreground text</p>
                <p class="text-muted-foreground text-lg">Muted foreground text</p>
                <p class="text-primary text-lg">Primary text</p>
                <p class="text-destructive text-lg">Destructive text</p>
              </div>
            </section>

            <section class="space-y-4">
              <h2 class="text-xl font-semibold">Border & Input</h2>
              <div class="space-y-4">
                <div class="h-16 rounded-lg border border-border bg-card"></div>
                <div class="h-16 rounded-lg border border-input bg-background"></div>
                <div class="h-16 rounded-lg ring-2 ring-ring bg-background"></div>
              </div>
            </section>
          </div>
        `;
      });

      await expect(page.locator('#root')).toHaveScreenshot(`color-palette-${theme}.png`, {
        maxDiffPixels: 200,
      });
    }
  });
});

test.describe('Accessibility in Themes', () => {
  test('focus states in light theme', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="bg-background p-8 space-y-6">
          <h1 class="text-2xl font-bold">Focus States - Light</h1>
          <div class="flex gap-4 flex-wrap">
            <button id="btn1" class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 h-10 px-4 py-2">
              Button 1
            </button>
            <button id="btn2" class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 h-10 px-4 py-2">
              Button 2
            </button>
            <input id="input1" type="text" placeholder="Focus me" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2" />
          </div>
        </div>
      `;
    });

    // Focus first button
    await page.locator('#btn1').focus();
    await expect(page.locator('.bg-background')).toHaveScreenshot('focus-light-button1.png');

    // Focus input
    await page.locator('#input1').focus();
    await expect(page.locator('.bg-background')).toHaveScreenshot('focus-light-input.png');
  });

  test('focus states in dark theme', async ({ page }) => {
    await page.goto('http://localhost:5173');

    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
      const root = document.querySelector('#root')!;
      root.innerHTML = `
        <div class="bg-background p-8 space-y-6">
          <h1 class="text-2xl font-bold">Focus States - Dark</h1>
          <div class="flex gap-4 flex-wrap">
            <button id="btn1" class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 h-10 px-4 py-2">
              Button 1
            </button>
            <button id="btn2" class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 h-10 px-4 py-2">
              Button 2
            </button>
            <input id="input1" type="text" placeholder="Focus me" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2" />
          </div>
        </div>
      `;
    });

    // Focus first button
    await page.locator('#btn1').focus();
    await expect(page.locator('.bg-background')).toHaveScreenshot('focus-dark-button1.png');

    // Focus input
    await page.locator('#input1').focus();
    await expect(page.locator('.bg-background')).toHaveScreenshot('focus-dark-input.png');
  });
});
