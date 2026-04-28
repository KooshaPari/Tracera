/**
 * Page Helper Functions for E2E Tests
 * Reusable functions for common page interactions
 */

import { expect, type Page } from '@playwright/test';

/**
 * Navigation Helpers
 */
export async function navigateToDashboard(page: Page): Promise<void> {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
}

export async function navigateToProjects(page: Page): Promise<void> {
  await page.getByRole('link', { name: /projects/i }).click();
  await page.waitForLoadState('networkidle');
}

export async function navigateToItems(page: Page): Promise<void> {
  await page.getByRole('link', { name: /items/i }).click();
  await page.waitForLoadState('networkidle');
}

export async function navigateToGraph(page: Page): Promise<void> {
  await page.getByRole('link', { name: /graph/i }).click();
  await page.waitForLoadState('networkidle');
}

export async function navigateToAgents(page: Page): Promise<void> {
  await page.getByRole('link', { name: /agents/i }).click();
  await page.waitForLoadState('networkidle');
}

export async function navigateToSettings(page: Page): Promise<void> {
  await page.getByRole('link', { name: /settings/i }).click();
  await page.waitForLoadState('networkidle');
}

/**
 * Command Palette Helpers
 */
export async function openCommandPalette(page: Page): Promise<void> {
  const isMac = process.platform === 'darwin';
  if (isMac) {
    await page.keyboard.press('Meta+K');
  } else {
    await page.keyboard.press('Control+K');
  }
}

export async function searchInCommandPalette(page: Page, query: string): Promise<void> {
  await openCommandPalette(page);
  const dialog = page.getByRole('dialog');
  const input = dialog.getByRole('combobox');
  await input.fill(query);
  await page.waitForTimeout(300);
}

export async function executeCommand(page: Page, command: string): Promise<void> {
  await searchInCommandPalette(page, command);
  await page.keyboard.press('Enter');
  await page.waitForLoadState('networkidle');
}

/**
 * Form Helpers
 */
export async function fillProjectForm(
  page: Page,
  data: { name: string; description?: string },
): Promise<void> {
  await page.getByLabel(/name/i).fill(data.name);
  if (data.description != null && data.description !== '') {
    await page.getByLabel(/description/i).fill(data.description);
  }
}

export async function fillItemForm(
  page: Page,
  data: {
    title: string;
    type?: string;
    description?: string;
    status?: string;
    priority?: string;
  },
): Promise<void> {
  await page.getByLabel(/title/i).fill(data.title);

  if (data.type != null && data.type !== '') {
    await page.getByLabel(/type/i).click();
    await page.getByText(new RegExp(data.type, 'i')).click();
  }

  if (data.description != null && data.description !== '') {
    await page.getByLabel(/description/i).fill(data.description);
  }

  if (data.status != null && data.status !== '') {
    await page.getByLabel(/status/i).click();
    await page.getByText(new RegExp(data.status, 'i')).click();
  }

  if (data.priority != null && data.priority !== '') {
    await page.getByLabel(/priority/i).click();
    await page.getByText(new RegExp(data.priority, 'i')).click();
  }
}

export async function submitForm(page: Page, buttonText = /create|save|submit/i): Promise<void> {
  await page.getByRole('button', { name: buttonText }).click();
  await page.waitForLoadState('networkidle');
}

export async function cancelForm(page: Page): Promise<void> {
  await page.getByRole('button', { name: /cancel|close/i }).click();
  await page.waitForTimeout(300);
}

/**
 * Dialog Helpers
 */
export async function confirmDialog(page: Page): Promise<void> {
  const confirmBtn = page.getByRole('button', { name: /confirm|yes|ok/i });
  await confirmBtn.click();
  await page.waitForLoadState('networkidle');
}

export async function cancelDialog(page: Page): Promise<void> {
  const cancelBtn = page.getByRole('button', { name: /cancel|no/i });
  await cancelBtn.click();
  await page.waitForTimeout(300);
}

export async function closeDialog(page: Page): Promise<void> {
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
}

/**
 * Search Helpers
 */
export async function searchGlobal(page: Page, query: string): Promise<void> {
  const searchInput = page.getByPlaceholder(/search/i);
  await searchInput.fill(query);
  await page.waitForLoadState('networkidle');
}

export async function clearSearch(page: Page): Promise<void> {
  const searchInput = page.getByPlaceholder(/search/i);
  await searchInput.click();
  await page.keyboard.press('Control+A');
  await page.keyboard.press('Backspace');
  await page.waitForLoadState('networkidle');
}

/**
 * Filter Helpers
 */
export async function applyFilter(
  page: Page,
  filterLabel: string | RegExp,
  value: string | RegExp,
): Promise<void> {
  const filter = page.getByLabel(filterLabel);
  await filter.click();
  await page.getByText(value).click();
  await page.waitForLoadState('networkidle');
}

export async function clearFilters(page: Page): Promise<void> {
  const clearBtn = page.getByRole('button', {
    name: /clear.*filter|reset.*filter/i,
  });
  await expect(clearBtn).toBeVisible({ timeout: 5000 });
  await clearBtn.click();
  await page.waitForLoadState('networkidle');
}

/**
 * CRUD Operation Helpers
 */
export async function createProject(
  page: Page,
  data: { name: string; description?: string },
): Promise<void> {
  await navigateToProjects(page);
  await page.getByRole('button', { name: /create|new.*project/i }).click();
  await fillProjectForm(page, data);
  await submitForm(page);
}

export async function createItem(
  page: Page,
  data: {
    title: string;
    type?: string;
    description?: string;
  },
): Promise<void> {
  await navigateToItems(page);
  await page.getByRole('button', { name: /create|new.*item/i }).click();
  await fillItemForm(page, data);
  await submitForm(page);
}

export async function deleteItem(page: Page, itemName: string): Promise<void> {
  await navigateToItems(page);
  const item = page.getByText(itemName);
  await item.click();
  await page.waitForLoadState('networkidle');

  const deleteBtn = page.getByRole('button', { name: /delete/i });
  await deleteBtn.click();
  await confirmDialog(page);
}

export async function updateItemStatus(
  page: Page,
  itemName: string,
  newStatus: string,
): Promise<void> {
  await navigateToItems(page);
  const item = page.getByText(itemName);
  await item.click();
  await page.waitForLoadState('networkidle');

  await page.getByLabel(/status/i).click();
  await page.getByText(new RegExp(newStatus, 'i')).click();
  await submitForm(page, /save|update/i);
}

/**
 * Assertion Helpers
 */
export async function assertSuccessMessage(page: Page, message?: string | RegExp): Promise<void> {
  const pattern =
    message != null && (typeof message !== 'string' || message !== '')
      ? message
      : /success|created|updated|deleted/i;
  const successMsg = page.getByText(pattern);
  await successMsg.waitFor({ state: 'visible', timeout: 5000 });
}

export async function assertErrorMessage(page: Page, message?: string | RegExp): Promise<void> {
  const pattern =
    message != null && (typeof message !== 'string' || message !== '')
      ? message
      : /error|failed|invalid/i;
  const errorMsg = page.getByText(pattern);
  await errorMsg.waitFor({ state: 'visible', timeout: 5000 });
}

export async function assertPageTitle(page: Page, title: string | RegExp): Promise<void> {
  const heading = page.getByRole('heading', { name: title });
  await heading.waitFor({ state: 'visible', timeout: 5000 });
}

/**
 * Waiting Helpers
 */
export async function waitForElement(page: Page, selector: string, timeout = 5000): Promise<void> {
  await page.waitForSelector(selector, { state: 'visible', timeout });
}

export async function waitForText(
  page: Page,
  text: string | RegExp,
  timeout = 5000,
): Promise<void> {
  await page.waitForSelector(`text=${text instanceof RegExp ? text.source : text}`, { timeout });
}

export async function waitForNavigation(page: Page, url: string | RegExp): Promise<void> {
  await page.waitForURL(url, { timeout: 5000 });
}

/**
 * Scroll Helpers
 */
export async function scrollToBottom(page: Page): Promise<void> {
  await page.evaluate(() => {
    window.scrollTo(0, document.body.scrollHeight);
  });
  await page.waitForTimeout(300);
}

export async function scrollToTop(page: Page): Promise<void> {
  await page.evaluate(() => {
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(300);
}

export async function scrollToElement(page: Page, selector: string): Promise<void> {
  const element = page.locator(selector);
  await element.scrollIntoViewIfNeeded();
  await page.waitForTimeout(300);
}

/**
 * Screenshot Helpers
 */
export async function takeScreenshot(page: Page, name: string): Promise<void> {
  await page.screenshot({
    fullPage: true,
    path: `test-results/screenshots/${name}.png`,
  });
}

export async function takeElementScreenshot(
  page: Page,
  selector: string,
  name: string,
): Promise<void> {
  const element = page.locator(selector);
  await element.screenshot({ path: `test-results/screenshots/${name}.png` });
}

/**
 * Table Helpers
 */
export async function getTableRowCount(page: Page, tableSelector = 'table'): Promise<number> {
  const rows = page.locator(`${tableSelector} tbody tr`);
  return rows.count();
}

export async function getTableCellValue(
  page: Page,
  row: number,
  column: number,
  tableSelector = 'table',
): Promise<string> {
  const cell = page.locator(`${tableSelector} tbody tr:nth-child(${row}) td:nth-child(${column})`);
  const text = await cell.textContent();
  return text ?? '';
}

export async function sortTableByColumn(page: Page, columnName: string | RegExp): Promise<void> {
  const header = page.getByRole('columnheader', { name: columnName });
  await header.click();
  await page.waitForTimeout(500);
}

/**
 * Keyboard Navigation Helpers
 */
export async function pressTab(page: Page, count = 1): Promise<void> {
  for (let i = 0; i < count; i++) {
    await page.keyboard.press('Tab');
    await page.waitForTimeout(100);
  }
}

export async function pressShiftTab(page: Page, count = 1): Promise<void> {
  for (let i = 0; i < count; i++) {
    await page.keyboard.press('Shift+Tab');
    await page.waitForTimeout(100);
  }
}

export async function pressEnter(page: Page): Promise<void> {
  await page.keyboard.press('Enter');
  await page.waitForTimeout(300);
}

export async function pressEscape(page: Page): Promise<void> {
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
}

/**
 * Drag and Drop Helpers
 */
export async function dragAndDrop(
  page: Page,
  sourceSelector: string,
  targetSelector: string,
): Promise<void> {
  const source = page.locator(sourceSelector);
  const target = page.locator(targetSelector);

  await source.dragTo(target);
  await page.waitForTimeout(500);
}

/**
 * Offline Mode Helpers
 */
export async function goOffline(page: Page): Promise<void> {
  await page.context().setOffline(true);
  await page.waitForTimeout(500);
}

export async function goOnline(page: Page): Promise<void> {
  await page.context().setOffline(false);
  await page.waitForTimeout(500);
}

/**
 * Local Storage Helpers
 */
export async function getLocalStorageItem(page: Page, key: string): Promise<string | null> {
  return page.evaluate((k) => localStorage.getItem(k), key);
}

export async function setLocalStorageItem(page: Page, key: string, value: string): Promise<void> {
  await page.evaluate(
    ({ k, v }) => {
      localStorage.setItem(k, v);
    },
    { k: key, v: value },
  );
}

export async function clearLocalStorage(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.clear();
  });
}

/**
 * Cookie Helpers
 */
export async function getCookie(page: Page, name: string): Promise<string | undefined> {
  const cookies = await page.context().cookies();
  return cookies.find((c) => c.name === name)?.value;
}

export async function setCookie(page: Page, name: string, value: string): Promise<void> {
  await page.context().addCookies([
    {
      domain: 'localhost',
      name,
      path: '/',
      value,
    },
  ]);
}

export async function clearCookies(page: Page): Promise<void> {
  await page.context().clearCookies();
}
