// tests/e2e/support/config/timeouts.ts
// Configuration: Timeout Settings
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
export const timeouts = {
  // Page load timeouts
  pageLoad: 30000,
  navigation: 10000,
  
  // Element timeouts
  element: 5000,
  elementVisible: 5000,
  elementHidden: 5000,
  
  // API timeouts
  apiRequest: 15000,
  apiResponse: 20000,
  
  // Action timeouts
  click: 5000,
  fill: 5000,
  select: 5000,
  
  // Wait timeouts
  networkIdle: 10000,
  domContentLoaded: 5000,
  
  // Custom timeouts
  short: 2000,
  medium: 5000,
  long: 10000,
  veryLong: 30000,
  
  // Performance thresholds
  pageLoadThreshold: 3000,
  apiResponseThreshold: 1000,
  elementInteractionThreshold: 500,
};

export type TimeoutKey = keyof typeof timeouts;

export function getTimeout(key: TimeoutKey): number {
  return timeouts[key];
}

export function setTimeout(key: TimeoutKey, value: number): void {
  (timeouts as any)[key] = value;
}
