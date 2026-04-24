import * as jestDomVitest from '@testing-library/jest-dom/vitest';

const ResizeObserverMock = class {
  disconnect() {}
  observe() {}
  unobserve() {}
};

if (!globalThis.ResizeObserver) {
  Object.defineProperty(globalThis, 'ResizeObserver', {
    configurable: true,
    value: ResizeObserverMock as unknown as typeof ResizeObserver,
    writable: true,
  });
}

if (typeof window !== 'undefined' && !window.ResizeObserver) {
  Object.defineProperty(window, 'ResizeObserver', {
    configurable: true,
    value: ResizeObserverMock as unknown as typeof ResizeObserver,
    writable: true,
  });
}

export const testMatchers = jestDomVitest;
