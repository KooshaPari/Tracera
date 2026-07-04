import 'vitest';

declare module 'vitest' {
  interface Assertion<T = any> {
    toHaveNoViolations(): void;
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
