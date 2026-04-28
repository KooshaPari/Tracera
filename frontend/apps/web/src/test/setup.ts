import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { toHaveNoViolations } from 'jest-axe';
import { createRequire } from 'node:module';
import { afterEach, beforeEach } from 'vitest';
import { expect } from 'vitest';

// jest-axe exports toHaveNoViolations as { toHaveNoViolations: matcher } — spread directly
// Cast needed because jest-axe types reference Jest's matcher types, not Vitest's
expect.extend(toHaveNoViolations as unknown as Parameters<typeof expect.extend>[0]);

// Setup localStorage mock BEFORE any tests run
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    clear() {
      store = {};
    },
    getItem(key: string) {
      return store[key] ?? null;
    },
    key(index: number) {
      const keys = Object.keys(store);
      return keys[index] ?? null;
    },
    get length() {
      return Object.keys(store).length;
    },
    removeItem(key: string) {
      delete store[key];
    },
    setItem(key: string, value: string) {
      store[key] = value.toString();
    },
  };
})();

Object.defineProperty(globalThis, 'localStorage', {
  configurable: true,
  value: localStorageMock,
  writable: true,
});

// Bun + ESM can trip over CJS interop for @testing-library/dom named exports when importing
// @testing-library/user-event's ESM build. Force the CJS build here to keep test setup stable.
const require = createRequire(import.meta.url);
const userEventModule = require('@testing-library/user-event') as {
  default?: { setup: typeof import('@testing-library/user-event').default.setup } | undefined;
  setup?: typeof import('@testing-library/user-event').default.setup | undefined;
};
const userEvent = userEventModule.default ?? userEventModule;

afterEach(() => {
  cleanup();
  localStorageMock.clear();
});

beforeEach(() => {
  globalThis.user = userEvent.setup!();
});
