import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { toHaveNoViolations } from 'jest-axe';
import { createRequire } from 'node:module';
import { afterEach, beforeEach } from 'vitest';
import { expect } from 'vitest';

expect.extend({ toHaveNoViolations });

// Bun + ESM can trip over CJS interop for @testing-library/dom named exports when importing
// @testing-library/user-event's ESM build. Force the CJS build here to keep test setup stable.
const require = createRequire(import.meta.url);
const userEventModule = require('@testing-library/user-event') as {
  default?: { setup: typeof import('@testing-library/user-event').default.setup };
  setup?: typeof import('@testing-library/user-event').default.setup;
};
const userEvent = userEventModule.default ?? userEventModule;

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  globalThis.user = userEvent.setup();
});
