import * as jestDomVitest from "@testing-library/jest-dom/vitest";

export const testMatchers = jestDomVitest;

// jsdom does not implement ResizeObserver; Radix UI primitives (e.g. Slider via
// @radix-ui/react-use-size) require it. Minimal no-op polyfill for tests.
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
