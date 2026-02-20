/**
 * Type definitions for jest-axe with Vitest
 */
import 'vitest';

declare module 'vitest' {
  interface Assertion<T = unknown> {
    toHaveNoViolations(): T;
  }
  interface AsymmetricMatchersContaining {
    toHaveNoViolations(): void;
  }
}

declare module 'jest-axe' {
  export function configureAxe(
    config?: Record<string, unknown>,
  ): (html: Element | Document | string, options?: Record<string, unknown>) => Promise<unknown>;
  export function toHaveNoViolations(): void;
}
