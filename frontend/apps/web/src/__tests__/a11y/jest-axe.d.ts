/**
 * Type definitions for jest-axe with Vitest
 */

import type { axe } from 'jest-axe'

declare global {
  namespace Vi {
    interface Matchers<R = any> {
      toHaveNoViolations(): R
    }
  }
}

export {}
