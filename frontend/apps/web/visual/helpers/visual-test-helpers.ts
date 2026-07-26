/**
 * Visual Testing Helper Utilities
 * Provides reusable functions for visual regression tests
 */

import type { Page } from '@playwright/test';

/**
 * Theme modes supported by TraceRTM
 */
export type ThemeMode = 'light' | 'dark';

/**
 * Set the theme mode for visual testing
 */
export async function setTheme(page: Page, theme: ThemeMode): Promise<void> {
  await page.evaluate((t) => {
    document.documentElement.classList.toggle('dark', t === 'dark');
  }, theme);

  // Wait for theme transition to complete
  await page.waitForTimeout(100);
}

/**
 * Disable all animations for consistent screenshots
 */
export async function disableAnimations(page: Page): Promise<void> {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0ms !important;
        animation-delay: 0ms !important;
        transition-duration: 0ms !important;
        transition-delay: 0ms !important;
      }
    `,
  });
}

/**
 * Wait for fonts to load before taking screenshots
 */
export async function waitForFonts(page: Page): Promise<void> {
  await page.evaluate(async () => {
    await document.fonts.ready;
  });
}

/**
 * Create a component showcase page for visual testing
 */
export async function createShowcasePage(page: Page, html: string): Promise<void> {
  await page.goto('http://localhost:5173');

  await page.evaluate((content) => {
    const root = document.querySelector('#root');
    if (root) {
      root.innerHTML = content;
    }
  }, html);

  await waitForFonts(page);
}

/**
 * Common button variants HTML for reuse
 */
export const BUTTON_VARIANTS_HTML = `
  <div class="space-y-8 p-8 bg-background">
    <section class="space-y-4">
      <h2 class="text-2xl font-bold">Button Variants</h2>
      <div class="flex gap-4 items-center flex-wrap">
        <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
          Primary
        </button>
        <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-destructive text-destructive-foreground hover:bg-destructive/90 h-10 px-4 py-2">
          Destructive
        </button>
        <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors border border-input bg-background hover:bg-accent h-10 px-4 py-2">
          Outline
        </button>
        <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors bg-secondary text-secondary-foreground hover:bg-secondary/80 h-10 px-4 py-2">
          Secondary
        </button>
        <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors hover:bg-accent h-10 px-4 py-2">
          Ghost
        </button>
      </div>
    </section>
  </div>
`;

/**
 * Common card layout HTML for reuse
 */
export const CARD_LAYOUT_HTML = `
  <div class="p-8 bg-background">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="rounded-xl border bg-card text-card-foreground shadow p-6 space-y-4">
        <h3 class="text-2xl font-semibold">Card Title</h3>
        <p class="text-sm text-muted-foreground">
          This is a sample card component with standard styling.
        </p>
        <div class="flex gap-2">
          <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-9 px-4">
            Action
          </button>
          <button class="inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-9 px-4">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
`;

/**
 * Form layout HTML for reuse
 */
export const FORM_LAYOUT_HTML = `
  <div class="p-8 bg-background max-w-md mx-auto">
    <div class="rounded-xl border bg-card p-6 space-y-4">
      <h2 class="text-2xl font-semibold">Sample Form</h2>

      <div class="space-y-2">
        <label class="text-sm font-medium">Name</label>
        <input type="text" placeholder="Enter name" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
      </div>

      <div class="space-y-2">
        <label class="text-sm font-medium">Email</label>
        <input type="email" placeholder="email@example.com" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
      </div>

      <div class="flex gap-2 pt-4">
        <button class="flex-1 inline-flex items-center justify-center rounded-lg text-sm font-medium bg-primary text-primary-foreground h-10 px-4">
          Submit
        </button>
        <button class="flex-1 inline-flex items-center justify-center rounded-lg text-sm font-medium border border-input bg-background h-10 px-4">
          Cancel
        </button>
      </div>
    </div>
  </div>
`;

/**
 * Wait for element to be stable (no layout shifts)
 */
export async function waitForStableElement(
  page: Page,
  selector: string,
  timeout = 1000,
): Promise<void> {
  await page.waitForSelector(selector, { state: 'visible' });

  // Wait for potential layout shifts
  await page.waitForTimeout(timeout);
}

/**
 * Screenshot comparison options optimized for component testing
 */
export const COMPONENT_SCREENSHOT_OPTIONS = {
  animations: 'disabled' as const,
  maxDiffPixels: 100,
  threshold: 0.2,
};

/**
 * Screenshot comparison options optimized for layout testing
 */
export const LAYOUT_SCREENSHOT_OPTIONS = {
  animations: 'disabled' as const,
  fullPage: true,
  maxDiffPixels: 200,
  threshold: 0.3,
};

/**
 * Screenshot comparison options optimized for theme testing
 */
export const THEME_SCREENSHOT_OPTIONS = {
  animations: 'disabled' as const,
  maxDiffPixels: 150,
  threshold: 0.25,
};

/**
 * Common viewport sizes for responsive testing
 */
export const VIEWPORTS = {
  desktop: { height: 800, width: 1280 },
  desktopLarge: { height: 1080, width: 1920 },
  mobile: { height: 667, width: 375 },
  mobileLarge: { height: 926, width: 428 },
  tablet: { height: 1024, width: 768 },
} as const;

/**
 * Test all theme modes for a given test
 */
export async function testAllThemes(
  page: Page,
  testFn: (theme: ThemeMode) => Promise<void>,
): Promise<void> {
  for (const theme of ['light', 'dark'] as const) {
    await setTheme(page, theme);
    await testFn(theme);
  }
}

/**
 * Create a grid of color swatches for theme testing
 */
export function createColorPaletteHTML(theme: ThemeMode): string {
  return `
    <div class="bg-background p-8 space-y-8">
      <h1 class="text-3xl font-bold text-foreground">${theme.charAt(0).toUpperCase() + theme.slice(1)} Theme Colors</h1>

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
        <h2 class="text-xl font-semibold">Text Colors</h2>
        <div class="rounded-lg border bg-card p-6 space-y-3">
          <p class="text-foreground text-lg">Foreground Text</p>
          <p class="text-muted-foreground text-lg">Muted Foreground</p>
          <p class="text-primary text-lg">Primary Text</p>
          <p class="text-destructive text-lg">Destructive Text</p>
        </div>
      </section>
    </div>
  `;
}

/**
 * Hide elements that may cause visual flakiness (e.g., time-based content)
 */
export async function hideFlakeyElements(page: Page, selectors: string[]): Promise<void> {
  for (const selector of selectors) {
    await page.evaluate((sel) => {
      const elements = document.querySelectorAll(sel);
      elements.forEach((el) => {
        if (el instanceof HTMLElement) {
          el.style.visibility = 'hidden';
        }
      });
    }, selector);
  }
}

/**
 * Mock current time for consistent timestamp displays
 */
export async function mockTime(page: Page, timestamp: Date): Promise<void> {
  await page.addInitScript(`{
    const mockDate = new Date('${timestamp.toISOString()}');
    Date = class extends Date {
      constructor(...args) {
        if (args.length === 0) {
          super(mockDate);
        } else {
          super(...args);
        }
      }
      static now() {
        return mockDate.getTime();
      }
    }
  }`);
}

/**
 * Standard setup for visual tests
 */
export async function setupVisualTest(page: Page): Promise<void> {
  await page.goto('http://localhost:5173');
  await disableAnimations(page);
  await waitForFonts(page);
}
