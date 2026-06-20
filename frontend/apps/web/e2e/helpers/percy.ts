/**
 * Percy Visual Regression Testing Helpers
 *
 * Utilities for taking Percy snapshots with consistent configuration
 */
import type { Page } from '@playwright/test';

import percySnapshot from '@percy/playwright';

/**
 * Common viewport widths for responsive testing
 */
export const VIEWPORT_WIDTHS = {
  mobile: [375, 414], // IPhone SE, iPhone 11
  tablet: [768, 1024], // IPad portrait and landscape
  desktop: [1280, 1920], // Standard and Full HD
  all: [375, 768, 1280, 1920],
};

/**
 * Percy snapshot options interface
 */
export interface PercySnapshotOptions {
  widths?: number[];
  minHeight?: number;
  enableJavaScript?: boolean;
  percyCSS?: string;
  scope?: string;
  waitForTimeout?: number;
  waitForSelector?: string;
}

/**
 * Take a Percy snapshot with default options
 */
export async function takeSnapshot(page: Page, name: string, options?: PercySnapshotOptions) {
  // Wait for specified timeout or selector
  if (options?.waitForTimeout) {
    await page.waitForTimeout(options.waitForTimeout);
  }

  if (options?.waitForSelector) {
    await page.waitForSelector(options.waitForSelector);
  }

  // Take snapshot
  await percySnapshot(page, name, {
    enableJavaScript: options?.enableJavaScript,
    minHeight: options?.minHeight,
    percyCSS: options?.percyCSS,
    scope: options?.scope,
    widths: options?.widths,
  });
}

/**
 * Take responsive snapshots across multiple breakpoints
 */
export async function takeResponsiveSnapshot(
  page: Page,
  name: string,
  options?: Omit<PercySnapshotOptions, 'widths'>,
) {
  await takeSnapshot(page, name, {
    ...options,
    widths: VIEWPORT_WIDTHS.all,
  });
}

/**
 * Take snapshot with animations disabled
 */
export async function takeSnapshotWithoutAnimations(
  page: Page,
  name: string,
  options?: PercySnapshotOptions,
) {
  // Disable all animations
  await page.addStyleTag({
    content: `
			*, *::before, *::after {
				animation-duration: 0s !important;
				animation-delay: 0s !important;
				transition-duration: 0s !important;
				transition-delay: 0s !important;
			}
		`,
  });

  await takeSnapshot(page, name, options);
}

/**
 * Take snapshot hiding dynamic content
 */
export async function takeSnapshotHidingDynamic(
  page: Page,
  name: string,
  dynamicSelectors: string[],
  options?: PercySnapshotOptions,
) {
  const percyCSS = `
		${dynamicSelectors.join(',\n')} {
			display: none !important;
		}
		${options?.percyCSS ?? ''}
	`;

  await takeSnapshot(page, name, {
    ...options,
    percyCSS,
  });
}

/**
 * Take snapshot in both light and dark mode
 */
export async function takeThemeSnapshots(page: Page, name: string, options?: PercySnapshotOptions) {
  // Light mode
  await page.emulateMedia({ colorScheme: 'light' });
  await page.waitForTimeout(300); // Wait for theme transition
  await takeSnapshot(page, `${name} - Light`, options);

  // Dark mode
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.waitForTimeout(300);
  await takeSnapshot(page, `${name} - Dark`, options);

  // Reset to light
  await page.emulateMedia({ colorScheme: 'light' });
}

/**
 * Take snapshot at specific viewport
 */
export async function takeSnapshotAtViewport(
  page: Page,
  name: string,
  viewport: { width: number; height: number },
  options?: PercySnapshotOptions,
) {
  // Set viewport
  await page.setViewportSize(viewport);

  // Wait for layout to stabilize
  await page.waitForTimeout(300);

  // Take snapshot
  await takeSnapshot(page, name, {
    ...options,
    widths: [viewport.width],
  });
}

/**
 * Take snapshot of specific element
 */
export async function takeElementSnapshot(
  page: Page,
  name: string,
  selector: string,
  options?: PercySnapshotOptions,
) {
  // Wait for element to be visible
  await page.waitForSelector(selector, { state: 'visible' });

  // Take snapshot scoped to element
  await takeSnapshot(page, name, {
    ...options,
    scope: selector,
  });
}

/**
 * Take snapshots of all interactive states
 */
export async function takeInteractiveStateSnapshots(
  page: Page,
  name: string,
  selector: string,
  options?: PercySnapshotOptions,
) {
  // Default state
  await takeSnapshot(page, `${name} - Default`, options);

  // Hover state
  await page.hover(selector);
  await page.waitForTimeout(100);
  await takeSnapshot(page, `${name} - Hover`, options);

  // Focus state
  await page.focus(selector);
  await page.waitForTimeout(100);
  await takeSnapshot(page, `${name} - Focus`, options);

  // Active state (mouse down)
  await page.dispatchEvent(selector, 'mousedown');
  await page.waitForTimeout(100);
  await takeSnapshot(page, `${name} - Active`, options);
  await page.dispatchEvent(selector, 'mouseup');
}

/**
 * Take snapshot waiting for network idle
 */
export async function takeSnapshotAfterNetworkIdle(
  page: Page,
  name: string,
  options?: PercySnapshotOptions,
) {
  await page.waitForLoadState('networkidle');
  await takeSnapshot(page, name, options);
}

/**
 * Take snapshot with custom Percy CSS to hide elements
 */
export async function takeSnapshotHidingElements(
  page: Page,
  name: string,
  hideSelectors: string[],
  options?: PercySnapshotOptions,
) {
  const percyCSS = hideSelectors.map((sel) => `${sel} { display: none !important; }`).join('\n');

  await takeSnapshot(page, name, {
    ...options,
    percyCSS: `${percyCSS}\n${options?.percyCSS ?? ''}`,
  });
}

/**
 * Common dynamic selectors to hide in snapshots
 */
export const COMMON_DYNAMIC_SELECTORS = [
  '.timestamp',
  '.live-update',
  '.real-time',
  "[data-testid='timestamp']",
  "[data-testid='live-data']",
  '.elapsed-time',
  '.current-time',
];

/**
 * Take snapshot hiding common dynamic elements
 */
export async function takeStableSnapshot(page: Page, name: string, options?: PercySnapshotOptions) {
  await takeSnapshotHidingDynamic(page, name, COMMON_DYNAMIC_SELECTORS, options);
}
